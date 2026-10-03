"""Adresses des factures (écrans au lot 5.6). Règles : RM-FACTURES.md."""

from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Response
from pydantic import BaseModel

from app.modeles.factures import Facture
from app.routes.dependances import Base, CompteConnecte, maintenant
from app.routes.prestataires import mon_profil_ou_404
from app.routes.rendez_vous import RendezVousVisible, vu_par_le_prestataire
from app.services import factures as service
from app.services import rendez_vous as service_rdv

routeur = APIRouter(prefix="/api")


class FactureVisible(BaseModel):
    id: int
    numero: str  # « F-2026-0001 », « R-2026-0001 »
    sorte: str  # vente · avoir · commission
    emise_le: datetime
    objet: str
    vendeur: str
    acheteur: str
    ttc_centimes: int  # négatif pour un avoir
    moyen_paiement: str | None
    avoir_de: str | None  # le numéro de la facture corrigée


class PayeEnDirect(BaseModel):
    moyen: Literal["especes", "cheque", "virement"]


def visible(db: Base, facture: Facture) -> FactureVisible:
    origine = db.get(Facture, facture.avoir_de_id) if facture.avoir_de_id else None
    return FactureVisible(
        id=facture.id, numero=service.numero(facture), sorte=facture.sorte, emise_le=facture.emise_le, objet=facture.objet,
        vendeur=facture.vendeur_nom, acheteur=facture.acheteur_nom, ttc_centimes=service.totaux(db, facture).ttc,
        moyen_paiement=facture.moyen_paiement, avoir_de=service.numero(origine) if origine else None,
    )


@routeur.get("/moi/factures")
def mes_factures(db: Base, compte: CompteConnecte) -> list[FactureVisible]:
    """Client : les factures (et avoirs) de ce qu'il a payé, les plus récentes d'abord."""
    return [visible(db, f) for f in service.du_client(db, compte.id)]


@routeur.get("/moi/prestataire/factures")
def factures_du_prestataire(db: Base, compte: CompteConnecte) -> list[FactureVisible]:
    """Prestataire : ses ventes, ses avoirs, et les factures de commission de rafals."""
    return [visible(db, f) for f in service.du_prestataire(db, mon_profil_ou_404(db, compte).id)]


@routeur.get("/factures/{facture_id}/pdf")
def telecharger(facture_id: int, db: Base, compte: CompteConnecte) -> Response:
    """Le PDF, pour le client de la facture, le prestataire concerné ou un administrateur."""
    facture = service.visible_par(db, compte, facture_id)
    return Response(content=service.pdf(db, facture), media_type="application/pdf",
                    headers={"Content-Disposition": f'inline; filename="{service.numero(facture)}.pdf"'})


@routeur.post("/moi/prestataire/rendez-vous/{rdv_id}/paye")
def paye_en_direct(rdv_id: int, donnees: PayeEnDirect, db: Base, compte: CompteConnecte) -> RendezVousVisible:
    """[Payé] sur un rendez-vous payé en espèces (prestataire avec SIRET) : rafals crée la facture."""
    prestataire = mon_profil_ou_404(db, compte)
    rdv = service_rdv.rendez_vous_du_prestataire(db, prestataire, rdv_id)
    service.encaisser_rendez_vous(db, prestataire, rdv, donnees.moyen, maintenant())
    db.commit()
    return vu_par_le_prestataire(db, prestataire, rdv)
