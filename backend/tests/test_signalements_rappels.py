"""Signalements d'annonces et de prestataires, rappels de déclaration URSSAF (RM-ADMINISTRATION.md, RM-DEMARCHES.md ;
lot 6.3)."""

from datetime import date, datetime

import pytest
from sqlalchemy.orm import Session

from app import reglages
from app.services import demarches
from tests.test_absences import passe
from tests.test_agenda import MARDI, heures, lea  # noqa: F401 (fixtures)
from tests.test_prestataires import fabrique_prestataire, metiers, siret_verifie  # noqa: F401 (fixtures)
from tests.test_rendez_vous import a, dupont, reserver  # noqa: F401 (fixtures)

PARIS = reglages.FUSEAU_AFFICHAGE


def signaler(compte, **donnees):
    return compte.client.post("/api/signalements", json=donnees)


def mon_signalement(admin, lea_compte) -> dict:  # noqa: F811
    prestataire_id = lea_compte.client.get("/api/moi/prestataire").json()["id"]
    return next(s for s in admin.client.get("/api/admin/signalements").json() if s["prestataire_id"] == prestataire_id)


# ---------- Signaler ----------


def test_signaler_un_prestataire_puis_classer_ou_bloquer(lea, dupont, fabrique_compte, mails_envoyes) -> None:  # noqa: F811
    prestataire_id = lea.client.get("/api/moi/prestataire").json()["id"]
    soi_meme = signaler(lea, prestataire_id=prestataire_id, motif="Je me signale moi-même pour voir")
    trop_court = signaler(dupont, prestataire_id=prestataire_id, motif="Nul")
    cree = signaler(dupont, prestataire_id=prestataire_id, motif="Elle ne répond plus au téléphone")
    deux_fois = signaler(dupont, prestataire_id=prestataire_id, motif="Elle ne répond toujours pas")
    admin = fabrique_compte(administrateur=True)
    avant = admin.client.get("/api/admin/tableau-de-bord").json()["a_traiter"]["signalements"]
    premier = mon_signalement(admin, lea)
    classe = admin.client.post(f"/api/admin/signalements/{premier['id']}", json={"action": "classer"})
    signaler(dupont, prestataire_id=prestataire_id, motif="Faux profil, la photo est volée")
    second = mon_signalement(admin, lea)
    sans_motif = admin.client.post(f"/api/admin/signalements/{second['id']}", json={"action": "bloquer_prestataire"})
    bloque = admin.client.post(f"/api/admin/signalements/{second['id']}", json={"action": "bloquer_prestataire", "decision": "Faux profil"})
    ancienne_action = admin.client.post(f"/api/admin/signalements/{second['id']}", json={"action": "retirer_annonce", "decision": "Prix mensonger"})

    assert soi_meme.status_code == 400 and "vous-même" in soi_meme.json()["detail"]
    assert trop_court.status_code == 400 and cree.status_code == 201
    assert deux_fois.status_code == 400 and "déjà signalé" in deux_fois.json()["detail"]
    assert avant >= 1 and premier["auteur"] == "Essai ZZTEST" and premier["motif"].startswith("Elle ne répond plus")
    assert classe.json()["statut"] == "classe"
    assert second["deja_signale"] == 1  # l'administrateur voit qu'il y en a déjà eu un
    assert sans_motif.status_code == 400
    assert bloque.json()["statut"] == "suivi" and lea.client.get("/api/moi/prestataire").json()["statut"] == "bloque"
    assert ancienne_action.status_code == 422  # « retirer l'annonce » n'existe plus
    # Léa reçoit le motif de l'administrateur, jamais le nom de celle qui a signalé
    mail = next(m for m in mails_envoyes if m["a"] == lea.email and "bloqué" in m["sujet"])
    assert "Faux profil" in mail["texte"] and "ZZTEST" not in mail["texte"]
    assert dupont.client.get("/api/admin/signalements").status_code == 403


def test_il_faut_etre_connecte_pour_signaler(lea, client) -> None:  # noqa: F811
    prestataire_id = lea.client.get("/api/moi/prestataire").json()["id"]

    assert client.post("/api/signalements", json={"prestataire_id": prestataire_id, "motif": "Faux profil, vraiment"}).status_code == 401


# ---------- Rappels URSSAF ----------


@pytest.mark.parametrize(("periodicite", "jour", "attendu"), [
    ("mois", date(2026, 11, 23), (date(2026, 10, 1), date(2026, 11, 30), "octobre 2026")),
    ("mois", date(2027, 1, 5), (date(2026, 12, 1), date(2027, 1, 31), "décembre 2026")),
    ("trimestre", date(2026, 10, 24), (date(2026, 7, 1), date(2026, 10, 31), "3e trimestre 2026")),
    ("trimestre", date(2027, 1, 30), (date(2026, 10, 1), date(2027, 1, 31), "4e trimestre 2026")),
    ("trimestre", date(2026, 4, 25), (date(2026, 1, 1), date(2026, 4, 30), "1er trimestre 2026")),
])
def test_periode_a_declarer(periodicite, jour, attendu) -> None:
    assert demarches.periode_a_declarer(periodicite, jour) == attendu


def test_rappel_7_jours_avant_puis_la_veille_jamais_deux_fois(lea, dupont, base: Session, mails_envoyes) -> None:  # noqa: F811
    siret_verifie(base, lea)
    sans_choix = lea.client.get("/api/moi/prestataire/demarches").json()["periodicite"]
    choisi = lea.client.post("/api/moi/prestataire/demarches/periodicite", json={"periodicite": "mois"}).json()
    # La période à déclarer est le mois dernier : sa date limite est la fin de ce mois-ci
    aujourd_hui = datetime.now(PARIS).date()
    _, limite, nom = demarches.periode_a_declarer("mois", aujourd_hui)

    def rappels_a(moment: datetime) -> int:
        base.expire_all()
        avant = len([m for m in mails_envoyes if m["a"] == lea.email and "URSSAF" in m["sujet"]])
        demarches.envoyer_rappels(base, moment)
        base.commit()
        return len([m for m in mails_envoyes if m["a"] == lea.email and "URSSAF" in m["sujet"]]) - avant

    def a_midi(jour: date) -> datetime:
        return datetime(jour.year, jour.month, jour.day, 12, tzinfo=PARIS)

    trop_tot = rappels_a(a_midi(date(limite.year, limite.month, limite.day - 10)))
    sept_jours = rappels_a(a_midi(date(limite.year, limite.month, limite.day - 7)))
    encore = rappels_a(a_midi(date(limite.year, limite.month, limite.day - 6)))
    veille = rappels_a(a_midi(date(limite.year, limite.month, limite.day - 1)))
    dernier_jour = rappels_a(a_midi(limite))

    assert sans_choix is None and choisi["periodicite"] == "mois"
    assert (trop_tot, sept_jours, encore, veille, dernier_jour) == (0, 1, 0, 1, 0)
    mail = next(m for m in mails_envoyes if m["a"] == lea.email and "URSSAF" in m["sujet"])
    assert nom in mail["sujet"] and "0,00 €" in mail["texte"] and f"{limite:%d/%m/%Y}" in mail["texte"]


def test_pas_de_rappel_sans_choix_ni_sans_siret(lea, base: Session, mails_envoyes) -> None:  # noqa: F811
    lea.client.post("/api/moi/prestataire/demarches/periodicite", json={"periodicite": "trimestre"})  # sans SIRET vérifié
    _, limite, _ = demarches.periode_a_declarer("trimestre", datetime.now(PARIS).date())
    demarches.envoyer_rappels(base, datetime(limite.year, limite.month, limite.day - 2, 12, tzinfo=PARIS))
    base.commit()

    assert [m for m in mails_envoyes if m["a"] == lea.email and "URSSAF" in m["sujet"]] == []
    assert lea.client.post("/api/moi/prestataire/demarches/periodicite", json={"periodicite": "semaine"}).status_code == 422
