"""Démarches administratives : le chiffre d'affaires à déclarer à l'URSSAF, par mois et par trimestre, préparé à
partir des factures faites par rafals (RM-DEMARCHES.md, lot 6.1 ; choix proposés par Claude le 03/10/2026, à valider
par Raphael). rafals prépare le chiffre et rappelle la date ; il ne déclare rien à la place du prestataire.
Rien n'est enregistré : tout se calcule à partir des factures."""

import calendar
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.factures import Facture
from app.modeles.comptes import Compte
from app.modeles.prestataires import Prestataire
from app.modeles.signalements import RappelDeclaration
from app.modeles.urssaf import DeclarationUrssaf
from app.services import factures, journal, mails, notifications, paiements
from app.services.erreurs import ErreurRegle

PARIS = reglages.FUSEAU_AFFICHAGE


@dataclass
class Periode:
    """Un mois (rang 1 à 12) ou un trimestre (rang 1 à 4) : ce qui a été encaissé, et jusqu'à quand le déclarer."""

    rang: int
    debut: date
    fin: date  # dernier jour compris
    encaisse_centimes: int
    nombre_factures: int
    a_declarer_avant: date
    terminee: bool  # la période est finie : le chiffre ne bougera plus


def limite_du_mois(annee: int, mois: int) -> date:
    """La fin du mois suivant. Ex. octobre 2026 → 30/11/2026 ; décembre 2026 → 31/01/2027."""
    annee_suivante, mois_suivant = (annee + 1, 1) if mois == 12 else (annee, mois + 1)
    return date(annee_suivante, mois_suivant, calendar.monthrange(annee_suivante, mois_suivant)[1])


def limite_du_trimestre(annee: int, trimestre: int) -> date:
    """30 avril, 31 juillet, 31 octobre, 31 janvier. Ex. juillet à septembre 2026 → 31/10/2026."""
    return (date(annee, 4, 30), date(annee, 7, 31), date(annee, 10, 31), date(annee + 1, 1, 31))[trimestre - 1]


def encaisse(db: Session, facture: Facture) -> int:
    """Ce qui compte pour l'URSSAF : le total payé par le client ; hors taxe si le prestataire facture la TVA.
    Un avoir (remboursement) est négatif."""
    t = factures.totaux(db, facture)
    return t.ht if facture.mention_tva is None else t.ttc


def chiffre_d_affaires(db: Session, prestataire: Prestataire, annee: int, maintenant: datetime) -> tuple[list[Periode], list[Periode]]:
    """Les 12 mois et les 4 trimestres de l'année : ventes moins avoirs, à la date de la facture (heure de Paris).
    Ex. octobre : 50,00 € + 1 190,00 € + 60,00 € - 50,00 € (un avoir) = 1 250,00 €, à déclarer avant le 30/11."""
    aujourd_hui = maintenant.astimezone(PARIS).date()
    par_mois = {mois: [0, 0] for mois in range(1, 13)}  # mois → [centimes, nombre de factures]
    lignes = db.scalars(select(Facture).where(Facture.prestataire_id == prestataire.id, Facture.sorte.in_(("vente", "avoir"))))
    for facture in lignes:
        jour = facture.emise_le.astimezone(PARIS).date()
        if jour.year == annee:
            par_mois[jour.month][0] += encaisse(db, facture)
            par_mois[jour.month][1] += 1
    mois = []
    for rang in range(1, 13):
        fin = date(annee, rang, calendar.monthrange(annee, rang)[1])
        mois.append(Periode(rang, date(annee, rang, 1), fin, par_mois[rang][0], par_mois[rang][1], limite_du_mois(annee, rang),
                            fin < aujourd_hui))
    trimestres = []
    for rang in range(1, 5):
        les_mois = mois[(rang - 1) * 3:rang * 3]
        trimestres.append(Periode(rang, les_mois[0].debut, les_mois[-1].fin, sum(m.encaisse_centimes for m in les_mois),
                                  sum(m.nombre_factures for m in les_mois), limite_du_trimestre(annee, rang),
                                  les_mois[-1].terminee))
    return mois, trimestres


# ---------- Mois ou trimestre, rappels par mail (lot 6.3) ----------

MOIS = ("janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre")


def choisir_periodicite(db: Session, prestataire: Prestataire, periodicite: str | None, maintenant: datetime) -> Prestataire:
    """« Je déclare chaque mois » ou « chaque trimestre » (comme choisi à l'URSSAF) ; vide : pas de rappel."""
    if periodicite not in (None, "mois", "trimestre"):
        raise ErreurRegle("Choisissez : chaque mois, chaque trimestre, ou pas de rappel.")
    avant = prestataire.declaration_periodicite
    prestataire.declaration_periodicite = periodicite
    journal.noter(db, auteur_id=prestataire.compte_id, action="choisir_periodicite_urssaf", table_cible="prestataire",
                  ligne_id=prestataire.id, avant={"declaration_periodicite": avant}, apres={"declaration_periodicite": periodicite},
                  maintenant=maintenant)
    return prestataire


def periode_a_declarer(periodicite: str, aujourd_hui: date) -> tuple[date, date, str]:
    """La dernière période finie : son 1er jour, sa date limite, son nom. Ex. le 23/11/2026, chaque mois →
    (01/10/2026, 30/11/2026, « octobre 2026 ») ; chaque trimestre → (01/07/2026, 31/10/2026, « 3e trimestre 2026 »)."""
    if periodicite == "mois":
        annee, mois = (aujourd_hui.year - 1, 12) if aujourd_hui.month == 1 else (aujourd_hui.year, aujourd_hui.month - 1)
        return date(annee, mois, 1), limite_du_mois(annee, mois), f"{MOIS[mois - 1]} {annee}"
    trimestre = (aujourd_hui.month - 1) // 3  # trimestre en cours, de 0 à 3 → le précédent est fini
    annee, rang = (aujourd_hui.year - 1, 4) if trimestre == 0 else (aujourd_hui.year, trimestre)
    return date(annee, (rang - 1) * 3 + 1, 1), limite_du_trimestre(annee, rang), f"{rang}{'er' if rang == 1 else 'e'} trimestre {annee}"


def envoyer_rappels(db: Session, maintenant: datetime) -> dict[str, int]:
    """Lancé toutes les heures : un mail 7 jours avant la date limite, un autre la veille, jamais deux fois le même.
    Ex. « Déclaration URSSAF d'octobre 2026 : 1 250,00 € à déclarer avant le 30/11/2026. »"""
    from app.services import paiements  # (import ici : même raison que dans factures)

    compte = {"rappels": 0}
    aujourd_hui = maintenant.astimezone(PARIS).date()
    concernes = db.scalars(select(Prestataire).where(Prestataire.declaration_periodicite.is_not(None),
                                                     Prestataire.siret_statut == "verifie",
                                                     Prestataire.statut.in_(("actif", "en_pause"))))
    for prestataire in concernes:
        debut, limite, nom = periode_a_declarer(prestataire.declaration_periodicite or "mois", aujourd_hui)
        if aujourd_hui > limite or aujourd_hui < limite - reglages.RAPPEL_URSSAF_AVANT:
            continue
        sorte = "veille" if aujourd_hui >= limite - timedelta(days=1) else "sept_jours"
        deja = db.scalar(select(RappelDeclaration.id).where(RappelDeclaration.prestataire_id == prestataire.id,
                                                            RappelDeclaration.periode_debut == debut,
                                                            RappelDeclaration.sorte == sorte))
        if deja is not None:
            continue
        declaree = db.scalar(select(DeclarationUrssaf.id).where(
            DeclarationUrssaf.prestataire_id == prestataire.id, DeclarationUrssaf.periode_debut == debut,
            DeclarationUrssaf.periodicite == prestataire.declaration_periodicite))
        if declaree is not None:  # déjà déclarée depuis rafals (lot 7.3) : plus de rappel
            continue
        mois, trimestres = chiffre_d_affaires(db, prestataire, debut.year, maintenant)
        periode = mois[debut.month - 1] if prestataire.declaration_periodicite == "mois" else trimestres[(debut.month - 1) // 3]
        db.add(RappelDeclaration(prestataire_id=prestataire.id, periode_debut=debut, sorte=sorte, envoye_le=maintenant))
        apostrophe = "d'" if nom[0] in "ao" else "de "
        mails.envoyer_mail(
            db.get_one(Compte, prestataire.compte_id).email, f"rafals : déclaration URSSAF {apostrophe}{nom}",
            f"Déclaration URSSAF {apostrophe}{nom} : {paiements.euros(periode.encaisse_centimes)} à déclarer avant le "
            f"{limite:%d/%m/%Y} (d'après vos factures sur rafals ; ajoutez ce que vous avez encaissé ailleurs). "
            "La déclaration se fait sur le site de l'URSSAF, même pour 0 €.")
        compte["rappels"] += 1
    return compte


# ---------- La barre de la TVA : prévenir à 80 % et au-delà du seuil (demande de Raphael du 17/10/2026) ----------


def prevenir_seuil_tva(db: Session, prestataire: Prestataire, facture: Facture, maintenant: datetime) -> None:
    """Appelé à chaque nouvelle facture de vente : une notification si elle fait passer 80 % du seuil, ou le seuil
    lui-même. Rien n'est enregistré : on compare le total de l'année avant et après cette facture.
    Ex. 1 : seuil 37 500 € ; Karim passe de 29 800 € à 30 050 € → « Vous approchez du seuil de TVA ».
    Ex. 2 : il passe de 37 400 € à 37 600 € → « Seuil de TVA dépassé ». Pas de barre pour qui facture déjà la TVA."""
    if prestataire.facture_tva or facture.sorte != "vente":
        return
    annee = facture.emise_le.astimezone(PARIS).year
    mois, _ = chiffre_d_affaires(db, prestataire, annee, maintenant)
    apres = sum(m.encaisse_centimes for m in mois)
    avant = apres - encaisse(db, facture)
    seuil = reglages.SEUIL_TVA_SERVICES_CENTIMES
    alerte = seuil * reglages.SEUIL_TVA_PREVENIR_POUR_CENT // 100
    if avant < seuil <= apres:
        notifications.prevenir(
            db, prestataire.compte_id, "Seuil de TVA dépassé",
            f"Vous avez encaissé {paiements.euros(apres)} en {annee}, plus que le seuil de TVA ({paiements.euros(seuil)}) : "
            "parlez-en à votre comptable ou à votre service des impôts.", "/mon-activite", maintenant)
    elif avant < alerte <= apres:
        notifications.prevenir(
            db, prestataire.compte_id, "Vous approchez du seuil de TVA",
            f"Vous avez encaissé {paiements.euros(apres)} en {annee} : {reglages.SEUIL_TVA_PREVENIR_POUR_CENT} % du seuil de TVA "
            f"({paiements.euros(seuil)}). Il vous reste {paiements.euros(seuil - apres)}.", "/mon-activite", maintenant)
