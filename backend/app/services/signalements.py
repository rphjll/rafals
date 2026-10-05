"""Signalements d'annonces et de prestataires (RM-ADMINISTRATION.md, lot 6.3 ; validé par Raphael le 04/10/2026).
Tout utilisateur connecté peut signaler ; l'administrateur classe (rien à faire) ou agit (retirer l'annonce, bloquer
le prestataire). Celui qui signale n'est jamais nommé au prestataire. Un signalement n'est jamais effacé."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.annonces import Annonce
from app.modeles.comptes import Compte
from app.modeles.messagerie import Conversation
from app.modeles.prestataires import Prestataire
from app.modeles.signalements import Signalement
from app.services import annonces, journal, mails, prestataires
from app.services.erreurs import ErreurRegle

ACTIONS = ("classer", "retirer_annonce", "bloquer_prestataire", "prevenir")


def signaler(db: Session, auteur: Compte, *, annonce_id: int | None, prestataire_id: int | None, motif: str,
             maintenant: datetime) -> Signalement:
    """Ex. Paul signale l'annonce « Plomberie — 5 € » : « Prix mensonger, il demande 80 € sur place »."""
    motif = (motif or "").strip()
    mini, maxi = reglages.SIGNALEMENT_MOTIF
    if not mini <= len(motif) <= maxi:
        raise ErreurRegle(f"Expliquez le problème en {mini} à {maxi} caractères (ex. « Prix mensonger, il demande 80 € sur place »).")
    annonce = None
    if annonce_id is not None:
        annonce = db.get(Annonce, annonce_id)
        if annonce is None:
            raise ErreurRegle("Cette annonce n'existe pas.", 404)
        prestataire_id = annonce.prestataire_id
    prestataire = db.get(Prestataire, prestataire_id) if prestataire_id is not None else None
    if prestataire is None:
        raise ErreurRegle("Ce prestataire n'existe pas.", 404)
    if prestataire.compte_id == auteur.id:
        raise ErreurRegle("Vous ne pouvez pas vous signaler vous-même.")
    deja = db.scalar(select(Signalement.id).where(
        Signalement.auteur_id == auteur.id, Signalement.prestataire_id == prestataire.id,
        Signalement.annonce_id.is_(None) if annonce is None else Signalement.annonce_id == annonce.id,
        Signalement.statut == "a_traiter"))
    if deja is not None:
        raise ErreurRegle("Vous l'avez déjà signalé : l'administrateur va regarder.")
    signalement = Signalement(auteur_id=auteur.id, prestataire_id=prestataire.id, annonce_id=annonce.id if annonce else None,
                              motif=motif, cree_le=maintenant, statut="a_traiter")
    db.add(signalement)
    db.flush()
    journal.noter(db, auteur_id=auteur.id, action="signaler", table_cible="signalement", ligne_id=signalement.id,
                  apres={"prestataire_id": prestataire.id, "annonce_id": signalement.annonce_id}, maintenant=maintenant)
    return signalement


def a_traiter(db: Session) -> list[Signalement]:
    return list(db.scalars(select(Signalement).where(Signalement.statut == "a_traiter").order_by(Signalement.cree_le)))


def traiter(db: Session, administrateur: Compte, signalement_id: int, *, action: str, decision: str,
            maintenant: datetime) -> Signalement:
    """Classer (rien à faire), ou agir : retirer l'annonce, bloquer le prestataire. Le prestataire reçoit le motif de
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
            raise ErreurRegle("Écrivez le motif : il est envoyé au prestataire (ex. « Prix mensonger »).")
        email = db.get_one(Compte, prestataire.compte_id).email
        if action == "retirer_annonce":
            if signalement.annonce_id is None:
                raise ErreurRegle("Ce signalement ne porte pas sur une annonce.")
            annonce = db.get_one(Annonce, signalement.annonce_id)
            if annonce.statut != "retiree":
                annonces.retirer_par_administrateur(db, administrateur, annonce, maintenant)
            mails.envoyer_mail(email, "rafals : une de vos annonces a été retirée",
                               f"L'administrateur de rafals a retiré votre annonce « {annonce.titre} ». Motif : « {decision} ».")
        else:
            prestataires.bloquer(db, administrateur, prestataire.id, bloque=True, maintenant=maintenant)
            mails.envoyer_mail(email, "rafals : votre profil est bloqué",
                               f"L'administrateur de rafals a bloqué votre profil. Motif : « {decision} ». Contactez-le pour en parler.")
    signalement.statut = "classe" if action == "classer" else "suivi"
    signalement.decision, signalement.traite_le, signalement.traite_par_id = decision[:500], maintenant, administrateur.id
    journal.noter(db, auteur_id=administrateur.id, action=f"signalement_{action}", table_cible="signalement",
                  ligne_id=signalement.id, apres={"statut": signalement.statut, "decision": signalement.decision},
                  maintenant=maintenant)
    return signalement
