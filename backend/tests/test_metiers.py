"""Métiers et catégories (RM-METIERS.md ; lot 2.1)."""

from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session


def noms(client, q: str) -> list[str]:
    return [m["nom"] for m in client.get("/api/metiers/recherche", params={"q": q}).json()]


def nom_unique(debut: str) -> str:
    return f"{debut} {uuid4().hex[:6]}"


# ---------- Recherche ----------


def test_premieres_lettres(client) -> None:
    assert noms(client, "plom")[0] == "Plombier"


def test_sans_accents(client) -> None:
    # RM-METIERS : « electricien » (sans accent) trouve « Électricien »
    assert "Électricien" in noms(client, "electricien")
    assert "Menuisier / Ébéniste" in noms(client, "ebeni")


def test_mots_cles(client) -> None:
    # RM-METIERS : « kine » trouve « Kinésithérapeute » ; « photo » trouve « Photographe »
    assert "Kinésithérapeute" in noms(client, "kine")
    assert "Plombier" in noms(client, "fuite")
    assert "Photographe" in noms(client, "photo")


def test_le_nom_passe_avant_les_mots_cles(client) -> None:
    resultats = noms(client, "photo")

    assert resultats[0] == "Photographe"


def test_caracteres_speciaux_sans_danger(client) -> None:
    assert client.get("/api/metiers/recherche", params={"q": "100%_'"}).status_code == 200
    assert noms(client, "%") == []


def test_dossiers_dans_l_ordre(client) -> None:
    dossiers = client.get("/api/metiers/dossiers").json()

    assert [d["nom"] for d in dossiers][:2] == ["Maison & travaux", "Ménage & entretien"]
    assert dossiers[-1]["nom"] == "Autre"
    assert "Plombier" in [m["nom"] for m in dossiers[0]["metiers"]]


def test_metier_desactive_n_est_plus_propose(fabrique_compte, client) -> None:
    admin = fabrique_compte(administrateur=True)
    nom = nom_unique("Sculpteur sur ballons")
    dossier = client.get("/api/metiers/dossiers").json()[0]["id"]
    metier = admin.client.post("/api/admin/metiers", json={"nom": nom, "categorie_id": dossier}).json()
    assert nom in noms(client, "sculpteur sur")

    admin.client.post(
        f"/api/admin/metiers/{metier['id']}",
        json={"nom": nom, "categorie_id": dossier, "mots_cles": [], "est_active": False},
    )

    assert nom not in noms(client, "sculpteur sur")


# ---------- Propositions ----------


def test_nadia_propose_cerf_voliste_accepte(fabrique_compte, client, base: Session) -> None:
    admin = fabrique_compte(administrateur=True)
    nadia = fabrique_compte()
    nom = nom_unique("Cerf-voliste")
    sport = next(d["id"] for d in client.get("/api/metiers/dossiers").json() if d["code"] == "sport-loisirs")

    reponse = nadia.client.post("/api/metiers/propositions", json={"nom": nom})
    proposition = next(p for p in admin.client.get("/api/admin/propositions").json() if p["nom_propose"] == nom)
    decision = admin.client.post(
        f"/api/admin/propositions/{proposition['id']}/decision", json={"decision": "acceptee", "categorie_id": sport}
    )

    assert reponse.status_code == 201
    assert "choisissez « Autre »" in reponse.json()["message"]
    assert decision.json()["statut"] == "acceptee"
    assert nom in noms(client, "cerf-voliste")


def test_proposer_un_metier_qui_existe_deja(fabrique_compte) -> None:
    tom = fabrique_compte()

    reponse = tom.client.post("/api/metiers/propositions", json={"nom": "plombier"})

    assert reponse.status_code == 400
    assert reponse.json()["detail"] == "Ce métier existe déjà dans la liste : « Plombier »."


def test_proposition_remplacee_devient_un_mot_cle(fabrique_compte, client) -> None:
    # RM-METIERS : Tom propose « Plombier chauffagiste » → « Plombier » ; le nom proposé devient un mot-clé
    admin = fabrique_compte(administrateur=True)
    tom = fabrique_compte()
    nom = nom_unique("Plombier zinguerie")
    plombier = next(m for m in client.get("/api/metiers/recherche", params={"q": "plombier"}).json() if m["nom"] == "Plombier")
    tom.client.post("/api/metiers/propositions", json={"nom": nom})
    proposition = next(p for p in admin.client.get("/api/admin/propositions").json() if p["nom_propose"] == nom)

    admin.client.post(
        f"/api/admin/propositions/{proposition['id']}/decision", json={"decision": "remplacee", "metier_id": plombier["id"]}
    )

    assert "Plombier" in noms(client, nom.lower())


def test_une_proposition_ne_se_decide_qu_une_fois(fabrique_compte) -> None:
    admin = fabrique_compte(administrateur=True)
    tom = fabrique_compte()
    nom = nom_unique("Luthier de cornemuses")
    tom.client.post("/api/metiers/propositions", json={"nom": nom})
    proposition = next(p for p in admin.client.get("/api/admin/propositions").json() if p["nom_propose"] == nom)
    adresse = f"/api/admin/propositions/{proposition['id']}/decision"

    admin.client.post(adresse, json={"decision": "refusee"})
    seconde = admin.client.post(adresse, json={"decision": "refusee"})

    assert seconde.status_code == 400
    assert seconde.json()["detail"] == "Cette proposition a déjà été décidée."


def test_accepter_exige_un_dossier(fabrique_compte) -> None:
    admin = fabrique_compte(administrateur=True)
    tom = fabrique_compte()
    nom = nom_unique("Accordeur de pianos")
    tom.client.post("/api/metiers/propositions", json={"nom": nom})
    proposition = next(p for p in admin.client.get("/api/admin/propositions").json() if p["nom_propose"] == nom)

    reponse = admin.client.post(f"/api/admin/propositions/{proposition['id']}/decision", json={"decision": "acceptee"})

    assert reponse.status_code == 400
    assert reponse.json()["detail"] == "Choisissez le dossier où ranger ce nouveau métier."


def test_proposer_exige_d_etre_connecte_et_decider_d_etre_administrateur(fabrique_compte, client) -> None:
    tom = fabrique_compte()

    assert client.post("/api/metiers/propositions", json={"nom": "Truc"}).status_code == 401
    assert tom.client.get("/api/admin/propositions").status_code == 403
    assert tom.client.post("/api/admin/metiers", json={"nom": "Truc", "categorie_id": 1}).status_code == 403


def test_decisions_notees_au_journal(fabrique_compte, base: Session) -> None:
    admin = fabrique_compte(administrateur=True)
    tom = fabrique_compte()
    nom = nom_unique("Doreur sur bois")
    tom.client.post("/api/metiers/propositions", json={"nom": nom})
    proposition = next(p for p in admin.client.get("/api/admin/propositions").json() if p["nom_propose"] == nom)
    admin.client.post(f"/api/admin/propositions/{proposition['id']}/decision", json={"decision": "refusee"})

    actions = base.execute(
        text("SELECT action FROM journal_action WHERE table_cible = 'proposition_metier' AND ligne_id = :id ORDER BY id"),
        {"id": proposition["id"]},
    ).scalars().all()

    assert actions == ["proposer_metier", "decider_proposition_metier"]
