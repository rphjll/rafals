"""Test de fiche du lot 7.1 : dossier de création d'auto-entreprise, et son papier (fiche liée).
Ajout → modification → fiche liée (papier) → suppression du dossier refusée tant qu'un papier existe → suppression."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modeles.creation import DossierCreation, PieceDossier
from app.modeles.fichiers import Fichier
from tests.fiches.outils import relire_et_comparer, valeurs
from tests.fiches.test_fiche_local import _supprimer, decor  # noqa: F401 (le décor est une fixture)


def test_fiche_dossier_creation(base: Session, decor) -> None:  # noqa: F811
    compte, _, (plombier, electricien), (pessac, talence) = decor
    # Valeurs imposées : listes de valeurs, formats (15 chiffres, 9 chiffres, 5 chiffres), et cohérence de l'état
    communes = {"civilite": "monsieur", "nationalite": "francaise", "situation_famille": "celibataire", "naissance_pays": None,
                "activite_en_meme_temps": "aucune", "ancien_siren": "443061841", "compte_id": compte.id}
    ajout = valeurs(DossierCreation, 1, communes | {
        "metier_id": plombier.id, "commune_id": pessac.id, "naissance_commune_id": talence.id, "local_commune_id": None,
        "lieu_travail": "chez_clients", "periodicite": "trimestre", "numero_secu": "198033306312352", "code_postal": "33600",
        "local_code_postal": None, "statut": "brouillon", "envoye_le": None, "siret_recu": None, "sensible_efface_le": None,
    })
    dossier = DossierCreation(**ajout)
    base.add(dossier)
    base.commit()
    relire_et_comparer(base, DossierCreation, dossier.id, ajout)

    # Accepté : envoyé, SIRET reçu, données sensibles effacées
    modification = valeurs(DossierCreation, 2, communes | {
        "metier_id": electricien.id, "commune_id": talence.id, "naissance_commune_id": pessac.id, "local_commune_id": pessac.id,
        "lieu_travail": "local", "periodicite": "mois", "numero_secu": None, "pere_nom": None, "mere_nom": None,
        "code_postal": "33400", "local_code_postal": "33600", "statut": "accepte", "siret_recu": "91234567800017",
        "civilite": "madame", "situation_famille": "marie", "activite_en_meme_temps": "salarie",
    })
    for rubrique, valeur in modification.items():
        setattr(dossier, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, DossierCreation, dossier.id, modification)

    # Fiche liée : un papier, avec son fichier puis effacé (le fichier est là tant que le papier n'est pas effacé)
    fichier = Fichier(**valeurs(Fichier, 1, {"depose_par_id": compte.id}))
    base.add(fichier)
    base.commit()
    ajout_piece = valeurs(PieceDossier, 1, {"dossier_id": dossier.id, "fichier_id": fichier.id, "sorte": "identite", "efface_le": None})
    piece = PieceDossier(**ajout_piece)
    base.add(piece)
    base.commit()
    relire_et_comparer(base, PieceDossier, piece.id, ajout_piece)
    modification_piece = valeurs(PieceDossier, 2, {"dossier_id": dossier.id, "fichier_id": None, "sorte": "diplome"})
    for rubrique, valeur in modification_piece.items():
        setattr(piece, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, PieceDossier, piece.id, modification_piece)

    base.delete(base.get_one(DossierCreation, dossier.id))
    with pytest.raises(IntegrityError):
        base.commit()
    base.rollback()
    for modele, identifiant in ((PieceDossier, piece.id), (Fichier, fichier.id), (DossierCreation, dossier.id)):
        _supprimer(base, modele, identifiant)
