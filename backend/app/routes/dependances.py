"""Ce que toutes les routes partagent : la base, l'heure, la personne connectée, le contrôle du rôle."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import Cookie, Depends
from sqlalchemy.orm import Session

from app import reglages
from app.db import ouvrir_base
from app.modeles.comptes import Compte
from app.services import comptes as service_comptes
from app.services.erreurs import ErreurRegle

Base = Annotated[Session, Depends(ouvrir_base)]
CookieSession = Annotated[str | None, Cookie(alias=reglages.NOM_COOKIE_SESSION)]


def maintenant() -> datetime:
    return datetime.now(UTC)


def compte_requis(db: Base, jeton: CookieSession = None) -> Compte:
    """Toute route qui en dépend refuse (401) une personne non connectée."""
    compte = service_comptes.compte_connecte(db, jeton, maintenant())
    if compte is None:
        raise ErreurRegle("Vous n'êtes pas connecté.", 401)
    return compte


def administrateur_requis(compte: Annotated[Compte, Depends(compte_requis)]) -> Compte:
    """Toute route qui en dépend refuse (403) une personne qui n'est pas administrateur."""
    if not compte.est_administrateur:
        raise ErreurRegle("Réservé aux administrateurs de rafals.", 403)
    return compte


CompteConnecte = Annotated[Compte, Depends(compte_requis)]
Administrateur = Annotated[Compte, Depends(administrateur_requis)]
