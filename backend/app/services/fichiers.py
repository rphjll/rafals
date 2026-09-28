"""Fichiers déposés (accord des parents, photo du prestataire…) : vérification puis rangement dans le stockage.
Un seul endroit pour ces règles (réutilisation)."""

from datetime import datetime

from sqlalchemy.orm import Session

from app.modeles.comptes import Compte
from app.modeles.fichiers import Fichier
from app.services import stockage
from app.services.erreurs import ErreurRegle

NOMS_FORMATS = {"application/pdf": "PDF", "image/jpeg": "JPG", "image/png": "PNG"}
# Premiers octets de chaque format : on vérifie le contenu, pas seulement le nom du fichier
_SIGNATURES = {"application/pdf": b"%PDF", "image/jpeg": b"\xff\xd8\xff", "image/png": b"\x89PNG"}


def verifier(contenu: bytes, type_mime: str, *, types_acceptes: set[str], taille_max_octets: int) -> None:
    if not contenu:
        raise ErreurRegle("Le fichier est vide.")
    formats = ", ".join(NOMS_FORMATS[t] for t in NOMS_FORMATS if t in types_acceptes)
    if type_mime not in types_acceptes or not contenu.startswith(_SIGNATURES[type_mime]):
        raise ErreurRegle(f"Ce fichier n'est pas accepté : envoyez un {formats}.")
    if len(contenu) > taille_max_octets:
        taille_max = taille_max_octets // (1024 * 1024)
        raise ErreurRegle(f"Le fichier est trop lourd : {taille_max} Mo au maximum (une photo de téléphone suffit).")


def enregistrer(db: Session, compte: Compte, *, nom_fichier: str, type_mime: str, contenu: bytes, maintenant: datetime) -> Fichier:
    """Range le fichier (déjà vérifié) dans le stockage et crée sa ligne FICHIER."""
    fichier = Fichier(
        depose_par_id=compte.id,
        cle_stockage=stockage.deposer(contenu, type_mime),
        nom_origine=nom_fichier[:200],
        type_mime=type_mime,
        taille_octets=len(contenu),
        depose_le=maintenant,
    )
    db.add(fichier)
    db.flush()
    return fichier
