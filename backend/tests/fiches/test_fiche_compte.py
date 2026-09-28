"""Test de fiche du compte : ajout → modification → fiches liées (session, lien par mail)
→ suppression du compte refusée tant qu'un lien existe → suppression."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modeles.comptes import Compte, JetonMail, SessionConnexion
from tests.fiches.outils import relire_et_comparer, valeurs

# Rubriques limitées par la base à une liste de valeurs (contrainte jeton_mail_usage_connu)
USAGES = {1: "verification", 2: "mot_de_passe"}


def modifier(db: Session, ligne: object, nouvelles_valeurs: dict) -> None:
    for rubrique, valeur in nouvelles_valeurs.items():
        setattr(ligne, rubrique, valeur)
    db.commit()


def suppression_du_compte_refusee(db: Session, compte: Compte) -> None:
    db.delete(compte)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_fiche_compte(base: Session) -> None:
    # 1. Ajout, toutes les rubriques remplies, puis relecture
    ajout = valeurs(Compte, 1)
    compte = Compte(**ajout)
    base.add(compte)
    base.commit()
    relire_et_comparer(base, Compte, compte.id, ajout)

    # 2. Modification de toutes les rubriques, puis relecture
    modification = valeurs(Compte, 2)
    modifier(base, compte, modification)
    relire_et_comparer(base, Compte, compte.id, modification)

    # 3. Fiches liées : ajout, modification, suppression du compte refusée, suppression de la fiche liée
    for modele, imposees in (
        (SessionConnexion, lambda v: {"compte_id": compte.id}),
        (JetonMail, lambda v: {"compte_id": compte.id, "usage": USAGES[v]}),
    ):
        ajout_lie = valeurs(modele, 1, imposees(1))
        liee = modele(**ajout_lie)
        base.add(liee)
        base.commit()
        relire_et_comparer(base, modele, liee.id, ajout_lie)

        modification_liee = valeurs(modele, 2, imposees(2))
        modifier(base, liee, modification_liee)
        relire_et_comparer(base, modele, liee.id, modification_liee)

        suppression_du_compte_refusee(base, base.get_one(Compte, compte.id))

        base.delete(base.get_one(modele, liee.id))
        base.commit()
        assert base.get(modele, liee.id) is None

    # 4. Suppression du compte, désormais possible
    identifiant = compte.id
    base.delete(base.get_one(Compte, identifiant))
    base.commit()
    base.expire_all()
    assert base.get(Compte, identifiant) is None
