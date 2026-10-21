"""Test de fiche de l'abonnement (schema_v31, demande de Raphael du 21/10/2026).
Ajout → modification → suppression du compte et du prestataire refusée tant que l'abonnement existe → suppression."""

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modeles.abonnements import Abonnement
from app.modeles.comptes import Compte
from app.modeles.prestataires import Prestataire
from tests.fiches.outils import relire_et_comparer, valeurs
from tests.fiches.test_fiche_local import _supprimer
from tests.test_prestataires import fabrique_prestataire, metiers  # noqa: F401 (fixtures)


def test_fiche_abonnement(base: Session, fabrique_prestataire, fabrique_compte) -> None:  # noqa: F811
    karim, julie = fabrique_prestataire(), fabrique_compte()
    prestataire = base.scalar(select(Prestataire).where(Prestataire.compte_id == karim.id))
    liens = {"compte_id": julie.id, "prestataire_id": prestataire.id}

    ajout = valeurs(Abonnement, 1, liens)
    abonnement = Abonnement(**ajout)
    base.add(abonnement)
    base.commit()
    relire_et_comparer(base, Abonnement, abonnement.id, ajout)

    modification = valeurs(Abonnement, 2, liens)
    for rubrique, valeur in modification.items():
        setattr(abonnement, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, Abonnement, abonnement.id, modification)

    # Ni le compte abonné ni le prestataire suivi ne disparaissent tant que l'abonnement existe
    for modele, identifiant in ((Compte, julie.id), (Prestataire, prestataire.id)):
        base.delete(base.get_one(modele, identifiant))
        with pytest.raises(IntegrityError):
            base.commit()
        base.rollback()
    _supprimer(base, Abonnement, abonnement.id)
