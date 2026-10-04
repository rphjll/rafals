"""Tableau de bord de l'administrateur et suivi des paiements (RM-ADMINISTRATION.md, lot 6.1 ; choix proposés par
Claude le 03/10/2026, à valider par Raphael). Lecture seule : rien n'est enregistré, tout se calcule à la demande."""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.annonces import Annonce
from app.modeles.comptes import Compte
from app.modeles.fichiers import AccordParental
from app.modeles.metiers import PropositionMetier
from app.modeles.paiements import Paiement
from app.modeles.prestataires import Prestataire
from app.modeles.rendez_vous import RendezVous
from app.services import absences, avis, devis, signalements

PARIS = reglages.FUSEAU_AFFICHAGE
PAYES = ("paye", "verse")  # paiements par carte gardés (ni abandonnés, ni remboursés)
PAIEMENTS_PAR_PAGE = 30


@dataclass
class ATraiter:
    """Ce qui attend une décision de l'administrateur ; la clé est l'onglet de l'écran."""

    accords: int
    absences: int
    avis: int
    devis: int
    propositions: int
    signalements: int


@dataclass
class Activite:
    """L'activité depuis le 1er du mois (heure de Paris), et ce qui est en ligne en ce moment."""

    mois: str  # « 2026-10 »
    nouveaux_comptes: int
    prestataires_actifs: int
    annonces_en_ligne: int
    rendez_vous: int
    paiements: int
    paiements_centimes: int
    commission_centimes: int
    rembourses: int


def a_traiter(db: Session) -> ATraiter:
    """Ex. « 2 accords, 1 absence contestée, 0 avis signalé »."""
    def compter(requete) -> int:
        return db.scalar(requete) or 0

    return ATraiter(
        accords=compter(select(func.count()).select_from(AccordParental).where(AccordParental.statut == "en_attente")),
        absences=len(absences.contestations_a_trancher(db)),
        avis=len(avis.avis_signales(db)),
        devis=len(devis.problemes_a_traiter(db)),
        propositions=compter(select(func.count()).select_from(PropositionMetier).where(PropositionMetier.statut == "en_attente")),
        signalements=len(signalements.a_traiter(db)),
    )


def debut_du_mois(maintenant: datetime) -> datetime:
    return maintenant.astimezone(PARIS).replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def activite(db: Session, maintenant: datetime) -> Activite:
    """Ex. « Octobre 2026 : 14 paiements par carte · 812,00 € · commission 40,60 € »."""
    depuis = debut_du_mois(maintenant)

    def compter(modele, *conditions) -> int:
        return db.scalar(select(func.count()).select_from(modele).where(*conditions)) or 0

    payes = (Paiement.statut.in_(PAYES), Paiement.paye_le >= depuis)
    return Activite(
        mois=f"{depuis:%Y-%m}",
        nouveaux_comptes=compter(Compte, Compte.cree_le >= depuis),
        prestataires_actifs=compter(Prestataire, Prestataire.statut == "actif"),
        annonces_en_ligne=compter(Annonce, Annonce.statut == "en_ligne"),
        rendez_vous=compter(RendezVous, RendezVous.cree_le >= depuis),
        paiements=compter(Paiement, *payes),
        paiements_centimes=db.scalar(select(func.coalesce(func.sum(Paiement.montant_centimes), 0)).where(*payes)) or 0,
        commission_centimes=db.scalar(select(func.coalesce(func.sum(Paiement.commission_centimes), 0)).where(*payes)) or 0,
        rembourses=compter(Paiement, Paiement.statut == "rembourse", Paiement.rembourse_le >= depuis),
    )


def paiements(db: Session, page: int) -> tuple[list[Paiement], int]:
    """Tous les paiements par carte, le plus récent d'abord, 30 par page ; et le nombre total."""
    total = db.scalar(select(func.count()).select_from(Paiement)) or 0
    lignes = db.scalars(select(Paiement).order_by(Paiement.id.desc()).limit(PAIEMENTS_PAR_PAGE)
                        .offset((max(page, 1) - 1) * PAIEMENTS_PAR_PAGE))
    return list(lignes), total
