"""Tests de fiche du lot 5.3 : demande de devis (+ photo liée), devis (+ ligne liée, + blocage des jours).
Ajout → modification → fiche liée (suppression de la fiche principale refusée tant que le lien existe) → suppression."""

from datetime import UTC, date, datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modeles.agenda import Blocage
from app.modeles.annonces import Annonce
from app.modeles.devis import DemandeDevis, Devis, LigneDevis, PhotoDemande
from app.modeles.fichiers import Fichier
from tests.fiches.outils import relire_et_comparer, valeurs
from tests.fiches.test_fiche_annonce import _supprimer, decor  # noqa: F401 (le décor est une fixture)

LE_14 = date(2027, 10, 14)


def _annonce(base: Session, prestataire, plombier) -> Annonce:
    annonce = Annonce(**valeurs(Annonce, 1, {
        "prestataire_id": prestataire.id, "metier_id": plombier.id, "forme_prix": "devis", "prix_centimes": None,
        "duree_minutes": None, "heures_min": None, "heures_max": None, "lieu": "chez_client", "paiement_especes": True,
        "statut": "en_ligne"}))
    base.add(annonce)
    base.commit()
    return annonce


def _demande(base: Session, compte, prestataire, annonce, commune_id: int) -> DemandeDevis:
    demande = DemandeDevis(**valeurs(DemandeDevis, 1, {
        "client_id": compte.id, "annonce_id": annonce.id, "prestataire_id": prestataire.id, "commune_id": commune_id,
        "code_postal": "33600", "texte": "Muret de 5 mètres au fond du jardin", "statut": "envoyee"}))
    base.add(demande)
    base.commit()
    return demande


def test_fiche_demande_devis_et_photo(base: Session, decor) -> None:  # noqa: F811
    compte, prestataire, (plombier, _), (pessac, talence) = decor
    annonce = _annonce(base, prestataire, plombier)
    liens = {"client_id": compte.id, "annonce_id": annonce.id, "prestataire_id": prestataire.id}
    # Valeurs imposées : liste des statuts, longueur du texte, adresse complète
    ajout = valeurs(DemandeDevis, 1, {**liens, "commune_id": pessac.id, "code_postal": "33600", "statut": "envoyee",
                                      "texte": "Muret de 5 mètres au fond du jardin"})
    demande = DemandeDevis(**ajout)
    base.add(demande)
    base.commit()
    relire_et_comparer(base, DemandeDevis, demande.id, ajout)

    modification = valeurs(DemandeDevis, 2, {**liens, "commune_id": talence.id, "code_postal": "33400", "statut": "declinee",
                                             "texte": "Terrasse de 20 m² en bois"})
    for rubrique, valeur in modification.items():
        setattr(demande, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, DemandeDevis, demande.id, modification)

    # Fiche liée : une photo de la demande
    fichiers = []
    for variante in (1, 2):
        fichier = Fichier(**valeurs(Fichier, variante, {"depose_par_id": compte.id}))
        base.add(fichier)
        base.commit()
        fichiers.append(fichier.id)
    ajout_lie = valeurs(PhotoDemande, 1, {"demande_devis_id": demande.id, "fichier_id": fichiers[0]})
    photo = PhotoDemande(**ajout_lie)
    base.add(photo)
    base.commit()
    relire_et_comparer(base, PhotoDemande, photo.id, ajout_lie)
    modification_liee = valeurs(PhotoDemande, 2, {"demande_devis_id": demande.id, "fichier_id": fichiers[1]})
    for rubrique, valeur in modification_liee.items():
        setattr(photo, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, PhotoDemande, photo.id, modification_liee)

    base.delete(base.get_one(DemandeDevis, demande.id))
    with pytest.raises(IntegrityError):
        base.commit()
    base.rollback()
    _supprimer(base, PhotoDemande, photo.id)
    for modele, identifiant in ((DemandeDevis, demande.id), (Annonce, annonce.id), (Fichier, fichiers[0]), (Fichier, fichiers[1])):
        _supprimer(base, modele, identifiant)


def test_fiche_devis_et_ligne(base: Session, decor) -> None:  # noqa: F811
    compte, prestataire, (plombier, _), (pessac, _) = decor
    annonce = _annonce(base, prestataire, plombier)
    demande = _demande(base, compte, prestataire, annonce, pessac.id)
    blocage = Blocage(prestataire_id=prestataire.id, debut=datetime(2027, 10, 14, tzinfo=UTC),
                      fin=datetime(2027, 10, 16, tzinfo=UTC), motif="Travaux D-2027-0001")
    base.add(blocage)
    base.commit()
    liens = {"demande_devis_id": demande.id}
    # Valeurs imposées : année et numéro, arrhes 0-100 %, dates dans l'ordre, statut et mode de paiement cohérents
    ajout = valeurs(Devis, 1, {**liens, "blocage_id": None, "annee": 2027, "numero": 1, "arrhes_pourcent": 30,
                               "travaux_debut": LE_14, "travaux_fin": LE_14 + timedelta(days=1), "statut": "envoye",
                               "mode_paiement": None, "accepte_le": None, "probleme": None, "probleme_le": None,
                               "moyen_direct": None})
    devis = Devis(**ajout)
    base.add(devis)
    base.commit()
    relire_et_comparer(base, Devis, devis.id, ajout)

    modification = valeurs(Devis, 2, {**liens, "blocage_id": blocage.id, "annee": 2027, "numero": 2, "arrhes_pourcent": 0,
                                      "travaux_debut": LE_14, "travaux_fin": LE_14 + timedelta(days=2), "statut": "paye",
                                      "mode_paiement": "direct", "moyen_direct": "cheque",
                                      "probleme": "Le muret penche de 5 cm"})
    for rubrique, valeur in modification.items():
        setattr(devis, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, Devis, devis.id, modification)

    # Fiche liée : une ligne du devis
    ajout_lie = valeurs(LigneDevis, 1, {"devis_id": devis.id, "libelle": "Parpaings", "quantite_centiemes": 4000,
                                        "prix_unitaire_centimes": 350, "tva_pour_mille": None})
    ligne = LigneDevis(**ajout_lie)
    base.add(ligne)
    base.commit()
    relire_et_comparer(base, LigneDevis, ligne.id, ajout_lie)
    modification_liee = valeurs(LigneDevis, 2, {"devis_id": devis.id, "libelle": "Main-d'œuvre", "quantite_centiemes": 1600,
                                                "prix_unitaire_centimes": 4500, "tva_pour_mille": 100})
    for rubrique, valeur in modification_liee.items():
        setattr(ligne, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, LigneDevis, ligne.id, modification_liee)

    base.delete(base.get_one(Devis, devis.id))
    with pytest.raises(IntegrityError):
        base.commit()
    base.rollback()
    for modele, identifiant in ((LigneDevis, ligne.id), (Devis, devis.id), (Blocage, blocage.id), (DemandeDevis, demande.id),
                                (Annonce, annonce.id)):
        _supprimer(base, modele, identifiant)
