"""Photos réduites à l'envoi (25/11/2026) : 1600 pixels au plus sur le grand côté, pour que les pages chargent vite."""

import io

from PIL import Image

from app import reglages
from app.services.fichiers import reduire_photo


def _image(largeur: int, hauteur: int, format_: str) -> bytes:
    """Une image avec du bruit (comme une vraie photo), sinon elle se compresse trop bien."""
    image = Image.effect_noise((largeur, hauteur), 60).convert("RGB")
    sortie = io.BytesIO()
    image.save(sortie, format_, **({"quality": 98} if format_ == "JPEG" else {}))
    return sortie.getvalue()


def test_grande_photo_jpeg_reduite():
    """Ex. photo de téléphone 4000 × 3000 → 1600 × 1200, bien plus légère."""
    avant = _image(4000, 3000, "JPEG")
    apres = reduire_photo(avant, "image/jpeg")
    with Image.open(io.BytesIO(apres)) as image:
        assert image.format == "JPEG"
        assert image.size == (reglages.PHOTO_COTE_MAX_PIXELS, 1200)
    assert len(apres) < len(avant)


def test_photo_prise_en_hauteur_remise_a_l_endroit():
    """Le téléphone range parfois la photo couchée avec une étiquette « tourner de 90° » : on la tourne vraiment."""
    image = Image.effect_noise((3000, 2000), 60).convert("RGB")
    etiquettes = image.getexif()
    etiquettes[0x0112] = 6  # orientation : tourner de 90°
    sortie = io.BytesIO()
    image.save(sortie, "JPEG", quality=98, exif=etiquettes)
    with Image.open(io.BytesIO(reduire_photo(sortie.getvalue(), "image/jpeg"))) as reduite:
        assert reduite.size == (1067, 1600)
        assert reduite.getexif().get(0x0112) in (None, 1)


def test_grande_image_png_reste_png():
    apres = reduire_photo(_image(2400, 1200, "PNG"), "image/png")
    with Image.open(io.BytesIO(apres)) as image:
        assert image.format == "PNG" and image.size == (1600, 800)


def test_petite_photo_gardee_telle_quelle():
    avant = _image(800, 600, "JPEG")
    assert reduire_photo(avant, "image/jpeg") == avant


def test_fichier_illisible_garde_tel_quel():
    faux = b"\xff\xd8\xff zztest pas une vraie image"
    assert reduire_photo(faux, "image/jpeg") == faux
