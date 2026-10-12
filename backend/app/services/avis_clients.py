"""Avis d'un prestataire sur un client : le prestataire note (1 à 5 ★ + texte) après un rendez-vous tenu, le client
répond une fois ou signale, l'administrateur cache. La page publique d'un client montre sa moyenne et ses avis.
Règles : .doc/regles-metier/RM-AVIS.md § « Notation dans les deux sens » (validé par Raphael le 04/10/2026).
Ces avis n'entrent jamais dans le classement de la recherche (table à part : avis_client)."""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.avis import AvisClient
from app.modeles.comptes import Compte
from app.modeles.prestataires import Prestataire
from app.modeles.rendez_vous import RendezVous
from app.services import avis as service_avis
from app.services import journal, mails
from app.services.erreurs import ErreurRegle
from app.services.messagerie import nom_du_client


def _noter(db: Session, auteur_id: int | None, action: str, avis: AvisClient, maintenant: datetime, **apres) -> None:
    journal.noter(db, auteur_id=auteur_id, action=action, table_cible="avis_client", ligne_id=avis.id,
                  apres=apres or None, maintenant=maintenant)


def _texte(db: Session, texte: str) -> str:
    mini, maxi = reglages.AVIS_CLIENT_TEXTE
    return service_avis.verifier_texte(db, texte, mini, "Votre avis", maxi)


# ---------- Le prestataire : noter, modifier, retirer ----------


def tenus_entre(db: Session, client_id: int, prestataire_id: int, maintenant: datetime) -> list[RendezVous]:
    """Rendez-vous tenus entre ce client et ce prestataire, encore dans les 30 jours (pour la carte « noter »)."""
    return [r for r in db.scalars(select(RendezVous).where(
        RendezVous.client_id == client_id, RendezVous.prestataire_id == prestataire_id, RendezVous.statut == "confirme",
        RendezVous.fin <= maintenant).order_by(RendezVous.fin)) if service_avis.peut_noter(r, maintenant)]


def du_rendez_vous(db: Session, rdv_id: int) -> AvisClient | None:
    return db.scalar(select(AvisClient).where(AvisClient.rendez_vous_id == rdv_id))


def peut_noter(db: Session, rdv: RendezVous, maintenant: datetime) -> bool:
    """Rendez-vous tenu (confirmé, terminé, sans absence), dans les 30 jours, pas encore noté, client toujours inscrit."""
    return (service_avis.peut_noter(rdv, maintenant) and du_rendez_vous(db, rdv.id) is None
            and db.get_one(Compte, rdv.client_id).ferme_le is None)


def laisser(db: Session, prestataire: Prestataire, rdv: RendezVous, note: int, texte: str, maintenant: datetime) -> AvisClient:
    """Ex. Karim note Mme Dupont : « ★★★★★ Accueillante, la fuite était bien décrite, payé tout de suite. »"""
    if rdv.prestataire_id != prestataire.id:
        raise ErreurRegle("Ce rendez-vous n'existe pas.", 404)
    if du_rendez_vous(db, rdv.id):
        raise ErreurRegle("Vous avez déjà noté ce client pour ce rendez-vous : modifiez votre avis.")
    if not service_avis.peut_noter(rdv, maintenant):
        raise ErreurRegle("Un avis se laisse après un rendez-vous tenu, dans les 30 jours.")
    client = db.get_one(Compte, rdv.client_id)
    if client.ferme_le is not None:
        raise ErreurRegle("Cette personne a quitté rafals : elle ne peut plus être notée.")
    if note not in range(1, 6):
        raise ErreurRegle("Choisissez une note de 1 à 5 étoiles.")
    avis = AvisClient(rendez_vous_id=rdv.id, prestataire_id=prestataire.id, client_id=rdv.client_id, note=note,
                      texte=_texte(db, texte), cree_le=maintenant, modifie_le=maintenant)
    db.add(avis)
    db.flush()
    _noter(db, prestataire.compte_id, "noter_client", avis, maintenant, note=note)
    mails.envoyer_mail(client.email, f"rafals : {prestataire.nom_affiche} vous a laissé un avis",
                       f"{prestataire.nom_affiche} vous a laissé un avis après « {rdv.titre} ». Pour le lire, y répondre "
                       "ou le signaler : « Mon profil », rubrique « Mes avis reçus ».")
    return avis


def _mon_avis(db: Session, prestataire: Prestataire, avis_id: int) -> AvisClient:
    avis = db.get(AvisClient, avis_id)
    if avis is None or avis.prestataire_id != prestataire.id:
        raise ErreurRegle("Cet avis n'existe pas.", 404)
    return avis


def modifier(db: Session, prestataire: Prestataire, avis_id: int, note: int, texte: str, maintenant: datetime) -> AvisClient:
    """Possible pendant les 30 jours ; ensuite il est figé. Un avis retiré ou caché ne se modifie plus."""
    avis = _mon_avis(db, prestataire, avis_id)
    if avis.retire_le or avis.cache_le:
        raise ErreurRegle("Cet avis n'est plus affiché : il ne peut plus être modifié.")
    if maintenant > service_avis.limite(db.get_one(RendezVous, avis.rendez_vous_id)):
        raise ErreurRegle("Les 30 jours sont passés : votre avis ne peut plus être modifié.")
    if note not in range(1, 6):
        raise ErreurRegle("Choisissez une note de 1 à 5 étoiles.")
    avis.note, avis.texte, avis.modifie_le = note, _texte(db, texte), maintenant
    _noter(db, prestataire.compte_id, "modifier_avis_client", avis, maintenant, note=note)
    return avis


def retirer(db: Session, prestataire: Prestataire, avis_id: int, maintenant: datetime) -> AvisClient:
    """À tout moment : l'avis est caché (pas effacé) et sa note ne compte plus."""
    avis = _mon_avis(db, prestataire, avis_id)
    if avis.retire_le is None:
        avis.retire_le = maintenant
        _noter(db, prestataire.compte_id, "retirer_avis_client", avis, maintenant)
    return avis


# ---------- Le client : lire, répondre une fois, signaler ----------


def _avis_recu(db: Session, client: Compte, avis_id: int) -> AvisClient:
    avis = db.get(AvisClient, avis_id)
    if avis is None or avis.client_id != client.id or avis.retire_le is not None:
        raise ErreurRegle("Cet avis n'existe pas.", 404)
    return avis


def recus(db: Session, client: Compte) -> list[AvisClient]:
    """« Mes avis reçus » : tous sauf ceux que le prestataire a retirés ; un avis caché reste montré avec son motif."""
    return list(db.scalars(select(AvisClient).where(AvisClient.client_id == client.id, AvisClient.retire_le.is_(None))
                           .order_by(AvisClient.cree_le.desc())))


def non_vus(db: Session, client: Compte) -> int:
    """Le compteur rouge de « Mes avis reçus » : avis visibles arrivés depuis sa dernière visite."""
    depuis = [AvisClient.cree_le > client.avis_recus_vus_le] if client.avis_recus_vus_le else []
    return db.scalar(select(func.count()).select_from(AvisClient).where(
        AvisClient.client_id == client.id, AvisClient.retire_le.is_(None), AvisClient.cache_le.is_(None), *depuis)) or 0


def marquer_vus(client: Compte, maintenant: datetime) -> None:
    client.avis_recus_vus_le = maintenant


def repondre(db: Session, client: Compte, avis_id: int, texte: str, maintenant: datetime) -> AvisClient:
    """Une seule réponse publique, affichée sous l'avis ; elle ne change pas la note."""
    avis = _avis_recu(db, client, avis_id)
    if avis.reponse is not None:
        raise ErreurRegle("Vous avez déjà répondu à cet avis.")
    avis.reponse = service_avis.verifier_texte(db, texte, reglages.REPONSE_TEXTE_MIN, "Votre réponse", reglages.AVIS_CLIENT_TEXTE[1])
    avis.repondu_le = maintenant
    _noter(db, client.id, "repondre_avis_client", avis, maintenant)
    return avis


def signaler(db: Session, client: Compte, avis_id: int, raison: str, maintenant: datetime) -> AvisClient:
    """L'avis reste affiché pendant l'examen par l'administrateur."""
    avis = _avis_recu(db, client, avis_id)
    raison = (raison or "").strip()
    if avis.signale_le is not None:
        raise ErreurRegle("Cet avis est déjà signalé : l'administrateur va le regarder.")
    if len(raison) < reglages.SIGNALEMENT_TEXTE_MIN:
        raise ErreurRegle("Expliquez pourquoi (ex. « Fausse accusation », « Ce n'était pas moi »).")
    avis.signale_le, avis.signalement = maintenant, raison[: reglages.AVIS_TEXTE_MAX]
    _noter(db, client.id, "signaler_avis_client", avis, maintenant)
    return avis


# ---------- L'administrateur ----------


def signales(db: Session) -> list[AvisClient]:
    return list(db.scalars(select(AvisClient).where(
        AvisClient.signale_le.is_not(None), AvisClient.signalement_traite_le.is_(None), AvisClient.cache_le.is_(None)
    ).order_by(AvisClient.signale_le)))


def decider(db: Session, administrateur: Compte, avis_id: int, cacher: bool, motif: str | None, maintenant: datetime) -> AvisClient:
    """Laisser l'avis, ou le cacher (sa note ne compte plus) avec un motif envoyé au prestataire. Rien n'est effacé."""
    avis = db.get(AvisClient, avis_id)
    if avis is None:
        raise ErreurRegle("Cet avis n'existe pas.", 404)
    if avis.cache_le is not None:
        raise ErreurRegle("Cet avis est déjà caché.")
    if cacher:
        motif = (motif or "").strip()
        if len(motif) < reglages.SIGNALEMENT_TEXTE_MIN:
            raise ErreurRegle("Écrivez le motif : il est envoyé au prestataire (ex. « Accusation grave sans élément »).")
        avis.cache_le, avis.cache_motif, avis.cache_par_id = maintenant, motif, administrateur.id
        prestataire = db.get_one(Prestataire, avis.prestataire_id)
        auteur = db.get_one(Compte, prestataire.compte_id)
        if auteur.ferme_le is None:
            mails.envoyer_mail(auteur.email, "rafals : votre avis sur un client est caché",
                               f"Votre avis sur un client a été caché par rafals. Motif : « {motif} ».")
    avis.signalement_traite_le = maintenant
    _noter(db, administrateur.id, "cacher_avis_client" if cacher else "laisser_avis_client_signale", avis, maintenant)
    return avis


# ---------- Ce que tout le monde voit ----------


def visibles(db: Session, client_id: int) -> list[AvisClient]:
    """Ni retirés ni cachés, les plus récents d'abord."""
    return list(db.scalars(select(AvisClient).where(
        AvisClient.client_id == client_id, AvisClient.retire_le.is_(None), AvisClient.cache_le.is_(None)
    ).order_by(AvisClient.cree_le.desc())))


def note_de(db: Session, client_id: int) -> tuple[float | None, int]:
    """(moyenne arrondie au dixième, nombre d'avis visibles). Ex. (4.8, 6) ; sans avis : (None, 0)."""
    somme, nombre = db.execute(select(func.coalesce(func.sum(AvisClient.note), 0), func.count()).where(
        AvisClient.client_id == client_id, AvisClient.retire_le.is_(None), AvisClient.cache_le.is_(None))).one()
    return (round(int(somme) / int(nombre), 1) if nombre else None), int(nombre)


def client_public_ou_404(db: Session, client_id: int) -> Compte:
    """La page publique d'un client existe tant que son compte n'est pas fermé."""
    client = db.get(Compte, client_id)
    if client is None or client.ferme_le is not None:
        raise ErreurRegle("Cette personne n'est pas (ou plus) sur rafals.", 404)
    return client


def auteur(db: Session, avis: AvisClient) -> str:
    """« Karim Benali » ; compte du prestataire fermé : « Prestataire ayant quitté rafals »."""
    prestataire = db.get_one(Prestataire, avis.prestataire_id)
    if db.get_one(Compte, prestataire.compte_id).ferme_le is not None:
        return "Prestataire ayant quitté rafals"
    return prestataire.nom_affiche


def nom_public(client: Compte) -> str:
    """« Marie D. » : jamais le nom complet."""
    return nom_du_client(client)
