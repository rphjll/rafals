"""Appels à l'URSSAF (« API Tierce Déclaration auto-entrepreneur ») : rafals déclare le chiffre d'affaires à la place
du prestataire qui lui a donné son accord. Règles : RM-DEMARCHES.md ; étude : technique/API-EXTERNES.md.

⚠️ LA DOCUMENTATION TECHNIQUE DE L'URSSAF N'EST PAS PUBLIQUE (accès restreint, contact-api@urssaf.fr). Les adresses et
les noms de champs de ce fichier sont donc PROVISOIRES : seul ce que le service sait faire est confirmé (enregistrer et
annuler un mandat, estimer les cotisations, déclarer). Le jour où la documentation est obtenue, c'est le SEUL fichier à
adapter : le reste de rafals n'appelle que les 4 fonctions du bas.

Sans identifiants de l'URSSAF dans le fichier .env, rafals est en « démonstration » : rien n'est envoyé, les
cotisations sont estimées par rafals avec les taux de reglages.py. Les tests remplacent `appeler` par un faux URSSAF."""

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date
from typing import Any

from app import config, reglages

DELAI_SECONDES = 30

_jeton: str | None = None


class UrssafIndisponible(Exception):
    """L'URSSAF ne répond pas : rien n'est envoyé, on peut réessayer."""


class UrssafRefus(Exception):
    """L'URSSAF a répondu non : son explication est montrée telle quelle au prestataire."""


@dataclass
class Personne:
    """Celui pour qui rafals déclare."""

    siret: str
    numero_secu: str


@dataclass
class Resultat:
    cotisations_centimes: int
    reference: str | None = None


def disponible() -> bool:
    """Le vrai URSSAF n'est branché que si les identifiants sont dans le fichier .env."""
    return bool(config.URSSAF_IDENTIFIANT and config.URSSAF_SECRET)


def _connexion() -> str:
    corps = urllib.parse.urlencode({"grant_type": "client_credentials", "client_id": config.URSSAF_IDENTIFIANT,
                                    "client_secret": config.URSSAF_SECRET}).encode()
    with urllib.request.urlopen(urllib.request.Request(config.URSSAF_ADRESSE_JETON, data=corps), timeout=DELAI_SECONDES) as reponse:
        return json.load(reponse)["access_token"]


def appeler(methode: str, chemin: str, donnees: dict[str, Any] | None = None, *, cle_unique: str | None = None) -> dict[str, Any]:
    """Un appel à l'URSSAF. `cle_unique` : la même demande refaite après une panne n'est pas faite deux fois."""
    global _jeton
    try:
        for essai in (1, 2):
            if _jeton is None:
                _jeton = _connexion()
            entetes = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"Bearer {_jeton}"}
            if cle_unique:
                entetes["Idempotency-Key"] = cle_unique
            requete = urllib.request.Request(f"{config.URSSAF_ADRESSE}{chemin}", headers=entetes, method=methode,
                                             data=json.dumps(donnees).encode() if donnees is not None else None)
            try:
                with urllib.request.urlopen(requete, timeout=DELAI_SECONDES) as reponse:
                    texte = reponse.read()
                    return json.loads(texte) if texte else {}
            except urllib.error.HTTPError as erreur:
                if erreur.code == 401 and essai == 1:
                    _jeton = None  # jeton expiré : on se reconnecte une fois
                    continue
                if 400 <= erreur.code < 500:  # l'URSSAF refuse : on garde son explication
                    try:
                        message = json.load(erreur).get("message", "")
                    except ValueError:
                        message = ""
                    raise UrssafRefus(message or "L'URSSAF a refusé la demande.") from erreur
                raise
    except UrssafRefus:
        raise
    except Exception as erreur:  # réseau, délai dépassé, réponse illisible, erreur du serveur : tout se traite pareil
        raise UrssafIndisponible(str(erreur)) from erreur
    raise UrssafIndisponible("connexion impossible")


def _periode(debut: date, fin: date) -> dict[str, str]:
    return {"dateDebut": debut.isoformat(), "dateFin": fin.isoformat()}


def _montants(nature: str, centimes: int) -> dict[str, float]:
    """L'URSSAF sépare les prestations de services et les activités libérales (taux différents)."""
    return {"prestationsServices" if nature == "services" else "activitesLiberales": centimes / 100}


# ---------- Les 4 gestes de rafals ----------


def enregistrer_mandat(personne: Personne) -> None:
    """Signale à l'URSSAF que cette personne autorise rafals à déclarer pour elle."""
    if disponible():
        appeler("POST", "/mandats", {"siret": personne.siret, "nir": personne.numero_secu})


def annuler_mandat(personne: Personne) -> None:
    if disponible():
        appeler("POST", "/mandats/annulation", {"siret": personne.siret, "nir": personne.numero_secu})


def estimer(personne: Personne, nature: str, debut: date, fin: date, centimes: int) -> Resultat:
    """Les cotisations que l'URSSAF demandera pour ce montant. Rien n'est déclaré."""
    if not disponible():
        return Resultat((centimes * reglages.URSSAF_TAUX_DEMONSTRATION_POUR_MILLE[nature] + 500) // 1000)
    reponse = appeler("POST", "/estimations", {"siret": personne.siret, "nir": personne.numero_secu, **_periode(debut, fin),
                                               "chiffreAffaires": _montants(nature, centimes)})
    return Resultat(round(float(reponse["montantCotisations"]) * 100))


def declarer(personne: Personne, nature: str, debut: date, fin: date, centimes: int, *, cle_unique: str) -> Resultat:
    """Déclare le chiffre d'affaires de la période. L'URSSAF renvoie les cotisations dues."""
    if not disponible():
        return Resultat(estimer(personne, nature, debut, fin, centimes).cotisations_centimes, None)
    reponse = appeler("POST", "/declarations", {"siret": personne.siret, "nir": personne.numero_secu, **_periode(debut, fin),
                                                "chiffreAffaires": _montants(nature, centimes)}, cle_unique=cle_unique)
    return Resultat(round(float(reponse["montantCotisations"]) * 100), str(reponse["reference"]) if reponse.get("reference") else None)
