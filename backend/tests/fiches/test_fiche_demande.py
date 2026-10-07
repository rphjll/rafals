"""Tests de fiche du lot 8.3 : demande publiée, photo d'une demande ; réponse, proposition, négociation.
Chacune : ajout → modification → suppression de la fiche principale refusée tant que la fiche liée existe → suppression."""

from datetime import timedelta

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modeles.comptes import Compte
from app.modeles.demandes import Demande, Negociation, PhotoDemandePubliee, Proposition, ReponseDemande
from app.modeles.messagerie import Conversation
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


def test_fiche_reponse_proposition_negociation(base: Session, decor) -> None:  # noqa: F811
    compte, prestataire, (plombier, electricien), (pessac, _) = decor
    client = Compte(**valeurs(Compte, 2))
    base.add(client)
    base.commit()
    demandes = []
    for variante in (1, 2):
        demande = Demande(**valeurs(Demande, variante, {
            "client_id": client.id, "metier_id": plombier.id, "commune_id": pessac.id, "cachee_par_id": None, "cachee_le": None,
            "quand": "jour_precis", "lieu": "chez_moi", "statut": "ouverte", "code_postal": "33600"}))
        base.add(demande)
        demandes.append(demande)
    conversation = Conversation(**valeurs(Conversation, 1, {
        "client_id": client.id, "prestataire_id": prestataire.id, "bloquee_par_id": None, "bloquee_le": None}))
    base.add(conversation)
    base.commit()

    # Réponse : Karim a répondu à la demande n° 1 ; à la modification, elle désigne la demande n° 2
    ajout = valeurs(ReponseDemande, 1, {"demande_id": demandes[0].id, "prestataire_id": prestataire.id, "conversation_id": conversation.id})
    reponse = ReponseDemande(**ajout)
    base.add(reponse)
    base.commit()
    relire_et_comparer(base, ReponseDemande, reponse.id, ajout)
    modification = valeurs(ReponseDemande, 2, {"demande_id": demandes[1].id, "prestataire_id": prestataire.id, "conversation_id": conversation.id})
    for rubrique, valeur in modification.items():
        setattr(reponse, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, ReponseDemande, reponse.id, modification)

    # Proposition : pour une demande, en attente ; puis sans demande, acceptée (la fin vient après le début)
    liens = {"conversation_id": conversation.id, "remplace_id": None}
    ajout_proposition = valeurs(Proposition, 1, {**liens, "demande_id": demandes[0].id, "metier_id": plombier.id,
                                                 "lieu": "chez_client", "statut": "en_attente"})
    ajout_proposition["fin"] = ajout_proposition["debut"] + timedelta(hours=1)
    proposition = Proposition(**ajout_proposition)
    base.add(proposition)
    base.commit()
    relire_et_comparer(base, Proposition, proposition.id, ajout_proposition)
    modification_proposition = valeurs(Proposition, 2, {**liens, "demande_id": None, "metier_id": electricien.id,
                                                        "lieu": "chez_moi", "statut": "acceptee", "paiement_especes": True})
    modification_proposition["fin"] = modification_proposition["debut"] + timedelta(hours=2)
    for rubrique, valeur in modification_proposition.items():
        setattr(proposition, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, Proposition, proposition.id, modification_proposition)

    # Fiche liée : une négociation, en attente (pas de date de réponse) puis acceptée
    ajout_negociation = valeurs(Negociation, 1, {"proposition_id": proposition.id, "statut": "en_attente", "repondu_le": None})
    negociation = Negociation(**ajout_negociation)
    base.add(negociation)
    base.commit()
    relire_et_comparer(base, Negociation, negociation.id, ajout_negociation)
    modification_negociation = valeurs(Negociation, 2, {"proposition_id": proposition.id, "statut": "acceptee"})
    for rubrique, valeur in modification_negociation.items():
        setattr(negociation, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, Negociation, negociation.id, modification_negociation)

    # Rien ne disparaît tant qu'une fiche liée existe : proposition → négociation, demande → réponse, conversation → proposition
    for modele, identifiant in ((Proposition, proposition.id), (Demande, demandes[1].id), (Conversation, conversation.id)):
        base.delete(base.get_one(modele, identifiant))
        with pytest.raises(IntegrityError):
            base.commit()
        base.rollback()

    for modele, identifiant in ((Negociation, negociation.id), (Proposition, proposition.id), (ReponseDemande, reponse.id),
                                (Conversation, conversation.id), (Demande, demandes[0].id), (Demande, demandes[1].id),
                                (Compte, client.id)):
        _supprimer(base, modele, identifiant)
