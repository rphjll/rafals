"""Ce que partagent les rendez-vous, l'agenda et les prestataires : textes des mails, changement d'état, et les
annulations faites par rafals pour le prestataire (congés, semaine type, date de fin d'un métier, blocage,
arrêt). Ce module ne dépend d'aucun autre service métier (pas de boucle entre fichiers)."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.comptes import Compte
from app.modeles.prestataires import Prestataire
from app.modeles.rendez_vous import RendezVous
from app.services import journal, mails

PARIS = reglages.FUSEAU_AFFICHAGE
ACTIFS = ("en_attente", "confirme")  # rendez-vous qui comptent encore


def texte_moment(moment: datetime) -> str:
    """« mardi 14/10/2026 à 10 h 00 » (heure de Paris)"""
    local = moment.astimezone(PARIS)
    jours = ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche")
    return f"{jours[local.weekday()]} {local:%d/%m/%Y} à {local.hour} h {local.minute:02d}"


def noter(db: Session, auteur_id: int | None, action: str, rdv: RendezVous, maintenant: datetime, **apres) -> None:
    journal.noter(db, auteur_id=auteur_id, action=action, table_cible="rendez_vous", ligne_id=rdv.id,
                  apres={"statut": rdv.statut, **apres}, maintenant=maintenant)


def changer(rdv: RendezVous, statut: str, maintenant: datetime, motif: str | None = None) -> None:
    rdv.statut, rdv.statut_change_le = statut, maintenant
    if motif is not None:
        rdv.motif = motif


def prevenir(db: Session, rdv: RendezVous, *, sujet: str, client: str | None = None, prestataire: str | None = None) -> None:
    """Mail au client et / ou au prestataire (le texte dit ce qui s'est passé)."""
    if client:
        mails.envoyer_mail(db.get_one(Compte, rdv.client_id).email, sujet, client)
    if prestataire:
        compte = db.get_one(Compte, db.get_one(Prestataire, rdv.prestataire_id).compte_id)
        mails.envoyer_mail(compte.email, sujet, prestataire)


def actifs_a_venir(db: Session, prestataire: Prestataire, maintenant: datetime) -> list[RendezVous]:
    """Rendez-vous confirmés et demandes en attente pas encore commencés, du plus proche au plus loin."""
    return list(db.scalars(
        select(RendezVous).where(RendezVous.prestataire_id == prestataire.id, RendezVous.statut.in_(ACTIFS),
                                 RendezVous.debut > maintenant).order_by(RendezVous.debut)
    ))


def annuler_par_rafals(db: Session, rdv: RendezVous, motif: str, auteur_id: int | None, maintenant: datetime) -> None:
    """Annulation décidée côté prestataire (par lui ou par l'administrateur) : le client est prévenu avec le motif
    (remboursement d'un paiement en ligne : niveau 5). Ex. « Le prestataire n'est pas disponible à cette date. »"""
    changer(rdv, "annule_prestataire", maintenant, motif)
    noter(db, auteur_id, "annuler_rendez_vous_prestataire", rdv, maintenant, automatique=True)
    nom = db.get_one(Prestataire, rdv.prestataire_id).nom_affiche
    prevenir(db, rdv, sujet="rafals : rendez-vous annulé par le prestataire",
             client=f"{nom} a annulé « {rdv.titre} », {texte_moment(rdv.debut)}. Motif : « {motif} ».")
