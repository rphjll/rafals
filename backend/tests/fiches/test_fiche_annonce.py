"""Tests de fiche du lot 3.1 : local, annonce, et photo d'annonce (fiche liée).
Annonce : ajout → modification → fiche liée (photo) → suppression de l'annonce refusée tant qu'une photo existe → suppression.
(Dans l'application, une annonce n'est jamais effacée ; la base, elle, doit savoir le faire proprement.)"""

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modeles.annonces import Annonce, Local, PhotoAnnonce
from app.modeles.comptes import Compte
from app.modeles.fichiers import Fichier
from app.modeles.metiers import Metier
from app.modeles.prestataires import Commune, Prestataire
from tests.fiches.outils import relire_et_comparer, valeurs


def _supprimer(base: Session, modele: type, identifiant: int) -> None:
    base.delete(base.get_one(modele, identifiant))
    base.commit()
    base.expire_all()
    assert base.get(modele, identifiant) is None


@pytest.fixture
def decor(base: Session):
    """Un compte et un prestataire d'essai (plombier à Pessac), effacés à la fin."""
    compte = Compte(**valeurs(Compte, 1))
    base.add(compte)
    base.commit()
    plombier = base.scalar(select(Metier).where(Metier.code == "plombier"))
    electricien = base.scalar(select(Metier).where(Metier.code == "electricien"))
    pessac = base.scalar(select(Commune).where(Commune.code_insee == "33318"))
    talence = base.scalar(select(Commune).where(Commune.code_insee == "33522"))
    assert plombier and electricien and pessac and talence
    prestataire = Prestataire(**valeurs(Prestataire, 1, {
        "compte_id": compte.id, "metier_principal_id": plombier.id, "commune_id": pessac.id, "photo_id": None,
        "siret": None, "siret_statut": "absent", "statut": "actif", "metier_principal_suivant_id": None, "agenda_pas_minutes": 15, "annulation_delai_heures": 24,
        "declaration_periodicite": None, "lieu": "chez_client",
    }))
    base.add(prestataire)
    base.commit()
    yield compte, prestataire, (plombier, electricien), (pessac, talence)
    base.rollback()
    for modele, identifiant in ((Prestataire, prestataire.id), (Compte, compte.id)):
        _supprimer(base, modele, identifiant)


def test_fiche_local(base: Session, decor) -> None:
    _, prestataire, _, (pessac, talence) = decor
    ajout = valeurs(Local, 1, {"prestataire_id": prestataire.id, "commune_id": pessac.id, "code_postal": "33600"})
    local = Local(**ajout)
    base.add(local)
    base.commit()
    relire_et_comparer(base, Local, local.id, ajout)

    modification = valeurs(Local, 2, {"prestataire_id": prestataire.id, "commune_id": talence.id, "code_postal": "33400"})
    for rubrique, valeur in modification.items():
        setattr(local, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, Local, local.id, modification)

    # Le prestataire ne peut pas disparaître tant que son local existe
    base.delete(base.get_one(Prestataire, prestataire.id))
    with pytest.raises(IntegrityError):
        base.commit()
    base.rollback()
    _supprimer(base, Local, local.id)


def test_fiche_annonce(base: Session, decor) -> None:
    compte, prestataire, (plombier, electricien), _ = decor
    # Valeurs imposées par les contraintes : forme du prix cohérente avec prix, durée et heures ; listes de valeurs
    fixe = {"prestataire_id": prestataire.id, "metier_id": plombier.id, "forme_prix": "fixe", "prix_centimes": 5000,
            "duree_minutes": 120, "heures_min": None, "heures_max": None, "lieu": "chez_client",
            "paiement_especes": True, "statut": "en_ligne"}
    a_l_heure = {"prestataire_id": prestataire.id, "metier_id": electricien.id, "forme_prix": "heure", "prix_centimes": 2500,
                 "duree_minutes": None, "heures_min": 2, "heures_max": 4, "lieu": "les_deux",
                 "paiement_especes": True, "statut": "en_pause"}

    # 1. Ajout, puis relecture
    ajout = valeurs(Annonce, 1, fixe)
    annonce = Annonce(**ajout)
    base.add(annonce)
    base.commit()
    relire_et_comparer(base, Annonce, annonce.id, ajout)

    # 2. Modification de toutes les rubriques, puis relecture
    modification = valeurs(Annonce, 2, a_l_heure)
    for rubrique, valeur in modification.items():
        setattr(annonce, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, Annonce, annonce.id, modification)

    # 3. Fiche liée : une photo (ajout, modification, suppression de l'annonce refusée)
    fichiers = []
    for variante in (1, 2):
        fichier = Fichier(**valeurs(Fichier, variante, {"depose_par_id": compte.id}))
        base.add(fichier)
        base.commit()
        fichiers.append(fichier.id)
    ajout_lie = valeurs(PhotoAnnonce, 1, {"annonce_id": annonce.id, "fichier_id": fichiers[0]})
    photo = PhotoAnnonce(**ajout_lie)
    base.add(photo)
    base.commit()
    relire_et_comparer(base, PhotoAnnonce, photo.id, ajout_lie)
    modification_liee = valeurs(PhotoAnnonce, 2, {"annonce_id": annonce.id, "fichier_id": fichiers[1]})
    for rubrique, valeur in modification_liee.items():
        setattr(photo, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, PhotoAnnonce, photo.id, modification_liee)

    base.delete(base.get_one(Annonce, annonce.id))
    with pytest.raises(IntegrityError):
        base.commit()
    base.rollback()

    # 4. Suppressions, désormais possibles
    _supprimer(base, PhotoAnnonce, photo.id)
    _supprimer(base, Annonce, annonce.id)
    for identifiant in fichiers:
        _supprimer(base, Fichier, identifiant)
