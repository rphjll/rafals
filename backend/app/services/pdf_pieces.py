"""Les PDF du dossier de création d'auto-entreprise (lot 7.1) : le guichet de l'État n'accepte que des PDF.
- une page de texte (le pouvoir donné à rafals, l'attestation sur l'honneur) : mêmes outils que la facture ;
- une photo JPG rangée telle quelle dans une page PDF (le format PDF sait contenir un JPG sans le transformer).
Pourquoi pas une bibliothèque : même raison que pour la facture (pas de conteneur à reconstruire)."""

from app.services.erreurs import ErreurRegle
from app.services.pdf_facture import HAUTEUR, LARGEUR, MARGE, Page, assembler, couper, fichier_pdf

LARGEUR_TEXTE = 92  # caractères par ligne en Helvetica 11 sur une page A4


def texte_en_pdf(titre: str, paragraphes: list[str]) -> bytes:
    """Ex. texte_en_pdf("Pouvoir", ["Je soussigné Karim BENALI…", "Fait sur rafals le 04/10/2026."])."""
    page = Page()
    page.ligne(titre, taille=16, police="gras")
    page.descendre(10)
    for paragraphe in paragraphes:
        for ligne in couper(paragraphe, LARGEUR_TEXTE):
            page.ligne(ligne, taille=11)
        page.descendre(8)
    return assembler(page, titre)


def _taille_jpeg(contenu: bytes) -> tuple[int, int, int]:
    """Largeur, hauteur et nombre de couleurs, lus dans l'en-tête du JPG (bloc « SOF »)."""
    position = 2
    while position + 9 < len(contenu):
        if contenu[position] != 0xFF:
            break
        marque = contenu[position + 1]
        longueur = int.from_bytes(contenu[position + 2:position + 4], "big")
        if 0xC0 <= marque <= 0xCF and marque not in (0xC4, 0xC8, 0xCC):
            hauteur = int.from_bytes(contenu[position + 5:position + 7], "big")
            largeur = int.from_bytes(contenu[position + 7:position + 9], "big")
            return largeur, hauteur, contenu[position + 9]
        position += 2 + longueur
    raise ErreurRegle("Cette photo est illisible : reprenez-la ou envoyez un PDF.")


def jpeg_en_pdf(contenu: bytes) -> bytes:
    """Une page A4 avec la photo, la plus grande possible sans la déformer."""
    largeur, hauteur, couleurs = _taille_jpeg(contenu)
    if not largeur or not hauteur or couleurs not in (1, 3):
        raise ErreurRegle("Cette photo est illisible : reprenez-la ou envoyez un PDF.")
    echelle = min((LARGEUR - 2 * MARGE) / largeur, (HAUTEUR - 2 * MARGE) / hauteur)
    l, h = largeur * echelle, hauteur * echelle
    flux = b"q %.1f 0 0 %.1f %.1f %.1f cm /Im1 Do Q" % (l, h, (LARGEUR - l) / 2, (HAUTEUR - h) / 2)
    objets = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %d %d] /Contents 4 0 R /Resources << /XObject << /Im1 5 0 R >> >> >>"
        % (LARGEUR, HAUTEUR),
        b"<< /Length %d >>\nstream\n%s\nendstream" % (len(flux), flux),
        b"<< /Type /XObject /Subtype /Image /Width %d /Height %d /ColorSpace /%s /BitsPerComponent 8 /Filter /DCTDecode "
        b"/Length %d >>\nstream\n%s\nendstream" % (largeur, hauteur, b"DeviceRGB" if couleurs == 3 else b"DeviceGray",
                                                   len(contenu), contenu),
    ]
    return fichier_pdf(objets)
