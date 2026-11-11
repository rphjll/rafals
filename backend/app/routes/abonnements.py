"""Adresses des abonnements à un prestataire (demande de Raphael du 21/10/2026 ; services/abonnements.py)."""

from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

from app.modeles.metiers import Metier
from app.modeles.prestataires import Commune, Prestataire
from app.routes.dependances import Base, CompteConnecte, maintenant
from app.services import abonnements as service
from app.services import avis as service_avis
from app.services.recherche import page_publique_visible

routeur = APIRouter(prefix="/api")


class EtatAbonnement(BaseModel):
    """Ce que le bouton [S'abonner] / [Abonné ✓] affiche après un clic. Ex. {"abonne": true, "abonnes": 13}."""

    abonne: bool
    abonnes: int


class Notifications(BaseModel):
    """Les 3 cases de « Paramètres », pour tous mes abonnements."""

    creneau: bool
    nouveaute: bool
    retour: bool


class AbonnementVisible(BaseModel):
    """Une petite carte de « Mes abonnements »."""

    prestataire_id: int
    nom_affiche: str
    a_une_photo: bool
    ville: str
    metier: str  # son métier principal, ex. « Plombier »
    note: float | None
    nombre_avis: int
    abonnes: int
    visible: bool  # False : en pause, bloqué ou arrêté → « Profil en pause » sur la carte, pas de lien
    muet: bool  # plus aucune notification de ce prestataire
    abonne_le: datetime


def _etat(db: Base, compte_id: int, prestataire_id: int) -> EtatAbonnement:
    return EtatAbonnement(abonne=service.abonnement_de(db, compte_id, prestataire_id) is not None,
                          abonnes=service.nombres(db, [prestataire_id]).get(prestataire_id, 0))


@routeur.post("/prestataires/{prestataire_id}/abonnement")
def abonner(prestataire_id: int, db: Base, compte: CompteConnecte) -> EtatAbonnement:
    """[S'abonner] sur une carte de « Trouver un prestataire » ou sur sa page publique."""
    service.abonner(db, compte, prestataire_id, maintenant())
    db.commit()
    return _etat(db, compte.id, prestataire_id)


@routeur.post("/prestataires/{prestataire_id}/abonnement/retirer")
def desabonner(prestataire_id: int, db: Base, compte: CompteConnecte) -> EtatAbonnement:
    service.desabonner(db, compte, prestataire_id)
    db.commit()
    return _etat(db, compte.id, prestataire_id)


class Muet(BaseModel):
    muet: bool


@routeur.post("/moi/abonnements/{prestataire_id}/muet")
def rendre_muet(prestataire_id: int, donnees: Muet, db: Base, compte: CompteConnecte) -> Muet:
    """[Rendre muet] : {"muet": true} ; [Réactiver les notifications] : {"muet": false}."""
    a = service.rendre_muet(db, compte, prestataire_id, donnees.muet)
    db.commit()
    return Muet(muet=a.muet)


def _cases(compte) -> Notifications:
    return Notifications(creneau=compte.abo_notif_creneau, nouveaute=compte.abo_notif_nouveaute, retour=compte.abo_notif_retour)


@routeur.get("/moi/abonnements/notifications")
def lire_notifications(compte: CompteConnecte) -> Notifications:
    """« Paramètres » : les 3 cases, pour tous mes abonnements."""
    return _cases(compte)


@routeur.post("/moi/abonnements/notifications")
def regler(donnees: Notifications, db: Base, compte: CompteConnecte) -> Notifications:
    """« Paramètres » : ex. {"creneau": true, "nouveaute": false, "retour": true}, pour tous mes abonnements."""
    service.regler(db, compte, creneau=donnees.creneau, nouveaute=donnees.nouveaute, retour=donnees.retour)
    db.commit()
    return _cases(compte)


@routeur.get("/moi/abonnements")
def mes_abonnements(db: Base, compte: CompteConnecte) -> list[AbonnementVisible]:
    """« Mes abonnements », le plus récent d'abord."""
    lignes = service.mes_abonnements(db, compte)
    ids = [a.prestataire_id for a in lignes]
    nombres, notes = service.nombres(db, ids), service_avis.notes(db, ids)
    cartes = []
    for a in lignes:
        p = db.get_one(Prestataire, a.prestataire_id)
        somme, nombre = notes.get(p.id, (0, 0))
        cartes.append(AbonnementVisible(
            prestataire_id=p.id, nom_affiche=p.nom_affiche, a_une_photo=p.photo_id is not None,
            ville=db.get_one(Commune, p.commune_id).nom, metier=db.get_one(Metier, p.metier_principal_id).nom,
            note=somme / nombre if nombre else None, nombre_avis=nombre, abonnes=nombres.get(p.id, 0),
            visible=page_publique_visible(p),
            muet=a.muet,
            abonne_le=a.cree_le,
        ))
    return cartes
