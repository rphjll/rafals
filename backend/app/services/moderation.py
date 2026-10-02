"""IA de modération des avis (RM-AVIS.md ; choisie par Raphael le 01/10/2026) : le conteneur « moderation »
(Detoxify, libre et gratuit) note un texte de 0 à 1. Les avis ne quittent jamais rafals.

Si l'IA ne répond pas (conteneur arrêté, trop lent), on ne bloque pas le client : le texte passe avec le seul filtre
des mots interdits, et la panne est écrite dans le journal du serveur."""

import json
import logging
import urllib.error
import urllib.request

from app import config

journal_serveur = logging.getLogger("rafals")


def interroger(texte: str) -> float:
    """Demande la note à l'IA. Lève une erreur si elle ne répond pas (les tests remplacent cette fonction)."""
    requete = urllib.request.Request(
        f"{config.MODERATION_ADRESSE}/analyser", data=json.dumps({"texte": texte}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(requete, timeout=config.MODERATION_DELAI_SECONDES) as reponse:
        return float(json.load(reponse)["toxicite"])


def toxicite(texte: str) -> float | None:
    """Note de 0 (rien d'injurieux) à 1 (très injurieux) ; None si l'IA est en panne."""
    try:
        return interroger(texte)
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, KeyError):
        journal_serveur.warning("IA de modération injoignable : avis vérifié par la liste des mots seulement")
        return None
