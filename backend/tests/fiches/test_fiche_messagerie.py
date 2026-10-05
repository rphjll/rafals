"""Tests de fiche du lot 8.1 : conversation, message, photo d'un message.
Chacune : ajout → modification → suppression de la fiche principale refusée tant que la fiche liée existe → suppression."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modeles.comptes import Compte
from app.modeles.fichiers import Fichier
from app.modeles.messagerie import Conversation, Message, PhotoMessage
from tests.fiches.outils import relire_et_comparer, valeurs
from tests.fiches.test_fiche_annonce import _supprimer, decor  # noqa: F401 (le décor est une fixture)


def test_fiche_conversation_message_photo(base: Session, decor) -> None:  # noqa: F811
    compte, prestataire, _, _ = decor
    client = Compte(**valeurs(Compte, 2))
    base.add(client)
    base.commit()

    # Conversation : pas bloquée à l'ajout, bloquée par le client à la modification (date et auteur vont ensemble)
    ajout = valeurs(Conversation, 1, {"client_id": client.id, "prestataire_id": prestataire.id, "bloquee_par_id": None, "bloquee_le": None})
    conversation = Conversation(**ajout)
    base.add(conversation)
    base.commit()
    relire_et_comparer(base, Conversation, conversation.id, ajout)
    modification = valeurs(Conversation, 2, {"client_id": client.id, "prestataire_id": prestataire.id, "bloquee_par_id": client.id})
    for rubrique, valeur in modification.items():
        setattr(conversation, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, Conversation, conversation.id, modification)

    # Fiche liée : un message
    ajout_message = valeurs(Message, 1, {"conversation_id": conversation.id, "auteur_id": client.id, "genre": "texte"})
    message = Message(**ajout_message)
    base.add(message)
    base.commit()
    relire_et_comparer(base, Message, message.id, ajout_message)
    modification_message = valeurs(Message, 2, {"conversation_id": conversation.id, "auteur_id": compte.id, "genre": "information"})
    for rubrique, valeur in modification_message.items():
        setattr(message, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, Message, message.id, modification_message)

    # Fiche liée au message : une photo
    fichiers = []
    for variante in (1, 2):
        fichier = Fichier(**valeurs(Fichier, variante, {"depose_par_id": client.id}))
        base.add(fichier)
        base.commit()
        fichiers.append(fichier.id)
    ajout_photo = valeurs(PhotoMessage, 1, {"message_id": message.id, "fichier_id": fichiers[0]})
    photo = PhotoMessage(**ajout_photo)
    base.add(photo)
    base.commit()
    relire_et_comparer(base, PhotoMessage, photo.id, ajout_photo)
    modification_photo = valeurs(PhotoMessage, 2, {"message_id": message.id, "fichier_id": fichiers[1]})
    for rubrique, valeur in modification_photo.items():
        setattr(photo, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, PhotoMessage, photo.id, modification_photo)

    # Rien ne disparaît tant qu'une fiche liée existe : message → photo, conversation → message
    for principale in (base.get_one(Message, message.id), base.get_one(Conversation, conversation.id)):
        base.delete(principale)
        with pytest.raises(IntegrityError):
            base.commit()
        base.rollback()

    for modele, identifiant in ((PhotoMessage, photo.id), (Message, message.id), (Conversation, conversation.id),
                                (Fichier, fichiers[0]), (Fichier, fichiers[1]), (Compte, client.id)):
        _supprimer(base, modele, identifiant)
