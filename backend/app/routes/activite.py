"""Adresse de « Mon activité » (lot 10.1) : les chiffres du haut de la page. Règles : RM-MON-ACTIVITE.md."""

from dataclasses import asdict

from fastapi import APIRouter
from pydantic import BaseModel

from app.routes.dependances import Base, CompteConnecte, maintenant
from app.services import activite as service
from app.services import prestataires as service_prestataires

routeur = APIRouter(prefix="/api")


class ChiffresPrestataire(BaseModel):
    demandes_pres: int
    rendez_vous_semaine: int
    devis_en_attente: int
    encaisse_mois_centimes: int
    encaisse_annee_centimes: int
    annee: int
    seuil_tva_centimes: int | None  # None : il facture déjà la TVA, pas de barre
    reste_avant_seuil_centimes: int | None


class ChiffresClient(BaseModel):
    demandes_en_ligne: int
    conversations_a_lire: int
    rendez_vous_a_venir: int


class Activite(BaseModel):
    """Un seul des deux est rempli : « prestataire » pour un compte qui a un profil, sinon « client »."""

    prestataire: ChiffresPrestataire | None
    client: ChiffresClient | None


@routeur.get("/moi/activite")
def mon_activite(db: Base, compte: CompteConnecte) -> Activite:
    prestataire = service_prestataires.profil_de(db, compte)
    if prestataire is not None:
        return Activite(prestataire=ChiffresPrestataire(**asdict(service.du_prestataire(db, prestataire, maintenant()))), client=None)
    return Activite(prestataire=None, client=ChiffresClient(**asdict(service.du_client(db, compte, maintenant()))))
