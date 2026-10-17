"""Local du prestataire (l'adresse où il reçoit ses clients) et garde « profil modifiable ».
Règles : .doc/regles-metier/RM-PRESTATAIRES.md (§ « Sans annonces », § « Une seule adresse »). Depuis le 07/10/2026,
le local est la copie de « Mon adresse » : c'est services/clients.py qui appelle ces fonctions."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modeles.locaux import Local
from app.modeles.prestataires import Prestataire
from app.services import communes, journal
from app.services.erreurs import ErreurRegle


def verifier_modifiable(prestataire: Prestataire) -> None:
    if prestataire.statut == "arrete":
        raise ErreurRegle("Votre activité est arrêtée : ce profil ne peut plus être modifié.")
    if prestataire.statut == "bloque":
        raise ErreurRegle("Votre profil est bloqué par l'administrateur de rafals : contactez-le.", 403)


def local_de(db: Session, prestataire: Prestataire) -> Local | None:
    return db.scalar(select(Local).where(Local.prestataire_id == prestataire.id))


def enregistrer_local(
    db: Session, prestataire: Prestataire, *, ligne: str, complement: str | None, commune_id: int, code_postal: str,
    maintenant: datetime,
) -> Local:
    """Ex. Léa : « 12 rue des Lilas », Mérignac, 33700 : là où viennent ses clients quand le service a lieu chez elle."""
    verifier_modifiable(prestataire)
    controle = communes.controler_adresse(db, ligne=ligne, complement=complement, commune_id=commune_id, code_postal=code_postal)
    local = local_de(db, prestataire)
    avant = None if local is None else {"ligne": local.ligne, "commune_id": local.commune_id}
    if local is None:
        local = Local(prestataire_id=prestataire.id, commune_id=controle.commune.id, ligne=controle.ligne,
                      complement=controle.complement, code_postal=controle.code_postal)
        db.add(local)
    else:
        local.commune_id, local.ligne = controle.commune.id, controle.ligne
        local.complement, local.code_postal = controle.complement, controle.code_postal
    local.modifie_le = maintenant
    db.flush()
    journal.noter(
        db, auteur_id=prestataire.compte_id, action="enregistrer_local", table_cible="local", ligne_id=local.id,
        avant=avant, apres={"ligne": local.ligne, "commune_id": local.commune_id}, maintenant=maintenant,
    )
    return local


def effacer_local(db: Session, prestataire: Prestataire, maintenant: datetime) -> None:
    """À appeler seulement si le lieu de ses services est « chez le client » (vérifié par services/clients.py)."""
    verifier_modifiable(prestataire)
    local = local_de(db, prestataire)
    if local is None:
        return
    journal.noter(
        db, auteur_id=prestataire.compte_id, action="effacer_local", table_cible="local", ligne_id=local.id,
        avant={"ligne": local.ligne, "commune_id": local.commune_id}, maintenant=maintenant,
    )
    db.delete(local)
