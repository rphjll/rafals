"""Tests de fiche du lot 3.3 : plage horaire (semaine type) et blocage, rattachés à un prestataire.
Chacune : ajout → modification → suppression du prestataire refusée tant qu'elle existe → suppression."""

from datetime import UTC, datetime, time, timedelta

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modeles.agenda import Blocage, PlageHoraire
from app.modeles.prestataires import Prestataire
from tests.fiches.outils import relire_et_comparer, valeurs
from tests.fiches.test_fiche_annonce import _supprimer, decor  # noqa: F401 (le décor est une fixture)


# Valeurs imposées par les contraintes : jour de 1 à 7, fin après le début
LE_14 = datetime(2027, 10, 14, 12, 0, tzinfo=UTC)


@pytest.mark.parametrize(("modele", "imposees"), [
    (PlageHoraire, [{"jour_semaine": 2, "debut": time(9), "fin": time(12)},
                    {"jour_semaine": 6, "debut": time(14), "fin": time(19)}]),
    (Blocage, [{"debut": LE_14, "fin": LE_14 + timedelta(hours=2)},
               {"debut": LE_14 + timedelta(days=1), "fin": LE_14 + timedelta(days=20)}]),
])
def test_fiche_agenda(base: Session, decor, modele, imposees) -> None:  # noqa: F811
    _, prestataire, _, _ = decor
    ajout = valeurs(modele, 1, {"prestataire_id": prestataire.id, **imposees[0]})
    ligne = modele(**ajout)
    base.add(ligne)
    base.commit()
    relire_et_comparer(base, modele, ligne.id, ajout)

    modification = valeurs(modele, 2, {"prestataire_id": prestataire.id, **imposees[1]})
    for rubrique, valeur in modification.items():
        setattr(ligne, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, modele, ligne.id, modification)

    base.delete(base.get_one(Prestataire, prestataire.id))
    with pytest.raises(IntegrityError):
        base.commit()
    base.rollback()
    _supprimer(base, modele, ligne.id)
