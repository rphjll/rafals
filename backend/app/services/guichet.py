"""Appels au guichet unique de l'État (API « mandataire de dépôt » de l'INPI) : rafals y dépose le dossier de création
d'auto-entreprise à la place de la personne. Règles : RM-CREATION-AUTO-ENTREPRISE.md ; étude : technique/API-EXTERNES.md.

Même façon de faire que pour Stripe : quelques appels web, sans bibliothèque ; les tests remplacent `appeler` par un
faux guichet (aucun appel à internet, aucune vraie entreprise créée).

Sans identifiants de l'INPI dans le fichier .env, rafals est en « démonstration » : rien n'est envoyé à l'État, le
dossier est accepté tout de suite avec un faux SIRET (qui n'est jamais recopié dans le profil).

⚠️ Avant la mise en ligne : essayer chaque appel dans l'espace d'essai de l'INPI (guichet-unique-demo.inpi.fr) ;
le contenu du dossier suit le dictionnaire de données de l'INPI mais n'a encore jamais été envoyé pour de vrai."""

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from app import config, reglages

DELAI_SECONDES = 30
PREFIXE_DEMONSTRATION = "DEMO-"

_jeton: str | None = None


class GuichetIndisponible(Exception):
    """Le guichet ne répond pas ou refuse la demande : on réessaiera plus tard."""


@dataclass
class Etat:
    statut: str  # envoye · en_examen · a_corriger · accepte · refuse · ferme
    a_signer: bool = False
    motif: str | None = None
    siret: str | None = None
    siren: str | None = None
    pieces_refusees: tuple[str, ...] = ()  # codes de l'INPI des papiers à refaire (ex. « PJ_11 » : la carte d'identité)


def disponible() -> bool:
    """Le vrai guichet n'est branché que si les identifiants de l'INPI sont dans le fichier .env."""
    return bool(config.INPI_IDENTIFIANT and config.INPI_MOT_DE_PASSE)


def en_demonstration(guichet_id: str | None) -> bool:
    return bool(guichet_id) and guichet_id.startswith(PREFIXE_DEMONSTRATION)


def _demander(methode: str, chemin: str, donnees: dict[str, Any] | None, jeton: str | None) -> dict[str, Any]:
    entetes = {"Content-Type": "application/json", "Accept": "application/json"}
    if jeton:
        entetes["Authorization"] = f"Bearer {jeton}"
    corps = json.dumps(donnees).encode() if donnees is not None else None
    requete = urllib.request.Request(f"{config.INPI_ADRESSE}{chemin}", data=corps, headers=entetes, method=methode)
    with urllib.request.urlopen(requete, timeout=DELAI_SECONDES) as reponse:
        texte = reponse.read()
        return json.loads(texte) if texte else {}


def appeler(methode: str, chemin: str, donnees: dict[str, Any] | None = None) -> dict[str, Any]:
    """Un appel au guichet, connecté avec le compte INPI de rafals (le jeton de connexion est gardé en mémoire et
    redemandé une fois s'il a expiré)."""
    global _jeton
    try:
        for essai in (1, 2):
            if _jeton is None:
                _jeton = _demander("POST", "/api/user/login/sso",
                                   {"username": config.INPI_IDENTIFIANT, "password": config.INPI_MOT_DE_PASSE}, None).get("token")
            try:
                return _demander(methode, chemin, donnees, _jeton)
            except urllib.error.HTTPError as erreur:
                if erreur.code != 401 or essai == 2:
                    raise
                _jeton = None  # jeton expiré : on se reconnecte une fois
    except urllib.error.HTTPError as erreur:  # le guichet a répondu, mais refuse : on garde son explication
        raise GuichetIndisponible(f"Le guichet refuse ({erreur.code}) : {erreur.read()[:500].decode(errors='replace')}") from erreur
    except Exception as erreur:  # réseau, délai dépassé, réponse illisible : tout se traite pareil
        raise GuichetIndisponible(str(erreur)) from erreur
    raise GuichetIndisponible("connexion impossible")


# ---------- Les 4 gestes de rafals ----------


def deposer(dossier: dict[str, Any]) -> tuple[str, str]:
    """Dépose le dossier. Renvoie (identifiant du guichet, numéro de dossier montré à la personne)."""
    if not disponible():
        return f"{PREFIXE_DEMONSTRATION}{uuid4().hex[:10]}", "DÉMONSTRATION"
    reponse = appeler("POST", "/api/formalities", dossier)
    return str(reponse["id"]), str(reponse.get("liasseNumber") or reponse["id"])


def signer(guichet_id: str) -> None:
    """Pour une création, une signature simple par l'API suffit (pas de certificat)."""
    if not en_demonstration(guichet_id):
        appeler("POST", "/api/signatures", {"formality": f"/api/formalities/{guichet_id}"})


def corriger(guichet_id: str, dossier: dict[str, Any]) -> None:
    """Renvoie le dossier corrigé après une demande de l'administration, puis le signe de nouveau."""
    if not en_demonstration(guichet_id):
        appeler("PUT", f"/api/formalities/{guichet_id}", dossier)
        signer(guichet_id)


ETATS = {
    "RECEIVED": "envoye", "SIGNATURE_PENDING": "envoye", "SIGNED": "envoye", "PAYMENT_PENDING": "envoye",
    "PAYMENT_VALIDATION_PENDING": "envoye", "PAID": "envoye", "ERROR": "envoye",
    "VALIDATION_PENDING": "en_examen", "AMENDMENT_PENDING": "a_corriger",
    "VALIDATED": "accepte", "REJECTED": "refuse", "EXPIRED": "ferme",
}


def _motif(reponse: dict[str, Any]) -> str | None:
    """Ce que les organismes (URSSAF, greffe, chambre de métiers) demandent ou reprochent."""
    textes = [str(demande["observation"]).strip() for demande in _demandes(reponse) if demande.get("observation")]
    return " ".join(dict.fromkeys(textes))[:1000] or None


def _demandes(reponse: dict[str, Any]) -> list[dict[str, Any]]:
    """Les demandes de correction (« regularizationObjects »), où qu'elles soient rangées dans la réponse."""
    demandes = list(reponse.get("regularizationObjects") or [])
    for validation in reponse.get("validationsRequests") or []:
        demandes += validation.get("regularizationObjects") or []
    return demandes


def etat(guichet_id: str) -> Etat:
    """Où en est le dossier."""
    if en_demonstration(guichet_id):
        return Etat("accepte", siret=reglages.CREATION_SIRET_DEMONSTRATION)
    reponse = appeler("GET", f"/api/formalities/{guichet_id}")
    officiel = str(reponse.get("status") or "")
    if officiel not in ETATS:
        raise GuichetIndisponible(f"état inconnu du guichet : {officiel}")
    principal = (((reponse.get("content") or {}).get("personnePhysique") or {}).get("etablissementPrincipal") or {})
    siret = (principal.get("descriptionEtablissement") or {}).get("siret")
    return Etat(ETATS[officiel], a_signer=officiel in ("RECEIVED", "SIGNATURE_PENDING"), motif=_motif(reponse),
                siret=str(siret) if siret else None, siren=str(reponse["siren"]) if reponse.get("siren") else None,
                pieces_refusees=tuple(d["attachment"]["typeDocument"] for d in _demandes(reponse)
                                      if d.get("type") == "INVALID_ATTACHMENT" and (d.get("attachment") or {}).get("typeDocument")))
