"""Refonte du calendrier (03/10/2026, RM-AGENDA.md) : un calendrier par métier, ouvertures exceptionnelles,
fermeture qui coupe une ouverture, réglage « un rendez-vous dans un métier bloque les autres calendriers »."""

from datetime import timedelta

import pytest

from tests.test_agenda import LEA_MARDI, MARDI, heures, lea, reglages_agenda  # noqa: F401 (fixtures)
from tests.test_annonces import fabrique_prestataire, menage, metiers, publier  # noqa: F401 (fixtures)
from tests.test_rendez_vous import a, dupont, reserver, statut  # noqa: F401 (fixtures)

MERCREDI = MARDI + timedelta(days=1)  # fermé dans la semaine type de Léa
MARDI_MATIN = [{"jour_semaine": 2, "debut": "09:00", "fin": "12:00"}]
MERCREDI_MATIN = [{"jour_semaine": 3, "debut": "09:00", "fin": "12:00"}]


@pytest.fixture
def karim(fabrique_prestataire, metiers):  # noqa: F811
    """Karim, plombier (mardi matin) et électricien (mercredi matin) : deux calendriers, une annonce de 2 h dans chacun."""
    compte = fabrique_prestataire()
    compte.plombier, compte.electricien = metiers["Plombier"], metiers["Électricien"]
    assert compte.client.post("/api/moi/agenda/semaine", json={"metier_id": compte.plombier, "plages": MARDI_MATIN}).status_code == 200
    assert compte.client.post("/api/moi/agenda/semaine", json={"metier_id": compte.electricien, "plages": MERCREDI_MATIN}).status_code == 200
    compte.fuite = publier(compte, menage(compte.plombier)).json()["id"]
    compte.prise = publier(compte, menage(compte.electricien, titre="Pose d'une prise")).json()["id"]
    return compte


def ouvrir(compte, debut: str, fin: str, **autres):
    return compte.client.post("/api/moi/agenda/ouvertures", json={"debut": debut, "fin": fin, **autres})


# ---------- Un calendrier par métier ----------


def test_chaque_metier_a_sa_semaine_type(karim, client) -> None:
    plombier = karim.client.get("/api/moi/agenda", params={"metier_id": karim.plombier}).json()
    electricien = karim.client.get("/api/moi/agenda", params={"metier_id": karim.electricien}).json()

    assert [p["jour_semaine"] for p in plombier["plages"]] == [2] and plombier["metier_id"] == karim.plombier
    assert [p["jour_semaine"] for p in electricien["plages"]] == [3]
    # Les clients : la fuite se réserve le mardi, la prise le mercredi
    assert heures(client, karim.fuite)[:1] == ["09:00"] and heures(client, karim.fuite, MERCREDI) == []
    assert heures(client, karim.prise) == [] and heures(client, karim.prise, MERCREDI)[:1] == ["09:00"]


def test_sans_metier_c_est_le_calendrier_du_metier_principal(karim) -> None:
    agenda = karim.client.get("/api/moi/agenda").json()

    assert agenda["metier_id"] == karim.plombier and [p["jour_semaine"] for p in agenda["plages"]] == [2]


def test_calendrier_d_un_metier_hors_du_profil_refuse(karim, metiers) -> None:  # noqa: F811
    reponse = karim.client.get("/api/moi/agenda", params={"metier_id": metiers["Coiffeur"]})
    ecriture = karim.client.post("/api/moi/agenda/semaine", json={"metier_id": metiers["Coiffeur"], "plages": MARDI_MATIN})

    assert reponse.status_code == 404 and ecriture.status_code == 404


def test_fermeture_ne_ferme_que_son_calendrier(karim, client) -> None:
    # Karim ferme le calendrier Électricien toute la semaine : le plombier reste réservable le mardi
    karim.client.post("/api/moi/agenda/blocages", json={
        "metier_id": karim.electricien, "debut": f"{MARDI}T00:00", "fin": f"{MARDI + timedelta(days=5)}T00:00"})

    assert heures(client, karim.prise, MERCREDI) == []
    assert heures(client, karim.fuite)[:1] == ["09:00"]
    assert karim.client.get("/api/moi/agenda", params={"metier_id": karim.plombier}).json()["blocages"] == []


# ---------- Ouvertures exceptionnelles ----------


def test_ouverture_exceptionnelle_un_jour_ferme(lea, client) -> None:
    # Léa est fermée le mercredi ; elle ouvre ce mercredi de 10 h à 13 h : coupes de 45 min de 10 h 00 à 12 h 15
    agenda = ouvrir(lea, f"{MERCREDI}T10:00", f"{MERCREDI}T13:00", motif="Mariage de Julie").json()

    libres = heures(client, lea.annonce, MERCREDI)
    reponse = client.get(f"/api/annonces/{lea.annonce}/horaires", params={"jour": MERCREDI.isoformat()})

    assert len(agenda["ouvertures"]) == 1 and agenda["ouvertures"][0]["motif"] == "Mariage de Julie"
    assert libres[0] == "10:00" and libres[-1] == "12:15"
    assert "Mariage" not in reponse.text  # le motif n'est jamais montré aux clients


def test_ouverture_qui_prolonge_la_semaine_type(lea, client) -> None:
    # Mardi 9 h-12 h, ouverture 12 h-14 h : une seule période 9 h-19 h, on peut réserver à 11 h 30 et à 13 h 15
    ouvrir(lea, f"{MARDI}T12:00", f"{MARDI}T14:00")

    libres = heures(client, lea.annonce)

    assert "11:30" in libres and "13:15" in libres


def test_ouverture_de_plusieurs_jours_sans_arret(lea, client) -> None:
    # Du mercredi 9 h au vendredi 18 h : ouvert jour et nuit, le jeudi à 3 h du matin est réservable
    ouvrir(lea, f"{MERCREDI}T09:00", f"{MERCREDI + timedelta(days=2)}T18:00")

    jeudi = heures(client, lea.annonce, MERCREDI + timedelta(days=1))

    assert jeudi[0] == "00:00" and "03:00" in jeudi and jeudi[-1] == "23:45"
    assert heures(client, lea.annonce, MERCREDI)[0] == "09:00"


def test_retirer_une_ouverture(lea, client) -> None:
    agenda = ouvrir(lea, f"{MERCREDI}T10:00", f"{MERCREDI}T13:00").json()

    apres = lea.client.post(f"/api/moi/agenda/ouvertures/{agenda['ouvertures'][0]['id']}/retirer")

    assert apres.status_code == 200 and apres.json()["ouvertures"] == []
    assert heures(client, lea.annonce, MERCREDI) == []


def test_retirer_une_ouverture_avec_un_rendez_vous_choisir(lea, dupont) -> None:
    agenda = ouvrir(lea, f"{MERCREDI}T10:00", f"{MERCREDI}T13:00").json()
    rdv = reserver(dupont, lea.annonce, a(MERCREDI, 10)).json()
    adresse = f"/api/moi/agenda/ouvertures/{agenda['ouvertures'][0]['id']}/retirer"

    sans_choix = lea.client.post(adresse)
    annule = lea.client.post(adresse, json={"rendez_vous": "annuler"})

    assert sans_choix.status_code == 409 and "annuler ou de les garder" in sans_choix.json()["detail"]
    assert annule.status_code == 200 and statut(dupont, rdv["id"]) == "annule_prestataire"


def test_on_ne_retire_pas_l_ouverture_d_un_autre(lea, karim) -> None:
    agenda = ouvrir(lea, f"{MERCREDI}T10:00", f"{MERCREDI}T13:00").json()

    reponse = karim.client.post(f"/api/moi/agenda/ouvertures/{agenda['ouvertures'][0]['id']}/retirer")

    assert reponse.status_code == 404


@pytest.mark.parametrize(("debut", "fin", "morceau"), [
    ("T13:00", "T10:00", "après le début"),
    ("PASSE", "PASSE", "déjà passée"),
])
def test_ouverture_incoherente_refusee(lea, debut, fin, morceau) -> None:
    hier = MARDI - timedelta(days=30)
    reponse = ouvrir(lea, f"{hier}T09:00", f"{hier}T10:00") if debut == "PASSE" else ouvrir(lea, f"{MERCREDI}{debut}", f"{MERCREDI}{fin}")

    assert reponse.status_code == 400 and morceau in reponse.json()["detail"]


# ---------- Une fermeture passe avant une ouverture ----------


def test_fermeture_au_milieu_coupe_l_ouverture_en_deux(lea, client) -> None:
    ouvrir(lea, f"{MERCREDI}T10:00", f"{MERCREDI}T13:00", motif="Mariage")

    agenda = lea.client.post("/api/moi/agenda/blocages", json={"debut": f"{MERCREDI}T11:00", "fin": f"{MERCREDI}T12:00"}).json()

    assert len(agenda["ouvertures"]) == 2 and {o["motif"] for o in agenda["ouvertures"]} == {"Mariage"}
    assert heures(client, lea.annonce, MERCREDI) == ["10:00", "10:15", "12:00", "12:15"]


def test_retirer_la_fermeture_ne_recolle_pas_l_ouverture(lea, client) -> None:
    ouvrir(lea, f"{MERCREDI}T10:00", f"{MERCREDI}T13:00")
    agenda = lea.client.post("/api/moi/agenda/blocages", json={"debut": f"{MERCREDI}T11:00", "fin": f"{MERCREDI}T12:00"}).json()

    apres = lea.client.post(f"/api/moi/agenda/blocages/{agenda['blocages'][0]['id']}/retirer").json()

    assert len(apres["ouvertures"]) == 2
    assert heures(client, lea.annonce, MERCREDI) == ["10:00", "10:15", "12:00", "12:15"]


def test_ouverture_par_dessus_une_fermeture_enregistree_coupee(lea) -> None:
    lea.client.post("/api/moi/agenda/blocages", json={"debut": f"{MERCREDI}T11:00", "fin": f"{MERCREDI}T12:00"})

    agenda = ouvrir(lea, f"{MERCREDI}T10:00", f"{MERCREDI}T13:00").json()
    toute_fermee = ouvrir(lea, f"{MERCREDI}T11:00", f"{MERCREDI}T12:00")

    assert len(agenda["ouvertures"]) == 2
    assert toute_fermee.status_code == 400 and "entièrement fermée" in toute_fermee.json()["detail"]


# ---------- Un rendez-vous dans un métier bloque-t-il les autres calendriers ? (au choix du prestataire) ----------


def test_un_rendez_vous_bloque_les_autres_calendriers_au_depart(karim, dupont, client) -> None:
    # Les deux métiers sont ouverts le mardi matin ; Mme Dupont réserve la fuite de 9 h à 11 h
    karim.client.post("/api/moi/agenda/semaine", json={"metier_id": karim.electricien, "plages": MARDI_MATIN})
    assert reserver(dupont, karim.fuite, a(MARDI, 9)).status_code == 201

    assert karim.client.get("/api/moi/agenda").json()["reglages"]["rendez_vous_bloque_autres_metiers"] is True
    assert heures(client, karim.prise) == []  # la prise (2 h) ne tient plus entre 11 h et 12 h


def test_calendriers_independants_si_le_prestataire_le_choisit(karim, dupont, client) -> None:
    karim.client.post("/api/moi/agenda/semaine", json={"metier_id": karim.electricien, "plages": MARDI_MATIN})
    reglages_agenda(karim, rendez_vous_bloque_autres_metiers=False)
    assert reserver(dupont, karim.fuite, a(MARDI, 9)).status_code == 201

    assert heures(client, karim.prise)[:1] == ["09:00"]  # la prise reste réservable à 9 h
    assert "09:00" not in heures(client, karim.fuite)  # dans son propre calendrier, l'horaire est pris


def test_reglage_inchange_si_non_envoye(karim) -> None:
    reglages_agenda(karim, rendez_vous_bloque_autres_metiers=False)

    reglages_agenda(karim, pas_minutes=30)  # sans la rubrique : elle ne bouge pas

    assert karim.client.get("/api/moi/agenda").json()["reglages"]["rendez_vous_bloque_autres_metiers"] is False


def test_changer_la_semaine_d_un_metier_ne_touche_pas_les_rendez_vous_de_l_autre(karim, dupont) -> None:
    rdv = reserver(dupont, karim.fuite, a(MARDI, 9)).json()

    # Karim vide la semaine type Électricien : le rendez-vous Plombier n'est pas concerné, aucun choix demandé
    reponse = karim.client.post("/api/moi/agenda/semaine", json={"metier_id": karim.electricien, "plages": []})

    assert reponse.status_code == 200 and statut(dupont, rdv["id"]) == "confirme"
