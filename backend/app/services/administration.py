"""Rôle administrateur. Règles : RM-COMPTES.md (administrateurs) : il reste toujours au moins un administrateur."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modeles.comptes import Compte
from app.services import journal
from app.services.erreurs import ErreurRegle


def changer_role_administrateur(
    db: Session, auteur: Compte, compte_id: int, *, est_administrateur: bool, maintenant: datetime
) -> Compte:
    # Verrouille les administrateurs le temps du calcul : deux retraits en même temps ne peuvent pas vider la liste
    administrateurs = db.scalars(select(Compte.id).where(Compte.est_administrateur).with_for_update()).all()
    cible = db.get(Compte, compte_id)
    if cible is None:
        raise ErreurRegle("Ce compte n'existe pas.", 404)
    if cible.est_administrateur == est_administrateur:
        return cible
    if est_administrateur and cible.ferme_le is not None:
        raise ErreurRegle("Ce compte est fermé : il ne peut pas devenir administrateur.")
    if not est_administrateur and len(administrateurs) <= 1:
        raise ErreurRegle("Il doit toujours rester au moins un administrateur.")

    cible.est_administrateur = est_administrateur
    journal.noter(
        db,
        auteur_id=auteur.id,
        action="nommer_administrateur" if est_administrateur else "retirer_administrateur",
        table_cible="compte",
        ligne_id=cible.id,
        avant={"est_administrateur": not est_administrateur},
        apres={"est_administrateur": est_administrateur},
        maintenant=maintenant,
    )
    return cible
