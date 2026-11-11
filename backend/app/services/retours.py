"""« Un problème ? Une idée ? » (RM-RETOURS.md, lot 13.1 ; règle validée par Raphael le 09/11/2026).
Un compte connecté envoie un problème ou une idée, avec au plus une capture d'écran ; 5 messages par jour au plus.
La page, l'appareil et le navigateur sont ajoutés tout seuls. Un message injurieux n'est pas refusé : il est gardé
pour l'administrateur (statut « injurieux ») et la routine du soir ne le lit jamais."""

import re
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.comptes import Compte
from app.modeles.retours import Retour
from app.services import fichiers, journal, moderation
from app.services.avis import mot_interdit_dans
from app.services.erreurs import ErreurRegle


@dataclass
class Capture:
    nom_fichier: str
    type_mime: str
    contenu: bytes


# Ordre important : Edge et Opera se présentent aussi comme Chrome, et Chrome comme Safari
_NAVIGATEURS = (("Edg/", "Edge"), ("OPR/", "Opera"), ("SamsungBrowser", "Samsung Internet"), ("Firefox/", "Firefox"),
                ("FxiOS", "Firefox"), ("CriOS", "Chrome"), ("Chrome/", "Chrome"), ("Safari/", "Safari"))
_SYSTEMES = (("Android", "Android"), ("iPhone", "iPhone"), ("iPad", "iPad"), ("Windows", "Windows"),
             ("Mac OS X", "Mac"), ("CrOS", "Chromebook"), ("Linux", "Linux"))


def appareil_et_navigateur(user_agent: str) -> tuple[str, str]:
    """Lu dans la carte d'identité que tout navigateur envoie (« User-Agent »).
    Ex. « Mozilla/5.0 (Linux; Android 14…) … Chrome/130… Mobile Safari/537.36 » → (« telephone », « Chrome sur Android »)."""
    ua = user_agent or ""
    navigateur = next((nom for marque, nom in _NAVIGATEURS if marque in ua), "Navigateur inconnu")
    systeme = next((nom for marque, nom in _SYSTEMES if marque in ua), None)
    telephone = bool(re.search(r"Mobi|Android|iPhone|iPad", ua))
    return ("telephone" if telephone else "ordinateur"), (f"{navigateur} sur {systeme}" if systeme else navigateur)


def envoyes_aujourd_hui(db: Session, compte: Compte, maintenant: datetime) -> int:
    """Messages du compte depuis minuit, heure de Paris (ex. envoyé à 23 h 50 puis à 0 h 10 : 2 jours différents)."""
    local = maintenant.astimezone(reglages.FUSEAU_AFFICHAGE)
    minuit = local.replace(hour=0, minute=0, second=0, microsecond=0)
    return db.scalar(select(func.count()).select_from(Retour).where(
        Retour.auteur_id == compte.id, Retour.cree_le >= minuit, Retour.cree_le < minuit + timedelta(days=1))) or 0


def _injurieux(db: Session, texte: str) -> bool:
    """Le même filtre que les avis (liste des mots interdits + IA de modération), mais sans refuser le message."""
    if mot_interdit_dans(db, texte):
        return True
    note = moderation.toxicite(texte)
    return note is not None and note >= reglages.AVIS_SEUIL_TOXICITE


def envoyer(db: Session, compte: Compte, *, sorte: str, texte: str, page: str, user_agent: str,
            capture: Capture | None, maintenant: datetime) -> Retour:
    """Ex. Julie, sur son téléphone : probleme, « Le bouton Publier ne répond pas », page /demandes/nouvelle, une capture."""
    if sorte not in reglages.RETOUR_SORTES:
        raise ErreurRegle("Choisissez « Un problème » ou « Une idée ».")
    texte = (texte or "").strip()
    mini, maxi = reglages.RETOUR_TEXTE
    if len(texte) < mini:
        raise ErreurRegle(f"Décrivez un peu plus ({mini} caractères au moins).")
    if len(texte) > maxi:
        raise ErreurRegle(f"Votre message est trop long : {maxi} caractères au plus.")
    if envoyes_aujourd_hui(db, compte, maintenant) >= reglages.RETOURS_PAR_JOUR:
        raise ErreurRegle(f"Vous avez déjà envoyé {reglages.RETOURS_PAR_JOUR} messages aujourd'hui, merci ! "
                          "Vous pourrez en envoyer d'autres demain.", 429)
    page = (page or "").strip()[:reglages.RETOUR_PAGE_MAX] or "/"
    appareil, navigateur = appareil_et_navigateur(user_agent)
    fichier_id = None
    if capture is not None:
        fichiers.verifier(capture.contenu, capture.type_mime, types_acceptes=reglages.PHOTO_TYPES_ACCEPTES,
                          taille_max_octets=reglages.PHOTO_TAILLE_MAX_OCTETS)
        fichier_id = fichiers.enregistrer(db, compte, nom_fichier=capture.nom_fichier, type_mime=capture.type_mime,
                                          contenu=capture.contenu, maintenant=maintenant).id
    retour = Retour(auteur_id=compte.id, fichier_id=fichier_id, sorte=sorte, texte=texte, page=page, appareil=appareil,
                    navigateur=navigateur, statut="injurieux" if _injurieux(db, texte) else "a_traiter", cree_le=maintenant)
    db.add(retour)
    db.flush()
    journal.noter(db, auteur_id=compte.id, action="envoyer_retour", table_cible="retour", ligne_id=retour.id,
                  apres={"sorte": sorte, "statut": retour.statut}, maintenant=maintenant)
    return retour
