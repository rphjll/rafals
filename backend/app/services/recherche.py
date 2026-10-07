"""Recherche d'un prestataire : un métier + la ville du client, ou tous les services d'une ville rangés par dossier.
Règles : .doc/regles-metier/RM-RECHERCHE.md (validé le 30/09/2026 ; « Sans annonces » et « Une rubrique par dossier », 07/10/2026).

Qui apparaît : un prestataire actif, qui exerce le métier, et dont le rayon couvre la ville du client (plus besoin d'annonce).
Ordre : métier principal d'abord ; puis les prestataires notés, du meilleur au moins bon selon la note pondérée ;
puis les nouveaux (sans avis, badge « Nouveau ») ; à égalité, le plus proche, puis le plus ancien sur rafals.
Aucune table : tout se calcule à partir des prestataires, des annonces, des communes et de l'agenda."""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.annonces import Annonce
from app.modeles.metiers import CategorieMetier, Metier
from app.modeles.prestataires import Commune, Prestataire
from app.services import agenda, avis, communes
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
    principal: bool  # le métier cherché (ou montré) est son métier principal
    metier_id: int  # le métier écrit sur sa carte
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


@dataclass
class Rubrique:
    """Un dossier de métiers (ex. « Jardinage ») et ses prestataires pour une ville, déjà dans l'ordre."""

    dossier: CategorieMetier
    resultats: list[Resultat]


def note_ponderee(somme_des_notes: int, nombre_avis: int) -> float:
    """(somme des notes + 5 avis fictifs à 4 ★) ÷ (nombre d'avis + 5). Ex. Sophie, 40 avis à 4,8 ★ → 4,71 ;
    Julie, 1 avis à 5 ★ → 4,17 : un seul avis ne suffit pas pour être premier."""
    fictifs = reglages.RECHERCHE_AVIS_FICTIFS
    return (somme_des_notes + fictifs * reglages.RECHERCHE_NOTE_FICTIVE) / (nombre_avis + fictifs)


def _avis(db: Session, prestataires: list[Prestataire]) -> dict[int, tuple[int, int]]:
    """Par prestataire : (somme des notes, nombre d'avis visibles)."""
    return avis.notes(db, [p.id for p in prestataires])


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


def _dans_le_rayon(db: Session, client: Commune, jour: date) -> list[tuple[Prestataire, Commune, float, list[int]]]:
    """Les prestataires actifs dont le rayon couvre la ville du client, avec leur ville de départ, la distance et
    leurs métiers exercés. Ex. Karim, « Pessac, jusqu'à 15 km » : gardé pour Talence (5 km), pas pour Libourne."""
    trouves = []
    for prestataire in db.scalars(select(Prestataire).where(Prestataire.statut == "actif")):
        depart = db.get_one(Commune, prestataire.commune_id)
        distance = communes.distance_km(depart, client)
        if distance <= prestataire.distance_km:
            trouves.append((prestataire, depart, distance, metiers_exerces(db, prestataire, jour)))
    return trouves


def _est_principal(prestataire: Prestataire, metier_id: int, jour: date) -> bool:
    return prestataire.metier_principal_id == metier_id and en_cours(prestataire.metier_principal_fin_le, jour)


def _noter(db: Session, resultats: list[Resultat]) -> None:
    notes = _avis(db, [r.prestataire for r in resultats])
    for r in resultats:
        somme, nombre = notes.get(r.prestataire.id, (0, 0))
        r.nombre_avis = nombre
        r.note = somme / nombre if nombre else None
        r.note_classement = note_ponderee(somme, nombre) if nombre else None


def _cle_note(r: Resultat) -> tuple:
    return (not r.principal, r.nouveau, -(r.note_classement or 0), r.distance_km, r.prestataire.cree_le)


def _cle_distance(r: Resultat) -> tuple:
    return (r.distance_km, not r.principal, r.nouveau, -(r.note_classement or 0), r.prestataire.cree_le)


def par_dossier(db: Session, *, commune_id: int, maintenant: datetime) -> list[Rubrique]:
    """« Trouver un prestataire » pour une ville : une rubrique par dossier de métiers, sans les dossiers vides.
    Ex. à Pessac : « Bricolage » (Karim, plombier ; Sarah, électricienne), « Jardinage » (Sophie).
    Un prestataire est une seule fois dans une rubrique, avec son métier principal s'il est dans ce dossier,
    sinon son premier métier secondaire de ce dossier ; il peut être dans deux rubriques (plombier et jardinier)."""
    client = db.get(Commune, commune_id)
    if client is None:
        raise ErreurRegle("Choisissez votre ville dans la liste.")
    jour = aujourd_hui(maintenant)
    dossier_du_metier = {m.id: m.categorie_id for m in db.scalars(select(Metier).where(Metier.est_active))}
    par_rubrique: dict[int, dict[int, Resultat]] = {}
    for prestataire, depart, distance, exerces in _dans_le_rayon(db, client, jour):
        for metier_id in exerces:  # le métier principal est le premier de la liste
            dossier_id = dossier_du_metier.get(metier_id)
            if dossier_id is not None:
                par_rubrique.setdefault(dossier_id, {}).setdefault(
                    prestataire.id, Resultat(prestataire, depart, distance, _est_principal(prestataire, metier_id, jour), metier_id)
                )
    rubriques = []
    for dossier in db.scalars(select(CategorieMetier).where(CategorieMetier.est_active).order_by(CategorieMetier.ordre)):
        resultats = list(par_rubrique.get(dossier.id, {}).values())
        if resultats:
            _noter(db, resultats)
            rubriques.append(Rubrique(dossier, sorted(resultats, key=_cle_note)))
    return rubriques


def rechercher(
    db: Session, *, metier_id: int, commune_id: int, maintenant: datetime, filtres: Filtres | None = None,
    tri: str = "note", page: int = 1,
) -> Page:
    """Ex. « Plombier » + Talence → les plombiers actifs dont le rayon couvre Talence, avec ou sans annonce."""
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

    resultats = []
    for prestataire, depart, distance, exerces in _dans_le_rayon(db, client, jour):
        if metier_id in exerces:
            resultats.append(Resultat(prestataire, depart, distance, _est_principal(prestataire, metier_id, jour), metier_id))
    # Tant que les annonces existent : celles en ligne de ce métier donnent le prix et servent aux filtres
    par_prestataire = {r.prestataire.id: r for r in resultats}
    for annonce in db.scalars(select(Annonce).where(Annonce.metier_id == metier_id, Annonce.statut == "en_ligne")):
        if annonce.prestataire_id in par_prestataire:
            par_prestataire[annonce.prestataire_id].annonces.append(annonce)
    _noter(db, resultats)
    resultats = [r for r in resultats if _garder(db, r, filtres, maintenant)]
    resultats.sort(key=_cle_note if tri == "note" else _cle_distance)

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
