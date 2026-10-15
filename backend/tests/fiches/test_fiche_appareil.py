"""Test de fiche du lot 8.7 : appareil (un téléphone qui reçoit les notifications).
Ajout → modification → suppression du compte refusée tant que l'appareil existe → suppression."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modeles.appareils import Appareil
from app.modeles.comptes import Compte
from tests.fiches.outils import relire_et_comparer, valeurs
from tests.fiches.test_fiche_annonce import _supprimer


def test_fiche_appareil(base: Session) -> None:
    compte = Compte(**valeurs(Compte, 1))
    base.add(compte)
    base.commit()

    ajout = valeurs(Appareil, 1, {"compte_id": compte.id})
    appareil = Appareil(**ajout)
    base.add(appareil)
    base.commit()
    relire_et_comparer(base, Appareil, appareil.id, ajout)

    modification = valeurs(Appareil, 2, {"compte_id": compte.id})
    for rubrique, valeur in modification.items():
        setattr(appareil, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, Appareil, appareil.id, modification)

    # Le compte ne disparaît pas tant qu'un appareil y est rattaché
    base.delete(base.get_one(Compte, compte.id))
    with pytest.raises(IntegrityError):
        base.commit()
    base.rollback()
    for modele, identifiant in ((Appareil, appareil.id), (Compte, compte.id)):
        _supprimer(base, modele, identifiant)
