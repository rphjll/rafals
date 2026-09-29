"""Serveur de rafals."""

import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import reglages
from app.db import moteur
from app.routes import accords, administration, comptes, metiers, prestataires
from app.services import prestataires as service_prestataires
from app.services.erreurs import ErreurRegle

journal_serveur = logging.getLogger("rafals")


def _reverifier_sirets() -> None:
    with Session(moteur) as db:
        traites = service_prestataires.reverifier_sirets_en_attente(db, datetime.now(UTC))
        db.commit()
    if traites:
        journal_serveur.info("SIRET revérifiés : %s", traites)


async def _boucle_sirets() -> None:
    """Toutes les 30 minutes : nouvel essai pour les SIRET restés « à vérifier » (lot 2.4)."""
    while True:
        await asyncio.sleep(reglages.SIRET_REVERIFICATION_MINUTES * 60)
        try:
            await asyncio.to_thread(_reverifier_sirets)
        except Exception:  # une erreur ne doit jamais arrêter la boucle ni le serveur
            journal_serveur.exception("Échec de la revérification des SIRET")


@asynccontextmanager
async def cycle_de_vie(_app: FastAPI) -> AsyncIterator[None]:
    tache = asyncio.create_task(_boucle_sirets())
    yield
    tache.cancel()


app = FastAPI(title="rafals", lifespan=cycle_de_vie)
app.include_router(comptes.routeur)
app.include_router(accords.routeur)
app.include_router(administration.routeur)
app.include_router(metiers.routeur)
app.include_router(prestataires.routeur)


@app.exception_handler(ErreurRegle)
def regle_non_respectee(_requete: Request, erreur: ErreurRegle) -> JSONResponse:
    """Une règle refuse l'action : le message est montré tel quel à l'utilisateur."""
    return JSONResponse(status_code=erreur.code_http, content={"detail": erreur.message})


@app.get("/api/etat")
def etat() -> dict[str, str]:
    """Répond pour prouver que le serveur tourne (lu par la page d'accueil provisoire)."""
    return {"message": "Le serveur de rafals répond."}


@app.get("/health")
def health() -> JSONResponse:
    """Adresse de contrôle : le serveur tourne-t-il, et joint-il la base avec le bon compte ?"""
    try:
        with moteur.connect() as connexion:
            compte = connexion.execute(text("SELECT current_user")).scalar_one()
    except Exception as erreur:  # la base ne répond pas : on le dit au lieu de planter
        return JSONResponse(
            status_code=503,
            content={"serveur": "ok", "base": "injoignable", "detail": str(erreur)},
        )
    return JSONResponse(content={"serveur": "ok", "base": "ok", "compte": compte})
