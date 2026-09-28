"""Serveur de rafals (lot 0.1 : version minimale, sans base de données)."""

from fastapi import FastAPI

app = FastAPI(title="rafals")


@app.get("/api/etat")
def etat() -> dict[str, str]:
    """Répond pour prouver que le serveur tourne (lu par la page d'accueil provisoire)."""
    return {"message": "Le serveur de rafals répond."}
