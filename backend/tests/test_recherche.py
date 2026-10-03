"""Recherche d'un prestataire (RM-RECHERCHE.md ; lot 4.1)."""

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import reglages
from app.services.recherche import note_ponderee
from tests.test_annonces import AUJOURD_HUI, carte_activee, menage, metiers, publier, siret_verifie  # noqa: F401 (fixture)
from tests.test_prestataires import devenir, id_commune, id_metier


@pytest.fixture
def villes(client) -> dict[str, int]:
    return {nom: id_commune(client, code, nom) for code, nom in
            (("33400", "Talence"), ("33600", "Pessac"), ("33000", "Bordeaux"), ("33500", "Libourne"), ("33700", "Mérignac"))}


@pytest.fixture
def fabrique(fabrique_compte, metiers, villes, base: Session):  # noqa: F811
    """Un prestataire avec une annonce en ligne : fabrique("Sophie", "Bordeaux", "Électricien", km=30, prix=5000…).
    fabrique.noms(page) : les noms des prestataires créés PAR CE TEST, dans l'ordre des résultats (la base de test
    contient aussi ceux des autres tests, parfois avec le même nom)."""
    crees: dict[int, str] = {}

    def fabriquer(nom: str, ville: str, principal: str, *, secondaires: tuple[str, ...] = (), km: int = 30,
                  annonce_dans: str | None = None, **annonce):
        compte = fabrique_compte()
        reponse = devenir(compte, {"nom_affiche": f"ZZTEST {nom}", "metier_principal_id": metiers[principal],
                                   "commune_id": villes[ville], "distance_km": km,
                                   "metiers_secondaires": [metiers[m] for m in secondaires]})
        assert reponse.status_code == 201, reponse.text
        compte.prestataire_id = reponse.json()["id"]
        crees[compte.prestataire_id] = nom
        if annonce.get("forme_prix") == "devis":
            siret_verifie(base, compte)  # « sur devis » demande un SIRET vérifié (lot 5.3)
        if annonce_dans != "":
            reponse = publier(compte, menage(metiers[annonce_dans or principal], titre=f"Annonce de {nom}", **annonce))
            assert reponse.status_code == 201, reponse.text
        return compte

    fabriquer.noms = lambda page: [crees[r["prestataire_id"]] for r in page["resultats"] if r["prestataire_id"] in crees]
    return fabriquer


def chercher(client, metier_id: int, ville_id: int, **params):
    """Toutes les pages réunies (sauf si le test demande une page précise)."""
    reponse = client.get("/api/recherche", params={"metier_id": metier_id, "commune_id": ville_id, **params})
    assert reponse.status_code == 200, reponse.text
    page = reponse.json()
    if "page" not in params:
        for numero in range(2, page["pages"] + 1):
            suite = client.get("/api/recherche", params={"metier_id": metier_id, "commune_id": ville_id, **params, "page": numero})
            page["resultats"] += suite.json()["resultats"]
    return page


# ---------- Qui apparaît ----------


def test_seulement_dans_le_rayon(fabrique, client, metiers, villes) -> None:
    fabrique("Karim", "Pessac", "Plombier", km=15)
    fabrique("Luc", "Libourne", "Plombier", km=10)  # Libourne → Talence : bien plus de 10 km

    page = chercher(client, metiers["Plombier"], villes["Talence"])

    assert "Karim" in fabrique.noms(page) and "Luc" not in fabrique.noms(page)
    karim = next(r for r in page["resultats"] if fabrique.noms({"resultats": [r]}) == ["Karim"])
    assert 3 <= karim["distance_km"] <= 10 and karim["ville"] == "Pessac"


def test_il_faut_une_annonce_en_ligne_de_ce_metier(fabrique, client, metiers, villes) -> None:
    fabrique("Sans annonce", "Pessac", "Plombier", annonce_dans="")
    fabrique("Électricien seulement", "Pessac", "Plombier", secondaires=("Électricien",), annonce_dans="Électricien")
    en_pause = fabrique("En pause", "Pessac", "Plombier")
    en_pause.client.post("/api/moi/prestataire/statut", json={"action": "pause"})

    page = chercher(client, metiers["Plombier"], villes["Talence"])

    assert not {"Sans annonce", "Électricien seulement", "En pause"} & set(fabrique.noms(page))


def test_metier_arrete_n_apparait_plus(fabrique, client, metiers, villes, base: Session) -> None:
    karim = fabrique("Karim", "Pessac", "Plombier", secondaires=("Électricien",), annonce_dans="Électricien")
    karim.client.post("/api/moi/prestataire/metiers/fin", json={"metier_id": metiers["Électricien"], "fin_le": AUJOURD_HUI.isoformat()})
    base.execute(text("UPDATE metier_secondaire SET fin_le = fin_le - 1 WHERE prestataire_id = :id"), {"id": karim.prestataire_id})
    base.commit()

    assert "Karim" not in fabrique.noms(chercher(client, metiers["Électricien"], villes["Talence"]))


# ---------- Ordre ----------


def test_metier_principal_avant_secondaire_meme_plus_loin(fabrique, client, metiers, villes) -> None:
    # RM-PRESTATAIRES : Sophie électricienne (principal) passe avant Karim (électricien en métier secondaire)
    fabrique("Karim", "Talence", "Plombier", secondaires=("Électricien",), annonce_dans="Électricien")
    fabrique("Sophie", "Bordeaux", "Électricien")

    ordre = fabrique.noms(chercher(client, metiers["Électricien"], villes["Talence"]))

    assert ordre.index("Sophie") < ordre.index("Karim")


def test_sans_avis_tous_nouveaux_puis_le_plus_proche(fabrique, client, metiers, villes) -> None:
    fabrique("Loin", "Mérignac", "Coiffeur")
    fabrique("Près", "Talence", "Coiffeur")

    page = chercher(client, metiers["Coiffeur"], villes["Talence"])
    mes = [r for r in page["resultats"] if fabrique.noms({"resultats": [r]})]

    assert all(r["nouveau"] and r["note"] is None and r["nombre_avis"] == 0 for r in mes)
    assert fabrique.noms(page) == ["Près", "Loin"]  # à égalité : le plus proche


def test_tri_les_plus_proches(fabrique, client, metiers, villes) -> None:
    fabrique("Secondaire proche", "Talence", "Plombier", secondaires=("Maçon",), annonce_dans="Maçon")
    fabrique("Principal loin", "Mérignac", "Maçon")

    par_note = fabrique.noms(chercher(client, metiers["Maçon"], villes["Talence"]))
    par_distance = fabrique.noms(chercher(client, metiers["Maçon"], villes["Talence"], tri="distance"))

    assert par_note.index("Principal loin") < par_note.index("Secondaire proche")
    assert par_distance.index("Secondaire proche") < par_distance.index("Principal loin")


def test_note_ponderee() -> None:
    # RM-RECHERCHE : Sophie 40 avis à 4,8 → 4,71 ; Julie 1 avis à 5 → 4,17 ; Marc 30 avis à 4,2 → 4,17
    assert round(note_ponderee(192, 40), 2) == 4.71
    assert round(note_ponderee(5, 1), 2) == 4.17
    assert round(note_ponderee(126, 30), 2) == 4.17


# ---------- Carte d'un prestataire ----------


def test_une_carte_par_prestataire_a_partir_du_moins_cher(fabrique, client, metiers, villes, base: Session) -> None:
    karim = fabrique("Karim", "Pessac", "Plombier", prix_centimes=5000)
    siret_verifie(base, karim)  # « sur devis » demande un SIRET vérifié (lot 5.3)
    publier(karim, menage(metiers["Plombier"], titre="À l'heure", forme_prix="heure", prix_centimes=4000,
                          duree_minutes=None, heures_min=1, heures_max=3))
    publier(karim, menage(metiers["Plombier"], titre="Chauffe-eau", forme_prix="devis", prix_centimes=None, duree_minutes=None))

    page = chercher(client, metiers["Plombier"], villes["Talence"])
    cartes = [r for r in page["resultats"] if r["prestataire_id"] == karim.prestataire_id]

    assert len(cartes) == 1
    assert cartes[0]["nombre_annonces"] == 3
    assert cartes[0]["a_partir_de_centimes"] == 4000 and cartes[0]["a_partir_de_par_heure"] is True
    assert "telephone" not in str(page) and "0600000000" not in str(page)


# ---------- Filtres ----------


def test_filtre_vient_chez_moi(fabrique, client, metiers, villes) -> None:
    lea = fabrique("Léa salon", "Talence", "Coiffeur", annonce_dans="")
    lea.client.post("/api/moi/local", json={"ligne": "12 rue des Lilas", "commune_id": villes["Talence"], "code_postal": "33400"})
    publier(lea, menage(metiers["Coiffeur"], titre="Coupe au salon", lieu="chez_moi"))
    fabrique("Nina domicile", "Talence", "Coiffeur")

    tous = fabrique.noms(chercher(client, metiers["Coiffeur"], villes["Talence"]))
    a_domicile = fabrique.noms(chercher(client, metiers["Coiffeur"], villes["Talence"], vient_chez_moi=True))

    assert {"Léa salon", "Nina domicile"} <= set(tous)
    assert "Nina domicile" in a_domicile and "Léa salon" not in a_domicile


def test_filtre_paiement_par_carte(fabrique, client, metiers, villes, base: Session) -> None:
    julie = fabrique("Julie carte", "Talence", "Maçon", annonce_dans="")
    siret_verifie(base, julie)
    carte_activee(base, julie)
    publier(julie, menage(metiers["Maçon"], titre="Muret", paiement_carte=True))
    fabrique("Paul espèces", "Talence", "Maçon")

    avec_carte = fabrique.noms(chercher(client, metiers["Maçon"], villes["Talence"], carte_bancaire=True))

    assert "Julie carte" in avec_carte and "Paul espèces" not in avec_carte


def test_filtre_prix_maximum_garde_les_devis(fabrique, client, metiers, villes) -> None:
    fabrique("Cher", "Talence", "Maçon", prix_centimes=8000)
    fabrique("Pas cher", "Talence", "Maçon", prix_centimes=4500)
    fabrique("Devis", "Talence", "Maçon", forme_prix="devis", prix_centimes=None, duree_minutes=None)

    resultat = fabrique.noms(chercher(client, metiers["Maçon"], villes["Talence"], prix_max=60))

    assert {"Pas cher", "Devis"} <= set(resultat) and "Cher" not in resultat


def test_filtre_libre_dans_les_7_jours(fabrique, client, metiers, villes) -> None:
    ouvert = fabrique("Ouvert", "Talence", "Maçon")
    tous_les_jours = [{"jour_semaine": j, "debut": "08:00", "fin": "20:00"} for j in range(1, 8)]
    ouvert.client.post("/api/moi/agenda/semaine", json={"plages": tous_les_jours})
    fabrique("Sans horaires", "Talence", "Maçon")

    libres = fabrique.noms(chercher(client, metiers["Maçon"], villes["Talence"], libre_7_jours=True))

    assert "Ouvert" in libres and "Sans horaires" not in libres


# ---------- Pages et aucun résultat ----------


def test_pages_de_resultats(fabrique, client, metiers, villes, monkeypatch) -> None:
    monkeypatch.setattr(reglages, "RECHERCHE_RESULTATS_PAR_PAGE", 2)
    for nom in ("A", "B", "C"):
        fabrique(nom, "Talence", "Coiffeur")

    page_1 = chercher(client, metiers["Coiffeur"], villes["Talence"], page=1)
    derniere = chercher(client, metiers["Coiffeur"], villes["Talence"], page=page_1["pages"])

    assert len(page_1["resultats"]) == 2 and page_1["pages"] >= 2
    assert derniere["page"] == page_1["pages"] and len(derniere["resultats"]) >= 1


def test_aucun_resultat_propose_des_metiers_voisins(client, villes) -> None:
    magicien = id_metier(client, "Magicien")  # aucun test ne crée de magicien

    page = chercher(client, magicien, villes["Libourne"])

    assert page["total"] == 0 and page["resultats"] == []
    assert page["metiers_voisins"] and all(m["nom"] != "Magicien" for m in page["metiers_voisins"])


def test_metier_ou_ville_inconnus(client) -> None:
    assert client.get("/api/recherche", params={"metier_id": 999999, "commune_id": 1}).status_code == 400


# ---------- Page publique d'un prestataire ----------


def test_page_publique_profil_et_annonces_sans_coordonnees(fabrique, client) -> None:
    karim = fabrique("Karim", "Pessac", "Plombier", secondaires=("Électricien",))

    page = client.get(f"/api/prestataires/{karim.prestataire_id}")

    assert page.status_code == 200
    assert page.json()["nom_affiche"] == "ZZTEST Karim" and len(page.json()["annonces"]) == 1
    assert [m["nom"] for m in page.json()["metiers"]] == ["Plombier", "Électricien"]
    assert karim.email not in page.text and "0600000000" not in page.text


def test_page_publique_cachee_en_pause_sauf_pour_son_auteur(fabrique, client) -> None:
    karim = fabrique("Karim", "Pessac", "Plombier")
    karim.client.post("/api/moi/prestataire/statut", json={"action": "pause"})

    assert client.get(f"/api/prestataires/{karim.prestataire_id}").status_code == 404
    assert karim.client.get(f"/api/prestataires/{karim.prestataire_id}").status_code == 200
