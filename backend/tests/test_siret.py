"""Vérification du SIRET auprès du répertoire de l'État (RM-PRESTATAIRES.md ; lot 2.4).
Les réponses de l'État sont simulées (fixture repertoire_de_l_etat) : aucun appel à internet."""

from datetime import UTC, datetime

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.prestataires import reverifier_sirets_en_attente

SIRET = "44306184100047"  # 14 chiffres avec une clé de contrôle correcte ; SIREN = 443061841


def entreprise(nom_complet: str = "ESSAI ZZTEST", *, etat: str = "A", dirigeants: list | None = None, diffusion: str = "O") -> dict:
    """Une réponse du répertoire de l'État. Les comptes d'essai s'appellent « ZZTEST » (voir conftest)."""
    etablissement = {"siret": SIRET, "etat_administratif": etat}
    return {
        "siren": SIRET[:9],
        "nom_complet": nom_complet,
        "nom_raison_sociale": None,
        "statut_diffusion": diffusion,
        "dirigeants": dirigeants or [],
        "siege": etablissement,
        "matching_etablissements": [etablissement],
    }


@pytest.fixture
def profil(client) -> dict:
    plombier = next(m["id"] for m in client.get("/api/metiers/recherche", params={"q": "plombier"}).json() if m["nom"] == "Plombier")
    pessac = client.get("/api/communes/recherche", params={"q": "33600"}).json()[0]["id"]
    return {"nom_affiche": "Julie Martin — Plomberie", "metier_principal_id": plombier, "commune_id": pessac, "distance_km": 10}


def avec_siret(compte, profil: dict):
    return compte.client.post("/api/moi/prestataire", json=profil | {"siret": SIRET})


def test_siret_ouvert_au_bon_nom_verifie(fabrique_compte, profil, repertoire_de_l_etat) -> None:
    repertoire_de_l_etat["reponse"] = [entreprise("ESSAI ZZTEST")]

    reponse = avec_siret(fabrique_compte(), profil)

    assert reponse.status_code == 201
    assert reponse.json()["siret_statut"] == "verifie"


def test_dirigeant_d_une_societe_verifie(fabrique_compte, profil, repertoire_de_l_etat) -> None:
    # Julie est gérante de « Net & Clair SARL » : son nom est parmi les dirigeants
    repertoire_de_l_etat["reponse"] = [entreprise("NET ET CLAIR", dirigeants=[{"nom": "ZZTEST", "prenoms": "JULIE"}])]

    assert avec_siret(fabrique_compte(), profil).json()["siret_statut"] == "verifie"


def test_nom_cache_par_l_etat_accepte_d_office(fabrique_compte, profil, repertoire_de_l_etat) -> None:
    # Décision de Raphael (29/09/2026) : nom « non diffusible » → accepté si le SIRET existe et est ouvert
    repertoire_de_l_etat["reponse"] = [entreprise("[NON-DIFFUSIBLE]", diffusion="P")]

    assert avec_siret(fabrique_compte(), profil).json()["siret_statut"] == "verifie"


@pytest.mark.parametrize(
    ("reponse", "message"),
    [
        ([], "n'existe pas dans le répertoire de l'État"),
        ([entreprise(etat="F")], "Cet établissement est fermé"),
        ([entreprise("GOOGLE FRANCE")], "Ce SIRET appartient à « GOOGLE FRANCE » : il ne semble pas être le vôtre"),
    ],
)
def test_siret_refuse_avec_la_raison(fabrique_compte, profil, repertoire_de_l_etat, reponse, message) -> None:
    repertoire_de_l_etat["reponse"] = reponse
    julie = fabrique_compte()

    refus = avec_siret(julie, profil)

    assert refus.status_code == 400
    assert message in refus.json()["detail"]
    assert julie.client.get("/api/moi/prestataire").status_code == 404  # rien n'a été enregistré


def test_panne_puis_nouvel_essai_automatique(fabrique_compte, profil, repertoire_de_l_etat, base: Session) -> None:
    julie = fabrique_compte()
    en_panne = avec_siret(julie, profil).json()  # par défaut, le répertoire simulé est en panne
    assert en_panne["siret_statut"] == "a_verifier"

    repertoire_de_l_etat["reponse"] = [entreprise("ESSAI ZZTEST")]
    reverifier_sirets_en_attente(base, datetime.now(UTC))
    base.commit()

    assert julie.client.get("/api/moi/prestataire").json()["siret_statut"] == "verifie"
    action = base.execute(
        text("SELECT action FROM journal_action WHERE table_cible = 'prestataire' AND ligne_id = :id ORDER BY id DESC LIMIT 1"),
        {"id": en_panne["id"]},
    ).scalar_one()
    assert action == "reverifier_siret"


def test_nouvel_essai_s_arrete_si_toujours_en_panne(fabrique_compte, profil, base: Session) -> None:
    julie = fabrique_compte()
    avec_siret(julie, profil)

    reverifier_sirets_en_attente(base, datetime.now(UTC))  # toujours en panne
    base.commit()

    assert julie.client.get("/api/moi/prestataire").json()["siret_statut"] == "a_verifier"


def test_l_administrateur_valide_un_siret_a_la_main(fabrique_compte, profil) -> None:
    admin = fabrique_compte(administrateur=True)
    julie = fabrique_compte()
    identifiant = avec_siret(julie, profil).json()["id"]  # en panne → « à vérifier »

    refuse = julie.client.post(f"/api/admin/prestataires/{identifiant}/siret-valide")
    valide = admin.client.post(f"/api/admin/prestataires/{identifiant}/siret-valide")

    assert refuse.status_code == 403
    assert valide.json()["siret_statut"] == "verifie"
