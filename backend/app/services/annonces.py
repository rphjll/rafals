"""Annonces et local du prestataire. Règles : .doc/regles-metier/RM-ANNONCES.md (validé le 29/09/2026)."""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.annonces import Annonce, Local, PhotoAnnonce
from app.modeles.comptes import Compte
from app.modeles.prestataires import Prestataire
from app.services import communes, droits, fichiers, journal
from app.services.erreurs import ErreurRegle
from app.services.prestataires import aujourd_hui, metiers_exerces

FORMES_PRIX = {"fixe", "heure", "devis"}
LIEUX = {"chez_client", "chez_moi", "les_deux"}


# ---------- Local (adresse du salon ou de l'atelier, une seule fois dans le profil) ----------


def local_de(db: Session, prestataire: Prestataire) -> Local | None:
    return db.scalar(select(Local).where(Local.prestataire_id == prestataire.id))


def enregistrer_local(
    db: Session, prestataire: Prestataire, *, ligne: str, complement: str | None, commune_id: int, code_postal: str,
    maintenant: datetime,
) -> Local:
    """Ex. Léa : « 12 rue des Lilas », Mérignac, 33700 ; ses annonces « au salon » l'utilisent toutes."""
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
    """Refusé tant qu'une annonce en ligne a lieu « chez moi » (elle n'aurait plus d'adresse)."""
    verifier_modifiable(prestataire)
    local = local_de(db, prestataire)
    if local is None:
        return
    chez_moi = db.scalar(select(func.count()).select_from(Annonce).where(
        Annonce.prestataire_id == prestataire.id, Annonce.statut == "en_ligne", Annonce.lieu.in_(("chez_moi", "les_deux"))
    ))
    if chez_moi:
        raise ErreurRegle("Des annonces en ligne ont lieu chez vous : mettez-les en pause ou changez leur lieu d'abord.")
    journal.noter(
        db, auteur_id=prestataire.compte_id, action="effacer_local", table_cible="local", ligne_id=local.id,
        avant={"ligne": local.ligne, "commune_id": local.commune_id}, maintenant=maintenant,
    )
    db.delete(local)


# ---------- Écrire une annonce ----------


@dataclass
class DonneesAnnonce:
    """Ce que le prestataire remplit (création ou modification)."""

    metier_id: int
    titre: str
    forme_prix: str
    lieu: str
    description: str | None = None
    prix_centimes: int | None = None
    duree_minutes: int | None = None
    heures_min: int | None = None
    heures_max: int | None = None
    paiement_carte: bool = False
    paiement_especes: bool = True


def verifier_modifiable(prestataire: Prestataire) -> None:
    if prestataire.statut == "arrete":
        raise ErreurRegle("Votre activité est arrêtée : ce profil ne peut plus être modifié.")
    if prestataire.statut == "bloque":
        raise ErreurRegle("Votre profil est bloqué par l'administrateur de rafals : contactez-le.", 403)


def _peut_mettre_en_ligne(db: Session, prestataire: Prestataire, annonce_id: int | None, maintenant: datetime) -> None:
    """Conditions pour qu'une annonce soit en ligne (RM-ANNONCES, « Qui peut faire quoi »)."""
    compte = db.get_one(Compte, prestataire.compte_id)
    if not droits.peut_reserver_ou_publier(db, compte, maintenant):
        raise ErreurRegle("Votre compte ne peut pas encore publier (adresse mail à vérifier, ou accord des parents).", 403)
    if prestataire.statut == "en_pause":
        raise ErreurRegle("Votre activité est en pause : reprenez-la (page « Mon activité ») pour publier.")
    requete = select(func.count()).select_from(Annonce).where(
        Annonce.prestataire_id == prestataire.id, Annonce.statut == "en_ligne"
    )
    if annonce_id is not None:
        requete = requete.where(Annonce.id != annonce_id)
    if db.scalar(requete) >= reglages.ANNONCES_EN_LIGNE_MAX:
        raise ErreurRegle(
            f"Vous avez déjà {reglages.ANNONCES_EN_LIGNE_MAX} annonces en ligne : mettez-en une en pause pour publier celle-ci."
        )


def _verifier(db: Session, prestataire: Prestataire, d: DonneesAnnonce, maintenant: datetime) -> DonneesAnnonce:
    titre = " ".join(d.titre.split())
    mini, maxi = reglages.ANNONCE_TITRE_LONGUEUR
    if not mini <= len(titre) <= maxi:
        raise ErreurRegle(f"Le titre doit faire entre {mini} et {maxi} caractères (ex. « Ménage 2 h »).")
    description = (d.description or "").strip() or None
    if description and len(description) > reglages.ANNONCE_DESCRIPTION_MAX:
        raise ErreurRegle(f"La description doit faire au plus {reglages.ANNONCE_DESCRIPTION_MAX} caractères.")
    if d.metier_id not in metiers_exerces(db, prestataire, aujourd_hui(maintenant)):
        raise ErreurRegle("Choisissez un des métiers de votre profil (ajoutez-le d'abord dans « Mon activité » si besoin).")

    if d.forme_prix not in FORMES_PRIX:
        raise ErreurRegle("Choisissez la forme du prix : fixe, à l'heure ou sur devis.")
    prix = duree = heures_min = heures_max = None
    if d.forme_prix in ("fixe", "heure"):
        if d.prix_centimes is None or d.prix_centimes <= 0:
            raise ErreurRegle("Indiquez un prix (ex. 50 €).")
        prix = d.prix_centimes
    if d.forme_prix == "fixe":
        if d.duree_minutes is None or d.duree_minutes <= 0:
            raise ErreurRegle("Indiquez la durée du service (ex. 2 h) : elle bloque votre agenda.")
        duree = d.duree_minutes
    if d.forme_prix == "heure":
        if d.heures_min is None or d.heures_max is None or not 1 <= d.heures_min <= d.heures_max:
            raise ErreurRegle("Indiquez le nombre d'heures que le client peut choisir (ex. de 2 h à 4 h).")
        heures_min, heures_max = d.heures_min, d.heures_max

    if d.lieu not in LIEUX:
        raise ErreurRegle("Choisissez où a lieu le service : chez le client, chez vous, ou les deux.")
    if d.lieu in ("chez_moi", "les_deux") and local_de(db, prestataire) is None:
        raise ErreurRegle("Indiquez d'abord l'adresse de votre local (page « Mon activité »).")

    if not (d.paiement_carte or d.paiement_especes):
        raise ErreurRegle("Choisissez au moins un mode de paiement.")
    if d.paiement_carte and prestataire.siret_statut != "verifie":
        raise ErreurRegle("Le paiement par carte demande un SIRET vérifié : sans lui, espèces seulement.")
    return DonneesAnnonce(
        d.metier_id, titre, d.forme_prix, d.lieu, description, prix, duree, heures_min, heures_max,
        d.paiement_carte, d.paiement_especes,
    )


def _etat(annonce: Annonce) -> dict:
    return {
        "titre": annonce.titre, "metier_id": annonce.metier_id, "forme_prix": annonce.forme_prix,
        "prix_centimes": annonce.prix_centimes, "duree_minutes": annonce.duree_minutes, "lieu": annonce.lieu,
        "statut": annonce.statut,
    }


def _remplir(annonce: Annonce, d: DonneesAnnonce) -> None:
    annonce.metier_id, annonce.titre, annonce.description = d.metier_id, d.titre, d.description
    annonce.forme_prix, annonce.prix_centimes, annonce.duree_minutes = d.forme_prix, d.prix_centimes, d.duree_minutes
    annonce.heures_min, annonce.heures_max, annonce.lieu = d.heures_min, d.heures_max, d.lieu
    annonce.paiement_carte, annonce.paiement_especes = d.paiement_carte, d.paiement_especes


def publier(db: Session, prestataire: Prestataire, donnees: DonneesAnnonce, maintenant: datetime) -> Annonce:
    """Une annonce écrite est aussitôt en ligne (le prestataire devient visible dès sa 1re annonce : RM-PRESTATAIRES)."""
    verifier_modifiable(prestataire)
    d = _verifier(db, prestataire, donnees, maintenant)
    _peut_mettre_en_ligne(db, prestataire, None, maintenant)
    annonce = Annonce(prestataire_id=prestataire.id, statut="en_ligne", statut_change_le=maintenant,
                      cree_le=maintenant, modifiee_le=maintenant)
    _remplir(annonce, d)
    db.add(annonce)
    db.flush()
    journal.noter(
        db, auteur_id=prestataire.compte_id, action="publier_annonce", table_cible="annonce", ligne_id=annonce.id,
        apres=_etat(annonce), maintenant=maintenant,
    )
    return annonce


def annonce_de(db: Session, prestataire: Prestataire, annonce_id: int) -> Annonce:
    """Seulement ses propres annonces : celle d'un autre prestataire répond « introuvable »."""
    annonce = db.get(Annonce, annonce_id)
    if annonce is None or annonce.prestataire_id != prestataire.id:
        raise ErreurRegle("Cette annonce n'existe pas.", 404)
    return annonce


def modifier(db: Session, prestataire: Prestataire, annonce: Annonce, donnees: DonneesAnnonce, maintenant: datetime) -> Annonce:
    """Les rendez-vous déjà pris gardent l'ancien prix (valeurs recopiées à la réservation, niveau 4)."""
    verifier_modifiable(prestataire)
    avant = _etat(annonce)
    _remplir(annonce, _verifier(db, prestataire, donnees, maintenant))
    annonce.modifiee_le = maintenant
    journal.noter(
        db, auteur_id=prestataire.compte_id, action="modifier_annonce", table_cible="annonce", ligne_id=annonce.id,
        avant=avant, apres=_etat(annonce), maintenant=maintenant,
    )
    return annonce


# ---------- Pause, retrait, republier (jamais d'effacement) ----------

_TRANSITIONS_ANNONCE = {
    # action : (statuts de départ permis, statut d'arrivée)
    "pause": ({"en_ligne"}, "en_pause"),
    "retirer": ({"en_ligne", "en_pause"}, "retiree"),
    "republier": ({"en_pause", "retiree"}, "en_ligne"),
}


def changer_statut(db: Session, prestataire: Prestataire, annonce: Annonce, action: str, maintenant: datetime) -> Annonce:
    verifier_modifiable(prestataire)
    if action not in _TRANSITIONS_ANNONCE:
        raise ErreurRegle("Action inconnue.")
    departs, arrivee = _TRANSITIONS_ANNONCE[action]
    if annonce.statut not in departs:
        messages = {"pause": "Cette annonce n'est pas en ligne.", "retirer": "Cette annonce est déjà retirée.",
                    "republier": "Cette annonce est déjà en ligne."}
        raise ErreurRegle(messages[action])
    if arrivee == "en_ligne":
        # Republier : l'annonce doit toujours respecter les règles (métier encore exercé, local, SIRET pour la carte…)
        _verifier(db, prestataire, DonneesAnnonce(
            annonce.metier_id, annonce.titre, annonce.forme_prix, annonce.lieu, annonce.description, annonce.prix_centimes,
            annonce.duree_minutes, annonce.heures_min, annonce.heures_max, annonce.paiement_carte and prestataire.siret_statut == "verifie",
            annonce.paiement_especes or annonce.paiement_carte,
        ), maintenant)
        _peut_mettre_en_ligne(db, prestataire, annonce.id, maintenant)
    ancien = annonce.statut
    annonce.statut = arrivee
    annonce.statut_change_le = maintenant
    journal.noter(
        db, auteur_id=prestataire.compte_id, action=f"annonce_{action}", table_cible="annonce", ligne_id=annonce.id,
        avant={"statut": ancien}, apres={"statut": arrivee}, maintenant=maintenant,
    )
    return annonce


# ---------- Photos (5 au plus, la n° 1 montrée en premier) ----------


def photos_de(db: Session, annonce: Annonce) -> list[PhotoAnnonce]:
    return list(db.scalars(select(PhotoAnnonce).where(PhotoAnnonce.annonce_id == annonce.id).order_by(PhotoAnnonce.ordre)))


def ajouter_photo(
    db: Session, compte: Compte, prestataire: Prestataire, annonce: Annonce, *, nom_fichier: str, type_mime: str,
    contenu: bytes, maintenant: datetime,
) -> PhotoAnnonce:
    verifier_modifiable(prestataire)
    deja = photos_de(db, annonce)
    if len(deja) >= reglages.ANNONCE_PHOTOS_MAX:
        raise ErreurRegle(f"Au plus {reglages.ANNONCE_PHOTOS_MAX} photos par annonce : retirez-en une d'abord.")
    fichiers.verifier(
        contenu, type_mime, types_acceptes=reglages.PHOTO_TYPES_ACCEPTES, taille_max_octets=reglages.PHOTO_TAILLE_MAX_OCTETS
    )
    fichier = fichiers.enregistrer(db, compte, nom_fichier=nom_fichier, type_mime=type_mime, contenu=contenu, maintenant=maintenant)
    photo = PhotoAnnonce(annonce_id=annonce.id, fichier_id=fichier.id, ordre=len(deja) + 1)
    db.add(photo)
    db.flush()
    journal.noter(
        db, auteur_id=compte.id, action="ajouter_photo_annonce", table_cible="annonce", ligne_id=annonce.id,
        apres={"fichier_id": fichier.id, "ordre": photo.ordre}, maintenant=maintenant,
    )
    return photo


def retirer_photo(db: Session, prestataire: Prestataire, annonce: Annonce, ordre: int, maintenant: datetime) -> None:
    """Les photos suivantes remontent d'un rang (ex. on retire la n° 2 : la n° 3 devient la n° 2).
    Le fichier reste rangé (comme l'ancienne photo d'un profil)."""
    verifier_modifiable(prestataire)
    photos = photos_de(db, annonce)
    photo = next((p for p in photos if p.ordre == ordre), None)
    if photo is None:
        raise ErreurRegle("Cette photo n'existe pas.", 404)
    db.delete(photo)
    db.flush()
    for suivante in photos:
        if suivante.ordre > ordre:
            suivante.ordre -= 1
            db.flush()  # un rang à la fois : deux photos n'ont jamais le même numéro
    journal.noter(
        db, auteur_id=prestataire.compte_id, action="retirer_photo_annonce", table_cible="annonce", ligne_id=annonce.id,
        avant={"fichier_id": photo.fichier_id, "ordre": ordre}, maintenant=maintenant,
    )


# ---------- Ce que voient les clients ----------


def modes_de_paiement(annonce: Annonce, prestataire: Prestataire) -> list[str]:
    """La carte est un souhait : proposée seulement si le SIRET est vérifié en ce moment et que Stripe a vérifié son
    compte (lot 5.1) ; sinon espèces (ex. SIRET de Julie refusé : « carte ou espèces » devient « espèces » sans qu'elle
    ressaisisse rien)."""
    carte = annonce.paiement_carte and prestataire.siret_statut == "verifie" and prestataire.stripe_pret
    especes = annonce.paiement_especes or (annonce.paiement_carte and not carte)
    return [mode for mode, oui in (("carte", carte), ("especes", especes)) if oui]


def raison_cachee(db: Session, annonce: Annonce, prestataire: Prestataire, maintenant: datetime) -> str | None:
    """Pourquoi les clients ne voient pas cette annonce ; None = visible de tous."""
    if prestataire.statut == "bloque":
        return "Votre profil est bloqué par l'administrateur."
    if prestataire.statut in ("en_pause", "arrete"):
        return "Votre activité est en pause." if prestataire.statut == "en_pause" else "Votre activité est arrêtée."
    if annonce.statut != "en_ligne":
        return "Annonce en pause." if annonce.statut == "en_pause" else "Annonce retirée."
    if annonce.metier_id not in metiers_exerces(db, prestataire, aujourd_hui(maintenant)):
        return "Vous avez arrêté ce métier (date de fin passée)."
    return None


def annonces_du_prestataire(db: Session, prestataire: Prestataire) -> list[Annonce]:
    return list(db.scalars(select(Annonce).where(Annonce.prestataire_id == prestataire.id).order_by(Annonce.cree_le.desc())))
