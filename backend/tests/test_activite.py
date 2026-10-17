"""« Mon activité » : les chiffres du haut de la page (lot 10.1) et « Mes clients » (lot 10.2). RM-MON-ACTIVITE.md."""

from datetime import datetime, time, timedelta

from sqlalchemy import text
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.prestataires import Prestataire
from app.services import activite
from tests.test_absences import passe
from tests.test_agenda import MARDI, lea  # noqa: F401 (fixtures)
from tests.test_prestataires import AUJOURD_HUI, fabrique_prestataire, metiers, siret_verifie  # noqa: F401 (fixtures)
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
    rdv = reserver(dupont, lea, a(MARDI, 10)).json()["id"]
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
    matin, apres_midi = (reserver(dupont, lea, a(MARDI, heure)).json() for heure in (10, 14))
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


# ---------- Mes clients (lot 10.2) ----------


def clients(prestataire) -> list[dict]:
    reponse = prestataire.client.get("/api/moi/prestataire/clients")
    assert reponse.status_code == 200, reponse.text
    return reponse.json()


def test_mes_clients_rendez_vous_argent_et_coordonnees(lea, dupont, fabrique_prestataire, base: Session) -> None:  # noqa: F811
    siret_verifie(base, lea)
    personne = clients(lea)
    rdv = reserver(dupont, lea, a(MARDI, 10)).json()["id"]
    a_venir = clients(lea)
    passe(base, rdv)
    assert lea.client.post(f"/api/moi/prestataire/rendez-vous/{rdv}/paye", json={"moyen": "especes"}).status_code == 200
    paye = clients(lea)
    base.execute(text("UPDATE rendez_vous SET debut = debut - interval '130 days', fin = fin - interval '130 days' WHERE id = :id"),
                 {"id": rdv})
    base.commit()
    ancien = clients(lea)

    assert personne == [] and len(a_venir) == len(paye) == len(ancien) == 1
    assert a_venir[0] | {"prochain_rendez_vous": None} == {
        "client_id": dupont.id, "nom": "Essai ZZTEST", "telephone": "0600000000", "rendez_vous": 1, "devis": 0,
        "devis_en_attente": 0, "paye_centimes": 0, "prochain_rendez_vous": None, "dernier_rendez_vous": None, "peut_ecrire": True}
    assert a_venir[0]["prochain_rendez_vous"] is not None
    assert (paye[0]["paye_centimes"], paye[0]["prochain_rendez_vous"]) == (5000, None) and paye[0]["dernier_rendez_vous"] is not None
    # Plus de 3 mois après le dernier rendez-vous : plus de nom complet ni de téléphone (RM-CLIENTS)
    assert (ancien[0]["nom"], ancien[0]["telephone"], ancien[0]["paye_centimes"]) == ("Essai Z.", None, 5000)
    assert clients(fabrique_prestataire()) == []  # un autre prestataire ne voit pas les clients de Léa
    assert dupont.client.get("/api/moi/prestataire/clients").status_code == 404  # pas prestataire


def test_mes_clients_un_devis_suffit_et_le_prestataire_peut_ecrire(paul, dupont, envoye) -> None:  # noqa: F811
    avec_devis = clients(paul)
    conversation = paul.client.post("/api/conversations", json={"client_id": dupont.id})
    dupont.client.post(f"/api/moi/devis/{envoye}/refuser", json={"motif": "Trop cher"})

    assert [(c["client_id"], c["nom"], c["telephone"], c["rendez_vous"], c["devis"], c["devis_en_attente"]) for c in avec_devis] == [
        (dupont.id, "Essai Z.", None, 0, 1, 1)]  # sans rendez-vous : ni nom complet ni téléphone
    assert conversation.status_code in (200, 201), conversation.text
    assert [(c["devis"], c["devis_en_attente"]) for c in clients(paul)] == [(1, 0)]  # refusé : toujours client, plus en attente


def fiche(prestataire, client_id: int):
    return prestataire.client.get(f"/api/moi/prestataire/clients/{client_id}")


def test_detail_et_profil_d_un_client(lea, dupont, metiers, fabrique_prestataire, base: Session) -> None:  # noqa: F811
    assert publier_demande(dupont, pelouse(metiers["Plombier"])).status_code == 201
    pas_encore = fiche(lea, dupont.id)
    rdv = reserver(dupont, lea, a(MARDI, 10)).json()["id"]
    avec = fiche(lea, dupont.id).json()
    base.execute(text("UPDATE rendez_vous SET debut = now() - interval '130 days', fin = now() - interval '130 days' + (fin - debut)"
                      " WHERE id = :id"), {"id": rdv})
    base.commit()
    ancien = fiche(lea, dupont.id).json()

    assert pas_encore.status_code == 404  # pas encore sa cliente : rien à voir
    assert (avec["nom"], avec["telephone"]) == ("Essai ZZTEST", "0600000000") and avec["adresse"].startswith("8 allée des Pins, 33400")
    assert [(r["id"], r["titre"], r["prix_centimes"], r["a_venir"]) for r in avec["les_rendez_vous"]] == [(rdv, "Coiffeur / Coiffeuse", 5000, True)]
    assert avec["les_devis"] == [] and [d["titre"] for d in avec["demandes"]] == ["Tondre ma pelouse"]
    assert avec["inscrit_le"] is not None and avec["rendez_vous"] == 1
    # Plus de 3 mois après : plus de nom complet, de téléphone ni d'adresse ; l'historique reste
    assert (ancien["nom"], ancien["telephone"], ancien["adresse"]) == ("Essai Z.", None, None)
    assert [r["a_venir"] for r in ancien["les_rendez_vous"]] == [False]
    assert fiche(fabrique_prestataire(), dupont.id).status_code == 404  # un autre prestataire ne voit rien d'elle
    assert fiche(dupont, dupont.id).status_code == 404  # pas prestataire


def test_profil_d_un_client_avec_devis(paul, dupont, envoye) -> None:  # noqa: F811
    avec_devis = fiche(paul, dupont.id).json()

    assert avec_devis["adresse"] is None and avec_devis["les_rendez_vous"] == []  # un devis seul ne montre pas l'adresse
    assert [(d["total_centimes"], d["statut"]) for d in avec_devis["les_devis"]] == [(119000, "envoye")]
    assert avec_devis["les_devis"][0]["numero"].startswith("D-")


def test_notification_a_80_pour_cent_puis_au_dela_du_seuil(lea, dupont, base: Session, notifications_envoyees, monkeypatch) -> None:  # noqa: F811
    """Demande de Raphael du 17/10/2026 : une notification quand la barre de la TVA passe 80 %, puis quand elle est
    dépassée. Seuil d'essai de 120,00 € : 80 % = 96,00 € ; trois rendez-vous de 50,00 € payés en espèces."""
    from tests.test_notifications import activer

    monkeypatch.setattr(reglages, "SEUIL_TVA_SERVICES_CENTIMES", 12000)
    siret_verifie(base, lea)
    activer(lea)
    rdv = [reserver(dupont, lea, a(MARDI, heure)).json()["id"] for heure in (10, 11, 14)]
    for identifiant in rdv:
        passe(base, identifiant)

    def payer(rang: int) -> list[str]:
        assert lea.client.post(f"/api/moi/prestataire/rendez-vous/{rdv[rang]}/paye", json={"moyen": "especes"}).status_code == 200
        return [n["titre"] for n in notifications_envoyees.envoyees if n["compte_id"] == lea.id and "TVA" in n["titre"]]

    assert payer(0) == []  # 50,00 € : 42 %
    assert payer(1) == ["Vous approchez du seuil de TVA"]  # 100,00 € : 83 %
    assert payer(2) == ["Vous approchez du seuil de TVA", "Seuil de TVA dépassé"]  # 150,00 €
    approche = next(n for n in notifications_envoyees.envoyees if n["titre"] == "Vous approchez du seuil de TVA")
    assert "80 % du seuil de TVA (120,00 €). Il vous reste 20,00 €." in approche["texte"] and approche["lien"] == "/mon-activite"
