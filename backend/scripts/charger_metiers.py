"""Charge la liste des dossiers et des métiers (app/donnees/metiers.json) dans la base.

Relançable sans risque : chaque dossier et chaque métier est reconnu par son code.
- nouveau code → ajouté ;
- code existant → nom, dossier, ordre et mots-clés mis à jour ;
- « SIRET obligatoire » : oui pour tout métier, sauf ceux de la liste `sans_siret` du fichier (RM-METIERS-SANS-SIRET.md) ;
- rien n'est jamais supprimé ni désactivé ici (un métier retiré de la liste se désactive à la main).

Lancé à la main (lot 2.1) :  docker compose exec -T backend python -m scripts.charger_metiers
et automatiquement au début des tests, sur la base de test.
"""

import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import moteur
from app.modeles.metiers import CategorieMetier, Metier

FICHIER = Path(__file__).resolve().parent.parent / "app" / "donnees" / "metiers.json"


def charger(db: Session) -> tuple[int, int]:
    donnees = json.loads(FICHIER.read_text(encoding="utf-8"))
    sans_siret = set(donnees.get("sans_siret", []))
    ajouts = 0
    total = 0
    for ordre, categorie_json in enumerate(donnees["categories"], start=1):
        categorie = db.scalar(select(CategorieMetier).where(CategorieMetier.code == categorie_json["code"]))
        if categorie is None:
            categorie = CategorieMetier(code=categorie_json["code"], nom=categorie_json["nom"], ordre=ordre)
            db.add(categorie)
            db.flush()
        else:
            categorie.nom, categorie.ordre = categorie_json["nom"], ordre
        for code, nom, mots in categorie_json["metiers"]:
            mots_cles = [mot.strip() for mot in mots.split(",") if mot.strip()]
            metier = db.scalar(select(Metier).where(Metier.code == code))
            if metier is None:
                db.add(Metier(categorie_id=categorie.id, code=code, nom=nom, mots_cles=mots_cles,
                              siret_obligatoire=code not in sans_siret))
                ajouts += 1
            else:
                metier.categorie_id, metier.nom, metier.mots_cles = categorie.id, nom, mots_cles
                metier.siret_obligatoire = code not in sans_siret
            total += 1
    return ajouts, total


if __name__ == "__main__":
    with Session(moteur) as db:
        ajoutes, total = charger(db)
        db.commit()
    print(f"Liste des métiers chargée : {total} métiers ({ajoutes} ajoutés, {total - ajoutes} mis à jour).")
