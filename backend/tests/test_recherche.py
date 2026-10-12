"""Recherche d'un prestataire (RM-RECHERCHE.md ; lot 4.1)."""

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import reglages
from app.services.recherche import note_ponderee
from tests.test_prestataires import AUJOURD_HUI, carte_activee, metiers, siret_verifie  # noqa: F401 (fixture)
from tests.test_prestataires import JPG, devenir, id_commune, id_metier


@pytest.fixture
def villes(client) -> dict[str, int]:
    return {nom: id_commune(client, code, nom) for code, nom in
            (("33400", "Talence"), ("33600", "Pessac"), ("33000", "Bordeaux"), ("33500", "Libourne"), ("33700", "Mérignac"))}


@pytest.fixture
def fabrique(fabrique_compte, metiers, villes):  # noqa: F811
    """Un prestataire visible : fabrique("Sophie", "Bordeaux", "Électricien", km=30…).
    fabrique.noms(page) : les noms des prestataires créés PAR CE TEST, dans l'ordre des résultats (la base de test
    contient aussi ceux des autres tests, parfois avec le même nom)."""
    crees: dict[int, str] = {}

    def fabriquer(nom: str, ville: str, principal: str, *, secondaires: tuple[str, ...] = (), km: int = 30):
        compte = fabrique_compte()
        compte.profil = {"nom_affiche": f"ZZTEST {nom}", "metier_principal_id": metiers[principal],
                         "commune_id": villes[ville], "distance_km": km,
                         "metiers_secondaires": [metiers[m] for m in secondaires]}
        reponse = devenir(compte, compte.profil)
        assert reponse.status_code == 201, reponse.text
        compte.prestataire_id = reponse.json()["id"]
        crees[compte.prestataire_id] = nom
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


def test_profil_rempli_on_apparait_sauf_en_pause(fabrique, client, metiers, villes) -> None:
    # RM-RECHERCHE § « Sans annonces » : il suffit d'être actif, d'exercer le métier et de couvrir la ville
    fabrique("Plombier seul", "Pessac", "Plombier")
    fabrique("Deux métiers", "Pessac", "Plombier", secondaires=("Électricien",))
    fabrique("Autre métier", "Pessac", "Coiffeur")
    en_pause = fabrique("En pause", "Pessac", "Plombier")
    en_pause.client.post("/api/moi/prestataire/statut", json={"action": "pause"})

    page = chercher(client, metiers["Plombier"], villes["Talence"])
    noms = set(fabrique.noms(page))

    assert {"Plombier seul", "Deux métiers"} <= noms and not {"Autre métier", "En pause"} & noms
    seul = next(r for r in page["resultats"] if fabrique.noms({"resultats": [r]}) == ["Plombier seul"])
    assert seul["metier"] == "Plombier" and "a_partir_de_centimes" not in seul and "nombre_annonces" not in seul
    assert seul["siret_verifie"] is False and seul["photos"] == [] and seul["vient_chez_vous"] is True


def test_metier_arrete_n_apparait_plus(fabrique, client, metiers, villes, base: Session) -> None:
    karim = fabrique("Karim", "Pessac", "Plombier", secondaires=("Électricien",))
    karim.client.post("/api/moi/prestataire/metiers/fin", json={"metier_id": metiers["Électricien"], "fin_le": AUJOURD_HUI.isoformat()})
    base.execute(text("UPDATE metier_secondaire SET fin_le = fin_le - 1 WHERE prestataire_id = :id"), {"id": karim.prestataire_id})
    base.commit()

    assert "Karim" not in fabrique.noms(chercher(client, metiers["Électricien"], villes["Talence"]))


# ---------- Ordre ----------


def test_metier_principal_avant_secondaire_meme_plus_loin(fabrique, client, metiers, villes) -> None:
    # RM-PRESTATAIRES : Sophie électricienne (principal) passe avant Karim (électricien en métier secondaire)
    fabrique("Karim", "Talence", "Plombier", secondaires=("Électricien",))
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
    fabrique("Secondaire proche", "Talence", "Plombier", secondaires=("Maçon",))
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


def test_une_carte_par_prestataire_sans_coordonnees(fabrique, client, metiers, villes) -> None:
    karim = fabrique("Karim", "Pessac", "Plombier", secondaires=("Électricien",))

    page = chercher(client, metiers["Plombier"], villes["Talence"])
    cartes = [r for r in page["resultats"] if r["prestataire_id"] == karim.prestataire_id]

    assert len(cartes) == 1 and cartes[0]["carte_possible"] is False
    assert "telephone" not in str(page) and "0600000000" not in str(page)


# ---------- Filtres ----------


def test_filtre_vient_chez_moi(fabrique, client, metiers, villes) -> None:
    # Léa reçoit au salon (lieu « chez moi » dans son profil, avec son adresse) ; Nina se déplace
    lea = fabrique("Léa salon", "Talence", "Coiffeur")
    lea.client.post("/api/moi/adresse", json={"ligne": "12 rue des Lilas", "commune_id": villes["Talence"], "code_postal": "33400"})
    assert lea.client.post("/api/moi/prestataire/modifier", json=lea.profil | {"lieu": "chez_moi"}).status_code == 200
    fabrique("Nina domicile", "Talence", "Coiffeur")

    tous = fabrique.noms(chercher(client, metiers["Coiffeur"], villes["Talence"]))
    a_domicile = fabrique.noms(chercher(client, metiers["Coiffeur"], villes["Talence"], vient_chez_moi=True))

    assert {"Léa salon", "Nina domicile"} <= set(tous)
    assert "Nina domicile" in a_domicile and "Léa salon" not in a_domicile


def test_filtre_paiement_par_carte(fabrique, client, metiers, villes, base: Session) -> None:
    # « Carte bancaire acceptée » : SIRET vérifié et paiement par carte activé
    julie = fabrique("Julie carte", "Talence", "Maçon")
    siret_verifie(base, julie)
    carte_activee(base, julie)
    fabrique("Paul espèces", "Talence", "Maçon")

    avec_carte = fabrique.noms(chercher(client, metiers["Maçon"], villes["Talence"], carte_bancaire=True))

    assert "Julie carte" in avec_carte and "Paul espèces" not in avec_carte


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


# ---------- Une rubrique par dossier de métiers (« Trouver un prestataire » par service) ----------


def rubriques_de(client, ville_id: int) -> list[dict]:
    reponse = client.get("/api/recherche/rubriques", params={"commune_id": ville_id})
    assert reponse.status_code == 200, reponse.text
    return reponse.json()["rubriques"]


def rubrique_entiere(client, dossier_id: int, ville_id: int) -> dict:
    """[Voir tout] : toutes les pages réunies."""
    adresse, params = f"/api/recherche/rubriques/{dossier_id}", {"commune_id": ville_id}
    rubrique = client.get(adresse, params=params).json()["rubriques"][0]
    for numero in range(2, rubrique["pages"] + 1):
        rubrique["resultats"] += client.get(adresse, params={**params, "page": numero}).json()["rubriques"][0]["resultats"]
    return rubrique


def test_rubriques_par_dossier_pour_une_ville(fabrique, client, metiers, villes, base: Session) -> None:
    karim = fabrique("Karim", "Pessac", "Plombier", secondaires=("Coiffeur",))
    fabrique("Luc", "Libourne", "Plombier", km=10)  # Talence est hors de son rayon
    en_pause = fabrique("En pause", "Pessac", "Plombier")
    en_pause.client.post("/api/moi/prestataire/statut", json={"action": "pause"})
    dossier = {nom: base.execute(text("SELECT categorie_id FROM metier WHERE id = :id"), {"id": metiers[nom]}).scalar_one()
               for nom in ("Plombier", "Coiffeur")}
    assert dossier["Plombier"] != dossier["Coiffeur"]

    rubriques = rubriques_de(client, villes["Talence"])

    assert all(r["total"] >= 1 for r in rubriques)  # aucun dossier vide
    assert [r["dossier_id"] for r in rubriques] == [
        i for i in base.execute(text("SELECT id FROM categorie_metier ORDER BY ordre")).scalars()
        if i in {r["dossier_id"] for r in rubriques}
    ]
    plomberie = rubrique_entiere(client, dossier["Plombier"], villes["Talence"])
    coiffure = rubrique_entiere(client, dossier["Coiffeur"], villes["Talence"])
    assert fabrique.noms(plomberie) == ["Karim"]  # ni Luc (trop loin), ni le prestataire en pause
    carte = next(r for r in plomberie["resultats"] if r["prestataire_id"] == karim.prestataire_id)
    assert carte["metier"] == "Plombier" and carte["principal"] is True and carte["ville"] == "Pessac"
    assert 3 <= carte["distance_km"] <= 10 and carte["nouveau"] is True and carte["siret_verifie"] is False
    # Karim est aussi dans le dossier de son métier secondaire, avec ce métier-là sur sa carte
    secondaire = next(r for r in coiffure["resultats"] if r["prestataire_id"] == karim.prestataire_id)
    assert secondaire["metier"].startswith("Coiffeur") and secondaire["principal"] is False
    assert "0600000000" not in str(rubriques) and karim.email not in str(rubriques)


def test_rubrique_une_seule_carte_par_prestataire_avec_ses_2_premieres_photos(fabrique, client, metiers, villes, base: Session) -> None:
    # Plombier et électricien sont dans le même dossier : une seule carte, celle du métier principal
    karim = fabrique("Karim", "Pessac", "Électricien", secondaires=("Plombier",))
    dossiers = {base.execute(text("SELECT categorie_id FROM metier WHERE id = :id"), {"id": metiers[nom]}).scalar_one()
                for nom in ("Plombier", "Électricien")}
    siret_verifie(base, karim)
    for numero in range(3):
        depot = karim.client.post("/api/moi/prestataire/photos", files={"fichier": (f"travail{numero}.jpg", JPG, "image/jpeg")})
        assert depot.status_code == 200, depot.text

    cartes = [r for dossier_id in dossiers for r in rubrique_entiere(client, dossier_id, villes["Talence"])["resultats"]
              if r["prestataire_id"] == karim.prestataire_id]

    if len(dossiers) == 1:
        assert len(cartes) == 1 and cartes[0]["metier"] == "Électricien"
    assert all(c["photos"] == [1, 2] and c["siret_verifie"] is True for c in cartes)


def test_rubriques_limitees_a_10_cartes_et_voir_tout(fabrique, client, metiers, villes, monkeypatch, base: Session) -> None:
    monkeypatch.setattr(reglages, "RECHERCHE_CARTES_PAR_RUBRIQUE", 2)
    for nom in ("Un", "Deux", "Trois"):
        fabrique(nom, "Talence", "Maçon")
    dossier_id = base.execute(text("SELECT categorie_id FROM metier WHERE id = :id"), {"id": metiers["Maçon"]}).scalar_one()

    courte = next(r for r in rubriques_de(client, villes["Talence"]) if r["dossier_id"] == dossier_id)
    entiere = rubrique_entiere(client, dossier_id, villes["Talence"])

    assert len(courte["resultats"]) == 2 and courte["total"] >= 3
    assert {"Un", "Deux", "Trois"} <= set(fabrique.noms(entiere)) and entiere["total"] == courte["total"]


def test_rubriques_ville_inconnue_ou_dossier_vide(client, villes) -> None:
    assert client.get("/api/recherche/rubriques", params={"commune_id": 0}).status_code == 400
    assert client.get("/api/recherche/rubriques/0", params={"commune_id": villes["Talence"]}).json()["rubriques"] == []


# ---------- Page publique d'un prestataire ----------


def test_page_publique_profil_sans_coordonnees(fabrique, client) -> None:
    karim = fabrique("Karim", "Pessac", "Plombier", secondaires=("Électricien",))

    page = client.get(f"/api/prestataires/{karim.prestataire_id}")

    assert page.status_code == 200
    assert page.json()["nom_affiche"] == "ZZTEST Karim" and "annonces" not in page.json()
    assert [m["nom"] for m in page.json()["metiers"]] == ["Plombier", "Électricien"]
    assert karim.email not in page.text and "0600000000" not in page.text


def test_page_publique_cachee_en_pause_sauf_pour_son_auteur(fabrique, client) -> None:
    karim = fabrique("Karim", "Pessac", "Plombier")
    karim.client.post("/api/moi/prestataire/statut", json={"action": "pause"})

    assert client.get(f"/api/prestataires/{karim.prestataire_id}").status_code == 404
    assert karim.client.get(f"/api/prestataires/{karim.prestataire_id}").status_code == 200
