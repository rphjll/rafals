"""Limites d'un prestataire sans SIRET vérifié (un « particulier, non professionnel »).
Règles : .doc/regles-metier/RM-PRESTATAIRES.md § « Limites d'un prestataire sans SIRET » (validé par Raphael le
09/10/2026) et RM-METIERS-SANS-SIRET.md. Dès que le SIRET est vérifié, aucune de ces limites ne s'applique.

1. Métiers interdits sans SIRET (METIER.siret_obligatoire).
2. 100 € au plus par proposition.
3. 2 rendez-vous par mois du calendrier (confirmés, à venir ou passés ; un rendez-vous annulé ne compte pas).
4. 1 000 € de rendez-vous qui ont eu lieu sur les 12 derniers mois ; atteints : ses propositions en attente sont
   retirées et il est prévenu.
7. Avant sa première réponse : son adresse, et la case « Mon activité est occasionnelle et je déclare mes revenus
   aux impôts ».
(Règles 5 et 6 : pas de limite de durée ; étiquette et avertissement, affichés par les écrans.)"""

from dataclasses import dataclass
from datetime import datetime, time, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.comptes import Compte
from app.modeles.demandes import Negociation, Proposition
from app.modeles.messagerie import Conversation
from app.modeles.metiers import Metier
from app.modeles.prestataires import Prestataire
from app.modeles.rendez_vous import RendezVous
from app.services import clients, journal, mails, messagerie
from app.services import paiements as service_paiements
from app.services.erreurs import ErreurRegle

PARIS = reglages.FUSEAU_AFFICHAGE
ETIQUETTE = "Particulier, non professionnel"
AVERTISSEMENT = "Pas de facture, pas de garantie, pas d'assurance professionnelle."
CASE = "Mon activité est occasionnelle et je déclare mes revenus aux impôts."
CREER = "créez votre auto-entreprise depuis « Mon activité » pour ne plus avoir de limite"


def _euros(centimes: int) -> str:
    return service_paiements.euros(centimes)


def est_particulier(prestataire: Prestataire) -> bool:
    """Sans SIRET vérifié (absent, à vérifier ou refusé). Ex. Emma, 19 ans, promène des chiens : oui ; Karim après la
    vérification de son SIRET : non."""
    return prestataire.siret_statut != "verifie"


# ---------- Règle 1 : les métiers ----------


def metier_interdit(db: Session, prestataire: Prestataire, metier_id: int) -> str | None:
    """La raison si ce métier demande un SIRET qu'il n'a pas ; None s'il peut l'exercer.
    Ex. Karim sans SIRET, « Plombier » → « Plombier demande un SIRET… » ; Emma, « Promeneur de chiens » → None."""
    if not est_particulier(prestataire):
        return None
    metier = db.get_one(Metier, metier_id)
    if not metier.siret_obligatoire:
        return None
    return f"« {metier.nom} » demande un SIRET : {CREER}."


# ---------- Règle 7 : l'adresse et la case ----------


def pas_pret(db: Session, prestataire: Prestataire) -> str | None:
    """Ce qu'il lui manque avant sa première réponse ; None s'il a tout (ou s'il a un SIRET vérifié)."""
    if not est_particulier(prestataire):
        return None
    manque = []
    if clients.adresse_de(db, db.get_one(Compte, prestataire.compte_id)) is None:
        manque.append("indiquez votre adresse")
    if prestataire.activite_occasionnelle_le is None:
        manque.append(f"cochez « {CASE} »")
    if not manque:
        return None
    return "Sans SIRET, avant de répondre : " + " et ".join(manque) + " dans « Mon profil »."


def cocher_la_case(db: Session, prestataire: Prestataire, maintenant: datetime) -> Prestataire:
    """La date est gardée une fois pour toutes : il n'a plus jamais à recommencer."""
    if prestataire.activite_occasionnelle_le is None:
        prestataire.activite_occasionnelle_le = maintenant
        journal.noter(db, auteur_id=prestataire.compte_id, action="declarer_activite_occasionnelle", table_cible="prestataire",
                      ligne_id=prestataire.id, maintenant=maintenant)
        db.flush()
    return prestataire


# ---------- Règles 3 et 4 : compter ----------


def _mois(jour: datetime) -> tuple[datetime, datetime]:
    """Le mois du calendrier (heure de Paris) où tombe ce moment. Ex. le 28/10/2026 → du 01/10 à 0 h au 01/11 à 0 h."""
    local = jour.astimezone(PARIS)
    debut = datetime.combine(local.date().replace(day=1), time(0), tzinfo=PARIS)
    fin = datetime.combine((debut.date() + timedelta(days=32)).replace(day=1), time(0), tzinfo=PARIS)
    return debut, fin


def rendez_vous_du_mois(db: Session, prestataire: Prestataire, jour: datetime) -> int:
    """Rendez-vous confirmés (à venir ou passés) dont le jour tombe dans ce mois ; un rendez-vous annulé ne compte pas."""
    debut, fin = _mois(jour)
    return db.scalar(select(func.count()).select_from(RendezVous).where(
        RendezVous.prestataire_id == prestataire.id, RendezVous.statut == "confirme",
        RendezVous.debut >= debut, RendezVous.debut < fin)) or 0


def total_des_12_mois(db: Session, prestataire: Prestataire, maintenant: datetime) -> int:
    """En centimes : les rendez-vous qui ont eu lieu (confirmés, terminés, sans absence signalée) depuis 12 mois.
    Ex. le 09/10/2026, on additionne ceux du 09/10/2025 au 09/10/2026 ; un rendez-vous à venir ne compte pas."""
    return db.scalar(select(func.coalesce(func.sum(RendezVous.prix_centimes), 0)).where(
        RendezVous.prestataire_id == prestataire.id, RendezVous.statut == "confirme", RendezVous.absent.is_(None),
        RendezVous.fin <= maintenant, RendezVous.fin > maintenant - reglages.PARTICULIER_TOTAL_SUR)) or 0


def plafond_atteint(db: Session, prestataire: Prestataire, maintenant: datetime) -> bool:
    return est_particulier(prestataire) and total_des_12_mois(db, prestataire, maintenant) >= reglages.PARTICULIER_TOTAL_CENTIMES


@dataclass
class Limites:
    """Où en est un particulier : montré dans « Mon profil »."""

    particulier: bool
    adresse_remplie: bool
    case_cochee_le: datetime | None
    prix_max_centimes: int
    rendez_vous_ce_mois: int
    rendez_vous_par_mois: int
    total_12_mois_centimes: int
    total_max_centimes: int
    plafond_atteint: bool


def limites_de(db: Session, prestataire: Prestataire, maintenant: datetime) -> Limites:
    total = total_des_12_mois(db, prestataire, maintenant)
    return Limites(
        particulier=est_particulier(prestataire),
        adresse_remplie=clients.adresse_de(db, db.get_one(Compte, prestataire.compte_id)) is not None,
        case_cochee_le=prestataire.activite_occasionnelle_le,
        prix_max_centimes=reglages.PARTICULIER_PRIX_MAX_CENTIMES,
        rendez_vous_ce_mois=rendez_vous_du_mois(db, prestataire, maintenant),
        rendez_vous_par_mois=reglages.PARTICULIER_RENDEZ_VOUS_PAR_MOIS,
        total_12_mois_centimes=total, total_max_centimes=reglages.PARTICULIER_TOTAL_CENTIMES,
        plafond_atteint=total >= reglages.PARTICULIER_TOTAL_CENTIMES,
    )


# ---------- Ce que les propositions vérifient ----------


def raison_de_ne_pas_repondre(db: Session, prestataire: Prestataire, metier_id: int, maintenant: datetime) -> str | None:
    """Pourquoi ce particulier ne peut pas répondre à une demande de ce métier ; None s'il peut (ou s'il a un SIRET)."""
    if not est_particulier(prestataire):
        return None
    interdit = metier_interdit(db, prestataire, metier_id)
    if interdit:
        return interdit
    if plafond_atteint(db, prestataire, maintenant):
        return (f"Vous avez atteint la limite des particuliers ({_euros(reglages.PARTICULIER_TOTAL_CENTIMES)} sur 12 mois) : "
                f"{CREER}.")
    return pas_pret(db, prestataire)


def verifier_reponse(db: Session, prestataire: Prestataire, metier_id: int, maintenant: datetime) -> None:
    raison = raison_de_ne_pas_repondre(db, prestataire, metier_id, maintenant)
    if raison:
        raise ErreurRegle(raison, 403)


def verifier_proposition(db: Session, prestataire: Prestataire, metier_id: int, prix_centimes: int, maintenant: datetime) -> None:
    """Avant d'envoyer une proposition : le métier, l'adresse et la case, le plafond de l'année, puis 100 € au plus."""
    if not est_particulier(prestataire):
        return
    verifier_reponse(db, prestataire, metier_id, maintenant)
    maxi = reglages.PARTICULIER_PRIX_MAX_CENTIMES
    if prix_centimes > maxi:
        raise ErreurRegle(f"Sans SIRET, une proposition ne peut pas dépasser {_euros(maxi)} : {CREER}.")


def verifier_acceptation(db: Session, prestataire: Prestataire, proposition: Proposition, maintenant: datetime) -> None:
    """Le client ne peut pas accepter si ce particulier a déjà ses 2 rendez-vous du mois, ou atteint ses 1 000 €."""
    if not est_particulier(prestataire):
        return
    if total_des_12_mois(db, prestataire, maintenant) >= reglages.PARTICULIER_TOTAL_CENTIMES:
        raise ErreurRegle(f"{prestataire.nom_affiche} a atteint la limite des particuliers : cette proposition ne peut plus être acceptée.")
    maxi = reglages.PARTICULIER_RENDEZ_VOUS_PAR_MOIS
    if rendez_vous_du_mois(db, prestataire, proposition.debut) >= maxi:
        raise ErreurRegle(f"{prestataire.nom_affiche} a atteint sa limite du mois ({maxi} rendez-vous sans SIRET) : "
                          "choisissez un jour du mois suivant, ou un autre prestataire.")


# ---------- Tâche de fond : le plafond de l'année ----------


def retirer_au_plafond(db: Session, maintenant: datetime) -> int:
    """Un particulier vient d'atteindre 1 000 € sur 12 mois : ses propositions encore en attente sont retirées, une ligne
    le dit dans chaque conversation, et il reçoit un mail. Un rendez-vous déjà confirmé n'est jamais annulé pour ça.
    Rend le nombre de propositions retirées."""
    en_attente = db.scalars(
        select(Proposition).join(Conversation, Conversation.id == Proposition.conversation_id)
        .join(Prestataire, Prestataire.id == Conversation.prestataire_id)
        .where(Proposition.statut == "en_attente", Prestataire.siret_statut != "verifie")
    ).all()
    retirees = 0
    prevenus: set[int] = set()
    for proposition in en_attente:
        conversation = db.get_one(Conversation, proposition.conversation_id)
        prestataire = db.get_one(Prestataire, conversation.prestataire_id)
        if not plafond_atteint(db, prestataire, maintenant):
            continue
        proposition.statut, proposition.statut_change_le = "retiree", maintenant
        for negociation in db.scalars(select(Negociation).where(Negociation.proposition_id == proposition.id,
                                                                Negociation.statut == "en_attente")):
            negociation.statut, negociation.repondu_le = "refusee", maintenant
        messagerie.informer(db, conversation, prestataire.compte_id,
                            f"La proposition de {_euros(proposition.prix_centimes)} de {prestataire.nom_affiche} est retirée : "
                            "il a atteint la limite des particuliers.", maintenant)
        retirees += 1
        if prestataire.id not in prevenus:
            prevenus.add(prestataire.id)
            compte = db.get_one(Compte, prestataire.compte_id)
            if compte.ferme_le is None:
                mails.envoyer_mail(
                    compte.email, "rafals : vous avez atteint la limite des particuliers",
                    f"Vos rendez-vous des 12 derniers mois atteignent {_euros(reglages.PARTICULIER_TOTAL_CENTIMES)} : c'est la "
                    "limite d'un prestataire sans SIRET. Vos propositions en attente ont été retirées. Pour continuer, "
                    f"{CREER} (10 minutes sur rafals). Vos rendez-vous déjà confirmés restent.")
    db.flush()
    return retirees
