"""Adresses des notifications sur le téléphone (lot 8.7). Règles : RM-ALERTES.md, RM-APPLICATION.md."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app import config
from app.routes.comptes import Message
from app.routes.dependances import Base, CompteConnecte, maintenant
from app.services import notifications as service

routeur = APIRouter(prefix="/api")


class Cle(BaseModel):
    """La clé publique que le navigateur demande pour s'abonner ; None = notifications pas encore branchées."""

    cle: str | None


class NouvelAppareil(BaseModel):
    """Ce que le navigateur donne quand on clique « Autoriser »."""

    adresse: str = Field(min_length=10, max_length=2000)
    cle_publique: str = Field(min_length=10, max_length=500)
    cle_secrete: str = Field(min_length=10, max_length=500)


class AdresseAppareil(BaseModel):
    adresse: str = Field(min_length=10, max_length=2000)


class EtatAppareil(BaseModel):
    """Cet appareil est-il enregistré pour ce compte ?"""

    active: bool


@routeur.get("/notifications/cle")
def cle() -> Cle:
    return Cle(cle=config.VAPID_PUBLIQUE if service.disponible() else None)


@routeur.post("/moi/appareils/etat")
def etat(donnees: AdresseAppareil, db: Base, compte: CompteConnecte) -> EtatAppareil:
    appareil = service.appareil_de(db, donnees.adresse)
    return EtatAppareil(active=appareil is not None and appareil.compte_id == compte.id)


@routeur.post("/moi/appareils")
def activer(donnees: NouvelAppareil, db: Base, compte: CompteConnecte) -> Message:
    moment = maintenant()
    service.enregistrer(db, compte, donnees.adresse, donnees.cle_publique, donnees.cle_secrete, moment)
    service.prevenir(db, compte.id, "rafals", "Les notifications sont activées sur cet appareil.", "/alertes", moment)
    db.commit()
    return Message(message="Notifications activées sur cet appareil.")


@routeur.post("/moi/appareils/couper")
def couper(donnees: AdresseAppareil, db: Base, compte: CompteConnecte) -> Message:
    service.couper(db, compte, donnees.adresse)
    db.commit()
    return Message(message="Notifications coupées sur cet appareil.")
