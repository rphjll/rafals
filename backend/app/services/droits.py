"""Qui a le droit de faire quoi. Règles : RM-COMPTES.md (inscription, âge minimum)."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.comptes import Compte
from app.modeles.fichiers import AccordParental
from app.services.comptes import age_le


def accord_parental_necessaire(compte: Compte, maintenant: datetime) -> bool:
    """Vrai pour un compte de 16 ou 17 ans (entre l'âge minimum et la majorité). Compte fermé (date effacée) : faux."""
    if compte.date_naissance is None:
        return False
    return age_le(compte.date_naissance, maintenant.date()) < reglages.AGE_MAJORITE


def accord_parental_accepte(db: Session, compte: Compte) -> bool:
    return (
        db.scalar(
            select(AccordParental.id).where(AccordParental.compte_id == compte.id, AccordParental.statut == "accepte")
        )
        is not None
    )


def peut_reserver_ou_publier(db: Session, compte: Compte, maintenant: datetime) -> bool:
    """Adresse vérifiée ET (18 ans ou plus, OU accord des parents accepté).
    Ex. Lucas, 16 ans, adresse vérifiée, accord en attente → non ; accord accepté → oui."""
    if compte.email_verifie_le is None:
        return False
    return not accord_parental_necessaire(compte, maintenant) or accord_parental_accepte(db, compte)
