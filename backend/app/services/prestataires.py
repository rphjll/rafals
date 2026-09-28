"""Profil prestataire. Règles : .doc/regles-metier/RM-PRESTATAIRES.md, RM-COMPTES.md (qui peut devenir prestataire)."""

from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.comptes import Compte
from app.modeles.metiers import Metier
from app.modeles.prestataires import Commune, MetierSecondaire, Prestataire
from app.services import droits, fichiers, journal
from app.services.erreurs import ErreurRegle


@dataclass
class Profil:
    """Ce que le prestataire remplit (création ou modification)."""

    nom_affiche: str
    metier_principal_id: int
    commune_id: int
    distance_km: int
    presentation: str | None = None
    siret: str | None = None
    metiers_secondaires: list[int] = field(default_factory=list)


# ---------- SIRET ----------


def normaliser_siret(texte: str | None) -> str | None:
    """« 912 345 678 00014 » → « 91234567800014 » ; vide → None."""
    chiffres = "".join(c for c in (texte or "") if not c.isspace())
    return chiffres or None


def siret_valide(siret: str) -> bool:
    """14 chiffres et la clé de contrôle (formule de Luhn), sauf La Poste (SIREN 356000000) dont la règle diffère."""
    if len(siret) != 14 or not siret.isdigit():
        return False
    if siret.startswith("356000000"):
        return sum(int(c) for c in siret) % 5 == 0
    total = 0
    for rang, chiffre in enumerate(reversed(siret)):
        valeur = int(chiffre) * (2 if rang % 2 else 1)
        total += valeur - 9 if valeur > 9 else valeur
    return total % 10 == 0


# ---------- Création et modification ----------


def profil_de(db: Session, compte: Compte) -> Prestataire | None:
    return db.scalar(select(Prestataire).where(Prestataire.compte_id == compte.id))


def metiers_secondaires(db: Session, prestataire: Prestataire) -> list[int]:
    return list(db.scalars(select(MetierSecondaire.metier_id).where(MetierSecondaire.prestataire_id == prestataire.id)))


def _verifier(db: Session, profil: Profil) -> Profil:
    nom = " ".join(profil.nom_affiche.split())
    mini, maxi = reglages.PRESTATAIRE_NOM_LONGUEUR
    if not mini <= len(nom) <= maxi:
        raise ErreurRegle(f"Le nom affiché doit faire entre {mini} et {maxi} caractères (ex. « Julie Martin — Ménage »).")
    presentation = (profil.presentation or "").strip() or None
    if presentation and len(presentation) > reglages.PRESTATAIRE_PRESENTATION_MAX:
        raise ErreurRegle(f"La présentation doit faire au plus {reglages.PRESTATAIRE_PRESENTATION_MAX} caractères.")
    principal = db.get(Metier, profil.metier_principal_id)
    if principal is None or not principal.est_active:
        raise ErreurRegle("Choisissez votre métier principal dans la liste.")
    if db.get(Commune, profil.commune_id) is None:
        raise ErreurRegle("Choisissez votre ville dans la liste.")
    if not 1 <= profil.distance_km <= reglages.PRESTATAIRE_DISTANCE_MAX_KM:
        raise ErreurRegle(f"La distance doit être comprise entre 1 et {reglages.PRESTATAIRE_DISTANCE_MAX_KM} km.")

    secondaires = list(dict.fromkeys(profil.metiers_secondaires))  # sans doublon, dans l'ordre choisi
    if profil.metier_principal_id in secondaires:
        raise ErreurRegle("Votre métier principal ne peut pas être aussi un métier secondaire.")
    if len(secondaires) > reglages.PRESTATAIRE_METIERS_SECONDAIRES_MAX:
        raise ErreurRegle(f"Au plus {reglages.PRESTATAIRE_METIERS_SECONDAIRES_MAX} métiers secondaires.")
    for metier_id in secondaires:
        metier = db.get(Metier, metier_id)
        if metier is None or not metier.est_active:
            raise ErreurRegle("Un des métiers secondaires n'existe plus : choisissez-le à nouveau.")

    siret = normaliser_siret(profil.siret)
    if siret is not None and not siret_valide(siret):
        raise ErreurRegle(
            "Ce SIRET n'est pas valide : il fait 14 chiffres, et le dernier sert de contrôle. "
            "Recopiez-le depuis votre avis de situation INSEE ou vos factures."
        )
    return Profil(nom, profil.metier_principal_id, profil.commune_id, profil.distance_km, presentation, siret, secondaires)


def _remplacer_secondaires(db: Session, prestataire: Prestataire, secondaires: list[int]) -> None:
    db.execute(delete(MetierSecondaire).where(MetierSecondaire.prestataire_id == prestataire.id))
    for metier_id in secondaires:
        db.add(MetierSecondaire(prestataire_id=prestataire.id, metier_id=metier_id))


def _etat(prestataire: Prestataire, secondaires: list[int]) -> dict:
    return {
        "nom_affiche": prestataire.nom_affiche,
        "metier_principal_id": prestataire.metier_principal_id,
        "metiers_secondaires": secondaires,
        "commune_id": prestataire.commune_id,
        "distance_km": prestataire.distance_km,
        "siret": prestataire.siret,
        "statut": prestataire.statut,
    }


def devenir_prestataire(db: Session, compte: Compte, profil: Profil, maintenant: datetime) -> Prestataire:
    """« Proposer mes services ». Condition (RM-COMPTES) : adresse vérifiée ; accord des parents accepté avant 18 ans."""
    if compte.email_verifie_le is None:
        raise ErreurRegle("Vérifiez d'abord votre adresse mail (lien reçu par mail), puis revenez proposer vos services.", 403)
    if not droits.peut_reserver_ou_publier(db, compte, maintenant):
        raise ErreurRegle("Il faut d'abord que l'accord de tes parents soit accepté (voir « Mon compte »).", 403)
    if profil_de(db, compte) is not None:
        raise ErreurRegle("Vous proposez déjà vos services : modifiez votre profil de prestataire.", 409)

    p = _verifier(db, profil)
    prestataire = Prestataire(
        compte_id=compte.id,
        metier_principal_id=p.metier_principal_id,
        commune_id=p.commune_id,
        nom_affiche=p.nom_affiche,
        presentation=p.presentation,
        distance_km=p.distance_km,
        siret=p.siret,
        siret_statut="a_verifier" if p.siret else "absent",
        statut="actif",
        statut_change_le=maintenant,
        cree_le=maintenant,
    )
    db.add(prestataire)
    db.flush()
    _remplacer_secondaires(db, prestataire, p.metiers_secondaires)
    journal.noter(
        db, auteur_id=compte.id, action="devenir_prestataire", table_cible="prestataire", ligne_id=prestataire.id,
        apres=_etat(prestataire, p.metiers_secondaires), maintenant=maintenant,
    )
    return prestataire


def modifier_profil(db: Session, prestataire: Prestataire, profil: Profil, maintenant: datetime) -> Prestataire:
    if prestataire.statut == "arrete":
        raise ErreurRegle("Votre activité est arrêtée : ce profil ne peut plus être modifié.")
    avant = _etat(prestataire, metiers_secondaires(db, prestataire))
    p = _verifier(db, profil)
    if p.siret != prestataire.siret:
        # Un SIRET changé repart à vérifier (lot 2.4) ; le retirer = « absent »
        prestataire.siret = p.siret
        prestataire.siret_statut = "a_verifier" if p.siret else "absent"
        prestataire.siret_verifie_le = None
    prestataire.nom_affiche = p.nom_affiche
    prestataire.presentation = p.presentation
    prestataire.metier_principal_id = p.metier_principal_id
    prestataire.commune_id = p.commune_id
    prestataire.distance_km = p.distance_km
    _remplacer_secondaires(db, prestataire, p.metiers_secondaires)
    journal.noter(
        db, auteur_id=prestataire.compte_id, action="modifier_profil_prestataire", table_cible="prestataire",
        ligne_id=prestataire.id, avant=avant, apres=_etat(prestataire, p.metiers_secondaires), maintenant=maintenant,
    )
    return prestataire


def deposer_photo(
    db: Session, compte: Compte, prestataire: Prestataire, *, nom_fichier: str, type_mime: str, contenu: bytes, maintenant: datetime
) -> Prestataire:
    if prestataire.statut == "arrete":
        raise ErreurRegle("Votre activité est arrêtée : ce profil ne peut plus être modifié.")
    fichiers.verifier(
        contenu, type_mime, types_acceptes=reglages.PHOTO_TYPES_ACCEPTES, taille_max_octets=reglages.PHOTO_TAILLE_MAX_OCTETS
    )
    fichier = fichiers.enregistrer(db, compte, nom_fichier=nom_fichier, type_mime=type_mime, contenu=contenu, maintenant=maintenant)
    ancienne = prestataire.photo_id
    prestataire.photo_id = fichier.id
    journal.noter(
        db, auteur_id=compte.id, action="changer_photo_prestataire", table_cible="prestataire", ligne_id=prestataire.id,
        avant={"photo_id": ancienne}, apres={"photo_id": fichier.id}, maintenant=maintenant,
    )
    return prestataire


# ---------- Statut : pause, arrêt (par le prestataire), blocage (par l'administrateur) ----------

_TRANSITIONS_PRESTATAIRE = {
    # action : (statuts de départ permis, statut d'arrivée)
    "pause": ({"actif"}, "en_pause"),
    "reprendre": ({"en_pause"}, "actif"),
    "arreter": ({"actif", "en_pause"}, "arrete"),
}


def _changer_statut(db: Session, prestataire: Prestataire, nouveau: str, auteur_id: int, action: str, maintenant: datetime) -> None:
    ancien = prestataire.statut
    prestataire.statut = nouveau
    prestataire.statut_change_le = maintenant
    journal.noter(
        db, auteur_id=auteur_id, action=action, table_cible="prestataire", ligne_id=prestataire.id,
        avant={"statut": ancien}, apres={"statut": nouveau}, maintenant=maintenant,
    )


def changer_statut(db: Session, prestataire: Prestataire, action: str, maintenant: datetime) -> Prestataire:
    """Par le prestataire lui-même : « pause », « reprendre » ou « arreter » (définitif)."""
    if action not in _TRANSITIONS_PRESTATAIRE:
        raise ErreurRegle("Action inconnue.")
    if prestataire.statut == "bloque":
        raise ErreurRegle("Votre profil est bloqué par l'administrateur de rafals : contactez-le.", 403)
    if prestataire.statut == "arrete":
        raise ErreurRegle("Votre activité est arrêtée : ce profil ne peut plus être modifié.")
    departs, arrivee = _TRANSITIONS_PRESTATAIRE[action]
    if prestataire.statut not in departs:
        messages = {"pause": "Votre profil est déjà en pause.", "reprendre": "Votre profil est déjà actif."}
        raise ErreurRegle(messages.get(action, "Ce changement n'est pas possible."))
    _changer_statut(db, prestataire, arrivee, prestataire.compte_id, f"prestataire_{action}", maintenant)
    return prestataire


def bloquer(db: Session, administrateur: Compte, prestataire_id: int, *, bloque: bool, maintenant: datetime) -> Prestataire:
    """Par un administrateur. Débloquer remet le profil actif.
    (Quand les rendez-vous existeront, bloquer annulera ceux à venir et préviendra les clients : RM-PRESTATAIRES.)"""
    prestataire = db.get(Prestataire, prestataire_id)
    if prestataire is None:
        raise ErreurRegle("Ce prestataire n'existe pas.", 404)
    if prestataire.statut == "arrete":
        raise ErreurRegle("Ce prestataire a arrêté son activité : il ne peut être ni bloqué ni débloqué.")
    if bloque and prestataire.statut != "bloque":
        _changer_statut(db, prestataire, "bloque", administrateur.id, "bloquer_prestataire", maintenant)
    elif not bloque and prestataire.statut == "bloque":
        _changer_statut(db, prestataire, "actif", administrateur.id, "debloquer_prestataire", maintenant)
    return prestataire
