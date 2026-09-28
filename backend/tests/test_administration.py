"""Rôle administrateur et journal des actions (RM-COMPTES.md, administrateurs ; lot 1.3)."""

import pytest
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session


def role(client, compte_id: int, est_administrateur: bool):
    return client.post(f"/api/admin/comptes/{compte_id}/administrateur", json={"est_administrateur": est_administrateur})


def test_raphael_nomme_tom_administrateur_et_c_est_note(fabrique_compte, base: Session) -> None:
    raphael = fabrique_compte(administrateur=True)
    tom = fabrique_compte()

    reponse = role(raphael.client, tom.id, True)
    journal = base.execute(
        text("SELECT auteur_id, action, avant, apres FROM journal_action "
             "WHERE table_cible = 'compte' AND ligne_id = :id"),
        {"id": tom.id},
    ).one()

    assert reponse.status_code == 200
    assert reponse.json()["est_administrateur"] is True
    assert tom.client.get("/api/moi").json()["est_administrateur"] is True
    assert tuple(journal) == (
        raphael.id,
        "nommer_administrateur",
        {"est_administrateur": False},
        {"est_administrateur": True},
    )


def test_on_ne_retire_jamais_le_dernier_administrateur(fabrique_compte, base: Session) -> None:
    raphael = fabrique_compte(administrateur=True)
    # Pour ce test, Raphael est le seul administrateur de la base de test
    base.execute(text("UPDATE compte SET est_administrateur = false WHERE id <> :id"), {"id": raphael.id})
    base.commit()

    reponse = role(raphael.client, raphael.id, False)

    assert reponse.status_code == 400
    assert reponse.json()["detail"] == "Il doit toujours rester au moins un administrateur."


def test_avec_deux_administrateurs_on_peut_en_retirer_un(fabrique_compte) -> None:
    raphael = fabrique_compte(administrateur=True)
    tom = fabrique_compte(administrateur=True)

    reponse = role(raphael.client, tom.id, False)

    assert reponse.status_code == 200
    assert tom.client.get("/api/moi").json()["est_administrateur"] is False


def test_un_non_administrateur_n_a_pas_acces(fabrique_compte) -> None:
    marie = fabrique_compte()
    tom = fabrique_compte()

    assert marie.client.get("/api/admin/comptes").status_code == 403
    assert role(marie.client, tom.id, True).status_code == 403


def test_l_administrateur_voit_la_liste_des_comptes(fabrique_compte) -> None:
    raphael = fabrique_compte(administrateur=True)
    marie = fabrique_compte()

    emails = [c["email"] for c in raphael.client.get("/api/admin/comptes").json()]

    assert marie.email in emails


def test_le_journal_ne_se_modifie_ni_ne_s_efface(fabrique_compte, base: Session) -> None:
    raphael = fabrique_compte(administrateur=True)
    tom = fabrique_compte()
    role(raphael.client, tom.id, True)

    with pytest.raises(ProgrammingError, match="permission denied"):
        base.execute(text("UPDATE journal_action SET action = 'triche' WHERE ligne_id = :id"), {"id": tom.id})
    base.rollback()
    with pytest.raises(ProgrammingError, match="permission denied"):
        base.execute(text("DELETE FROM journal_action WHERE ligne_id = :id"), {"id": tom.id})
    base.rollback()
