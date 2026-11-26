"""Corrections de l'audit du 14/11/2026 (.doc/AUDIT-2026-11-14.md) : un test par point corrigé, avec son numéro."""

from datetime import datetime, time, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import reglages
from tests.conftest import MOT_DE_PASSE_TEST
from tests.test_demandes import AUJOURD_HUI, pelouse, publier, sur_l_accueil
from tests.test_devis import demander, envoyer
from tests.test_prestataires import devenir, id_commune, id_metier, siret_verifie

PARIS = reglages.FUSEAU_AFFICHAGE


def a(jours: int, heure: int = 10) -> datetime:
    return datetime.combine(AUJOURD_HUI + timedelta(days=jours), time(heure), tzinfo=PARIS)


def adresse(compte, client, code: str = "33600", ville: str = "Pessac") -> None:
    reponse = compte.client.post("/api/moi/adresse", json={"ligne": "3 rue du Moulin", "commune_id": id_commune(client, code, ville),
                                                           "code_postal": code})
    assert reponse.status_code in (200, 201), reponse.text


def profil(client, metier: str, **modifs) -> dict:
    return {"nom_affiche": "ZZTEST Audit", "metier_principal_id": id_metier(client, metier),
            "commune_id": id_commune(client, "33600", "Pessac"), "distance_km": 15, "metiers_secondaires": []} | modifs


@pytest.fixture
def fabrique(fabrique_compte, client):
    """Un prestataire d'essai à Pessac (avec son adresse), ex. fabrique("Jardinier") ; une cliente : fabrique()."""

    def fabriquer(metier: str | None = None, **modifs):
        compte = fabrique_compte()
        adresse(compte, client)
        if metier is not None:
            reponse = devenir(compte, profil(client, metier, **modifs))
            assert reponse.status_code == 201, reponse.text
            compte.pid = reponse.json()["id"]
        return compte

    return fabriquer


def conversation(cliente, prestataire) -> int:
    reponse = cliente.client.post("/api/conversations", json={"prestataire_id": prestataire.pid})
    assert reponse.status_code == 201, reponse.text
    return reponse.json()["id"]


def proposer(prestataire, conversation_id: int, client, metier: str, **modifs):
    donnees = {"prix_centimes": 6000, "debut": a(3).isoformat(), "duree_minutes": 60, "paiement_especes": True,
               "metier_id": id_metier(client, metier), "lieu": "chez_client"} | modifs
    return prestataire.client.post(f"/api/conversations/{conversation_id}/propositions", json=donnees)


def accepter(cliente, proposition_id: int):
    return cliente.client.post(f"/api/propositions/{proposition_id}/accepter", json={"mode_paiement": "especes"})


def devis_envoye(cliente, macon) -> int:
    return envoyer(macon, demander(cliente, macon).json()["id"]).json()["demande"]["devis"]["id"]


# ---------- A2 : montants, dates, mail ----------


def test_a2_montants_et_dates_hors_limites(fabrique, client, base: Session) -> None:
    lea, cliente = fabrique("Jardinier"), fabrique()
    fil = conversation(cliente, lea)

    assert proposer(lea, fil, client, "Jardinier", prix_centimes=3_000_000_000).status_code == 400
    assert proposer(lea, fil, client, "Jardinier", prix_centimes=1).status_code == 400
    assert proposer(lea, fil, client, "Jardinier", debut=datetime(2100, 1, 1, 10, tzinfo=PARIS).isoformat()).status_code == 400
    assert publier(cliente, pelouse(id_metier(client, "Jardinier"), budget_centimes=3_000_000_000)).status_code == 400
    assert publier(cliente, pelouse(id_metier(client, "Jardinier"), quand="jour_precis", jour="2099-01-01")).status_code == 400
    paul = fabrique("Maçon")
    siret_verifie(base, paul)
    demande = demander(cliente, paul).json()["id"]
    enorme = [{"libelle": "Or massif", "quantite_centiemes": 100000, "prix_unitaire_centimes": 2_000_000_000}]
    assert envoyer(paul, demande, lignes=enorme).status_code == 400
    assert envoyer(paul, demande, travaux_debut="2090-01-01", travaux_fin="2090-01-02").status_code == 400


@pytest.mark.parametrize("modifs", [
    {"email": "@example.com"}, {"email": "zztest@@example.com"}, {"email": "zz test@example.com"}, {"telephone": "abc"},
    {"telephone": "1"}, {"prenom": "a" * 61}, {"prenom": "<script>"}, {"date_naissance": "1800-01-01"}, {"mot_de_passe": "a" * 201},
    {"mot_de_passe": "1234567890"}, {"mot_de_passe": "aaaaaaaaaa"}, {"mot_de_passe": "Motdepasse1"},
])
def test_d1_inscription_refusee(modifs) -> None:
    from app.main import app

    donnees = {"email": f"zztest.{uuid4().hex[:10]}@example.com", "mot_de_passe": MOT_DE_PASSE_TEST, "prenom": "Essai", "nom": "ZZTEST",
               "telephone": "06 12 34 56 78", "date_naissance": "1990-01-01"} | modifs

    assert TestClient(app).post("/api/comptes", json=donnees).status_code == 400


# ---------- A3, A6, D4 : accepter une proposition ----------


def test_a3_conversation_bloquee_plus_d_acceptation(fabrique, client) -> None:
    lea, cliente = fabrique("Jardinier"), fabrique()
    fil = conversation(cliente, lea)
    proposition = proposer(lea, fil, client, "Jardinier").json()["id"]
    assert lea.client.post(f"/api/conversations/{fil}/bloquer").status_code == 200

    assert cliente.client.post(f"/api/propositions/{proposition}/negocier", json={"prix_centimes": 5000}).status_code == 400
    assert "bloquée" in accepter(cliente, proposition).json()["detail"]


@pytest.mark.limites_particulier
def test_a6_siret_retire_la_proposition_ne_vaut_plus(fabrique, client, base: Session) -> None:
    karim, cliente = fabrique("Plombier"), fabrique()
    siret_verifie(base, karim)
    proposition = proposer(karim, conversation(cliente, karim), client, "Plombier", prix_centimes=50000).json()["id"]
    assert karim.client.post("/api/moi/prestataire/modifier", json=profil(client, "Plombier", siret=None)).status_code == 200

    assert "ne peut plus tenir" in accepter(cliente, proposition).json()["detail"]


def test_a6_metier_retire_la_proposition_ne_vaut_plus(fabrique, client) -> None:
    lea, cliente = fabrique("Jardinier"), fabrique()
    proposition = proposer(lea, conversation(cliente, lea), client, "Jardinier").json()["id"]
    assert lea.client.post("/api/moi/prestataire/modifier", json=profil(client, "Repassage")).status_code == 200

    assert accepter(cliente, proposition).status_code == 400


def test_d4_pas_deux_rendez_vous_a_la_meme_heure_pour_la_cliente(fabrique, client) -> None:
    cliente, un, deux = fabrique(), fabrique("Jardinier"), fabrique("Jardinier")
    premiere = proposer(un, conversation(cliente, un), client, "Jardinier").json()["id"]
    seconde = proposer(deux, conversation(cliente, deux), client, "Jardinier").json()["id"]

    assert accepter(cliente, premiere).status_code == 201
    assert accepter(cliente, seconde).status_code == 409


def test_d4_pas_deux_fois_la_meme_demande(fabrique, client) -> None:
    cliente, jardinier = fabrique(), id_metier(client, "Jardinier")

    assert publier(cliente, pelouse(jardinier)).status_code == 201
    assert publier(cliente, pelouse(jardinier)).status_code == 400


# ---------- A4, A5 : devis ----------


def test_a4_devis_d_un_prestataire_bloque_ou_en_pause(fabrique, fabrique_compte, base: Session) -> None:
    cliente, bloque, en_pause = fabrique(), fabrique("Maçon"), fabrique("Maçon")
    siret_verifie(base, bloque)
    siret_verifie(base, en_pause)
    devis_1, devis_2 = devis_envoye(cliente, bloque), devis_envoye(cliente, en_pause)
    administrateur = fabrique_compte(administrateur=True)
    assert administrateur.client.post(f"/api/admin/prestataires/{bloque.pid}/blocage", json={"bloque": True}).status_code == 200
    assert en_pause.client.post("/api/moi/prestataire/statut", json={"action": "pause"}).status_code == 200

    for devis in (devis_1, devis_2):
        assert cliente.client.post(f"/api/moi/devis/{devis}/accepter", json={"mode_paiement": "direct"}).status_code == 400


def test_a5_ni_arret_ni_fermeture_avec_un_devis_accepte(fabrique, base: Session) -> None:
    cliente, paul = fabrique(), fabrique("Maçon")
    siret_verifie(base, paul)
    devis = devis_envoye(cliente, paul)
    assert cliente.client.post(f"/api/moi/devis/{devis}/accepter", json={"mode_paiement": "direct"}).status_code == 200

    arret = paul.client.post("/api/moi/prestataire/statut", json={"action": "arreter"})
    fermeture = cliente.client.post("/api/moi/fermer", json={"mot_de_passe": MOT_DE_PASSE_TEST})

    assert arret.status_code == 400 and "D-" in arret.json()["detail"]
    assert fermeture.status_code == 400 and "D-" in fermeture.json()["detail"]


def test_a5_fermer_son_compte_ferme_ses_demandes(fabrique, client, base: Session) -> None:
    cliente = fabrique()
    demande = publier(cliente, pelouse(id_metier(client, "Jardinier"))).json()["id"]

    assert cliente.client.post("/api/moi/fermer", json={"mot_de_passe": MOT_DE_PASSE_TEST}).status_code == 200
    assert base.execute(text("SELECT statut FROM demande WHERE id = :id"), {"id": demande}).scalar_one() == "fermee"


# ---------- A7, A8, B1, B2 : profil ----------


@pytest.mark.parametrize("modifs", [{"nom_affiche": "ZZTEST Léa 06 12 34 56 78"}, {"presentation": "Écrivez à lea.zztest@example.com"}])
def test_a7_ni_telephone_ni_mail_dans_le_profil(fabrique_compte, client, modifs) -> None:
    lea = fabrique_compte()
    adresse(lea, client)

    assert devenir(lea, profil(client, "Jardinier", **modifs)).status_code == 400


def test_a8_un_siret_pour_un_seul_profil(fabrique, fabrique_compte, client, repertoire_de_l_etat) -> None:
    siret = "73282932000074"
    repertoire_de_l_etat["reponse"] = [{"siren": siret[:9], "nom_complet": "ZZTEST ENTREPRISE", "statut_diffusion": "O",
                                        "siege": {"siret": siret, "etat_administratif": "A"}, "dirigeants": [{"nom": "ZZTEST"}]}]
    premier = fabrique("Plombier", siret=siret)
    second = fabrique_compte()
    adresse(second, client)

    refus = devenir(second, profil(client, "Plombier", siret=siret))

    assert refus.status_code == 400 and "déjà utilisé" in refus.json()["detail"]
    # Le premier arrête son activité : le SIRET redevient libre
    assert premier.client.post("/api/moi/prestataire/statut", json={"action": "arreter"}).status_code == 200
    assert devenir(second, profil(client, "Plombier", siret=siret)).status_code == 201


@pytest.mark.limites_particulier
def test_b1_sans_siret_pas_montre_sous_un_metier_qui_en_demande_un(fabrique, client, base: Session) -> None:
    karim = fabrique("Plombier", metiers_secondaires=[id_metier(client, "Montage de meubles")])
    pessac = id_commune(client, "33600", "Pessac")

    def trouve(metier: str) -> bool:
        page, pages = 1, 1
        while page <= pages:
            reponse = client.get("/api/recherche", params={"metier_id": id_metier(client, metier), "commune_id": pessac, "page": page}).json()
            if any(r["prestataire_id"] == karim.pid for r in reponse["resultats"]):
                return True
            page, pages = page + 1, reponse["pages"]
        return False

    assert not trouve("Plombier") and trouve("Montage de meubles")
    assert [m["nom"] for m in client.get(f"/api/prestataires/{karim.pid}").json()["metiers"]] == ["Montage de meubles"]
    siret_verifie(base, karim)
    assert trouve("Plombier")


def test_b2_metier_desactive_le_profil_se_modifie_encore(fabrique, fabrique_compte, client) -> None:
    administrateur = fabrique_compte(administrateur=True)
    metier = administrateur.client.post("/api/admin/metiers", json={"nom": f"ZZTEST Métier {uuid4().hex[:6]}", "categorie_id": 1}).json()
    lea = fabrique(metier["nom"])
    retrait = administrateur.client.post(f"/api/admin/metiers/{metier['id']}", json={
        "nom": metier["nom"], "categorie_id": 1, "mots_cles": [], "est_active": False})
    assert retrait.status_code == 200

    garde = lea.client.post("/api/moi/prestataire/modifier", json=profil(client, "Jardinier", metier_principal_id=metier["id"],
                                                                         nom_affiche="ZZTEST Nouveau nom"))
    nouveau = fabrique_compte()
    adresse(nouveau, client)

    assert garde.status_code == 200 and garde.json()["nom_affiche"] == "ZZTEST Nouveau nom"
    assert devenir(nouveau, profil(client, "Jardinier", metier_principal_id=metier["id"])).status_code == 400


# ---------- A9 : payé et absences ----------


def test_a9_paye_et_absence_ne_vont_pas_ensemble(fabrique, client, base: Session) -> None:
    lea = fabrique("Jardinier")
    siret_verifie(base, lea)

    def rendez_vous_passe(jours: int, en_cours: bool = False) -> tuple:
        cliente = fabrique()
        proposition = proposer(lea, conversation(cliente, lea), client, "Jardinier", debut=a(jours).isoformat()).json()["id"]
        rdv = accepter(cliente, proposition).json()["rendez_vous_id"]
        debut, fin = ("10 minutes", "-50 minutes") if en_cours else ("3 hours", "2 hours")
        base.execute(text(f"UPDATE rendez_vous SET debut = now() - interval '{debut}', fin = now() - interval '{fin}' WHERE id = :id"),
                     {"id": rdv})
        base.commit()
        return cliente, rdv

    cliente, rdv = rendez_vous_passe(3)
    assert cliente.client.post(f"/api/moi/rendez-vous/{rdv}/absent").status_code == 200
    assert lea.client.post(f"/api/moi/prestataire/rendez-vous/{rdv}/paye", json={"moyen": "especes"}).status_code == 400

    _, rdv = rendez_vous_passe(4)
    assert lea.client.post(f"/api/moi/prestataire/rendez-vous/{rdv}/paye", json={"moyen": "especes"}).status_code == 200
    assert lea.client.post(f"/api/moi/prestataire/rendez-vous/{rdv}/absent").status_code == 400

    _, rdv = rendez_vous_passe(5, en_cours=True)
    assert lea.client.post(f"/api/moi/prestataire/rendez-vous/{rdv}/paye", json={"moyen": "especes"}).status_code == 200
    assert lea.client.post(f"/api/moi/prestataire/rendez-vous/{rdv}/annuler", json={"motif": "Finalement non"}).status_code == 400


# ---------- C3, D3, D6 ----------


def test_c3_demande_chez_le_prestataire_fermee_a_celui_qui_ne_recoit_pas(fabrique, fabrique_compte, client) -> None:
    lea = fabrique("Coiffeur / Coiffeuse")  # elle va seulement chez ses clientes
    demande = publier(fabrique_compte(), pelouse(id_metier(client, "Coiffeur / Coiffeuse"), titre="Coupe et brushing",
                                                 lieu="chez_prestataire", adresse_ligne=None)).json()["id"]

    assert sur_l_accueil(lea.client, demande)["peut_repondre"] is False
    refus = lea.client.post(f"/api/demandes/{demande}/repondre")
    assert refus.status_code == 403 and "chez le prestataire" in refus.json()["detail"]


def test_d3_ecrire_a_un_prestataire_demande_un_mail_verifie(fabrique, fabrique_compte) -> None:
    lea, pas_verifie = fabrique("Jardinier"), fabrique_compte(verifie=False)

    assert pas_verifie.client.post("/api/conversations", json={"prestataire_id": lea.pid}).status_code == 403
    assert pas_verifie.client.post(f"/api/prestataires/{lea.pid}/abonnement").status_code == 403
    assert pas_verifie.client.post("/api/metiers/propositions", json={"nom": f"ZZTEST {uuid4().hex[:6]}"}).status_code == 403


def test_d3_mineur_ecrit_seulement_apres_l_accord_des_parents(fabrique, fabrique_compte, base: Session) -> None:
    from tests.test_accords import decider, deposer, dernier_accord_id

    lea, lucas, admin = fabrique("Jardinier"), fabrique_compte(age=16), fabrique_compte(administrateur=True)
    deposer(lucas.client)

    refus = lucas.client.post("/api/conversations", json={"prestataire_id": lea.pid})
    assert refus.status_code == 403 and "accord de vos parents" in refus.json()["detail"]
    assert decider(admin.client, dernier_accord_id(base, lucas.id), accepte=True).status_code == 200
    assert lucas.client.post("/api/conversations", json={"prestataire_id": lea.pid}).status_code == 201


@pytest.mark.limites_particulier
def test_d5_sans_siret_prix_de_l_heure_100_euros_au_plus(fabrique, client, base: Session) -> None:
    emma = fabrique("Jardinier")
    metier = id_metier(client, "Jardinier")

    def prix(centimes: int):
        return emma.client.post("/api/moi/prestataire/prix", json={"metier_id": metier, "prix_centimes": centimes})

    refus = prix(150_00)
    assert refus.status_code == 400 and "100 €" in refus.json()["detail"]
    assert prix(100_00).status_code == 200
    siret_verifie(base, emma)
    assert prix(150_00).status_code == 200


@pytest.mark.limites_particulier
def test_d5_sans_siret_pas_d_encaisse_ailleurs(fabrique, base: Session) -> None:
    emma = fabrique("Jardinier")

    def ajouter():
        return emma.client.post("/api/moi/prestataire/encaisse-ailleurs",
                                json={"montant_centimes": 40_000_00, "encaisse_le": AUJOURD_HUI.isoformat()})

    assert ajouter().status_code == 403
    siret_verifie(base, emma)
    assert ajouter().status_code == 201


def test_c1_pas_de_proposition_pendant_ses_conges(fabrique, client) -> None:
    lea, cliente = fabrique("Jardinier"), fabrique()
    debut, reprise = (AUJOURD_HUI + timedelta(days=3)), (AUJOURD_HUI + timedelta(days=6))
    conges = lea.client.post("/api/moi/agenda/blocages", json={"debut": f"{debut}T00:00", "fin": f"{reprise}T00:00", "motif": "Congés"})
    assert conges.status_code in (200, 201), conges.text
    fil = conversation(cliente, lea)

    refus = proposer(lea, fil, client, "Jardinier", debut=a(4).isoformat())

    assert refus.status_code == 409 and "fermé (Congés)" in refus.json()["detail"]
    assert proposer(lea, fil, client, "Jardinier", debut=a(7).isoformat()).status_code == 201


def test_d6_en_pause_la_vraie_raison(fabrique, fabrique_compte, client) -> None:
    lea = fabrique("Jardinier")
    demande = publier(fabrique_compte(), pelouse(id_metier(client, "Jardinier"))).json()["id"]
    assert lea.client.post("/api/moi/prestataire/statut", json={"action": "pause"}).status_code == 200

    assert "en pause" in lea.client.post(f"/api/demandes/{demande}/repondre").json()["detail"]
