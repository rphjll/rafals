"""Adresses de « Ma carte de visite » (lot 10.4, regles-metier/RM-CARTE-VISITE.md ; services/carte_visite.py)."""

from typing import Literal

from fastapi import APIRouter, Response
from pydantic import BaseModel

from app.routes.dependances import Base, CompteConnecte, maintenant
from app.routes.prestataires import mon_profil_ou_404
from app.services import carte_visite as service

routeur = APIRouter(prefix="/api")


class Couleur(BaseModel):
    """Une des 6 pastilles. Ex. {"code": "bleu-nuit", "nom": "Bleu nuit", "teinte": "#1D3A5F"}."""

    code: str
    nom: str
    teinte: str


class Apercu(BaseModel):
    """Ce que montre la page avant de télécharger. Ex. {"nom": "Karim Benali", "metier": "Plombier · Chauffagiste", …,
    "telephone": "06 12 34 56 78", "couleur": "bleu-nuit", "phrase": "Devis gratuit…", "raison": null}.
    `raison` : pourquoi les boutons sont verrouillés (sinon null). `couleurs` : les 6 pastilles, dans l'ordre."""

    nom: str
    metier: str
    ville: str
    note: str
    telephone: str | None  # le numéro du compte, montré à côté de la case « Mettre mon téléphone sur la carte »
    adresse: str
    couleur: str  # celle enregistrée (« vert » au départ)
    phrase: str | None  # celle enregistrée
    couleurs: list[Couleur]
    raison: str | None


class Reglages(BaseModel):
    """[Enregistrer ma carte]. Ex. {"couleur": "bleu-nuit", "phrase": "Devis gratuit, intervention sous 48 h"}."""

    couleur: str
    phrase: str | None = None


def _apercu(db: Base, compte: CompteConnecte) -> Apercu:
    prestataire = mon_profil_ou_404(db, compte)
    c = service.contenu(db, prestataire, compte, avec_telephone=False, maintenant=maintenant())
    return Apercu(nom=c.nom, metier=c.metier, ville=c.ville, note=c.note, telephone=compte.telephone, adresse=c.adresse,
                  couleur=c.couleur, phrase=c.phrase, raison=service.raison_du_refus(prestataire),
                  couleurs=[Couleur(code=code, nom=nom, teinte=teinte) for code, (nom, teinte) in service.COULEURS.items()])


@routeur.get("/moi/prestataire/carte-de-visite")
def apercu(db: Base, compte: CompteConnecte) -> Apercu:
    return _apercu(db, compte)


@routeur.post("/moi/prestataire/carte-de-visite")
def enregistrer(donnees: Reglages, db: Base, compte: CompteConnecte) -> Apercu:
    service.enregistrer(db, mon_profil_ou_404(db, compte), donnees.couleur, donnees.phrase)
    db.commit()
    return _apercu(db, compte)


@routeur.get("/moi/prestataire/carte-de-visite/carre.svg")
def carre(db: Base, compte: CompteConnecte, couleur: str = "vert") -> Response:
    """Le carré à scanner de l'aperçu (le même que sur le PDF), dans la couleur affichée sur la page."""
    prestataire = mon_profil_ou_404(db, compte)
    return Response(service.carre_svg(service.adresse_publique(prestataire), couleur), media_type="image/svg+xml")


@routeur.get("/moi/prestataire/carte-de-visite/pdf")
def pdf(db: Base, compte: CompteConnecte, forme: Literal["planche", "carte"] = "planche", telephone: bool = False,
        couleur: str | None = None, phrase: str | None = None) -> Response:
    """[Télécharger la planche à découper] (forme=planche) ou [Télécharger pour un imprimeur] (forme=carte).
    `couleur` / `phrase` : celles affichées sur la page, même pas encore enregistrées (sinon celles du profil)."""
    prestataire = mon_profil_ou_404(db, compte)
    service.verifier(prestataire, compte, avec_telephone=telephone)
    if couleur is not None:
        couleur, phrase = service.verifier_reglages(db, couleur, phrase)
    c = service.contenu(db, prestataire, compte, avec_telephone=telephone, maintenant=maintenant(), couleur=couleur, phrase=phrase)
    planche = forme == "planche"
    return Response(
        service.pdf_planche(c) if planche else service.pdf_carte(c), media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{service.nom_de_fichier(c.nom, planche)}"'},
    )
