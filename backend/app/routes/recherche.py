"""Adresses de la recherche et de la page publique d'un prestataire (écrans au lot 4.2). Règles : RM-RECHERCHE.md."""

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import select

from app.modeles.annonces import Annonce
from app.modeles.comptes import Compte
from app.modeles.metiers import Metier
from app.modeles.prestataires import Commune, Prestataire
from app.routes.annonces import AnnoncePublique, annonce_publique
from app.routes.dependances import Base, CompteOuPersonne, maintenant
from app.routes.prestataires import CommuneVisible, MetierCourt, commune_visible
from app.services import absences
from app.services import avis as service_avis
from app.services import recherche as service
from app.services.annonces import modes_de_paiement, raison_cachee
from app.services.erreurs import ErreurRegle
from app.services.prestataires import aujourd_hui, metiers_exerces

routeur = APIRouter(prefix="/api")


class CarteResultat(BaseModel):
    """Une carte par prestataire (RM-RECHERCHE) : jamais son téléphone, son mail ni la rue de son local."""

    prestataire_id: int
    nom_affiche: str
    a_une_photo: bool
    ville: str
    distance_km: int
    principal: bool
    note: float | None
    nombre_avis: int
    nouveau: bool
    a_partir_de_centimes: int | None
    a_partir_de_par_heure: bool
    nombre_annonces: int
    vient_chez_vous: bool
    carte_possible: bool


class PageResultats(BaseModel):
    metier: MetierCourt
    ville: CommuneVisible
    total: int
    page: int
    pages: int
    resultats: list[CarteResultat]
    metiers_voisins: list[MetierCourt]


class PrestatairePublic(BaseModel):
    id: int
    nom_affiche: str
    presentation: str | None
    a_une_photo: bool
    ville: str
    distance_km: int
    metiers: list[MetierCourt]
    siret_verifie: bool
    note: float | None
    nombre_avis: int
    absences: int  # « 1 absence sans prévenir » en 6 mois (RM-RENDEZ-VOUS)
    annonces: list[AnnoncePublique]


def carte(r: service.Resultat) -> CarteResultat:
    moins_cher = r.a_partir_de
    return CarteResultat(
        prestataire_id=r.prestataire.id, nom_affiche=r.prestataire.nom_affiche, a_une_photo=r.prestataire.photo_id is not None,
        ville=r.commune.nom, distance_km=round(r.distance_km), principal=r.principal, note=r.note, nombre_avis=r.nombre_avis,
        nouveau=r.nouveau, a_partir_de_centimes=moins_cher.prix_centimes if moins_cher else None,
        a_partir_de_par_heure=bool(moins_cher and moins_cher.forme_prix == "heure"), nombre_annonces=len(r.annonces),
        vient_chez_vous=any(a.lieu in ("chez_client", "les_deux") for a in r.annonces),
        carte_possible=any("carte" in modes_de_paiement(a, r.prestataire) for a in r.annonces),
    )


@routeur.get("/recherche")
def rechercher(
    metier_id: int, commune_id: int, db: Base, tri: str = "note", page: int = 1, vient_chez_moi: bool = False,
    carte_bancaire: bool = False, libre_7_jours: bool = False, prix_max: float | None = None,
) -> PageResultats:
    """Ex. /api/recherche?metier_id=3&commune_id=33522&carte_bancaire=true&prix_max=60 (prix en euros). Ouvert à tous."""
    filtres = service.Filtres(
        vient_chez_moi=vient_chez_moi, carte=carte_bancaire, libre_7_jours=libre_7_jours,
        prix_max_centimes=None if prix_max is None else round(prix_max * 100),
    )
    resultat = service.rechercher(
        db, metier_id=metier_id, commune_id=commune_id, maintenant=maintenant(), filtres=filtres, tri=tri, page=page
    )
    metier = db.get_one(Metier, metier_id)
    return PageResultats(
        metier=MetierCourt(id=metier.id, nom=metier.nom), ville=commune_visible(db.get_one(Commune, commune_id)),
        total=resultat.total,
        page=resultat.page, pages=resultat.pages, resultats=[carte(r) for r in resultat.resultats],
        metiers_voisins=[MetierCourt(id=m.id, nom=m.nom) for m in resultat.metiers_voisins],
    )


def prestataire_visible_ou_404(db: Base, prestataire_id: int, compte: Compte | None) -> Prestataire:
    """Page publique (et ses avis) : visible si l'activité est active ; son auteur la voit toujours (aperçu)."""
    prestataire = db.get(Prestataire, prestataire_id)
    auteur = prestataire is not None and compte is not None and compte.id == prestataire.compte_id
    if prestataire is None or not (auteur or service.page_publique_visible(prestataire)):
        raise ErreurRegle("Ce prestataire n'existe pas.", 404)
    return prestataire


@routeur.get("/prestataires/{prestataire_id}")
def page_publique(prestataire_id: int, db: Base, compte: CompteOuPersonne) -> PrestatairePublic:
    """Profil, note et annonces en ligne d'un prestataire."""
    prestataire = prestataire_visible_ou_404(db, prestataire_id, compte)
    maintenant_ = maintenant()
    annonces = [
        a for a in db.scalars(select(Annonce).where(Annonce.prestataire_id == prestataire.id).order_by(Annonce.cree_le))
        if raison_cachee(db, a, prestataire, maintenant_) is None
    ]
    metiers = [db.get_one(Metier, i) for i in metiers_exerces(db, prestataire, aujourd_hui(maintenant_))]
    somme, nombre = service_avis.notes(db, [prestataire.id]).get(prestataire.id, (0, 0))
    note = somme / nombre if nombre else None
    return PrestatairePublic(
        id=prestataire.id, nom_affiche=prestataire.nom_affiche, presentation=prestataire.presentation,
        a_une_photo=prestataire.photo_id is not None, ville=db.get_one(Commune, prestataire.commune_id).nom,
        distance_km=prestataire.distance_km, metiers=[MetierCourt(id=m.id, nom=m.nom) for m in metiers],
        siret_verifie=prestataire.siret_statut == "verifie", note=note, nombre_avis=nombre,
        absences=len(absences.absences_du_prestataire(db, prestataire.id, maintenant_)),
        annonces=[annonce_publique(db, a, prestataire) for a in annonces],
    )
