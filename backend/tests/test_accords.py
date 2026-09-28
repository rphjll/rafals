"""Accord des parents (RM-COMPTES.md, âge minimum ; lot 1.3)."""

from sqlalchemy import text
from sqlalchemy.orm import Session

PDF = b"%PDF-1.4\n% accord signe des parents de Lucas\n"
JPG = b"\xff\xd8\xff\xe0" + b"photo" * 100


def deposer(client, contenu: bytes = PDF, nom: str = "accord-parents.pdf", type_mime: str = "application/pdf"):
    return client.post("/api/moi/accord-parental", files={"fichier": (nom, contenu, type_mime)})


def decider(admin_client, accord_id: int, accepte: bool, motif: str | None = None):
    return admin_client.post(f"/api/admin/accords/{accord_id}/decision", json={"accepte": accepte, "motif_refus": motif})


def dernier_accord_id(base: Session, compte_id: int) -> int:
    return base.execute(
        text("SELECT max(id) FROM accord_parental WHERE compte_id = :c"), {"c": compte_id}
    ).scalar_one()


def test_lucas_16_ans_depose_son_accord(fabrique_compte) -> None:
    lucas = fabrique_compte(age=16)

    reponse = deposer(lucas.client)

    assert reponse.status_code == 201
    assert reponse.json()["statut"] == "en_attente"
    assert lucas.client.get("/api/moi/accord-parental").json()["necessaire"] is True


def test_un_majeur_n_a_pas_besoin_d_accord(fabrique_compte) -> None:
    marie = fabrique_compte(age=54)

    reponse = deposer(marie.client)

    assert reponse.status_code == 400
    assert "aucun accord des parents n'est nécessaire" in reponse.json()["detail"]


def test_fichier_refuse_si_le_contenu_ne_correspond_pas(fabrique_compte) -> None:
    lucas = fabrique_compte(age=16)

    faux_pdf = deposer(lucas.client, b"ceci est un texte, pas un PDF", "accord.pdf", "application/pdf")
    mauvais_format = deposer(lucas.client, b"GIF89a....", "accord.gif", "image/gif")

    assert faux_pdf.status_code == mauvais_format.status_code == 400
    assert "envoyez un PDF, JPG, PNG" in faux_pdf.json()["detail"]


def test_fichier_de_plus_de_5_mo_refuse(fabrique_compte) -> None:
    lucas = fabrique_compte(age=17)

    reponse = deposer(lucas.client, b"%PDF" + b"0" * (5 * 1024 * 1024))

    assert reponse.status_code == 400
    assert "5 Mo au maximum" in reponse.json()["detail"]


def test_un_seul_accord_en_attente_a_la_fois(fabrique_compte) -> None:
    lucas = fabrique_compte(age=16)
    deposer(lucas.client)

    reponse = deposer(lucas.client, JPG, "photo.jpg", "image/jpeg")

    assert reponse.status_code == 400
    assert reponse.json()["detail"] == "Un accord attend déjà la décision de l'administrateur."


def test_lucas_ne_peut_reserver_qu_apres_l_accord_accepte(fabrique_compte, base: Session) -> None:
    admin = fabrique_compte(administrateur=True)
    lucas = fabrique_compte(age=16)
    deposer(lucas.client)
    assert lucas.client.get("/api/moi").json()["peut_reserver_ou_publier"] is False

    reponse = decider(admin.client, dernier_accord_id(base, lucas.id), accepte=True)

    assert reponse.status_code == 200
    assert lucas.client.get("/api/moi").json()["peut_reserver_ou_publier"] is True


def test_majeur_peut_reserver_seulement_avec_adresse_verifiee(fabrique_compte) -> None:
    verifiee = fabrique_compte(age=30, verifie=True)
    pas_verifiee = fabrique_compte(age=30, verifie=False)

    assert verifiee.client.get("/api/moi").json()["peut_reserver_ou_publier"] is True
    assert pas_verifiee.client.get("/api/moi").json()["peut_reserver_ou_publier"] is False


def test_refus_avec_motif_puis_nouveau_depot(fabrique_compte, base: Session) -> None:
    admin = fabrique_compte(administrateur=True)
    ines = fabrique_compte(age=17)
    deposer(ines.client)
    accord_id = dernier_accord_id(base, ines.id)

    sans_motif = decider(admin.client, accord_id, accepte=False)
    avec_motif = decider(admin.client, accord_id, accepte=False, motif="Signature illisible")
    etat = ines.client.get("/api/moi/accord-parental").json()
    nouveau = deposer(ines.client, JPG, "accord-photo.jpg", "image/jpeg")

    assert sans_motif.status_code == 400
    assert "motif du refus" in sans_motif.json()["detail"]
    assert avec_motif.status_code == 200
    assert etat["statut"] == "refuse" and etat["motif_refus"] == "Signature illisible"
    assert nouveau.status_code == 201


def test_un_accord_ne_se_decide_qu_une_fois(fabrique_compte, base: Session) -> None:
    admin = fabrique_compte(administrateur=True)
    lucas = fabrique_compte(age=16)
    deposer(lucas.client)
    accord_id = dernier_accord_id(base, lucas.id)
    decider(admin.client, accord_id, accepte=True)

    reponse = decider(admin.client, accord_id, accepte=False, motif="Changement d'avis")

    assert reponse.status_code == 400
    assert reponse.json()["detail"] == "Cet accord a déjà été décidé."


def test_seul_un_administrateur_voit_et_decide(fabrique_compte, base: Session, client) -> None:
    lucas = fabrique_compte(age=16)
    marie = fabrique_compte(age=54)
    deposer(lucas.client)
    accord_id = dernier_accord_id(base, lucas.id)

    assert marie.client.get("/api/admin/accords").status_code == 403
    assert decider(marie.client, accord_id, accepte=True).status_code == 403
    assert client.get("/api/admin/accords").status_code == 401  # personne n'est connecté


def test_l_administrateur_voit_le_fichier_depose(fabrique_compte, base: Session) -> None:
    admin = fabrique_compte(administrateur=True)
    lucas = fabrique_compte(age=16)
    deposer(lucas.client)
    accord_id = dernier_accord_id(base, lucas.id)

    liste = admin.client.get("/api/admin/accords").json()
    fichier = admin.client.get(f"/api/admin/accords/{accord_id}/fichier")

    assert accord_id in [a["id"] for a in liste]
    assert fichier.status_code == 200
    assert fichier.content == PDF
    assert fichier.headers["content-type"] == "application/pdf"


def test_depot_et_decision_notes_au_journal(fabrique_compte, base: Session) -> None:
    admin = fabrique_compte(administrateur=True)
    lucas = fabrique_compte(age=16)
    deposer(lucas.client)
    accord_id = dernier_accord_id(base, lucas.id)
    decider(admin.client, accord_id, accepte=True)

    lignes = base.execute(
        text("SELECT auteur_id, action, apres->>'statut' FROM journal_action "
             "WHERE table_cible = 'accord_parental' AND ligne_id = :id ORDER BY id"),
        {"id": accord_id},
    ).all()

    assert [tuple(l) for l in lignes] == [
        (lucas.id, "deposer_accord_parental", "en_attente"),
        (admin.id, "decider_accord_parental", "accepte"),
    ]
