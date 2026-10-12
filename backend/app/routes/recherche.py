"""Adresses de la recherche et de la page publique d'un prestataire (écrans au lot 4.2). Règles : RM-RECHERCHE.md."""

from fastapi import APIRouter
from pydantic import BaseModel

from app import reglages
from app.modeles.comptes import Compte
from app.modeles.metiers import Metier
from app.modeles.prestataires import Commune, Prestataire
from app.routes.dependances import Base, CompteOuPersonne, maintenant
from app.routes.prestataires import CommuneVisible, MetierCourt, commune_visible
from app.services import absences
from app.services import avis as service_avis
from app.services import prestataires as service_prestataires
from app.services import recherche as service
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
    metier: str  # le métier écrit sur la carte, ex. « Plombier »
    principal: bool
    siret_verifie: bool  # coin de la carte : « SIRET vérifié » ou « Particulier »
    photos: list[int]  # rangs des 2 premières photos de son travail → /api/prestataires/12/photos/1
    note: float | None
    nombre_avis: int
    nouveau: bool
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


class RubriqueVisible(BaseModel):
    """Un dossier de métiers et ses prestataires pour une ville (« Trouver un prestataire » par service)."""

    dossier_id: int
    code: str
    nom: str
    total: int
    page: int
    pages: int
    resultats: list[CarteResultat]


class PageRubriques(BaseModel):
    ville: CommuneVisible
    rubriques: list[RubriqueVisible]


class PrestatairePublic(BaseModel):
    id: int
    nom_affiche: str
    presentation: str | None
    a_une_photo: bool
    ville: str
    distance_km: int
    lieu: str  # chez_client, chez_moi ou les_deux
    metiers: list[MetierCourt]
    siret_verifie: bool
    note: float | None
    nombre_avis: int
    absences: int  # « 1 absence sans prévenir » en 6 mois (RM-RENDEZ-VOUS)
    photos: list[int]  # rangs des photos de son travail (10 au plus)


def carte(db: Base, r: service.Resultat) -> CarteResultat:
    photos = service_prestataires.photos_de(db, r.prestataire.id)[: reglages.RECHERCHE_PHOTOS_SUR_CARTE]
    return CarteResultat(
        prestataire_id=r.prestataire.id, nom_affiche=r.prestataire.nom_affiche, a_une_photo=r.prestataire.photo_id is not None,
        ville=r.commune.nom, distance_km=round(r.distance_km), metier=db.get_one(Metier, r.metier_id).nom,
        principal=r.principal, siret_verifie=r.prestataire.siret_statut == "verifie", photos=[p.ordre for p in photos],
        note=r.note, nombre_avis=r.nombre_avis,
        nouveau=r.nouveau, vient_chez_vous=service.vient_chez_le_client(r),
        carte_possible=service.carte_acceptee(r.prestataire),
    )


@routeur.get("/recherche")
def rechercher(
    metier_id: int, commune_id: int, db: Base, tri: str = "note", page: int = 1, vient_chez_moi: bool = False,
    carte_bancaire: bool = False,
) -> PageResultats:
    """Ex. /api/recherche?metier_id=3&commune_id=33522&carte_bancaire=true. Ouvert à tous."""
    filtres = service.Filtres(vient_chez_moi=vient_chez_moi, carte=carte_bancaire)
    resultat = service.rechercher(
        db, metier_id=metier_id, commune_id=commune_id, maintenant=maintenant(), filtres=filtres, tri=tri, page=page
    )
    metier = db.get_one(Metier, metier_id)
    return PageResultats(
        metier=MetierCourt(id=metier.id, nom=metier.nom), ville=commune_visible(db.get_one(Commune, commune_id)),
        total=resultat.total,
        page=resultat.page, pages=resultat.pages, resultats=[carte(db, r) for r in resultat.resultats],
        metiers_voisins=[MetierCourt(id=m.id, nom=m.nom) for m in resultat.metiers_voisins],
    )


def _rubrique(db: Base, rubrique: service.Rubrique, *, par_page: int, page: int = 1) -> RubriqueVisible:
    pages = max(1, -(-len(rubrique.resultats) // par_page))
    page = min(max(1, page), pages)
    return RubriqueVisible(
        dossier_id=rubrique.dossier.id, code=rubrique.dossier.code, nom=rubrique.dossier.nom, total=len(rubrique.resultats),
        page=page, pages=pages, resultats=[carte(db, r) for r in rubrique.resultats[(page - 1) * par_page: page * par_page]],
    )


@routeur.get("/recherche/rubriques")
def rubriques(commune_id: int, db: Base) -> PageRubriques:
    """Ex. /api/recherche/rubriques?commune_id=33318 → « Bricolage » (14, les 10 premiers), « Jardinage » (9)… Ouvert à tous."""
    trouvees = service.par_dossier(db, commune_id=commune_id, maintenant=maintenant())
    return PageRubriques(
        ville=commune_visible(db.get_one(Commune, commune_id)),
        rubriques=[_rubrique(db, r, par_page=reglages.RECHERCHE_CARTES_PAR_RUBRIQUE) for r in trouvees],
    )


@routeur.get("/recherche/rubriques/{dossier_id}")
def rubrique_entiere(dossier_id: int, commune_id: int, db: Base, page: int = 1) -> PageRubriques:
    """[Voir tout] : tous les prestataires d'un dossier pour une ville, 30 par page. Dossier vide : aucune rubrique."""
    trouvees = service.par_dossier(db, commune_id=commune_id, maintenant=maintenant())
    return PageRubriques(
        ville=commune_visible(db.get_one(Commune, commune_id)),
        rubriques=[_rubrique(db, r, par_page=reglages.RECHERCHE_RESULTATS_PAR_PAGE, page=page)
                   for r in trouvees if r.dossier.id == dossier_id],
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
    """Profil, note et photos du travail d'un prestataire."""
    prestataire = prestataire_visible_ou_404(db, prestataire_id, compte)
    maintenant_ = maintenant()
    metiers = [db.get_one(Metier, i) for i in metiers_exerces(db, prestataire, aujourd_hui(maintenant_))]
    somme, nombre = service_avis.notes(db, [prestataire.id]).get(prestataire.id, (0, 0))
    note = somme / nombre if nombre else None
    return PrestatairePublic(
        id=prestataire.id, nom_affiche=prestataire.nom_affiche, presentation=prestataire.presentation,
        a_une_photo=prestataire.photo_id is not None, ville=db.get_one(Commune, prestataire.commune_id).nom,
        distance_km=prestataire.distance_km, lieu=prestataire.lieu, metiers=[MetierCourt(id=m.id, nom=m.nom) for m in metiers],
        siret_verifie=prestataire.siret_statut == "verifie", note=note, nombre_avis=nombre,
        absences=len(absences.absences_du_prestataire(db, prestataire.id, maintenant_)),
        photos=[p.ordre for p in service_prestataires.photos_de(db, prestataire.id)],
    )
