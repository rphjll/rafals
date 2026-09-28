"""Test de fiche du fichier : ajout → modification → fiche liée (accord des parents)
→ suppression du fichier refusée tant que l'accord existe → suppression.
(Le journal des actions n'a pas de test de fiche : il ne se modifie ni ne s'efface, voir test_administration.py.)"""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modeles.comptes import Compte
from app.modeles.fichiers import AccordParental, Fichier
from tests.fiches.outils import relire_et_comparer, valeurs


def test_fiche_fichier(base: Session) -> None:
    proprietaire = Compte(**valeurs(Compte, 1))
    base.add(proprietaire)
    base.commit()

    # 1. Ajout, puis relecture
    ajout = valeurs(Fichier, 1, {"depose_par_id": proprietaire.id})
    fichier = Fichier(**ajout)
    base.add(fichier)
    base.commit()
    relire_et_comparer(base, Fichier, fichier.id, ajout)

    # 2. Modification de toutes les rubriques, puis relecture
    modification = valeurs(Fichier, 2, {"depose_par_id": proprietaire.id})
    for rubrique, valeur in modification.items():
        setattr(fichier, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, Fichier, fichier.id, modification)

    # 3. Fiche liée : l'accord des parents (valeurs cohérentes imposées par la base : refusé = décidé + motif)
    lien = {"compte_id": proprietaire.id, "fichier_id": fichier.id, "decide_par_id": proprietaire.id}
    ajout_accord = valeurs(AccordParental, 1, lien | {"statut": "refuse"})
    accord = AccordParental(**ajout_accord)
    base.add(accord)
    base.commit()
    relire_et_comparer(base, AccordParental, accord.id, ajout_accord)

    modification_accord = valeurs(AccordParental, 2, lien | {"statut": "accepte", "motif_refus": None})
    for rubrique, valeur in modification_accord.items():
        setattr(accord, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, AccordParental, accord.id, modification_accord)

    base.delete(base.get_one(Fichier, fichier.id))
    with pytest.raises(IntegrityError):
        base.commit()
    base.rollback()

    base.delete(base.get_one(AccordParental, accord.id))
    base.commit()

    # 4. Suppression du fichier, désormais possible
    identifiant = fichier.id
    base.delete(base.get_one(Fichier, identifiant))
    base.commit()
    base.expire_all()
    assert base.get(Fichier, identifiant) is None

    base.delete(base.get_one(Compte, proprietaire.id))
    base.commit()
