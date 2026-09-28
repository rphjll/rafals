"""Outils communs des tests de fiche : les rubriques sont LUES dans le modèle, jamais listées à la main.
Une rubrique ajoutée plus tard à une table entre donc toute seule dans le test."""

from datetime import UTC, date, datetime, timedelta
from typing import Any
from uuid import uuid4

from sqlalchemy import ARRAY, Boolean, Date, DateTime, Float, Integer, Text, inspect
from sqlalchemy.orm import Session


def rubriques(modele: type) -> list[str]:
    """Toutes les colonnes sauf l'identifiant (PK)."""
    return [colonne.key for colonne in inspect(modele).columns if not colonne.primary_key]


def valeurs(modele: type, variante: int, imposees: dict[str, Any] | None = None) -> dict[str, Any]:
    """Une valeur d'essai pour chaque rubrique, différente selon la variante (1 = ajout, 2 = modification).
    `imposees` : liens (xxx_id) et rubriques limitées à une liste de valeurs par la base."""
    imposees = imposees or {}
    suffixe = uuid4().hex[:8]
    resultat: dict[str, Any] = {}
    for colonne in inspect(modele).columns:
        if colonne.primary_key:
            continue
        if colonne.key in imposees:
            resultat[colonne.key] = imposees[colonne.key]
        elif isinstance(colonne.type, Text):
            # Marqué comme donnée d'essai, en minuscules (certaines colonnes l'exigent)
            resultat[colonne.key] = f"zztest.{colonne.key}.{variante}.{suffixe}@example.com"
        elif isinstance(colonne.type, DateTime):
            resultat[colonne.key] = datetime(2026, 1, 1, 9, 0, tzinfo=UTC) + timedelta(days=variante)
        elif isinstance(colonne.type, Date):
            resultat[colonne.key] = date(1990, 1, 1) + timedelta(days=variante)
        elif isinstance(colonne.type, ARRAY):
            resultat[colonne.key] = [f"zztest{variante}", f"essai{variante}"]
        elif isinstance(colonne.type, Float):
            resultat[colonne.key] = 40.0 + variante / 10
        elif isinstance(colonne.type, Boolean):
            resultat[colonne.key] = variante == 1
        elif isinstance(colonne.type, Integer):
            resultat[colonne.key] = variante
        else:
            raise AssertionError(f"Type de rubrique non prévu dans le test de fiche : {colonne.key} ({colonne.type})")
    return resultat


def relire_et_comparer(db: Session, modele: type, identifiant: int, attendu: dict[str, Any]) -> None:
    db.expire_all()
    ligne = db.get_one(modele, identifiant)
    for rubrique in rubriques(modele):
        assert getattr(ligne, rubrique) == attendu[rubrique], f"{modele.__name__}.{rubrique} mal enregistrée"
