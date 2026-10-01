"""Absences, contestations, compteurs, et annulations « côté prestataire » (RM-RENDEZ-VOUS.md, RM-AGENDA.md ; lot 4.5)."""

from datetime import datetime, timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.rendez_vous import RendezVous
from app.services import absences
from tests.test_agenda import MARDI, heures, lea  # noqa: F401 (fixtures)
from tests.test_annonces import AUJOURD_HUI, fabrique_prestataire, menage, metiers, publier  # noqa: F401 (fixtures)
from tests.test_rendez_vous import a, dupont, reserver, statut  # noqa: F401 (fixtures)


def passe(base: Session, rdv_id: int, jours: int = 1) -> None:
    """Fait comme si le rendez-vous avait eu lieu il y a quelques jours (l'heure du rendez-vous est passée)."""
    base.execute(text("UPDATE rendez_vous SET debut = debut - make_interval(days => :j + 30), fin = fin - make_interval(days => :j + 30)"
                      " WHERE id = :id"), {"j": jours, "id": rdv_id})
    base.commit()


def vieillir_signalement(base: Session, rdv_id: int, jours: int) -> None:
    base.execute(text("UPDATE rendez_vous SET absence_signalee_le = absence_signalee_le - make_interval(days => :j) WHERE id = :id"),
                 {"j": jours, "id": rdv_id})
    base.commit()


@pytest.fixture
def rdv_passe(lea, dupont, base: Session):
    """Un rendez-vous confirmé de Mme Dupont chez Léa, dont l'heure est passée."""
    rdv = reserver(dupont, lea.annonce, a(MARDI, 10)).json()
    passe(base, rdv["id"])
    return rdv["id"]


# ---------- Signaler ----------


def test_pas_d_absence_avant_l_heure(lea, dupont) -> None:
    rdv = reserver(dupont, lea.annonce, a(MARDI, 10)).json()

    reponse = lea.client.post(f"/api/moi/prestataire/rendez-vous/{rdv['id']}/absent")

    assert reponse.status_code == 400 and "après l'heure" in reponse.json()["detail"]


def test_client_absent_compte_apres_7_jours_sans_contestation(lea, dupont, rdv_passe, base: Session, mails_envoyes) -> None:
    signale = lea.client.post(f"/api/moi/prestataire/rendez-vous/{rdv_passe}/absent").json()
    compteur_tout_de_suite = dupont.client.get("/api/moi/absences").json()["absences"]
    vieillir_signalement(base, rdv_passe, 8)

    assert signale["absence"]["absent"] == "client" and signale["absence"]["compte"] is False
    assert compteur_tout_de_suite == 0  # pendant les 7 jours de contestation : pas encore compté
    assert dupont.client.get("/api/moi/absences").json()["absences"] == 1
    assert any("Je suis venu" in m["texte"] for m in mails_envoyes if m["a"] == dupont.email)
    # Le prestataire suivant voit « 1 absence » chez cette cliente
    assert lea.client.get("/api/moi/prestataire/rendez-vous").json()[0]["autre"]["absences"] == 1


def test_une_seule_absence_par_rendez_vous(lea, dupont, rdv_passe) -> None:
    lea.client.post(f"/api/moi/prestataire/rendez-vous/{rdv_passe}/absent")

    deuxieme = dupont.client.post(f"/api/moi/rendez-vous/{rdv_passe}/absent")

    assert deuxieme.status_code == 400 and "déjà signalée" in deuxieme.json()["detail"]


def test_prestataire_absent_visible_sur_sa_page(lea, dupont, rdv_passe, base: Session, client) -> None:
    dupont.client.post(f"/api/moi/rendez-vous/{rdv_passe}/absent")
    prestataire_id = lea.client.get("/api/moi/prestataire").json()["id"]
    avant = client.get(f"/api/prestataires/{prestataire_id}").json()["absences"]
    vieillir_signalement(base, rdv_passe, 8)

    assert avant == 0 and client.get(f"/api/prestataires/{prestataire_id}").json()["absences"] == 1


# ---------- Contester, trancher ----------


def test_contester_puis_l_administrateur_tranche(lea, dupont, rdv_passe, base: Session, fabrique_compte) -> None:
    dupont.client.post(f"/api/moi/rendez-vous/{rdv_passe}/absent")
    trop_court = lea.client.post(f"/api/moi/prestataire/rendez-vous/{rdv_passe}/contester", json={"explication": "non"})
    conteste = lea.client.post(f"/api/moi/prestataire/rendez-vous/{rdv_passe}/contester",
                               json={"explication": "Je suis venu à 10 h, personne n'a ouvert."})
    vieillir_signalement(base, rdv_passe, 8)
    prestataire_id = base.get_one(RendezVous, rdv_passe).prestataire_id
    compte_avant_decision = len(absences.absences_du_prestataire(base, prestataire_id, datetime.now(reglages.FUSEAU_AFFICHAGE)))
    raphael = fabrique_compte(administrateur=True)
    a_trancher = [c for c in raphael.client.get("/api/admin/contestations").json() if c["rendez_vous_id"] == rdv_passe]
    decision = raphael.client.post(f"/api/admin/contestations/{rdv_passe}", json={"compte": False})

    assert trop_court.status_code == 400
    assert conteste.json()["absence"]["contestation"].startswith("Je suis venu")
    assert compte_avant_decision == 0  # contestée : ni comptée ni affichée en attendant
    assert len(a_trancher) == 1 and decision.json() == {"decision": "ne_compte_pas"}
    assert raphael.client.post(f"/api/admin/contestations/{rdv_passe}", json={"compte": True}).status_code == 400


def test_seule_la_personne_marquee_absente_conteste_et_dans_les_7_jours(lea, dupont, rdv_passe, base: Session) -> None:
    lea.client.post(f"/api/moi/prestataire/rendez-vous/{rdv_passe}/absent")  # la cliente est marquée absente

    par_lea = lea.client.post(f"/api/moi/prestataire/rendez-vous/{rdv_passe}/contester", json={"explication": "Je conteste moi aussi"})
    vieillir_signalement(base, rdv_passe, 8)
    trop_tard = dupont.client.post(f"/api/moi/rendez-vous/{rdv_passe}/contester", json={"explication": "J'étais là à 10 h"})

    assert par_lea.status_code == 404
    assert trop_tard.status_code == 400 and "7 jours" in trop_tard.json()["detail"]


def test_un_non_administrateur_ne_tranche_pas(dupont) -> None:
    assert dupont.client.get("/api/admin/contestations").status_code == 403


# ---------- 3 absences en 6 mois → 1 mois sans réserver ----------


def test_trois_absences_un_mois_sans_reserver(lea, dupont, base: Session, client) -> None:
    for heure_ in (9, 10, 11):
        rdv = reserver(dupont, lea.annonce, a(MARDI, heure_)).json()
        passe(base, rdv["id"])
        lea.client.post(f"/api/moi/prestataire/rendez-vous/{rdv['id']}/absent")
        vieillir_signalement(base, rdv["id"], 8)

    compteur = dupont.client.get("/api/moi/absences").json()
    refus = reserver(dupont, lea.annonce, a(MARDI, 14))

    assert compteur["absences"] == 3 and compteur["reservation_suspendue_jusqu_au"] is not None
    assert refus.status_code == 403 and "ne pouvez plus réserver" in refus.json()["detail"]


# ---------- Annulations « côté prestataire » branchées au niveau 4 ----------


def test_bloquer_une_periode_avec_un_rendez_vous_choisir(lea, dupont, client, mails_envoyes) -> None:
    rdv = reserver(dupont, lea.annonce, a(MARDI, 10)).json()
    periode = {"debut": f"{MARDI}T00:00", "fin": f"{MARDI + timedelta(days=1)}T00:00", "motif": "Congés"}

    sans_choix = lea.client.post("/api/moi/agenda/blocages", json=periode)
    garder = lea.client.post("/api/moi/agenda/blocages", json={**periode, "rendez_vous": "garder"})

    assert sans_choix.status_code == 409 and "annuler ou de les garder" in sans_choix.json()["detail"]
    assert garder.status_code == 200 and statut(dupont, rdv["id"]) == "confirme"
    assert heures(client, lea.annonce) == []  # tout le reste du jour est bloqué


def test_bloquer_en_annulant_les_rendez_vous(lea, dupont, mails_envoyes) -> None:
    rdv = reserver(dupont, lea.annonce, a(MARDI, 10)).json()

    lea.client.post("/api/moi/agenda/blocages", json={"debut": f"{MARDI}T09:00", "fin": f"{MARDI}T12:00", "rendez_vous": "annuler"})

    assert statut(dupont, rdv["id"]) == "annule_prestataire"
    assert any("pas disponible à cette date" in m["texte"] for m in mails_envoyes if m["a"] == dupont.email)


def test_changer_de_semaine_type_avec_un_rendez_vous(lea, dupont) -> None:
    rdv = reserver(dupont, lea.annonce, a(MARDI, 10)).json()
    sans_mardi = {"plages": [{"jour_semaine": 6, "debut": "09:00", "fin": "12:00"}]}

    sans_choix = lea.client.post("/api/moi/agenda/semaine", json=sans_mardi)
    annule = lea.client.post("/api/moi/agenda/semaine", json={**sans_mardi, "rendez_vous": "annuler"})

    assert sans_choix.status_code == 409
    assert annule.status_code == 200 and statut(dupont, rdv["id"]) == "annule_prestataire"


def test_date_de_fin_d_un_metier_annule_les_rendez_vous_apres(lea, dupont, metiers) -> None:  # noqa: F811
    rdv = reserver(dupont, lea.annonce, a(MARDI, 10)).json()

    lea.client.post("/api/moi/prestataire/metiers/fin", json={"metier_id": metiers["Coiffeur"], "fin_le": AUJOURD_HUI.isoformat()})

    assert statut(dupont, rdv["id"]) == "annule_prestataire"


def test_blocage_par_l_administrateur_annule_les_rendez_vous(lea, dupont, fabrique_compte) -> None:
    rdv = reserver(dupont, lea.annonce, a(MARDI, 10)).json()
    raphael = fabrique_compte(administrateur=True)
    prestataire_id = lea.client.get("/api/moi/prestataire").json()["id"]

    raphael.client.post(f"/api/admin/prestataires/{prestataire_id}/blocage", json={"bloque": True})

    assert statut(dupont, rdv["id"]) == "annule_prestataire"


def test_arreter_son_activite_refuse_avec_des_rendez_vous(lea, dupont) -> None:
    reserver(dupont, lea.annonce, a(MARDI, 10))

    reponse = lea.client.post("/api/moi/prestataire/statut", json={"action": "arreter"})

    assert reponse.status_code == 400 and "rendez-vous à venir" in reponse.json()["detail"]


def test_fermer_son_compte_refuse_avec_un_rendez_vous_a_venir(lea, dupont) -> None:
    reserver(dupont, lea.annonce, a(MARDI, 10))

    reponse = dupont.client.post("/api/moi/fermer", json={"mot_de_passe": "MaisonBleue44"})

    assert reponse.status_code == 400 and "Annulez d'abord votre rendez-vous" in reponse.json()["detail"]


def test_moment_ou_une_absence_compte() -> None:
    signale = datetime(2026, 10, 14, 11, 0, tzinfo=reglages.FUSEAU_AFFICHAGE)
    sans = RendezVous(absent="client", absence_signalee_le=signale)
    contestee = RendezVous(absent="client", absence_signalee_le=signale, contestee_le=signale + timedelta(days=1))

    assert absences.moment_ou_elle_compte(sans) == signale + timedelta(days=7)
    assert absences.moment_ou_elle_compte(contestee) is None
