"""Appels à Stripe (paiement par carte, choisi par Raphael le 02/10/2026 : Stripe Connect, « Stripe gère la
tarification »). Règles : RM-PAIEMENTS.md.

Pourquoi pas la bibliothèque officielle de Stripe : l'ajouter demanderait de reconstruire le conteneur du serveur ;
quelques appels web suffisent (même façon de faire que pour le SIRET et l'IA des avis). Les tests remplacent
`appeler` par un faux Stripe : aucune vraie carte, aucun appel à internet.

Formule choisie : chaque prestataire a son propre compte Stripe (« compte connecté ») ; le client paie directement
sur ce compte, rafals y prend sa commission, et c'est rafals qui décide quand l'argent part vers la banque du
prestataire (versements « manuels »)."""

import hashlib
import hmac
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from app import config

ADRESSE = "https://api.stripe.com"
DELAI_SECONDES = 20
TOLERANCE_SIGNATURE_SECONDES = 5 * 60


class StripeIndisponible(Exception):
    """Stripe ne répond pas ou refuse la demande : on réessaiera plus tard (tâche de fond)."""


def disponible() -> bool:
    """Le paiement par carte n'existe que si la clé secrète de Stripe est dans le fichier .env."""
    return bool(config.STRIPE_CLE_SECRETE)


def _aplatir(donnees: dict[str, Any], prefixe: str = "") -> list[tuple[str, str]]:
    """Stripe attend un formulaire : {"metadata": {"paiement_id": 3}} → metadata[paiement_id]=3."""
    paires: list[tuple[str, str]] = []
    for cle, valeur in donnees.items():
        nom = f"{prefixe}[{cle}]" if prefixe else cle
        if isinstance(valeur, dict):
            paires += _aplatir(valeur, nom)
        elif isinstance(valeur, list):
            for i, element in enumerate(valeur):
                if isinstance(element, dict):
                    paires += _aplatir(element, f"{nom}[{i}]")
                else:
                    paires.append((f"{nom}[{i}]", str(element)))
        elif isinstance(valeur, bool):
            paires.append((nom, "true" if valeur else "false"))
        elif valeur is not None:
            paires.append((nom, str(valeur)))
    return paires


def appeler(methode: str, chemin: str, donnees: dict[str, Any] | None = None, *, compte: str | None = None,
            cle_unique: str | None = None) -> dict[str, Any]:
    """Un appel à Stripe. `compte` : agir sur le compte Stripe d'un prestataire (acct_…). `cle_unique` : si le même
    appel est refait (panne au mauvais moment), Stripe ne le fait pas deux fois (ex. jamais deux remboursements)."""
    corps = urllib.parse.urlencode(_aplatir(donnees or {})).encode()
    adresse = f"{ADRESSE}{chemin}"
    if methode == "GET" and corps:
        adresse, corps = f"{adresse}?{corps.decode()}", b""
    entetes = {"Authorization": f"Bearer {config.STRIPE_CLE_SECRETE}"}
    if config.STRIPE_VERSION:
        entetes["Stripe-Version"] = config.STRIPE_VERSION
    if compte:
        entetes["Stripe-Account"] = compte
    if cle_unique:
        entetes["Idempotency-Key"] = cle_unique
    requete = urllib.request.Request(adresse, data=corps if methode != "GET" else None, headers=entetes, method=methode)
    try:
        with urllib.request.urlopen(requete, timeout=DELAI_SECONDES) as reponse:
            return json.load(reponse)
    except urllib.error.HTTPError as erreur:  # Stripe a répondu, mais refuse : on garde son explication
        try:
            message = json.load(erreur).get("error", {}).get("message", "")
        except ValueError:
            message = ""
        raise StripeIndisponible(f"Stripe refuse ({erreur.code}) : {message}") from erreur
    except Exception as erreur:  # réseau, délai dépassé, réponse illisible : tout se traite pareil
        raise StripeIndisponible(str(erreur)) from erreur


def lire_evenement(corps: bytes, signature: str, maintenant: float | None = None) -> dict[str, Any]:
    """Stripe prévient rafals (« webhook ») : on vérifie que le message vient bien de Stripe (signature calculée avec
    le secret du fichier .env) et qu'il est récent, puis on le lit. Lève ValueError sinon."""
    morceaux = [p.split("=", 1) for p in signature.split(",") if "=" in p]  # « t=1696240000,v1=5257a8… »
    horodatage = next((v for k, v in morceaux if k == "t"), "")
    recue = [v for k, v in morceaux if k == "v1"]
    if not config.STRIPE_SECRET_WEBHOOK or not horodatage.isdigit() or not recue:
        raise ValueError("signature absente")
    attendue = hmac.new(config.STRIPE_SECRET_WEBHOOK.encode(), f"{horodatage}.".encode() + corps, hashlib.sha256).hexdigest()
    if not any(hmac.compare_digest(attendue, v) for v in recue):
        raise ValueError("signature fausse")
    if abs((maintenant or time.time()) - int(horodatage)) > TOLERANCE_SIGNATURE_SECONDES:
        raise ValueError("message trop ancien")
    return json.loads(corps)
