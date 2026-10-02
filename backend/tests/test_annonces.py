"""Annonces, local du prestataire, dates de fin de métier (RM-ANNONCES.md ; lot 3.1)."""

from datetime import UTC, date, datetime, timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import reglages
from app.services.prestataires import appliquer_fins_de_metier
from tests.test_prestataires import JPG, PDF, devenir, id_commune, id_metier

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


def menage(metier_id: int, **modifs) -> dict:
    """« Dépannage fuite — 50 € — 2 h — chez le client — espèces »."""
    return {"metier_id": metier_id, "titre": "Dépannage fuite", "forme_prix": "fixe", "prix_centimes": 5000,
            "duree_minutes": 120, "lieu": "chez_client", "paiement_especes": True} | modifs


def publier(compte, donnees: dict):
    return compte.client.post("/api/moi/annonces", json=donnees)


def siret_verifie(base: Session, compte) -> None:
    base.execute(text("UPDATE prestataire SET siret = '44306184100047', siret_statut = 'verifie' WHERE compte_id = :id"),
                 {"id": compte.id})
    base.commit()


def carte_activee(base: Session, compte) -> None:
    """Comme si Stripe avait vérifié son compte (lot 5.1) : ses annonces peuvent proposer la carte."""
    base.execute(text("UPDATE prestataire SET stripe_compte = 'acct_zztest_' || id, stripe_pret = true WHERE compte_id = :id"),
                 {"id": compte.id})
    base.commit()


# ---------- Écrire une annonce ----------


def test_les_trois_formes_de_prix(fabrique_prestataire, metiers) -> None:
    karim = fabrique_prestataire()

    fixe = publier(karim, menage(metiers["Plombier"]))
    heure = publier(karim, menage(metiers["Plombier"], titre="Dépannage à l'heure", forme_prix="heure", prix_centimes=4000,
                                  duree_minutes=None, heures_min=1, heures_max=3))
    devis = publier(karim, menage(metiers["Électricien"], titre="Tableau électrique", forme_prix="devis", prix_centimes=None,
                                  duree_minutes=None))

    assert fixe.status_code == 201 and fixe.json()["duree_minutes"] == 120
    assert heure.status_code == 201 and (heure.json()["heures_min"], heure.json()["heures_max"]) == (1, 3)
    assert heure.json()["duree_minutes"] is None
    assert devis.status_code == 201 and devis.json()["prix_centimes"] is None and devis.json()["duree_minutes"] is None


@pytest.mark.parametrize(("modifs", "morceau_du_message"), [
    ({"duree_minutes": None}, "durée"),
    ({"prix_centimes": 0}, "prix"),
    ({"forme_prix": "heure", "heures_min": 4, "heures_max": 2}, "nombre d'heures"),
    ({"titre": "ab"}, "titre"),
    ({"description": "x" * 1001}, "1000 caractères"),
    ({"paiement_especes": False}, "mode de paiement"),
])
def test_annonce_incomplete_refusee(fabrique_prestataire, metiers, modifs, morceau_du_message) -> None:
    reponse = publier(fabrique_prestataire(), menage(metiers["Plombier"], **modifs))

    assert reponse.status_code == 400
    assert morceau_du_message in reponse.json()["detail"]


def test_seulement_dans_un_metier_du_profil(fabrique_prestataire, metiers) -> None:
    # RM-ANNONCES : Karim ne peut pas publier dans « Coiffeur » sans l'ajouter d'abord à son profil
    reponse = publier(fabrique_prestataire(), menage(metiers["Coiffeur"], titre="Coupe homme"))

    assert reponse.status_code == 400 and "métiers de votre profil" in reponse.json()["detail"]


def test_carte_seulement_avec_un_siret_verifie(fabrique_prestataire, metiers, base: Session) -> None:
    karim = fabrique_prestataire()
    sans_siret = publier(karim, menage(metiers["Plombier"], paiement_carte=True))
    siret_verifie(base, karim)
    avec_siret = publier(karim, menage(metiers["Plombier"], paiement_carte=True))
    carte_activee(base, karim)  # lot 5.1 : la carte n'est proposée qu'une fois son compte Stripe vérifié
    modes = next(a for a in karim.client.get("/api/moi/annonces").json() if a["id"] == avec_siret.json()["id"])["modes_de_paiement"]

    assert sans_siret.status_code == 400 and "SIRET vérifié" in sans_siret.json()["detail"]
    assert avec_siret.status_code == 201 and avec_siret.json()["modes_de_paiement"] == ["especes"]
    assert modes == ["carte", "especes"]


def test_siret_perdu_la_carte_devient_especes(fabrique_prestataire, metiers, base: Session) -> None:
    # MLD 3.1 : la carte est un souhait ; SIRET refusé → « espèces », sans rien ressaisir
    karim = fabrique_prestataire()
    siret_verifie(base, karim)
    carte_activee(base, karim)
    annonce = publier(karim, menage(metiers["Plombier"], paiement_carte=True, paiement_especes=False)).json()
    base.execute(text("UPDATE prestataire SET siret_statut = 'refuse' WHERE compte_id = :id"), {"id": karim.id})
    base.commit()

    modes = next(a for a in karim.client.get("/api/moi/annonces").json() if a["id"] == annonce["id"])["modes_de_paiement"]

    assert modes == ["especes"]


def test_au_plus_20_annonces_en_ligne(fabrique_prestataire, metiers, base: Session) -> None:
    karim = fabrique_prestataire()
    for rang in range(reglages.ANNONCES_EN_LIGNE_MAX):
        assert publier(karim, menage(metiers["Plombier"], titre=f"Annonce {rang}")).status_code == 201

    de_trop = publier(karim, menage(metiers["Plombier"], titre="La 21e"))
    premiere = karim.client.get("/api/moi/annonces").json()[-1]
    karim.client.post(f"/api/moi/annonces/{premiere['id']}/statut", json={"action": "pause"})
    apres_pause = publier(karim, menage(metiers["Plombier"], titre="La 21e"))

    assert de_trop.status_code == 400 and "déjà 20 annonces en ligne" in de_trop.json()["detail"]
    assert apres_pause.status_code == 201


def test_modifier_son_annonce_et_pas_celle_d_un_autre(fabrique_prestataire, metiers) -> None:
    julie, karim = fabrique_prestataire(), fabrique_prestataire()
    annonce = publier(julie, menage(metiers["Plombier"])).json()

    modifiee = julie.client.post(f"/api/moi/annonces/{annonce['id']}/modifier", json=menage(metiers["Plombier"], prix_centimes=5500))
    par_karim = karim.client.post(f"/api/moi/annonces/{annonce['id']}/modifier", json=menage(metiers["Plombier"], prix_centimes=1))

    assert modifiee.status_code == 200 and modifiee.json()["prix_centimes"] == 5500
    assert par_karim.status_code == 404


def test_un_client_sans_activite_ne_publie_pas(fabrique_compte, metiers) -> None:
    reponse = publier(fabrique_compte(), menage(metiers["Plombier"]))

    assert reponse.status_code == 404


# ---------- Pause, retrait, republier ----------


def test_pause_retrait_republier_jamais_d_effacement(fabrique_prestataire, metiers, client) -> None:
    julie = fabrique_prestataire()
    annonce = publier(julie, menage(metiers["Plombier"], titre="Repassage")).json()
    statut = lambda action: julie.client.post(f"/api/moi/annonces/{annonce['id']}/statut", json={"action": action})  # noqa: E731

    visible_au_debut = client.get(f"/api/annonces/{annonce['id']}").status_code
    pause = statut("pause").json()
    cachee_en_pause = client.get(f"/api/annonces/{annonce['id']}").status_code
    retiree = statut("retirer").json()
    republiee = statut("republier").json()

    assert visible_au_debut == 200
    assert pause["statut"] == "en_pause" and pause["raison_cachee"] == "Annonce en pause."
    assert cachee_en_pause == 404
    assert retiree["statut"] == "retiree"
    assert republiee["statut"] == "en_ligne" and client.get(f"/api/annonces/{annonce['id']}").status_code == 200
    assert statut("republier").status_code == 400  # déjà en ligne


def test_activite_en_pause_cache_les_annonces(fabrique_prestataire, metiers, client) -> None:
    julie = fabrique_prestataire()
    annonce = publier(julie, menage(metiers["Plombier"])).json()

    julie.client.post("/api/moi/prestataire/statut", json={"action": "pause"})

    assert client.get(f"/api/annonces/{annonce['id']}").status_code == 404
    assert julie.client.get(f"/api/annonces/{annonce['id']}").status_code == 200  # son auteur la voit (aperçu)


# ---------- Local : la ville pour tous, la rue après réservation ----------


def test_chez_moi_demande_le_local_et_ne_montre_que_la_ville(fabrique_prestataire, metiers, client) -> None:
    lea = fabrique_prestataire("Coiffeur", ())
    coupe = menage(metiers["Coiffeur"], titre="Coupe femme", lieu="chez_moi", duree_minutes=45)

    sans_local = publier(lea, coupe)
    lea.client.post("/api/moi/local", json={"ligne": "12 rue des Lilas", "commune_id": id_commune(client, "33700", "Mérignac"),
                                            "code_postal": "33700"})
    annonce = publier(lea, coupe).json()
    publique = client.get(f"/api/annonces/{annonce['id']}")

    assert sans_local.status_code == 400 and "adresse de votre local" in sans_local.json()["detail"]
    assert publique.json()["ville"] == "Mérignac"
    assert "Lilas" not in publique.text


def test_local_non_effacable_si_une_annonce_chez_moi_est_en_ligne(fabrique_prestataire, metiers, client) -> None:
    lea = fabrique_prestataire("Coiffeur", ())
    lea.client.post("/api/moi/local", json={"ligne": "12 rue des Lilas", "commune_id": id_commune(client, "33700", "Mérignac"),
                                            "code_postal": "33700"})
    publier(lea, menage(metiers["Coiffeur"], titre="Coupe femme", lieu="les_deux", duree_minutes=45))

    reponse = lea.client.post("/api/moi/local/effacer")

    assert reponse.status_code == 400 and lea.client.get("/api/moi/local").json()["ligne"] == "12 rue des Lilas"


# ---------- Photos ----------


def test_cinq_photos_au_plus_et_la_suivante_remonte(fabrique_prestataire, metiers, client) -> None:
    julie = fabrique_prestataire()
    annonce = publier(julie, menage(metiers["Plombier"])).json()
    envoyer = lambda contenu, type_mime="image/jpeg": julie.client.post(  # noqa: E731
        f"/api/moi/annonces/{annonce['id']}/photos", files={"fichier": ("cuisine.jpg", contenu, type_mime)}
    )

    for rang in range(reglages.ANNONCE_PHOTOS_MAX):
        assert envoyer(JPG + bytes([rang])).status_code == 200
    sixieme = envoyer(JPG)
    julie.client.post(f"/api/moi/annonces/{annonce['id']}/photos/5/retirer")
    pas_une_photo = envoyer(PDF, "application/pdf")
    julie.client.post(f"/api/moi/annonces/{annonce['id']}/photos/1/retirer")
    nouvelle_premiere = client.get(f"/api/annonces/{annonce['id']}/photos/1")

    assert sixieme.status_code == 400 and "Au plus 5 photos" in sixieme.json()["detail"]
    assert pas_une_photo.status_code == 400
    assert nouvelle_premiere.content == JPG + bytes([1])  # l'ancienne n° 2 est devenue la n° 1
    assert client.get(f"/api/annonces/{annonce['id']}").json()["nombre_photos"] == 3


# ---------- Date de fin d'un métier ----------


def fin(compte, metier_id: int, fin_le: date | None, suivant_id: int | None = None):
    return compte.client.post("/api/moi/prestataire/metiers/fin", json={
        "metier_id": metier_id, "fin_le": None if fin_le is None else fin_le.isoformat(), "suivant_id": suivant_id,
    })


def vieillir_fin(base: Session, compte, jours: int) -> None:
    """Fait comme si les dates de fin avaient été posées il y a longtemps (elles sont alors dépassées)."""
    for requete in (
        "UPDATE prestataire SET metier_principal_fin_le = metier_principal_fin_le - :j WHERE compte_id = :id",
        "UPDATE metier_secondaire SET fin_le = fin_le - :j WHERE prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id)",
    ):
        base.execute(text(requete), {"j": jours, "id": compte.id})
    base.commit()


def test_pas_de_suppression_d_un_metier_qui_a_des_annonces(fabrique_prestataire, metiers, client) -> None:
    karim = fabrique_prestataire()
    publier(karim, menage(metiers["Électricien"], titre="Tableau électrique"))
    profil = karim.client.get("/api/moi/prestataire").json()
    formulaire = {"nom_affiche": profil["nom_affiche"], "metier_principal_id": metiers["Plombier"],
                  "commune_id": profil["commune"]["id"], "distance_km": 15, "metiers_secondaires": []}

    reponse = karim.client.post("/api/moi/prestataire/modifier", json=formulaire)

    assert reponse.status_code == 400 and "date de fin" in reponse.json()["detail"]


def test_metier_secondaire_arrete_annonces_cachees_puis_reprise(fabrique_prestataire, metiers, base: Session, client) -> None:
    # RM-ANNONCES : Karim arrête Électricien ; ses annonces sont cachées, pas effacées ; il reprend plus tard
    karim = fabrique_prestataire()
    annonce = publier(karim, menage(metiers["Électricien"], titre="Tableau électrique")).json()

    assert fin(karim, metiers["Électricien"], AUJOURD_HUI - timedelta(days=1)).status_code == 400  # date passée
    fin(karim, metiers["Électricien"], AUJOURD_HUI)
    encore_visible_aujourd_hui = client.get(f"/api/annonces/{annonce['id']}").status_code
    vieillir_fin(base, karim, 1)
    cachee_avant_la_tache = client.get(f"/api/annonces/{annonce['id']}").status_code
    appliquer_fins_de_metier(base, datetime.now(UTC))
    base.commit()
    profil = karim.client.get("/api/moi/prestataire").json()
    statut = lambda: next(a for a in karim.client.get("/api/moi/annonces").json() if a["id"] == annonce["id"])["statut"]  # noqa: E731
    en_pause = statut()
    nouvelle = publier(karim, menage(metiers["Électricien"], titre="Prise"))
    republier = lambda: karim.client.post(f"/api/moi/annonces/{annonce['id']}/statut", json={"action": "republier"})  # noqa: E731
    avant_reprise = republier()
    fin(karim, metiers["Électricien"], None)  # en mars, il reprend Électricien
    apres_reprise = republier()

    assert encore_visible_aujourd_hui == 200
    assert cachee_avant_la_tache == 404
    assert [m["nom"] for m in profil["metiers_arretes"]] == ["Électricien"] and profil["metiers_secondaires"] == []
    assert en_pause == "en_pause"  # gardée, pas effacée
    assert nouvelle.status_code == 400
    assert avant_reprise.status_code == 400
    assert apres_reprise.status_code == 200 and client.get(f"/api/annonces/{annonce['id']}").status_code == 200


def test_metier_principal_arrete_le_secondaire_devient_principal(fabrique_prestataire, metiers, base: Session) -> None:
    # RM-ANNONCES : Karim arrête Plombier au 15/11 → Électricien devient principal automatiquement
    karim = fabrique_prestataire()
    publier(karim, menage(metiers["Plombier"]))
    reponse = fin(karim, metiers["Plombier"], AUJOURD_HUI).json()
    vieillir_fin(base, karim, 1)

    traites = appliquer_fins_de_metier(base, datetime.now(UTC))
    base.commit()
    profil = karim.client.get("/api/moi/prestataire").json()

    assert reponse["metier_principal_suivant"]["nom"] == "Électricien"  # annoncé d'avance
    assert traites >= 1
    assert profil["metier_principal"]["nom"] == "Électricien" and profil["metier_principal"]["fin_le"] is None
    assert [m["nom"] for m in profil["metiers_arretes"]] == ["Plombier"]


def test_plusieurs_secondaires_on_choisit_le_suivant(fabrique_prestataire, metiers) -> None:
    julie = fabrique_prestataire("Plombier", ("Électricien", "Maçon"))

    par_defaut = fin(julie, metiers["Plombier"], AUJOURD_HUI + timedelta(days=30)).json()
    choisi = fin(julie, metiers["Plombier"], AUJOURD_HUI + timedelta(days=30), metiers["Maçon"]).json()
    hors_profil = fin(julie, metiers["Plombier"], AUJOURD_HUI + timedelta(days=30), metiers["Coiffeur"])

    assert par_defaut["metier_principal_suivant"]["nom"] == "Électricien"  # le 1er ajouté, choisi d'avance
    assert choisi["metier_principal_suivant"]["nom"] == "Maçon"
    assert hors_profil.status_code == 400


def test_seul_metier_arrete_le_profil_reste_sans_annonce(fabrique_prestataire, metiers, base: Session, client) -> None:
    # RM-ANNONCES : Léa n'a que Coiffeur ; après la date de fin, son profil reste, sans annonce visible
    lea = fabrique_prestataire("Coiffeur", ())
    annonce = publier(lea, menage(metiers["Coiffeur"], titre="Coupe femme", duree_minutes=45)).json()
    fin(lea, metiers["Coiffeur"], AUJOURD_HUI)
    vieillir_fin(base, lea, 1)
    appliquer_fins_de_metier(base, datetime.now(UTC))
    base.commit()

    profil = lea.client.get("/api/moi/prestataire").json()
    cachee = client.get(f"/api/annonces/{annonce['id']}").status_code
    fin(lea, metiers["Coiffeur"], None)  # elle remet Coiffeur, puis republie son annonce
    lea.client.post(f"/api/moi/annonces/{annonce['id']}/statut", json={"action": "republier"})

    assert profil["statut"] == "actif" and profil["metier_principal"]["nom"] == "Coiffeur / Coiffeuse"
    assert cachee == 404
    assert client.get(f"/api/annonces/{annonce['id']}").status_code == 200


# ---------- Données personnelles ----------


def test_mes_donnees_contiennent_annonces_et_local(fabrique_prestataire, metiers, client) -> None:
    karim = fabrique_prestataire()
    publier(karim, menage(metiers["Plombier"]))
    karim.client.post("/api/moi/local", json={"ligne": "3 rue du Moulin", "commune_id": id_commune(client, "33600", "Pessac"),
                                              "code_postal": "33600"})

    donnees = karim.client.get("/api/moi/donnees").json()["profil_prestataire"]

    assert donnees["annonces"][0]["titre"] == "Dépannage fuite"
    assert donnees["local"][0]["ligne"] == "3 rue du Moulin"
