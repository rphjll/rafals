"""Tests de fiche du lot 8.3 (première partie) : demande publiée, photo d'une demande.
Chacune : ajout → modification → suppression de la fiche principale refusée tant que la fiche liée existe → suppression."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modeles.demandes import Demande, PhotoDemandePubliee
from app.modeles.fichiers import Fichier
from tests.fiches.outils import relire_et_comparer, valeurs
from tests.fiches.test_fiche_annonce import _supprimer, decor  # noqa: F401 (le décor est une fixture)


def test_fiche_demande_photo(base: Session, decor) -> None:  # noqa: F811
    compte, _, (plombier, electricien), (pessac, talence) = decor

    # Demande : ouverte et pas cachée à l'ajout ; fermée, chez le prestataire et cachée à la modification
    ajout = valeurs(Demande, 1, {
        "client_id": compte.id, "metier_id": plombier.id, "commune_id": pessac.id, "cachee_par_id": None, "cachee_le": None,
        "quand": "jour_precis", "lieu": "chez_moi", "statut": "ouverte", "code_postal": "33600",
    })
    demande = Demande(**ajout)
    base.add(demande)
    base.commit()
    relire_et_comparer(base, Demande, demande.id, ajout)
    modification = valeurs(Demande, 2, {
        "client_id": compte.id, "metier_id": electricien.id, "commune_id": talence.id, "cachee_par_id": compte.id,
        "quand": "jour_precis", "lieu": "chez_prestataire", "statut": "fermee", "code_postal": "33400",
    })
    for rubrique, valeur in modification.items():
        setattr(demande, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, Demande, demande.id, modification)

    # Fiche liée : une photo
    fichiers = []
    for variante in (1, 2):
        fichier = Fichier(**valeurs(Fichier, variante, {"depose_par_id": compte.id}))
        base.add(fichier)
        base.commit()
        fichiers.append(fichier.id)
    ajout_photo = valeurs(PhotoDemandePubliee, 1, {"demande_id": demande.id, "fichier_id": fichiers[0]})
    photo = PhotoDemandePubliee(**ajout_photo)
    base.add(photo)
    base.commit()
    relire_et_comparer(base, PhotoDemandePubliee, photo.id, ajout_photo)
    modification_photo = valeurs(PhotoDemandePubliee, 2, {"demande_id": demande.id, "fichier_id": fichiers[1]})
    for rubrique, valeur in modification_photo.items():
        setattr(photo, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, PhotoDemandePubliee, photo.id, modification_photo)

    # La demande ne disparaît pas tant qu'une photo existe
    base.delete(base.get_one(Demande, demande.id))
    with pytest.raises(IntegrityError):
        base.commit()
    base.rollback()

    for modele, identifiant in ((PhotoDemandePubliee, photo.id), (Demande, demande.id), (Fichier, fichiers[0]), (Fichier, fichiers[1])):
        _supprimer(base, modele, identifiant)
