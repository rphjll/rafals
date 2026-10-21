"""S'abonner à un prestataire (demande de Raphael du 21/10/2026 ; services/abonnements.py) : bouton [S'abonner],
« 12 abonnés » visible par tous, « Mes abonnements » et sa cloche, notifications choisies prestataire par prestataire
(créneau libre, nouveau métier, retour après une absence)."""

from datetime import datetime, time, timedelta

from sqlalchemy.orm import Session

from app.modeles.prestataires import Prestataire
from app.services import abonnements
from tests.conftest import MOT_DE_PASSE_TEST
from tests.test_agenda import MARDI, PARIS, lea  # noqa: F401 (fixtures)
from tests.test_notifications import activer
from tests.test_prestataires import AUJOURD_HUI, fabrique_prestataire, id_commune, metiers  # noqa: F401 (fixtures)
from tests.test_rendez_vous import a, dupont, reserver  # noqa: F401 (fixtures)

JOURS = ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche")


def numero(prestataire) -> int:
    return prestataire.client.get("/api/moi/prestataire").json()["id"]


def abonner(compte, prestataire_id: int):
    return compte.client.post(f"/api/prestataires/{prestataire_id}/abonnement")


def cloche(compte, prestataire_id: int, creneau: bool = True, nouveaute: bool = True, retour: bool = True):
    return compte.client.post(f"/api/moi/abonnements/{prestataire_id}/notifications",
                              json={"creneau": creneau, "nouveaute": nouveaute, "retour": retour})


def recues(notifications_envoyees, compte, titre: str) -> list[str]:
    return [n["texte"] for n in notifications_envoyees.envoyees if n["compte_id"] == compte.id and n["titre"] == titre]


def test_s_abonner_et_nombre_d_abonnes(fabrique_prestataire, fabrique_compte, client, metiers) -> None:  # noqa: F811
    karim, julie, paul = fabrique_prestataire(), fabrique_compte(), fabrique_compte()
    karim_id = numero(karim)

    premier = abonner(julie, karim_id)
    deux_fois = abonner(julie, karim_id)
    abonner(paul, karim_id)
    vu_par_julie = julie.client.get(f"/api/prestataires/{karim_id}").json()
    vu_sans_compte = client.get(f"/api/prestataires/{karim_id}").json()
    soi_meme = abonner(karim, karim_id)
    sans_compte = client.post(f"/api/prestataires/{karim_id}/abonnement")
    inconnu = abonner(julie, 999_999_999)
    pessac = id_commune(client, "33600", "Pessac")
    carte = next(c for c in paul.client.get("/api/recherche", params={"metier_id": metiers["Plombier"], "commune_id": pessac})
                 .json()["resultats"] if c["prestataire_id"] == karim_id)
    retire = julie.client.post(f"/api/prestataires/{karim_id}/abonnement/retirer")

    assert premier.status_code == 200 and premier.json() == {"abonne": True, "abonnes": 1}
    assert deux_fois.json() == {"abonne": True, "abonnes": 1}  # jamais deux fois le même prestataire
    assert (vu_par_julie["abonne"], vu_par_julie["abonnes"]) == (True, 2)
    assert (vu_sans_compte["abonne"], vu_sans_compte["abonnes"]) == (False, 2)  # le nombre est visible par tous
    assert soi_meme.status_code == 400 and "votre propre profil" in soi_meme.json()["detail"]
    assert sans_compte.status_code == 401 and inconnu.status_code == 404
    assert (carte["abonne"], carte["abonnes"]) == (True, 2)
    assert retire.json() == {"abonne": False, "abonnes": 1}


def test_mes_abonnements_et_la_cloche(fabrique_prestataire, fabrique_compte, lea) -> None:  # noqa: F811
    karim, julie = fabrique_prestataire(), fabrique_compte()
    karim_id, lea_id = numero(karim), numero(lea)
    abonner(julie, karim_id)
    abonner(julie, lea_id)

    reglee = cloche(julie, karim_id, creneau=False, nouveaute=False)
    pas_abonne = cloche(julie, 999_999_999)
    lea.client.post("/api/moi/prestataire/statut", json={"action": "pause"})
    liste = julie.client.get("/api/moi/abonnements").json()
    nouveau_en_pause = abonner(fabrique_compte(), lea_id)

    assert reglee.json() == {"creneau": False, "nouveaute": False, "retour": True}
    assert pas_abonne.status_code == 404
    # Le plus récent d'abord ; les 3 cases cochées au départ ; un profil en pause reste dans la liste
    assert [c["prestataire_id"] for c in liste] == [lea_id, karim_id]
    assert liste[0]["notifications"] == {"creneau": True, "nouveaute": True, "retour": True}
    assert liste[1]["notifications"] == {"creneau": False, "nouveaute": False, "retour": True}
    assert (liste[0]["visible"], liste[1]["visible"]) == (False, True)
    assert liste[1]["metier"] == "Plombier" and liste[1]["ville"] == "Pessac" and liste[1]["abonnes"] == 1
    assert nouveau_en_pause.status_code == 404  # un profil caché ne se suit pas


def test_creneau_libre_quand_un_client_annule(lea, dupont, fabrique_compte, notifications_envoyees) -> None:  # noqa: F811
    julie, paul = fabrique_compte(), fabrique_compte()
    lea_id = numero(lea)
    for compte in (julie, paul):
        abonner(compte, lea_id)
        activer(compte)
    cloche(paul, lea_id, creneau=False)
    rdv = reserver(dupont, lea, a(MARDI, 10)).json()

    dupont.client.post(f"/api/moi/rendez-vous/{rdv['id']}/annuler")

    assert recues(notifications_envoyees, julie, "Créneau libre") == [
        f"Karim Benali est libre mardi {MARDI:%d/%m/%Y} à 10 h 00"]
    assert recues(notifications_envoyees, paul, "Créneau libre") == []  # case décochée
    assert recues(notifications_envoyees, dupont, "Créneau libre") == []  # pas abonnée


def test_fermeture_retiree_une_seule_fois_en_6_heures(lea, fabrique_compte, notifications_envoyees) -> None:  # noqa: F811
    julie = fabrique_compte()
    abonner(julie, numero(lea))
    activer(julie)
    for jour in (MARDI, MARDI + timedelta(days=4)):
        lea.client.post("/api/moi/agenda/blocages", json={"debut": f"{jour}T00:00", "fin": f"{jour + timedelta(days=1)}T00:00"})
    blocages = lea.client.get("/api/moi/agenda").json()["blocages"]

    for blocage in blocages:
        lea.client.post(f"/api/moi/agenda/blocages/{blocage['id']}/retirer")

    assert len(blocages) == 2
    # Deux jours rouverts coup sur coup : une seule notification
    assert recues(notifications_envoyees, julie, "Créneau libre") == [f"Karim Benali est disponible mardi {MARDI:%d/%m/%Y}"]


def test_nouveau_metier(fabrique_prestataire, fabrique_compte, metiers, notifications_envoyees) -> None:  # noqa: F811
    karim, julie, paul = fabrique_prestataire(), fabrique_compte(), fabrique_compte()
    karim_id = numero(karim)
    for compte in (julie, paul):
        abonner(compte, karim_id)
        activer(compte)
    cloche(paul, karim_id, nouveaute=False)
    profil = karim.client.get("/api/moi/prestataire").json()
    formulaire = {"nom_affiche": profil["nom_affiche"], "metier_principal_id": metiers["Plombier"],
                  "commune_id": profil["commune"]["id"], "distance_km": 15}

    karim.client.post("/api/moi/prestataire/modifier", json=formulaire | {"metiers_secondaires": [metiers["Électricien"], metiers["Maçon"]]})
    karim.client.post("/api/moi/prestataire/modifier", json=formulaire | {"metiers_secondaires": [metiers["Maçon"]]})

    # Électricien retiré : rien ; Maçon ajouté : une notification
    assert recues(notifications_envoyees, julie, "Nouveau métier") == ["Karim Benali propose maintenant : Maçon"]
    assert recues(notifications_envoyees, paul, "Nouveau métier") == []


def test_retour_apres_une_absence(lea, fabrique_compte, base: Session, notifications_envoyees) -> None:  # noqa: F811
    julie = fabrique_compte()
    abonner(julie, numero(lea))
    activer(julie)
    reprise = MARDI + timedelta(days=3)  # fermée mardi, mercredi, jeudi : reprend le vendredi
    lea.client.post("/api/moi/agenda/blocages", json={"debut": f"{MARDI}T00:00", "fin": f"{reprise}T00:00", "motif": "Congés"})
    lea.client.post("/api/moi/agenda/blocages", json={"debut": f"{reprise + timedelta(days=4)}T00:00",
                                                      "fin": f"{reprise + timedelta(days=5)}T00:00"})  # 1 jour : pas une absence
    a_8_h = datetime.combine(reprise, time(8, 0), tzinfo=PARIS)

    abonnements.traiter(base, a_8_h - timedelta(minutes=1))
    avant_8_h = recues(notifications_envoyees, julie, "De retour")
    abonnements.traiter(base, a_8_h + timedelta(minutes=30))
    abonnements.traiter(base, a_8_h + timedelta(hours=1))  # l'heure suivante : déjà prévenue
    abonnements.traiter(base, a_8_h + timedelta(days=5, hours=1))  # après la fermeture d'un seul jour
    base.rollback()

    assert avant_8_h == []
    assert recues(notifications_envoyees, julie, "De retour") == [
        f"Karim Benali reprend son activité ce vendredi {reprise:%d/%m/%Y}"]


def test_retour_apres_une_pause(fabrique_prestataire, fabrique_compte, notifications_envoyees) -> None:  # noqa: F811
    karim, julie = fabrique_prestataire(), fabrique_compte()
    abonner(julie, numero(karim))
    activer(julie)

    karim.client.post("/api/moi/prestataire/statut", json={"action": "pause"})
    karim.client.post("/api/moi/prestataire/statut", json={"action": "reprendre"})

    assert recues(notifications_envoyees, julie, "De retour") == [
        f"Karim Benali reprend son activité ce {JOURS[AUJOURD_HUI.weekday()]} {AUJOURD_HUI:%d/%m/%Y}"]


def test_compte_ferme_ne_compte_plus(fabrique_prestataire, fabrique_compte, base: Session, client) -> None:  # noqa: F811
    karim, julie = fabrique_prestataire(), fabrique_compte()
    karim_id = numero(karim)
    abonner(julie, karim_id)

    ferme = julie.client.post("/api/moi/fermer", json={"mot_de_passe": MOT_DE_PASSE_TEST})

    assert ferme.status_code == 200
    assert client.get(f"/api/prestataires/{karim_id}").json()["abonnes"] == 0
    assert base.get_one(Prestataire, karim_id).statut == "actif"
