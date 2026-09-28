"""Adresses des comptes et de la connexion (appelées par les écrans du lot 1.2)."""

from datetime import date, datetime

from fastapi import APIRouter, Request, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import config, reglages
from app.modeles.comptes import Compte
from app.routes.dependances import Base, CompteConnecte, CookieSession, maintenant
from app.services import comptes as service
from app.services import droits

routeur = APIRouter(prefix="/api")


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
    est_administrateur: bool
    accord_parental_necessaire: bool
    peut_reserver_ou_publier: bool

    @classmethod
    def depuis(cls, db: Session, compte: Compte, moment: datetime) -> "CompteVisible":
        return cls(
            id=compte.id,
            email=compte.email,
            prenom=compte.prenom,
            nom=compte.nom,
            email_verifie=compte.email_verifie_le is not None,
            est_administrateur=bool(compte.est_administrateur),
            accord_parental_necessaire=droits.accord_parental_necessaire(compte, moment),
            peut_reserver_ou_publier=droits.peut_reserver_ou_publier(db, compte, moment),
        )


class Message(BaseModel):
    message: str


@routeur.post("/comptes", status_code=201)
def inscription(donnees: Inscription, db: Base) -> CompteVisible:
    moment = maintenant()
    compte = service.inscrire(db, **donnees.model_dump(), maintenant=moment)
    db.commit()
    return CompteVisible.depuis(db, compte, moment)


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
    moment = maintenant()
    compte, jeton = service.connecter(
        db,
        email=donnees.email,
        mot_de_passe=donnees.mot_de_passe,
        appareil=requete.headers.get("user-agent"),
        maintenant=moment,
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
    return CompteVisible.depuis(db, compte, moment)


@routeur.post("/deconnexion")
def deconnexion(reponse: Response, db: Base, jeton: CookieSession = None) -> Message:
    service.deconnecter(db, jeton, maintenant())
    db.commit()
    reponse.delete_cookie(reglages.NOM_COOKIE_SESSION)
    return Message(message="Vous êtes déconnecté.")


@routeur.get("/moi")
def moi(db: Base, compte: CompteConnecte) -> CompteVisible:
    return CompteVisible.depuis(db, compte, maintenant())


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
