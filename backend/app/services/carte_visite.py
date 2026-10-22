"""Ma carte de visite (lot 10.4, regles-metier/RM-CARTE-VISITE.md) : deux PDF fabriqués à la demande. Seules la couleur
et la petite phrase sont gardées (schema_v33, dans PRESTATAIRE) ; le PDF, lui, n'est jamais stocké.
- la planche : une page A4 avec 10 cartes identiques (2 × 5) et des repères de coupe, à imprimer chez soi ;
- la carte seule : une page de 8,5 × 5,5 cm, pour un imprimeur.
Le carré à scanner (QR code) est calculé par la bibliothèque `segno` (choix de Raphael du 22/10/2026), puis dessiné
en petits carrés noirs dans le PDF écrit à la main (comme les factures, services/pdf_facture.py)."""

import io
import unicodedata
from dataclasses import dataclass
from datetime import datetime

import segno
from sqlalchemy.orm import Session

from app import config
from app.modeles.comptes import Compte
from app.modeles.metiers import Metier
from app.modeles.prestataires import Commune, Prestataire
from app.services import avis as service_avis
from app.services.erreurs import ErreurRegle
from app.services.pdf_facture import HAUTEUR, LARGEUR, Page, assembler
from app.services.prestataires import aujourd_hui, en_cours, metiers_secondaires

MM = 72 / 25.4  # 1 mm en points PDF
CARTE_L, CARTE_H = 85 * MM, 55 * MM  # format habituel d'une carte de visite
COLONNES, LIGNES = 2, 5  # 10 cartes sur la planche A4
REPERE = 5 * MM  # longueur des repères de coupe, dans les marges
METIER_MAX = 30  # au-delà, le métier secondaire n'est pas ajouté (« Plombier · Chauffagiste » tient)

PAS_DE_SIRET = "Les cartes de visite sont réservées aux prestataires avec un SIRET vérifié."
PAS_ACTIF = {
    "en_pause": "Votre profil est en pause : sa page publique est fermée, le carré à scanner ne mènerait nulle part. "
                "Reprenez votre activité d'abord.",
    "bloque": "Votre profil est bloqué par l'administrateur de rafals : sa page publique est fermée. Contactez-le.",
    "arrete": "Votre activité est arrêtée : sa page publique est fermée.",
}
SANS_TELEPHONE = "Ajoutez d'abord votre téléphone dans Mon profil › Mon compte › Mes informations."

# Les 6 couleurs toutes prêtes (Raphael, 22/10/2026 : « toute pretes ») : code rangé dans la base → nom et teinte.
# Toutes assez foncées pour que le nom reste lisible et que le carré se scanne bien. La liste de la base
# (contrainte prestataire_carte_couleur_connue, schema_v33.sql) doit rester la même.
COULEURS = {
    "vert": ("Vert rafals", "#2F6B4F"),
    "bleu-nuit": ("Bleu nuit", "#1D3A5F"),
    "orange": ("Orange", "#C4561B"),
    "bordeaux": ("Bordeaux", "#7A1F2B"),
    "violet": ("Violet", "#4B2E83"),
    "noir": ("Noir", "#1D2620"),
}
PHRASE_MAX = 40
COULEUR_INCONNUE = "Choisissez une des 6 couleurs proposées."


@dataclass
class Contenu:
    """Ce qui est écrit sur la carte. Ex. « Karim Benali », « Plombier · Chauffagiste », « Pessac », « 4,8/5 · 23 avis sur rafals »."""

    nom: str
    metier: str
    ville: str
    note: str
    telephone: str | None  # seulement si le prestataire l'a demandé
    adresse: str  # la page publique, ex. « https://rafals.fr/prestataires/12 »
    couleur: str = "vert"  # un code de COULEURS, ex. « bleu-nuit »
    phrase: str | None = None  # ex. « Devis gratuit, intervention sous 48 h »


def raison_du_refus(prestataire: Prestataire) -> str | None:
    """Pourquoi la carte ne peut pas être téléchargée (SIRET pas vérifié, profil pas actif), ou None si elle peut l'être."""
    if prestataire.siret_statut != "verifie":
        return PAS_DE_SIRET
    return PAS_ACTIF.get(prestataire.statut) if prestataire.statut != "actif" else None


def adresse_publique(prestataire: Prestataire) -> str:
    """Ce que contient le carré à scanner ; sur le PC de Raphael « http://localhost:5174/prestataires/12 »."""
    return f"{config.ADRESSE_SITE.rstrip('/')}/prestataires/{prestataire.id}"


def texte_note(somme: int, nombre: int) -> str:
    """« 4,8/5 · 23 avis sur rafals », « 5,0/5 · 1 avis sur rafals » ; sans avis : « Nouveau sur rafals »."""
    if not nombre:
        return "Nouveau sur rafals"
    return f"{somme / nombre:.1f}".replace(".", ",") + f"/5 · {nombre} avis sur rafals"


def verifier(prestataire: Prestataire, compte: Compte, *, avec_telephone: bool) -> None:
    """Avant de fabriquer un PDF : SIRET vérifié, profil actif, et un téléphone dans le compte s'il est demandé."""
    if (raison := raison_du_refus(prestataire)) is not None:
        raise ErreurRegle(raison, 403)
    if avec_telephone and not compte.telephone:
        raise ErreurRegle(SANS_TELEPHONE)


def verifier_reglages(db: Session, couleur: str, phrase: str | None) -> tuple[str, str | None]:
    """La couleur doit être une des 6 ; la phrase passe le filtre commun (40 caractères, mots interdits, IA).
    Rend (couleur, phrase nettoyée ou None si vide)."""
    if couleur not in COULEURS:
        raise ErreurRegle(COULEUR_INCONNUE)
    if not (phrase or "").strip():
        return couleur, None
    return couleur, service_avis.verifier_texte(db, phrase or "", 1, "La petite phrase", PHRASE_MAX)


def enregistrer(db: Session, prestataire: Prestataire, couleur: str, phrase: str | None) -> Prestataire:
    """[Enregistrer ma carte] : la couleur et la phrase sont gardées pour les prochaines visites."""
    if (raison := raison_du_refus(prestataire)) is not None:
        raise ErreurRegle(raison, 403)
    prestataire.carte_couleur, prestataire.carte_phrase = verifier_reglages(db, couleur, phrase)
    return prestataire


def contenu(db: Session, prestataire: Prestataire, compte: Compte, *, avec_telephone: bool, maintenant: datetime,
            couleur: str | None = None, phrase: str | None = None) -> Contenu:
    """Le contenu de la carte, tel qu'il est dans le profil aujourd'hui (aussi pour l'aperçu, même verrouillé).
    `couleur` / `phrase` : celles affichées sur la page, pas encore enregistrées (sinon celles du profil)."""
    jour = aujourd_hui(maintenant)
    # Le métier principal, et un métier secondaire s'il tient sur la ligne
    noms = [db.get_one(Metier, prestataire.metier_principal_id).nom] if en_cours(prestataire.metier_principal_fin_le, jour) else []
    noms += [db.get_one(Metier, i).nom for i in metiers_secondaires(db, prestataire, jour)]
    metier = noms[0] if noms else ""
    if len(noms) > 1 and len(f"{metier} · {noms[1]}") <= METIER_MAX:
        metier = f"{metier} · {noms[1]}"
    somme, nombre = service_avis.notes(db, [prestataire.id]).get(prestataire.id, (0, 0))
    return Contenu(
        nom=prestataire.nom_affiche, metier=metier, ville=db.get_one(Commune, prestataire.commune_id).nom,
        note=texte_note(somme, nombre), telephone=compte.telephone if avec_telephone and compte.telephone else None,
        adresse=adresse_publique(prestataire),
        couleur=couleur if couleur is not None else prestataire.carte_couleur,
        phrase=phrase if couleur is not None else prestataire.carte_phrase,
    )


def carre_svg(adresse: str, couleur: str = "vert") -> bytes:
    """Le carré à scanner en image, pour l'aperçu de la page « Ma carte de visite ». Fichier SVG complet (avec son
    « xmlns ») : sans lui, le navigateur n'affiche pas l'image (svg_inline ne sert qu'au milieu d'une page HTML)."""
    sortie = io.BytesIO()
    segno.make(adresse, error="m").save(sortie, kind="svg", scale=4, border=0, dark=COULEURS.get(couleur, COULEURS["vert"])[1], xmldecl=False)
    return sortie.getvalue()


def nom_de_fichier(nom: str, planche: bool) -> str:
    """« Karim Benali » → « carte-de-visite-karim-benali-planche.pdf » (sans accents ni espaces)."""
    simple = unicodedata.normalize("NFKD", nom).encode("ascii", "ignore").decode().lower()
    morceaux = "-".join(m for m in "".join(ch if ch.isalnum() else " " for ch in simple).split()) or "rafals"
    return f"carte-de-visite-{morceaux}{'-planche' if planche else ''}.pdf"


def _rgb(couleur: str) -> bytes:
    """« bleu-nuit » → « 0.114 0.227 0.373 » : la teinte en langage PDF."""
    teinte = COULEURS.get(couleur, COULEURS["vert"])[1]
    return b"%.3f %.3f %.3f" % tuple(int(teinte[i:i + 2], 16) / 255 for i in (1, 3, 5))


def _taille(texte: str, taille: float, largeur: float) -> float:
    """Réduit la police si le texte dépasse : Helvetica fait environ 0,55 × la taille par caractère."""
    return min(taille, largeur / max(1, len(texte) * 0.55))


def _dessiner_carte(page: Page, c: Contenu, x: float, y: float) -> None:
    """Une carte dont le coin en bas à gauche est en (x, y), en points."""
    marge = 5 * MM
    bande = 3 * MM  # la bande de couleur, sur le côté gauche
    gauche = bande + 4 * MM  # le texte commence après la bande
    cote_qr = 25 * MM
    texte_l = CARTE_L - gauche - marge - cote_qr - 3 * MM  # la colonne de texte, à gauche du carré
    teinte = _rgb(c.couleur)

    def ecrire(texte: str, hauteur: float, taille: float, police: str = "normal") -> None:
        page.y = y + hauteur
        page.ecrire(texte, x=x + gauche, taille=_taille(texte, taille, texte_l), police=police)  # type: ignore[arg-type]

    page.contenu.append(b"%s rg %.2f %.2f %.2f %.2f re f 0 g" % (teinte, x, y, bande, CARTE_H))
    page.contenu.append(teinte + b" rg")  # le nom en couleur
    ecrire(c.nom, CARTE_H - marge - 12, 13, "gras")
    page.contenu.append(b"0 g")
    ecrire(c.metier, CARTE_H - marge - 27, 9.5)
    ecrire(c.ville, CARTE_H - marge - 39, 8.5)
    if c.phrase:
        ecrire(c.phrase, CARTE_H - marge - 52, 8)
    ecrire(c.note, 4 * MM + 26, 8)
    if c.telephone:
        ecrire(c.telephone, 4 * MM + 13, 9.5, "gras")
    page.y = y + 4 * MM - 1
    page.ecrire("rafals.", x=x + gauche, taille=6.5)

    # Le carré à scanner, à droite, et sa légende dessous
    qr = segno.make(c.adresse, error="m")
    lignes = list(qr.matrix_iter(border=0))
    module = cote_qr / len(lignes)
    qx, qy = x + CARTE_L - marge - cote_qr, y + (CARTE_H - cote_qr) / 2 + 3
    carres = [
        b"%.2f %.2f %.2f %.2f re" % (qx + col * module, qy + cote_qr - (rang + 1) * module, module + 0.05, module + 0.05)
        for rang, ligne in enumerate(lignes) for col, noir in enumerate(ligne) if noir
    ]
    page.contenu.append(teinte + b" rg\n" + b"\n".join(carres) + b"\nf 0 g")
    page.y = qy - 9
    page.ecrire("Mes avis et mes photos", x=qx + (cote_qr - 22 * 6 * 0.5) / 2, taille=6)


def pdf_carte(c: Contenu) -> bytes:
    """Une carte au format exact (8,5 × 5,5 cm), pour un imprimeur."""
    page = Page()
    _dessiner_carte(page, c, 0, 0)
    return assembler(page, f"Carte de visite — {c.nom}", largeur=CARTE_L, hauteur=CARTE_H)


def pdf_planche(c: Contenu) -> bytes:
    """Une page A4 avec 10 cartes identiques et des repères de coupe dans les marges."""
    page = Page()
    gauche = (LARGEUR - COLONNES * CARTE_L) / 2
    bas = (HAUTEUR - LIGNES * CARTE_H) / 2
    for colonne in range(COLONNES):
        for ligne in range(LIGNES):
            _dessiner_carte(page, c, gauche + colonne * CARTE_L, bas + ligne * CARTE_H)
    # Repères de coupe : un petit trait gris en face de chaque ligne de coupe, en dehors des cartes
    traits = []
    for i in range(COLONNES + 1):
        cx = gauche + i * CARTE_L
        haut = bas + LIGNES * CARTE_H
        traits += [(cx, bas - 2 - REPERE, cx, bas - 2), (cx, haut + 2, cx, haut + 2 + REPERE)]
    for i in range(LIGNES + 1):
        cy = bas + i * CARTE_H
        droite = gauche + COLONNES * CARTE_L
        traits += [(gauche - 2 - REPERE, cy, gauche - 2, cy), (droite + 2, cy, droite + 2 + REPERE, cy)]
    page.contenu.append(b"0.6 G\n" + b"\n".join(b"%.2f %.2f m %.2f %.2f l S" % t for t in traits) + b"\n0 G")
    return assembler(page, f"Cartes de visite — {c.nom}")
