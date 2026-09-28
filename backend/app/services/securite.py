"""Brouillage des mots de passe et fabrication des jetons secrets (sessions, liens des mails)."""

import hashlib
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError

_hacheur = PasswordHasher()


def hacher_mot_de_passe(mot_de_passe: str) -> str:
    return _hacheur.hash(mot_de_passe)


def mot_de_passe_correct(mot_de_passe: str, hache: str) -> bool:
    try:
        return _hacheur.verify(hache, mot_de_passe)
    except VerificationError:
        return False


def nouveau_jeton() -> tuple[str, str]:
    """Renvoie (jeton en clair, jeton brouillé). Le clair part au navigateur ou dans le mail ;
    seule la version brouillée est gardée dans la base."""
    clair = secrets.token_urlsafe(32)
    return clair, hacher_jeton(clair)


def hacher_jeton(clair: str) -> str:
    return hashlib.sha256(clair.encode()).hexdigest()
