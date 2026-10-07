"""Test de fiche du prestataire : ajout → modification → fiches liées (métier secondaire, photo de son travail)
→ suppression du prestataire refusée tant qu'une fiche liée existe → suppression.
(La commune est une donnée de référence chargée depuis la liste officielle : pas de fiche à part.)"""

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modeles.comptes import Compte
from app.modeles.fichiers import Fichier
from app.modeles.metiers import Metier
from app.modeles.prestataires import Commune, MetierSecondaire, PhotoPrestataire, Prestataire
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
               "metier_principal_suivant_id": electricien.id, "agenda_pas_minutes": 15,
               "annulation_delai_heures": 24, "declaration_periodicite": "mois"}
    liens_2 = {"compte_id": compte.id, "metier_principal_id": electricien.id, "commune_id": talence.id, "photo_id": None,
               "siret": None, "siret_statut": "absent", "statut": "actif",
               "metier_principal_suivant_id": None, "agenda_pas_minutes": 30,
               "annulation_delai_heures": 48, "declaration_periodicite": "trimestre"}

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

    # 3 bis. Fiche liée : une photo de son travail (ajout, modification, suppression du prestataire refusée)
    base.delete(base.get_one(MetierSecondaire, secondaire.id))
    base.commit()
    fichiers = []
    for variante in (1, 2):
        fichier = Fichier(**valeurs(Fichier, variante, {"depose_par_id": compte.id}))
        base.add(fichier)
        base.commit()
        fichiers.append(fichier.id)
    ajout_photo = valeurs(PhotoPrestataire, 1, {"prestataire_id": prestataire.id, "fichier_id": fichiers[0]})
    photo = PhotoPrestataire(**ajout_photo)
    base.add(photo)
    base.commit()
    relire_et_comparer(base, PhotoPrestataire, photo.id, ajout_photo)
    modification_photo = valeurs(PhotoPrestataire, 2, {"prestataire_id": prestataire.id, "fichier_id": fichiers[1]})
    for rubrique, valeur in modification_photo.items():
        setattr(photo, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, PhotoPrestataire, photo.id, modification_photo)

    base.delete(base.get_one(Prestataire, prestataire.id))
    with pytest.raises(IntegrityError):
        base.commit()
    base.rollback()

    # 4. Suppressions, désormais possibles
    for modele, identifiant in ((PhotoPrestataire, photo.id), (Prestataire, prestataire.id), (Fichier, fichiers[0]),
                                (Fichier, fichiers[1]), (Compte, compte.id)):
        base.delete(base.get_one(modele, identifiant))
        base.commit()
        base.expire_all()
        assert base.get(modele, identifiant) is None
