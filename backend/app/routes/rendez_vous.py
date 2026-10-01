"""Adresses des rendez-vous, côté client et côté prestataire (écrans au lot 4.4). Règles : RM-RENDEZ-VOUS.md."""

from datetime import datetime
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import select

from app import reglages
from app.modeles.comptes import Compte
from app.modeles.prestataires import Prestataire
from app.modeles.rendez_vous import RendezVous
from app.routes.dependances import Administrateur, Base, CompteConnecte, maintenant
from app.routes.prestataires import mon_profil_ou_404
from app.services import absences
from app.services import rendez_vous as service

routeur = APIRouter(prefix="/api")


class DemandeReservation(BaseModel):
    annonce_id: int
    debut: datetime
    heures: int | None = None
    lieu: Literal["chez_client", "chez_moi"] | None = None
    mode_paiement: Literal["especes", "carte"] = "especes"


class Deplacement(BaseModel):
    debut: datetime


class Motif(BaseModel):
    motif: str | None = None


class Explication(BaseModel):
    explication: str


class Decision(BaseModel):
    compte: bool


class Absence(BaseModel):
    """Absence sur un rendez-vous (RM-RENDEZ-VOUS) : qui, quand, contestation, décision."""

    absent: str  # « client » ou « prestataire »
    signalee_le: datetime
    contestable_jusqu_au: datetime
    contestation: str | None
    contestee_le: datetime | None
    decision: str | None
    compte: bool  # compte déjà dans le compteur


class CompteurAbsences(BaseModel):
    absences: int
    reservation_suspendue_jusqu_au: datetime | None


class ContestationAdministree(BaseModel):
    rendez_vous_id: int
    titre: str
    debut: datetime
    absent: str
    client: str
    prestataire: str
    contestation: str
    contestee_le: datetime


class AnnulationsTardives(BaseModel):
    prestataire_id: int
    nom: str
    nombre: int


class ReglagesRendezVous(BaseModel):
    confirmation_automatique: bool
    annulation_delai_heures: int


class RendezVousVisible(BaseModel):
    """Ce que voit le client ou le prestataire. Les coordonnées de l'autre seulement quand elles sont permises."""

    id: int
    annonce_id: int
    remplace_id: int | None
    debut: datetime
    fin: datetime
    titre: str
    prix_centimes: int | None
    heures: int | None
    lieu: str
    adresse: str | None  # « 3 rue du Moulin, 33600 Pessac »
    mode_paiement: str
    statut: str
    motif: str | None
    reponse_avant: datetime | None
    annulable_jusqu_au: datetime | None
    absence: Absence | None
    autre: dict  # le prestataire (vu par le client) ou le client (vu par le prestataire)


def absence_visible(rdv: RendezVous) -> Absence | None:
    if rdv.absent is None or rdv.absence_signalee_le is None:
        return None
    return Absence(
        absent=rdv.absent, signalee_le=rdv.absence_signalee_le,
        contestable_jusqu_au=rdv.absence_signalee_le + reglages.ABSENCE_CONTESTATION_DELAI, contestation=rdv.contestation,
        contestee_le=rdv.contestee_le, decision=rdv.absence_decision, compte=absences.compte_deja(rdv, maintenant()),
    )


def _adresse(db: Base, rdv: RendezVous) -> str | None:
    if not rdv.adresse_ligne:
        return None
    complement = f", {rdv.adresse_complement}" if rdv.adresse_complement else ""
    return f"{rdv.adresse_ligne}{complement}, {rdv.code_postal} {service.commune_nom(db, rdv)}"


def vu_par_le_client(db: Base, rdv: RendezVous) -> RendezVousVisible:
    """Après réservation confirmée, le client voit le téléphone du prestataire et la rue du local (RM-PRESTATAIRES)."""
    prestataire = db.get_one(Prestataire, rdv.prestataire_id)
    confirme = rdv.statut == "confirme"
    telephone = db.get_one(Compte, prestataire.compte_id).telephone if confirme else None
    return RendezVousVisible(
        id=rdv.id, annonce_id=rdv.annonce_id, remplace_id=rdv.remplace_id, debut=rdv.debut, fin=rdv.fin, titre=rdv.titre,
        prix_centimes=rdv.prix_centimes, heures=rdv.heures, lieu=rdv.lieu,
        adresse=_adresse(db, rdv) if (rdv.lieu == "chez_client" or confirme) else None,
        mode_paiement=rdv.mode_paiement, statut=rdv.statut, motif=rdv.motif, reponse_avant=rdv.reponse_avant,
        annulable_jusqu_au=service.limite_annulation(prestataire, rdv) if rdv.statut == "confirme" else None,
        absence=absence_visible(rdv),
        autre={"prestataire_id": prestataire.id, "nom": prestataire.nom_affiche, "telephone": telephone},
    )


def vu_par_le_prestataire(db: Base, prestataire: Prestataire, rdv: RendezVous) -> RendezVousVisible:
    """Le prestataire voit le nom, le téléphone et l'adresse du client seulement selon RM-CLIENTS (3 mois après)."""
    visibles = service.coordonnees_client_visibles(db, prestataire, rdv.client_id, maintenant())
    client = db.get_one(Compte, rdv.client_id)
    return RendezVousVisible(
        id=rdv.id, annonce_id=rdv.annonce_id, remplace_id=rdv.remplace_id, debut=rdv.debut, fin=rdv.fin, titre=rdv.titre,
        prix_centimes=rdv.prix_centimes, heures=rdv.heures, lieu=rdv.lieu, adresse=_adresse(db, rdv) if visibles else None,
        mode_paiement=rdv.mode_paiement, statut=rdv.statut, motif=rdv.motif, reponse_avant=rdv.reponse_avant,
        annulable_jusqu_au=None, absence=absence_visible(rdv),
        # RM-RENDEZ-VOUS : chaque prestataire qui reçoit une réservation voit les absences du client
        autre={"client_id": client.id, "nom": f"{client.prenom} {client.nom}" if visibles else "Client",
               "telephone": client.telephone if visibles else None,
               "absences": len(absences.absences_du_client(db, client.id, maintenant()))},
    )


# ---------- Côté client ----------


@routeur.post("/rendez-vous", status_code=201)
def reserver(donnees: DemandeReservation, db: Base, compte: CompteConnecte) -> RendezVousVisible:
    rdv = service.reserver(db, compte, service.Demande(**donnees.model_dump()), maintenant())
    db.commit()
    return vu_par_le_client(db, rdv)


@routeur.get("/moi/rendez-vous")
def mes_rendez_vous(db: Base, compte: CompteConnecte) -> list[RendezVousVisible]:
    """Les plus proches d'abord (à venir), puis les passés."""
    liste = db.scalars(select(RendezVous).where(RendezVous.client_id == compte.id).order_by(RendezVous.debut.desc())).all()
    return [vu_par_le_client(db, r) for r in liste]


@routeur.post("/moi/rendez-vous/{rdv_id}/annuler")
def annuler(rdv_id: int, db: Base, compte: CompteConnecte) -> RendezVousVisible:
    rdv = service.annuler_par_client(db, compte, service.rendez_vous_du_client(db, compte, rdv_id), maintenant())
    db.commit()
    return vu_par_le_client(db, rdv)


@routeur.post("/moi/rendez-vous/{rdv_id}/deplacer")
def deplacer(rdv_id: int, donnees: Deplacement, db: Base, compte: CompteConnecte) -> RendezVousVisible:
    nouveau = service.deplacer(db, compte, service.rendez_vous_du_client(db, compte, rdv_id), donnees.debut, maintenant())
    db.commit()
    return vu_par_le_client(db, nouveau)


# ---------- Côté prestataire ----------


@routeur.get("/moi/prestataire/rendez-vous")
def rendez_vous_recus(db: Base, compte: CompteConnecte) -> list[RendezVousVisible]:
    prestataire = mon_profil_ou_404(db, compte)
    liste = db.scalars(
        select(RendezVous).where(RendezVous.prestataire_id == prestataire.id).order_by(RendezVous.debut.desc())
    ).all()
    return [vu_par_le_prestataire(db, prestataire, r) for r in liste]


def _repondre(db: Base, compte: Compte, rdv_id: int, action: str, motif: str | None) -> RendezVousVisible:
    prestataire = mon_profil_ou_404(db, compte)
    rdv = service.rendez_vous_du_prestataire(db, prestataire, rdv_id)
    if action == "accepter":
        service.accepter(db, prestataire, rdv, maintenant())
    elif action == "refuser":
        service.refuser(db, prestataire, rdv, motif, maintenant())
    else:
        service.annuler_par_prestataire(db, prestataire, rdv, motif or "", maintenant())
    db.commit()
    return vu_par_le_prestataire(db, prestataire, rdv)


@routeur.post("/moi/prestataire/rendez-vous/{rdv_id}/accepter")
def accepter(rdv_id: int, db: Base, compte: CompteConnecte) -> RendezVousVisible:
    return _repondre(db, compte, rdv_id, "accepter", None)


@routeur.post("/moi/prestataire/rendez-vous/{rdv_id}/refuser")
def refuser(rdv_id: int, donnees: Motif, db: Base, compte: CompteConnecte) -> RendezVousVisible:
    return _repondre(db, compte, rdv_id, "refuser", donnees.motif)


@routeur.post("/moi/prestataire/rendez-vous/{rdv_id}/annuler")
def annuler_prestataire(rdv_id: int, donnees: Motif, db: Base, compte: CompteConnecte) -> RendezVousVisible:
    return _repondre(db, compte, rdv_id, "annuler", donnees.motif)


@routeur.get("/moi/prestataire/rendez-vous/reglages")
def reglages_rdv(db: Base, compte: CompteConnecte) -> ReglagesRendezVous:
    p = mon_profil_ou_404(db, compte)
    return ReglagesRendezVous(confirmation_automatique=p.confirmation_automatique, annulation_delai_heures=p.annulation_delai_heures)


@routeur.post("/moi/prestataire/rendez-vous/reglages")
def modifier_reglages_rdv(donnees: ReglagesRendezVous, db: Base, compte: CompteConnecte) -> ReglagesRendezVous:
    p = service.modifier_reglages(db, mon_profil_ou_404(db, compte), **donnees.model_dump(), maintenant=maintenant())
    db.commit()
    return ReglagesRendezVous(confirmation_automatique=p.confirmation_automatique, annulation_delai_heures=p.annulation_delai_heures)


# ---------- Absences (lot 4.5) ----------


@routeur.post("/moi/rendez-vous/{rdv_id}/absent")
def prestataire_absent(rdv_id: int, db: Base, compte: CompteConnecte) -> RendezVousVisible:
    """[Karim n'est pas venu], par le client, après l'heure du rendez-vous."""
    rdv = absences.signaler_prestataire_absent(db, compte, service.rendez_vous_du_client(db, compte, rdv_id), maintenant())
    db.commit()
    return vu_par_le_client(db, rdv)


@routeur.post("/moi/prestataire/rendez-vous/{rdv_id}/absent")
def client_absent(rdv_id: int, db: Base, compte: CompteConnecte) -> RendezVousVisible:
    """[Client absent], par le prestataire, après l'heure du rendez-vous."""
    prestataire = mon_profil_ou_404(db, compte)
    rdv = absences.signaler_client_absent(db, prestataire, service.rendez_vous_du_prestataire(db, prestataire, rdv_id), maintenant())
    db.commit()
    return vu_par_le_prestataire(db, prestataire, rdv)


@routeur.post("/moi/rendez-vous/{rdv_id}/contester")
def contester_client(rdv_id: int, donnees: Explication, db: Base, compte: CompteConnecte) -> RendezVousVisible:
    """[Je suis venu], par le client marqué absent, dans les 7 jours."""
    rdv = absences.contester(db, compte, service.rendez_vous_du_client(db, compte, rdv_id), donnees.explication, maintenant())
    db.commit()
    return vu_par_le_client(db, rdv)


@routeur.post("/moi/prestataire/rendez-vous/{rdv_id}/contester")
def contester_prestataire(rdv_id: int, donnees: Explication, db: Base, compte: CompteConnecte) -> RendezVousVisible:
    """[Je suis venu], par le prestataire marqué absent, dans les 7 jours."""
    prestataire = mon_profil_ou_404(db, compte)
    rdv = absences.contester(db, compte, service.rendez_vous_du_prestataire(db, prestataire, rdv_id), donnees.explication,
                             maintenant())
    db.commit()
    return vu_par_le_prestataire(db, prestataire, rdv)


@routeur.get("/moi/absences")
def mes_absences(db: Base, compte: CompteConnecte) -> CompteurAbsences:
    """« 2 absences sans prévenir en 6 mois » dans « Mon compte », et le mois sans réserver s'il y en a un."""
    c = absences.compteur_client(db, compte.id, maintenant())
    return CompteurAbsences(absences=c.absences, reservation_suspendue_jusqu_au=c.reservation_suspendue_jusqu_au)


# ---------- Administration : contestations à trancher ----------


@routeur.get("/admin/contestations")
def contestations(db: Base, _admin: Administrateur) -> list[ContestationAdministree]:
    lignes = []
    for rdv in absences.contestations_a_trancher(db):
        client = db.get_one(Compte, rdv.client_id)
        lignes.append(ContestationAdministree(
            rendez_vous_id=rdv.id, titre=rdv.titre, debut=rdv.debut, absent=rdv.absent or "",
            client=f"{client.prenom} {client.nom}", prestataire=db.get_one(Prestataire, rdv.prestataire_id).nom_affiche,
            contestation=rdv.contestation or "", contestee_le=rdv.contestee_le or rdv.debut,
        ))
    return lignes


@routeur.post("/admin/contestations/{rdv_id}")
def trancher(rdv_id: int, donnees: Decision, db: Base, admin: Administrateur) -> dict[str, str]:
    rdv = absences.trancher(db, admin, rdv_id, donnees.compte, maintenant())
    db.commit()
    return {"decision": rdv.absence_decision or ""}


@routeur.get("/admin/annulations-tardives")
def annulations_tardives(db: Base, _admin: Administrateur) -> list[AnnulationsTardives]:
    """Annulations par les prestataires moins de 24 h avant, sur 6 mois (RM-RENDEZ-VOUS)."""
    return [AnnulationsTardives(prestataire_id=p.id, nom=p.nom_affiche, nombre=n)
            for p, n in absences.annulations_tardives(db, maintenant())]
