"""Recherche d'un prestataire : un métier + la ville du client. Règles : .doc/regles-metier/RM-RECHERCHE.md (validé le 30/09/2026).

Ordre : métier principal d'abord ; puis les prestataires notés, du meilleur au moins bon selon la note pondérée ;
puis les nouveaux (sans avis, badge « Nouveau ») ; à égalité, le plus proche, puis le plus ancien sur rafals.
Aucune table : tout se calcule à partir des prestataires, des annonces, des communes et de l'agenda."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.annonces import Annonce
from app.modeles.metiers import Metier
from app.modeles.prestataires import Commune, Prestataire
from app.services import agenda, communes
from app.services.annonces import modes_de_paiement
from app.services.erreurs import ErreurRegle
from app.services.prestataires import aujourd_hui, en_cours, metiers_exerces


@dataclass
class Filtres:
    vient_chez_moi: bool = False
    carte: bool = False
    libre_7_jours: bool = False
    prix_max_centimes: int | None = None


@dataclass
class Resultat:
    prestataire: Prestataire
    commune: Commune
    distance_km: float
    principal: bool  # le métier cherché est son métier principal
    annonces: list[Annonce] = field(default_factory=list)
    note: float | None = None  # vraie note moyenne, montrée au client
    nombre_avis: int = 0
    note_classement: float | None = None  # note pondérée, sert seulement à l'ordre

    @property
    def nouveau(self) -> bool:
        return self.nombre_avis == 0

    @property
    def a_partir_de(self) -> Annonce | None:
        """L'annonce la moins chère (prix fixe, ou prix de l'heure) ; None s'il n'a que des annonces sur devis."""
        avec_prix = [a for a in self.annonces if a.prix_centimes is not None]
        return min(avec_prix, key=lambda a: a.prix_centimes or 0) if avec_prix else None


@dataclass
class Page:
    resultats: list[Resultat]
    total: int
    page: int
    pages: int
    metiers_voisins: list[Metier]


def note_ponderee(somme_des_notes: int, nombre_avis: int) -> float:
    """(somme des notes + 5 avis fictifs à 4 ★) ÷ (nombre d'avis + 5). Ex. Sophie, 40 avis à 4,8 ★ → 4,71 ;
    Julie, 1 avis à 5 ★ → 4,17 : un seul avis ne suffit pas pour être premier."""
    fictifs = reglages.RECHERCHE_AVIS_FICTIFS
    return (somme_des_notes + fictifs * reglages.RECHERCHE_NOTE_FICTIVE) / (nombre_avis + fictifs)


def _avis(db: Session, prestataires: list[Prestataire]) -> dict[int, tuple[int, int]]:
    """Par prestataire : (somme des notes, nombre d'avis). Les avis arrivent au lot 4.7 : pour l'instant, aucun."""
    return {}


def _libre_dans_7_jours(db: Session, r: Resultat, maintenant: datetime) -> bool:
    jour = aujourd_hui(maintenant)
    for annonce in (a for a in r.annonces if a.forme_prix != "devis"):
        for decalage in range(7):
            if agenda.horaires_libres(db, r.prestataire, annonce, jour + timedelta(days=decalage), maintenant):
                return True
    return False


def _garder(db: Session, r: Resultat, filtres: Filtres, maintenant: datetime) -> bool:
    if filtres.vient_chez_moi and not any(a.lieu in ("chez_client", "les_deux") for a in r.annonces):
        return False
    if filtres.carte and not any("carte" in modes_de_paiement(a, r.prestataire) for a in r.annonces):
        return False
    moins_cher = r.a_partir_de
    if filtres.prix_max_centimes is not None and moins_cher is not None:
        if (moins_cher.prix_centimes or 0) > filtres.prix_max_centimes:
            return False  # « sur devis » seulement : il reste affiché
    return not (filtres.libre_7_jours and not _libre_dans_7_jours(db, r, maintenant))


def rechercher(
    db: Session, *, metier_id: int, commune_id: int, maintenant: datetime, filtres: Filtres | None = None,
    tri: str = "note", page: int = 1,
) -> Page:
    """Ex. « Plombier » + Talence → les plombiers dont le rayon couvre Talence et qui ont une annonce de plomberie en ligne."""
    metier = db.get(Metier, metier_id)
    client = db.get(Commune, commune_id)
    if metier is None:
        raise ErreurRegle("Choisissez un métier dans la liste.")
    if client is None:
        raise ErreurRegle("Choisissez votre ville dans la liste.")
    if tri not in ("note", "distance"):
        raise ErreurRegle("Tri inconnu.")
    filtres = filtres or Filtres()
    jour = aujourd_hui(maintenant)

    # Annonces en ligne de ce métier, regroupées par prestataire actif
    lignes = db.execute(
        select(Annonce, Prestataire)
        .join(Prestataire, Prestataire.id == Annonce.prestataire_id)
        .where(Annonce.metier_id == metier_id, Annonce.statut == "en_ligne", Prestataire.statut == "actif")
    ).all()
    par_prestataire: dict[int, Resultat] = {}
    for annonce, prestataire in lignes:
        if prestataire.id not in par_prestataire:
            if metier_id not in metiers_exerces(db, prestataire, jour):
                continue  # métier arrêté (date de fin passée)
            depart = db.get_one(Commune, prestataire.commune_id)
            distance = communes.distance_km(depart, client)
            if distance > prestataire.distance_km:
                continue  # la ville du client est hors de son rayon
            principal = prestataire.metier_principal_id == metier_id and en_cours(prestataire.metier_principal_fin_le, jour)
            par_prestataire[prestataire.id] = Resultat(prestataire, depart, distance, principal)
        par_prestataire[prestataire.id].annonces.append(annonce)

    resultats = list(par_prestataire.values())
    avis = _avis(db, [r.prestataire for r in resultats])
    for r in resultats:
        somme, nombre = avis.get(r.prestataire.id, (0, 0))
        r.nombre_avis = nombre
        r.note = somme / nombre if nombre else None
        r.note_classement = note_ponderee(somme, nombre) if nombre else None
    resultats = [r for r in resultats if _garder(db, r, filtres, maintenant)]

    def cle_note(r: Resultat) -> tuple:
        return (not r.principal, r.nouveau, -(r.note_classement or 0), r.distance_km, r.prestataire.cree_le)

    def cle_distance(r: Resultat) -> tuple:
        return (r.distance_km, not r.principal, r.nouveau, -(r.note_classement or 0), r.prestataire.cree_le)

    resultats.sort(key=cle_note if tri == "note" else cle_distance)

    par_page = reglages.RECHERCHE_RESULTATS_PAR_PAGE
    pages = max(1, -(-len(resultats) // par_page))
    page = min(max(1, page), pages)
    voisins: list[Metier] = []
    if not resultats:
        # Aucun résultat : les autres métiers du même dossier (ex. Plombier → Chauffagiste…)
        voisins = list(db.scalars(
            select(Metier).where(Metier.categorie_id == metier.categorie_id, Metier.id != metier.id, Metier.est_active)
            .order_by(Metier.nom).limit(reglages.RECHERCHE_METIERS_VOISINS)
        ))
    return Page(resultats[(page - 1) * par_page: page * par_page], len(resultats), page, pages, voisins)


def page_publique_visible(prestataire: Prestataire) -> bool:
    """Page publique d'un prestataire : visible si son activité est active (en pause, bloquée ou arrêtée : cachée).
    Un prestataire dont le seul métier est arrêté reste visible, avec « Aucune annonce » (RM-ANNONCES)."""
    return prestataire.statut == "actif"
