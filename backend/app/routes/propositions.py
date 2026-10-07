"""Adresses pour répondre à une demande et pour les propositions (suite du lot 8.3). Règles : RM-DEMANDES.md."""

from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import select

from app.modeles.demandes import Demande, Proposition
from app.modeles.metiers import Metier
from app.modeles.prestataires import Prestataire
from app.modeles.rendez_vous import RendezVous
from app.routes.demandes import DemandeVisible, MaDemande, _mienne, _visible
from app.routes.dependances import Base, CompteConnecte, maintenant
from app.routes.prestataires import mon_profil_ou_404
from app.services import demandes as service_demandes
from app.services import messagerie
from app.services import paiements as service_paiements
from app.services import propositions as service

routeur = APIRouter(prefix="/api")


class NouvelleProposition(BaseModel):
    prix_centimes: int
    debut: datetime
    duree_minutes: int
    demande_id: int | None = None
    metier_id: int | None = None
    lieu: str | None = None
    paiement_carte: bool = False
    paiement_especes: bool = True


class Prix(BaseModel):
    prix_centimes: int


class Acceptation(BaseModel):
    mode_paiement: str = "especes"


class NegociationVisible(BaseModel):
    id: int
    prix_centimes: int
    statut: str


class PropositionVisible(BaseModel):
    id: int
    conversation_id: int
    demande_id: int | None
    demande_titre: str | None
    metier: str
    prix_centimes: int
    debut: datetime
    fin: datetime
    lieu: str  # « chez_client » ou « chez_moi » (chez le prestataire)
    paiement_carte: bool
    paiement_especes: bool
    modes_de_paiement: list[str]  # ce que le client peut vraiment choisir en acceptant
    statut: str
    remplace_id: int | None
    cree_le: datetime
    negociation: NegociationVisible | None  # le prix proposé par le client, s'il attend une réponse
    rendez_vous_id: int | None


class RendezVousCree(BaseModel):
    rendez_vous_id: int
    proposition: PropositionVisible
    paiement_adresse: str | None  # par carte : la page de paiement de Stripe (30 minutes pour payer)


class ReponseFaite(BaseModel):
    conversation_id: int


def _proposition(db: Base, proposition: Proposition) -> PropositionVisible:
    conversation = service._proposition(db, proposition.id)[1]
    prestataire = db.get_one(Prestataire, conversation.prestataire_id)
    demande = db.get(Demande, proposition.demande_id) if proposition.demande_id is not None else None
    negociation = service.negociation_en_attente(db, proposition.id)
    rdv = db.scalar(select(RendezVous.id).where(RendezVous.proposition_id == proposition.id))
    return PropositionVisible(
        id=proposition.id, conversation_id=proposition.conversation_id, demande_id=proposition.demande_id,
        demande_titre=demande.titre if demande is not None else None, metier=db.get_one(Metier, proposition.metier_id).nom,
        prix_centimes=proposition.prix_centimes, debut=proposition.debut, fin=proposition.fin, lieu=proposition.lieu,
        paiement_carte=proposition.paiement_carte, paiement_especes=proposition.paiement_especes,
        modes_de_paiement=service.modes_de_paiement(proposition, prestataire), statut=proposition.statut,
        remplace_id=proposition.remplace_id, cree_le=proposition.cree_le,
        negociation=None if negociation is None else NegociationVisible(
            id=negociation.id, prix_centimes=negociation.prix_centimes, statut=negociation.statut),
        rendez_vous_id=rdv,
    )


# ---------- Répondre à une demande ----------


@routeur.get("/moi/prestataire/demandes")
def demandes_pres_de_chez_moi(db: Base, compte: CompteConnecte) -> list[DemandeVisible]:
    """« Demandes près de chez moi » : celles de mes métiers, dans mon rayon."""
    prestataire = mon_profil_ou_404(db, compte)
    return [_visible(db, compte, d) for d in service.demandes_pour(db, prestataire, maintenant())]


@routeur.post("/demandes/{demande_id}/repondre", status_code=201)
def repondre(demande_id: int, db: Base, compte: CompteConnecte) -> ReponseFaite:
    """[Répondre] : ouvre (ou rouvre) la conversation avec le client."""
    conversation = service.repondre(db, mon_profil_ou_404(db, compte), demande_id, maintenant())
    db.commit()
    return ReponseFaite(conversation_id=conversation.id)


@routeur.post("/demandes/{demande_id}/rouvrir")
def rouvrir(demande_id: int, db: Base, compte: CompteConnecte) -> MaDemande:
    demande = service_demandes.ma_demande_ou_404(db, compte, demande_id)
    service.rouvrir(db, compte, demande, maintenant())
    db.commit()
    return _mienne(db, compte, demande)


# ---------- Propositions d'une conversation ----------


@routeur.get("/conversations/{conversation_id}/demandes")
def demandes_de_la_conversation(conversation_id: int, db: Base, compte: CompteConnecte) -> list[DemandeVisible]:
    """Les demandes auxquelles ce prestataire a répondu dans cette conversation : rappelées en haut du fil."""
    conversation = messagerie.conversation_ou_404(db, compte, conversation_id)
    return [_visible(db, compte, d) for d in service.demandes_de(db, conversation.id)]


@routeur.get("/conversations/{conversation_id}/propositions")
def propositions(conversation_id: int, db: Base, compte: CompteConnecte) -> list[PropositionVisible]:
    """Pour les deux personnes de la conversation, de la plus ancienne à la plus récente."""
    conversation = messagerie.conversation_ou_404(db, compte, conversation_id)
    return [_proposition(db, p) for p in service.propositions_de(db, conversation.id)]


@routeur.post("/conversations/{conversation_id}/propositions", status_code=201)
def proposer(conversation_id: int, donnees: NouvelleProposition, db: Base, compte: CompteConnecte) -> PropositionVisible:
    proposition = service.proposer(db, mon_profil_ou_404(db, compte), conversation_id, service.Saisie(**donnees.model_dump()),
                                   maintenant())
    db.commit()
    return _proposition(db, proposition)


@routeur.post("/propositions/{proposition_id}/retirer")
def retirer(proposition_id: int, db: Base, compte: CompteConnecte) -> PropositionVisible:
    proposition = service.retirer(db, mon_profil_ou_404(db, compte), proposition_id, maintenant())
    db.commit()
    return _proposition(db, proposition)


@routeur.post("/propositions/{proposition_id}/refuser")
def refuser(proposition_id: int, db: Base, compte: CompteConnecte) -> PropositionVisible:
    proposition = service.refuser(db, compte, proposition_id, maintenant())
    db.commit()
    return _proposition(db, proposition)


@routeur.post("/propositions/{proposition_id}/negocier", status_code=201)
def negocier(proposition_id: int, donnees: Prix, db: Base, compte: CompteConnecte) -> PropositionVisible:
    negociation = service.negocier(db, compte, proposition_id, donnees.prix_centimes, maintenant())
    db.commit()
    return _proposition(db, db.get_one(Proposition, negociation.proposition_id))


@routeur.post("/negociations/{negociation_id}/accepter")
def accepter_le_prix(negociation_id: int, db: Base, compte: CompteConnecte) -> PropositionVisible:
    """Le prestataire accepte le prix du client : rend la nouvelle proposition, à ce prix."""
    proposition = service.repondre_au_prix(db, mon_profil_ou_404(db, compte), negociation_id, True, maintenant())
    db.commit()
    return _proposition(db, proposition)


@routeur.post("/negociations/{negociation_id}/refuser")
def refuser_le_prix(negociation_id: int, db: Base, compte: CompteConnecte) -> PropositionVisible:
    """Le prestataire garde son prix : sa proposition de départ attend de nouveau."""
    proposition = service.repondre_au_prix(db, mon_profil_ou_404(db, compte), negociation_id, False, maintenant())
    db.commit()
    return _proposition(db, proposition)


@routeur.post("/propositions/{proposition_id}/accepter", status_code=201)
def accepter(proposition_id: int, donnees: Acceptation, db: Base, compte: CompteConnecte) -> RendezVousCree:
    rdv = service.accepter(db, compte, proposition_id, donnees.mode_paiement, maintenant())
    adresse = service_paiements.commencer(db, rdv, compte, maintenant()) if rdv.mode_paiement == "carte" else None
    db.commit()
    return RendezVousCree(rendez_vous_id=rdv.id, proposition=_proposition(db, db.get_one(Proposition, proposition_id)),
                          paiement_adresse=adresse)
