"""Communes : recherche par nom ou code postal, distance à vol d'oiseau entre deux communes.
Règle : RM-PRESTATAIRES.md (zone d'intervention : distance à vol d'oiseau entre les centres des villes)."""

import math

from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from app.modeles.prestataires import Commune
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
