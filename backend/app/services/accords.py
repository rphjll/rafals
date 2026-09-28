"""Accord des parents pour les comptes de 16 et 17 ans. Règles : RM-COMPTES.md (âge minimum)."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.comptes import Compte
from app.modeles.fichiers import AccordParental
from app.services import fichiers, journal
from app.services.droits import accord_parental_necessaire
from app.services.erreurs import ErreurRegle


def dernier_accord(db: Session, compte: Compte) -> AccordParental | None:
    return db.scalar(
        select(AccordParental).where(AccordParental.compte_id == compte.id).order_by(AccordParental.id.desc()).limit(1)
    )


def deposer_accord(
    db: Session, compte: Compte, *, nom_fichier: str, type_mime: str, contenu: bytes, maintenant: datetime
) -> AccordParental:
    if not accord_parental_necessaire(compte, maintenant):
        raise ErreurRegle(f"Vous avez {reglages.AGE_MAJORITE} ans ou plus : aucun accord des parents n'est nécessaire.")
    precedent = dernier_accord(db, compte)
    if precedent is not None and precedent.statut == "accepte":
        raise ErreurRegle("L'accord de vos parents est déjà accepté.")
    if precedent is not None and precedent.statut == "en_attente":
        raise ErreurRegle("Un accord attend déjà la décision de l'administrateur.")

    fichiers.verifier(
        contenu, type_mime,
        types_acceptes=set(reglages.ACCORD_TYPES_ACCEPTES), taille_max_octets=reglages.ACCORD_TAILLE_MAX_OCTETS,
    )
    fichier = fichiers.enregistrer(db, compte, nom_fichier=nom_fichier, type_mime=type_mime, contenu=contenu, maintenant=maintenant)
    accord = AccordParental(compte_id=compte.id, fichier_id=fichier.id, statut="en_attente", depose_le=maintenant)
    db.add(accord)
    db.flush()
    journal.noter(
        db,
        auteur_id=compte.id,
        action="deposer_accord_parental",
        table_cible="accord_parental",
        ligne_id=accord.id,
        apres={"statut": "en_attente", "fichier": fichier.nom_origine},
        maintenant=maintenant,
    )
    return accord


def decider_accord(
    db: Session, administrateur: Compte, accord_id: int, *, accepte: bool, motif_refus: str | None, maintenant: datetime
) -> AccordParental:
    accord = db.get(AccordParental, accord_id)
    if accord is None:
        raise ErreurRegle("Cet accord n'existe pas.", 404)
    if accord.statut != "en_attente":
        raise ErreurRegle("Cet accord a déjà été décidé.")
    motif = (motif_refus or "").strip()
    if not accepte and not motif:
        raise ErreurRegle("Indiquez le motif du refus (ex. « Signature illisible »).")

    accord.statut = "accepte" if accepte else "refuse"
    accord.decide_par_id = administrateur.id
    accord.decide_le = maintenant
    accord.motif_refus = None if accepte else motif
    journal.noter(
        db,
        auteur_id=administrateur.id,
        action="decider_accord_parental",
        table_cible="accord_parental",
        ligne_id=accord.id,
        avant={"statut": "en_attente"},
        apres={"statut": accord.statut, "motif_refus": accord.motif_refus},
        maintenant=maintenant,
    )
    return accord
