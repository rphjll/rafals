"""Adresses de l'agenda du prestataire et de ses horaires libres (écrans au lot 3.4). Règles : RM-AGENDA.md."""

from datetime import date, datetime, time, timedelta
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from app.modeles.prestataires import Prestataire
from app.routes.dependances import Base, CompteConnecte, maintenant
from app.routes.prestataires import mon_profil_ou_404
from app.services import agenda as service
from app.services.erreurs import ErreurRegle

routeur = APIRouter(prefix="/api")


class PlageDemande(BaseModel):
    jour_semaine: int
    debut: time
    fin: time


class Semaine(BaseModel):
    metier_id: int | None = None  # le calendrier concerné ; rien = métier principal
    plages: list[PlageDemande]
    rendez_vous: Literal["annuler", "garder"] | None = None  # si des rendez-vous tombent hors des nouveaux horaires


class BlocageDemande(BaseModel):
    """Sans fuseau, lu à l'heure de Paris : ex. « 2026-08-04T00:00 » → « 2026-08-25T00:00 » pour des congés."""

    metier_id: int | None = None  # le calendrier concerné ; rien = métier principal
    debut: datetime
    fin: datetime
    motif: str | None = None
    rendez_vous: Literal["annuler", "garder"] | None = None  # si des rendez-vous tombent pendant la période


class OuvertureDemande(BaseModel):
    """Ouverture exceptionnelle, sans fuseau = heure de Paris : ex. « 2026-10-18T10:00 » → « 2026-10-18T13:00 »."""

    metier_id: int | None = None
    debut: datetime
    fin: datetime
    motif: str | None = None


class Retrait(BaseModel):
    rendez_vous: Literal["annuler", "garder"] | None = None  # si des rendez-vous ont été pris pendant l'ouverture


class BlocageVisible(BaseModel):
    id: int
    debut: datetime
    fin: datetime
    motif: str | None


class Reglages(BaseModel):
    pas_minutes: int
    pause_minutes: int
    delai_min_minutes: int
    delai_max_mois: int
    rendez_vous_bloque_autres_metiers: bool | None = None  # à l'envoi : rien = inchangé


class AgendaVisible(BaseModel):
    """Le calendrier d'un métier : sa semaine type, ses fermetures (blocages) et ses ouvertures exceptionnelles."""

    metier_id: int
    plages: list[PlageDemande]
    blocages: list[BlocageVisible]
    ouvertures: list[BlocageVisible]
    reglages: Reglages


class Horaires(BaseModel):
    jour: date
    duree_minutes: int
    debuts: list[datetime]


def agenda_visible(db: Base, prestataire: Prestataire, metier_id: int | None = None) -> AgendaVisible:
    metier_id = service.metier_du_calendrier(db, prestataire, metier_id)
    return AgendaVisible(
        metier_id=metier_id,
        plages=[PlageDemande(jour_semaine=p.jour_semaine, debut=p.debut, fin=p.fin)
                for p in service.plages_de(db, prestataire, metier_id)],
        blocages=[BlocageVisible(id=b.id, debut=b.debut, fin=b.fin, motif=b.motif)
                  for b in service.blocages_a_venir(db, prestataire, metier_id, maintenant())],
        ouvertures=[BlocageVisible(id=o.id, debut=o.debut, fin=o.fin, motif=o.motif)
                    for o in service.ouvertures_a_venir(db, prestataire, metier_id, maintenant())],
        reglages=Reglages(pas_minutes=prestataire.agenda_pas_minutes, pause_minutes=prestataire.agenda_pause_minutes,
                          delai_min_minutes=prestataire.reservation_delai_min_minutes,
                          delai_max_mois=prestataire.reservation_delai_max_mois,
                          rendez_vous_bloque_autres_metiers=prestataire.rendez_vous_bloque_autres_metiers),
    )


# ---------- Mon agenda ----------


@routeur.get("/moi/agenda")
def mon_agenda(db: Base, compte: CompteConnecte, metier_id: int | None = None) -> AgendaVisible:
    """Ex. /api/moi/agenda?metier_id=12 : le calendrier de ce métier ; sans rien, celui du métier principal."""
    return agenda_visible(db, mon_profil_ou_404(db, compte), metier_id)


@routeur.post("/moi/agenda/semaine")
def semaine(donnees: Semaine, db: Base, compte: CompteConnecte) -> AgendaVisible:
    prestataire = mon_profil_ou_404(db, compte)
    service.remplacer_semaine(db, prestataire, [service.Plage(**p.model_dump()) for p in donnees.plages], maintenant(),
                              donnees.rendez_vous, donnees.metier_id)
    db.commit()
    return agenda_visible(db, prestataire, donnees.metier_id)


@routeur.post("/moi/agenda/blocages")
def bloquer(donnees: BlocageDemande, db: Base, compte: CompteConnecte) -> AgendaVisible:
    prestataire = mon_profil_ou_404(db, compte)
    service.bloquer(db, prestataire, **donnees.model_dump(), maintenant=maintenant())
    db.commit()
    return agenda_visible(db, prestataire, donnees.metier_id)


@routeur.post("/moi/agenda/blocages/{blocage_id}/retirer")
def debloquer(blocage_id: int, db: Base, compte: CompteConnecte) -> AgendaVisible:
    prestataire = mon_profil_ou_404(db, compte)
    metier_id = service.debloquer(db, prestataire, blocage_id, maintenant())
    db.commit()
    return agenda_visible(db, prestataire, metier_id)


@routeur.post("/moi/agenda/ouvertures")
def ouvrir(donnees: OuvertureDemande, db: Base, compte: CompteConnecte) -> AgendaVisible:
    prestataire = mon_profil_ou_404(db, compte)
    service.ouvrir(db, prestataire, **donnees.model_dump(), maintenant=maintenant())
    db.commit()
    return agenda_visible(db, prestataire, donnees.metier_id)


@routeur.post("/moi/agenda/ouvertures/{ouverture_id}/retirer")
def retirer_ouverture(ouverture_id: int, db: Base, compte: CompteConnecte, donnees: Retrait | None = None) -> AgendaVisible:
    prestataire = mon_profil_ou_404(db, compte)
    metier_id = service.retirer_ouverture(db, prestataire, ouverture_id, maintenant(), donnees.rendez_vous if donnees else None)
    db.commit()
    return agenda_visible(db, prestataire, metier_id)


@routeur.post("/moi/agenda/reglages")
def reglages(donnees: Reglages, db: Base, compte: CompteConnecte) -> AgendaVisible:
    prestataire = mon_profil_ou_404(db, compte)
    service.modifier_reglages(db, prestataire, **donnees.model_dump(), maintenant=maintenant())
    db.commit()
    return agenda_visible(db, prestataire)


# ---------- Horaires libres d'un de ses calendriers (pour le prestataire) ----------


@routeur.get("/moi/agenda/horaires")
def horaires(jour: date, duree_minutes: int, db: Base, compte: CompteConnecte, metier_id: int | None = None) -> Horaires:
    """Ex. /api/moi/agenda/horaires?jour=2026-10-14&duree_minutes=45 : les heures de début libres ce jour-là dans un de
    ses calendriers (sans metier_id : celui du métier principal). Pour le prestataire seulement : le client ne voit
    plus les horaires libres (RM-AGENDA § « Sans annonces »)."""
    prestataire = mon_profil_ou_404(db, compte)
    if not 1 <= duree_minutes <= 24 * 60:
        raise ErreurRegle("La durée doit faire entre 1 minute et 24 heures.")
    metier = service.metier_du_calendrier(db, prestataire, metier_id)
    return Horaires(jour=jour, duree_minutes=duree_minutes,
                    debuts=service.horaires_libres(db, prestataire, metier, timedelta(minutes=duree_minutes), jour, maintenant()))

