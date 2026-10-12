"""Adresses de la messagerie (lot 8.1 ; écrans au lot 8.2). Règles : RM-MESSAGERIE.md."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Form, Response, UploadFile
from pydantic import BaseModel

from app.modeles.comptes import Compte
from app.modeles.fichiers import Fichier
from app.modeles.messagerie import Conversation, Message
from app.modeles.prestataires import Prestataire
from app.routes.dependances import Administrateur, Base, CompteConnecte, maintenant
from app.routes.prestataires import mon_profil_ou_404
from app.services import avis as service_avis
from app.services import avis_clients
from app.services import messagerie as service
from app.services import stockage
from app.services.erreurs import ErreurRegle

routeur = APIRouter(prefix="/api")


class Debut(BaseModel):
    """Le client envoie prestataire_id ([Écrire à Karim]) ; le prestataire envoie client_id."""

    prestataire_id: int | None = None
    client_id: int | None = None


class Motif(BaseModel):
    motif: str


class MessageVisible(BaseModel):
    id: int
    de_moi: bool
    genre: str  # « texte » ou « information » (ligne écrite par rafals)
    texte: str  # coordonnées masquées tant qu'il n'y a pas de rendez-vous entre les deux
    cree_le: datetime
    lu: bool  # mes messages : l'autre les a-t-il lus ?
    nombre_photos: int


class ConversationResumee(BaseModel):
    id: int
    cote: str  # « client » ou « prestataire » : mon côté dans cette conversation
    avec: str  # « Karim Benali » pour le client, « Marie D. » pour le prestataire
    prestataire_id: int
    client_id: int
    dernier_message_le: datetime
    apercu: str
    non_lus: int
    bloquee: bool
    avec_note: float | None = None  # la moyenne de l'autre : avis sur le client, ou avis sur le prestataire
    avec_avis: int = 0


class ConversationVisible(ConversationResumee):
    bloquee_par_moi: bool
    coordonnees_masquees: bool
    messages: list[MessageVisible]


def _texte(message: Message, masque: bool) -> str:
    return service.masquer(message.texte) if masque and message.genre == "texte" else message.texte


def _note_de_l_autre(db: Base, compte: Compte, conversation: Conversation) -> dict:
    """« Marie D. · 4,8 ★ · 6 avis » pour le prestataire ; « Karim B. · 4,7 ★ · 3 avis » pour le client."""
    if service.cote(db, compte, conversation) == "prestataire":
        note, nombre = avis_clients.note_de(db, conversation.client_id)
    else:
        somme, nombre = service_avis.notes(db, [conversation.prestataire_id]).get(conversation.prestataire_id, (0, 0))
        note = round(somme / nombre, 1) if nombre else None
    return {"avec_note": note, "avec_avis": nombre}


def _resumee(db: Base, compte: Compte, conversation: Conversation) -> ConversationResumee:
    messages = service.messages_de(db, conversation)
    dernier = messages[-1] if messages else None
    masque = not service.rendez_vous_ensemble(db, conversation)
    apercu = "" if dernier is None else (_texte(dernier, masque) or "Photo")
    return ConversationResumee(
        id=conversation.id, cote=service.cote(db, compte, conversation), avec=service.nom_de_l_autre(db, compte, conversation),
        prestataire_id=conversation.prestataire_id, client_id=conversation.client_id,
        dernier_message_le=conversation.dernier_message_le, apercu=apercu[:120],
        non_lus=service.non_lus(db, compte, conversation), bloquee=conversation.bloquee_le is not None,
        **_note_de_l_autre(db, compte, conversation),
    )


def _visible(db: Base, compte: Compte, conversation: Conversation) -> ConversationVisible:
    masque = not service.rendez_vous_ensemble(db, conversation)
    return ConversationVisible(
        **_resumee(db, compte, conversation).model_dump(),
        bloquee_par_moi=conversation.bloquee_par_id == compte.id, coordonnees_masquees=masque,
        messages=[
            MessageVisible(
                id=m.id, de_moi=m.auteur_id == compte.id and m.genre == "texte", genre=m.genre, texte=_texte(m, masque),
                cree_le=m.cree_le, lu=service.lu_par_l_autre(db, compte, conversation, m),
                nombre_photos=len(service.photos_de(db, m.id)),
            ) for m in service.messages_de(db, conversation)
        ],
    )


# ---------- Mes conversations ----------


@routeur.get("/moi/conversations")
def mes_conversations(db: Base, compte: CompteConnecte) -> list[ConversationResumee]:
    return [_resumee(db, compte, c) for c in service.mes_conversations(db, compte)]


@routeur.get("/moi/conversations/non-lues")
def non_lues(db: Base, compte: CompteConnecte) -> dict[str, int]:
    """Le compteur rouge de l'onglet « Messages »."""
    return {"nombre": service.conversations_non_lues(db, compte)}


@routeur.post("/conversations", status_code=201)
def commencer(donnees: Debut, db: Base, compte: CompteConnecte) -> ConversationVisible:
    """Le client : avec un prestataire visible. Le prestataire : seulement avec un client qui a un rendez-vous ou un
    devis avec lui (répondre à une demande : lot 8.3)."""
    if donnees.prestataire_id is not None:
        conversation = service.commencer_par_le_client(db, compte, donnees.prestataire_id, maintenant())
    elif donnees.client_id is not None:
        conversation = service.commencer_par_le_prestataire(db, mon_profil_ou_404(db, compte), donnees.client_id, maintenant())
    else:
        raise ErreurRegle("Indiquez à qui vous écrivez.")
    db.commit()
    return _visible(db, compte, conversation)


@routeur.get("/conversations/{conversation_id}")
def lire(conversation_id: int, db: Base, compte: CompteConnecte) -> ConversationVisible:
    """Ouvrir la conversation = tout lire (le compteur retombe, l'autre voit « lu »)."""
    conversation = service.conversation_ou_404(db, compte, conversation_id)
    service.marquer_lu(db, compte, conversation, maintenant())
    db.commit()
    return _visible(db, compte, conversation)


@routeur.post("/conversations/{conversation_id}/messages", status_code=201)
async def ecrire(conversation_id: int, db: Base, compte: CompteConnecte, texte: Annotated[str, Form()] = "",
                 photos: list[UploadFile] | None = None) -> ConversationVisible:
    """Un formulaire (pas du JSON) : « texte » et jusqu'à 5 fichiers « photos »."""
    conversation = service.conversation_ou_404(db, compte, conversation_id)
    jointes = [service.Photo(nom_fichier=p.filename or "photo", type_mime=p.content_type or "", contenu=await p.read())
               for p in photos or []]
    service.envoyer(db, compte, conversation, texte, jointes, maintenant())
    db.commit()
    return _visible(db, compte, conversation)


@routeur.get("/messages/{message_id}/photos/{ordre}")
def voir_photo(message_id: int, ordre: int, db: Base, compte: CompteConnecte) -> Response:
    """Seulement pour les deux personnes de la conversation."""
    message = db.get(Message, message_id)
    if message is None:
        raise ErreurRegle("Cette photo n'existe pas.", 404)
    service.conversation_ou_404(db, compte, message.conversation_id)
    photo = next((p for p in service.photos_de(db, message.id) if p.ordre == ordre), None)
    if photo is None:
        raise ErreurRegle("Cette photo n'existe pas.", 404)
    fichier = db.get_one(Fichier, photo.fichier_id)
    return Response(content=stockage.lire(fichier.cle_stockage), media_type=fichier.type_mime)


@routeur.post("/conversations/{conversation_id}/bloquer")
def bloquer(conversation_id: int, db: Base, compte: CompteConnecte) -> ConversationVisible:
    conversation = service.conversation_ou_404(db, compte, conversation_id)
    service.bloquer(db, compte, conversation, maintenant())
    db.commit()
    return _visible(db, compte, conversation)


@routeur.post("/conversations/{conversation_id}/debloquer")
def debloquer(conversation_id: int, db: Base, compte: CompteConnecte) -> ConversationVisible:
    conversation = service.conversation_ou_404(db, compte, conversation_id)
    service.debloquer(db, compte, conversation, maintenant())
    db.commit()
    return _visible(db, compte, conversation)


@routeur.post("/conversations/{conversation_id}/signaler", status_code=201)
def signaler(conversation_id: int, donnees: Motif, db: Base, compte: CompteConnecte) -> dict[str, int]:
    conversation = service.conversation_ou_404(db, compte, conversation_id)
    signalement = service.signaler(db, compte, conversation, donnees.motif, maintenant())
    db.commit()
    return {"id": signalement.id}


# ---------- Administrateur : seulement une conversation signalée ----------


class MessageAdministre(BaseModel):
    auteur: str
    genre: str
    texte: str
    cree_le: datetime


class ConversationAdministree(BaseModel):
    id: int
    client: str
    prestataire: str
    messages: list[MessageAdministre]


@routeur.get("/admin/conversations/{conversation_id}")
def lire_signalee(conversation_id: int, db: Base, _admin: Administrateur) -> ConversationAdministree:
    """Le fil entier, en clair, pour juger un signalement. Refusé (404) si la conversation n'a pas été signalée."""
    conversation = service.conversation_signalee(db, conversation_id)
    client, prestataire = db.get_one(Compte, conversation.client_id), db.get_one(Prestataire, conversation.prestataire_id)
    noms = {client.id: f"{client.prenom} {client.nom}", prestataire.compte_id: prestataire.nom_affiche}
    return ConversationAdministree(
        id=conversation.id, client=noms[client.id], prestataire=prestataire.nom_affiche,
        messages=[MessageAdministre(auteur="rafals" if m.genre == "information" else noms.get(m.auteur_id, "?"),
                                    genre=m.genre, texte=m.texte, cree_le=m.cree_le)
                  for m in service.messages_de(db, conversation)],
    )
