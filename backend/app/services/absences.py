"""Absences sur un rendez-vous : signalées par l'autre, contestables 7 jours, tranchées par l'administrateur ;
compteurs « en 6 mois » et « 3 absences → 1 mois sans réserver ». Règles : RM-RENDEZ-VOUS.md (validé le 30/09/2026).
Aucun compteur n'est enregistré : tout se calcule à partir des rendez-vous."""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.comptes import Compte
from app.modeles.prestataires import Prestataire
from app.modeles.rendez_vous import RendezVous
from app.services import rendez_vous_communs as communs
from app.services.agenda import ajouter_mois
from app.services.erreurs import ErreurRegle


# ---------- Quand une absence compte ----------


def moment_ou_elle_compte(rdv: RendezVous) -> datetime | None:
    """Sans contestation : 7 jours après le signalement. Contestée : quand l'administrateur décide qu'elle compte.
    None = elle ne compte pas (ou pas encore de décision)."""
    if rdv.absent is None or rdv.absence_signalee_le is None:
        return None
    if rdv.contestee_le is None:
        return rdv.absence_signalee_le + reglages.ABSENCE_CONTESTATION_DELAI
    return rdv.absence_decide_le if rdv.absence_decision == "compte" else None


def compte_deja(rdv: RendezVous, maintenant: datetime) -> bool:
    moment = moment_ou_elle_compte(rdv)
    return moment is not None and moment <= maintenant


def _il_y_a_6_mois(maintenant: datetime) -> datetime:
    local = maintenant.astimezone(reglages.FUSEAU_AFFICHAGE)
    jour = ajouter_mois(local.date(), -reglages.ABSENCES_FENETRE_MOIS)
    return local.replace(year=jour.year, month=jour.month, day=jour.day)


def absences_du_client(db: Session, client_id: int, maintenant: datetime) -> list[RendezVous]:
    """Ses absences qui comptent, sur les rendez-vous des 6 derniers mois."""
    lignes = db.scalars(select(RendezVous).where(
        RendezVous.client_id == client_id, RendezVous.absent == "client", RendezVous.debut >= _il_y_a_6_mois(maintenant)
    ))
    return [r for r in lignes if compte_deja(r, maintenant)]


def absences_du_prestataire(db: Session, prestataire_id: int, maintenant: datetime) -> list[RendezVous]:
    lignes = db.scalars(select(RendezVous).where(
        RendezVous.prestataire_id == prestataire_id, RendezVous.absent == "prestataire",
        RendezVous.debut >= _il_y_a_6_mois(maintenant),
    ))
    return [r for r in lignes if compte_deja(r, maintenant)]


def reservation_suspendue_jusqu_au(db: Session, client_id: int, maintenant: datetime) -> datetime | None:
    """3 absences qui comptent en 6 mois → 1 mois sans réserver, à partir du moment où la 3e a compté.
    Ex. 3e absence comptée le 10/11 → plus de réservation jusqu'au 10/12."""
    moments = sorted(m for r in absences_du_client(db, client_id, maintenant) if (m := moment_ou_elle_compte(r)))
    if len(moments) < reglages.ABSENCES_AVANT_SUSPENSION:
        return None
    depuis = moments[-1].astimezone(reglages.FUSEAU_AFFICHAGE)
    jour = ajouter_mois(depuis.date(), reglages.SUSPENSION_MOIS)
    fin = depuis.replace(year=jour.year, month=jour.month, day=jour.day)
    return fin if fin > maintenant else None


# ---------- Signaler ----------


def _apres_le_debut(rdv: RendezVous, maintenant: datetime) -> None:
    if rdv.statut != "confirme":
        raise ErreurRegle("Seul un rendez-vous confirmé peut avoir une absence.")
    if maintenant < rdv.debut:
        raise ErreurRegle("Vous pourrez signaler une absence après l'heure du rendez-vous.")
    if rdv.absent is not None:
        raise ErreurRegle("Une absence est déjà signalée pour ce rendez-vous.")
    if maintenant > rdv.fin + reglages.ABSENCE_SIGNALEMENT_DELAI:
        raise ErreurRegle("Le délai de 7 jours pour signaler une absence est passé.")


def signaler_client_absent(db: Session, prestataire: Prestataire, rdv: RendezVous, maintenant: datetime) -> RendezVous:
    """[Client absent], par le prestataire, après l'heure. Le client est prévenu et a 7 jours pour contester."""
    _apres_le_debut(rdv, maintenant)
    rdv.absent, rdv.absence_signalee_le = "client", maintenant
    communs.noter(db, prestataire.compte_id, "signaler_client_absent", rdv, maintenant)
    communs.prevenir(db, rdv, sujet="rafals : absence signalée",
                     client=f"{prestataire.nom_affiche} indique que vous n'êtes pas venu à « {rdv.titre} », "
                            f"{communs.texte_moment(rdv.debut)}. Si c'est faux, cliquez [Je suis venu] dans "
                            "« Mes rendez-vous » dans les 7 jours.")
    return rdv


def signaler_prestataire_absent(db: Session, client: Compte, rdv: RendezVous, maintenant: datetime) -> RendezVous:
    """[N'est pas venu], par le client, après l'heure (remboursement d'un paiement en ligne : niveau 5)."""
    _apres_le_debut(rdv, maintenant)
    rdv.absent, rdv.absence_signalee_le = "prestataire", maintenant
    communs.noter(db, client.id, "signaler_prestataire_absent", rdv, maintenant)
    communs.prevenir(db, rdv, sujet="rafals : absence signalée",
                     prestataire=f"Le client indique que vous n'êtes pas venu à « {rdv.titre} », "
                                 f"{communs.texte_moment(rdv.debut)}. Si c'est faux, cliquez [Je suis venu] dans "
                                 "« Mon agenda › Rendez-vous » dans les 7 jours.")
    return rdv


# ---------- Contester, trancher ----------


def contester(db: Session, compte: Compte, rdv: RendezVous, explication: str, maintenant: datetime) -> RendezVous:
    """[Je suis venu], par la personne marquée absente, dans les 7 jours : l'absence n'est plus ni comptée ni affichée
    tant que l'administrateur n'a pas tranché."""
    explication = (explication or "").strip()
    concerne = rdv.client_id if rdv.absent == "client" else db.get_one(Prestataire, rdv.prestataire_id).compte_id
    if rdv.absent is None or concerne != compte.id:
        raise ErreurRegle("Aucune absence à contester pour vous sur ce rendez-vous.", 404)
    if rdv.contestee_le is not None:
        raise ErreurRegle("Vous avez déjà contesté cette absence : l'administrateur va trancher.")
    if rdv.absence_signalee_le and maintenant > rdv.absence_signalee_le + reglages.ABSENCE_CONTESTATION_DELAI:
        raise ErreurRegle("Le délai de 7 jours pour contester est passé.")
    if len(explication) < reglages.CONTESTATION_LONGUEUR_MIN:
        raise ErreurRegle("Expliquez ce qui s'est passé (ex. « Je suis venu à 10 h, personne n'a ouvert »).")
    rdv.contestation, rdv.contestee_le = explication[:1000], maintenant
    communs.noter(db, compte.id, "contester_absence", rdv, maintenant)
    return rdv


def trancher(db: Session, administrateur: Compte, rdv_id: int, compte_l_absence: bool, maintenant: datetime) -> RendezVous:
    rdv = db.get(RendezVous, rdv_id)
    if rdv is None or rdv.contestee_le is None:
        raise ErreurRegle("Aucune contestation à trancher sur ce rendez-vous.", 404)
    if rdv.absence_decision is not None:
        raise ErreurRegle("Cette contestation est déjà tranchée.")
    rdv.absence_decision = "compte" if compte_l_absence else "ne_compte_pas"
    rdv.absence_decide_par_id, rdv.absence_decide_le = administrateur.id, maintenant
    communs.noter(db, administrateur.id, "trancher_absence", rdv, maintenant, decision=rdv.absence_decision)
    resultat = "L'absence compte." if compte_l_absence else "L'absence ne compte pas : rien n'est affiché."
    texte = f"Absence contestée sur « {rdv.titre} », {communs.texte_moment(rdv.debut)} : décision de rafals. {resultat}"
    communs.prevenir(db, rdv, sujet="rafals : décision sur une absence", client=texte, prestataire=texte)
    return rdv


def contestations_a_trancher(db: Session) -> list[RendezVous]:
    return list(db.scalars(select(RendezVous).where(
        RendezVous.contestee_le.is_not(None), RendezVous.absence_decision.is_(None)
    ).order_by(RendezVous.contestee_le)))


# ---------- Annulations de dernière minute par les prestataires (vues par l'administrateur) ----------


def annulations_tardives(db: Session, maintenant: datetime) -> list[tuple[Prestataire, int]]:
    """Rendez-vous annulés par le prestataire moins de 24 h avant, sur 6 mois ; les plus nombreux d'abord.
    Ex. Léa Martin · 2."""
    lignes = db.scalars(select(RendezVous).where(
        RendezVous.statut == "annule_prestataire", RendezVous.debut >= _il_y_a_6_mois(maintenant)
    ))
    par_prestataire: dict[int, int] = {}
    for rdv in lignes:
        if rdv.debut - rdv.statut_change_le < reglages.ANNULATION_TARDIVE:
            par_prestataire[rdv.prestataire_id] = par_prestataire.get(rdv.prestataire_id, 0) + 1
    return sorted(((db.get_one(Prestataire, i), n) for i, n in par_prestataire.items()), key=lambda c: -c[1])


# ---------- Compteurs montrés ----------


@dataclass
class Compteur:
    absences: int
    reservation_suspendue_jusqu_au: datetime | None = None


def compteur_client(db: Session, client_id: int, maintenant: datetime) -> Compteur:
    return Compteur(len(absences_du_client(db, client_id, maintenant)),
                    reservation_suspendue_jusqu_au(db, client_id, maintenant))


def compteur_prestataire(db: Session, prestataire_id: int, maintenant: datetime) -> Compteur:
    return Compteur(len(absences_du_prestataire(db, prestataire_id, maintenant)))
