"""Fichiers déposés (accord des parents, photo du prestataire…) : vérification puis rangement dans le stockage.
Un seul endroit pour ces règles (réutilisation)."""

import io
from datetime import datetime

from PIL import Image, ImageOps
from sqlalchemy.orm import Session

from app import reglages
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


def reduire_photo(contenu: bytes, type_mime: str) -> bytes:
    """Photo trop grande ramenée à 1600 pixels sur le grand côté (25/11/2026), pour que les pages chargent vite.
    Ex. 4000 × 3000 et 2,7 Mo → 1600 × 1200 et environ 250 Ko ; une photo de 800 × 600 reste telle quelle.
    Remise à l'endroit si le téléphone l'avait prise de côté ; les informations cachées (lieu GPS) disparaissent.
    Image illisible par Pillow ou résultat plus lourd : on garde l'original."""
    try:
        with Image.open(io.BytesIO(contenu)) as image:
            image.load()
            cote_max = reglages.PHOTO_COTE_MAX_PIXELS
            if max(image.size) <= cote_max and len(contenu) <= 600 * 1024:
                return contenu
            image = ImageOps.exif_transpose(image)
            image.thumbnail((cote_max, cote_max), Image.Resampling.LANCZOS)
            sortie = io.BytesIO()
            if type_mime == "image/jpeg":
                image.convert("RGB").save(sortie, "JPEG", quality=reglages.PHOTO_QUALITE_JPEG, optimize=True, progressive=True)
            else:
                image.save(sortie, "PNG", optimize=True)
    except (OSError, ValueError, Image.DecompressionBombError):
        return contenu
    reduite = sortie.getvalue()
    return reduite if len(reduite) < len(contenu) else contenu


def enregistrer(
    db: Session, compte: Compte, *, nom_fichier: str, type_mime: str, contenu: bytes, maintenant: datetime,
    photo: bool = False,
) -> Fichier:
    """Range le fichier (déjà vérifié) dans le stockage et crée sa ligne FICHIER.
    photo=True : une photo (profil, travail, demande, message), réduite si elle est trop grande. Les documents
    (accord des parents, pièces d'identité) et les captures d'écran gardent leur taille, pour rester lisibles."""
    if photo:
        contenu = reduire_photo(contenu, type_mime)
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
