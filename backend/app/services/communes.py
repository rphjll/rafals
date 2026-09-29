"""Communes : recherche par nom ou code postal, distance à vol d'oiseau entre deux communes.
Règle : RM-PRESTATAIRES.md (zone d'intervention : distance à vol d'oiseau entre les centres des villes)."""

import math
from dataclasses import dataclass

from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.prestataires import Commune
from app.services.erreurs import ErreurRegle
from app.services.metiers import sans_accents

RAYON_TERRE_KM = 6371.0


def distance_km(a: Commune, b: Commune) -> float:
    """Distance à vol d'oiseau entre les centres de deux communes (formule de haversine).
    Ex. Pessac → Talence ≈ 6 km ; Pessac → Libourne ≈ 40 km."""
    lat1, lat2 = math.radians(a.latitude), math.radians(b.latitude)
    dlat = lat2 - lat1
    dlon = math.radians(b.longitude - a.longitude)
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * RAYON_TERRE_KM * math.asin(math.sqrt(h))


def rechercher(db: Session, texte: str, limite: int = 10) -> list[Commune]:
    """Par le début du nom (sans accents, « st » ou « saint ») ou par le code postal.
    Ex. « pes » → Pessac… ; « 33600 » → Pessac ; « saint-e » → Saint-Émilion…"""
    q = sans_accents(texte).replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    if not q:
        return []
    if q.isdigit():
        condition = func.array_to_string(Commune.codes_postaux, " ").like("%" + q + "%", escape="\\")
        rang = case((func.array_to_string(Commune.codes_postaux, " ").like(q + "%", escape="\\"), 1), else_=2)
    else:
        nom = func.replace(func.unaccent(func.lower(Commune.nom)), "-", " ")
        q_espaces = q.replace("-", " ")
        variantes = {q_espaces}
        if q_espaces.startswith("st "):
            variantes.add("saint " + q_espaces[3:])
        condition = or_(*(nom.like(v + "%", escape="\\") for v in variantes))
        rang = func.length(Commune.nom)  # à début égal, la commune au nom le plus court d'abord (Pessac avant Pessac-sur-Dordogne)
    return list(db.scalars(select(Commune).where(condition).order_by(rang, Commune.nom).limit(limite)))


@dataclass
class AdresseControlee:
    ligne: str
    complement: str | None
    commune: Commune
    code_postal: str


def controler_adresse(db: Session, *, ligne: str, complement: str | None, commune_id: int, code_postal: str) -> AdresseControlee:
    """Adresse d'un client ou local d'un prestataire. Ex. « 8 allée des Pins », Talence, 33400 → acceptée ;
    Talence avec 33600 (code de Pessac) → refusée."""
    ligne = " ".join(ligne.split())
    mini, maxi = reglages.ADRESSE_LIGNE_LONGUEUR
    if not mini <= len(ligne) <= maxi:
        raise ErreurRegle(f"L'adresse doit faire entre {mini} et {maxi} caractères (ex. « 8 allée des Pins »).")
    commune = db.get(Commune, commune_id)
    if commune is None:
        raise ErreurRegle("Choisissez la ville dans la liste.")
    code_postal = code_postal.strip()
    if code_postal not in commune.codes_postaux:
        codes = ", ".join(commune.codes_postaux)
        raise ErreurRegle(f"Le code postal {code_postal} ne correspond pas à {commune.nom} ({codes}).")
    return AdresseControlee(ligne, (complement or "").strip()[:maxi] or None, commune, code_postal)
