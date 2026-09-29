"""Vérification d'un SIRET auprès du service officiel « Recherche d'entreprises » de l'État
(recherche-entreprises.api.gouv.fr : gratuit, sans inscription). Règles : RM-PRESTATAIRES.md (lot 2.4).

Vérifié : le SIRET existe, l'établissement est ouvert, et le nom de famille du compte apparaît dans le nom
officiel ou parmi les dirigeants — ou le nom est caché par l'État (« non diffusible » : accepté d'office,
décision de Raphael du 29/09/2026). Refusé sinon, avec la raison. Service injoignable : « à vérifier ».
"""

import json
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Literal

from app.modeles.comptes import Compte
from app.services.metiers import sans_accents

ADRESSE = "https://recherche-entreprises.api.gouv.fr/search"
DELAI_SECONDES = 8


class ServiceIndisponible(Exception):
    """Le service de l'État ne répond pas (panne, pas d'internet) : on réessaiera plus tard."""


@dataclass
class Resultat:
    statut: Literal["verifie", "refuse", "a_verifier"]
    message: str
    nom_officiel: str | None = None


def interroger(siret: str) -> list[dict[str, Any]]:
    """Demande au service de l'État les entreprises qui correspondent à ce SIRET. (Remplacé par une fausse
    réponse dans les tests, pour ne pas dépendre d'internet.)"""
    adresse = f"{ADRESSE}?{urllib.parse.urlencode({'q': siret, 'per_page': 5})}"
    try:
        with urllib.request.urlopen(adresse, timeout=DELAI_SECONDES) as reponse:
            return json.load(reponse).get("results", [])
    except Exception as erreur:  # réseau, délai dépassé, réponse illisible : tout se traite pareil
        raise ServiceIndisponible(str(erreur)) from erreur


def _mots(texte: str | None) -> set[str]:
    return set(re.findall(r"[a-z]+", sans_accents(texte or "")))


def _nom_cache(entreprise: dict[str, Any]) -> bool:
    return entreprise.get("statut_diffusion") in ("P", "N") or "NON-DIFFUSIBLE" in (entreprise.get("nom_complet") or "").upper()


def _porte_le_nom(entreprise: dict[str, Any], compte: Compte) -> bool:
    noms_du_compte = {mot for mot in _mots(compte.nom) if len(mot) >= 2}
    textes = [entreprise.get("nom_complet"), entreprise.get("nom_raison_sociale")]
    for dirigeant in entreprise.get("dirigeants") or []:
        textes += [dirigeant.get("nom"), dirigeant.get("nom_usage"), dirigeant.get("denomination")]
    mots_officiels = set().union(*(_mots(t) for t in textes))
    return bool(noms_du_compte & mots_officiels)


def verifier(siret: str, compte: Compte) -> Resultat:
    try:
        entreprises = interroger(siret)
    except ServiceIndisponible:
        return Resultat("a_verifier", "Le répertoire de l'État ne répond pas : votre SIRET sera vérifié automatiquement plus tard.")

    entreprise = next((e for e in entreprises if e.get("siren") == siret[:9]), None)
    etablissement = None
    if entreprise is not None:
        candidats = [*(entreprise.get("matching_etablissements") or []), entreprise.get("siege") or {}]
        etablissement = next((e for e in candidats if e.get("siret") == siret), None)
    if entreprise is None or etablissement is None:
        return Resultat("refuse", "Ce SIRET n'existe pas dans le répertoire de l'État. Vérifiez-le sur votre avis de situation INSEE.")
    if etablissement.get("etat_administratif") == "F":
        return Resultat("refuse", "Cet établissement est fermé dans le répertoire de l'État : indiquez le SIRET de votre activité actuelle.")

    nom_officiel = entreprise.get("nom_complet")
    if _nom_cache(entreprise):
        return Resultat("verifie", "SIRET vérifié (nom non public).", None)
    if not _porte_le_nom(entreprise, compte):
        return Resultat(
            "refuse",
            f"Ce SIRET appartient à « {nom_officiel} » : il ne semble pas être le vôtre. "
            "Si c'est une erreur, contactez l'administrateur de rafals.",
            nom_officiel,
        )
    return Resultat("verifie", f"SIRET vérifié : {nom_officiel}.", nom_officiel)
