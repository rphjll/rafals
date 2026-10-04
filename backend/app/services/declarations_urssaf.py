"""Déclarer à l'URSSAF depuis rafals (RM-DEMARCHES.md, lot 7.3 ; maquette et MLD validés par Raphael le 04/10/2026).
Le prestataire donne son accord une fois (le « mandat »), puis clique [Déclarer] pour chaque période finie : rafals
envoie le montant (encaissé sur rafals + encaissé ailleurs) à l'URSSAF (services/urssaf.py) et garde la preuve.
rafals déclare, il ne paie pas. Rien ne part sans un clic."""

import calendar
from dataclasses import dataclass
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modeles.comptes import Compte
from app.modeles.metiers import Metier
from app.modeles.prestataires import Prestataire
from app.modeles.urssaf import DeclarationUrssaf, MandatUrssaf
from app.services import demarches, journal, mails, urssaf
from app.services.creation_entreprise import forme_exercice, numero_secu_valide
from app.services.erreurs import ErreurRegle

TEXTE_MANDAT = ("Je donne mandat à rafals pour déclarer mon chiffre d'affaires à l'URSSAF, en mon nom, chaque fois que je "
                "clique sur [Déclarer]. Je peux le retirer quand je veux.")
SITE = "autoentrepreneur.urssaf.fr"


@dataclass
class ADeclarer:
    """La période que le prestataire peut déclarer maintenant."""

    periodicite: str
    debut: date
    fin: date
    nom: str  # « 3e trimestre 2026 »
    limite: date
    montant_rafals_centimes: int
    nombre_factures: int


# ---------- L'accord ----------


def mandat_en_cours(db: Session, prestataire: Prestataire) -> MandatUrssaf | None:
    return db.scalar(select(MandatUrssaf).where(MandatUrssaf.prestataire_id == prestataire.id, MandatUrssaf.retire_le.is_(None)))


def _personne(prestataire: Prestataire, mandat: MandatUrssaf) -> urssaf.Personne:
    return urssaf.Personne(prestataire.siret or "", mandat.numero_secu or "")


def donner_mandat(db: Session, compte: Compte, prestataire: Prestataire, *, numero_secu: str, accepte: bool,
                  maintenant: datetime) -> MandatUrssaf:
    """Ex. Léa écrit son numéro de sécurité sociale et coche la case : rafals le signale à l'URSSAF."""
    if prestataire.siret_statut != "verifie":
        raise ErreurRegle("Il faut un SIRET vérifié pour déclarer à l'URSSAF depuis rafals.")
    if mandat_en_cours(db, prestataire) is not None:
        raise ErreurRegle("Vous avez déjà donné votre accord.")
    numero = "".join(numero_secu.split()).upper()
    if not numero_secu_valide(numero):
        raise ErreurRegle("Ce numéro de sécurité sociale n'est pas correct : recopiez les 15 chiffres de votre carte Vitale.")
    if not accepte:
        raise ErreurRegle("Cochez la case pour donner votre accord.")
    mandat = MandatUrssaf(prestataire_id=prestataire.id, numero_secu=numero, texte=TEXTE_MANDAT, donne_le=maintenant,
                          demonstration=not urssaf.disponible())
    try:
        urssaf.enregistrer_mandat(_personne(prestataire, mandat))
    except urssaf.UrssafRefus as refus:
        raise ErreurRegle(f"L'URSSAF n'a pas accepté : « {refus} » Si vous n'avez pas encore d'espace sur {SITE}, créez-le d'abord.") from refus
    except urssaf.UrssafIndisponible as panne:
        raise ErreurRegle("L'URSSAF ne répond pas : réessayez dans quelques minutes.", 503) from panne
    db.add(mandat)
    db.flush()
    journal.noter(db, auteur_id=compte.id, action="urssaf_donner_mandat", table_cible="mandat_urssaf", ligne_id=mandat.id,
                  apres={"prestataire_id": prestataire.id}, maintenant=maintenant)
    return mandat


def retirer_mandat(db: Session, compte: Compte, prestataire: Prestataire, maintenant: datetime) -> None:
    """L'accord est retiré : rafals le signale à l'URSSAF et efface le numéro de sécurité sociale. Les déclarations restent."""
    mandat = mandat_en_cours(db, prestataire)
    if mandat is None:
        raise ErreurRegle("Vous n'avez pas donné d'accord.")
    try:
        urssaf.annuler_mandat(_personne(prestataire, mandat))
    except urssaf.UrssafRefus:
        pass  # l'URSSAF ne le connaît plus : il est retiré de toute façon chez rafals
    except urssaf.UrssafIndisponible as panne:
        raise ErreurRegle("L'URSSAF ne répond pas : réessayez dans quelques minutes.", 503) from panne
    mandat.retire_le, mandat.numero_secu = maintenant, None
    journal.noter(db, auteur_id=compte.id, action="urssaf_retirer_mandat", table_cible="mandat_urssaf", ligne_id=mandat.id,
                  maintenant=maintenant)


# ---------- La période à déclarer ----------


def nature(db: Session, prestataire: Prestataire) -> str:
    """« services » ou « liberale », d'après le métier principal (même correspondance que la création d'entreprise)."""
    forme = forme_exercice(db, db.get_one(Metier, prestataire.metier_principal_id))
    return "liberale" if forme == "INDEPENDANTE" else "services"


def _fin(periodicite: str, debut: date) -> date:
    mois = debut.month if periodicite == "mois" else debut.month + 2
    return date(debut.year, mois, calendar.monthrange(debut.year, mois)[1])


def declarations(db: Session, prestataire: Prestataire) -> list[DeclarationUrssaf]:
    return list(db.scalars(select(DeclarationUrssaf).where(DeclarationUrssaf.prestataire_id == prestataire.id)
                           .order_by(DeclarationUrssaf.periode_debut)))


def _deja_declaree(db: Session, prestataire: Prestataire, debut: date, fin: date) -> bool:
    """Une déclaration couvre déjà tout ou partie de ces jours (ex. octobre déclaré, puis le 4e trimestre demandé)."""
    return any(d.periode_debut <= fin and _fin(d.periodicite, d.periode_debut) >= debut for d in declarations(db, prestataire))


def a_declarer(db: Session, prestataire: Prestataire, maintenant: datetime) -> ADeclarer | None:
    """La dernière période finie, si le prestataire a dit « chaque mois » ou « chaque trimestre », si sa date limite
    n'est pas passée et si elle n'est pas déjà déclarée. Ex. le 24/10/2026, chaque trimestre → juillet à septembre."""
    periodicite = prestataire.declaration_periodicite
    if periodicite is None:
        return None
    aujourd_hui = maintenant.astimezone(demarches.PARIS).date()
    debut, limite, nom = demarches.periode_a_declarer(periodicite, aujourd_hui)
    fin = _fin(periodicite, debut)
    if aujourd_hui > limite or _deja_declaree(db, prestataire, debut, fin):
        return None
    mois, trimestres = demarches.chiffre_d_affaires(db, prestataire, debut.year, maintenant)
    periode = mois[debut.month - 1] if periodicite == "mois" else trimestres[(debut.month - 1) // 3]
    return ADeclarer(periodicite, debut, fin, nom, limite, periode.encaisse_centimes, periode.nombre_factures)


def _pret(db: Session, prestataire: Prestataire, ailleurs_centimes: int, maintenant: datetime) -> tuple[MandatUrssaf, ADeclarer, int]:
    mandat = mandat_en_cours(db, prestataire)
    if mandat is None:
        raise ErreurRegle("Donnez d'abord votre accord à rafals.")
    if prestataire.declaration_periodicite is None:
        raise ErreurRegle("Dites d'abord si vous déclarez chaque mois ou chaque trimestre (« Rappels par mail »).")
    periode = a_declarer(db, prestataire, maintenant)
    if periode is None:
        raise ErreurRegle(f"Il n'y a rien à déclarer depuis rafals pour le moment (période déjà déclarée, ou date limite passée : voyez {SITE}).")
    if not 0 <= ailleurs_centimes <= 100_000_000:
        raise ErreurRegle("Le montant encaissé ailleurs doit être positif (0 s'il n'y a rien).")
    total = periode.montant_rafals_centimes + ailleurs_centimes
    if periode.montant_rafals_centimes < 0:
        raise ErreurRegle(f"Vos remboursements dépassent vos ventes sur cette période : déclarez sur {SITE}.")
    return mandat, periode, total


def estimer(db: Session, prestataire: Prestataire, ailleurs_centimes: int, maintenant: datetime) -> tuple[int, int]:
    """(total déclaré, cotisations estimées), montrés avant l'envoi. Ex. 1 250,00 € + 200,00 € → (145000, 30740)."""
    mandat, periode, total = _pret(db, prestataire, ailleurs_centimes, maintenant)
    try:
        resultat = urssaf.estimer(_personne(prestataire, mandat), nature(db, prestataire), periode.debut, periode.fin, total)
    except urssaf.UrssafRefus as refus:
        raise ErreurRegle(f"L'URSSAF n'a pas accepté : « {refus} »") from refus
    except urssaf.UrssafIndisponible as panne:
        raise ErreurRegle("L'URSSAF ne répond pas : réessayez dans quelques minutes.", 503) from panne
    return total, resultat.cotisations_centimes


def declarer(db: Session, compte: Compte, prestataire: Prestataire, *, ailleurs_centimes: int, certifie: bool,
             maintenant: datetime) -> DeclarationUrssaf:
    """Le clic [Envoyer à l'URSSAF]. Une période déclarée ne se redéclare pas depuis rafals."""
    from app.services import paiements  # (import ici : même raison que dans demarches)

    mandat, periode, total = _pret(db, prestataire, ailleurs_centimes, maintenant)
    if not certifie:
        raise ErreurRegle("Cochez la case : vous certifiez que ce montant est exact.")
    sorte = nature(db, prestataire)
    try:
        resultat = urssaf.declarer(_personne(prestataire, mandat), sorte, periode.debut, periode.fin, total,
                                   cle_unique=f"rafals-{prestataire.id}-{periode.periodicite}-{periode.debut:%Y%m%d}")
    except urssaf.UrssafRefus as refus:
        raise ErreurRegle(f"L'URSSAF n'a pas accepté la déclaration : « {refus} » Rien n'a été envoyé. Vérifiez sur {SITE}.") from refus
    except urssaf.UrssafIndisponible as panne:
        raise ErreurRegle("L'URSSAF ne répond pas : réessayez dans quelques minutes. Rien n'est envoyé deux fois.", 503) from panne
    declaration = DeclarationUrssaf(
        prestataire_id=prestataire.id, mandat_id=mandat.id, periodicite=periode.periodicite, periode_debut=periode.debut,
        nature=sorte, montant_rafals_centimes=periode.montant_rafals_centimes, montant_ailleurs_centimes=ailleurs_centimes,
        cotisations_centimes=resultat.cotisations_centimes, declaree_le=maintenant, reference_urssaf=resultat.reference,
        demonstration=not urssaf.disponible(),
    )
    db.add(declaration)
    db.flush()
    journal.noter(db, auteur_id=compte.id, action="urssaf_declarer", table_cible="declaration_urssaf", ligne_id=declaration.id,
                  apres={"periode_debut": str(periode.debut), "total_centimes": total}, maintenant=maintenant)
    apostrophe = "d'" if periode.nom[0] in "ao" else "du " if periode.periodicite == "trimestre" else "de "
    demonstration = " (mode démonstration : rien n'a été envoyé à l'URSSAF)" if declaration.demonstration else ""
    mails.envoyer_mail(
        compte.email, f"rafals : votre déclaration URSSAF {apostrophe}{periode.nom} est envoyée",
        f"Votre déclaration {apostrophe}{periode.nom} est envoyée{demonstration} : {paiements.euros(total)}, "
        f"cotisations {paiements.euros(resultat.cotisations_centimes)}. rafals a déclaré, il n'a pas payé : "
        f"le paiement des cotisations se fait sur {SITE}.")
    return declaration
