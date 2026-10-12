"""Date de fin d'un métier et local du prestataire (RM-PRESTATAIRES.md ; lot 3.1, revu au lot 9.2 sans les annonces)."""

from datetime import UTC, date, datetime, timedelta

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.prestataires import appliquer_fins_de_metier
from tests.test_prestataires import AUJOURD_HUI, fabrique_prestataire, id_commune, metiers  # noqa: F401 (fixtures)


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


def _formulaire(compte, metiers, secondaires: list[int]) -> dict:  # noqa: F811
    profil = compte.client.get("/api/moi/prestataire").json()
    return {"nom_affiche": profil["nom_affiche"], "metier_principal_id": metiers["Plombier"],
            "commune_id": profil["commune"]["id"], "distance_km": 15, "metiers_secondaires": secondaires}


def test_un_metier_secondaire_se_retire_du_profil(fabrique_prestataire, metiers) -> None:  # noqa: F811
    # Sans annonces, plus rien ne retient un métier : Karim retire Électricien de son profil
    karim = fabrique_prestataire()

    reponse = karim.client.post("/api/moi/prestataire/modifier", json=_formulaire(karim, metiers, []))

    assert reponse.status_code == 200 and reponse.json()["metiers_secondaires"] == []


def test_metier_secondaire_arrete_puis_repris(fabrique_prestataire, metiers, base: Session) -> None:  # noqa: F811
    # Karim arrête Électricien à une date ; le métier reste dans son profil comme « arrêté » ; il le reprend plus tard
    karim = fabrique_prestataire()

    assert fin(karim, metiers["Électricien"], AUJOURD_HUI - timedelta(days=1)).status_code == 400  # date passée
    fin(karim, metiers["Électricien"], AUJOURD_HUI)
    encore_exerce_aujourd_hui = [m["nom"] for m in karim.client.get("/api/moi/prestataire").json()["metiers_secondaires"]]
    vieillir_fin(base, karim, 1)
    appliquer_fins_de_metier(base, datetime.now(UTC))
    base.commit()
    arrete = karim.client.get("/api/moi/prestataire").json()
    fin(karim, metiers["Électricien"], None)  # en mars, il reprend Électricien
    repris = karim.client.get("/api/moi/prestataire").json()

    assert encore_exerce_aujourd_hui == ["Électricien"]
    assert [m["nom"] for m in arrete["metiers_arretes"]] == ["Électricien"] and arrete["metiers_secondaires"] == []
    assert [m["nom"] for m in repris["metiers_secondaires"]] == ["Électricien"] and repris["metiers_arretes"] == []


def test_metier_principal_arrete_le_secondaire_devient_principal(fabrique_prestataire, metiers, base: Session) -> None:  # noqa: F811
    # Karim arrête Plombier au 15/11 → Électricien devient principal automatiquement
    karim = fabrique_prestataire()
    reponse = fin(karim, metiers["Plombier"], AUJOURD_HUI).json()
    vieillir_fin(base, karim, 1)

    traites = appliquer_fins_de_metier(base, datetime.now(UTC))
    base.commit()
    profil = karim.client.get("/api/moi/prestataire").json()

    assert reponse["metier_principal_suivant"]["nom"] == "Électricien"  # annoncé d'avance
    assert traites >= 1
    assert profil["metier_principal"]["nom"] == "Électricien" and profil["metier_principal"]["fin_le"] is None
    assert [m["nom"] for m in profil["metiers_arretes"]] == ["Plombier"]


def test_plusieurs_secondaires_on_choisit_le_suivant(fabrique_prestataire, metiers) -> None:  # noqa: F811
    julie = fabrique_prestataire("Plombier", ("Électricien", "Maçon"))

    par_defaut = fin(julie, metiers["Plombier"], AUJOURD_HUI + timedelta(days=30)).json()
    choisi = fin(julie, metiers["Plombier"], AUJOURD_HUI + timedelta(days=30), metiers["Maçon"]).json()
    hors_profil = fin(julie, metiers["Plombier"], AUJOURD_HUI + timedelta(days=30), metiers["Coiffeur"])

    assert par_defaut["metier_principal_suivant"]["nom"] == "Électricien"  # le 1er ajouté, choisi d'avance
    assert choisi["metier_principal_suivant"]["nom"] == "Maçon"
    assert hors_profil.status_code == 400


def test_seul_metier_arrete_le_profil_reste(fabrique_prestataire, metiers, base: Session) -> None:  # noqa: F811
    # Léa n'a que Coiffeur ; après la date de fin, son profil reste ; elle peut reprendre son métier
    lea = fabrique_prestataire("Coiffeur", ())
    fin(lea, metiers["Coiffeur"], AUJOURD_HUI)
    vieillir_fin(base, lea, 1)
    appliquer_fins_de_metier(base, datetime.now(UTC))
    base.commit()

    profil = lea.client.get("/api/moi/prestataire").json()
    reprise = fin(lea, metiers["Coiffeur"], None)

    assert profil["statut"] == "actif" and profil["metier_principal"]["nom"] == "Coiffeur / Coiffeuse"
    assert reprise.status_code == 200 and reprise.json()["metier_principal"]["fin_le"] is None


def test_mes_donnees_contiennent_le_local(fabrique_prestataire, client) -> None:  # noqa: F811
    # « Mon adresse » d'un prestataire est aussi son local (décision du 07/10/2026)
    karim = fabrique_prestataire()
    karim.client.post("/api/moi/adresse", json={"ligne": "3 rue du Moulin", "commune_id": id_commune(client, "33600", "Pessac"),
                                                "code_postal": "33600"})

    donnees = karim.client.get("/api/moi/donnees").json()["profil_prestataire"]

    assert donnees["local"][0]["ligne"] == "3 rue du Moulin" and "annonces" not in donnees
