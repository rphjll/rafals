"""Rendez-vous : réserver, confirmer, accepter / refuser / expirer, annuler, déplacer, rappels (RM-RENDEZ-VOUS.md ; lot 4.3)."""

from datetime import UTC, datetime, time, timedelta

import pytest
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.rendez_vous import RendezVous
from app.services import rendez_vous as service
from tests.test_agenda import LEA_MARDI, MARDI, heures, lea  # noqa: F401 (fixtures)
from tests.test_annonces import fabrique_prestataire, menage, metiers, publier  # noqa: F401 (fixtures)
from tests.test_prestataires import id_commune

PARIS = reglages.FUSEAU_AFFICHAGE


def a(jour, h: int, m: int = 0) -> str:
    """Mardi à 10 h, heure de Paris, au format envoyé par l'écran."""
    return datetime.combine(jour, time(h, m), tzinfo=PARIS).isoformat()


@pytest.fixture
def dupont(fabrique_compte, client):
    """Mme Dupont, cliente, avec son adresse à Talence (les annonces de Léa ont lieu chez le client)."""
    compte = fabrique_compte()
    compte.client.post("/api/moi/adresse", json={"ligne": "8 allée des Pins", "commune_id": id_commune(client, "33400", "Talence"),
                                                 "code_postal": "33400"})
    return compte


def reserver(compte, annonce_id: int, debut: str, **autres):
    return compte.client.post("/api/rendez-vous", json={"annonce_id": annonce_id, "debut": debut, **autres})


def mails_a(mails_envoyes, compte) -> list[str]:
    return [m["sujet"] for m in mails_envoyes if m["a"] == compte.email]


def statut(compte, rdv_id: int, cote: str = "client") -> str:
    chemin = "/api/moi/rendez-vous" if cote == "client" else "/api/moi/prestataire/rendez-vous"
    return next(r for r in compte.client.get(chemin).json() if r["id"] == rdv_id)["statut"]


# ---------- Réserver ----------


def test_confirmation_automatique_et_horaire_pris(lea, dupont, client, mails_envoyes) -> None:
    reponse = reserver(dupont, lea.annonce, a(MARDI, 10))
    libres = heures(client, lea.annonce)

    assert reponse.status_code == 201 and reponse.json()["statut"] == "confirme"
    assert reponse.json()["prix_centimes"] == 5000 and reponse.json()["adresse"].startswith("8 allée des Pins")
    assert any("confirmé" in s for s in mails_a(mails_envoyes, dupont))
    assert any("Nouveau rendez-vous" in m["texte"] for m in mails_envoyes if m["a"] == lea.email)
    # La coupe 10 h 00-10 h 45 est prise : ni 9 h 30 (finirait à 10 h 15) ni 10 h 30 ne sont libres
    assert "09:15" in libres and "09:30" not in libres and "10:30" not in libres and "10:45" in libres


def test_meme_horaire_ne_se_prend_pas_deux_fois(lea, dupont, fabrique_compte, client) -> None:
    petit = fabrique_compte()
    petit.client.post("/api/moi/adresse", json={"ligne": "3 rue du Moulin", "commune_id": id_commune(client, "33600", "Pessac"),
                                                "code_postal": "33600"})
    reserver(dupont, lea.annonce, a(MARDI, 10))

    deuxieme = reserver(petit, lea.annonce, a(MARDI, 10))

    assert deuxieme.status_code == 409 and "vient d'être pris" in deuxieme.json()["detail"]


def test_la_pause_du_prestataire_est_respectee(lea, dupont, client) -> None:
    lea.client.post("/api/moi/agenda/reglages", json={"pas_minutes": 15, "pause_minutes": 30, "delai_min_minutes": 120,
                                                      "delai_max_mois": 2})
    reserver(dupont, lea.annonce, a(MARDI, 10))

    libres = heures(client, lea.annonce)

    # 10 h 00-10 h 45 + 30 min de pause : prochain début 11 h 15 ; avant : la coupe doit finir à 9 h 30 (début 8 h 45 → 9 h)
    assert "11:15" in libres and "11:00" not in libres
    assert "09:00" not in libres  # 9 h 00-9 h 45, puis 30 min de pause → 10 h 15 > 10 h 00


def test_valeurs_recopiees_a_la_reservation(lea, dupont, metiers) -> None:  # noqa: F811
    rdv = reserver(dupont, lea.annonce, a(MARDI, 10)).json()
    lea.client.post(f"/api/moi/annonces/{lea.annonce}/modifier", json=menage(metiers["Coiffeur"], titre="Coupe femme", duree_minutes=45,
                                                                             prix_centimes=5500))

    assert next(r for r in dupont.client.get("/api/moi/rendez-vous").json() if r["id"] == rdv["id"])["prix_centimes"] == 5000


def test_prix_a_l_heure_multiplie(fabrique_prestataire, dupont, metiers) -> None:  # noqa: F811
    sonia = fabrique_prestataire()
    sonia.client.post("/api/moi/agenda/semaine", json={"plages": LEA_MARDI})
    annonce = publier(sonia, menage(metiers["Plombier"], titre="Ménage", forme_prix="heure", prix_centimes=2500,
                                    duree_minutes=None, heures_min=2, heures_max=4)).json()["id"]

    rdv = reserver(dupont, annonce, a(MARDI, 9), heures=3).json()

    assert rdv["prix_centimes"] == 7500 and rdv["heures"] == 3
    assert datetime.fromisoformat(rdv["fin"]) - datetime.fromisoformat(rdv["debut"]) == timedelta(hours=3)


@pytest.mark.parametrize(("cas", "morceau"), [("propre", "propre annonce"), ("carte", "paiement"), ("hors", "choisissez-en un autre")])
def test_reservations_refusees(lea, dupont, cas, morceau) -> None:
    if cas == "propre":
        reponse = reserver(lea, lea.annonce, a(MARDI, 10))
    elif cas == "carte":
        reponse = reserver(dupont, lea.annonce, a(MARDI, 10), mode_paiement="carte")
    else:
        reponse = reserver(dupont, lea.annonce, a(MARDI, 13))  # entre les deux plages : fermé

    assert reponse.status_code in (400, 409) and morceau in reponse.json()["detail"]


def test_chez_le_client_sans_adresse(lea, fabrique_compte) -> None:
    sans_adresse = fabrique_compte()

    reponse = reserver(sans_adresse, lea.annonce, a(MARDI, 10))

    assert reponse.status_code == 400 and "votre adresse" in reponse.json()["detail"]


# ---------- « J'accepte chaque demande » ----------


def demandes(lea) -> None:
    lea.client.post("/api/moi/prestataire/rendez-vous/reglages", json={"confirmation_automatique": False, "annulation_delai_heures": 24})


def test_demande_en_attente_garde_l_horaire_puis_acceptee(lea, dupont, client) -> None:
    demandes(lea)
    rdv = reserver(dupont, lea.annonce, a(MARDI, 10)).json()

    assert rdv["statut"] == "en_attente" and rdv["reponse_avant"] is not None
    assert "10:00" not in heures(client, lea.annonce)  # l'horaire est gardé pendant l'attente
    assert rdv["autre"]["telephone"] is None  # pas encore de téléphone avant confirmation
    accepte = lea.client.post(f"/api/moi/prestataire/rendez-vous/{rdv['id']}/accepter", json={})
    assert accepte.json()["statut"] == "confirme"
    assert next(r for r in dupont.client.get("/api/moi/rendez-vous").json() if r["id"] == rdv["id"])["autre"]["telephone"]


def test_demande_refusee_libere_l_horaire(lea, dupont, client, mails_envoyes) -> None:
    demandes(lea)
    rdv = reserver(dupont, lea.annonce, a(MARDI, 10)).json()

    lea.client.post(f"/api/moi/prestataire/rendez-vous/{rdv['id']}/refuser", json={"motif": "Déjà pris ce jour-là"})

    assert statut(dupont, rdv["id"]) == "refuse" and "10:00" in heures(client, lea.annonce)
    assert any("Déjà pris" in m["texte"] for m in mails_envoyes if m["a"] == dupont.email)


def test_sans_reponse_rappel_puis_expiree(lea, dupont, base: Session, mails_envoyes, client) -> None:
    # RM-RENDEZ-VOUS : rappel au prestataire 2 h avant la fin des 24 h, puis la demande expire
    demandes(lea)
    rdv = reserver(dupont, lea.annonce, a(MARDI, 10)).json()
    limite = datetime.fromisoformat(rdv["reponse_avant"])

    service.traiter(base, limite - timedelta(hours=1))
    base.commit()
    rappel = [m for m in mails_envoyes if m["a"] == lea.email and "attend votre réponse" in m["sujet"]]
    service.traiter(base, limite + timedelta(minutes=1))
    base.commit()

    assert len(rappel) == 1
    assert statut(dupont, rdv["id"]) == "expire" and "10:00" in heures(client, lea.annonce)
    assert any("n'a pas répondu" in m["texte"] for m in mails_envoyes if m["a"] == dupont.email)
    assert lea.client.post(f"/api/moi/prestataire/rendez-vous/{rdv['id']}/accepter", json={}).status_code == 400


# ---------- Annuler ----------


def test_client_annule_dans_le_delai_pas_apres(lea, dupont, base: Session) -> None:
    rdv = reserver(dupont, lea.annonce, a(MARDI, 10)).json()
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
    rdv = reserver(dupont, lea.annonce, a(MARDI, 10)).json()
    chemin = f"/api/moi/prestataire/rendez-vous/{rdv['id']}/annuler"

    sans_motif = lea.client.post(chemin, json={})
    avec_motif = lea.client.post(chemin, json={"motif": "Malade, désolée"})

    assert sans_motif.status_code == 400 and "motif" in sans_motif.json()["detail"]
    assert avec_motif.json()["statut"] == "annule_prestataire"
    assert any("Malade, désolée" in m["texte"] for m in mails_envoyes if m["a"] == dupont.email)


def test_un_autre_ne_touche_pas_mes_rendez_vous(lea, dupont, fabrique_compte, fabrique_prestataire) -> None:  # noqa: F811
    rdv = reserver(dupont, lea.annonce, a(MARDI, 10)).json()
    curieux, karim = fabrique_compte(), fabrique_prestataire()

    assert curieux.client.post(f"/api/moi/rendez-vous/{rdv['id']}/annuler").status_code == 404
    assert karim.client.post(f"/api/moi/prestataire/rendez-vous/{rdv['id']}/annuler", json={"motif": "x"}).status_code == 404


# ---------- Déplacer ----------


def test_deplacer_confirmation_automatique(lea, dupont, client) -> None:
    rdv = reserver(dupont, lea.annonce, a(MARDI, 10)).json()

    nouveau = dupont.client.post(f"/api/moi/rendez-vous/{rdv['id']}/deplacer", json={"debut": a(MARDI, 14)}).json()

    assert nouveau["statut"] == "confirme" and nouveau["remplace_id"] == rdv["id"] and nouveau["prix_centimes"] == 5000
    assert statut(dupont, rdv["id"]) == "deplace"
    libres = heures(client, lea.annonce)
    assert "10:00" in libres and "14:00" not in libres


def test_deplacer_avec_accord_l_ancien_tient_jusqu_a_l_accord(lea, dupont, client) -> None:
    rdv = reserver(dupont, lea.annonce, a(MARDI, 10)).json()
    demandes(lea)

    nouveau = dupont.client.post(f"/api/moi/rendez-vous/{rdv['id']}/deplacer", json={"debut": a(MARDI, 14)}).json()
    avant_accord = statut(dupont, rdv["id"])
    lea.client.post(f"/api/moi/prestataire/rendez-vous/{nouveau['id']}/accepter", json={})

    assert nouveau["statut"] == "en_attente" and avant_accord == "confirme"
    assert statut(dupont, rdv["id"]) == "deplace" and statut(dupont, nouveau["id"]) == "confirme"


def test_deplacer_un_peu_plus_tard_sur_son_propre_horaire(lea, dupont) -> None:
    rdv = reserver(dupont, lea.annonce, a(MARDI, 10)).json()

    nouveau = dupont.client.post(f"/api/moi/rendez-vous/{rdv['id']}/deplacer", json={"debut": a(MARDI, 10, 15)})

    assert nouveau.status_code == 200  # son propre horaire ne le bloque pas


# ---------- Rappel la veille ----------


def test_rappel_la_veille_a_18_h(lea, dupont, base: Session, mails_envoyes) -> None:
    rdv = reserver(dupont, lea.annonce, a(MARDI, 10)).json()
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
    rdv = reserver(dupont, lea.annonce, a(MARDI, 10)).json()
    vu_par_lea = next(r for r in lea.client.get("/api/moi/prestataire/rendez-vous").json() if r["id"] == rdv["id"])

    assert rdv["autre"]["telephone"] == "0600000000"  # le téléphone de Léa, pour Mme Dupont
    assert vu_par_lea["autre"]["nom"] == "Essai ZZTEST" and vu_par_lea["autre"]["telephone"] == "0600000000"
    assert vu_par_lea["adresse"].startswith("8 allée des Pins")


def test_reglages_delai_d_annulation(lea) -> None:
    mauvais = lea.client.post("/api/moi/prestataire/rendez-vous/reglages", json={"confirmation_automatique": True,
                                                                                  "annulation_delai_heures": 5})
    bon = lea.client.post("/api/moi/prestataire/rendez-vous/reglages", json={"confirmation_automatique": False,
                                                                              "annulation_delai_heures": 48})

    assert mauvais.status_code == 400
    assert bon.json() == {"confirmation_automatique": False, "annulation_delai_heures": 48}


def test_mes_donnees_contiennent_mes_rendez_vous(lea, dupont) -> None:
    reserver(dupont, lea.annonce, a(MARDI, 10))

    assert dupont.client.get("/api/moi/donnees").json()["mes_rendez_vous"][0]["titre"] == "Coupe femme"


def test_moment_du_rappel_jour_meme() -> None:
    rdv = RendezVous(debut=datetime(2026, 10, 14, 16, 0, tzinfo=UTC), cree_le=datetime(2026, 10, 14, 7, 0, tzinfo=UTC))

    assert service.moment_du_rappel(rdv) == datetime(2026, 10, 14, 14, 0, tzinfo=UTC)  # pris le jour même : 2 h avant
