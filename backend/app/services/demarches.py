"""Démarches administratives : le chiffre d'affaires à déclarer à l'URSSAF, par mois et par trimestre, préparé à
partir des factures faites par rafals (RM-DEMARCHES.md, lot 6.1 ; choix proposés par Claude le 03/10/2026, à valider
par Raphael). rafals prépare le chiffre et rappelle la date ; il ne déclare rien à la place du prestataire.
Rien n'est enregistré : tout se calcule à partir des factures."""

import calendar
from dataclasses import dataclass
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.factures import Facture
from app.modeles.prestataires import Prestataire
from app.services import factures

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
