"""Serveur de rafals."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.db import moteur

app = FastAPI(title="rafals")


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
