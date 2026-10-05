"""Avis : laisser, modifier, retirer ; réponse du prestataire ; filtre des mots interdits ; signalement et avis caché
par l'administrateur ; note du prestataire ; rappel le lendemain. Règles : .doc/regles-metier/RM-AVIS.md (30/09/2026).
Un avis n'est jamais effacé ; la note n'est jamais enregistrée : elle se calcule à partir des avis visibles."""

import re
from datetime import date, datetime, time, timedelta

from sqlalchemy import and_, exists, func, select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.avis import Avis, MotInterdit
from app.modeles.comptes import Compte
from app.modeles.journal import JournalAction
from app.modeles.prestataires import Prestataire
from app.modeles.rendez_vous import RendezVous
from app.services import journal, moderation
from app.services import rendez_vous_communs as communs
from app.services.erreurs import ErreurRegle
from app.services.metiers import sans_accents

PARIS = reglages.FUSEAU_AFFICHAGE
MOIS = ("janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre")


def _noter(db: Session, auteur_id: int | None, action: str, avis: Avis, maintenant: datetime, **apres) -> None:
    journal.noter(db, auteur_id=auteur_id, action=action, table_cible="avis", ligne_id=avis.id, apres=apres or None,
                  maintenant=maintenant)


# ---------- Mots interdits ----------


def mot_interdit_dans(db: Session, texte: str) -> str | None:
    """Le 1er mot interdit trouvé (mot entier, sans tenir compte des accents ni des majuscules), sinon None.
    Ex. « Karim est un Connard » → « connard » ; « une conserve » → None (« con » n'est pas un mot entier ici)."""
    mots = set(re.findall(r"[a-z0-9]+", sans_accents(texte)))
    return next((m for m in db.scalars(select(MotInterdit.mot)) if m in mots), None)


def verifier_texte(db: Session, texte: str, mini: int, quoi: str, maxi: int = reglages.AVIS_TEXTE_MAX) -> str:
    """Le filtre commun à tout texte écrit par un utilisateur et lu par un autre (avis, réponses, messages, demandes) :
    longueur, mots interdits, IA de modération. Rend le texte nettoyé de ses espaces autour."""
    texte = (texte or "").strip()
    if not mini <= len(texte) <= maxi:
        raise ErreurRegle(f"{quoi} doit faire entre {mini} et {maxi} caractères.")
    if mot_interdit_dans(db, texte):
        raise ErreurRegle(f"{quoi} contient un mot interdit : reformulez-le, s'il vous plaît.")
    # L'IA lit aussi le texte : une injure sans gros mot est refusée (ex. « un gros nul qui arnaque les vieux »)
    note = moderation.toxicite(texte)
    if note is not None and note >= reglages.AVIS_SEUIL_TOXICITE:
        raise ErreurRegle(f"{quoi} semble injurieux : reformulez-le calmement, s'il vous plaît.")
    return texte


_verifier_texte = verifier_texte  # ancien nom, gardé pour les appels de ce fichier


def mots_interdits(db: Session) -> list[MotInterdit]:
    return list(db.scalars(select(MotInterdit).order_by(MotInterdit.mot)))


def ajouter_mot(db: Session, administrateur: Compte, mot: str, maintenant: datetime) -> MotInterdit:
    mot = sans_accents(mot).strip()
    if len(mot) < 2 or not re.fullmatch(r"[a-z0-9]+", mot):
        raise ErreurRegle("Un seul mot, d'au moins 2 lettres (sans espace).")
    if db.scalar(select(MotInterdit).where(MotInterdit.mot == mot)):
        raise ErreurRegle(f"« {mot} » est déjà dans la liste.")
    ligne = MotInterdit(mot=mot, ajoute_par_id=administrateur.id, ajoute_le=maintenant)
    db.add(ligne)
    db.flush()
    journal.noter(db, auteur_id=administrateur.id, action="ajouter_mot_interdit", table_cible="mot_interdit",
                  ligne_id=ligne.id, apres={"mot": mot}, maintenant=maintenant)
    return ligne


def retirer_mot(db: Session, administrateur: Compte, mot_id: int, maintenant: datetime) -> None:
    ligne = db.get(MotInterdit, mot_id)
    if ligne is None:
        raise ErreurRegle("Ce mot n'est pas dans la liste.", 404)
    journal.noter(db, auteur_id=administrateur.id, action="retirer_mot_interdit", table_cible="mot_interdit",
                  ligne_id=ligne.id, avant={"mot": ligne.mot}, maintenant=maintenant)
    db.delete(ligne)


# ---------- Laisser, modifier, retirer (le client) ----------


def limite(rdv: RendezVous) -> datetime:
    """30 jours après le rendez-vous. Ex. rendez-vous le 14/10 → avis possible jusqu'au 13/11."""
    return rdv.fin + reglages.AVIS_DELAI


def peut_noter(rdv: RendezVous, maintenant: datetime) -> bool:
    """Un rendez-vous tenu (confirmé, terminé, sans absence), dans les 30 jours."""
    return rdv.statut == "confirme" and rdv.absent is None and rdv.fin <= maintenant <= limite(rdv)


def avis_du_rendez_vous(db: Session, rdv_id: int) -> Avis | None:
    return db.scalar(select(Avis).where(Avis.rendez_vous_id == rdv_id))


def laisser(db: Session, client: Compte, rdv: RendezVous, note: int, texte: str, maintenant: datetime) -> Avis:
    if rdv.client_id != client.id:
        raise ErreurRegle("Ce rendez-vous n'existe pas.", 404)
    if avis_du_rendez_vous(db, rdv.id):
        raise ErreurRegle("Vous avez déjà laissé un avis pour ce rendez-vous : modifiez-le.")
    if not peut_noter(rdv, maintenant):
        raise ErreurRegle("Un avis se laisse après un rendez-vous tenu, dans les 30 jours.")
    if note not in range(1, 6):
        raise ErreurRegle("Choisissez une note de 1 à 5 étoiles.")
    avis = Avis(rendez_vous_id=rdv.id, client_id=client.id, prestataire_id=rdv.prestataire_id, note=note,
                texte=_verifier_texte(db, texte, reglages.AVIS_TEXTE_MIN, "Votre avis"), cree_le=maintenant, modifie_le=maintenant)
    db.add(avis)
    db.flush()
    _noter(db, client.id, "laisser_avis", avis, maintenant, note=note)
    return avis


def _mon_avis(db: Session, client: Compte, avis_id: int) -> Avis:
    avis = db.get(Avis, avis_id)
    if avis is None or avis.client_id != client.id:
        raise ErreurRegle("Cet avis n'existe pas.", 404)
    return avis


def modifier(db: Session, client: Compte, avis_id: int, note: int, texte: str, maintenant: datetime) -> Avis:
    """Possible pendant les 30 jours ; ensuite il est figé. Un avis retiré ou caché ne se modifie plus."""
    avis = _mon_avis(db, client, avis_id)
    if avis.retire_le or avis.cache_le:
        raise ErreurRegle("Cet avis n'est plus affiché : il ne peut plus être modifié.")
    if maintenant > limite(db.get_one(RendezVous, avis.rendez_vous_id)):
        raise ErreurRegle("Les 30 jours sont passés : votre avis ne peut plus être modifié.")
    if note not in range(1, 6):
        raise ErreurRegle("Choisissez une note de 1 à 5 étoiles.")
    avis.note, avis.texte = note, _verifier_texte(db, texte, reglages.AVIS_TEXTE_MIN, "Votre avis")
    avis.modifie_le = maintenant
    _noter(db, client.id, "modifier_avis", avis, maintenant, note=note)
    return avis


def retirer(db: Session, client: Compte, avis_id: int, maintenant: datetime) -> Avis:
    """À tout moment : l'avis est caché (pas effacé) et sa note ne compte plus."""
    avis = _mon_avis(db, client, avis_id)
    if avis.retire_le is None:
        avis.retire_le = maintenant
        _noter(db, client.id, "retirer_avis", avis, maintenant)
    return avis


# ---------- Le prestataire : répondre, signaler ----------


def _avis_recu(db: Session, prestataire: Prestataire, avis_id: int) -> Avis:
    avis = db.get(Avis, avis_id)
    if avis is None or avis.prestataire_id != prestataire.id:
        raise ErreurRegle("Cet avis n'existe pas.", 404)
    return avis


def repondre(db: Session, prestataire: Prestataire, avis_id: int, texte: str, maintenant: datetime) -> Avis:
    """Une seule réponse publique, affichée sous l'avis ; elle ne change pas la note."""
    avis = _avis_recu(db, prestataire, avis_id)
    if avis.reponse is not None:
        raise ErreurRegle("Vous avez déjà répondu à cet avis.")
    avis.reponse, avis.repondu_le = _verifier_texte(db, texte, reglages.REPONSE_TEXTE_MIN, "Votre réponse"), maintenant
    _noter(db, prestataire.compte_id, "repondre_avis", avis, maintenant)
    return avis


def signaler(db: Session, prestataire: Prestataire, avis_id: int, raison: str, maintenant: datetime) -> Avis:
    """L'avis reste affiché pendant l'examen par l'administrateur."""
    avis = _avis_recu(db, prestataire, avis_id)
    raison = (raison or "").strip()
    if avis.signale_le is not None:
        raise ErreurRegle("Cet avis est déjà signalé : l'administrateur va le regarder.")
    if len(raison) < reglages.SIGNALEMENT_TEXTE_MIN:
        raise ErreurRegle("Expliquez pourquoi (ex. « Fausse accusation », « Contient mon numéro de téléphone »).")
    avis.signale_le, avis.signalement = maintenant, raison[: reglages.AVIS_TEXTE_MAX]
    _noter(db, prestataire.compte_id, "signaler_avis", avis, maintenant)
    return avis


# ---------- L'administrateur ----------


def avis_signales(db: Session) -> list[Avis]:
    return list(db.scalars(select(Avis).where(
        Avis.signale_le.is_not(None), Avis.signalement_traite_le.is_(None), Avis.cache_le.is_(None)
    ).order_by(Avis.signale_le)))


def decider(db: Session, administrateur: Compte, avis_id: int, cacher: bool, motif: str | None, maintenant: datetime) -> Avis:
    """Laisser l'avis, ou le cacher (sa note ne compte plus) avec un motif envoyé au client. Rien n'est effacé."""
    avis = db.get(Avis, avis_id)
    if avis is None:
        raise ErreurRegle("Cet avis n'existe pas.", 404)
    if avis.cache_le is not None:
        raise ErreurRegle("Cet avis est déjà caché.")
    if cacher:
        motif = (motif or "").strip()
        if len(motif) < reglages.SIGNALEMENT_TEXTE_MIN:
            raise ErreurRegle("Écrivez le motif : il est envoyé au client (ex. « Accusation grave sans élément »).")
        avis.cache_le, avis.cache_motif, avis.cache_par_id = maintenant, motif, administrateur.id
        rdv = db.get_one(RendezVous, avis.rendez_vous_id)
        communs.prevenir(db, rdv, sujet="rafals : votre avis est caché",
                         client=f"Votre avis sur « {rdv.titre} » a été caché par rafals. Motif : « {motif} ».")
    avis.signalement_traite_le = maintenant
    _noter(db, administrateur.id, "cacher_avis" if cacher else "laisser_avis_signale", avis, maintenant)
    return avis


# ---------- Ce que voient les clients ----------


def visibles(db: Session, prestataire_id: int) -> list[Avis]:
    """Ni retirés ni cachés, les plus récents d'abord."""
    return list(db.scalars(select(Avis).where(
        Avis.prestataire_id == prestataire_id, Avis.retire_le.is_(None), Avis.cache_le.is_(None)
    ).order_by(Avis.cree_le.desc())))


def notes(db: Session, prestataire_ids: list[int]) -> dict[int, tuple[int, int]]:
    """Par prestataire : (somme des notes, nombre d'avis visibles) — pour la note pondérée de la recherche."""
    if not prestataire_ids:
        return {}
    lignes = db.execute(
        select(Avis.prestataire_id, func.sum(Avis.note), func.count())
        .where(Avis.prestataire_id.in_(prestataire_ids), Avis.retire_le.is_(None), Avis.cache_le.is_(None))
        .group_by(Avis.prestataire_id)
    ).all()
    return {p: (int(s), int(n)) for p, s, n in lignes}


def auteur(db: Session, avis: Avis) -> str:
    """« Marie D. » ; compte fermé : « Client ayant quitté rafals »."""
    client = db.get_one(Compte, avis.client_id)
    if client.ferme_le is not None:
        return "Client ayant quitté rafals"
    initiale = client.nom.strip()[:1].upper()
    return f"{client.prenom} {initiale}." if initiale else client.prenom


def mois(moment: datetime) -> str:
    """« octobre 2026 »"""
    local = moment.astimezone(PARIS)
    return f"{MOIS[local.month - 1]} {local.year}"


# ---------- Rappel le lendemain du rendez-vous ----------


def envoyer_rappels(db: Session, maintenant: datetime) -> int:
    """Le lendemain d'un rendez-vous tenu, à partir de 10 h : « Comment s'est passé votre rendez-vous avec Karim ? ».
    Une seule fois par rendez-vous (le journal garde la trace de l'envoi)."""
    aujourd_hui: date = maintenant.astimezone(PARIS).date()
    if maintenant.astimezone(PARIS).time() < time(reglages.AVIS_RAPPEL_HEURE):
        return 0
    hier_debut = datetime.combine(aujourd_hui - timedelta(days=1), time(0), tzinfo=PARIS)
    hier_fin = datetime.combine(aujourd_hui, time(0), tzinfo=PARIS)
    deja = exists().where(and_(JournalAction.table_cible == "rendez_vous", JournalAction.ligne_id == RendezVous.id,
                               JournalAction.action == "rappel_avis"))
    sans_avis = ~exists().where(Avis.rendez_vous_id == RendezVous.id)
    candidats = db.scalars(select(RendezVous).where(
        RendezVous.statut == "confirme", RendezVous.absent.is_(None), RendezVous.fin >= hier_debut,
        RendezVous.fin < hier_fin, sans_avis, ~deja,
    )).all()
    for rdv in candidats:
        nom = db.get_one(Prestataire, rdv.prestataire_id).nom_affiche
        communs.prevenir(db, rdv, sujet=f"rafals : comment s'est passé votre rendez-vous avec {nom} ?",
                         client=f"Donnez votre avis sur « {rdv.titre} » avec {nom} (page « Mes rendez-vous »), "
                                f"jusqu'au {limite(rdv).astimezone(PARIS):%d/%m/%Y}.")
        communs.noter(db, None, "rappel_avis", rdv, maintenant)
    return len(candidats)
