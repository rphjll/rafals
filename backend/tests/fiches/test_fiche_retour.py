"""Test de fiche du retour « Un problème ? Une idée ? » (schema_v34, lot 13.1).
Ajout → modification → fiches liées (le compte ne peut pas disparaître tant que le retour existe ; effacer la capture
vide seulement la case) → suppression."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modeles.comptes import Compte
from app.modeles.fichiers import Fichier
from app.modeles.retours import Retour
from tests.fiches.outils import relire_et_comparer, valeurs
from tests.fiches.test_fiche_local import _supprimer


def test_fiche_retour(base: Session) -> None:
    auteur = Compte(**valeurs(Compte, 1))
    base.add(auteur)
    base.commit()
    captures = [Fichier(**valeurs(Fichier, v, {"depose_par_id": auteur.id})) for v in (1, 2)]
    base.add_all(captures)
    base.commit()

    # Valeurs imposées par la base : sorte, appareil et statut dans leur liste
    ajout = valeurs(Retour, 1, {"auteur_id": auteur.id, "fichier_id": captures[0].id, "sorte": "probleme",
                                "appareil": "telephone", "statut": "a_traiter"})
    retour = Retour(**ajout)
    base.add(retour)
    base.commit()
    relire_et_comparer(base, Retour, retour.id, ajout)

    modification = valeurs(Retour, 2, {"auteur_id": auteur.id, "fichier_id": captures[1].id, "sorte": "idee",
                                       "appareil": "ordinateur", "statut": "injurieux"})
    for rubrique, valeur in modification.items():
        setattr(retour, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, Retour, retour.id, modification)

    # Le compte qui a écrit ne peut pas disparaître tant que le retour existe
    base.delete(base.get_one(Compte, auteur.id))
    with pytest.raises(IntegrityError):
        base.commit()
    base.rollback()

    # Effacer la capture (problème réglé) ne supprime pas le retour : la case redevient vide
    _supprimer(base, Fichier, captures[1].id)
    assert base.get_one(Retour, retour.id).fichier_id is None

    _supprimer(base, Retour, retour.id)
    _supprimer(base, Fichier, captures[0].id)
    _supprimer(base, Compte, auteur.id)
