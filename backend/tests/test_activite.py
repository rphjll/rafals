"""Les chiffres du haut de « Mon activité » (RM-MON-ACTIVITE.md ; lot 10.1)."""

from datetime import datetime, time, timedelta

from sqlalchemy.orm import Session

from app import reglages
from app.modeles.prestataires import Prestataire
from app.services import activite
from tests.test_absences import passe
from tests.test_agenda import MARDI, lea  # noqa: F401 (fixtures)
from tests.test_annonces import AUJOURD_HUI, fabrique_prestataire, metiers, siret_verifie  # noqa: F401 (fixtures)
from tests.test_demandes import pelouse
from tests.test_demandes import publier as publier_demande
from tests.test_devis import envoye, paul  # noqa: F401 (fixtures)
from tests.test_messagerie import id_prestataire
from tests.test_propositions import fuite  # noqa: F401 (fixtures)
from tests.test_rendez_vous import a, dupont, reserver  # noqa: F401 (fixtures)

PARIS = reglages.FUSEAU_AFFICHAGE
SEUIL = reglages.SEUIL_TVA_SERVICES_CENTIMES


def chiffres(compte) -> dict:
    reponse = compte.client.get("/api/moi/activite")
    assert reponse.status_code == 200, reponse.text
    return reponse.json()


def test_il_faut_etre_connecte(client) -> None:
    assert client.get("/api/moi/activite").status_code == 401


def test_fin_de_semaine_dimanche_minuit_heure_de_paris() -> None:
    lundi_12 = datetime(2026, 10, 12, 0, 0, tzinfo=PARIS)

    assert activite.fin_de_semaine(datetime(2026, 10, 7, 15, 0, tzinfo=PARIS)) == lundi_12  # un mercredi
    assert activite.fin_de_semaine(datetime(2026, 10, 11, 23, 0, tzinfo=PARIS)) == lundi_12  # dimanche soir
    assert activite.fin_de_semaine(datetime(2026, 10, 12, 0, 30, tzinfo=PARIS)) == lundi_12 + timedelta(days=7)  # lundi


def test_chiffres_du_client(dupont, lea, metiers, base: Session) -> None:  # noqa: F811
    vide = chiffres(dupont)
    assert publier_demande(dupont, pelouse(metiers["Plombier"])).status_code == 201
    rdv = reserver(dupont, lea.annonce, a(MARDI, 10)).json()["id"]
    avec = chiffres(dupont)["client"]
    pastille = dupont.client.get("/api/moi/conversations/non-lues").json()["nombre"]
    passe(base, rdv)

    assert vide == {"prestataire": None, "client": {"demandes_en_ligne": 0, "conversations_a_lire": 0, "rendez_vous_a_venir": 0}}
    assert (avec["demandes_en_ligne"], avec["rendez_vous_a_venir"]) == (1, 1)
    assert avec["conversations_a_lire"] == pastille  # le même nombre que la pastille rouge de « Messages »
    assert chiffres(dupont)["client"]["rendez_vous_a_venir"] == 0  # un rendez-vous commencé ne compte plus


def test_rendez_vous_de_la_semaine_et_argent_encaisse(lea, dupont, base: Session) -> None:  # noqa: F811
    siret_verifie(base, lea)
    vide = chiffres(lea)
    matin, apres_midi = (reserver(dupont, lea.annonce, a(MARDI, heure)).json() for heure in (10, 14))
    prestataire = base.get(Prestataire, id_prestataire(lea))
    lundi_8h = datetime.combine(MARDI - timedelta(days=1), time(8), tzinfo=PARIS)
    mardi_midi = datetime.combine(MARDI, time(12), tzinfo=PARIS)
    dimanche_d_avant = lundi_8h - timedelta(days=1)

    assert vide["client"] is None and vide["prestataire"] == {
        "demandes_pres": 0, "rendez_vous_semaine": 0, "devis_en_attente": 0, "encaisse_mois_centimes": 0,
        "encaisse_annee_centimes": 0, "annee": AUJOURD_HUI.year, "seuil_tva_centimes": SEUIL, "reste_avant_seuil_centimes": SEUIL}
    assert matin["statut"] == apres_midi["statut"] == "confirme"
    assert activite.du_prestataire(base, prestataire, lundi_8h).rendez_vous_semaine == 2  # les deux sont cette semaine-là
    assert activite.du_prestataire(base, prestataire, mardi_midi).rendez_vous_semaine == 1  # celui de 10 h est passé
    assert activite.du_prestataire(base, prestataire, dimanche_d_avant).rendez_vous_semaine == 0  # la semaine d'avant

    passe(base, matin["id"])
    assert lea.client.post(f"/api/moi/prestataire/rendez-vous/{matin['id']}/paye", json={"moyen": "especes"}).status_code == 200
    paye = chiffres(lea)["prestataire"]

    assert (paye["encaisse_mois_centimes"], paye["encaisse_annee_centimes"]) == (5000, 5000)  # 50,00 €
    assert paye["reste_avant_seuil_centimes"] == SEUIL - 5000


def test_pas_de_barre_de_tva_pour_qui_la_facture_deja(lea, base: Session) -> None:  # noqa: F811
    siret_verifie(base, lea)
    assert lea.client.post("/api/moi/prestataire/tva", json={"facture_tva": True}).status_code == 200

    avec_tva = chiffres(lea)["prestataire"]

    assert avec_tva["seuil_tva_centimes"] is None and avec_tva["reste_avant_seuil_centimes"] is None


def test_demandes_pres_de_chez_moi_et_devis_en_attente(fabrique_prestataire, fuite, paul, dupont, envoye) -> None:  # noqa: F811
    karim = fabrique_prestataire()  # plombier à Pessac : la fuite de Mme Dupont est pour lui
    pres = [d["id"] for d in karim.client.get("/api/moi/prestataire/demandes").json()]
    en_attente = chiffres(paul)["prestataire"]["devis_en_attente"]
    dupont.client.post(f"/api/moi/devis/{envoye}/refuser", json={"motif": "Trop cher"})

    # Le même nombre que la page « Demandes près de chez moi » (d'autres tests y laissent aussi des demandes)
    assert fuite.demande in pres and chiffres(karim)["prestataire"]["demandes_pres"] == len(pres)
    assert en_attente == 1
    assert chiffres(paul)["prestataire"]["devis_en_attente"] == 0  # refusé : il n'attend plus de réponse
