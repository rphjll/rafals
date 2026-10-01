"""Charge la liste de départ des mots interdits (app/donnees/mots_interdits.json) dans la base.

Relançable sans risque : un mot déjà présent est ignoré ; rien n'est jamais supprimé ici
(l'administrateur retire un mot depuis l'écran Administration).

Lancé à la main (lot 4.7) :  docker compose exec -T backend python -m scripts.charger_mots_interdits
et automatiquement au début des tests, sur la base de test.
"""

import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import moteur
from app.modeles.avis import MotInterdit
from app.services.metiers import sans_accents

FICHIER = Path(__file__).resolve().parent.parent / "app" / "donnees" / "mots_interdits.json"


def charger(db: Session) -> int:
    deja = set(db.scalars(select(MotInterdit.mot)))
    ajouts = 0
    for mot in json.loads(FICHIER.read_text(encoding="utf-8"))["mots"]:
        mot = sans_accents(mot).strip()
        if len(mot) >= 2 and mot not in deja:
            db.add(MotInterdit(mot=mot))
            deja.add(mot)
            ajouts += 1
    return ajouts


if __name__ == "__main__":
    with Session(moteur) as session:
        nombre = charger(session)
        session.commit()
    print(f"{nombre} mot(s) ajouté(s) à la liste des mots interdits.")
