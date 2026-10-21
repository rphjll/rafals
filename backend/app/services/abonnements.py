"""S'abonner à un prestataire (demande de Raphael du 21/10/2026 ; MLD .doc/mld/MLD-abonnement.html, schema_v31).
Un client suit un prestataire, le retrouve dans « Mes abonnements » et choisit, prestataire par prestataire, ses
notifications : créneau libre, nouveau métier, retour après une absence. Le nombre d'abonnés est visible par tous,
jamais leurs noms.
Ex. 1 : Julie suit Karim avec « Créneau libre » coché → un client annule jeudi 23/10 à 14 h, Julie est prévenue.
Ex. 2 : Julie suit Sonia, tout décoché → Julie ne reçoit rien, mais compte dans les « 12 abonnés » de Sonia."""

from datetime import datetime, time

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.abonnements import Abonnement
from app.modeles.comptes import Compte
from app.modeles.journal import JournalAction
from app.modeles.metiers import Metier
from app.modeles.prestataires import Prestataire
from app.services import journal, notifications
from app.services.erreurs import ErreurRegle
from app.services.rendez_vous_communs import PARIS, texte_moment

JOURS = ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche")


def _visible(prestataire: Prestataire) -> bool:
    from app.services.recherche import page_publique_visible  # ici : recherche dépend des prestataires (pas de boucle)

    return page_publique_visible(prestataire)


def abonnement_de(db: Session, compte_id: int, prestataire_id: int) -> Abonnement | None:
    return db.scalar(select(Abonnement).where(Abonnement.compte_id == compte_id, Abonnement.prestataire_id == prestataire_id))


def abonner(db: Session, compte: Compte, prestataire_id: int, maintenant: datetime) -> Abonnement:
    """[S'abonner] : les 3 notifications sont cochées au départ. Déjà abonné : rien ne change."""
    prestataire = db.get(Prestataire, prestataire_id)
    if prestataire is None or not _visible(prestataire):
        raise ErreurRegle("Ce prestataire n'existe pas.", 404)
    if prestataire.compte_id == compte.id:
        raise ErreurRegle("Vous ne pouvez pas vous abonner à votre propre profil.")
    abonnement = abonnement_de(db, compte.id, prestataire_id)
    if abonnement is None:
        abonnement = Abonnement(compte_id=compte.id, prestataire_id=prestataire_id, notif_creneau=True,
                                notif_nouveaute=True, notif_retour=True, cree_le=maintenant)
        db.add(abonnement)
        db.flush()
    return abonnement


def desabonner(db: Session, compte: Compte, prestataire_id: int) -> None:
    """[Se désabonner] : la ligne disparaît (même si le prestataire est en pause ou arrêté). Pas abonné : rien à faire."""
    db.execute(delete(Abonnement).where(Abonnement.compte_id == compte.id, Abonnement.prestataire_id == prestataire_id))


def regler(db: Session, compte: Compte, prestataire_id: int, *, creneau: bool, nouveaute: bool, retour: bool) -> Abonnement:
    """La cloche d'une carte de « Mes abonnements » : les 3 cases de ce prestataire seulement."""
    abonnement = abonnement_de(db, compte.id, prestataire_id)
    if abonnement is None:
        raise ErreurRegle("Vous n'êtes pas abonné à ce prestataire.", 404)
    abonnement.notif_creneau, abonnement.notif_nouveaute, abonnement.notif_retour = creneau, nouveaute, retour
    db.flush()
    return abonnement


def mes_abonnements(db: Session, compte: Compte) -> list[Abonnement]:
    """Le plus récent d'abord."""
    return list(db.scalars(select(Abonnement).where(Abonnement.compte_id == compte.id)
                           .order_by(Abonnement.cree_le.desc(), Abonnement.id.desc())))


def nombres(db: Session, prestataire_ids: list[int]) -> dict[int, int]:
    """« 12 abonnés » : compté à chaque affichage, jamais rangé à part. Ex. {12: 3} ; un prestataire sans abonné n'y est pas."""
    if not prestataire_ids:
        return {}
    lignes = db.execute(select(Abonnement.prestataire_id, func.count()).where(Abonnement.prestataire_id.in_(prestataire_ids))
                        .group_by(Abonnement.prestataire_id))
    return {prestataire_id: nombre for prestataire_id, nombre in lignes}


def suivis(db: Session, compte: Compte | None, prestataire_ids: list[int]) -> set[int]:
    """Parmi ces prestataires, ceux que la personne connectée suit (bouton [Abonné ✓]). Pas connectée : aucun."""
    if compte is None or not prestataire_ids:
        return set()
    return set(db.scalars(select(Abonnement.prestataire_id).where(
        Abonnement.compte_id == compte.id, Abonnement.prestataire_id.in_(prestataire_ids))))


def fermer_compte(db: Session, compte_id: int) -> None:
    """Compte fermé : il ne suit plus personne (il ne compte plus dans les abonnés)."""
    db.execute(delete(Abonnement).where(Abonnement.compte_id == compte_id))


# ---------- Les notifications envoyées aux abonnés ----------


def _prevenir(db: Session, prestataire: Prestataire, case, titre: str, texte: str, maintenant: datetime) -> int:
    """Chaque abonné qui a coché cette case, sur ses appareils (notifications.prevenir). Rend le nombre d'abonnés visés.
    Un prestataire caché (pause, bloqué, arrêté) ne prévient personne."""
    if not _visible(prestataire):
        return 0
    comptes = db.scalars(select(Abonnement.compte_id).where(Abonnement.prestataire_id == prestataire.id, case.is_(True))).all()
    for compte_id in comptes:
        notifications.prevenir(db, compte_id, titre, texte, f"/prestataires/{prestataire.id}", maintenant)
    return len(comptes)


def _deja_prevenu(db: Session, action: str, table_cible: str, ligne_id: int, depuis: datetime | None = None) -> bool:
    requete = select(JournalAction.id).where(JournalAction.action == action, JournalAction.table_cible == table_cible,
                                             JournalAction.ligne_id == ligne_id)
    if depuis is not None:
        requete = requete.where(JournalAction.fait_le > depuis)
    return db.scalar(requete.limit(1)) is not None


def _quand(debut: datetime) -> str:
    """Un jour entier : « disponible samedi 25/10/2026 » ; sinon « libre jeudi 23/10/2026 à 14 h 00 »."""
    local = debut.astimezone(PARIS)
    if local.time() == time(0, 0):
        return f"disponible {JOURS[local.weekday()]} {local:%d/%m/%Y}"
    return f"libre {texte_moment(debut)}"


def creneau_libre(db: Session, prestataire: Prestataire, debut: datetime, maintenant: datetime) -> int:
    """Un rendez-vous annulé par le client, une fermeture retirée, un jour ouvert en plus. Au plus une notification par
    prestataire en 6 h (ex. Karim ouvre 4 samedis de suite : ses abonnés ne sont prévenus qu'une fois)."""
    if debut <= maintenant or _deja_prevenu(db, "prevenir_abonnes_creneau", "prestataire", prestataire.id,
                                            maintenant - reglages.ABONNEMENT_CRENEAU_ECART):
        return 0
    prevenus = _prevenir(db, prestataire, Abonnement.notif_creneau, "Créneau libre",
                         f"{prestataire.nom_affiche} est {_quand(debut)}", maintenant)
    if prevenus:
        journal.noter(db, auteur_id=None, action="prevenir_abonnes_creneau", table_cible="prestataire",
                      ligne_id=prestataire.id, apres={"debut": debut.isoformat(), "abonnes": prevenus}, maintenant=maintenant)
    return prevenus


def nouveaux_metiers(db: Session, prestataire: Prestataire, metier_ids: list[int], maintenant: datetime) -> int:
    """Ex. Karim ajoute Chauffagiste à son profil → « Karim Benali propose maintenant : Chauffagiste »."""
    if not metier_ids:
        return 0
    noms = ", ".join(db.get_one(Metier, i).nom for i in metier_ids)
    return _prevenir(db, prestataire, Abonnement.notif_nouveaute, "Nouveau métier",
                     f"{prestataire.nom_affiche} propose maintenant : {noms}", maintenant)


def retour(db: Session, prestataire: Prestataire, reprise: datetime, maintenant: datetime) -> int:
    """Fin d'une absence (fermeture de 2 jours ou plus) ou fin d'une pause du profil."""
    local = reprise.astimezone(PARIS)
    return _prevenir(db, prestataire, Abonnement.notif_retour, "De retour",
                     f"{prestataire.nom_affiche} reprend son activité ce {JOURS[local.weekday()]} {local:%d/%m/%Y}", maintenant)


def traiter(db: Session, maintenant: datetime) -> dict[str, int]:
    """Toutes les heures : les absences finies prévenues une fois, à 8 h (heure de Paris) le jour de la reprise.
    Pas une absence : moins de 2 jours, les horaires d'un seul jour, les jours de travaux d'un devis. Ex. Léa, fermée du
    04/08 au 24/08 inclus → ses abonnés reçoivent le 25/08 à 8 h « Léa reprend son activité ce lundi 25/08/2026 »."""
    from app.modeles.agenda import Blocage
    from app.modeles.devis import Devis
    from app.services.agenda import MOTIF_HORAIRES_DU_JOUR, a_paris

    travaux = select(Devis.blocage_id).where(Devis.blocage_id.is_not(None))
    finies = db.scalars(select(Blocage).where(
        Blocage.fin <= maintenant, Blocage.fin > maintenant - reglages.ABONNEMENT_RETOUR_RATTRAPAGE,
        Blocage.fin - Blocage.debut >= reglages.ABONNEMENT_ABSENCE_MIN,
        Blocage.motif.is_distinct_from(MOTIF_HORAIRES_DU_JOUR), Blocage.id.not_in(travaux),
    ).order_by(Blocage.fin)).all()
    deja: set[int] = set()
    prevenus = 0
    for blocage in finies:
        jour = blocage.fin.astimezone(PARIS).date()
        if (maintenant < a_paris(jour, time(reglages.ABONNEMENT_RETOUR_HEURE))
                or _deja_prevenu(db, "prevenir_abonnes_retour", "blocage", blocage.id)):
            continue
        # Une autre fermeture qui commence à la reprise : l'absence continue (ex. un 2e métier fermé plus longtemps)
        encore = db.scalar(select(Blocage.id).where(Blocage.prestataire_id == blocage.prestataire_id, Blocage.id != blocage.id,
                                                    Blocage.debut <= blocage.fin, Blocage.fin > maintenant).limit(1))
        if encore is not None:
            continue
        journal.noter(db, auteur_id=None, action="prevenir_abonnes_retour", table_cible="blocage", ligne_id=blocage.id,
                      maintenant=maintenant)
        if blocage.prestataire_id not in deja:  # 2 métiers fermés pour les mêmes congés : une seule notification
            deja.add(blocage.prestataire_id)
            prevenus += retour(db, db.get_one(Prestataire, blocage.prestataire_id), blocage.fin, maintenant)
    db.flush()
    return {"retours": len(deja), "abonnes_prevenus": prevenus}
