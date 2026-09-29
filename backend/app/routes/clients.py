"""Adresses « Mon compte » : adresse, informations, télécharger mes données, fermer mon compte (écrans au lot 2.7)."""

import json

from fastapi import APIRouter, Response
from pydantic import BaseModel

from app import reglages
from app.modeles.prestataires import Commune
from app.routes.dependances import Base, CompteConnecte, maintenant
from app.services import clients as service

routeur = APIRouter(prefix="/api/moi")


class AdresseDemande(BaseModel):
    ligne: str
    complement: str | None = None
    commune_id: int
    code_postal: str


class AdresseVisible(BaseModel):
    ligne: str
    complement: str | None
    code_postal: str
    commune: dict


class Informations(BaseModel):
    prenom: str
    nom: str
    telephone: str


class Fermeture(BaseModel):
    mot_de_passe: str


def visible(db: Base, adresse) -> AdresseVisible:
    commune = db.get_one(Commune, adresse.commune_id)
    return AdresseVisible(
        ligne=adresse.ligne, complement=adresse.complement, code_postal=adresse.code_postal,
        commune={"id": commune.id, "nom": commune.nom, "codes_postaux": commune.codes_postaux, "departement": commune.departement},
    )


@routeur.get("/adresse")
def mon_adresse(db: Base, compte: CompteConnecte) -> AdresseVisible | None:
    adresse = service.adresse_de(db, compte)
    return None if adresse is None else visible(db, adresse)


@routeur.post("/adresse")
def enregistrer_adresse(donnees: AdresseDemande, db: Base, compte: CompteConnecte) -> AdresseVisible:
    adresse = service.enregistrer_adresse(db, compte, **donnees.model_dump(), maintenant=maintenant())
    db.commit()
    return visible(db, adresse)


@routeur.post("/adresse/effacer")
def effacer_adresse(db: Base, compte: CompteConnecte) -> dict[str, str]:
    service.effacer_adresse(db, compte, maintenant())
    db.commit()
    return {"message": "Votre adresse est effacée."}


@routeur.post("/informations")
def informations(donnees: Informations, db: Base, compte: CompteConnecte) -> dict[str, str]:
    service.modifier_informations(db, compte, **donnees.model_dump(), maintenant=maintenant())
    db.commit()
    return {"message": "Vos informations sont enregistrées."}


@routeur.get("/donnees")
def mes_donnees(db: Base, compte: CompteConnecte) -> Response:
    """Le fichier « mes-donnees-rafals.json », à enregistrer (droit d'accès, RGPD)."""
    donnees = service.exporter(db, compte, maintenant())
    db.commit()
    return Response(
        content=json.dumps(donnees, ensure_ascii=False, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": 'attachment; filename="mes-donnees-rafals.json"'},
    )


@routeur.post("/fermer")
def fermer(donnees: Fermeture, reponse: Response, db: Base, compte: CompteConnecte) -> dict[str, str]:
    service.fermer(db, compte, donnees.mot_de_passe, maintenant())
    db.commit()
    reponse.delete_cookie(reglages.NOM_COOKIE_SESSION)
    return {"message": "Votre compte est fermé et vos informations personnelles sont effacées."}
