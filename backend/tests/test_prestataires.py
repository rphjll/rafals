"""Profil prestataire (RM-PRESTATAIRES.md, RM-COMPTES.md ; lot 2.3)."""

from datetime import datetime

import pytest
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.prestataires import Commune
from app.services.communes import distance_km
from app.services.prestataires import siret_valide

JPG = b"\xff\xd8\xff\xe0" + b"photo" * 100
PDF = b"%PDF-1.4 pas une photo"


def id_metier(client, nom: str) -> int:
    return next(m["id"] for m in client.get("/api/metiers/recherche", params={"q": nom}).json() if m["nom"] == nom)


def id_commune(client, texte: str, nom: str) -> int:
    return next(c["id"] for c in client.get("/api/communes/recherche", params={"q": texte}).json() if c["nom"] == nom)


@pytest.fixture
def profil_karim(client) -> dict:
    """Karim : plombier (principal), électricien (secondaire), Pessac, 15 km, sans SIRET."""
    return {
        "nom_affiche": "Karim Benali — Plomberie",
        "metier_principal_id": id_metier(client, "Plombier"),
        "commune_id": id_commune(client, "33600", "Pessac"),
        "distance_km": 15,
        "presentation": "Dépannages rapides, devis gratuit.",
        "metiers_secondaires": [id_metier(client, "Électricien")],
    }


def devenir(compte, profil: dict):
    return compte.client.post("/api/moi/prestataire", json=profil)


# ---------- Outils repris par les autres fichiers de tests ----------

AUJOURD_HUI = datetime.now(reglages.FUSEAU_AFFICHAGE).date()


@pytest.fixture
def metiers(client) -> dict[str, int]:
    noms = {"Plombier": "Plombier", "Électricien": "Électricien", "Coiffeur": "Coiffeur / Coiffeuse", "Maçon": "Maçon"}
    return {court: id_metier(client, nom) for court, nom in noms.items()}


@pytest.fixture
def fabrique_prestataire(fabrique_compte, client, metiers):
    """Un prestataire d'essai : Karim, plombier (principal) et électricien (secondaire), Pessac, sans SIRET."""

    def fabriquer(principal: str = "Plombier", secondaires: tuple[str, ...] = ("Électricien",)):
        compte = fabrique_compte()
        reponse = devenir(compte, {
            "nom_affiche": "Karim Benali", "metier_principal_id": metiers[principal],
            "commune_id": id_commune(client, "33600", "Pessac"), "distance_km": 15,
            "metiers_secondaires": [metiers[m] for m in secondaires],
        })
        assert reponse.status_code == 201, reponse.text
        return compte

    return fabriquer


def siret_verifie(base: Session, compte) -> None:
    base.execute(text("UPDATE prestataire SET siret = '44306184100047', siret_statut = 'verifie' WHERE compte_id = :id"),
                 {"id": compte.id})
    base.commit()


def carte_activee(base: Session, compte) -> None:
    """Comme si Stripe avait vérifié son compte (lot 5.1) : ses propositions peuvent accepter la carte."""
    base.execute(text("UPDATE prestataire SET stripe_compte = 'acct_zztest_' || id, stripe_pret = true WHERE compte_id = :id"),
                 {"id": compte.id})
    base.commit()


# ---------- Communes et distances ----------


def test_zone_d_intervention_a_vol_d_oiseau(base: Session) -> None:
    # RM-PRESTATAIRES : « Pessac, jusqu'à 15 km » → Talence dans le rayon, Libourne non
    commune = lambda code: base.scalar(select(Commune).where(Commune.code_insee == code))  # noqa: E731
    pessac, talence, libourne = commune("33318"), commune("33522"), commune("33243")

    assert distance_km(pessac, talence) < 15
    assert distance_km(pessac, libourne) > 15


def test_recherche_de_commune_par_nom_ou_code_postal(client) -> None:
    par_code = [c["nom"] for c in client.get("/api/communes/recherche", params={"q": "33600"}).json()]
    par_nom = [c["nom"] for c in client.get("/api/communes/recherche", params={"q": "st emilion"}).json()]

    assert par_code == ["Pessac"]
    assert "Saint-Émilion" in par_nom


# ---------- Devenir prestataire ----------


def test_karim_propose_ses_services(fabrique_compte, profil_karim) -> None:
    karim = fabrique_compte()

    reponse = devenir(karim, profil_karim)

    assert reponse.status_code == 201
    profil = reponse.json()
    assert profil["metier_principal"]["nom"] == "Plombier"
    assert [m["nom"] for m in profil["metiers_secondaires"]] == ["Électricien"]
    assert profil["commune"]["nom"] == "Pessac" and profil["distance_km"] == 15
    assert profil["siret_statut"] == "absent" and profil["statut"] == "actif"
    assert karim.client.get("/api/moi").json()["prestataire_id"] == profil["id"]


# ---------- Lieu des services (RM-PRESTATAIRES § « Sans annonces », lot 9.1) ----------


def _adresse(compte, commune_id: int):
    return compte.client.post("/api/moi/adresse", json={"ligne": "3 rue du Moulin", "commune_id": commune_id, "code_postal": "33600"})


def test_lieu_chez_le_client_au_depart(fabrique_compte, profil_karim) -> None:
    profil = devenir(fabrique_compte(), profil_karim).json()

    assert profil["lieu"] == "chez_client"


def test_lieu_chez_moi_demande_une_adresse(fabrique_compte, profil_karim) -> None:
    # Léa, coiffeuse, reçoit au salon : sans « Mon adresse », refusé ; avec, accepté
    lea = fabrique_compte()

    sans_adresse = devenir(lea, profil_karim | {"lieu": "chez_moi"})
    _adresse(lea, profil_karim["commune_id"])
    avec_adresse = devenir(lea, profil_karim | {"lieu": "chez_moi"})

    assert sans_adresse.status_code == 400 and "Mon adresse" in sans_adresse.json()["detail"]
    assert avec_adresse.status_code == 201 and avec_adresse.json()["lieu"] == "chez_moi"


def test_lieu_modifiable_et_inconnu_refuse(fabrique_compte, profil_karim) -> None:
    karim = fabrique_compte()
    devenir(karim, profil_karim)
    _adresse(karim, profil_karim["commune_id"])

    les_deux = karim.client.post("/api/moi/prestataire/modifier", json=profil_karim | {"lieu": "les_deux"})
    inconnu = karim.client.post("/api/moi/prestataire/modifier", json=profil_karim | {"lieu": "sur_la_lune"})

    assert les_deux.json()["lieu"] == "les_deux"
    assert inconnu.status_code == 400
    assert karim.client.get("/api/moi/prestataire").json()["lieu"] == "les_deux"


def test_adresse_gardee_tant_que_les_clients_viennent_chez_moi(fabrique_compte, profil_karim) -> None:
    lea = fabrique_compte()
    _adresse(lea, profil_karim["commune_id"])
    devenir(lea, profil_karim | {"lieu": "chez_moi"})

    refuse = lea.client.post("/api/moi/adresse/effacer")
    lea.client.post("/api/moi/prestataire/modifier", json=profil_karim | {"lieu": "chez_client"})
    accepte = lea.client.post("/api/moi/adresse/effacer")

    assert refuse.status_code == 400 and "lieu de vos services" in refuse.json()["detail"]
    assert accepte.status_code == 200 and lea.client.get("/api/moi/adresse").json() is None


def test_page_publique_dit_le_lieu(fabrique_compte, profil_karim, client) -> None:
    lea = fabrique_compte()
    _adresse(lea, profil_karim["commune_id"])
    profil = devenir(lea, profil_karim | {"lieu": "les_deux"}).json()

    publique = client.get(f"/api/prestataires/{profil['id']}").json()

    assert publique["lieu"] == "les_deux"


def test_adresse_non_verifiee_refusee(fabrique_compte, profil_karim) -> None:
    karim = fabrique_compte(verifie=False)

    reponse = devenir(karim, profil_karim)

    assert reponse.status_code == 403
    assert "Vérifiez d'abord votre adresse mail" in reponse.json()["detail"]


def test_lucas_16_ans_sans_accord_refuse(fabrique_compte, profil_karim) -> None:
    lucas = fabrique_compte(age=16)

    reponse = devenir(lucas, profil_karim)

    assert reponse.status_code == 403
    assert "accord de tes parents" in reponse.json()["detail"]


def test_un_seul_profil_par_compte(fabrique_compte, profil_karim) -> None:
    karim = fabrique_compte()
    devenir(karim, profil_karim)

    reponse = devenir(karim, profil_karim)

    assert reponse.status_code == 409


@pytest.mark.parametrize(
    ("modif", "message"),
    [
        ({"distance_km": 0}, "entre 1 et 100 km"),
        ({"distance_km": 101}, "entre 1 et 100 km"),
        ({"nom_affiche": "K"}, "entre 2 et 80 caractères"),
        ({"presentation": "x" * 1001}, "au plus 1000 caractères"),
        ({"commune_id": 999999999}, "Choisissez votre ville"),
        ({"siret": "123 456 789 01234"}, "Ce SIRET n'est pas valide"),
    ],
)
def test_champs_controles(fabrique_compte, profil_karim, modif, message) -> None:
    karim = fabrique_compte()

    reponse = devenir(karim, profil_karim | modif)

    assert reponse.status_code == 400
    assert message in reponse.json()["detail"]


def test_metier_principal_pas_aussi_secondaire(fabrique_compte, profil_karim) -> None:
    karim = fabrique_compte()

    reponse = devenir(karim, profil_karim | {"metiers_secondaires": [profil_karim["metier_principal_id"]]})

    assert reponse.status_code == 400
    assert reponse.json()["detail"] == "Votre métier principal ne peut pas être aussi un métier secondaire."


def test_au_plus_5_metiers_secondaires(fabrique_compte, profil_karim, client) -> None:
    karim = fabrique_compte()
    six = [id_metier(client, n) for n in ("Électricien", "Chauffagiste", "Serrurier", "Vitrier", "Ramoneur", "Carreleur")]

    reponse = devenir(karim, profil_karim | {"metiers_secondaires": six})

    assert reponse.status_code == 400
    assert "Au plus 5" in reponse.json()["detail"]


# ---------- SIRET (format ; la vérification auprès de l'État arrive au lot 2.4) ----------


def test_cle_de_controle_du_siret() -> None:
    assert siret_valide("44306184100047")
    assert not siret_valide("44306184100048")  # dernier chiffre faux
    assert not siret_valide("4430618410004")  # 13 chiffres


def test_siret_saisi_avec_espaces_puis_retire(fabrique_compte, profil_karim) -> None:
    julie = fabrique_compte()

    avec = devenir(julie, profil_karim | {"siret": "443 061 841 00047"}).json()
    sans = julie.client.post("/api/moi/prestataire/modifier", json=profil_karim | {"siret": ""}).json()

    assert avec["siret"] == "44306184100047" and avec["siret_statut"] == "a_verifier"
    assert sans["siret"] is None and sans["siret_statut"] == "absent"


# ---------- Modifier, pause, arrêt ----------


def test_modifier_son_profil_est_note_au_journal(fabrique_compte, profil_karim, client, base: Session) -> None:
    karim = fabrique_compte()
    identifiant = devenir(karim, profil_karim).json()["id"]

    reponse = karim.client.post(
        "/api/moi/prestataire/modifier",
        json=profil_karim | {"distance_km": 25, "commune_id": id_commune(client, "33400", "Talence"), "metiers_secondaires": []},
    )
    actions = base.execute(
        text("SELECT action FROM journal_action WHERE table_cible = 'prestataire' AND ligne_id = :id ORDER BY id"),
        {"id": identifiant},
    ).scalars().all()

    assert reponse.json()["commune"]["nom"] == "Talence" and reponse.json()["metiers_secondaires"] == []
    assert actions == ["devenir_prestataire", "modifier_profil_prestataire"]


def test_pause_puis_reprise(fabrique_compte, profil_karim) -> None:
    # RM-PRESTATAIRES : Julie se met en pause pour ses congés, puis reprend
    julie = fabrique_compte()
    devenir(julie, profil_karim)
    statut = lambda action: julie.client.post("/api/moi/prestataire/statut", json={"action": action})  # noqa: E731

    pause = statut("pause")
    deuxieme_pause = statut("pause")
    reprise = statut("reprendre")

    assert pause.json()["statut"] == "en_pause"
    assert deuxieme_pause.status_code == 400 and deuxieme_pause.json()["detail"] == "Votre profil est déjà en pause."
    assert reprise.json()["statut"] == "actif"


def test_arret_definitif(fabrique_compte, profil_karim) -> None:
    julie = fabrique_compte()
    devenir(julie, profil_karim)

    arret = julie.client.post("/api/moi/prestataire/statut", json={"action": "arreter"})
    reprise = julie.client.post("/api/moi/prestataire/statut", json={"action": "reprendre"})
    modification = julie.client.post("/api/moi/prestataire/modifier", json=profil_karim)

    assert arret.json()["statut"] == "arrete"
    assert reprise.status_code == modification.status_code == 400
    assert "activité est arrêtée" in modification.json()["detail"]


# ---------- Blocage par l'administrateur ----------


def test_blocage_par_l_administrateur(fabrique_compte, profil_karim) -> None:
    admin = fabrique_compte(administrateur=True)
    faux = fabrique_compte()
    identifiant = devenir(faux, profil_karim).json()["id"]

    bloque = admin.client.post(f"/api/admin/prestataires/{identifiant}/blocage", json={"bloque": True})
    tentative = faux.client.post("/api/moi/prestataire/statut", json={"action": "reprendre"})
    debloque = admin.client.post(f"/api/admin/prestataires/{identifiant}/blocage", json={"bloque": False})

    assert bloque.json()["statut"] == "bloque"
    assert tentative.status_code == 403 and "bloqué par l'administrateur" in tentative.json()["detail"]
    assert debloque.json()["statut"] == "actif"
    assert identifiant in [p["id"] for p in admin.client.get("/api/admin/prestataires").json()]


def test_seul_un_administrateur_bloque(fabrique_compte, profil_karim) -> None:
    karim = fabrique_compte()
    identifiant = devenir(karim, profil_karim).json()["id"]

    assert karim.client.post(f"/api/admin/prestataires/{identifiant}/blocage", json={"bloque": True}).status_code == 403
    assert karim.client.get("/api/admin/prestataires").status_code == 403


# ---------- Photo ----------


def test_photo_jpg_acceptee_et_visible(fabrique_compte, profil_karim, client) -> None:
    karim = fabrique_compte()
    identifiant = devenir(karim, profil_karim).json()["id"]

    depot = karim.client.post("/api/moi/prestataire/photo", files={"fichier": ("karim.jpg", JPG, "image/jpeg")})
    vue = client.get(f"/api/prestataires/{identifiant}/photo")

    assert depot.json()["a_une_photo"] is True
    assert vue.status_code == 200 and vue.content == JPG


def test_photos_de_travaux_ajout_rang_et_retrait(fabrique_compte, profil_karim, client) -> None:
    # RM-PRESTATAIRES § « Sans annonces » : des photos de son travail sur le profil, visibles par tous
    karim = fabrique_compte()
    identifiant = devenir(karim, profil_karim).json()["id"]
    autre = b"\xff\xd8\xff\xe0" + b"salle de bain" * 50

    karim.client.post("/api/moi/prestataire/photos", files={"fichier": ("cuisine.jpg", JPG, "image/jpeg")})
    depot = karim.client.post("/api/moi/prestataire/photos", files={"fichier": ("bain.jpg", autre, "image/jpeg")})

    assert depot.status_code == 200 and depot.json()["photos"] == [1, 2]
    assert depot.json()["a_une_photo"] is False  # la photo de profil est une autre rubrique
    assert client.get(f"/api/prestataires/{identifiant}").json()["photos"] == [1, 2]
    assert client.get(f"/api/prestataires/{identifiant}/photos/2").content == autre

    retrait = karim.client.post("/api/moi/prestataire/photos/1/retirer")

    assert retrait.status_code == 200 and retrait.json()["photos"] == [1]  # la n° 2 est remontée d'un rang
    assert client.get(f"/api/prestataires/{identifiant}/photos/1").content == autre
    assert client.get(f"/api/prestataires/{identifiant}/photos/2").status_code == 404
    assert karim.client.post("/api/moi/prestataire/photos/5/retirer").status_code == 404


def test_photos_de_travaux_10_au_plus_et_formats(fabrique_compte, profil_karim, monkeypatch) -> None:
    monkeypatch.setattr(reglages, "PRESTATAIRE_PHOTOS_MAX", 2)
    karim = fabrique_compte()
    devenir(karim, profil_karim)

    refus_pdf = karim.client.post("/api/moi/prestataire/photos", files={"fichier": ("cv.pdf", PDF, "application/pdf")})
    for _ in range(2):
        assert karim.client.post("/api/moi/prestataire/photos", files={"fichier": ("a.jpg", JPG, "image/jpeg")}).status_code == 200
    de_trop = karim.client.post("/api/moi/prestataire/photos", files={"fichier": ("a.jpg", JPG, "image/jpeg")})

    assert refus_pdf.status_code == 400 and "envoyez un JPG, PNG" in refus_pdf.json()["detail"]
    assert de_trop.status_code == 400 and "Au plus 2 photos" in de_trop.json()["detail"]


def test_photos_de_travaux_cachees_en_pause_sauf_pour_leur_auteur(fabrique_compte, profil_karim, client) -> None:
    karim = fabrique_compte()
    identifiant = devenir(karim, profil_karim).json()["id"]
    karim.client.post("/api/moi/prestataire/photos", files={"fichier": ("cuisine.jpg", JPG, "image/jpeg")})
    karim.client.post("/api/moi/prestataire/statut", json={"action": "pause"})

    assert client.get(f"/api/prestataires/{identifiant}/photos/1").status_code == 404
    assert karim.client.get(f"/api/prestataires/{identifiant}/photos/1").status_code == 200
    assert fabrique_compte().client.post("/api/moi/prestataire/photos",
                                         files={"fichier": ("a.jpg", JPG, "image/jpeg")}).status_code == 404  # pas prestataire


def test_photo_pdf_refusee(fabrique_compte, profil_karim) -> None:
    karim = fabrique_compte()
    devenir(karim, profil_karim)

    reponse = karim.client.post("/api/moi/prestataire/photo", files={"fichier": ("cv.pdf", PDF, "application/pdf")})

    assert reponse.status_code == 400
    assert "envoyez un JPG, PNG" in reponse.json()["detail"]
