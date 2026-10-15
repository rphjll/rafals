"""Notifications sur le téléphone ou l'ordinateur (lot 8.7 ; RM-ALERTES.md, RM-APPLICATION.md § « Notifications sur
l'appareil »). Chaque appareil donne son accord séparément ; une notification ne contient jamais de nom complet, de
téléphone, d'adresse ni le texte d'un message. Elle part en plus du mail, jamais à sa place.
Ex. 1 : Karim a activé son téléphone → une demande « Fuite sous l'évier » à Talence le fait sonner tout de suite.
Ex. 2 : Mme Dupont n'a rien activé → rien ne part vers elle, elle garde ses mails."""

import importlib.util
import json
import logging
from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app import config
from app.modeles.appareils import Appareil
from app.modeles.comptes import Compte

journal_technique = logging.getLogger(__name__)

# La bibliothèque d'envoi (pywebpush) est-elle installée dans le conteneur ? Sans elle, rien ne part.
BIBLIOTHEQUE = importlib.util.find_spec("pywebpush") is not None


class AppareilDisparu(Exception):
    """Le navigateur répond que cette adresse n'existe plus (téléphone changé, rafals désinstallé)."""


def disponible() -> bool:
    """Les deux clés sont dans .env et la bibliothèque est installée : sinon, aucune notification (les mails continuent)
    et le bouton [Activer les notifications] reste verrouillé."""
    return BIBLIOTHEQUE and bool(config.VAPID_PUBLIQUE and config.VAPID_PRIVEE)


def appareil_de(db: Session, adresse: str) -> Appareil | None:
    return db.scalar(select(Appareil).where(Appareil.adresse == adresse))


def enregistrer(db: Session, compte: Compte, adresse: str, cle_publique: str, cle_secrete: str, maintenant: datetime) -> Appareil:
    """[Activer les notifications] : une ligne par appareil. Déjà connu (même sur un autre compte, ex. un téléphone
    prêté) : il passe à ce compte, avec ses nouvelles clés."""
    appareil = appareil_de(db, adresse)
    if appareil is None:
        appareil = Appareil(compte_id=compte.id, adresse=adresse, cle_publique=cle_publique, cle_secrete=cle_secrete, cree_le=maintenant)
        db.add(appareil)
    else:
        appareil.compte_id, appareil.cle_publique, appareil.cle_secrete = compte.id, cle_publique, cle_secrete
    db.flush()
    return appareil


def couper(db: Session, compte: Compte, adresse: str) -> None:
    """[Couper les notifications] ou déconnexion sur cet appareil : sa ligne s'efface (réglage technique, rien de perdu)."""
    db.execute(delete(Appareil).where(Appareil.adresse == adresse, Appareil.compte_id == compte.id))


def couper_tout(db: Session, compte_id: int) -> None:
    """Compte fermé : plus aucun appareil."""
    db.execute(delete(Appareil).where(Appareil.compte_id == compte_id))


def prevenir(db: Session, compte_id: int, titre: str, texte: str, lien: str, maintenant: datetime) -> int:
    """Une notification sur chaque appareil du compte ; un clic ouvre `lien` (ex. « /messages/12 »). Rend le nombre
    d'appareils prévenus. Un appareil disparu est effacé ; une panne n'empêche jamais le reste (mail, enregistrement)."""
    if not disponible() or db.get_one(Compte, compte_id).ferme_le is not None:
        return 0
    donnees = json.dumps({"titre": titre, "texte": texte, "lien": lien}, ensure_ascii=False)
    prevenus = 0
    for appareil in db.scalars(select(Appareil).where(Appareil.compte_id == compte_id)).all():
        try:
            _pousser(appareil, donnees)
        except AppareilDisparu:
            db.delete(appareil)
            continue
        except Exception:  # noqa: BLE001 — le service du navigateur ne répond pas : on n'empêche rien
            journal_technique.exception("Notification non envoyée à l'appareil %s", appareil.id)
            continue
        appareil.dernier_envoi_le = maintenant
        prevenus += 1
    db.flush()
    return prevenus


def _pousser(appareil: Appareil, donnees: str) -> None:
    """L'envoi réel, par le service de notifications du navigateur (Google, Mozilla, Apple). Remplacé dans les tests."""
    from pywebpush import WebPushException, webpush

    try:
        webpush(
            subscription_info={"endpoint": appareil.adresse, "keys": {"p256dh": appareil.cle_publique, "auth": appareil.cle_secrete}},
            data=donnees, vapid_private_key=config.VAPID_PRIVEE, vapid_claims={"sub": config.VAPID_CONTACT}, timeout=10,
        )
    except WebPushException as erreur:
        if erreur.response is not None and erreur.response.status_code in (404, 410):
            raise AppareilDisparu from erreur
        raise
