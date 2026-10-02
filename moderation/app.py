"""IA de modération des avis de rafals (RM-AVIS.md) : reçoit un texte, renvoie une note de 0 à 1
(0 = rien d'injurieux, 1 = très injurieux). Modèle libre Detoxify « multilingual » (Apache 2.0), sur le processeur.
Aucun texte n'est gardé : il est lu, noté, puis oublié."""

from detoxify import Detoxify
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="rafals - modération")
modele = Detoxify("multilingual")


class Texte(BaseModel):
    texte: str


@app.post("/analyser")
def analyser(donnees: Texte) -> dict[str, float]:
    """Ex. « Ponctuel et soigneux » → 0,00 ; « Karim est un gros nul qui arnaque les vieux » → note élevée."""
    resultat = modele.predict(donnees.texte[:2000])
    return {"toxicite": round(float(resultat["toxicity"]), 4)}


@app.get("/health")
def sante() -> dict[str, str]:
    return {"etat": "ok"}
