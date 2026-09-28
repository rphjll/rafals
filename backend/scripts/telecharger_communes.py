"""Télécharge la liste officielle des communes de France (geo.api.gouv.fr) et la range,
compressée, dans app/donnees/communes.json.gz (gardée dans git : rafals s'installe sans internet).

À relancer seulement pour rafraîchir la liste (fusions de communes…) :
  docker compose exec -T backend python -m scripts.telecharger_communes
puis charger-communes.bat.
"""

import gzip
import json
import urllib.request
from datetime import date
from pathlib import Path

ADRESSE = "https://geo.api.gouv.fr/communes?fields=nom,code,codesPostaux,centre,codeDepartement&format=json"
FICHIER = Path(__file__).resolve().parent.parent / "app" / "donnees" / "communes.json.gz"


def main() -> None:
    with urllib.request.urlopen(ADRESSE, timeout=120) as reponse:
        brut = json.load(reponse)
    communes, sans_centre = [], []
    for c in brut:
        if not c.get("centre"):
            sans_centre.append(c["nom"])
            continue
        longitude, latitude = c["centre"]["coordinates"]
        communes.append(
            {
                "code_insee": c["code"],
                "nom": c["nom"],
                "codes_postaux": c.get("codesPostaux", []),
                "departement": c.get("codeDepartement", ""),
                "latitude": latitude,
                "longitude": longitude,
            }
        )
    with gzip.open(FICHIER, "wt", encoding="utf-8") as sortie:
        json.dump({"_source": f"geo.api.gouv.fr/communes, téléchargé le {date.today():%d/%m/%Y}", "communes": communes}, sortie, ensure_ascii=False)
    print(f"{len(brut)} communes reçues, {len(communes)} gardées, {len(sans_centre)} sans centre : {sans_centre[:5]}")


if __name__ == "__main__":
    main()
