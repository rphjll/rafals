"""Adresses de « Mon activité » : les chiffres du haut de la page (lot 10.1) et « Mes clients » (lot 10.2).
Règles : RM-MON-ACTIVITE.md."""

from dataclasses import asdict
from datetime import date, datetime

from fastapi import APIRouter
from pydantic import BaseModel

from app.routes.dependances import Base, CompteConnecte, maintenant
from app.routes.prestataires import mon_profil_ou_404
from app.services import activite as service
from app.services import demarches
from app.services import prestataires as service_prestataires

routeur = APIRouter(prefix="/api")


class ChiffresPrestataire(BaseModel):
    demandes_pres: int
    rendez_vous_semaine: int
    devis_en_attente: int
    encaisse_mois_centimes: int
    encaisse_annee_centimes: int
    annee: int
    ailleurs_annee_centimes: int  # encaissé hors de rafals cette année, compté dans la barre de la TVA
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


class EncaisseAilleurs(BaseModel):
    id: int
    montant_centimes: int
    encaisse_le: date


class EncaisseAilleursAjoute(EncaisseAilleurs):
    tva_activee: bool  # vrai si la barre est pleine : la TVA est activée (peut-être par cet ajout)


class NouvelEncaisseAilleurs(BaseModel):
    montant_centimes: int
    encaisse_le: date


@routeur.get("/moi/prestataire/encaisse-ailleurs")
def mes_encaissements_ailleurs(db: Base, compte: CompteConnecte) -> list[EncaisseAilleurs]:
    """Ce que j'ai encaissé hors de rafals cette année (sous la barre de la TVA), le plus récent d'abord."""
    annee = maintenant().astimezone(demarches.PARIS).year
    return [EncaisseAilleurs(id=e.id, montant_centimes=e.montant_centimes, encaisse_le=e.encaisse_le)
            for e in demarches.encaisse_ailleurs(db, mon_profil_ou_404(db, compte), annee)]


@routeur.post("/moi/prestataire/encaisse-ailleurs", status_code=201)
def ajouter_encaisse_ailleurs(donnees: NouvelEncaisseAilleurs, db: Base, compte: CompteConnecte) -> EncaisseAilleursAjoute:
    """[Ajouter ce que j'ai encaissé ailleurs] : peut activer la TVA si la barre devient pleine (RM-MON-ACTIVITE)."""
    prestataire = mon_profil_ou_404(db, compte)
    ligne = demarches.ajouter_ailleurs(db, prestataire, donnees.montant_centimes, donnees.encaisse_le, maintenant())
    db.commit()
    return EncaisseAilleursAjoute(id=ligne.id, montant_centimes=ligne.montant_centimes, encaisse_le=ligne.encaisse_le,
                                  tva_activee=prestataire.facture_tva)


@routeur.post("/moi/prestataire/encaisse-ailleurs/{ligne_id}/retirer")
def retirer_encaisse_ailleurs(ligne_id: int, db: Base, compte: CompteConnecte) -> dict[str, bool | str]:
    """Un ajout fait par erreur disparaît ; la TVA activée par la barre se désactive si rien n'a été facturé avec
    (décision de Raphael du 09/11/2026). Ex. {"retire": true, "tva_activee": false, "message": "40 000,00 € retirés. …"}"""
    prestataire = mon_profil_ou_404(db, compte)
    message = demarches.supprimer_ailleurs(db, prestataire, ligne_id, maintenant())
    db.commit()
    return {"retire": True, "tva_activee": prestataire.facture_tva, "message": message}


class ClientVisible(BaseModel):
    client_id: int
    nom: str  # « Julie Martin » tant que les coordonnées sont visibles (3 mois après le dernier rendez-vous), sinon « Julie M. »
    telephone: str | None
    rendez_vous: int
    devis: int
    devis_en_attente: int
    paye_centimes: int
    prochain_rendez_vous: datetime | None
    dernier_rendez_vous: datetime | None
    peut_ecrire: bool


@routeur.get("/moi/prestataire/clients")
def mes_clients(db: Base, compte: CompteConnecte) -> list[ClientVisible]:
    """« Mes clients » : ceux qui ont un rendez-vous confirmé ou un devis avec moi, le plus récent d'abord."""
    clients = service.clients_de(db, mon_profil_ou_404(db, compte), maintenant())
    return [_client(c) for c in clients]


def _client(client: service.ClientDuPrestataire) -> ClientVisible:
    return ClientVisible(**{cle: valeur for cle, valeur in asdict(client).items() if cle != "vu_le"})


class RendezVousDuClient(BaseModel):
    id: int
    debut: datetime
    titre: str
    prix_centimes: int | None
    a_venir: bool


class DevisDuClient(BaseModel):
    numero: str
    total_centimes: int
    statut: str
    envoye_le: datetime


class DemandeDuClient(BaseModel):
    id: int
    titre: str
    ville: str


class FicheClient(ClientVisible):
    """Le détail ouvert sous un client de « Mes clients », et sa page « Profil »."""

    adresse: str | None
    inscrit_le: datetime
    les_rendez_vous: list[RendezVousDuClient]
    les_devis: list[DevisDuClient]
    demandes: list[DemandeDuClient]


@routeur.get("/moi/prestataire/clients/{client_id}")
def fiche_d_un_client(client_id: int, db: Base, compte: CompteConnecte) -> FicheClient:
    fiche = service.fiche_client(db, mon_profil_ou_404(db, compte), client_id, maintenant())
    return FicheClient(
        **_client(fiche.resume).model_dump(), adresse=fiche.adresse, inscrit_le=fiche.inscrit_le,
        les_rendez_vous=[RendezVousDuClient(**asdict(r)) for r in fiche.rendez_vous],
        les_devis=[DevisDuClient(**asdict(d)) for d in fiche.devis],
        demandes=[DemandeDuClient(**asdict(d)) for d in fiche.demandes],
    )
