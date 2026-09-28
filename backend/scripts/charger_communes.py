"""Charge la liste des communes (app/donnees/communes.json.gz) dans la base.

Relançable sans risque : chaque commune est reconnue par son code INSEE (ajoutée ou mise à jour,
jamais supprimée). Une seule requête pour les ~35 000 communes (quelques secondes).
Lancé à la main avec charger-communes.bat, et automatiquement au début des tests.
"""

import gzip
import json
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import moteur

FICHIER = Path(__file__).resolve().parent.parent / "app" / "donnees" / "communes.json.gz"

_REQUETE = text(
    """
    INSERT INTO commune (code_insee, nom, codes_postaux, departement, latitude, longitude)
    SELECT c.code_insee, c.nom, ARRAY(SELECT jsonb_array_elements_text(c.codes_postaux)), c.departement, c.latitude, c.longitude
    FROM jsonb_to_recordset(CAST(:donnees AS jsonb))
      AS c(code_insee text, nom text, codes_postaux jsonb, departement text, latitude double precision, longitude double precision)
    ON CONFLICT (code_insee) DO UPDATE SET
      nom = EXCLUDED.nom, codes_postaux = EXCLUDED.codes_postaux, departement = EXCLUDED.departement,
      latitude = EXCLUDED.latitude, longitude = EXCLUDED.longitude
    """
)


def charger(db: Session) -> int:
    with gzip.open(FICHIER, "rt", encoding="utf-8") as entree:
        communes = json.load(entree)["communes"]
    db.execute(_REQUETE, {"donnees": json.dumps(communes, ensure_ascii=False)})
    return len(communes)


if __name__ == "__main__":
    with Session(moteur) as db:
        nombre = charger(db)
        db.commit()
    print(f"Liste des communes chargée : {nombre} communes.")
