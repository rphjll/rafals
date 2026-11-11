"""Les horaires d'un seul jour : clic droit sur un jour du calendrier (RM-AGENDA § « Agenda simplifié », 17/10/2026)."""

from datetime import datetime, timedelta

from app import reglages

from tests.test_agenda import MARDI, heures, lea  # noqa: F401 (fixtures)
from tests.test_prestataires import AUJOURD_HUI, fabrique_prestataire, metiers  # noqa: F401 (fixtures)
from tests.test_rendez_vous import a, dupont, reserver, statut  # noqa: F401 (fixtures)

DIMANCHE = MARDI + timedelta(days=5)  # fermé dans la semaine type de Léa
H = 60  # minutes dans une heure
PARIS = reglages.FUSEAU_AFFICHAGE


def fixer(compte, jour, **donnees):
    return compte.client.post(f"/api/moi/agenda/jours/{jour.isoformat()}", json=donnees)


def test_ouvert_seulement_a_ces_heures_puis_horaires_habituels(lea) -> None:
    # Léa, d'habitude 9 h-12 h et 14 h-19 h le mardi : ce mardi-là, 8 h-12 h et 14 h-18 h
    agenda = fixer(lea, MARDI, ouvert=[[8 * H, 12 * H], [14 * H, 18 * H]]).json()
    libres = heures(lea, MARDI, 60)

    assert libres[0] == "08:00" and "11:00" in libres and "12:00" not in libres and libres[-1] == "17:00"
    assert {b["motif"] for b in agenda["blocages"]} == {"Horaires du jour"}
    assert [o["motif"] for o in agenda["ouvertures"]] == ["Horaires du jour"]  # 8 h-9 h : en plus de la semaine type

    revenu = fixer(lea, MARDI).json()  # ni ouvert ni fermé : les horaires habituels reviennent
    assert heures(lea, MARDI, 60)[0] == "09:00" and heures(lea, MARDI, 60)[-1] == "18:00"
    assert revenu["blocages"] == [] and revenu["ouvertures"] == []


def test_un_jour_ferme_d_habitude_s_ouvre(lea) -> None:
    fixer(lea, DIMANCHE, ouvert=[[10 * H, 13 * H]])

    assert heures(lea, DIMANCHE, 60) == ["10:00", "10:15", "10:30", "10:45", "11:00", "11:15", "11:30", "11:45", "12:00"]


def test_ferme_seulement_a_ces_heures_dans_des_conges(lea) -> None:
    # Congés du mardi au jeudi ; le mardi, finalement fermé seulement de 14 h à 19 h
    lea.client.post("/api/moi/agenda/blocages", json={"debut": f"{MARDI}T00:00", "fin": f"{MARDI + timedelta(days=3)}T00:00",
                                                      "motif": "Congés"})
    agenda = fixer(lea, MARDI, ferme=[[14 * H, 19 * H]]).json()

    assert heures(lea, MARDI, 60)[0] == "09:00" and heures(lea, MARDI, 60)[-1] == "11:00"  # le matin seulement
    a_paris = lambda texte: datetime.fromisoformat(texte).astimezone(PARIS).strftime("%Y-%m-%dT%H:%M")  # noqa: E731
    morceaux = sorted((a_paris(b["debut"]), a_paris(b["fin"]), b["motif"]) for b in agenda["blocages"])
    assert morceaux[0] == (f"{MARDI}T14:00", f"{MARDI}T19:00", "Congés")
    assert morceaux[1] == (f"{MARDI + timedelta(days=1)}T00:00", f"{MARDI + timedelta(days=3)}T00:00", "Congés")  # le reste


def test_les_autres_exceptions_du_jour_sont_remplacees(lea) -> None:
    # Une fermeture 16 h-19 h (dentiste) ce mardi : en fixant 9 h-19 h, elle disparaît de ce jour
    lea.client.post("/api/moi/agenda/blocages", json={"debut": f"{MARDI}T16:00", "fin": f"{MARDI}T19:00", "motif": "Dentiste"})

    agenda = fixer(lea, MARDI, ouvert=[[9 * H, 19 * H]]).json()

    assert "Dentiste" not in {b["motif"] for b in agenda["blocages"]}
    assert heures(lea, MARDI, 60)[-1] == "18:00" and "12:30" in heures(lea, MARDI, 60)  # la pause du midi est ouverte


def test_rendez_vous_hors_des_nouvelles_heures_choisir(lea, dupont) -> None:
    rdv = reserver(dupont, lea, a(MARDI, 10)).json()

    sans_choix = fixer(lea, MARDI, ouvert=[[14 * H, 19 * H]])
    garder = fixer(lea, MARDI, ouvert=[[14 * H, 19 * H]], rendez_vous="garder")

    assert sans_choix.status_code == 409 and "annuler ou de les garder" in sans_choix.json()["detail"]
    assert garder.status_code == 200 and statut(dupont, rdv["id"]) == "confirme"


def test_refus(lea) -> None:
    chevauchent = fixer(lea, MARDI, ouvert=[[8 * H, 12 * H], [11 * H, 15 * H]])
    a_l_envers = fixer(lea, MARDI, ouvert=[[12 * H, 8 * H]])
    passe = fixer(lea, AUJOURD_HUI - timedelta(days=1), ouvert=[[8 * H, 12 * H]])
    les_deux = fixer(lea, MARDI, ouvert=[[8 * H, 12 * H]], ferme=[[14 * H, 16 * H]])

    assert chevauchent.status_code == 400 and "chevauchent" in chevauchent.json()["detail"]
    assert a_l_envers.status_code == 400 and passe.status_code == 400 and les_deux.status_code == 400


def test_fermetures_de_jours_entiers_reunies(lea) -> None:
    # Fermé du mardi au jeudi, puis du jeudi au samedi, puis le dimanche : une seule fermeture du mardi au dimanche
    for de, a in ((0, 3), (2, 5), (5, 6)):
        lea.client.post("/api/moi/agenda/blocages", json={"debut": f"{MARDI + timedelta(days=de)}T00:00",
                                                          "fin": f"{MARDI + timedelta(days=a)}T00:00"})
    blocages = lea.client.get("/api/moi/agenda").json()["blocages"]
    deja = lea.client.post("/api/moi/agenda/blocages", json={"debut": f"{MARDI}T00:00", "fin": f"{MARDI + timedelta(days=1)}T00:00"})

    assert len(blocages) == 1
    assert len(deja.json()["blocages"]) == 1  # refermer un jour déjà fermé ne crée pas de doublon


def test_aucune_plage_ferme_toute_la_journee(lea) -> None:
    # Demande du 21/10/2026 : ce qui n'est pas dit ouvert est fermé ; sans aucune plage, le jour est fermé
    agenda = fixer(lea, MARDI, ouvert=[]).json()

    assert heures(lea, MARDI, 60) == []
    assert [b["motif"] for b in agenda["blocages"]] == ["Horaires du jour"]


def test_horaires_habituels_enlevent_toute_exception_du_jour(lea) -> None:
    # Congés du mardi au jeudi : « horaires habituels » sur le mercredi → congés le mardi et le jeudi seulement
    lea.client.post("/api/moi/agenda/blocages", json={"debut": f"{MARDI}T00:00", "fin": f"{MARDI + timedelta(days=3)}T00:00",
                                                      "motif": "Congés"})
    agenda = fixer(lea, MARDI + timedelta(days=1)).json()

    assert len(agenda["blocages"]) == 2 and {b["motif"] for b in agenda["blocages"]} == {"Congés"}
    assert heures(lea, MARDI, 60) == []
