"""Serveur de rafals."""

import asyncio
import logging
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import reglages
from app.db import moteur
from app.routes import accords, administration, clients, comptes, metiers, prestataires
from app.services import clients as service_clients
from app.services import prestataires as service_prestataires
from app.services.erreurs import ErreurRegle

journal_serveur = logging.getLogger("rafals")


def _dans_une_session(travail: Callable[[Session, datetime], object]) -> Callable[[], object]:
    """Lance un travail de fond avec sa propre session de base, puis valide (commit)."""

    def lancer() -> object:
        with Session(moteur) as db:
            resultat = travail(db, datetime.now(UTC))
            db.commit()
        return resultat

    return lancer


async def _tache_periodique(nom: str, intervalle_secondes: int, travail: Callable[[], object]) -> None:
    """Refait un travail à intervalle régulier ; une erreur est notée mais n'arrête jamais le serveur."""
    while True:
        await asyncio.sleep(intervalle_secondes)
        try:
            resultat = await asyncio.to_thread(travail)
            journal_serveur.info("%s : %s", nom, resultat)
        except Exception:
            journal_serveur.exception("Échec de la tâche « %s »", nom)


@asynccontextmanager
async def cycle_de_vie(_app: FastAPI) -> AsyncIterator[None]:
    taches = [
        # SIRET restés « à vérifier » (service de l'État en panne) : nouvel essai (lot 2.4)
        asyncio.create_task(_tache_periodique(
            "revérification des SIRET", reglages.SIRET_REVERIFICATION_MINUTES * 60,
            _dans_une_session(service_prestataires.reverifier_sirets_en_attente),
        )),
        # Comptes inactifs depuis 3 ans : mail, puis fermeture 30 jours après (lot 2.6)
        asyncio.create_task(_tache_periodique(
            "comptes inactifs (prévenus, fermés)", 24 * 60 * 60, _dans_une_session(service_clients.traiter_inactifs),
        )),
    ]
    yield
    for tache in taches:
        tache.cancel()


app = FastAPI(title="rafals", lifespan=cycle_de_vie)
app.include_router(comptes.routeur)
app.include_router(accords.routeur)
app.include_router(administration.routeur)
app.include_router(metiers.routeur)
app.include_router(prestataires.routeur)
app.include_router(clients.routeur)


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
