"""Les chiffres du haut de « Mon activité » (RM-MON-ACTIVITE.md, lot 10.1 ; définitions proposées par Claude le
07/10/2026, à valider par Raphael). Rien n'est enregistré : tout se compte à partir de ce qui existe déjà."""

from dataclasses import dataclass
from datetime import datetime, time, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.comptes import Compte
from app.modeles.devis import DemandeDevis, Devis
from app.modeles.prestataires import Prestataire
from app.modeles.rendez_vous import RendezVous
from app.services import demandes, demarches, messagerie, propositions

PARIS = reglages.FUSEAU_AFFICHAGE


@dataclass
class ChiffresPrestataire:
    demandes_pres: int
    rendez_vous_semaine: int
    devis_en_attente: int
    encaisse_mois_centimes: int
    encaisse_annee_centimes: int
    annee: int
    # La barre de la TVA : None pour un prestataire qui facture déjà la TVA
    seuil_tva_centimes: int | None
    reste_avant_seuil_centimes: int | None


@dataclass
class ChiffresClient:
    demandes_en_ligne: int
    conversations_a_lire: int
    rendez_vous_a_venir: int


def fin_de_semaine(maintenant: datetime) -> datetime:
    """Dimanche minuit, heure de Paris. Ex. mercredi 07/10/2026 à 15 h → lundi 12/10/2026 à 0 h."""
    aujourd_hui = maintenant.astimezone(PARIS).date()
    lundi_suivant = aujourd_hui + timedelta(days=7 - aujourd_hui.weekday())
    return datetime.combine(lundi_suivant, time(0), tzinfo=PARIS)


def du_prestataire(db: Session, prestataire: Prestataire, maintenant: datetime) -> ChiffresPrestataire:
    """Ex. Karim, mercredi : 3 demandes près de chez lui, 2 rendez-vous d'ici dimanche, 1 devis sans réponse,
    640,00 € encaissés en octobre, 5 320,00 € en 2026, donc 32 180,00 € avant le seuil de TVA."""
    rendez_vous = db.scalar(select(func.count()).select_from(RendezVous).where(
        RendezVous.prestataire_id == prestataire.id, RendezVous.statut == "confirme",
        RendezVous.debut >= maintenant, RendezVous.debut < fin_de_semaine(maintenant))) or 0
    devis = db.scalar(select(func.count()).select_from(Devis).join(DemandeDevis, DemandeDevis.id == Devis.demande_devis_id).where(
        DemandeDevis.prestataire_id == prestataire.id, Devis.statut == "envoye")) or 0
    aujourd_hui = maintenant.astimezone(PARIS).date()
    mois, _trimestres = demarches.chiffre_d_affaires(db, prestataire, aujourd_hui.year, maintenant)
    annee = sum(m.encaisse_centimes for m in mois)
    seuil = None if prestataire.facture_tva else reglages.SEUIL_TVA_SERVICES_CENTIMES
    return ChiffresPrestataire(
        demandes_pres=len(propositions.demandes_pour(db, prestataire, maintenant)),
        rendez_vous_semaine=rendez_vous,
        devis_en_attente=devis,
        encaisse_mois_centimes=mois[aujourd_hui.month - 1].encaisse_centimes,
        encaisse_annee_centimes=annee,
        annee=aujourd_hui.year,
        seuil_tva_centimes=seuil,
        reste_avant_seuil_centimes=None if seuil is None else max(0, seuil - annee),
    )


def du_client(db: Session, client: Compte, maintenant: datetime) -> ChiffresClient:
    """Ex. Julie : 1 demande en ligne, 2 conversations à lire, 1 rendez-vous à venir."""
    rendez_vous = db.scalar(select(func.count()).select_from(RendezVous).where(
        RendezVous.client_id == client.id, RendezVous.statut.in_(("en_attente", "confirme")),
        RendezVous.debut >= maintenant)) or 0
    return ChiffresClient(
        demandes_en_ligne=demandes.nombre_ouvertes(db, client),
        conversations_a_lire=messagerie.conversations_non_lues(db, client),
        rendez_vous_a_venir=rendez_vous,
    )
