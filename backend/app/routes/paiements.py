"""Adresses du paiement par carte (écrans au lot 5.2). Règles : RM-PAIEMENTS.md."""

from datetime import datetime

from fastapi import APIRouter, Header, Request
from pydantic import BaseModel

from app import reglages
from app.modeles.comptes import Compte
from app.modeles.paiements import Paiement
from app.modeles.prestataires import Prestataire
from app.routes.dependances import Base, CompteConnecte, maintenant
from app.routes.prestataires import mon_profil_ou_404
from app.services import paiements as service
from app.services import stripe_api
from app.services.erreurs import ErreurRegle

routeur = APIRouter(prefix="/api")


class EtatCarte(BaseModel):
    """Où en est le prestataire pour être payé par carte."""

    ouvert: bool  # le paiement par carte existe sur rafals (clés de Stripe présentes)
    siret_verifie: bool
    mandat_facturation_le: datetime | None
    compte_cree: bool  # il a commencé chez Stripe
    pret: bool  # Stripe a vérifié son identité et son RIB : ses annonces peuvent proposer « carte »


class Activation(BaseModel):
    mandat: bool = False  # « J'accepte que rafals fasse mes factures à ma place »


class AdresseStripe(BaseModel):
    adresse: str


class PaiementVisible(BaseModel):
    """Un paiement par carte, vu par le client (sans les sommes internes) ou par le prestataire (tout)."""

    id: int
    rendez_vous_id: int | None
    devis_id: int | None = None
    sorte: str = "rendez_vous"  # rendez_vous · arrhes · solde
    titre: str
    debut: datetime
    avec: str  # le prestataire (vu par le client) ou le client (vu par le prestataire, « Client » hors délai RM-CLIENTS)
    statut: str  # a_payer · paye · verse · rembourse · abandonne
    montant_centimes: int
    paye_le: datetime | None
    rembourse_le: datetime | None
    rembourse_centimes: int | None
    rembourse_si_annule_centimes: int | None = None  # client : ce qu'il récupère s'il annule à temps (prix - frais)
    commission_centimes: int | None = None
    frais_stripe_centimes: int | None = None
    net_centimes: int | None = None  # ce que reçoit le prestataire
    verse_le: datetime | None = None
    versement_prevu_le: datetime | None = None  # 48 h après la fin, si rien ne le retient (absence)


def visible(db: Base, paiement: Paiement, *, prestataire: bool) -> PaiementVisible:
    """Un paiement de rendez-vous, ou les arrhes / le solde d'un devis (« titre » : « Muret de jardin — devis
    D-2026-0002 (arrhes) »)."""
    from app.services import rendez_vous as service_rdv

    s = service.sujet(db, paiement)
    rdv = s.rdv
    if prestataire:
        client = db.get_one(Compte, s.client_id)
        # Devis : le prestataire connaît son client ; rendez-vous : selon RM-CLIENTS (3 mois après)
        visibles = rdv is None or service_rdv.coordonnees_client_visibles(db, s.prestataire, client.id, maintenant())
        avec = f"{client.prenom} {client.nom}" if visibles else "Client"
    else:
        avec = s.prestataire.nom_affiche
    titre = s.titre if rdv is not None else f"{s.titre} — {s.quand}"
    debut = rdv.debut if rdv is not None else paiement.cree_le
    vu = PaiementVisible(id=paiement.id, rendez_vous_id=rdv.id if rdv else None, devis_id=paiement.devis_id, sorte=paiement.sorte,
                         titre=titre, debut=debut, avec=avec, statut=paiement.statut, montant_centimes=paiement.montant_centimes,
                         paye_le=paiement.paye_le, rembourse_le=paiement.rembourse_le,
                         rembourse_centimes=paiement.rembourse_centimes)
    if rdv is not None and paiement.statut == "paye" and paiement.frais_stripe_centimes is not None:
        vu.rembourse_si_annule_centimes = paiement.montant_centimes - paiement.frais_stripe_centimes
    if prestataire:
        vu.commission_centimes, vu.frais_stripe_centimes = paiement.commission_centimes, paiement.frais_stripe_centimes
        vu.net_centimes, vu.verse_le = service.net(paiement), paiement.verse_le
        if rdv is not None and paiement.statut == "paye" and rdv.statut in ("confirme", "en_attente") and rdv.absent is None:
            vu.versement_prevu_le = rdv.fin + reglages.VERSEMENT_APRES_FIN
    return vu


def _etat(prestataire: Prestataire) -> EtatCarte:
    return EtatCarte(ouvert=stripe_api.disponible(), siret_verifie=prestataire.siret_statut == "verifie",
                     mandat_facturation_le=prestataire.mandat_facturation_le, compte_cree=prestataire.stripe_compte is not None,
                     pret=prestataire.stripe_pret)


# ---------- Le prestataire active la carte ----------


@routeur.get("/moi/prestataire/paiement-carte")
def etat_carte(db: Base, compte: CompteConnecte) -> EtatCarte:
    """Relu chez Stripe à chaque fois (ex. au retour de la page de Stripe)."""
    prestataire = service.actualiser(db, mon_profil_ou_404(db, compte))
    db.commit()
    return _etat(prestataire)


@routeur.post("/moi/prestataire/paiement-carte")
def activer_carte(donnees: Activation, db: Base, compte: CompteConnecte) -> AdresseStripe:
    """Renvoie l'adresse de la page de Stripe où le prestataire donne son identité et son RIB."""
    adresse = service.activer(db, mon_profil_ou_404(db, compte), compte, donnees.mandat, maintenant())
    db.commit()
    return AdresseStripe(adresse=adresse)


# ---------- Mes paiements ----------


@routeur.get("/moi/paiements")
def mes_paiements(db: Base, compte: CompteConnecte) -> list[PaiementVisible]:
    """Client : ce qu'il a payé par carte, les plus récents d'abord."""
    return [visible(db, p, prestataire=False) for p in service.du_client(db, compte.id) if p.statut != "abandonne"]


@routeur.get("/moi/prestataire/paiements")
def paiements_recus(db: Base, compte: CompteConnecte) -> list[PaiementVisible]:
    """Prestataire : ce qu'on lui a payé par carte (bloqué, versé, remboursé)."""
    prestataire = mon_profil_ou_404(db, compte)
    return [visible(db, p, prestataire=True) for p in service.du_prestataire(db, prestataire.id)
            if p.statut not in service.CACHES_AU_PRESTATAIRE]


# ---------- Stripe prévient rafals ----------


@routeur.post("/stripe/evenements")
async def evenement_stripe(requete: Request, db: Base, stripe_signature: str = Header("")) -> dict[str, str]:
    """Adresse appelée par Stripe (« webhook ») : un message sans la bonne signature est refusé."""
    corps = await requete.body()
    try:
        evenement = stripe_api.lire_evenement(corps, stripe_signature)
    except ValueError as erreur:
        raise ErreurRegle("Message refusé : il ne vient pas de Stripe.", 400) from erreur
    resultat = service.recevoir(db, evenement, maintenant())
    db.commit()
    return {"resultat": resultat}
