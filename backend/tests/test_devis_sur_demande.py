"""Devis envoyé sur une demande publiée, lien « ou un devis » de « Demandes » (demande de Raphael du 25/11/2026 ;
RM-DEVIS.md § « Devis sur une demande publiée »)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modeles.devis import DemandeDevis
from tests.test_demandes import sur_l_accueil
from tests.test_devis import un_devis
from tests.test_prestataires import fabrique_prestataire, metiers, siret_verifie  # noqa: F401 (fixtures)
from tests.test_propositions import fuite, infos  # noqa: F401 (fixture)


def devis_sur(prestataire, demande_id: int, **modifs):
    return prestataire.client.post(f"/api/moi/prestataire/demandes/{demande_id}/devis", json=un_devis(**modifs))


def test_karim_envoie_un_devis_sur_la_fuite(fabrique_prestataire, fuite, base: Session) -> None:  # noqa: F811
    karim = fabrique_prestataire()  # plombier à Pessac
    siret_verifie(base, karim)
    assert sur_l_accueil(karim.client, fuite.demande)["peut_devis"] is True

    reponse = devis_sur(karim, fuite.demande)

    assert reponse.status_code == 201, reponse.text
    envoye = reponse.json()["demande"]
    assert envoye["devis"]["statut"] == "envoye" and envoye["devis"]["ttc_centimes"] == 119_000
    # La demande de devis est rattachée à la demande publiée, avec son titre et sa description
    ligne = base.scalar(select(DemandeDevis).where(DemandeDevis.id == envoye["id"]))
    assert ligne.demande_id == fuite.demande and ligne.texte.startswith("Fuite sous l'évier : Le siphon goutte")
    # Cela compte comme une réponse : la conversation est ouverte, et le lien disparaît
    vue = sur_l_accueil(karim.client, fuite.demande)
    assert vue["nombre_reponses"] == 1 and vue["conversation_id"] is not None and vue["peut_devis"] is False
    assert infos(fuite, vue["conversation_id"]) == ["Karim Benali a répondu à la demande « Fuite sous l'évier »."]
    # La cliente le retrouve dans « Devis et factures », Karim aussi
    assert [d["id"] for d in fuite.client.get("/api/moi/devis").json()] == [envoye["id"]]
    assert envoye["id"] in [d["id"] for d in karim.client.get("/api/moi/prestataire/devis").json()]

    deuxieme = devis_sur(karim, fuite.demande)
    assert deuxieme.status_code == 400 and "déjà envoyé un devis" in deuxieme.json()["detail"]


def test_pas_de_devis_sans_siret_ni_hors_de_ses_metiers(fabrique_prestataire, fuite, base: Session) -> None:  # noqa: F811
    sans_siret = fabrique_prestataire()
    electricien = fabrique_prestataire("Électricien", ())
    siret_verifie(base, electricien)

    refuse = devis_sur(sans_siret, fuite.demande)
    pas_son_metier = devis_sur(electricien, fuite.demande)

    assert sur_l_accueil(sans_siret.client, fuite.demande)["peut_devis"] is False
    assert refuse.status_code == 400 and "SIRET vérifié" in refuse.json()["detail"]
    assert pas_son_metier.status_code == 403
    # Rien n'est resté : ni réponse, ni demande de devis
    assert sur_l_accueil(fuite.client, fuite.demande)["nombre_reponses"] == 0
    assert base.scalar(select(DemandeDevis.id).where(DemandeDevis.demande_id == fuite.demande)) is None


def test_un_devis_refuse_par_ses_controles_ne_laisse_rien(fabrique_prestataire, fuite, base: Session) -> None:  # noqa: F811
    karim = fabrique_prestataire()
    siret_verifie(base, karim)

    vide = devis_sur(karim, fuite.demande, lignes=[])

    assert vide.status_code == 400 and "au moins une ligne" in vide.json()["detail"]
    assert sur_l_accueil(fuite.client, fuite.demande)["nombre_reponses"] == 0
    assert base.scalar(select(DemandeDevis.id).where(DemandeDevis.demande_id == fuite.demande)) is None
