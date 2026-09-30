"""Adresses des annonces et du local du prestataire (écrans au lot 3.2). Règles : RM-ANNONCES.md."""

from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Response, UploadFile
from pydantic import BaseModel

from app.modeles.annonces import Annonce, Local
from app.modeles.comptes import Compte
from app.modeles.fichiers import Fichier
from app.modeles.metiers import Metier
from app.modeles.prestataires import Commune, Prestataire
from app.routes.dependances import Base, CompteConnecte, CompteOuPersonne, maintenant
from app.routes.prestataires import CommuneVisible, MetierCourt, commune_visible, mon_profil_ou_404
from app.services import annonces as service
from app.services import stockage
from app.services.erreurs import ErreurRegle
from app.services.prestataires import aujourd_hui, metiers_exerces

routeur = APIRouter(prefix="/api")


class LocalDemande(BaseModel):
    ligne: str
    complement: str | None = None
    commune_id: int
    code_postal: str


class LocalVisible(BaseModel):
    ligne: str
    complement: str | None
    code_postal: str
    commune: CommuneVisible


class AnnonceDemande(BaseModel):
    metier_id: int
    titre: str
    forme_prix: str
    lieu: str
    description: str | None = None
    prix_centimes: int | None = None
    duree_minutes: int | None = None
    heures_min: int | None = None
    heures_max: int | None = None
    paiement_carte: bool = False
    paiement_especes: bool = True


class AnnonceVisible(BaseModel):
    """Ce que voit le prestataire dans « Mes annonces »."""

    id: int
    metier: MetierCourt
    titre: str
    description: str | None
    forme_prix: str
    prix_centimes: int | None
    duree_minutes: int | None
    heures_min: int | None
    heures_max: int | None
    lieu: str
    paiement_carte: bool
    paiement_especes: bool
    modes_de_paiement: list[str]
    statut: str
    raison_cachee: str | None
    metier_arrete: bool
    nombre_photos: int
    cree_le: datetime
    modifiee_le: datetime


class AnnoncePublique(BaseModel):
    """Ce que voit un client : la ville, jamais la rue du local (RM-ANNONCES)."""

    id: int
    prestataire: dict
    metier: MetierCourt
    titre: str
    description: str | None
    forme_prix: str
    prix_centimes: int | None
    duree_minutes: int | None
    heures_min: int | None
    heures_max: int | None
    lieu: str
    ville: str
    modes_de_paiement: list[str]
    nombre_photos: int


class ActionAnnonce(BaseModel):
    action: Literal["pause", "retirer", "republier"]


def local_visible(db: Base, local: Local) -> LocalVisible:
    return LocalVisible(ligne=local.ligne, complement=local.complement, code_postal=local.code_postal,
                        commune=commune_visible(db.get_one(Commune, local.commune_id)))


def visible(db: Base, annonce: Annonce, prestataire: Prestataire) -> AnnonceVisible:
    metier = db.get_one(Metier, annonce.metier_id)
    return AnnonceVisible(
        id=annonce.id, metier=MetierCourt(id=metier.id, nom=metier.nom), titre=annonce.titre, description=annonce.description,
        forme_prix=annonce.forme_prix, prix_centimes=annonce.prix_centimes, duree_minutes=annonce.duree_minutes,
        heures_min=annonce.heures_min, heures_max=annonce.heures_max, lieu=annonce.lieu,
        paiement_carte=annonce.paiement_carte, paiement_especes=annonce.paiement_especes,
        modes_de_paiement=service.modes_de_paiement(annonce, prestataire), statut=annonce.statut,
        raison_cachee=service.raison_cachee(db, annonce, prestataire, maintenant()),
        metier_arrete=annonce.metier_id not in metiers_exerces(db, prestataire, aujourd_hui(maintenant())),
        nombre_photos=len(service.photos_de(db, annonce)), cree_le=annonce.cree_le, modifiee_le=annonce.modifiee_le,
    )


def _donnees(d: AnnonceDemande) -> service.DonneesAnnonce:
    return service.DonneesAnnonce(**d.model_dump())


# ---------- Mon local ----------


@routeur.get("/moi/local")
def mon_local(db: Base, compte: CompteConnecte) -> LocalVisible | None:
    local = service.local_de(db, mon_profil_ou_404(db, compte))
    return None if local is None else local_visible(db, local)


@routeur.post("/moi/local")
def enregistrer_local(donnees: LocalDemande, db: Base, compte: CompteConnecte) -> LocalVisible:
    local = service.enregistrer_local(db, mon_profil_ou_404(db, compte), **donnees.model_dump(), maintenant=maintenant())
    db.commit()
    return local_visible(db, local)


@routeur.post("/moi/local/effacer")
def effacer_local(db: Base, compte: CompteConnecte) -> dict[str, str]:
    service.effacer_local(db, mon_profil_ou_404(db, compte), maintenant())
    db.commit()
    return {"message": "L'adresse de votre local est effacée."}


# ---------- Mes annonces ----------


@routeur.get("/moi/annonces")
def mes_annonces(db: Base, compte: CompteConnecte) -> list[AnnonceVisible]:
    prestataire = mon_profil_ou_404(db, compte)
    return [visible(db, a, prestataire) for a in service.annonces_du_prestataire(db, prestataire)]


@routeur.post("/moi/annonces", status_code=201)
def publier(donnees: AnnonceDemande, db: Base, compte: CompteConnecte) -> AnnonceVisible:
    prestataire = mon_profil_ou_404(db, compte)
    annonce = service.publier(db, prestataire, _donnees(donnees), maintenant())
    db.commit()
    return visible(db, annonce, prestataire)


@routeur.post("/moi/annonces/{annonce_id}/modifier")
def modifier(annonce_id: int, donnees: AnnonceDemande, db: Base, compte: CompteConnecte) -> AnnonceVisible:
    prestataire = mon_profil_ou_404(db, compte)
    annonce = service.modifier(db, prestataire, service.annonce_de(db, prestataire, annonce_id), _donnees(donnees), maintenant())
    db.commit()
    return visible(db, annonce, prestataire)


@routeur.post("/moi/annonces/{annonce_id}/statut")
def statut(annonce_id: int, donnees: ActionAnnonce, db: Base, compte: CompteConnecte) -> AnnonceVisible:
    prestataire = mon_profil_ou_404(db, compte)
    annonce = service.changer_statut(db, prestataire, service.annonce_de(db, prestataire, annonce_id), donnees.action, maintenant())
    db.commit()
    return visible(db, annonce, prestataire)


@routeur.post("/moi/annonces/{annonce_id}/photos")
async def ajouter_photo(annonce_id: int, fichier: UploadFile, db: Base, compte: CompteConnecte) -> AnnonceVisible:
    prestataire = mon_profil_ou_404(db, compte)
    annonce = service.annonce_de(db, prestataire, annonce_id)
    service.ajouter_photo(
        db, compte, prestataire, annonce, nom_fichier=fichier.filename or "photo", type_mime=fichier.content_type or "",
        contenu=await fichier.read(), maintenant=maintenant(),
    )
    db.commit()
    return visible(db, annonce, prestataire)


@routeur.post("/moi/annonces/{annonce_id}/photos/{ordre}/retirer")
def retirer_photo(annonce_id: int, ordre: int, db: Base, compte: CompteConnecte) -> AnnonceVisible:
    prestataire = mon_profil_ou_404(db, compte)
    annonce = service.annonce_de(db, prestataire, annonce_id)
    service.retirer_photo(db, prestataire, annonce, ordre, maintenant())
    db.commit()
    return visible(db, annonce, prestataire)


# ---------- Une annonce, pour tous (même sans compte) ----------


def annonce_visible_ou_404(db: Base, annonce_id: int, compte: Compte | None) -> tuple[Annonce, Prestataire]:
    """Une annonce cachée n'existe pas pour les clients ; son auteur la voit quand même (aperçu)."""
    annonce = db.get(Annonce, annonce_id)
    if annonce is None:
        raise ErreurRegle("Cette annonce n'existe pas.", 404)
    prestataire = db.get_one(Prestataire, annonce.prestataire_id)
    auteur = compte is not None and compte.id == prestataire.compte_id
    if not auteur and service.raison_cachee(db, annonce, prestataire, maintenant()) is not None:
        raise ErreurRegle("Cette annonce n'existe pas.", 404)
    return annonce, prestataire


@routeur.get("/annonces/{annonce_id}")
def voir(annonce_id: int, db: Base, compte: CompteOuPersonne) -> AnnoncePublique:
    annonce, prestataire = annonce_visible_ou_404(db, annonce_id, compte)
    return annonce_publique(db, annonce, prestataire)


def annonce_publique(db: Base, annonce: Annonce, prestataire: Prestataire) -> AnnoncePublique:
    """Une annonce telle que la voit un client (aussi sur la page publique du prestataire)."""
    metier = db.get_one(Metier, annonce.metier_id)
    local = service.local_de(db, prestataire)
    commune_id = local.commune_id if annonce.lieu == "chez_moi" and local else prestataire.commune_id
    return AnnoncePublique(
        id=annonce.id,
        prestataire={"id": prestataire.id, "nom_affiche": prestataire.nom_affiche, "a_une_photo": prestataire.photo_id is not None},
        metier=MetierCourt(id=metier.id, nom=metier.nom), titre=annonce.titre, description=annonce.description,
        forme_prix=annonce.forme_prix, prix_centimes=annonce.prix_centimes, duree_minutes=annonce.duree_minutes,
        heures_min=annonce.heures_min, heures_max=annonce.heures_max, lieu=annonce.lieu,
        ville=db.get_one(Commune, commune_id).nom, modes_de_paiement=service.modes_de_paiement(annonce, prestataire),
        nombre_photos=len(service.photos_de(db, annonce)),
    )


@routeur.get("/annonces/{annonce_id}/photos/{ordre}")
def voir_photo(annonce_id: int, ordre: int, db: Base, compte: CompteOuPersonne) -> Response:
    annonce, _ = annonce_visible_ou_404(db, annonce_id, compte)
    photo = next((p for p in service.photos_de(db, annonce) if p.ordre == ordre), None)
    if photo is None:
        raise ErreurRegle("Pas de photo.", 404)
    fichier = db.get_one(Fichier, photo.fichier_id)
    return Response(content=stockage.lire(fichier.cle_stockage), media_type=fichier.type_mime)
