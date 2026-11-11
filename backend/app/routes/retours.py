"""Adresse de « Un problème ? Une idée ? » (RM-RETOURS.md, lot 13.1 ; services/retours.py)."""

from typing import Annotated

from fastapi import APIRouter, Form, Header, UploadFile
from pydantic import BaseModel

from app.routes.dependances import Base, CompteConnecte, maintenant
from app.services import retours as service

routeur = APIRouter(prefix="/api")


class RetourEnvoye(BaseModel):
    """Ex. {"id": 12, "message": "Merci, c'est envoyé. Nous regardons chaque soir."}"""

    id: int
    message: str


@routeur.post("/retours", status_code=201)
async def envoyer(db: Base, compte: CompteConnecte, sorte: Annotated[str, Form()], texte: Annotated[str, Form()],
                  page: Annotated[str, Form()] = "/", capture: UploadFile | None = None,
                  user_agent: Annotated[str, Header()] = "") -> RetourEnvoye:
    """Un formulaire (pas du JSON) : « sorte » (probleme / idee), « texte », « page » et une « capture » facultative."""
    jointe = None
    if capture is not None and capture.filename:
        jointe = service.Capture(nom_fichier=capture.filename, type_mime=capture.content_type or "", contenu=await capture.read())
    retour = service.envoyer(db, compte, sorte=sorte, texte=texte, page=page, user_agent=user_agent, capture=jointe,
                             maintenant=maintenant())
    db.commit()
    return RetourEnvoye(id=retour.id, message="Merci, c'est envoyé. Nous regardons chaque soir.")
