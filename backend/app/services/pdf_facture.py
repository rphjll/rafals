"""Le PDF d'une facture, fabriqué à la demande à partir de ce qui est figé dans la base (MLD 5.5, choix validé par
Raphael le 03/10/2026) : le même PDF à chaque téléchargement, rien d'autre n'est stocké.

Pourquoi pas une bibliothèque PDF : en ajouter une demanderait de reconstruire le conteneur du serveur ; une facture
d'une page (du texte et quelques traits) s'écrit directement dans le format PDF, avec ses polices de base."""

from dataclasses import dataclass, field

LARGEUR, HAUTEUR = 595, 842  # une page A4, en points
MARGE = 50
POLICES = {"normal": "F1", "gras": "F2", "chiffres": "F3"}  # Helvetica, Helvetica gras, Courier (chiffres alignés)
LARGEUR_COURIER = 0.6  # chaque caractère de Courier fait 0,6 × la taille : on peut aligner à droite


def _texte(valeur: str) -> bytes:
    """Texte PDF : accents français (jeu de caractères d'Europe de l'Ouest), parenthèses et barres protégées."""
    propre = valeur.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return propre.encode("cp1252", errors="replace")


@dataclass
class Page:
    """Une page sur laquelle on écrit de haut en bas ; `y` descend à chaque ligne."""

    y: float = HAUTEUR - MARGE
    contenu: list[bytes] = field(default_factory=list)

    def ecrire(self, texte: str, *, x: float = MARGE, taille: int = 10, police: str = "normal", droite: float | None = None) -> None:
        """`droite` : le texte finit à cette position (chiffres en Courier, alignés à droite)."""
        if droite is not None:
            police = "chiffres"
            x = droite - len(texte) * taille * LARGEUR_COURIER
        self.contenu.append(b"BT /%s %d Tf %.1f %.1f Td (%s) Tj ET" % (POLICES[police].encode(), taille, x, self.y, _texte(texte)))

    def trait(self) -> None:
        self.contenu.append(b"%.1f %.1f m %.1f %.1f l S" % (MARGE, self.y + 9, LARGEUR - MARGE, self.y + 9))

    def descendre(self, points: float = 14) -> None:
        self.y -= points

    def ligne(self, texte: str, **reglages) -> None:
        self.ecrire(texte, **reglages)
        self.descendre()


def assembler(page: Page, titre: str) -> bytes:
    """Le fichier PDF : la page, ses 3 polices de base, et la table qui dit où trouver chaque morceau."""
    flux = b"0.5 w\n" + b"\n".join(page.contenu)
    police = b"<< /Type /Font /Subtype /Type1 /BaseFont /%s /Encoding /WinAnsiEncoding >>"
    objets = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %d %d] /Contents 4 0 R /Resources << /Font << /F1 5 0 R /F2 6 0 R /F3 7 0 R >> >> >>"
        % (LARGEUR, HAUTEUR),
        b"<< /Length %d >>\nstream\n%s\nendstream" % (len(flux), flux),
        police % b"Helvetica", police % b"Helvetica-Bold", police % b"Courier",
        b"<< /Title (%s) /Producer (rafals) >>" % _texte(titre),
    ]
    return fichier_pdf(objets, avec_infos=True)


def fichier_pdf(objets: list[bytes], *, avec_infos: bool = False) -> bytes:
    """Range les morceaux (« objets ») dans un fichier PDF, avec la table qui dit où trouver chacun.
    `avec_infos` : le dernier objet est la fiche d'informations (titre, auteur)."""
    sortie = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    positions = []
    for rang, objet in enumerate(objets, start=1):
        positions.append(len(sortie))
        sortie += b"%d 0 obj\n%s\nendobj\n" % (rang, objet)
    table = len(sortie)
    sortie += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objets) + 1)
    for position in positions:
        sortie += b"%010d 00000 n \n" % position
    infos = b" /Info %d 0 R" % len(objets) if avec_infos else b""
    sortie += b"trailer\n<< /Size %d /Root 1 0 R%s >>\nstartxref\n%d\n%%%%EOF\n" % (len(objets) + 1, infos, table)
    return bytes(sortie)


def couper(texte: str, largeur: int) -> list[str]:
    """Coupe un texte long en lignes d'au plus `largeur` caractères, sans couper les mots."""
    lignes: list[str] = []
    courante = ""
    for mot in texte.split():
        if courante and len(courante) + 1 + len(mot) > largeur:
            lignes.append(courante)
            courante = mot
        else:
            courante = f"{courante} {mot}".strip()
    return lignes + [courante] if courante else lignes or [""]
