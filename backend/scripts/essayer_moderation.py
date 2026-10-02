"""Essai de l'IA de modération avec quelques phrases en français : affiche la note de chacune (0 à 1) et la décision
avec le seuil de reglages.py. Sert à régler le seuil. Lancé à la main :
    docker compose exec -T backend python -m scripts.essayer_moderation
"""

from app import reglages
from app.services import moderation

PHRASES = [
    "Ponctuelle et soigneuse, je recommande vivement.",
    "En retard d'une heure, sinon travail correct.",
    "Très déçu, le travail est bâclé et il a fallu tout refaire.",
    "Trop cher pour ce que c'est, je ne reviendrai pas.",
    "Karim est un gros nul qui arnaque les vieux.",
    "Quelle grosse conne, à fuir absolument.",
    "Espèce d'incapable, tu devrais avoir honte.",
    "Je vais te retrouver et tu vas le regretter.",
]

if __name__ == "__main__":
    for phrase in PHRASES:
        note = moderation.toxicite(phrase)
        decision = "IA en panne" if note is None else ("REFUSÉ" if note >= reglages.AVIS_SEUIL_TOXICITE else "accepté")
        print(f"{note if note is not None else '-':>6}  {decision:<9}  {phrase}")
