"""Messagerie : une conversation par couple client / prestataire, messages, photos, coordonnées masquées avant le
premier rendez-vous, lu / non lu, mail après 15 minutes, bloquer, signaler, effacement après 3 ans.
Règles : .doc/regles-metier/RM-MESSAGERIE.md (validé par Raphael le 04/10/2026).
Les messages ne sont lus que par les deux personnes ; l'administrateur ne lit qu'une conversation signalée."""

import re
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import delete, exists, func, or_, select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.comptes import Compte
from app.modeles.demandes import Proposition, ReponseDemande
from app.modeles.devis import DemandeDevis
from app.modeles.messagerie import Conversation, Message, PhotoMessage
from app.modeles.prestataires import Prestataire
from app.modeles.rendez_vous import RendezVous
from app.modeles.signalements import Signalement
from app.services import avis, fichiers, journal, mails
from app.services.erreurs import ErreurRegle

# Un numéro de téléphone français (« 06 12 34 56 78 », « +33 6 12 34 56 78 », « 0612345678 ») ou une adresse mail
COORDONNEES = re.compile(r"(?:\+33|0033|0)[\s.\-]?[1-9](?:[\s.\-]?\d{2}){4}|[\w.+\-]+@[\w\-]+(?:\.[\w\-]+)+")
MASQUE = "(coordonnées masquées jusqu'à la réservation)"
PARTI = "Personne ayant quitté rafals"


@dataclass
class Photo:
    nom_fichier: str
    type_mime: str
    contenu: bytes


# ---------- Qui est qui ----------


def cote(db: Session, compte: Compte, conversation: Conversation) -> str:
    """« client » ou « prestataire » : de quel côté de la conversation est cette personne. 404 si elle n'y est pas."""
    if conversation.client_id == compte.id:
        return "client"
    if db.get_one(Prestataire, conversation.prestataire_id).compte_id == compte.id:
        return "prestataire"
    raise ErreurRegle("Cette conversation n'existe pas.", 404)


def conversation_ou_404(db: Session, compte: Compte, conversation_id: int) -> Conversation:
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise ErreurRegle("Cette conversation n'existe pas.", 404)
    cote(db, compte, conversation)
    return conversation


def nom_du_client(client: Compte) -> str:
    """« Marie D. » : jamais le nom complet avant un rendez-vous ; compte fermé : « Personne ayant quitté rafals »."""
    if client.ferme_le is not None:
        return PARTI
    initiale = client.nom.strip()[:1].upper()
    return f"{client.prenom} {initiale}." if initiale else client.prenom


def nom_de_l_autre(db: Session, compte: Compte, conversation: Conversation) -> str:
    """Le client voit le nom affiché du prestataire ; le prestataire voit « Marie D. »."""
    prestataire = db.get_one(Prestataire, conversation.prestataire_id)
    if cote(db, compte, conversation) == "prestataire":
        return nom_du_client(db.get_one(Compte, conversation.client_id))
    return PARTI if db.get_one(Compte, prestataire.compte_id).ferme_le is not None else prestataire.nom_affiche


def rendez_vous_ensemble(db: Session, conversation: Conversation) -> bool:
    """Ont-ils (eu) un rendez-vous confirmé ensemble ? Tant que non, les coordonnées sont masquées dans les messages."""
    return bool(db.scalar(select(exists().where(
        RendezVous.client_id == conversation.client_id, RendezVous.prestataire_id == conversation.prestataire_id,
        RendezVous.statut == "confirme",
    ))))


def masquer(texte: str) -> str:
    """« appelez-moi au 06 12 34 56 78 » → « appelez-moi au (coordonnées masquées jusqu'à la réservation) »."""
    return COORDONNEES.sub(MASQUE, texte)


# ---------- Commencer une conversation ----------


def _conversation(db: Session, client_id: int, prestataire_id: int) -> Conversation | None:
    return db.scalar(select(Conversation).where(
        Conversation.client_id == client_id, Conversation.prestataire_id == prestataire_id))


def creer(db: Session, client_id: int, prestataire: Prestataire, maintenant: datetime) -> Conversation:
    """La conversation de ce couple (créée si elle n'existe pas). Sans contrôle de droit : c'est à l'appelant de vérifier
    qui a le droit de commencer (voir commencer_par_le_client, commencer_par_le_prestataire ; lot 8.3 : répondre à une
    demande)."""
    if prestataire.compte_id == client_id:
        raise ErreurRegle("Vous ne pouvez pas vous écrire à vous-même.")
    conversation = _conversation(db, client_id, prestataire.id)
    if conversation is None:
        conversation = Conversation(client_id=client_id, prestataire_id=prestataire.id, cree_le=maintenant,
                                    dernier_message_le=maintenant)
        db.add(conversation)
        db.flush()
    return conversation


def commencer_par_le_client(db: Session, client: Compte, prestataire_id: int, maintenant: datetime) -> Conversation:
    """[Écrire à Karim] sur sa page publique : avec n'importe quel prestataire visible."""
    prestataire = db.get(Prestataire, prestataire_id)
    if prestataire is None:
        raise ErreurRegle("Ce prestataire n'existe pas.", 404)
    existante = _conversation(db, client.id, prestataire.id)
    if existante is None and prestataire.statut != "actif":
        raise ErreurRegle("Ce prestataire n'est pas joignable en ce moment.")
    return existante or creer(db, client.id, prestataire, maintenant)


def commencer_par_le_prestataire(db: Session, prestataire: Prestataire, client_id: int, maintenant: datetime) -> Conversation:
    """Un prestataire n'écrit en premier qu'à un client qui a déjà un rendez-vous ou une demande de devis avec lui
    (répondre à une demande publiée : lot 8.3). Ex. refusé : Karim écrit à tous les clients de Pessac."""
    existante = _conversation(db, client_id, prestataire.id)
    if existante is not None:
        return existante
    client = db.get(Compte, client_id)
    lie = client is not None and client.ferme_le is None and (
        db.scalar(select(exists().where(RendezVous.client_id == client_id, RendezVous.prestataire_id == prestataire.id)))
        or db.scalar(select(exists().where(DemandeDevis.client_id == client_id, DemandeDevis.prestataire_id == prestataire.id)))
    )
    if not lie:
        raise ErreurRegle("Vous pouvez écrire à un client seulement s'il a un rendez-vous ou un devis avec vous, "
                          "ou pour répondre à sa demande.", 403)
    return creer(db, client_id, prestataire, maintenant)


# ---------- Écrire ----------


def _verifier_ouverte(db: Session, conversation: Conversation) -> None:
    if conversation.bloquee_le is not None:
        raise ErreurRegle("Cette conversation est bloquée : plus aucun message ne passe.")
    prestataire = db.get_one(Prestataire, conversation.prestataire_id)
    if any(db.get_one(Compte, c).ferme_le is not None for c in (conversation.client_id, prestataire.compte_id)):
        raise ErreurRegle("Cette personne a quitté rafals : on ne peut plus lui écrire.")


def envoyer(db: Session, compte: Compte, conversation: Conversation, texte: str, photos: list[Photo],
            maintenant: datetime) -> Message:
    """Un texte de 1 à 2000 caractères, ou des photos (5 au plus), ou les deux. Même filtre que les avis.
    Ex. Karim : « Bonjour, la fuite vient du siphon ou du robinet ? »"""
    cote(db, compte, conversation)
    _verifier_ouverte(db, conversation)
    texte = (texte or "").strip()
    if not texte and not photos:
        raise ErreurRegle("Écrivez un message.")
    if len(photos) > reglages.MESSAGE_PHOTOS_MAX:
        raise ErreurRegle(f"Au plus {reglages.MESSAGE_PHOTOS_MAX} photos par message.")
    if texte:
        texte = avis.verifier_texte(db, texte, 1, "Votre message", reglages.MESSAGE_TEXTE_MAX)
    for photo in photos:
        fichiers.verifier(photo.contenu, photo.type_mime, types_acceptes=reglages.PHOTO_TYPES_ACCEPTES,
                          taille_max_octets=reglages.PHOTO_TAILLE_MAX_OCTETS)
    message = Message(conversation_id=conversation.id, auteur_id=compte.id, texte=texte, genre="texte", cree_le=maintenant)
    db.add(message)
    db.flush()
    for ordre, photo in enumerate(photos, start=1):
        fichier = fichiers.enregistrer(db, compte, nom_fichier=photo.nom_fichier, type_mime=photo.type_mime,
                                       contenu=photo.contenu, maintenant=maintenant)
        db.add(PhotoMessage(message_id=message.id, fichier_id=fichier.id, ordre=ordre))
    conversation.dernier_message_le = maintenant
    _marquer_lu(db, compte, conversation, maintenant)  # celui qui écrit a forcément lu ce qui précède
    db.flush()
    return message


def informer(db: Session, conversation: Conversation, auteur_id: int, texte: str, maintenant: datetime) -> Message:
    """Une ligne écrite par rafals dans le fil (ex. « Marie D. a refusé la proposition de 35 € »), sans filtre."""
    message = Message(conversation_id=conversation.id, auteur_id=auteur_id, texte=texte[:reglages.MESSAGE_TEXTE_MAX],
                      genre="information", cree_le=maintenant)
    db.add(message)
    conversation.dernier_message_le = maintenant
    db.flush()
    return message


# ---------- Lire ----------


def _lu_le(conversation: Conversation, de_quel_cote: str) -> datetime | None:
    return conversation.client_lu_le if de_quel_cote == "client" else conversation.prestataire_lu_le


def _marquer_lu(db: Session, compte: Compte, conversation: Conversation, maintenant: datetime) -> None:
    if cote(db, compte, conversation) == "client":
        conversation.client_lu_le = maintenant
    else:
        conversation.prestataire_lu_le = maintenant


def marquer_lu(db: Session, compte: Compte, conversation: Conversation, maintenant: datetime) -> None:
    """Ouvrir la conversation = tout lire : le compteur rouge retombe, l'autre voit « lu »."""
    _marquer_lu(db, compte, conversation, maintenant)


def messages_de(db: Session, conversation: Conversation) -> list[Message]:
    return list(db.scalars(select(Message).where(Message.conversation_id == conversation.id).order_by(Message.cree_le, Message.id)))


def photos_de(db: Session, message_id: int) -> list[PhotoMessage]:
    return list(db.scalars(select(PhotoMessage).where(PhotoMessage.message_id == message_id).order_by(PhotoMessage.ordre)))


def non_lus(db: Session, compte: Compte, conversation: Conversation) -> int:
    """Messages de l'autre arrivés depuis ma dernière lecture."""
    lu_le = _lu_le(conversation, cote(db, compte, conversation))
    return db.scalar(select(func.count()).select_from(Message).where(
        Message.conversation_id == conversation.id, Message.auteur_id != compte.id,
        *([Message.cree_le > lu_le] if lu_le else []),
    )) or 0


def lu_par_l_autre(db: Session, compte: Compte, conversation: Conversation, message: Message) -> bool:
    autre = "prestataire" if cote(db, compte, conversation) == "client" else "client"
    lu_le = _lu_le(conversation, autre)
    return lu_le is not None and lu_le >= message.cree_le


def mes_conversations(db: Session, compte: Compte) -> list[Conversation]:
    """Toutes mes conversations (comme client et comme prestataire), la plus récente d'abord."""
    miens = select(Prestataire.id).where(Prestataire.compte_id == compte.id)
    return list(db.scalars(select(Conversation).where(
        or_(Conversation.client_id == compte.id, Conversation.prestataire_id.in_(miens))
    ).order_by(Conversation.dernier_message_le.desc())))


def conversations_non_lues(db: Session, compte: Compte) -> int:
    """Le compteur rouge de l'onglet « Messages » : nombre de conversations avec du nouveau."""
    return sum(1 for c in mes_conversations(db, compte) if non_lus(db, compte, c))


# ---------- Bloquer, signaler ----------


def bloquer(db: Session, compte: Compte, conversation: Conversation, maintenant: datetime) -> None:
    """Plus aucun message ne passe, dans les deux sens ; les rendez-vous déjà pris restent."""
    cote(db, compte, conversation)
    if conversation.bloquee_le is not None:
        raise ErreurRegle("Cette conversation est déjà bloquée.")
    conversation.bloquee_le, conversation.bloquee_par_id = maintenant, compte.id
    journal.noter(db, auteur_id=compte.id, action="bloquer_conversation", table_cible="conversation",
                  ligne_id=conversation.id, maintenant=maintenant)


def debloquer(db: Session, compte: Compte, conversation: Conversation, maintenant: datetime) -> None:
    """Seul celui qui a bloqué peut débloquer."""
    cote(db, compte, conversation)
    if conversation.bloquee_par_id != compte.id:
        raise ErreurRegle("Seule la personne qui a bloqué la conversation peut la débloquer.", 403)
    conversation.bloquee_le, conversation.bloquee_par_id = None, None
    journal.noter(db, auteur_id=compte.id, action="debloquer_conversation", table_cible="conversation",
                  ligne_id=conversation.id, maintenant=maintenant)


def signaler(db: Session, compte: Compte, conversation: Conversation, motif: str, maintenant: datetime) -> Signalement:
    """Ex. Mme Dupont : « Il insiste pour être payé avant de venir ». L'administrateur a alors le droit de lire le fil.
    Le client qui signale vise le prestataire ; le prestataire qui signale vise le client (pas de prestataire visé)."""
    de_quel_cote = cote(db, compte, conversation)
    motif = (motif or "").strip()
    mini, maxi = reglages.SIGNALEMENT_MOTIF
    if not mini <= len(motif) <= maxi:
        raise ErreurRegle(f"Expliquez le problème en {mini} à {maxi} caractères (ex. « Il insiste pour être payé avant de venir »).")
    if db.scalar(select(Signalement.id).where(Signalement.auteur_id == compte.id, Signalement.conversation_id == conversation.id,
                                              Signalement.statut == "a_traiter")) is not None:
        raise ErreurRegle("Vous l'avez déjà signalée : l'administrateur va regarder.")
    signalement = Signalement(
        auteur_id=compte.id, conversation_id=conversation.id, motif=motif, cree_le=maintenant, statut="a_traiter",
        prestataire_id=conversation.prestataire_id if de_quel_cote == "client" else None,
    )
    db.add(signalement)
    db.flush()
    journal.noter(db, auteur_id=compte.id, action="signaler", table_cible="signalement", ligne_id=signalement.id,
                  apres={"conversation_id": conversation.id}, maintenant=maintenant)
    return signalement


def conversation_signalee(db: Session, conversation_id: int) -> Conversation:
    """Pour l'administrateur : seulement une conversation qui a été signalée (404 sinon)."""
    conversation = db.get(Conversation, conversation_id)
    signalee = conversation is not None and db.scalar(
        select(exists().where(Signalement.conversation_id == conversation_id)))
    if not signalee:
        raise ErreurRegle("Cette conversation n'a pas été signalée : elle ne peut pas être lue.", 404)
    return conversation


# ---------- Tâches de fond ----------


def prevenir_par_mail(db: Session, maintenant: datetime) -> int:
    """Message pas lu au bout de 15 minutes → un mail « Karim vous a écrit sur rafals » (sans recopier le message),
    au plus un mail par conversation et par heure. Rend le nombre de mails envoyés."""
    en_attente = db.scalars(select(Message).where(
        Message.genre == "texte", Message.mail_envoye_le.is_(None), Message.cree_le <= maintenant - reglages.MESSAGE_MAIL_APRES,
        Message.cree_le > maintenant - reglages.MESSAGE_MAIL_AU_PLUS_TARD,
    ).order_by(Message.cree_le)).all()
    groupes: dict[tuple[int, int], list[Message]] = {}
    for message in en_attente:
        groupes.setdefault((message.conversation_id, message.auteur_id), []).append(message)
    envoyes = 0
    for (conversation_id, auteur_id), messages in groupes.items():
        conversation = db.get_one(Conversation, conversation_id)
        prestataire = db.get_one(Prestataire, conversation.prestataire_id)
        ecrit_par_le_client = auteur_id == conversation.client_id
        destinataire = db.get_one(Compte, prestataire.compte_id if ecrit_par_le_client else conversation.client_id)
        lu_le = conversation.prestataire_lu_le if ecrit_par_le_client else conversation.client_lu_le
        pas_lus = [m for m in messages if lu_le is None or lu_le < m.cree_le]
        if not pas_lus or conversation.bloquee_le is not None or destinataire.ferme_le is not None:
            continue
        mail_recent = db.scalar(select(exists().where(
            Message.conversation_id == conversation_id, Message.auteur_id == auteur_id,
            Message.mail_envoye_le > maintenant - reglages.MESSAGE_MAIL_ECART,
        )))
        if mail_recent:
            continue  # déjà un mail il y a moins d'une heure : on réessaiera plus tard si c'est toujours pas lu
        auteur = nom_du_client(db.get_one(Compte, conversation.client_id)) if ecrit_par_le_client else prestataire.nom_affiche
        mails.envoyer_mail(destinataire.email, f"rafals : {auteur} vous a écrit",
                           f"{auteur} vous a écrit sur rafals. Pour lire son message et répondre : rubrique « Messages ».")
        for message in pas_lus:  # un seul mail pour tous les messages en attente de cette conversation
            message.mail_envoye_le = maintenant
        envoyes += 1
    return envoyes


def effacer_les_anciennes(db: Session, maintenant: datetime) -> int:
    """Une conversation sans message depuis 3 ans est effacée (données personnelles) ; une conversation signalée
    reste (le signalement n'est jamais effacé). Si elle porte une proposition ou une réponse à une demande (jamais
    effacées : un rendez-vous peut en venir), seuls ses messages et leurs photos sont effacés, la conversation reste
    vide. Rend le nombre de conversations effacées ou vidées."""
    anciennes = db.scalars(select(Conversation).where(
        Conversation.dernier_message_le < maintenant - reglages.MESSAGE_CONSERVATION,
        ~exists().where(Signalement.conversation_id == Conversation.id),
    )).all()
    traitees = 0
    for conversation in anciennes:
        a_garder = db.scalar(select(exists().where(Proposition.conversation_id == conversation.id))) or db.scalar(
            select(exists().where(ReponseDemande.conversation_id == conversation.id)))
        ids = select(Message.id).where(Message.conversation_id == conversation.id)
        if a_garder and db.scalar(select(func.count()).select_from(Message).where(Message.conversation_id == conversation.id)) == 0:
            continue  # déjà vidée lors d'un passage précédent
        db.execute(delete(PhotoMessage).where(PhotoMessage.message_id.in_(ids)))
        db.execute(delete(Message).where(Message.conversation_id == conversation.id))
        if not a_garder:
            db.delete(conversation)
        traitees += 1
    db.flush()
    return traitees


def traiter(db: Session, maintenant: datetime) -> tuple[int, int]:
    """La tâche de fond : (mails envoyés, conversations effacées)."""
    return prevenir_par_mail(db, maintenant), effacer_les_anciennes(db, maintenant)
