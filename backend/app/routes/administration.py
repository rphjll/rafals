"""Adresses de l'administration des comptes (écran Administration au lot 1.4)."""

from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import select

from app.modeles.comptes import Compte
from app.routes.dependances import Administrateur, Base, maintenant
from app.services import administration as service

routeur = APIRouter(prefix="/api/admin")


class CompteAdministre(BaseModel):
    id: int
    email: str
    prenom: str
    nom: str
    email_verifie: bool
    est_administrateur: bool
    cree_le: datetime


class Role(BaseModel):
    est_administrateur: bool


def visible(compte: Compte) -> CompteAdministre:
    return CompteAdministre(
        id=compte.id,
        email=compte.email,
        prenom=compte.prenom,
        nom=compte.nom,
        email_verifie=compte.email_verifie_le is not None,
        est_administrateur=compte.est_administrateur,
        cree_le=compte.cree_le,
    )


@routeur.get("/comptes")
def comptes(db: Base, _admin: Administrateur) -> list[CompteAdministre]:
    return [visible(c) for c in db.scalars(select(Compte).order_by(Compte.nom, Compte.prenom))]


@routeur.post("/comptes/{compte_id}/administrateur")
def changer_role(compte_id: int, role: Role, db: Base, admin: Administrateur) -> CompteAdministre:
    compte = service.changer_role_administrateur(
        db, admin, compte_id, est_administrateur=role.est_administrateur, maintenant=maintenant()
    )
    db.commit()
    return visible(compte)
