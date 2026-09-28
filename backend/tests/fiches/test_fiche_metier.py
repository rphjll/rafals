"""Tests de fiche du dossier de métiers et du métier :
ajout → modification → fiche liée → suppression de la fiche principale refusée → suppression."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modeles.comptes import Compte
from app.modeles.metiers import CategorieMetier, Metier, PropositionMetier
from tests.fiches.outils import relire_et_comparer, valeurs


def modifier(db: Session, ligne: object, nouvelles: dict) -> None:
    for rubrique, valeur in nouvelles.items():
        setattr(ligne, rubrique, valeur)
    db.commit()


def suppression_refusee(db: Session, modele: type, identifiant: int) -> None:
    db.delete(db.get_one(modele, identifiant))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_fiche_categorie_et_metier(base: Session) -> None:
    compte = Compte(**valeurs(Compte, 1))
    base.add(compte)
    base.commit()

    # Dossier : ajout, modification
    ajout = valeurs(CategorieMetier, 1)
    categorie = CategorieMetier(**ajout)
    base.add(categorie)
    base.commit()
    relire_et_comparer(base, CategorieMetier, categorie.id, ajout)
    modification = valeurs(CategorieMetier, 2)
    modifier(base, categorie, modification)
    relire_et_comparer(base, CategorieMetier, categorie.id, modification)

    # Fiche liée au dossier : le métier (ajout, modification)
    ajout_metier = valeurs(Metier, 1, {"categorie_id": categorie.id})
    metier = Metier(**ajout_metier)
    base.add(metier)
    base.commit()
    relire_et_comparer(base, Metier, metier.id, ajout_metier)
    modification_metier = valeurs(Metier, 2, {"categorie_id": categorie.id})
    modifier(base, metier, modification_metier)
    relire_et_comparer(base, Metier, metier.id, modification_metier)
    suppression_refusee(base, CategorieMetier, categorie.id)

    # Fiche liée au métier : la proposition (valeurs cohérentes imposées par la base)
    lien = {"propose_par_id": compte.id, "decide_par_id": compte.id, "metier_retenu_id": metier.id}
    ajout_prop = valeurs(PropositionMetier, 1, lien | {"statut": "acceptee"})
    proposition = PropositionMetier(**ajout_prop)
    base.add(proposition)
    base.commit()
    relire_et_comparer(base, PropositionMetier, proposition.id, ajout_prop)
    modification_prop = valeurs(PropositionMetier, 2, lien | {"statut": "remplacee"})
    modifier(base, proposition, modification_prop)
    relire_et_comparer(base, PropositionMetier, proposition.id, modification_prop)
    suppression_refusee(base, Metier, metier.id)

    # Suppressions, dans l'ordre inverse, désormais possibles
    for modele, identifiant in (
        (PropositionMetier, proposition.id),
        (Metier, metier.id),
        (CategorieMetier, categorie.id),
        (Compte, compte.id),
    ):
        base.delete(base.get_one(modele, identifiant))
        base.commit()
        base.expire_all()
        assert base.get(modele, identifiant) is None
