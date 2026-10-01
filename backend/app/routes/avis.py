"""Adresses des avis : le client, le prestataire, l'administrateur, et les avis publics (écrans au lot 4.8).
Règles : RM-AVIS.md."""

from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

from app.modeles.avis import Avis
from app.modeles.prestataires import Prestataire
from app.modeles.rendez_vous import RendezVous
from app.routes.dependances import Administrateur, Base, CompteConnecte, CompteOuPersonne, maintenant
from app.routes.prestataires import mon_profil_ou_404
from app.routes.recherche import prestataire_visible_ou_404
from app.services import avis as service
from app.services import rendez_vous as service_rdv

routeur = APIRouter(prefix="/api")


class AvisDemande(BaseModel):
    note: int
    texte: str


class Texte(BaseModel):
    texte: str


class Decision(BaseModel):
    cacher: bool
    motif: str | None = None


class Mot(BaseModel):
    mot: str


class AvisPublic(BaseModel):
    """Ce que voit tout le monde : « ★★★★★ Marie D., octobre 2026 : … » et la réponse du prestataire."""

    id: int
    note: int
    texte: str
    auteur: str
    mois: str
    reponse: str | None


class AvisDetaille(AvisPublic):
    """Ce que voient son auteur et le prestataire concerné : en plus, les états."""

    rendez_vous_id: int
    modifiable_jusqu_au: datetime
    retire: bool
    cache_motif: str | None
    signale: bool


class AvisSignale(BaseModel):
    avis: AvisPublic
    prestataire: str
    signalement: str
    signale_le: datetime


class MotVisible(BaseModel):
    id: int
    mot: str


def public(db: Base, a: Avis) -> AvisPublic:
    return AvisPublic(id=a.id, note=a.note, texte=a.texte, auteur=service.auteur(db, a), mois=service.mois(a.cree_le),
                      reponse=a.reponse)


def detaille(db: Base, a: Avis) -> AvisDetaille:
    rdv = db.get_one(RendezVous, a.rendez_vous_id)
    return AvisDetaille(**public(db, a).model_dump(), rendez_vous_id=rdv.id, modifiable_jusqu_au=service.limite(rdv),
                        retire=a.retire_le is not None, cache_motif=a.cache_motif, signale=a.signale_le is not None)


# ---------- Pour tous ----------


@routeur.get("/prestataires/{prestataire_id}/avis")
def avis_d_un_prestataire(prestataire_id: int, db: Base, compte: CompteOuPersonne) -> list[AvisPublic]:
    """Les avis visibles (ni retirés, ni cachés), les plus récents d'abord ; comme sa page, cachés si l'activité ne l'est pas."""
    prestataire_visible_ou_404(db, prestataire_id, compte)
    return [public(db, a) for a in service.visibles(db, prestataire_id)]


# ---------- Le client ----------


@routeur.post("/moi/rendez-vous/{rdv_id}/avis", status_code=201)
def laisser(rdv_id: int, donnees: AvisDemande, db: Base, compte: CompteConnecte) -> AvisDetaille:
    rdv = service_rdv.rendez_vous_du_client(db, compte, rdv_id)
    a = service.laisser(db, compte, rdv, donnees.note, donnees.texte, maintenant())
    db.commit()
    return detaille(db, a)


@routeur.post("/moi/avis/{avis_id}/modifier")
def modifier(avis_id: int, donnees: AvisDemande, db: Base, compte: CompteConnecte) -> AvisDetaille:
    a = service.modifier(db, compte, avis_id, donnees.note, donnees.texte, maintenant())
    db.commit()
    return detaille(db, a)


@routeur.post("/moi/avis/{avis_id}/retirer")
def retirer(avis_id: int, db: Base, compte: CompteConnecte) -> AvisDetaille:
    a = service.retirer(db, compte, avis_id, maintenant())
    db.commit()
    return detaille(db, a)


# ---------- Le prestataire ----------


@routeur.post("/moi/prestataire/avis/{avis_id}/repondre")
def repondre(avis_id: int, donnees: Texte, db: Base, compte: CompteConnecte) -> AvisDetaille:
    a = service.repondre(db, mon_profil_ou_404(db, compte), avis_id, donnees.texte, maintenant())
    db.commit()
    return detaille(db, a)


@routeur.post("/moi/prestataire/avis/{avis_id}/signaler")
def signaler(avis_id: int, donnees: Texte, db: Base, compte: CompteConnecte) -> AvisDetaille:
    a = service.signaler(db, mon_profil_ou_404(db, compte), avis_id, donnees.texte, maintenant())
    db.commit()
    return detaille(db, a)


# ---------- L'administrateur ----------


@routeur.get("/admin/avis-signales")
def avis_signales(db: Base, _admin: Administrateur) -> list[AvisSignale]:
    return [AvisSignale(avis=public(db, a), prestataire=db.get_one(Prestataire, a.prestataire_id).nom_affiche,
                        signalement=a.signalement or "", signale_le=a.signale_le or a.cree_le)
            for a in service.avis_signales(db)]


@routeur.post("/admin/avis/{avis_id}/decision")
def decider(avis_id: int, donnees: Decision, db: Base, admin: Administrateur) -> dict[str, bool]:
    a = service.decider(db, admin, avis_id, donnees.cacher, donnees.motif, maintenant())
    db.commit()
    return {"cache": a.cache_le is not None}


@routeur.get("/admin/mots-interdits")
def mots(db: Base, _admin: Administrateur) -> list[MotVisible]:
    return [MotVisible(id=m.id, mot=m.mot) for m in service.mots_interdits(db)]


@routeur.post("/admin/mots-interdits", status_code=201)
def ajouter_mot(donnees: Mot, db: Base, admin: Administrateur) -> MotVisible:
    m = service.ajouter_mot(db, admin, donnees.mot, maintenant())
    db.commit()
    return MotVisible(id=m.id, mot=m.mot)


@routeur.post("/admin/mots-interdits/{mot_id}/retirer")
def retirer_mot(mot_id: int, db: Base, admin: Administrateur) -> dict[str, str]:
    service.retirer_mot(db, admin, mot_id, maintenant())
    db.commit()
    return {"message": "Mot retiré de la liste."}

