"""Signalements de prestataires et de conversations (RM-ADMINISTRATION.md, lot 6.3 ; validé par Raphael le 04/10/2026).
Tout utilisateur connecté peut signaler ; l'administrateur classe (rien à faire) ou agit (bloquer le prestataire,
prévenir). Celui qui signale n'est jamais nommé au prestataire. Un signalement n'est jamais effacé."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.comptes import Compte
from app.modeles.demandes import Demande
from app.modeles.messagerie import Conversation
from app.modeles.prestataires import Prestataire
from app.modeles.signalements import Signalement
from app.services import journal, mails, prestataires
from app.services.erreurs import ErreurRegle

ACTIONS = ("classer", "bloquer_prestataire", "prevenir", "cacher_demande")


def signaler(db: Session, auteur: Compte, *, prestataire_id: int | None, motif: str, maintenant: datetime) -> Signalement:
    """Ex. Mme Dupont signale le profil « Plombier pas cher » : « Photos volées sur un autre site »."""
    motif = (motif or "").strip()
    mini, maxi = reglages.SIGNALEMENT_MOTIF
    if not mini <= len(motif) <= maxi:
        raise ErreurRegle(f"Expliquez le problème en {mini} à {maxi} caractères (ex. « Prix mensonger, il demande 80 € sur place »).")
    prestataire = db.get(Prestataire, prestataire_id) if prestataire_id is not None else None
    if prestataire is None:
        raise ErreurRegle("Ce prestataire n'existe pas.", 404)
    if prestataire.compte_id == auteur.id:
        raise ErreurRegle("Vous ne pouvez pas vous signaler vous-même.")
    deja = db.scalar(select(Signalement.id).where(
        Signalement.auteur_id == auteur.id, Signalement.prestataire_id == prestataire.id,
        Signalement.conversation_id.is_(None), Signalement.statut == "a_traiter"))
    if deja is not None:
        raise ErreurRegle("Vous l'avez déjà signalé : l'administrateur va regarder.")
    signalement = Signalement(auteur_id=auteur.id, prestataire_id=prestataire.id, annonce_id=None, motif=motif,
                              cree_le=maintenant, statut="a_traiter")
    db.add(signalement)
    db.flush()
    journal.noter(db, auteur_id=auteur.id, action="signaler", table_cible="signalement", ligne_id=signalement.id,
                  apres={"prestataire_id": prestataire.id}, maintenant=maintenant)
    return signalement


def signaler_demande(db: Session, auteur: Compte, demande_id: int, motif: str, maintenant: datetime) -> Signalement:
    """Un prestataire signale une demande (fausse, hors sujet, illégale) : l'administrateur la laisse ou la cache.
    Ex. Karim signale « Travail au noir, pas de facture » : « Il demande de ne rien déclarer »."""
    motif = (motif or "").strip()
    mini, maxi = reglages.SIGNALEMENT_MOTIF
    if not mini <= len(motif) <= maxi:
        raise ErreurRegle(f"Expliquez le problème en {mini} à {maxi} caractères (ex. « Ce n'est pas une vraie demande »).")
    demande = db.get(Demande, demande_id)
    if demande is None or demande.statut != "ouverte" or demande.cachee_le is not None:
        raise ErreurRegle("Cette demande n'est plus ouverte.", 404)
    if demande.client_id == auteur.id:
        raise ErreurRegle("Vous ne pouvez pas signaler votre propre demande.")
    if db.scalar(select(Signalement.id).where(Signalement.auteur_id == auteur.id, Signalement.demande_id == demande.id,
                                              Signalement.statut == "a_traiter")) is not None:
        raise ErreurRegle("Vous l'avez déjà signalée : l'administrateur va regarder.")
    signalement = Signalement(auteur_id=auteur.id, prestataire_id=None, annonce_id=None, demande_id=demande.id, motif=motif,
                              cree_le=maintenant, statut="a_traiter")
    db.add(signalement)
    db.flush()
    journal.noter(db, auteur_id=auteur.id, action="signaler", table_cible="signalement", ligne_id=signalement.id,
                  apres={"demande_id": demande.id}, maintenant=maintenant)
    return signalement


def a_traiter(db: Session) -> list[Signalement]:
    return list(db.scalars(select(Signalement).where(Signalement.statut == "a_traiter").order_by(Signalement.cree_le)))


def traiter(db: Session, administrateur: Compte, signalement_id: int, *, action: str, decision: str,
            maintenant: datetime) -> Signalement:
    """Classer (rien à faire), ou agir : bloquer le prestataire. Le prestataire reçoit le motif de
    l'administrateur, jamais le nom de celui qui a signalé."""
    signalement = db.get(Signalement, signalement_id)
    if signalement is None:
        raise ErreurRegle("Ce signalement n'existe pas.", 404)
    if signalement.statut != "a_traiter":
        raise ErreurRegle("Ce signalement est déjà traité.")
    if action not in ACTIONS:
        raise ErreurRegle("Action inconnue.")
    decision = (decision or "").strip()
    # Conversation signalée par le prestataire : c'est le client qui est visé, il n'y a pas de prestataire à bloquer
    prestataire = db.get_one(Prestataire, signalement.prestataire_id) if signalement.prestataire_id else None
    if action == "classer":
        decision = decision or "Rien à faire"
    elif action == "cacher_demande":
        # La demande disparaît de l'accueil ; le client reçoit le motif, jamais le nom de celui qui a signalé
        if signalement.demande_id is None:
            raise ErreurRegle("Ce signalement ne porte pas sur une demande.")
        if len(decision) < 5:
            raise ErreurRegle("Écrivez le motif : il est envoyé au client (ex. « Demande contraire à la loi »).")
        demande = db.get_one(Demande, signalement.demande_id)
        if demande.cachee_le is None:
            demande.cachee_le, demande.cachee_motif, demande.cachee_par_id = maintenant, decision[:500], administrateur.id
        mails.envoyer_mail(db.get_one(Compte, demande.client_id).email, "rafals : votre demande a été cachée",
                           f"L'administrateur de rafals a caché votre demande « {demande.titre} ». Motif : « {decision} ».")
    elif action == "prevenir":
        # Avertissement par mail à la personne visée par une conversation signalée (lot 8.1)
        if signalement.conversation_id is None:
            raise ErreurRegle("Ce signalement ne porte pas sur une conversation.")
        if len(decision) < 5:
            raise ErreurRegle("Écrivez l'avertissement : il est envoyé à la personne signalée (ex. « Restez courtois »).")
        conversation = db.get_one(Conversation, signalement.conversation_id)
        vise = prestataire.compte_id if prestataire else conversation.client_id
        mails.envoyer_mail(db.get_one(Compte, vise).email, "rafals : avertissement de l'administrateur",
                           f"Une de vos conversations sur rafals a été signalée. Message de l'administrateur : « {decision} ».")
    elif prestataire is None:
        raise ErreurRegle("Ce signalement vise un client : classez-le ou prévenez-le.")
    else:
        if len(decision) < 5:
            raise ErreurRegle("Écrivez le motif : il est envoyé au prestataire (ex. « Photos volées »).")
        email = db.get_one(Compte, prestataire.compte_id).email
        prestataires.bloquer(db, administrateur, prestataire.id, bloque=True, maintenant=maintenant)
        mails.envoyer_mail(email, "rafals : votre profil est bloqué",
                           f"L'administrateur de rafals a bloqué votre profil. Motif : « {decision} ». Contactez-le pour en parler.")
    signalement.statut = "classe" if action == "classer" else "suivi"
    signalement.decision, signalement.traite_le, signalement.traite_par_id = decision[:500], maintenant, administrateur.id
    journal.noter(db, auteur_id=administrateur.id, action=f"signalement_{action}", table_cible="signalement",
                  ligne_id=signalement.id, apres={"statut": signalement.statut, "decision": signalement.decision},
                  maintenant=maintenant)
    return signalement
