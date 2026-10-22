"""Ma carte de visite (lot 10.4, regles-metier/RM-CARTE-VISITE.md) : aperçu, planche de 10 cartes, carte seule, verrous."""

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services import carte_visite
from tests.test_agenda import MARDI, lea  # noqa: F401 (fixtures)
from tests.test_avis import noter, rdv_tenu  # noqa: F401 (fixtures)
from tests.test_prestataires import fabrique_prestataire, metiers, siret_verifie  # noqa: F401 (fixtures)
from tests.test_rendez_vous import dupont  # noqa: F401 (fixtures)

CHEMIN = "/api/moi/prestataire/carte-de-visite"


def apercu(compte) -> dict:
    reponse = compte.client.get(CHEMIN)
    assert reponse.status_code == 200, reponse.text
    return reponse.json()


def pdf(compte, forme: str = "planche", telephone: bool = False):
    return compte.client.get(f"{CHEMIN}/pdf", params={"forme": forme, "telephone": str(telephone).lower()})


def test_il_faut_etre_connecte(client) -> None:
    assert client.get(CHEMIN).status_code == 401
    assert client.get(f"{CHEMIN}/pdf").status_code == 401


def test_pas_de_carte_sans_siret_verifie(fabrique_prestataire) -> None:  # noqa: F811
    # Raphael, 22/10/2026 : « pas de carte sans siret » → l'aperçu reste visible, les boutons sont verrouillés
    karim = fabrique_prestataire()
    assert apercu(karim)["raison"] == carte_visite.PAS_DE_SIRET
    refus = pdf(karim)
    assert refus.status_code == 403
    assert refus.json()["detail"] == carte_visite.PAS_DE_SIRET


def test_planche_de_10_cartes_et_carte_seule(fabrique_prestataire, base: Session) -> None:  # noqa: F811
    karim = fabrique_prestataire()
    siret_verifie(base, karim)
    vu = apercu(karim)
    assert vu["raison"] is None
    assert (vu["nom"], vu["metier"], vu["ville"], vu["note"]) == ("Karim Benali", "Plombier · Électricien", "Pessac", "Nouveau sur rafals")
    assert vu["telephone"] == "0600000000"  # le numéro du compte, proposé à côté de la case

    planche = pdf(karim)
    assert planche.status_code == 200
    assert planche.headers["content-type"] == "application/pdf"
    assert planche.headers["content-disposition"] == 'attachment; filename="carte-de-visite-karim-benali-planche.pdf"'
    assert planche.content.startswith(b"%PDF")
    assert planche.content.count(b"(Karim Benali)") == 10
    assert b"0600000000" not in planche.content  # le téléphone seulement si la case est cochée
    assert b"/MediaBox [0 0 595 842]" in planche.content  # A4

    carte = pdf(karim, "carte", telephone=True)
    assert carte.status_code == 200
    assert carte.headers["content-disposition"] == 'attachment; filename="carte-de-visite-karim-benali.pdf"'
    assert carte.content.count(b"(Karim Benali)") == 1
    assert b"(0600000000)" in carte.content
    assert b"/MediaBox [0 0 240.94 155.91]" in carte.content  # 8,5 × 5,5 cm


def test_telephone_demande_sans_numero_dans_le_compte(fabrique_prestataire, base: Session) -> None:  # noqa: F811
    karim = fabrique_prestataire()
    siret_verifie(base, karim)
    base.execute(text("UPDATE compte SET telephone = NULL WHERE id = :id"), {"id": karim.id})
    base.commit()
    assert apercu(karim)["telephone"] is None
    refus = pdf(karim, telephone=True)
    assert refus.status_code == 400
    assert refus.json()["detail"] == carte_visite.SANS_TELEPHONE
    assert pdf(karim).status_code == 200  # sans la case, la carte se télécharge


def test_pas_de_carte_quand_le_profil_est_en_pause(fabrique_prestataire, base: Session) -> None:  # noqa: F811
    karim = fabrique_prestataire()
    siret_verifie(base, karim)
    assert karim.client.post("/api/moi/prestataire/statut", json={"action": "pause"}).status_code == 200
    assert apercu(karim)["raison"] == carte_visite.PAS_ACTIF["en_pause"]
    assert pdf(karim).status_code == 403


def test_la_note_et_le_carre_vers_la_page_publique(lea, dupont, rdv_tenu, base: Session) -> None:  # noqa: F811
    siret_verifie(base, lea)
    assert noter(dupont, rdv_tenu, note=5).status_code == 201
    vu = apercu(lea)
    assert vu["note"] == "5,0/5 · 1 avis sur rafals"
    identifiant = lea.client.get("/api/moi/prestataire").json()["id"]
    assert vu["adresse"].endswith(f"/prestataires/{identifiant}")
    carre = lea.client.get(f"{CHEMIN}/carre.svg")
    assert carre.status_code == 200
    assert carre.headers["content-type"] == "image/svg+xml"
    assert carre.content.startswith(b"<svg")
    assert b'xmlns="http://www.w3.org/2000/svg"' in carre.content  # sinon le navigateur n'affiche pas l'image


def test_textes() -> None:
    assert carte_visite.texte_note(0, 0) == "Nouveau sur rafals"
    assert carte_visite.texte_note(110, 23) == "4,8/5 · 23 avis sur rafals"
    assert carte_visite.nom_de_fichier("Élodie D'Arc", planche=False) == "carte-de-visite-elodie-d-arc.pdf"
    assert carte_visite.nom_de_fichier("ZZTEST Net & Clair", planche=True) == "carte-de-visite-zztest-net-clair-planche.pdf"


# ---------- Couleur et petite phrase (schema_v33, 22/10/2026) ----------


def enregistrer(compte, couleur: str, phrase: str | None):
    return compte.client.post(CHEMIN, json={"couleur": couleur, "phrase": phrase})


def test_couleur_et_phrase_gardees_d_une_visite_a_l_autre(fabrique_prestataire, base: Session) -> None:  # noqa: F811
    karim = fabrique_prestataire()
    siret_verifie(base, karim)
    depart = apercu(karim)
    assert (depart["couleur"], depart["phrase"]) == ("vert", None)  # la carte d'avant
    assert [c["code"] for c in depart["couleurs"]] == ["vert", "bleu-nuit", "orange", "bordeaux", "violet", "noir"]

    reponse = enregistrer(karim, "bleu-nuit", "  Devis gratuit, intervention sous 48 h ")
    assert reponse.status_code == 200, reponse.text
    assert (reponse.json()["couleur"], reponse.json()["phrase"]) == ("bleu-nuit", "Devis gratuit, intervention sous 48 h")
    assert (apercu(karim)["couleur"], apercu(karim)["phrase"]) == ("bleu-nuit", "Devis gratuit, intervention sous 48 h")

    carte = pdf(karim, "carte")
    assert b"(Devis gratuit, intervention sous 48 h)" in carte.content
    assert b"0.114 0.227 0.373 rg" in carte.content  # le bleu nuit (#1D3A5F)
    assert b'stroke="#1d3a5f"' in karim.client.get(f"{CHEMIN}/carre.svg", params={"couleur": "bleu-nuit"}).content

    # Une phrase vide efface la phrase
    assert enregistrer(karim, "noir", "   ").json()["phrase"] is None


def test_le_pdf_prend_ce_qui_est_affiche_sans_l_enregistrer(fabrique_prestataire, base: Session) -> None:  # noqa: F811
    karim = fabrique_prestataire()
    siret_verifie(base, karim)
    carte = karim.client.get(f"{CHEMIN}/pdf", params={"forme": "carte", "couleur": "bordeaux", "phrase": "Depuis 1998"})
    assert carte.status_code == 200
    assert b"(Depuis 1998)" in carte.content
    assert apercu(karim)["couleur"] == "vert"  # rien n'est enregistré par un téléchargement


@pytest.mark.parametrize(("couleur", "phrase", "message"), [
    ("rose-bonbon", None, carte_visite.COULEUR_INCONNUE),
    ("vert", "x" * 41, "La petite phrase doit faire entre 1 et 40 caractères."),
])
def test_couleur_inconnue_ou_phrase_trop_longue(fabrique_prestataire, base: Session, couleur, phrase, message) -> None:  # noqa: F811
    karim = fabrique_prestataire()
    siret_verifie(base, karim)
    refus = enregistrer(karim, couleur, phrase)
    assert refus.status_code == 400
    assert refus.json()["detail"] == message
    assert apercu(karim)["couleur"] == "vert"


def test_pas_de_reglage_sans_siret(fabrique_prestataire) -> None:  # noqa: F811
    karim = fabrique_prestataire()
    refus = enregistrer(karim, "orange", "Bonjour")
    assert refus.status_code == 403
    assert refus.json()["detail"] == carte_visite.PAS_DE_SIRET
