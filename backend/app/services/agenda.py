"""Agenda du prestataire : un calendrier par métier (semaine type, fermetures et ouvertures exceptionnelles),
réglages, horaires libres d'un métier pour une durée. Règles : .doc/regles-metier/RM-AGENDA.md (validé le 29/09/2026, refonte du 03/10/2026).
« Blocage » dans le code = « fermeture exceptionnelle » à l'écran.

Heures : la semaine type est une heure « de pendule » à Paris (9 h 00 reste 9 h 00 été comme hiver) ;
les blocages, les ouvertures et les horaires calculés sont de vrais moments (enregistrés en UTC)."""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.agenda import Blocage, Ouverture, PlageHoraire
from app.modeles.prestataires import Prestataire
from app.modeles.rendez_vous import RendezVous
from app.services import journal
from app.services import rendez_vous_communs as communs
from app.services.locaux import verifier_modifiable
from app.services.erreurs import ErreurRegle
from app.services.prestataires import aujourd_hui, lignes_secondaires, metiers_exerces

PARIS = reglages.FUSEAU_AFFICHAGE


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


# ---------- Un calendrier par métier ----------


def metier_du_calendrier(db: Session, prestataire: Prestataire, metier_id: int | None) -> int:
    """Le calendrier demandé ; rien = celui du métier principal. Ex. Léa : Coiffeuse (principal) ou Maquilleuse.
    Seulement un métier de son profil (même arrêté : son calendrier reste lisible)."""
    if metier_id is None or metier_id == prestataire.metier_principal_id:
        return prestataire.metier_principal_id
    if metier_id not in [ligne.metier_id for ligne in lignes_secondaires(db, prestataire)]:
        raise ErreurRegle("Ce métier n'est pas dans votre profil.", 404)
    return metier_id


def _rendez_vous_du_metier(db: Session, prestataire: Prestataire, metier_id: int, maintenant: datetime) -> list[RendezVous]:
    """Rendez-vous à venir de ce métier (les seuls touchés par un changement de ce calendrier)."""
    return [r for r in communs.actifs_a_venir(db, prestataire, maintenant) if r.metier_id == metier_id]


# ---------- Semaine type ----------


@dataclass
class Plage:
    jour_semaine: int  # 1 = lundi … 7 = dimanche
    debut: time
    fin: time


def plages_de(db: Session, prestataire: Prestataire, metier_id: int) -> list[PlageHoraire]:
    return list(db.scalars(
        select(PlageHoraire).where(PlageHoraire.prestataire_id == prestataire.id, PlageHoraire.metier_id == metier_id)
        .order_by(PlageHoraire.jour_semaine, PlageHoraire.debut)
    ))


def remplacer_semaine(
    db: Session, prestataire: Prestataire, plages: list[Plage], maintenant: datetime, rendez_vous: str | None = None,
    metier_id: int | None = None,
) -> list[PlageHoraire]:
    """Toute la semaine type d'un métier d'un coup (l'écran l'envoie en entier). Ex. Léa, Coiffeuse : mardi 9 h-12 h et
    14 h-19 h, samedi 9 h-12 h ; Maquilleuse : samedi 14 h-19 h.
    Rendez-vous déjà pris hors des nouveaux horaires : le prestataire choisit rendez_vous = « annuler » ou « garder »
    (sinon refus 409 avec la liste, pour qu'il choisisse)."""
    verifier_modifiable(prestataire)
    metier_id = metier_du_calendrier(db, prestataire, metier_id)
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
    ouvertures = ouvertures_a_venir(db, prestataire, metier_id, maintenant)
    hors = [r for r in _rendez_vous_du_metier(db, prestataire, metier_id, maintenant)
            if not _dans_les_horaires(r, triees, ouvertures)]
    _decider(db, prestataire, hors, rendez_vous, "en dehors de vos nouveaux horaires",
             "Le prestataire a changé ses horaires.", maintenant)
    avant = [_texte_plage(p) for p in plages_de(db, prestataire, metier_id)]
    db.execute(delete(PlageHoraire).where(PlageHoraire.prestataire_id == prestataire.id, PlageHoraire.metier_id == metier_id))
    for plage in triees:
        db.add(PlageHoraire(prestataire_id=prestataire.id, metier_id=metier_id, jour_semaine=plage.jour_semaine,
                            debut=plage.debut, fin=plage.fin))
    db.flush()
    journal.noter(
        db, auteur_id=prestataire.compte_id, action="modifier_semaine_type", table_cible="prestataire", ligne_id=prestataire.id,
        avant={"metier_id": metier_id, "plages": avant}, apres={"metier_id": metier_id, "plages": [_texte_plage(p) for p in triees]},
        maintenant=maintenant,
    )
    return plages_de(db, prestataire, metier_id)


def _dans_les_horaires(rdv, plages: list, ouvertures: list[Ouverture]) -> bool:
    """Le rendez-vous tient-il entièrement dans une plage de la semaine type (heure de Paris) ou dans une ouverture
    exceptionnelle ?"""
    debut, fin = rdv.debut.astimezone(PARIS), rdv.fin.astimezone(PARIS)
    return any(p.jour_semaine == debut.isoweekday() and p.debut <= debut.time() and fin.time() <= p.fin
               and debut.date() == fin.date() for p in plages) or any(o.debut <= rdv.debut and rdv.fin <= o.fin for o in ouvertures)


def _decider(db: Session, prestataire: Prestataire, touches: list, choix: str | None, ou: str, motif: str,
             maintenant: datetime) -> None:
    """Rendez-vous touchés : refus tant que le prestataire n'a pas choisi ; « annuler » les annule (clients prévenus)."""
    if not touches:
        return
    if choix not in ("annuler", "garder"):
        liste = " ; ".join(communs.texte_moment(r.debut) for r in touches[:5])
        raise ErreurRegle(f"{len(touches)} rendez-vous {ou} ({liste}) : choisissez de les annuler ou de les garder.", 409)
    if choix == "annuler":
        for rdv in touches:
            communs.annuler_par_rafals(db, rdv, motif, prestataire.compte_id, maintenant)


JOURS = {1: "lundi", 2: "mardi", 3: "mercredi", 4: "jeudi", 5: "vendredi", 6: "samedi", 7: "dimanche"}


def _hm(heure: time) -> str:
    """09:00 → « 9 h 00 »"""
    return f"{heure.hour} h {heure.minute:02d}"


def _texte_plage(p: Plage | PlageHoraire) -> str:
    return f"{JOURS[p.jour_semaine]} {_hm(p.debut)}-{_hm(p.fin)}"


# ---------- Fermetures exceptionnelles (blocages : congés, absences) ----------


def blocages_a_venir(db: Session, prestataire: Prestataire, metier_id: int, maintenant: datetime) -> list[Blocage]:
    return list(db.scalars(
        select(Blocage).where(Blocage.prestataire_id == prestataire.id, Blocage.metier_id == metier_id, Blocage.fin > maintenant)
        .order_by(Blocage.debut)
    ))


def _periode(debut: datetime, fin: datetime, maintenant: datetime) -> tuple[datetime, datetime]:
    """Une date sans fuseau est lue à l'heure de Paris. Refus : fin avant le début, période déjà passée."""
    debut, fin = (d if d.tzinfo else d.replace(tzinfo=PARIS) for d in (debut, fin))
    if fin <= debut:
        raise ErreurRegle("La fin doit être après le début.")
    if fin <= maintenant:
        raise ErreurRegle("Cette période est déjà passée.")
    return debut, fin


def bloquer(
    db: Session, prestataire: Prestataire, *, debut: datetime, fin: datetime, motif: str | None, maintenant: datetime,
    rendez_vous: str | None = None, metier_id: int | None = None,
) -> Blocage:
    """Ex. Léa, congés du 04/08 au 24/08 inclus : du 04/08 0 h au 25/08 0 h. Karim, dentiste : 14/10 de 14 h à 16 h.
    Ferme le calendrier d'un seul métier. Rendez-vous de ce métier pendant la période : le prestataire choisit
    « annuler » ou « garder » (sinon refus 409 avec la liste). Une ouverture exceptionnelle traversée est coupée."""
    verifier_modifiable(prestataire)
    metier_id = metier_du_calendrier(db, prestataire, metier_id)
    debut, fin = _periode(debut, fin, maintenant)
    touches = [r for r in _rendez_vous_du_metier(db, prestataire, metier_id, maintenant) if r.debut < fin and r.fin > debut]
    _decider(db, prestataire, touches, rendez_vous, "pendant cette période",
             "Le prestataire n'est pas disponible à cette date.", maintenant)
    blocage = Blocage(prestataire_id=prestataire.id, metier_id=metier_id, debut=debut, fin=fin,
                      motif=(motif or "").strip()[:120] or None, cree_le=maintenant)
    db.add(blocage)
    db.flush()
    for ouverture in db.scalars(select(Ouverture).where(
        Ouverture.prestataire_id == prestataire.id, Ouverture.metier_id == metier_id, Ouverture.debut < fin, Ouverture.fin > debut,
    )).all():
        _couper(db, ouverture, debut, fin)
    journal.noter(
        db, auteur_id=prestataire.compte_id, action="bloquer_agenda", table_cible="blocage", ligne_id=blocage.id,
        apres={"metier_id": metier_id, "debut": debut.isoformat(), "fin": fin.isoformat()}, maintenant=maintenant,
    )
    return blocage


def debloquer(db: Session, prestataire: Prestataire, blocage_id: int, maintenant: datetime) -> int:
    """Ex. Léa annule ses congés : les horaires redeviennent réservables. Seulement ses propres blocages.
    (Une ouverture coupée par cette fermeture ne se recolle pas.) Rend le métier du calendrier touché."""
    verifier_modifiable(prestataire)
    blocage = db.get(Blocage, blocage_id)
    if blocage is None or blocage.prestataire_id != prestataire.id:
        raise ErreurRegle("Cette période n'existe pas.", 404)
    from app.modeles.devis import Devis  # jours de travaux d'un devis accepté (lot 5.3)

    if db.scalar(select(Devis.id).where(Devis.blocage_id == blocage.id)) is not None:
        raise ErreurRegle("Ces jours sont réservés aux travaux d'un devis accepté : pour les libérer, annulez le devis.")
    journal.noter(
        db, auteur_id=prestataire.compte_id, action="debloquer_agenda", table_cible="blocage", ligne_id=blocage.id,
        avant={"metier_id": blocage.metier_id, "debut": blocage.debut.isoformat(), "fin": blocage.fin.isoformat()},
        maintenant=maintenant,
    )
    db.delete(blocage)
    return blocage.metier_id


# ---------- Ouvertures exceptionnelles ----------


def ouvertures_a_venir(db: Session, prestataire: Prestataire, metier_id: int, maintenant: datetime) -> list[Ouverture]:
    return list(db.scalars(
        select(Ouverture).where(Ouverture.prestataire_id == prestataire.id, Ouverture.metier_id == metier_id,
                                Ouverture.fin > maintenant).order_by(Ouverture.debut)
    ))


def _couper(db: Session, ouverture: Ouverture, debut: datetime, fin: datetime) -> None:
    """Une fermeture passe avant une ouverture : l'ouverture devient ce qui reste avant et après la fermeture.
    Ex. ouverture 10 h-13 h, fermeture 11 h-12 h → deux ouvertures : 10 h-11 h et 12 h-13 h."""
    for de, a in ((ouverture.debut, debut), (fin, ouverture.fin)):
        if de < a:
            db.add(Ouverture(prestataire_id=ouverture.prestataire_id, metier_id=ouverture.metier_id, debut=de, fin=a,
                             motif=ouverture.motif, cree_le=ouverture.cree_le))
    db.delete(ouverture)
    db.flush()


def ouvrir(
    db: Session, prestataire: Prestataire, *, debut: datetime, fin: datetime, motif: str | None, maintenant: datetime,
    metier_id: int | None = None,
) -> list[Ouverture]:
    """Ex. Léa, fermée le dimanche, ouvre le dimanche 18/10 de 10 h à 13 h : ces heures deviennent réservables.
    Sur plusieurs jours, l'ouverture vaut sans arrêt du début à la fin. Les fermetures déjà posées la coupent
    (ex. fermeture 11 h-12 h → deux ouvertures). Rend les ouvertures créées."""
    verifier_modifiable(prestataire)
    metier_id = metier_du_calendrier(db, prestataire, metier_id)
    debut, fin = _periode(debut, fin, maintenant)
    morceaux = [(debut, fin)]
    for blocage in blocages_a_venir(db, prestataire, metier_id, maintenant):
        restes = []
        for de, a in morceaux:
            if blocage.fin <= de or blocage.debut >= a:
                restes.append((de, a))
                continue
            if de < blocage.debut:
                restes.append((de, blocage.debut))
            if blocage.fin < a:
                restes.append((blocage.fin, a))
        morceaux = restes
    if not morceaux:
        raise ErreurRegle("Cette période est entièrement fermée par une fermeture exceptionnelle : retirez-la d'abord.")
    creees = [Ouverture(prestataire_id=prestataire.id, metier_id=metier_id, debut=de, fin=a,
                        motif=(motif or "").strip()[:120] or None, cree_le=maintenant) for de, a in morceaux]
    db.add_all(creees)
    db.flush()
    for ouverture in creees:
        journal.noter(
            db, auteur_id=prestataire.compte_id, action="ouvrir_agenda", table_cible="ouverture", ligne_id=ouverture.id,
            apres={"metier_id": metier_id, "debut": ouverture.debut.isoformat(), "fin": ouverture.fin.isoformat()},
            maintenant=maintenant,
        )
    return creees


def retirer_ouverture(db: Session, prestataire: Prestataire, ouverture_id: int, maintenant: datetime,
                      rendez_vous: str | None = None) -> int:
    """Ces heures ne sont plus réservables. Rendez-vous déjà pris pendant l'ouverture (et hors de la semaine type) :
    le prestataire choisit « annuler » ou « garder », comme pour une fermeture. Rend le métier du calendrier touché."""
    verifier_modifiable(prestataire)
    ouverture = db.get(Ouverture, ouverture_id)
    if ouverture is None or ouverture.prestataire_id != prestataire.id:
        raise ErreurRegle("Cette ouverture n'existe pas.", 404)
    plages = plages_de(db, prestataire, ouverture.metier_id)
    autres = [o for o in ouvertures_a_venir(db, prestataire, ouverture.metier_id, maintenant) if o.id != ouverture.id]
    touches = [r for r in _rendez_vous_du_metier(db, prestataire, ouverture.metier_id, maintenant)
               if r.debut < ouverture.fin and r.fin > ouverture.debut and not _dans_les_horaires(r, plages, autres)]
    _decider(db, prestataire, touches, rendez_vous, "pendant cette ouverture",
             "Le prestataire n'est pas disponible à cette date.", maintenant)
    journal.noter(
        db, auteur_id=prestataire.compte_id, action="retirer_ouverture_agenda", table_cible="ouverture", ligne_id=ouverture.id,
        avant={"metier_id": ouverture.metier_id, "debut": ouverture.debut.isoformat(), "fin": ouverture.fin.isoformat()},
        maintenant=maintenant,
    )
    db.delete(ouverture)
    return ouverture.metier_id


# ---------- Réglages ----------


def modifier_reglages(
    db: Session, prestataire: Prestataire, *, pas_minutes: int, pause_minutes: int, delai_min_minutes: int, delai_max_mois: int,
    maintenant: datetime, rendez_vous_bloque_autres_metiers: bool | None = None,
) -> Prestataire:
    verifier_modifiable(prestataire)
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
    if rendez_vous_bloque_autres_metiers is not None:  # rien = inchangé
        prestataire.rendez_vous_bloque_autres_metiers = rendez_vous_bloque_autres_metiers
    journal.noter(
        db, auteur_id=prestataire.compte_id, action="modifier_reglages_agenda", table_cible="prestataire",
        ligne_id=prestataire.id, avant=avant, apres=_reglages(prestataire), maintenant=maintenant,
    )
    return prestataire


def _reglages(p: Prestataire) -> dict:
    return {"pas": p.agenda_pas_minutes, "pause": p.agenda_pause_minutes,
            "delai_min_minutes": p.reservation_delai_min_minutes, "delai_max_mois": p.reservation_delai_max_mois,
            "rendez_vous_bloque_autres_metiers": p.rendez_vous_bloque_autres_metiers}


# ---------- Horaires libres ----------


OCCUPENT_L_AGENDA = ("en_attente", "confirme")  # une demande en attente garde l'horaire (RM-RENDEZ-VOUS)


def horaires_libres(
    db: Session, prestataire: Prestataire, metier_id: int, duree: timedelta, jour: date, maintenant: datetime,
) -> list[datetime]:
    """Heures de début libres ce jour-là dans le calendrier d'un métier, pour un service de cette durée. Sert au
    prestataire (le client ne voit plus les horaires : RM-AGENDA § « Sans annonces »). Ex. Léa, mardi 9 h-12 h, 45 min,
    pas de 15 min → 9 h 00, 9 h 15 … 11 h 15 (la dernière finit à 12 h). S'ajoutent les ouvertures exceptionnelles.
    Sont retirés : ce qui est trop tôt (« au plus tôt 2 h avant »), trop loin (« au plus tard 2 mois »), les fermetures,
    et les rendez-vous pris + la pause qui les suit (ceux des autres métiers aussi, si le prestataire l'a réglé ainsi)."""
    if prestataire.statut != "actif":
        return []
    if metier_id not in metiers_exerces(db, prestataire, jour):
        return []  # métier arrêté ce jour-là (date d'arrêt passée)
    if jour > ajouter_mois(aujourd_hui(maintenant), prestataire.reservation_delai_max_mois):
        return []
    au_plus_tot = maintenant + timedelta(minutes=prestataire.reservation_delai_min_minutes)
    pas = timedelta(minutes=prestataire.agenda_pas_minutes)
    debut_jour, fin_jour = a_paris(jour, time(0)), a_paris(jour + timedelta(days=1), time(0))
    autres_metiers = prestataire.rendez_vous_bloque_autres_metiers

    # Périodes ouvertes : la semaine type de ce jour + les ouvertures exceptionnelles (qui peuvent déborder sur le
    # lendemain : un service commencé à 23 h 30 dans une ouverture sans arrêt peut finir après minuit), fusionnées.
    ouvertes = [(a_paris(jour, p.debut), a_paris(jour, p.fin))
                for p in plages_de(db, prestataire, metier_id) if p.jour_semaine == jour.isoweekday()]
    ouvertes += [(max(o.debut, debut_jour), o.fin) for o in db.scalars(select(Ouverture).where(
        Ouverture.prestataire_id == prestataire.id, Ouverture.metier_id == metier_id,
        Ouverture.debut < fin_jour, Ouverture.fin > debut_jour,
    ))]
    fenetres: list[tuple[datetime, datetime]] = []
    for de, a in sorted(ouvertes):
        if fenetres and de <= fenetres[-1][1]:
            fenetres[-1] = (fenetres[-1][0], max(fenetres[-1][1], a))
        else:
            fenetres.append((de, a))

    # Fermetures de ce calendrier ; les jours de travaux d'un devis comptent comme un rendez-vous (toute la personne).
    from app.modeles.devis import Devis

    travaux = set(db.scalars(select(Devis.blocage_id).where(Devis.blocage_id.is_not(None))))
    blocages = [
        (b.debut, b.fin) for b in db.scalars(select(Blocage).where(
            Blocage.prestataire_id == prestataire.id, Blocage.debut < fin_jour + duree, Blocage.fin > debut_jour,
        )) if b.metier_id == metier_id or (autres_metiers and b.id in travaux)
    ]
    # Rendez-vous pris (et demandes en attente), avec la pause du prestataire avant et après : un nouveau rendez-vous
    # ne peut ni commencer pendant la pause qui suit, ni finir moins d'une pause avant le suivant.
    pause = timedelta(minutes=prestataire.agenda_pause_minutes)
    pris = db.scalars(select(RendezVous).where(
        RendezVous.prestataire_id == prestataire.id, RendezVous.statut.in_(OCCUPENT_L_AGENDA),
        RendezVous.debut < fin_jour + duree + pause, RendezVous.fin > debut_jour - pause,
    ))
    occupes = blocages + [
        (r.debut - pause, r.fin + pause) for r in pris if autres_metiers or r.metier_id == metier_id
    ]

    libres: list[datetime] = []
    for moment, fin_fenetre in fenetres:
        while moment + duree <= fin_fenetre and moment < fin_jour:
            fin_service = moment + duree
            if moment >= au_plus_tot and not any(moment < f and fin_service > d for d, f in occupes):
                libres.append(moment)
            moment += pas
    return libres
