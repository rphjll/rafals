"""Agenda : semaine type, blocages, réglages, horaires libres (RM-AGENDA.md ; lot 3.3)."""

from datetime import date, datetime, time, timedelta

import pytest
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.annonces import Annonce
from app.modeles.prestataires import Prestataire
from app.services.agenda import ajouter_mois, horaires_libres
from tests.test_annonces import AUJOURD_HUI, fabrique_prestataire, menage, metiers, publier  # noqa: F401 (fixtures)

PARIS = reglages.FUSEAU_AFFICHAGE
# Un mardi entre 1 et 2 semaines d'ici : assez loin pour « au plus tôt », assez près pour « au plus tard »
MARDI = AUJOURD_HUI + timedelta(days=7 + (2 - AUJOURD_HUI.isoweekday()) % 7)
LEA_MARDI = [{"jour_semaine": 2, "debut": "09:00", "fin": "12:00"}, {"jour_semaine": 2, "debut": "14:00", "fin": "19:00"},
             {"jour_semaine": 6, "debut": "09:00", "fin": "12:00"}]


@pytest.fixture
def lea(fabrique_prestataire, metiers):  # noqa: F811
    """Léa, coiffeuse : mardi 9 h-12 h et 14 h-19 h, samedi 9 h-12 h ; annonce « Coupe femme » de 45 min."""
    compte = fabrique_prestataire("Coiffeur", ())
    assert compte.client.post("/api/moi/agenda/semaine", json={"plages": LEA_MARDI}).status_code == 200
    compte.annonce = publier(compte, menage(metiers["Coiffeur"], titre="Coupe femme", duree_minutes=45)).json()["id"]
    return compte


def heures(compte_ou_client, annonce_id: int, jour: date = MARDI, **params) -> list[str]:
    """Les heures de début libres, en heure de Paris : ["09:00", "09:15", …]."""
    client = getattr(compte_ou_client, "client", compte_ou_client)
    reponse = client.get(f"/api/annonces/{annonce_id}/horaires", params={"jour": jour.isoformat(), **params})
    assert reponse.status_code == 200, reponse.text
    return [datetime.fromisoformat(d).astimezone(PARIS).strftime("%H:%M") for d in reponse.json()["debuts"]]


def reglages_agenda(compte, **modifs):
    donnees = {"pas_minutes": 15, "pause_minutes": 0, "delai_min_minutes": 120, "delai_max_mois": 2} | modifs
    return compte.client.post("/api/moi/agenda/reglages", json=donnees)


# ---------- Semaine type ----------


def test_semaine_type_plusieurs_plages_par_jour(lea) -> None:
    agenda = lea.client.get("/api/moi/agenda").json()

    assert [(p["jour_semaine"], p["debut"], p["fin"]) for p in agenda["plages"]] == [
        (2, "09:00:00", "12:00:00"), (2, "14:00:00", "19:00:00"), (6, "09:00:00", "12:00:00")]
    assert agenda["reglages"] == {"pas_minutes": 15, "pause_minutes": 0, "delai_min_minutes": 120, "delai_max_mois": 2}


@pytest.mark.parametrize(("plages", "morceau"), [
    ([{"jour_semaine": 2, "debut": "12:00", "fin": "09:00"}], "finir après son début"),
    ([{"jour_semaine": 2, "debut": "09:00", "fin": "12:00"}, {"jour_semaine": 2, "debut": "11:00", "fin": "13:00"}], "chevauchent"),
])
def test_semaine_type_incoherente_refusee(lea, plages, morceau) -> None:
    reponse = lea.client.post("/api/moi/agenda/semaine", json={"plages": plages})

    assert reponse.status_code == 400 and morceau in reponse.json()["detail"]


# ---------- Horaires libres ----------


def test_heures_de_debut_tous_les_quarts_d_heure(lea, client) -> None:
    # RM-AGENDA : Léa, pas de 15 min, 9 h-12 h, coupe de 45 min → 9 h 00, 9 h 15… 11 h 15
    libres = heures(client, lea.annonce)

    assert libres[:3] == ["09:00", "09:15", "09:30"]
    assert "11:15" in libres and "11:30" not in libres  # la dernière coupe finit à 12 h
    assert libres[libres.index("11:15") + 1] == "14:00"  # la plage de l'après-midi
    assert heures(client, lea.annonce, MARDI + timedelta(days=1)) == []  # mercredi : fermé


def test_pas_de_30_minutes(lea, client) -> None:
    reglages_agenda(lea, pas_minutes=30)

    assert heures(client, lea.annonce)[:5] == ["09:00", "09:30", "10:00", "10:30", "11:00"]


def test_blocage_de_quelques_heures(lea, client) -> None:
    # Léa bloque 10 h-11 h : aucune coupe ne peut empiéter dessus
    lea.client.post("/api/moi/agenda/blocages", json={
        "debut": f"{MARDI}T10:00", "fin": f"{MARDI}T11:00", "motif": "Dentiste"})

    matin = [h for h in heures(client, lea.annonce) if h < "12:00"]

    assert matin == ["09:00", "09:15", "11:00", "11:15"]


def test_conges_plusieurs_jours_et_motif_jamais_montre(lea, client) -> None:
    fin = MARDI + timedelta(days=4)  # du mardi au vendredi inclus : jusqu'au samedi 0 h
    lea.client.post("/api/moi/agenda/blocages", json={
        "debut": f"{MARDI}T00:00", "fin": f"{fin}T00:00", "motif": "Congés"})

    reponse = client.get(f"/api/annonces/{lea.annonce}/horaires", params={"jour": MARDI.isoformat()})

    assert reponse.json()["debuts"] == []
    assert "Congés" not in reponse.text
    assert heures(client, lea.annonce, MARDI + timedelta(days=4))[:1] == ["09:00"]  # samedi : de nouveau libre


def test_debloquer_rend_les_horaires(lea, client) -> None:
    agenda = lea.client.post("/api/moi/agenda/blocages", json={"debut": f"{MARDI}T00:00", "fin": f"{MARDI}T23:59"}).json()

    lea.client.post(f"/api/moi/agenda/blocages/{agenda['blocages'][0]['id']}/retirer")

    assert heures(client, lea.annonce)[:1] == ["09:00"]


def test_on_ne_debloque_pas_l_agenda_d_un_autre(lea, fabrique_prestataire) -> None:  # noqa: F811
    agenda = lea.client.post("/api/moi/agenda/blocages", json={"debut": f"{MARDI}T00:00", "fin": f"{MARDI}T23:59"}).json()
    karim = fabrique_prestataire()

    reponse = karim.client.post(f"/api/moi/agenda/blocages/{agenda['blocages'][0]['id']}/retirer")

    assert reponse.status_code == 404


def test_periode_deja_passee_refusee(lea) -> None:
    hier = AUJOURD_HUI - timedelta(days=1)
    reponse = lea.client.post("/api/moi/agenda/blocages", json={"debut": f"{hier}T09:00", "fin": f"{hier}T10:00"})

    assert reponse.status_code == 400 and "déjà passée" in reponse.json()["detail"]


def test_au_plus_tot_2_heures_avant(lea, base: Session) -> None:
    # RM-AGENDA : il est 8 h, délai 2 h → premier horaire 10 h 00
    prestataire = base.get_one(Prestataire, lea.client.get("/api/moi/prestataire").json()["id"])
    annonce = base.get_one(Annonce, lea.annonce)
    a_8h = datetime.combine(MARDI, time(8), tzinfo=PARIS)

    libres = horaires_libres(base, prestataire, annonce, MARDI, a_8h)

    assert libres[0].astimezone(PARIS).time() == time(10)


def test_au_plus_tard_2_mois(lea, client) -> None:
    trop_loin = ajouter_mois(AUJOURD_HUI, 2) + timedelta(days=7)

    assert heures(client, lea.annonce, trop_loin) == []
    reglages_agenda(lea, delai_max_mois=4)
    assert heures(client, lea.annonce, trop_loin + timedelta(days=(2 - trop_loin.isoweekday()) % 7))[:1] == ["09:00"]


def test_prix_a_l_heure_le_client_choisit_ses_heures(fabrique_prestataire, metiers, client) -> None:  # noqa: F811
    sonia = fabrique_prestataire()
    sonia.client.post("/api/moi/agenda/semaine", json={"plages": [{"jour_semaine": 2, "debut": "09:00", "fin": "12:00"}]})
    annonce = publier(sonia, menage(metiers["Plombier"], titre="Ménage", forme_prix="heure", prix_centimes=2500,
                                    duree_minutes=None, heures_min=2, heures_max=4)).json()["id"]

    deux_heures = heures(client, annonce)
    trois_heures = heures(client, annonce, heures=3)
    hors_limites = client.get(f"/api/annonces/{annonce}/horaires", params={"jour": MARDI.isoformat(), "heures": 5})

    assert deux_heures[-1] == "10:00" and trois_heures == ["09:00"]
    assert hors_limites.status_code == 400 and "entre 2 h et 4 h" in hors_limites.json()["detail"]


def test_sur_devis_pas_d_agenda(fabrique_prestataire, metiers, client) -> None:  # noqa: F811
    paul = fabrique_prestataire()
    annonce = publier(paul, menage(metiers["Plombier"], titre="Muret", forme_prix="devis", prix_centimes=None,
                                   duree_minutes=None)).json()["id"]

    reponse = client.get(f"/api/annonces/{annonce}/horaires", params={"jour": MARDI.isoformat()})

    assert reponse.status_code == 400 and "sur devis" in reponse.json()["detail"]


def test_metier_arrete_plus_d_horaires_apres_la_date_de_fin(lea, metiers, client) -> None:  # noqa: F811
    lea.client.post("/api/moi/prestataire/metiers/fin", json={"metier_id": metiers["Coiffeur"], "fin_le": AUJOURD_HUI.isoformat()})

    assert heures(lea, lea.annonce) == []  # le mardi qui vient est après la date de fin


def test_activite_en_pause_pas_d_horaires_pour_les_clients(lea, client) -> None:
    lea.client.post("/api/moi/prestataire/statut", json={"action": "pause"})

    assert client.get(f"/api/annonces/{lea.annonce}/horaires", params={"jour": MARDI.isoformat()}).status_code == 404


# ---------- Réglages ----------


@pytest.mark.parametrize(("modifs", "morceau"), [
    ({"pas_minutes": 20}, "15 min, 30 min ou 1 h"),
    ({"pause_minutes": 500}, "pause"),
    ({"delai_max_mois": 0}, "au plus tard"),
])
def test_reglages_hors_limites_refuses(lea, modifs, morceau) -> None:
    reponse = reglages_agenda(lea, **modifs)

    assert reponse.status_code == 400 and morceau in reponse.json()["detail"]


def test_ajouter_des_mois() -> None:
    assert ajouter_mois(date(2026, 10, 31), 2) == date(2026, 12, 31)
    assert ajouter_mois(date(2026, 12, 31), 2) == date(2027, 2, 28)
    assert ajouter_mois(date(2026, 10, 13), 2) == date(2026, 12, 13)
