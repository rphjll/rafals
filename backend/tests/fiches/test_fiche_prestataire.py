"""Test de fiche du prestataire : ajout → modification → fiche liée (métier secondaire)
→ suppression du prestataire refusée tant qu'un métier secondaire existe → suppression.
(La commune est une donnée de référence chargée depuis la liste officielle : pas de fiche à part.)"""

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modeles.comptes import Compte
from app.modeles.metiers import Metier
from app.modeles.prestataires import Commune, MetierSecondaire, Prestataire
from tests.fiches.outils import relire_et_comparer, valeurs


def test_fiche_prestataire(base: Session) -> None:
    compte = Compte(**valeurs(Compte, 1))
    base.add(compte)
    base.commit()
    plombier = base.scalar(select(Metier).where(Metier.code == "plombier"))
    electricien = base.scalar(select(Metier).where(Metier.code == "electricien"))
    pessac = base.scalar(select(Commune).where(Commune.code_insee == "33318"))
    talence = base.scalar(select(Commune).where(Commune.code_insee == "33522"))
    assert plombier and electricien and pessac and talence

    # Valeurs imposées par les contraintes de la base (formats, listes de statuts, cohérence SIRET)
    liens_1 = {"compte_id": compte.id, "metier_principal_id": plombier.id, "commune_id": pessac.id, "photo_id": None,
               "siret": "44306184100047", "siret_statut": "a_verifier", "statut": "en_pause",
               "metier_principal_suivant_id": electricien.id}
    liens_2 = {"compte_id": compte.id, "metier_principal_id": electricien.id, "commune_id": talence.id, "photo_id": None,
               "siret": None, "siret_statut": "absent", "statut": "actif",
               "metier_principal_suivant_id": None}

    # 1. Ajout, puis relecture
    ajout = valeurs(Prestataire, 1, liens_1)
    prestataire = Prestataire(**ajout)
    base.add(prestataire)
    base.commit()
    relire_et_comparer(base, Prestataire, prestataire.id, ajout)

    # 2. Modification de toutes les rubriques, puis relecture
    modification = valeurs(Prestataire, 2, liens_2)
    for rubrique, valeur in modification.items():
        setattr(prestataire, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, Prestataire, prestataire.id, modification)

    # 3. Fiche liée : un métier secondaire (ajout, modification, suppression du prestataire refusée)
    ajout_lie = valeurs(MetierSecondaire, 1, {"prestataire_id": prestataire.id, "metier_id": plombier.id})
    secondaire = MetierSecondaire(**ajout_lie)
    base.add(secondaire)
    base.commit()
    relire_et_comparer(base, MetierSecondaire, secondaire.id, ajout_lie)
    modification_liee = valeurs(MetierSecondaire, 2, {"prestataire_id": prestataire.id, "metier_id": electricien.id})
    for rubrique, valeur in modification_liee.items():
        setattr(secondaire, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, MetierSecondaire, secondaire.id, modification_liee)

    base.delete(base.get_one(Prestataire, prestataire.id))
    with pytest.raises(IntegrityError):
        base.commit()
    base.rollback()

    # 4. Suppressions, désormais possibles
    for modele, identifiant in ((MetierSecondaire, secondaire.id), (Prestataire, prestataire.id), (Compte, compte.id)):
        base.delete(base.get_one(modele, identifiant))
        base.commit()
        base.expire_all()
        assert base.get(modele, identifiant) is None
