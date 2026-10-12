"""« Mon activité » (RM-MON-ACTIVITE.md) : les chiffres du haut de la page (lot 10.1) et « Mes clients » (lot 10.2).
Définitions proposées par Claude le 07/10/2026, à valider par Raphael. Rien n'est enregistré : tout se calcule à
partir de ce qui existe déjà."""

from dataclasses import dataclass
from datetime import datetime, time, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.comptes import Compte
from app.modeles.devis import DemandeDevis, Devis
from app.modeles.factures import Facture
from app.modeles.prestataires import Commune, Prestataire
from app.modeles.rendez_vous import RendezVous
from app.services import demandes, demarches, messagerie, paiements, propositions
from app.services import devis as service_devis
from app.services import rendez_vous as service_rendez_vous
from app.services.erreurs import ErreurRegle

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


# ---------- Mes clients (lot 10.2) ----------


@dataclass
class ClientDuPrestataire:
    client_id: int
    nom: str  # « Julie Martin » tant que les coordonnées sont visibles, sinon « Julie M. »
    telephone: str | None
    rendez_vous: int
    devis: int
    devis_en_attente: int
    paye_centimes: int
    prochain_rendez_vous: datetime | None
    dernier_rendez_vous: datetime | None
    peut_ecrire: bool  # faux pour un compte fermé
    vu_le: datetime  # pour l'ordre : le rendez-vous ou le devis le plus récent


def clients_de(db: Session, prestataire: Prestataire, maintenant: datetime) -> list[ClientDuPrestataire]:
    """« Mes clients » : les comptes qui ont un rendez-vous confirmé ou un devis envoyé avec ce prestataire, le plus
    récent d'abord. Ex. Julie : 2 rendez-vous, 1 devis, 85,00 € payés, prochain rendez-vous le 10/10/2026."""
    les_rendez_vous: dict[int, list[RendezVous]] = {}
    for rdv in db.scalars(select(RendezVous).where(RendezVous.prestataire_id == prestataire.id, RendezVous.statut == "confirme")):
        les_rendez_vous.setdefault(rdv.client_id, []).append(rdv)
    les_devis: dict[int, list[Devis]] = {}
    for devis, client_id in db.execute(select(Devis, DemandeDevis.client_id).join(
            DemandeDevis, DemandeDevis.id == Devis.demande_devis_id).where(DemandeDevis.prestataire_id == prestataire.id)):
        les_devis.setdefault(client_id, []).append(devis)
    paye: dict[int, int] = {}
    for facture in db.scalars(select(Facture).where(Facture.prestataire_id == prestataire.id, Facture.client_id.is_not(None),
                                                    Facture.sorte.in_(("vente", "avoir")))):
        paye[facture.client_id] = paye.get(facture.client_id, 0) + demarches.encaisse(db, facture)

    clients = []
    for client_id in les_rendez_vous.keys() | les_devis.keys():
        compte = db.get_one(Compte, client_id)
        rendez_vous, devis = les_rendez_vous.get(client_id, []), les_devis.get(client_id, [])
        a_venir = sorted(r.debut for r in rendez_vous if r.debut >= maintenant)
        passes = sorted(r.debut for r in rendez_vous if r.debut < maintenant)
        ferme = compte.ferme_le is not None
        visibles = not ferme and service_rendez_vous.coordonnees_client_visibles(db, prestataire, client_id, maintenant)
        clients.append(ClientDuPrestataire(
            client_id=client_id,
            nom=f"{compte.prenom} {compte.nom}".strip() if visibles else messagerie.nom_du_client(compte),
            telephone=compte.telephone if visibles else None,
            rendez_vous=len(rendez_vous),
            devis=len(devis),
            devis_en_attente=sum(1 for d in devis if d.statut == "envoye"),
            paye_centimes=paye.get(client_id, 0),
            prochain_rendez_vous=a_venir[0] if a_venir else None,
            dernier_rendez_vous=passes[-1] if passes else None,
            peut_ecrire=not ferme,
            vu_le=max([r.debut for r in rendez_vous] + [d.envoye_le for d in devis]),
        ))
    return sorted(clients, key=lambda c: c.vu_le, reverse=True)


@dataclass
class RendezVousDuClient:
    id: int
    debut: datetime
    titre: str
    prix_centimes: int | None
    a_venir: bool


@dataclass
class DevisDuClient:
    numero: str  # « D-2026-0002 »
    total_centimes: int
    statut: str
    envoye_le: datetime


@dataclass
class DemandeDuClient:
    id: int
    titre: str
    ville: str


@dataclass
class FicheClient:
    """Le détail d'un client et son profil, vus par un de ses prestataires."""

    resume: ClientDuPrestataire
    adresse: str | None  # celle de son dernier rendez-vous chez lui, tant que les coordonnées sont visibles
    inscrit_le: datetime
    rendez_vous: list[RendezVousDuClient]  # avec ce prestataire, le plus récent d'abord
    devis: list[DevisDuClient]  # de ce prestataire, le plus récent d'abord
    demandes: list[DemandeDuClient]  # ses demandes encore en ligne (déjà visibles de tous sur l'accueil)


def fiche_client(db: Session, prestataire: Prestataire, client_id: int, maintenant: datetime) -> FicheClient:
    """Tout ce qu'un prestataire peut voir d'un de ses clients (RM-MON-ACTIVITE.md § « Mes clients »). Refusé (404)
    pour quelqu'un qui n'est pas son client : pas de rendez-vous confirmé ni de devis avec lui."""
    resume = next((c for c in clients_de(db, prestataire, maintenant) if c.client_id == client_id), None)
    if resume is None:
        raise ErreurRegle("Cette personne ne fait pas partie de vos clients.", 404)
    compte = db.get_one(Compte, client_id)
    rendez_vous = list(db.scalars(select(RendezVous).where(
        RendezVous.prestataire_id == prestataire.id, RendezVous.client_id == client_id, RendezVous.statut == "confirme",
    ).order_by(RendezVous.debut.desc())))
    adresse = None
    if resume.telephone is not None or service_rendez_vous.coordonnees_client_visibles(db, prestataire, client_id, maintenant):
        chez_lui = next((r for r in rendez_vous if r.adresse_ligne), None)
        if chez_lui is not None and compte.ferme_le is None:
            adresse = f"{chez_lui.adresse_ligne}, {chez_lui.code_postal} {service_rendez_vous.commune_nom(db, chez_lui) or ''}".strip()
    devis = db.scalars(select(Devis).join(DemandeDevis, DemandeDevis.id == Devis.demande_devis_id).where(
        DemandeDevis.prestataire_id == prestataire.id, DemandeDevis.client_id == client_id).order_by(Devis.envoye_le.desc()))
    en_ligne = [] if compte.ferme_le is not None else [d for d in demandes.ouvertes(db, maintenant) if d.client_id == client_id]
    return FicheClient(
        resume=resume,
        adresse=adresse,
        inscrit_le=compte.cree_le,
        rendez_vous=[RendezVousDuClient(r.id, r.debut, r.titre, r.prix_centimes, r.debut >= maintenant) for r in rendez_vous],
        devis=[DevisDuClient(paiements.numero_devis(d), service_devis.totaux_du_devis(db, d).ttc, d.statut, d.envoye_le) for d in devis],
        demandes=[DemandeDuClient(d.id, d.titre, db.get_one(Commune, d.commune_id).nom) for d in en_ligne],
    )
