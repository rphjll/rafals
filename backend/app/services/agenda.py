"""Agenda du prestataire : semaine type, blocages, réglages, horaires libres d'une annonce.
Règles : .doc/regles-metier/RM-AGENDA.md (validé le 29/09/2026).

Heures : la semaine type est une heure « de pendule » à Paris (9 h 00 reste 9 h 00 été comme hiver) ;
les blocages et les horaires calculés sont de vrais moments (enregistrés en UTC)."""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.agenda import Blocage, PlageHoraire
from app.modeles.annonces import Annonce
from app.modeles.prestataires import Prestataire
from app.services import journal
from app.services.erreurs import ErreurRegle
from app.services.prestataires import aujourd_hui, metiers_exerces

PARIS = reglages.FUSEAU_AFFICHAGE


def _modifiable(prestataire: Prestataire) -> None:
    if prestataire.statut == "arrete":
        raise ErreurRegle("Votre activité est arrêtée : ce profil ne peut plus être modifié.")
    if prestataire.statut == "bloque":
        raise ErreurRegle("Votre profil est bloqué par l'administrateur de rafals : contactez-le.", 403)


def a_paris(jour: date, heure: time) -> datetime:
    """Mardi 14/10 à 9 h 00, heure de Paris → le vrai moment (09:00+02:00 en été, 09:00+01:00 en hiver)."""
    return datetime.combine(jour, heure, tzinfo=PARIS)


def ajouter_mois(jour: date, mois: int) -> date:
    """31/10 + 2 mois → 31/12 ; 31/12 + 2 mois → 28/02 (dernier jour du mois s'il n'existe pas)."""
    rang = jour.month - 1 + mois
    annee, mois_final = jour.year + rang // 12, rang % 12 + 1
    for jour_final in range(jour.day, 27, -1):
        try:
            return date(annee, mois_final, jour_final)
        except ValueError:
            continue
    return date(annee, mois_final, min(jour.day, 28))


# ---------- Semaine type ----------


@dataclass
class Plage:
    jour_semaine: int  # 1 = lundi … 7 = dimanche
    debut: time
    fin: time


def plages_de(db: Session, prestataire: Prestataire) -> list[PlageHoraire]:
    return list(db.scalars(
        select(PlageHoraire).where(PlageHoraire.prestataire_id == prestataire.id)
        .order_by(PlageHoraire.jour_semaine, PlageHoraire.debut)
    ))


def remplacer_semaine(db: Session, prestataire: Prestataire, plages: list[Plage], maintenant: datetime) -> list[PlageHoraire]:
    """Toute la semaine type d'un coup (l'écran l'envoie en entier). Ex. Léa : mardi 9 h-12 h et 14 h-19 h, samedi 9 h-12 h.
    (Rendez-vous déjà pris hors des nouveaux horaires : « annuler ou garder », branché au niveau 4.)"""
    _modifiable(prestataire)
    triees = sorted(plages, key=lambda p: (p.jour_semaine, p.debut))
    for rang, plage in enumerate(triees):
        if not 1 <= plage.jour_semaine <= 7:
            raise ErreurRegle("Jour inconnu.")
        if plage.fin <= plage.debut:
            raise ErreurRegle(f"Une plage doit finir après son début (ex. de 9 h 00 à 12 h 00), pas de {_hm(plage.debut)} à {_hm(plage.fin)}.")
        precedente = triees[rang - 1] if rang else None
        if precedente and precedente.jour_semaine == plage.jour_semaine and plage.debut < precedente.fin:
            raise ErreurRegle(f"Deux plages se chevauchent le {JOURS[plage.jour_semaine]} : "
                              f"{_hm(precedente.debut)}-{_hm(precedente.fin)} et {_hm(plage.debut)}-{_hm(plage.fin)}.")
    avant = [_texte_plage(p) for p in plages_de(db, prestataire)]
    db.execute(delete(PlageHoraire).where(PlageHoraire.prestataire_id == prestataire.id))
    for plage in triees:
        db.add(PlageHoraire(prestataire_id=prestataire.id, jour_semaine=plage.jour_semaine, debut=plage.debut, fin=plage.fin))
    db.flush()
    journal.noter(
        db, auteur_id=prestataire.compte_id, action="modifier_semaine_type", table_cible="prestataire", ligne_id=prestataire.id,
        avant={"plages": avant}, apres={"plages": [_texte_plage(p) for p in triees]}, maintenant=maintenant,
    )
    return plages_de(db, prestataire)


JOURS = {1: "lundi", 2: "mardi", 3: "mercredi", 4: "jeudi", 5: "vendredi", 6: "samedi", 7: "dimanche"}


def _hm(heure: time) -> str:
    """09:00 → « 9 h 00 »"""
    return f"{heure.hour} h {heure.minute:02d}"


def _texte_plage(p: Plage | PlageHoraire) -> str:
    return f"{JOURS[p.jour_semaine]} {_hm(p.debut)}-{_hm(p.fin)}"


# ---------- Blocages (congés, absences) ----------


def blocages_a_venir(db: Session, prestataire: Prestataire, maintenant: datetime) -> list[Blocage]:
    return list(db.scalars(
        select(Blocage).where(Blocage.prestataire_id == prestataire.id, Blocage.fin > maintenant).order_by(Blocage.debut)
    ))


def bloquer(
    db: Session, prestataire: Prestataire, *, debut: datetime, fin: datetime, motif: str | None, maintenant: datetime
) -> Blocage:
    """Ex. Léa, congés du 04/08 au 24/08 inclus : du 04/08 0 h au 25/08 0 h. Karim, dentiste : 14/10 de 14 h à 16 h.
    Une date sans fuseau est lue à l'heure de Paris. (Rendez-vous déjà pris pendant la période : niveau 4.)"""
    _modifiable(prestataire)
    debut, fin = (d if d.tzinfo else d.replace(tzinfo=PARIS) for d in (debut, fin))
    if fin <= debut:
        raise ErreurRegle("La fin doit être après le début.")
    if fin <= maintenant:
        raise ErreurRegle("Cette période est déjà passée.")
    blocage = Blocage(prestataire_id=prestataire.id, debut=debut, fin=fin,
                      motif=(motif or "").strip()[:120] or None, cree_le=maintenant)
    db.add(blocage)
    db.flush()
    journal.noter(
        db, auteur_id=prestataire.compte_id, action="bloquer_agenda", table_cible="blocage", ligne_id=blocage.id,
        apres={"debut": debut.isoformat(), "fin": fin.isoformat()}, maintenant=maintenant,
    )
    return blocage


def debloquer(db: Session, prestataire: Prestataire, blocage_id: int, maintenant: datetime) -> None:
    """Ex. Léa annule ses congés : les horaires redeviennent réservables. Seulement ses propres blocages."""
    _modifiable(prestataire)
    blocage = db.get(Blocage, blocage_id)
    if blocage is None or blocage.prestataire_id != prestataire.id:
        raise ErreurRegle("Cette période n'existe pas.", 404)
    journal.noter(
        db, auteur_id=prestataire.compte_id, action="debloquer_agenda", table_cible="blocage", ligne_id=blocage.id,
        avant={"debut": blocage.debut.isoformat(), "fin": blocage.fin.isoformat()}, maintenant=maintenant,
    )
    db.delete(blocage)


# ---------- Réglages ----------


def modifier_reglages(
    db: Session, prestataire: Prestataire, *, pas_minutes: int, pause_minutes: int, delai_min_minutes: int, delai_max_mois: int,
    maintenant: datetime,
) -> Prestataire:
    _modifiable(prestataire)
    if pas_minutes not in reglages.AGENDA_PAS_CHOIX:
        raise ErreurRegle("Choisissez l'écart entre deux heures de début : 15 min, 30 min ou 1 h.")
    if not 0 <= pause_minutes <= reglages.AGENDA_PAUSE_MAX_MINUTES:
        raise ErreurRegle(f"La pause entre deux rendez-vous va de 0 à {reglages.AGENDA_PAUSE_MAX_MINUTES} minutes.")
    if not 0 <= delai_min_minutes <= reglages.RESERVATION_DELAI_MIN_MAX_MINUTES:
        raise ErreurRegle("Le délai « au plus tôt » va de 0 à 7 jours.")
    if not 1 <= delai_max_mois <= reglages.RESERVATION_DELAI_MAX_MAX_MOIS:
        raise ErreurRegle(f"Le délai « au plus tard » va de 1 à {reglages.RESERVATION_DELAI_MAX_MAX_MOIS} mois.")
    avant = _reglages(prestataire)
    prestataire.agenda_pas_minutes, prestataire.agenda_pause_minutes = pas_minutes, pause_minutes
    prestataire.reservation_delai_min_minutes, prestataire.reservation_delai_max_mois = delai_min_minutes, delai_max_mois
    journal.noter(
        db, auteur_id=prestataire.compte_id, action="modifier_reglages_agenda", table_cible="prestataire",
        ligne_id=prestataire.id, avant=avant, apres=_reglages(prestataire), maintenant=maintenant,
    )
    return prestataire


def _reglages(p: Prestataire) -> dict:
    return {"pas": p.agenda_pas_minutes, "pause": p.agenda_pause_minutes,
            "delai_min_minutes": p.reservation_delai_min_minutes, "delai_max_mois": p.reservation_delai_max_mois}


# ---------- Horaires libres ----------


def duree_reservee(annonce: Annonce, heures: int | None) -> timedelta:
    """Prix fixe : la durée de l'annonce. À l'heure : les heures choisies par le client, dans les limites (au départ, le minimum).
    Sur devis : pas d'agenda (demande écrite)."""
    if annonce.forme_prix == "devis":
        raise ErreurRegle("Cette annonce est sur devis : pas de rendez-vous, le client écrit sa demande.")
    if annonce.forme_prix == "heure":
        heures = annonce.heures_min if heures is None else heures
        if not (annonce.heures_min or 1) <= heures <= (annonce.heures_max or 1):
            raise ErreurRegle(f"Choisissez entre {annonce.heures_min} h et {annonce.heures_max} h.")
        return timedelta(hours=heures)
    return timedelta(minutes=annonce.duree_minutes or 0)


def horaires_libres(
    db: Session, prestataire: Prestataire, annonce: Annonce, jour: date, maintenant: datetime, heures: int | None = None
) -> list[datetime]:
    """Heures de début réservables ce jour-là. Ex. Léa, mardi 9 h-12 h, coupe de 45 min, pas de 15 min →
    9 h 00, 9 h 15 … 11 h 15 (la dernière finit à 12 h). Sont retirés : ce qui est trop tôt (« au plus tôt 2 h avant »),
    trop loin (« au plus tard 2 mois »), les blocages, et (niveau 4) les rendez-vous pris + la pause qui les suit."""
    duree = duree_reservee(annonce, heures)
    if prestataire.statut != "actif" or annonce.statut != "en_ligne":
        return []
    if annonce.metier_id not in metiers_exerces(db, prestataire, jour):
        return []  # métier arrêté ce jour-là (date de fin passée)
    if jour > ajouter_mois(aujourd_hui(maintenant), prestataire.reservation_delai_max_mois):
        return []
    au_plus_tot = maintenant + timedelta(minutes=prestataire.reservation_delai_min_minutes)
    pas = timedelta(minutes=prestataire.agenda_pas_minutes)
    plages = [p for p in plages_de(db, prestataire) if p.jour_semaine == jour.isoweekday()]
    debut_jour, fin_jour = a_paris(jour, time(0)), a_paris(jour + timedelta(days=1), time(0))
    blocages = [
        (b.debut, b.fin) for b in db.scalars(select(Blocage).where(
            Blocage.prestataire_id == prestataire.id, Blocage.debut < fin_jour, Blocage.fin > debut_jour
        ))
    ]
    occupes = blocages  # au niveau 4 : + rendez-vous pris, chacun suivi de la pause (agenda_pause_minutes)

    libres: list[datetime] = []
    for plage in plages:
        moment, fin_plage = a_paris(jour, plage.debut), a_paris(jour, plage.fin)
        while moment + duree <= fin_plage:
            fin_service = moment + duree
            if moment >= au_plus_tot and not any(moment < f and fin_service > d for d, f in occupes):
                libres.append(moment)
            moment += pas
    return libres
