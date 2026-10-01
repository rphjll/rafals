"""Adresses de l'agenda du prestataire et des horaires libres d'une annonce (écrans au lot 3.4). Règles : RM-AGENDA.md."""

from datetime import date, datetime, time
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from app.modeles.prestataires import Prestataire
from app.routes.annonces import annonce_visible_ou_404
from app.routes.dependances import Base, CompteConnecte, CompteOuPersonne, maintenant
from app.routes.prestataires import mon_profil_ou_404
from app.services import agenda as service

routeur = APIRouter(prefix="/api")


class PlageDemande(BaseModel):
    jour_semaine: int
    debut: time
    fin: time


class Semaine(BaseModel):
    plages: list[PlageDemande]
    rendez_vous: Literal["annuler", "garder"] | None = None  # si des rendez-vous tombent hors des nouveaux horaires


class BlocageDemande(BaseModel):
    """Sans fuseau, lu à l'heure de Paris : ex. « 2026-08-04T00:00 » → « 2026-08-25T00:00 » pour des congés."""

    debut: datetime
    fin: datetime
    motif: str | None = None
    rendez_vous: Literal["annuler", "garder"] | None = None  # si des rendez-vous tombent pendant la période


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


class AgendaVisible(BaseModel):
    plages: list[PlageDemande]
    blocages: list[BlocageVisible]
    reglages: Reglages


class Horaires(BaseModel):
    jour: date
    duree_minutes: int
    debuts: list[datetime]


def agenda_visible(db: Base, prestataire: Prestataire) -> AgendaVisible:
    return AgendaVisible(
        plages=[PlageDemande(jour_semaine=p.jour_semaine, debut=p.debut, fin=p.fin) for p in service.plages_de(db, prestataire)],
        blocages=[BlocageVisible(id=b.id, debut=b.debut, fin=b.fin, motif=b.motif)
                  for b in service.blocages_a_venir(db, prestataire, maintenant())],
        reglages=Reglages(pas_minutes=prestataire.agenda_pas_minutes, pause_minutes=prestataire.agenda_pause_minutes,
                          delai_min_minutes=prestataire.reservation_delai_min_minutes,
                          delai_max_mois=prestataire.reservation_delai_max_mois),
    )


# ---------- Mon agenda ----------


@routeur.get("/moi/agenda")
def mon_agenda(db: Base, compte: CompteConnecte) -> AgendaVisible:
    return agenda_visible(db, mon_profil_ou_404(db, compte))


@routeur.post("/moi/agenda/semaine")
def semaine(donnees: Semaine, db: Base, compte: CompteConnecte) -> AgendaVisible:
    prestataire = mon_profil_ou_404(db, compte)
    service.remplacer_semaine(db, prestataire, [service.Plage(**p.model_dump()) for p in donnees.plages], maintenant(),
                              donnees.rendez_vous)
    db.commit()
    return agenda_visible(db, prestataire)


@routeur.post("/moi/agenda/blocages")
def bloquer(donnees: BlocageDemande, db: Base, compte: CompteConnecte) -> AgendaVisible:
    prestataire = mon_profil_ou_404(db, compte)
    service.bloquer(db, prestataire, **donnees.model_dump(), maintenant=maintenant())
    db.commit()
    return agenda_visible(db, prestataire)


@routeur.post("/moi/agenda/blocages/{blocage_id}/retirer")
def debloquer(blocage_id: int, db: Base, compte: CompteConnecte) -> AgendaVisible:
    prestataire = mon_profil_ou_404(db, compte)
    service.debloquer(db, prestataire, blocage_id, maintenant())
    db.commit()
    return agenda_visible(db, prestataire)


@routeur.post("/moi/agenda/reglages")
def reglages(donnees: Reglages, db: Base, compte: CompteConnecte) -> AgendaVisible:
    prestataire = mon_profil_ou_404(db, compte)
    service.modifier_reglages(db, prestataire, **donnees.model_dump(), maintenant=maintenant())
    db.commit()
    return agenda_visible(db, prestataire)


# ---------- Horaires libres d'une annonce (pour tous) ----------


@routeur.get("/annonces/{annonce_id}/horaires")
def horaires(annonce_id: int, jour: date, db: Base, compte: CompteOuPersonne, heures: int | None = None) -> Horaires:
    """Ex. /api/annonces/12/horaires?jour=2026-10-14 ; à l'heure : &heures=3. Seulement les horaires libres, jamais
    les autres rendez-vous ni la raison d'un blocage (RM-AGENDA, « Ce que voit le client »)."""
    annonce, prestataire = annonce_visible_ou_404(db, annonce_id, compte)
    duree = service.duree_reservee(annonce, heures)
    return Horaires(jour=jour, duree_minutes=int(duree.total_seconds() // 60),
                    debuts=service.horaires_libres(db, prestataire, annonce, jour, maintenant(), heures))

