"""Rendez-vous : nés d'une proposition acceptée, annuler, rappels, coordonnées (RM-RENDEZ-VOUS.md ; lot 4.3, revu au lot 9.2)."""

from datetime import UTC, datetime, time, timedelta

import pytest
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.rendez_vous import RendezVous
from app.services import rendez_vous as service
from tests.test_agenda import LEA_MARDI, MARDI, heures, lea  # noqa: F401 (fixtures)
from tests.test_prestataires import fabrique_prestataire, metiers  # noqa: F401 (fixtures)
from tests.test_prestataires import id_commune

PARIS = reglages.FUSEAU_AFFICHAGE


def a(jour, h: int, m: int = 0) -> str:
    """Mardi à 10 h, heure de Paris, au format envoyé par l'écran."""
    return datetime.combine(jour, time(h, m), tzinfo=PARIS).isoformat()


@pytest.fixture
def dupont(fabrique_compte, client):
    """Mme Dupont, cliente, avec son adresse à Talence (Léa vient chez ses clientes)."""
    compte = fabrique_compte()
    compte.client.post("/api/moi/adresse", json={"ligne": "8 allée des Pins", "commune_id": id_commune(client, "33400", "Talence"),
                                                 "code_postal": "33400"})
    return compte


class _Reponse:
    """Le rendez-vous créé, présenté comme une réponse du serveur (status_code, json())."""

    def __init__(self, corps: dict) -> None:
        self.status_code, self._corps, self.text = 201, corps, str(corps)

    def json(self) -> dict:
        return self._corps


def reserver(compte, prestataire, debut: str, *, prix_centimes: int = 5000, duree_minutes: int = 45,
             mode_paiement: str = "especes", lieu: str = "chez_client", metier_id: int | None = None):
    """Le seul chemin vers un rendez-vous (RM-RENDEZ-VOUS § « Sans annonces ») : la cliente écrit au prestataire, il
    propose un prix, un jour et une heure, elle accepte. Renvoie le rendez-vous, ou la première réponse refusée."""
    profil = prestataire.client.get("/api/moi/prestataire").json()
    conversation = compte.client.post("/api/conversations", json={"prestataire_id": profil["id"]})
    if conversation.status_code != 201:
        return conversation
    proposition = prestataire.client.post(f"/api/conversations/{conversation.json()['id']}/propositions", json={
        "prix_centimes": prix_centimes, "debut": debut, "duree_minutes": duree_minutes,
        "metier_id": metier_id or profil["metier_principal"]["id"], "lieu": lieu,
        "paiement_carte": mode_paiement == "carte", "paiement_especes": mode_paiement != "carte"})
    if proposition.status_code != 201:
        return proposition
    accord = compte.client.post(f"/api/propositions/{proposition.json()['id']}/accepter", json={"mode_paiement": mode_paiement})
    if accord.status_code != 201:
        return accord
    rdv = next(r for r in compte.client.get("/api/moi/rendez-vous").json() if r["id"] == accord.json()["rendez_vous_id"])
    return _Reponse(rdv | {"paiement_adresse": accord.json()["paiement_adresse"]})


def mails_a(mails_envoyes, compte) -> list[str]:
    return [m["sujet"] for m in mails_envoyes if m["a"] == compte.email]


def statut(compte, rdv_id: int, cote: str = "client") -> str:
    chemin = "/api/moi/rendez-vous" if cote == "client" else "/api/moi/prestataire/rendez-vous"
    return next(r for r in compte.client.get(chemin).json() if r["id"] == rdv_id)["statut"]


# ---------- Un rendez-vous naît d'une proposition acceptée ----------


def test_proposition_acceptee_rendez_vous_confirme(lea, dupont, mails_envoyes) -> None:
    # RM-RENDEZ-VOUS § « Sans annonces » : un rendez-vous naît seulement d'une proposition acceptée, confirmé aussitôt
    reponse = reserver(dupont, lea, a(MARDI, 10))

    assert reponse.status_code == 201 and reponse.json()["statut"] == "confirme"
    assert reponse.json()["prix_centimes"] == 5000 and reponse.json()["adresse"].startswith("8 allée des Pins")
    assert reponse.json()["titre"] == "Coiffeur / Coiffeuse"  # sans demande publiée : le métier de la proposition
    assert any("confirmé" in s for s in mails_a(mails_envoyes, dupont))
    assert any("Nouveau rendez-vous" in m["texte"] for m in mails_envoyes if m["a"] == lea.email)


def test_meme_horaire_ne_se_propose_pas_deux_fois(lea, dupont, fabrique_compte, client) -> None:
    petit = fabrique_compte()
    petit.client.post("/api/moi/adresse", json={"ligne": "3 rue du Moulin", "commune_id": id_commune(client, "33600", "Pessac"),
                                                "code_postal": "33600"})
    reserver(dupont, lea, a(MARDI, 10))

    deuxieme = reserver(petit, lea, a(MARDI, 10))

    assert deuxieme.status_code == 409 and "déjà un rendez-vous à cette heure-là" in deuxieme.json()["detail"]


def test_carte_refusee_sans_siret_verifie(lea, dupont) -> None:
    reponse = reserver(dupont, lea, a(MARDI, 10), mode_paiement="carte")

    assert reponse.status_code == 400 and "paiement" in reponse.json()["detail"]


def test_chez_le_client_sans_adresse(lea, fabrique_compte) -> None:
    sans_adresse = fabrique_compte()

    reponse = reserver(sans_adresse, lea, a(MARDI, 10))

    assert reponse.status_code == 400 and "votre adresse" in reponse.json()["detail"]


# ---------- Annuler ----------


def test_client_annule_dans_le_delai_pas_apres(lea, dupont, base: Session) -> None:
    rdv = reserver(dupont, lea, a(MARDI, 10)).json()
    ligne = base.get_one(RendezVous, rdv["id"])
    from app.modeles.comptes import Compte

    compte = base.get_one(Compte, dupont.id)
    trop_tard = datetime.fromisoformat(rdv["debut"]) - timedelta(hours=23)
    with pytest.raises(Exception, match="Moins de 24 h avant"):
        service.annuler_par_client(base, compte, ligne, trop_tard)
    base.rollback()

    ok = dupont.client.post(f"/api/moi/rendez-vous/{rdv['id']}/annuler")

    assert ok.status_code == 200 and ok.json()["statut"] == "annule_client"


def test_prestataire_annule_avec_un_motif_obligatoire(lea, dupont, mails_envoyes) -> None:
    rdv = reserver(dupont, lea, a(MARDI, 10)).json()
    chemin = f"/api/moi/prestataire/rendez-vous/{rdv['id']}/annuler"

    sans_motif = lea.client.post(chemin, json={})
    avec_motif = lea.client.post(chemin, json={"motif": "Malade, désolée"})

    assert sans_motif.status_code == 400 and "motif" in sans_motif.json()["detail"]
    assert avec_motif.json()["statut"] == "annule_prestataire"
    assert any("Malade, désolée" in m["texte"] for m in mails_envoyes if m["a"] == dupont.email)


def test_un_autre_ne_touche_pas_mes_rendez_vous(lea, dupont, fabrique_compte, fabrique_prestataire) -> None:  # noqa: F811
    rdv = reserver(dupont, lea, a(MARDI, 10)).json()
    curieux, karim = fabrique_compte(), fabrique_prestataire()

    assert curieux.client.post(f"/api/moi/rendez-vous/{rdv['id']}/annuler").status_code == 404
    assert karim.client.post(f"/api/moi/prestataire/rendez-vous/{rdv['id']}/annuler", json={"motif": "x"}).status_code == 404


# ---------- Rappel la veille ----------


def test_rappel_la_veille_a_18_h(lea, dupont, base: Session, mails_envoyes) -> None:
    rdv = reserver(dupont, lea, a(MARDI, 10)).json()
    veille_18h = datetime.combine(MARDI - timedelta(days=1), time(18), tzinfo=PARIS)

    service.traiter(base, veille_18h - timedelta(minutes=5))
    base.commit()
    avant = [s for s in mails_a(mails_envoyes, dupont) if "rappel" in s]
    service.traiter(base, veille_18h + timedelta(minutes=1))
    service.traiter(base, veille_18h + timedelta(minutes=6))  # une seule fois
    base.commit()

    assert avant == [] and len([s for s in mails_a(mails_envoyes, dupont) if "rappel" in s]) == 1
    assert rdv["id"]


# ---------- Coordonnées et réglages ----------


def test_coordonnees_visibles_seulement_apres_reservation(lea, dupont) -> None:
    rdv = reserver(dupont, lea, a(MARDI, 10)).json()
    vu_par_lea = next(r for r in lea.client.get("/api/moi/prestataire/rendez-vous").json() if r["id"] == rdv["id"])

    assert rdv["autre"]["telephone"] == "0600000000"  # le téléphone de Léa, pour Mme Dupont
    assert vu_par_lea["autre"]["nom"] == "Essai ZZTEST" and vu_par_lea["autre"]["telephone"] == "0600000000"
    assert vu_par_lea["adresse"].startswith("8 allée des Pins")


def test_reglages_delai_d_annulation(lea) -> None:
    mauvais = lea.client.post("/api/moi/prestataire/rendez-vous/reglages", json={"annulation_delai_heures": 5})
    bon = lea.client.post("/api/moi/prestataire/rendez-vous/reglages", json={"annulation_delai_heures": 48})

    assert mauvais.status_code == 400
    assert bon.json() == {"annulation_delai_heures": 48}
    assert lea.client.get("/api/moi/prestataire/rendez-vous/reglages").json() == {"annulation_delai_heures": 48}


def test_mes_donnees_contiennent_mes_rendez_vous(lea, dupont) -> None:
    reserver(dupont, lea, a(MARDI, 10))

    assert dupont.client.get("/api/moi/donnees").json()["mes_rendez_vous"][0]["titre"] == "Coiffeur / Coiffeuse"


def test_moment_du_rappel_jour_meme() -> None:
    rdv = RendezVous(debut=datetime(2026, 10, 14, 16, 0, tzinfo=UTC), cree_le=datetime(2026, 10, 14, 7, 0, tzinfo=UTC))

    assert service.moment_du_rappel(rdv) == datetime(2026, 10, 14, 14, 0, tzinfo=UTC)  # pris le jour même : 2 h avant
