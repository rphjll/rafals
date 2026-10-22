"""Adresses de « Ma carte de visite » (lot 10.4, regles-metier/RM-CARTE-VISITE.md ; services/carte_visite.py)."""

from typing import Literal

from fastapi import APIRouter, Response
from pydantic import BaseModel

from app.routes.dependances import Base, CompteConnecte, maintenant
from app.routes.prestataires import mon_profil_ou_404
from app.services import carte_visite as service

routeur = APIRouter(prefix="/api")


class Apercu(BaseModel):
    """Ce que montre la page avant de télécharger. Ex. {"nom": "Karim Benali", "metier": "Plombier · Chauffagiste", …,
    "telephone": "06 12 34 56 78", "raison": null}. `raison` : pourquoi les boutons sont verrouillés (sinon null)."""

    nom: str
    metier: str
    ville: str
    note: str
    telephone: str | None  # le numéro du compte, montré à côté de la case « Mettre mon téléphone sur la carte »
    adresse: str
    raison: str | None


@routeur.get("/moi/prestataire/carte-de-visite")
def apercu(db: Base, compte: CompteConnecte) -> Apercu:
    prestataire = mon_profil_ou_404(db, compte)
    c = service.contenu(db, prestataire, compte, avec_telephone=False, maintenant=maintenant())
    return Apercu(nom=c.nom, metier=c.metier, ville=c.ville, note=c.note, telephone=compte.telephone, adresse=c.adresse,
                  raison=service.raison_du_refus(prestataire))


@routeur.get("/moi/prestataire/carte-de-visite/carre.svg")
def carre(db: Base, compte: CompteConnecte) -> Response:
    """Le carré à scanner de l'aperçu (le même que sur le PDF)."""
    prestataire = mon_profil_ou_404(db, compte)
    return Response(service.carre_svg(service.adresse_publique(prestataire)), media_type="image/svg+xml")


@routeur.get("/moi/prestataire/carte-de-visite/pdf")
def pdf(db: Base, compte: CompteConnecte, forme: Literal["planche", "carte"] = "planche", telephone: bool = False) -> Response:
    """[Télécharger la planche à découper] (forme=planche) ou [Télécharger pour un imprimeur] (forme=carte)."""
    prestataire = mon_profil_ou_404(db, compte)
    service.verifier(prestataire, compte, avec_telephone=telephone)
    c = service.contenu(db, prestataire, compte, avec_telephone=telephone, maintenant=maintenant())
    planche = forme == "planche"
    return Response(
        service.pdf_planche(c) if planche else service.pdf_carte(c), media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{service.nom_de_fichier(c.nom, planche)}"'},
    )
