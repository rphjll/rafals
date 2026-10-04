"""Niveau 6 sans nouvelle table (lot 6.1) : tableau de bord et paiements de l'administrateur (RM-ADMINISTRATION.md),
chiffre d'affaires à déclarer par mois et par trimestre (RM-DEMARCHES.md)."""

from datetime import UTC, date, datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services import demarches
from tests.test_absences import passe
from tests.test_agenda import MARDI, lea  # noqa: F401 (fixtures)
from tests.test_annonces import AUJOURD_HUI, fabrique_prestataire, menage, metiers, publier, siret_verifie  # noqa: F401
from tests.test_paiements import lea_carte, paye, traiter  # noqa: F401 (fixtures)
from tests.test_rendez_vous import a, dupont, reserver  # noqa: F401 (fixtures)

# ---------- Administration ----------


def test_tableau_de_bord_reserve_a_l_administrateur(paye, dupont, fabrique_compte) -> None:  # noqa: F811
    admin = fabrique_compte(administrateur=True)
    tableau = admin.client.get("/api/admin/tableau-de-bord").json()

    assert dupont.client.get("/api/admin/tableau-de-bord").status_code == 403
    assert set(tableau["a_traiter"]) == {"accords", "absences", "avis", "devis", "propositions", "signalements"}
    activite = tableau["activite"]
    assert activite["mois"] == f"{AUJOURD_HUI:%Y-%m}"
    # La base de test contient aussi les paiements des autres tests : au moins celui-ci (50,00 €, commission 2,50 €)
    assert activite["paiements"] >= 1 and activite["paiements_centimes"] >= 5000 and activite["commission_centimes"] >= 250
    assert activite["nouveaux_comptes"] >= 3 and activite["prestataires_actifs"] >= 1 and activite["rendez_vous"] >= 1


def test_une_absence_contestee_compte_dans_ce_qui_est_a_traiter(lea, dupont, fabrique_compte, base: Session) -> None:  # noqa: F811
    admin = fabrique_compte(administrateur=True)
    avant = admin.client.get("/api/admin/tableau-de-bord").json()["a_traiter"]["absences"]
    rdv = reserver(dupont, lea.annonce, a(MARDI, 10)).json()["id"]
    passe(base, rdv)
    lea.client.post(f"/api/moi/prestataire/rendez-vous/{rdv}/absent")
    dupont.client.post(f"/api/moi/rendez-vous/{rdv}/contester", json={"explication": "J'étais là à 10 h, porte fermée."})

    assert admin.client.get("/api/admin/tableau-de-bord").json()["a_traiter"]["absences"] == avant + 1


def test_liste_de_tous_les_paiements_par_pages_de_30(paye, lea_carte, dupont, fabrique_compte) -> None:  # noqa: F811
    admin = fabrique_compte(administrateur=True)
    page = admin.client.get("/api/admin/paiements").json()

    assert dupont.client.get("/api/admin/paiements").status_code == 403
    assert page["par_page"] == 30 and page["total"] >= 1 and len(page["paiements"]) <= 30
    dernier = page["paiements"][0]  # le plus récent d'abord : celui de ce test
    assert (dernier["titre"], dernier["montant_centimes"], dernier["commission_centimes"], dernier["statut"]) == (
        "Coupe carte", 5000, 250, "paye")
    assert dernier["prestataire"] == "Karim Benali" and dernier["client"] == "Essai ZZTEST"


# ---------- Mes démarches ----------


def test_dates_limites_de_declaration() -> None:
    assert demarches.limite_du_mois(2026, 10) == date(2026, 11, 30)
    assert demarches.limite_du_mois(2026, 12) == date(2027, 1, 31)
    assert [demarches.limite_du_trimestre(2026, t) for t in (1, 2, 3, 4)] == [
        date(2026, 4, 30), date(2026, 7, 31), date(2026, 10, 31), date(2027, 1, 31)]


def test_chiffre_a_declarer_ventes_moins_avoirs(lea, dupont, base: Session) -> None:  # noqa: F811
    siret_verifie(base, lea)
    vide = lea.client.get("/api/moi/prestataire/demarches").json()
    for heure in (10, 14):
        rdv = reserver(dupont, lea.annonce, a(MARDI, heure)).json()["id"]
        passe(base, rdv)
        assert lea.client.post(f"/api/moi/prestataire/rendez-vous/{rdv}/paye", json={"moyen": "especes"}).status_code == 200
    demarche = lea.client.get("/api/moi/prestataire/demarches").json()
    mois = demarche["mois"][AUJOURD_HUI.month - 1]
    trimestre = demarche["trimestres"][(AUJOURD_HUI.month - 1) // 3]

    assert vide["siret_verifie"] is True and all(m["encaisse_centimes"] == 0 for m in vide["mois"])
    assert len(demarche["mois"]) == 12 and len(demarche["trimestres"]) == 4 and demarche["annee"] == AUJOURD_HUI.year
    assert (mois["encaisse_centimes"], mois["nombre_factures"]) == (10000, 2)  # 2 × 50,00 €
    assert mois["a_declarer_avant"] == demarches.limite_du_mois(AUJOURD_HUI.year, AUJOURD_HUI.month).isoformat()
    assert trimestre["encaisse_centimes"] == 10000 and mois["terminee"] is False


def test_un_avoir_se_retire_du_chiffre(paye, lea_carte, dupont, base: Session) -> None:  # noqa: F811
    avant = lea_carte.client.get("/api/moi/prestataire/demarches").json()["mois"][AUJOURD_HUI.month - 1]["encaisse_centimes"]
    lea_carte.client.post(f"/api/moi/prestataire/rendez-vous/{paye}/annuler", json={"motif": "Malade"})
    traiter(base)
    apres = lea_carte.client.get("/api/moi/prestataire/demarches").json()["mois"][AUJOURD_HUI.month - 1]

    assert avant == 5000 and apres["encaisse_centimes"] == 0 and apres["nombre_factures"] == 2  # la facture et son avoir


def test_avec_tva_le_chiffre_est_hors_taxe(lea, dupont, base: Session) -> None:  # noqa: F811
    siret_verifie(base, lea)
    lea.client.post("/api/moi/prestataire/tva", json={"facture_tva": True})
    rdv = reserver(dupont, lea.annonce, a(MARDI, 10)).json()["id"]
    passe(base, rdv)
    lea.client.post(f"/api/moi/prestataire/rendez-vous/{rdv}/paye", json={"moyen": "cheque"})

    demarche = lea.client.get("/api/moi/prestataire/demarches").json()

    assert demarche["facture_tva"] is True and demarche["mois"][AUJOURD_HUI.month - 1]["encaisse_centimes"] == 4167


def test_annee_et_acces(lea, dupont, base: Session) -> None:  # noqa: F811
    base.execute(text("SELECT 1"))
    assert lea.client.get("/api/moi/prestataire/demarches", params={"annee": 2020}).status_code == 400
    assert dupont.client.get("/api/moi/prestataire/demarches").status_code == 404  # pas prestataire
    assert datetime.now(UTC).year >= 2026
