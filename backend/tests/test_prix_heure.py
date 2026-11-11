"""Le prix de l'heure de chaque métier (schema_v35, MLD validé par Raphael le 11/11/2026 ; services/prestataires.py) :
facultatif, de 1 € à 1 000 €, montré sur la carte de « Trouver » (« 45 €/h ») et sur la page publique ; il suit son
métier quand un métier secondaire devient principal."""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.services.prestataires import appliquer_fins_de_metier
from tests.test_fin_de_metier import fin, vieillir_fin
from tests.test_prestataires import AUJOURD_HUI, fabrique_prestataire, id_commune, metiers  # noqa: F401 (fixtures)


def prix(compte, metier_id: int, centimes: int | None):
    return compte.client.post("/api/moi/prestataire/prix", json={"metier_id": metier_id, "prix_centimes": centimes})


def test_prix_du_principal_et_d_un_secondaire(fabrique_prestataire, metiers) -> None:  # noqa: F811
    # Karim : plombier à 45,00 € de l'heure, électricien à 50,00 €
    karim = fabrique_prestataire()
    au_depart = karim.client.get("/api/moi/prestataire").json()
    principal = prix(karim, metiers["Plombier"], 4500)
    secondaire = prix(karim, metiers["Électricien"], 5000).json()
    efface = prix(karim, metiers["Plombier"], None).json()

    assert au_depart["metier_principal"]["prix_centimes"] is None  # facultatif : vide au départ
    assert principal.status_code == 200 and principal.json()["metier_principal"]["prix_centimes"] == 4500
    assert secondaire["metiers_secondaires"][0]["prix_centimes"] == 5000
    assert efface["metier_principal"]["prix_centimes"] is None and efface["metiers_secondaires"][0]["prix_centimes"] == 5000


def test_prix_refuses(fabrique_prestataire, fabrique_compte, metiers) -> None:  # noqa: F811
    karim, julie = fabrique_prestataire(), fabrique_compte()
    trop_bas = prix(karim, metiers["Plombier"], 99)  # 0,99 €
    trop_haut = prix(karim, metiers["Plombier"], 100_001)  # 1 000,01 €
    pas_son_metier = prix(karim, metiers["Maçon"], 4000)
    pas_prestataire = prix(julie, metiers["Plombier"], 4000)

    assert trop_bas.status_code == 400 and trop_bas.json()["detail"] == "Le prix de l'heure doit être entre 1 € et 1 000 €."
    assert trop_haut.status_code == 400
    assert pas_son_metier.status_code == 404 and "pas dans votre profil" in pas_son_metier.json()["detail"]
    assert pas_prestataire.status_code == 404


def test_prix_sur_la_carte_et_la_page_publique(fabrique_prestataire, client, metiers) -> None:  # noqa: F811
    karim = fabrique_prestataire()
    prix(karim, metiers["Plombier"], 4500)
    karim_id = karim.client.get("/api/moi/prestataire").json()["id"]
    pessac = id_commune(client, "33600", "Pessac")
    carte_plombier = next(c for c in client.get("/api/recherche", params={"metier_id": metiers["Plombier"], "commune_id": pessac})
                          .json()["resultats"] if c["prestataire_id"] == karim_id)
    carte_electricien = next(c for c in client.get("/api/recherche", params={"metier_id": metiers["Électricien"], "commune_id": pessac})
                             .json()["resultats"] if c["prestataire_id"] == karim_id)
    publique = client.get(f"/api/prestataires/{karim_id}").json()

    assert carte_plombier["prix_centimes"] == 4500  # « 45 €/h »
    assert carte_electricien["prix_centimes"] is None  # pas de prix donné pour Électricien : rien d'écrit
    assert [(m["nom"], m["prix_centimes"]) for m in publique["metiers"]] == [("Plombier", 4500), ("Électricien", None)]


def test_le_prix_suit_le_metier_qui_devient_principal(fabrique_prestataire, metiers, base: Session) -> None:  # noqa: F811
    # Karim arrête Plombier (45 €) : Électricien (50 €) devient principal avec son prix ; Plombier garde le sien
    karim = fabrique_prestataire()
    prix(karim, metiers["Plombier"], 4500)
    prix(karim, metiers["Électricien"], 5000)
    fin(karim, metiers["Plombier"], AUJOURD_HUI)
    vieillir_fin(base, karim, 1)
    appliquer_fins_de_metier(base, datetime.now(UTC))
    base.commit()
    profil = karim.client.get("/api/moi/prestataire").json()

    assert (profil["metier_principal"]["nom"], profil["metier_principal"]["prix_centimes"]) == ("Électricien", 5000)
    assert [(m["nom"], m["prix_centimes"]) for m in profil["metiers_arretes"]] == [("Plombier", 4500)]
