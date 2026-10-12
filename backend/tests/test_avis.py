"""Avis (RM-AVIS.md ; lot 4.7) : laisser, modifier, retirer, répondre, mots interdits, signaler, cacher, note, rappel."""

from datetime import datetime, time, timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import reglages
from app.services import avis as service
from tests.test_absences import passe
from tests.test_agenda import MARDI, lea  # noqa: F401 (fixtures)
from tests.test_prestataires import fabrique_prestataire, metiers  # noqa: F401 (fixtures)
from tests.test_rendez_vous import a, dupont, reserver  # noqa: F401 (fixtures)

PARIS = reglages.FUSEAU_AFFICHAGE


@pytest.fixture
def rdv_tenu(lea, dupont, base: Session) -> int:
    """Mme Dupont a eu sa coupe chez Léa hier."""
    rdv = reserver(dupont, lea, a(MARDI, 10)).json()
    passe(base, rdv["id"])
    return rdv["id"]


def noter(compte, rdv_id: int, note: int = 5, texte: str = "Ponctuelle et soigneuse, je recommande."):
    return compte.client.post(f"/api/moi/rendez-vous/{rdv_id}/avis", json={"note": note, "texte": texte})


def prestataire_id(lea) -> int:
    return lea.client.get("/api/moi/prestataire").json()["id"]


# ---------- Laisser un avis ----------


def test_laisser_un_avis_apres_un_rendez_vous_tenu(lea, dupont, rdv_tenu, client) -> None:
    reponse = noter(dupont, rdv_tenu)
    publics = client.get(f"/api/prestataires/{prestataire_id(lea)}/avis").json()
    page = client.get(f"/api/prestataires/{prestataire_id(lea)}").json()

    assert reponse.status_code == 201 and reponse.json()["auteur"] == "Essai Z."  # « Essai ZZTEST » → prénom + initiale
    assert publics[0]["note"] == 5 and publics[0]["texte"].startswith("Ponctuelle")
    assert page["note"] == 5 and page["nombre_avis"] == 1


def test_pas_d_avis_avant_le_rendez_vous_ni_deux_fois(lea, dupont, rdv_tenu) -> None:
    a_venir = reserver(dupont, lea, a(MARDI, 11)).json()

    avant = noter(dupont, a_venir["id"])
    noter(dupont, rdv_tenu)
    deuxieme = noter(dupont, rdv_tenu)

    assert avant.status_code == 400 and "rendez-vous tenu" in avant.json()["detail"]
    assert deuxieme.status_code == 400 and "déjà laissé" in deuxieme.json()["detail"]


def test_pas_d_avis_apres_30_jours(dupont, rdv_tenu, base: Session) -> None:
    passe(base, rdv_tenu, jours=31)

    assert noter(dupont, rdv_tenu).status_code == 400


def test_pas_d_avis_sur_un_rendez_vous_avec_absence(lea, dupont, rdv_tenu) -> None:
    lea.client.post(f"/api/moi/prestataire/rendez-vous/{rdv_tenu}/absent")

    assert noter(dupont, rdv_tenu).status_code == 400


@pytest.mark.parametrize(("note", "texte", "morceau"), [
    (6, "Très bien, merci beaucoup", "1 à 5"),
    (4, "Bien", "entre 10 et 1000"),
    (1, "Léa est une CONNASSE !", "mot interdit"),
])
def test_avis_refuses(dupont, rdv_tenu, note, texte, morceau) -> None:
    reponse = noter(dupont, rdv_tenu, note, texte)

    assert reponse.status_code == 400 and morceau in reponse.json()["detail"]


def test_l_ia_refuse_une_injure_sans_gros_mot(dupont, rdv_tenu) -> None:
    # « ZZINJURE » : marque que la fausse IA des tests juge injurieuse (la vraie lit le sens du texte)
    reponse = noter(dupont, rdv_tenu, 1, "Une arnaqueuse ZZINJURE qui profite des vieux")

    assert reponse.status_code == 400 and "semble injurieux" in reponse.json()["detail"]


def test_ia_en_panne_l_avis_passe_avec_la_liste_seule(dupont, rdv_tenu, ia_de_moderation) -> None:
    ia_de_moderation["panne"] = 1

    assert noter(dupont, rdv_tenu, 4, "Très bien, rien à redire ZZINJURE").status_code == 201


def test_un_mot_seulement_s_il_est_entier(base: Session) -> None:
    assert service.mot_interdit_dans(base, "Une conserve de qualité, un concours réussi") is None
    assert service.mot_interdit_dans(base, "Quel Connard !") == "connard"


def test_on_ne_note_pas_le_rendez_vous_d_un_autre(fabrique_compte, rdv_tenu) -> None:
    assert noter(fabrique_compte(), rdv_tenu).status_code == 404


# ---------- Modifier, retirer ----------


def test_modifier_puis_retirer(lea, dupont, rdv_tenu, client) -> None:
    avis = noter(dupont, rdv_tenu, 3, "Correct, sans plus.....").json()

    modifie = dupont.client.post(f"/api/moi/avis/{avis['id']}/modifier", json={"note": 4, "texte": "Finalement très bien."})
    retire = dupont.client.post(f"/api/moi/avis/{avis['id']}/retirer")

    assert modifie.json()["note"] == 4
    assert retire.json()["retire"] is True
    assert client.get(f"/api/prestataires/{prestataire_id(lea)}/avis").json() == []
    assert client.get(f"/api/prestataires/{prestataire_id(lea)}").json()["nombre_avis"] == 0
    assert dupont.client.post(f"/api/moi/avis/{avis['id']}/modifier", json={"note": 5, "texte": "Encore changé !"}).status_code == 400


# ---------- Le prestataire répond, signale ----------


def test_le_prestataire_repond_une_seule_fois(lea, dupont, rdv_tenu, client) -> None:
    avis = noter(dupont, rdv_tenu, 2, "En retard d'une heure.").json()

    reponse = lea.client.post(f"/api/moi/prestataire/avis/{avis['id']}/repondre", json={"texte": "Bouchon sur la rocade, désolée."})
    deuxieme = lea.client.post(f"/api/moi/prestataire/avis/{avis['id']}/repondre", json={"texte": "Encore moi"})

    assert reponse.json()["reponse"].startswith("Bouchon")
    assert deuxieme.status_code == 400
    assert client.get(f"/api/prestataires/{prestataire_id(lea)}/avis").json()[0]["note"] == 2  # la note ne change pas


def test_signaler_puis_l_administrateur_cache(lea, dupont, rdv_tenu, fabrique_compte, client, mails_envoyes) -> None:
    avis = noter(dupont, rdv_tenu, 1, "Elle m'a volé un bijou.").json()
    lea.client.post(f"/api/moi/prestataire/avis/{avis['id']}/signaler", json={"texte": "Fausse accusation"})
    raphael = fabrique_compte(administrateur=True)

    a_regarder = [x for x in raphael.client.get("/api/admin/avis-signales").json() if x["avis"]["id"] == avis["id"]]
    sans_motif = raphael.client.post(f"/api/admin/avis/{avis['id']}/decision", json={"cacher": True})
    cache = raphael.client.post(f"/api/admin/avis/{avis['id']}/decision",
                                json={"cacher": True, "motif": "Accusation grave sans élément"})

    assert len(a_regarder) == 1 and a_regarder[0]["signalement"] == "Fausse accusation"
    assert sans_motif.status_code == 400 and cache.json() == {"cache": True}
    assert client.get(f"/api/prestataires/{prestataire_id(lea)}/avis").json() == []
    assert any("Accusation grave" in m["texte"] for m in mails_envoyes if m["a"] == dupont.email)


def test_l_administrateur_peut_laisser_un_avis_signale(lea, dupont, rdv_tenu, fabrique_compte, client) -> None:
    avis = noter(dupont, rdv_tenu, 2, "Pas très aimable ce jour-là.").json()
    lea.client.post(f"/api/moi/prestataire/avis/{avis['id']}/signaler", json={"texte": "Avis injuste"})
    raphael = fabrique_compte(administrateur=True)

    raphael.client.post(f"/api/admin/avis/{avis['id']}/decision", json={"cacher": False})

    assert not [x for x in raphael.client.get("/api/admin/avis-signales").json() if x["avis"]["id"] == avis["id"]]
    assert len(client.get(f"/api/prestataires/{prestataire_id(lea)}/avis").json()) == 1


# ---------- Liste des mots interdits (administrateur) ----------


def test_l_administrateur_ajoute_et_retire_un_mot(fabrique_compte, dupont, rdv_tenu) -> None:
    raphael = fabrique_compte(administrateur=True)

    ajoute = raphael.client.post("/api/admin/mots-interdits", json={"mot": "Zzinterdit"})
    refuse = noter(dupont, rdv_tenu, 3, "Un vrai zzinterdit, ce rendez-vous.")
    raphael.client.post(f"/api/admin/mots-interdits/{ajoute.json()['id']}/retirer")
    accepte = noter(dupont, rdv_tenu, 3, "Un vrai zzinterdit, ce rendez-vous.")

    assert ajoute.json()["mot"] == "zzinterdit"
    assert refuse.status_code == 400 and accepte.status_code == 201
    assert dupont.client.get("/api/admin/mots-interdits").status_code == 403


# ---------- La recherche utilise les avis ----------


def test_la_note_ponderee_classe_la_recherche(lea, dupont, rdv_tenu, client, metiers, base: Session) -> None:  # noqa: F811
    noter(dupont, rdv_tenu, 4, "Bonne coupe, rapide et efficace.")
    page = client.get("/api/recherche", params={"metier_id": metiers["Coiffeur"], "commune_id": base.execute(
        text("SELECT commune_id FROM prestataire WHERE id = :id"), {"id": prestataire_id(lea)}).scalar_one(), "tri": "note"}).json()

    carte = next(r for r in page["resultats"] if r["prestataire_id"] == prestataire_id(lea))
    assert carte["nouveau"] is False and carte["note"] == 4 and carte["nombre_avis"] == 1


# ---------- Rappel le lendemain ----------


def test_rappel_le_lendemain_une_seule_fois(lea, dupont, base: Session, mails_envoyes) -> None:
    rdv = reserver(dupont, lea, a(MARDI, 10)).json()
    lendemain_10h = datetime.combine(MARDI + timedelta(days=1), time(10, 5), tzinfo=PARIS)

    service.envoyer_rappels(base, lendemain_10h)
    service.envoyer_rappels(base, lendemain_10h + timedelta(hours=1))
    base.commit()

    rappels = [m for m in mails_envoyes if m["a"] == dupont.email and "comment s'est passé" in m["sujet"]]
    assert len(rappels) == 1 and rdv["id"]
