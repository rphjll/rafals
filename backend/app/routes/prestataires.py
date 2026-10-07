"""Adresses du profil prestataire, des communes et de l'administration des prestataires (écrans au lot 2.5)."""

from datetime import date, datetime
from typing import Literal

from fastapi import APIRouter, Response, UploadFile
from pydantic import BaseModel
from sqlalchemy import select

from app.modeles.comptes import Compte
from app.modeles.fichiers import Fichier
from app.modeles.metiers import Metier
from app.modeles.prestataires import Commune, Prestataire
from app.routes.dependances import Administrateur, Base, CompteConnecte, CompteOuPersonne, maintenant
from app.services import communes as service_communes
from app.services import prestataires as service
from app.services import stockage
from app.services.erreurs import ErreurRegle

routeur = APIRouter(prefix="/api")


class CommuneVisible(BaseModel):
    id: int
    nom: str
    codes_postaux: list[str]
    departement: str


class ProfilDemande(BaseModel):
    nom_affiche: str
    metier_principal_id: int
    commune_id: int
    distance_km: int
    presentation: str | None = None
    siret: str | None = None
    metiers_secondaires: list[int] = []


class MetierCourt(BaseModel):
    id: int
    nom: str


class MetierExerce(BaseModel):
    id: int
    nom: str
    fin_le: date | None = None


class ProfilVisible(BaseModel):
    id: int
    nom_affiche: str
    presentation: str | None
    metier_principal: MetierExerce
    metier_principal_suivant: MetierCourt | None
    metiers_secondaires: list[MetierExerce]
    metiers_arretes: list[MetierExerce]
    commune: CommuneVisible
    distance_km: int
    siret: str | None
    siret_statut: str
    statut: str
    a_une_photo: bool
    photos: list[int]  # rangs des photos de son travail, ex. [1, 2, 3] → /api/prestataires/12/photos/1
    cree_le: datetime
    facture_tva: bool  # case « Je facture la TVA » (lot 5.3, RM-DEVIS)


class FinMetier(BaseModel):
    metier_id: int
    fin_le: date | None = None
    suivant_id: int | None = None


class ActionStatut(BaseModel):
    action: Literal["pause", "reprendre", "arreter"]


class Blocage(BaseModel):
    bloque: bool


class PrestataireAdministre(BaseModel):
    id: int
    nom_affiche: str
    metier_principal: str
    commune: str
    siret_statut: str
    statut: str
    email_compte: str
    cree_le: datetime


def commune_visible(commune: Commune) -> CommuneVisible:
    return CommuneVisible(id=commune.id, nom=commune.nom, codes_postaux=commune.codes_postaux, departement=commune.departement)


def visible(db: Base, prestataire: Prestataire) -> ProfilVisible:
    """Métiers secondaires encore exercés (avec leur date de fin éventuelle) et métiers arrêtés (date de fin passée)."""
    jour = service.aujourd_hui(maintenant())
    principal = db.get_one(Metier, prestataire.metier_principal_id)
    suivant = db.get(Metier, prestataire.metier_principal_suivant_id) if prestataire.metier_principal_suivant_id else None
    lignes = [(ligne, db.get_one(Metier, ligne.metier_id)) for ligne in service.lignes_secondaires(db, prestataire)]
    return ProfilVisible(
        id=prestataire.id,
        nom_affiche=prestataire.nom_affiche,
        presentation=prestataire.presentation,
        metier_principal=MetierExerce(id=principal.id, nom=principal.nom, fin_le=prestataire.metier_principal_fin_le),
        metier_principal_suivant=MetierCourt(id=suivant.id, nom=suivant.nom) if suivant else None,
        metiers_secondaires=[
            MetierExerce(id=m.id, nom=m.nom, fin_le=ligne.fin_le) for ligne, m in lignes if service.en_cours(ligne.fin_le, jour)
        ],
        metiers_arretes=[
            MetierExerce(id=m.id, nom=m.nom, fin_le=ligne.fin_le) for ligne, m in lignes if not service.en_cours(ligne.fin_le, jour)
        ],
        commune=commune_visible(db.get_one(Commune, prestataire.commune_id)),
        distance_km=prestataire.distance_km,
        siret=prestataire.siret,
        siret_statut=prestataire.siret_statut,
        statut=prestataire.statut,
        a_une_photo=prestataire.photo_id is not None,
        photos=[p.ordre for p in service.photos_de(db, prestataire.id)],
        cree_le=prestataire.cree_le,
        facture_tva=prestataire.facture_tva,
    )


def mon_profil_ou_404(db: Base, compte: Compte) -> Prestataire:
    prestataire = service.profil_de(db, compte)
    if prestataire is None:
        raise ErreurRegle("Vous ne proposez pas encore vos services.", 404)
    return prestataire


# ---------- Communes (pour tous) ----------


@routeur.get("/communes/recherche")
def communes(q: str, db: Base) -> list[CommuneVisible]:
    return [commune_visible(c) for c in service_communes.rechercher(db, q)]


# ---------- Mon profil de prestataire ----------


@routeur.get("/moi/prestataire")
def mon_profil(db: Base, compte: CompteConnecte) -> ProfilVisible:
    return visible(db, mon_profil_ou_404(db, compte))


@routeur.post("/moi/prestataire", status_code=201)
def devenir(donnees: ProfilDemande, db: Base, compte: CompteConnecte) -> ProfilVisible:
    prestataire = service.devenir_prestataire(db, compte, service.Profil(**donnees.model_dump()), maintenant())
    db.commit()
    return visible(db, prestataire)


@routeur.post("/moi/prestataire/modifier")
def modifier(donnees: ProfilDemande, db: Base, compte: CompteConnecte) -> ProfilVisible:
    prestataire = service.modifier_profil(db, mon_profil_ou_404(db, compte), service.Profil(**donnees.model_dump()), maintenant())
    db.commit()
    return visible(db, prestataire)


@routeur.post("/moi/prestataire/photo")
async def photo(fichier: UploadFile, db: Base, compte: CompteConnecte) -> ProfilVisible:
    prestataire = service.deposer_photo(
        db, compte, mon_profil_ou_404(db, compte),
        nom_fichier=fichier.filename or "photo", type_mime=fichier.content_type or "",
        contenu=await fichier.read(), maintenant=maintenant(),
    )
    db.commit()
    return visible(db, prestataire)


@routeur.post("/moi/prestataire/metiers/fin")
def fin_metier(donnees: FinMetier, db: Base, compte: CompteConnecte) -> ProfilVisible:
    """Date de fin d'un métier (vide = l'enlever, ou reprendre un métier arrêté) : RM-ANNONCES."""
    prestataire = service.fixer_fin_metier(
        db, mon_profil_ou_404(db, compte), donnees.metier_id, donnees.fin_le, donnees.suivant_id, maintenant()
    )
    db.commit()
    return visible(db, prestataire)


@routeur.post("/moi/prestataire/statut")
def statut(donnees: ActionStatut, db: Base, compte: CompteConnecte) -> ProfilVisible:
    prestataire = service.changer_statut(db, mon_profil_ou_404(db, compte), donnees.action, maintenant())
    db.commit()
    return visible(db, prestataire)


# ---------- Photo d'un prestataire (pour tous : elle sera montrée sur ses annonces) ----------


@routeur.post("/moi/prestataire/photos")
async def ajouter_photo_travail(fichier: UploadFile, db: Base, compte: CompteConnecte) -> ProfilVisible:
    """Une photo de son travail de plus (10 au plus), montrée sur son profil et sur sa carte."""
    prestataire = mon_profil_ou_404(db, compte)
    service.ajouter_photo_travail(
        db, compte, prestataire, nom_fichier=fichier.filename or "photo", type_mime=fichier.content_type or "",
        contenu=await fichier.read(), maintenant=maintenant(),
    )
    db.commit()
    return visible(db, prestataire)


@routeur.post("/moi/prestataire/photos/{ordre}/retirer")
def retirer_photo_travail(ordre: int, db: Base, compte: CompteConnecte) -> ProfilVisible:
    prestataire = mon_profil_ou_404(db, compte)
    service.retirer_photo_travail(db, prestataire, ordre, maintenant())
    db.commit()
    return visible(db, prestataire)


@routeur.get("/prestataires/{prestataire_id}/photos/{ordre}")
def voir_photo_travail(prestataire_id: int, ordre: int, db: Base, compte: CompteOuPersonne) -> Response:
    """Pour tous, comme la page publique : cachée si l'activité est en pause, arrêtée ou bloquée (sauf pour son auteur)."""
    prestataire = db.get(Prestataire, prestataire_id)
    auteur = prestataire is not None and compte is not None and compte.id == prestataire.compte_id
    photo = next((p for p in service.photos_de(db, prestataire_id) if p.ordre == ordre), None)
    if prestataire is None or photo is None or not (auteur or prestataire.statut == "actif"):
        raise ErreurRegle("Cette photo n'existe pas.", 404)
    fichier = db.get_one(Fichier, photo.fichier_id)
    return Response(content=stockage.lire(fichier.cle_stockage), media_type=fichier.type_mime)


@routeur.get("/prestataires/{prestataire_id}/photo")
def voir_photo(prestataire_id: int, db: Base) -> Response:
    prestataire = db.get(Prestataire, prestataire_id)
    if prestataire is None or prestataire.photo_id is None:
        raise ErreurRegle("Pas de photo.", 404)
    fichier = db.get_one(Fichier, prestataire.photo_id)
    return Response(content=stockage.lire(fichier.cle_stockage), media_type=fichier.type_mime)


# ---------- Administrateur ----------


@routeur.get("/admin/prestataires")
def prestataires(db: Base, _admin: Administrateur) -> list[PrestataireAdministre]:
    lignes = db.execute(
        select(Prestataire, Compte, Metier, Commune)
        .join(Compte, Compte.id == Prestataire.compte_id)
        .join(Metier, Metier.id == Prestataire.metier_principal_id)
        .join(Commune, Commune.id == Prestataire.commune_id)
        .order_by(Prestataire.cree_le.desc())
    ).all()
    return [
        PrestataireAdministre(
            id=p.id, nom_affiche=p.nom_affiche, metier_principal=m.nom, commune=c.nom, siret_statut=p.siret_statut,
            statut=p.statut, email_compte=compte.email, cree_le=p.cree_le,
        )
        for p, compte, m, c in lignes
    ]


@routeur.post("/admin/prestataires/{prestataire_id}/siret-valide")
def valider_siret(prestataire_id: int, db: Base, admin: Administrateur) -> dict[str, str]:
    prestataire = service.valider_siret_a_la_main(db, admin, prestataire_id, maintenant())
    db.commit()
    return {"siret_statut": prestataire.siret_statut}


@routeur.post("/admin/prestataires/{prestataire_id}/blocage")
def blocage(prestataire_id: int, donnees: Blocage, db: Base, admin: Administrateur) -> dict[str, str]:
    prestataire = service.bloquer(db, admin, prestataire_id, bloque=donnees.bloque, maintenant=maintenant())
    db.commit()
    return {"statut": prestataire.statut}
