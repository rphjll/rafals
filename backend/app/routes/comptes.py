"""Adresses des comptes et de la connexion (appelées par les écrans du lot 1.2)."""

from datetime import UTC, date, datetime
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import config, reglages
from app.db import ouvrir_base
from app.modeles.comptes import Compte
from app.services import comptes as service
from app.services.erreurs import ErreurRegle

routeur = APIRouter(prefix="/api")

Base = Annotated[Session, Depends(ouvrir_base)]
CookieSession = Annotated[str | None, Cookie(alias=reglages.NOM_COOKIE_SESSION)]


def maintenant() -> datetime:
    return datetime.now(UTC)


class Inscription(BaseModel):
    email: str
    mot_de_passe: str
    prenom: str
    nom: str
    telephone: str
    date_naissance: date


class Connexion(BaseModel):
    email: str
    mot_de_passe: str


class AdresseMail(BaseModel):
    email: str


class Jeton(BaseModel):
    jeton: str


class NouveauMotDePasse(BaseModel):
    jeton: str
    mot_de_passe: str


class CompteVisible(BaseModel):
    id: int
    email: str
    prenom: str
    nom: str
    email_verifie: bool

    @classmethod
    def depuis(cls, compte: Compte) -> "CompteVisible":
        return cls(
            id=compte.id,
            email=compte.email,
            prenom=compte.prenom,
            nom=compte.nom,
            email_verifie=compte.email_verifie_le is not None,
        )


class Message(BaseModel):
    message: str


@routeur.post("/comptes", status_code=201)
def inscription(donnees: Inscription, db: Base) -> CompteVisible:
    compte = service.inscrire(db, **donnees.model_dump(), maintenant=maintenant())
    db.commit()
    return CompteVisible.depuis(compte)


@routeur.post("/comptes/verification")
def verification(donnees: Jeton, db: Base) -> Message:
    service.verifier_adresse(db, donnees.jeton, maintenant())
    db.commit()
    return Message(message="Votre adresse mail est vérifiée.")


@routeur.post("/comptes/verification/renvoi")
def renvoi_verification(donnees: AdresseMail, db: Base) -> Message:
    service.renvoyer_lien_verification(db, donnees.email, maintenant())
    db.commit()
    return Message(message="Si un compte non vérifié existe avec cette adresse, un nouveau lien vient d'être envoyé.")


@routeur.post("/connexion")
def connexion(donnees: Connexion, requete: Request, reponse: Response, db: Base) -> CompteVisible:
    compte, jeton = service.connecter(
        db,
        email=donnees.email,
        mot_de_passe=donnees.mot_de_passe,
        appareil=requete.headers.get("user-agent"),
        maintenant=maintenant(),
    )
    db.commit()
    reponse.set_cookie(
        reglages.NOM_COOKIE_SESSION,
        jeton,
        max_age=int(reglages.SESSION_DUREE.total_seconds()),
        httponly=True,
        samesite="lax",
        secure=config.COOKIE_SECURISE,
    )
    return CompteVisible.depuis(compte)


@routeur.post("/deconnexion")
def deconnexion(reponse: Response, db: Base, jeton: CookieSession = None) -> Message:
    service.deconnecter(db, jeton, maintenant())
    db.commit()
    reponse.delete_cookie(reglages.NOM_COOKIE_SESSION)
    return Message(message="Vous êtes déconnecté.")


@routeur.get("/moi")
def moi(db: Base, jeton: CookieSession = None) -> CompteVisible:
    compte = service.compte_connecte(db, jeton, maintenant())
    if compte is None:
        raise ErreurRegle("Vous n'êtes pas connecté.", 401)
    return CompteVisible.depuis(compte)


@routeur.post("/mot-de-passe/oubli")
def oubli(donnees: AdresseMail, db: Base) -> Message:
    service.demander_nouveau_mot_de_passe(db, donnees.email, maintenant())
    db.commit()
    return Message(message="Si un compte existe avec cette adresse, un lien vient d'être envoyé (valable 1 heure).")


@routeur.post("/mot-de-passe/nouveau")
def nouveau_mot_de_passe(donnees: NouveauMotDePasse, db: Base) -> Message:
    service.changer_mot_de_passe_oublie(db, donnees.jeton, donnees.mot_de_passe, maintenant())
    db.commit()
    return Message(message="Votre mot de passe est changé. Vous pouvez vous connecter.")
