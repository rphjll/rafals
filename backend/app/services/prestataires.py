"""Profil prestataire. Règles : .doc/regles-metier/RM-PRESTATAIRES.md, RM-COMPTES.md (qui peut devenir prestataire),
RM-ANNONCES.md (date de fin d'un métier au lieu d'un bouton « supprimer »)."""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from sqlalchemy import exists, or_, select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.annonces import Annonce
from app.modeles.comptes import Compte
from app.modeles.metiers import Metier
from app.modeles.prestataires import Commune, MetierSecondaire, PhotoPrestataire, Prestataire
from app.services import droits, fichiers, journal
from app.services import rendez_vous_communs as communs
from app.services import siret as service_siret
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


SIRET_NON_VALIDE = ("Ce SIRET n'est pas valide : il fait 14 chiffres, et le dernier sert de contrôle. "
                    "Recopiez-le depuis votre avis de situation INSEE ou vos factures.")


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


def _controler_siret(siret: str | None, compte: Compte, maintenant: datetime) -> tuple[str, datetime | None]:
    """Renvoie (état du SIRET, date de vérification). Un SIRET refusé par l'État n'est pas enregistré :
    la personne voit tout de suite la raison. Service de l'État en panne : « à vérifier » (nouvel essai plus tard)."""
    if siret is None:
        return "absent", None
    resultat = service_siret.verifier(siret, compte)
    if resultat.statut == "refuse":
        raise ErreurRegle(resultat.message)
    return resultat.statut, (maintenant if resultat.statut == "verifie" else None)


def ajouter_siret(db: Session, compte: Compte, prestataire: Prestataire, siret: str, maintenant: datetime) -> Prestataire:
    """« J'ai déjà une entreprise » (demande de Raphael du 04/10/2026) : le SIRET est ajouté au profil, sans rien créer.
    Même contrôle que dans « Mon activité » : 14 chiffres, clé, puis vérification auprès de l'État."""
    if prestataire.statut == "arrete":
        raise ErreurRegle("Votre activité est arrêtée : ce profil ne peut plus être modifié.")
    if prestataire.siret:
        raise ErreurRegle(f"Votre profil a déjà un SIRET ({prestataire.siret}) : changez-le dans « Mon activité ».")
    propre = normaliser_siret(siret)
    if propre is None or not siret_valide(propre):
        raise ErreurRegle(SIRET_NON_VALIDE)
    prestataire.siret_statut, prestataire.siret_verifie_le = _controler_siret(propre, compte, maintenant)
    prestataire.siret = propre
    journal.noter(
        db, auteur_id=compte.id, action="ajouter_siret", table_cible="prestataire", ligne_id=prestataire.id,
        avant={"siret": None}, apres={"siret": propre, "siret_statut": prestataire.siret_statut}, maintenant=maintenant,
    )
    return prestataire


def reverifier_sirets_en_attente(db: Session, maintenant: datetime) -> int:
    """Nouvel essai pour les SIRET restés « à vérifier » (service de l'État en panne au moment de l'envoi).
    Lancé toutes les 30 minutes par le serveur. S'arrête au premier « toujours en panne ». Renvoie le nombre traité."""
    traites = 0
    for prestataire in db.scalars(select(Prestataire).where(Prestataire.siret_statut == "a_verifier")).all():
        compte = db.get_one(Compte, prestataire.compte_id)
        resultat = service_siret.verifier(prestataire.siret or "", compte)
        if resultat.statut == "a_verifier":
            break
        prestataire.siret_statut = resultat.statut
        prestataire.siret_verifie_le = maintenant if resultat.statut == "verifie" else None
        journal.noter(
            db, auteur_id=None, action="reverifier_siret", table_cible="prestataire", ligne_id=prestataire.id,
            avant={"siret_statut": "a_verifier"}, apres={"siret_statut": resultat.statut, "message": resultat.message},
            maintenant=maintenant,
        )
        traites += 1
    return traites


def valider_siret_a_la_main(db: Session, administrateur: Compte, prestataire_id: int, maintenant: datetime) -> Prestataire:
    """Par un administrateur, pour un cas particulier (ex. salarié qui n'est pas dirigeant, après avoir vu un justificatif)."""
    prestataire = db.get(Prestataire, prestataire_id)
    if prestataire is None:
        raise ErreurRegle("Ce prestataire n'existe pas.", 404)
    if prestataire.siret is None:
        raise ErreurRegle("Ce prestataire n'a pas indiqué de SIRET.")
    avant = prestataire.siret_statut
    prestataire.siret_statut = "verifie"
    prestataire.siret_verifie_le = maintenant
    journal.noter(
        db, auteur_id=administrateur.id, action="valider_siret_a_la_main", table_cible="prestataire", ligne_id=prestataire.id,
        avant={"siret_statut": avant}, apres={"siret_statut": "verifie"}, maintenant=maintenant,
    )
    return prestataire


# ---------- Création et modification ----------


def profil_de(db: Session, compte: Compte) -> Prestataire | None:
    return db.scalar(select(Prestataire).where(Prestataire.compte_id == compte.id))


def aujourd_hui(maintenant: datetime) -> date:
    """Le jour en France (une date de fin « 15/11 » se lit à l'heure de Paris)."""
    return maintenant.astimezone(reglages.FUSEAU_AFFICHAGE).date()


def en_cours(fin_le: date | None, jour: date) -> bool:
    """Un métier est encore exercé le jour donné si sa date de fin n'est pas dépassée (fin le 15/11 → exercé le 15/11)."""
    return fin_le is None or fin_le >= jour


def lignes_secondaires(db: Session, prestataire: Prestataire) -> list[MetierSecondaire]:
    """Dans l'ordre où ils ont été ajoutés au profil."""
    return list(db.scalars(
        select(MetierSecondaire).where(MetierSecondaire.prestataire_id == prestataire.id).order_by(MetierSecondaire.id)
    ))


def metiers_secondaires(db: Session, prestataire: Prestataire, jour: date) -> list[int]:
    """Métiers secondaires encore exercés ce jour-là."""
    return [ligne.metier_id for ligne in lignes_secondaires(db, prestataire) if en_cours(ligne.fin_le, jour)]


def metiers_exerces(db: Session, prestataire: Prestataire, jour: date) -> list[int]:
    """Métier principal (s'il n'est pas arrêté) puis métiers secondaires exercés ce jour-là : ceux où il peut publier."""
    principal = [prestataire.metier_principal_id] if en_cours(prestataire.metier_principal_fin_le, jour) else []
    return principal + metiers_secondaires(db, prestataire, jour)


def _a_des_annonces(db: Session, prestataire: Prestataire, metier_id: int) -> bool:
    return bool(db.scalar(select(exists().where(Annonce.prestataire_id == prestataire.id, Annonce.metier_id == metier_id))))


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
        raise ErreurRegle(SIRET_NON_VALIDE)
    return Profil(nom, profil.metier_principal_id, profil.commune_id, profil.distance_km, presentation, siret, secondaires)


def _nom_metier(db: Session, metier_id: int) -> str:
    return db.get_one(Metier, metier_id).nom


def _mettre_a_jour_metiers(
    db: Session, prestataire: Prestataire, ancien_principal: int | None, voulus: list[int], jour: date
) -> None:
    """Applique les métiers choisis dans le formulaire du profil (RM-ANNONCES : pas de bouton « supprimer ») :
    - un métier arrêté (date de fin passée) remis dans la liste reprend (ex. Karim remet Chauffagiste en mars) ;
    - un métier arrêté absent de la liste reste arrêté, ses annonces cachées mais gardées ;
    - un métier exercé retiré de la liste n'est accepté que s'il n'a aucune annonce, sinon il faut une date de fin.
    À appeler AVANT de changer prestataire.metier_principal_id."""
    nouveau_principal = prestataire.metier_principal_id
    lignes = {ligne.metier_id: ligne for ligne in lignes_secondaires(db, prestataire)} if prestataire.id else {}
    principal_change = ancien_principal is not None and ancien_principal != nouveau_principal

    if principal_change and ancien_principal not in voulus and _a_des_annonces(db, prestataire, ancien_principal):
        if en_cours(prestataire.metier_principal_fin_le, jour):
            raise ErreurRegle(
                f"Vous avez des annonces dans « {_nom_metier(db, ancien_principal)} » : gardez-le en métier "
                "secondaire, ou mettez-lui une date de fin dans votre calendrier."
            )
        # Métier principal déjà arrêté (ex. Léa) : il reste dans le profil comme métier arrêté, ses annonces gardées
        db.add(MetierSecondaire(prestataire_id=prestataire.id, metier_id=ancien_principal, fin_le=prestataire.metier_principal_fin_le))
    if principal_change:
        prestataire.metier_principal_fin_le = None
        prestataire.metier_principal_suivant_id = None

    for metier_id, ligne in lignes.items():
        if metier_id == nouveau_principal:
            db.delete(ligne)  # devient le métier principal
        elif metier_id in voulus:
            if not en_cours(ligne.fin_le, jour):
                ligne.fin_le = None  # reprise d'un métier arrêté
        elif en_cours(ligne.fin_le, jour):
            if _a_des_annonces(db, prestataire, metier_id):
                raise ErreurRegle(
                    f"Vous avez des annonces dans « {_nom_metier(db, metier_id)} » : pour arrêter ce métier, "
                    "mettez-lui une date de fin dans votre calendrier."
                )
            db.delete(ligne)  # métier jamais utilisé (ex. ajouté par erreur)
    db.flush()
    for metier_id in voulus:
        if metier_id not in lignes:
            db.add(MetierSecondaire(prestataire_id=prestataire.id, metier_id=metier_id))
    if prestataire.metier_principal_suivant_id is not None and prestataire.metier_principal_suivant_id not in voulus:
        prestataire.metier_principal_suivant_id = None
    db.flush()


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
    siret_statut, siret_verifie_le = _controler_siret(p.siret, compte, maintenant)
    prestataire = Prestataire(
        compte_id=compte.id,
        metier_principal_id=p.metier_principal_id,
        commune_id=p.commune_id,
        nom_affiche=p.nom_affiche,
        presentation=p.presentation,
        distance_km=p.distance_km,
        siret=p.siret,
        siret_statut=siret_statut,
        siret_verifie_le=siret_verifie_le,
        statut="actif",
        statut_change_le=maintenant,
        cree_le=maintenant,
    )
    db.add(prestataire)
    db.flush()
    _mettre_a_jour_metiers(db, prestataire, None, p.metiers_secondaires, aujourd_hui(maintenant))
    journal.noter(
        db, auteur_id=compte.id, action="devenir_prestataire", table_cible="prestataire", ligne_id=prestataire.id,
        apres=_etat(prestataire, p.metiers_secondaires), maintenant=maintenant,
    )
    return prestataire


def modifier_profil(db: Session, prestataire: Prestataire, profil: Profil, maintenant: datetime) -> Prestataire:
    if prestataire.statut == "arrete":
        raise ErreurRegle("Votre activité est arrêtée : ce profil ne peut plus être modifié.")
    jour = aujourd_hui(maintenant)
    avant = _etat(prestataire, metiers_secondaires(db, prestataire, jour))
    p = _verifier(db, profil)
    if p.siret != prestataire.siret:
        # Un SIRET nouveau ou changé est vérifié tout de suite auprès de l'État ; le retirer = « absent »
        compte = db.get_one(Compte, prestataire.compte_id)
        prestataire.siret_statut, prestataire.siret_verifie_le = _controler_siret(p.siret, compte, maintenant)
        prestataire.siret = p.siret
    prestataire.nom_affiche = p.nom_affiche
    prestataire.presentation = p.presentation
    ancien_principal = prestataire.metier_principal_id
    prestataire.metier_principal_id = p.metier_principal_id
    _mettre_a_jour_metiers(db, prestataire, ancien_principal, p.metiers_secondaires, jour)
    prestataire.commune_id = p.commune_id
    prestataire.distance_km = p.distance_km
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


# ---------- Photos de son travail (10 au plus, la n° 1 montrée en premier ; RM-PRESTATAIRES § « Sans annonces ») ----------


def photos_de(db: Session, prestataire_id: int) -> list[PhotoPrestataire]:
    return list(db.scalars(
        select(PhotoPrestataire).where(PhotoPrestataire.prestataire_id == prestataire_id).order_by(PhotoPrestataire.ordre)
    ))


def ajouter_photo_travail(
    db: Session, compte: Compte, prestataire: Prestataire, *, nom_fichier: str, type_mime: str, contenu: bytes, maintenant: datetime
) -> PhotoPrestataire:
    """Ex. Karim ajoute la photo d'une salle de bain refaite : elle prend le rang suivant (la 3e photo = n° 3)."""
    if prestataire.statut == "arrete":
        raise ErreurRegle("Votre activité est arrêtée : ce profil ne peut plus être modifié.")
    deja = photos_de(db, prestataire.id)
    if len(deja) >= reglages.PRESTATAIRE_PHOTOS_MAX:
        raise ErreurRegle(f"Au plus {reglages.PRESTATAIRE_PHOTOS_MAX} photos sur votre profil : retirez-en une d'abord.")
    fichiers.verifier(
        contenu, type_mime, types_acceptes=reglages.PHOTO_TYPES_ACCEPTES, taille_max_octets=reglages.PHOTO_TAILLE_MAX_OCTETS
    )
    fichier = fichiers.enregistrer(db, compte, nom_fichier=nom_fichier, type_mime=type_mime, contenu=contenu, maintenant=maintenant)
    photo = PhotoPrestataire(prestataire_id=prestataire.id, fichier_id=fichier.id, ordre=len(deja) + 1)
    db.add(photo)
    db.flush()
    journal.noter(
        db, auteur_id=compte.id, action="ajouter_photo_travail", table_cible="prestataire", ligne_id=prestataire.id,
        apres={"fichier_id": fichier.id, "ordre": photo.ordre}, maintenant=maintenant,
    )
    return photo


def retirer_photo_travail(db: Session, prestataire: Prestataire, ordre: int, maintenant: datetime) -> None:
    """Les photos suivantes remontent d'un rang (ex. on retire la n° 2 : la n° 3 devient la n° 2).
    Le fichier reste rangé (comme l'ancienne photo d'un profil)."""
    if prestataire.statut == "arrete":
        raise ErreurRegle("Votre activité est arrêtée : ce profil ne peut plus être modifié.")
    photos = photos_de(db, prestataire.id)
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
        db, auteur_id=prestataire.compte_id, action="retirer_photo_travail", table_cible="prestataire", ligne_id=prestataire.id,
        avant={"fichier_id": photo.fichier_id, "ordre": ordre}, maintenant=maintenant,
    )


# ---------- Date de fin d'un métier (RM-ANNONCES) ----------


def _texte(etat: dict) -> dict:
    return {cle: str(valeur) if isinstance(valeur, date) else valeur for cle, valeur in etat.items()}


def fixer_fin_metier(
    db: Session, prestataire: Prestataire, metier_id: int, fin_le: date | None, suivant_id: int | None, maintenant: datetime
) -> Prestataire:
    """Met (ou enlève, fin_le vide) la date de fin d'un métier du profil.
    Métier principal : après sa date de fin, un métier secondaire devient principal tout seul ; s'il y en a plusieurs,
    celui choisi (suivant_id), sinon le 1er ajouté. Sans métier secondaire : le profil reste affiché, sans annonce.
    Enlever la date de fin d'un métier arrêté = le reprendre. (Annulation des rendez-vous après la date : niveau 4.)"""
    if prestataire.statut == "arrete":
        raise ErreurRegle("Votre activité est arrêtée : ce profil ne peut plus être modifié.")
    jour = aujourd_hui(maintenant)
    if fin_le is not None and fin_le < jour:
        raise ErreurRegle("La date de fin ne peut pas être déjà passée.")
    lignes = lignes_secondaires(db, prestataire)

    if metier_id == prestataire.metier_principal_id:
        avant = {"fin_le": prestataire.metier_principal_fin_le, "suivant_id": prestataire.metier_principal_suivant_id}
        suivant = None
        if fin_le is not None:
            # Candidats : métiers secondaires encore exercés le lendemain de la date de fin
            candidats = [ligne.metier_id for ligne in lignes if en_cours(ligne.fin_le, fin_le + timedelta(days=1))]
            if suivant_id is not None and suivant_id not in candidats:
                raise ErreurRegle("Choisissez, parmi vos métiers secondaires, celui qui deviendra principal.")
            suivant = suivant_id if suivant_id is not None else (candidats[0] if candidats else None)
        prestataire.metier_principal_fin_le = fin_le
        prestataire.metier_principal_suivant_id = suivant
        apres = {"fin_le": fin_le, "suivant_id": suivant}
    else:
        ligne = next((ligne for ligne in lignes if ligne.metier_id == metier_id), None)
        if ligne is None:
            raise ErreurRegle("Ce métier n'est pas dans votre profil.", 404)
        reprise = fin_le is None and not en_cours(ligne.fin_le, jour)
        if reprise and len(metiers_secondaires(db, prestataire, jour)) >= reglages.PRESTATAIRE_METIERS_SECONDAIRES_MAX:
            raise ErreurRegle(f"Au plus {reglages.PRESTATAIRE_METIERS_SECONDAIRES_MAX} métiers secondaires.")
        avant = {"fin_le": ligne.fin_le}
        ligne.fin_le = fin_le
        if fin_le is not None and prestataire.metier_principal_suivant_id == metier_id:
            prestataire.metier_principal_suivant_id = None
        apres = {"fin_le": fin_le}
    if fin_le is not None:
        # RM-ANNONCES : les réservations de ce métier après la date de fin sont annulées
        lendemain = datetime.combine(fin_le + timedelta(days=1), datetime.min.time(), tzinfo=reglages.FUSEAU_AFFICHAGE)
        for rdv in communs.actifs_a_venir(db, prestataire, maintenant):
            if rdv.debut >= lendemain and rdv.metier_id == metier_id:
                communs.annuler_par_rafals(db, rdv, "Le prestataire n'exerce plus ce métier à cette date.",
                                           prestataire.compte_id, maintenant)
    journal.noter(
        db, auteur_id=prestataire.compte_id, action="fixer_fin_metier", table_cible="prestataire", ligne_id=prestataire.id,
        avant={"metier_id": metier_id, **_texte(avant)}, apres={"metier_id": metier_id, **_texte(apres)},
        maintenant=maintenant,
    )
    return prestataire


def _mettre_en_pause_annonces_arretees(db: Session, jour: date, maintenant: datetime) -> None:
    """Annonces en ligne dans un métier arrêté → en pause (gardées ; le prestataire les republie s'il reprend le métier)."""
    avec_fin_passee = select(Prestataire).where(Prestataire.statut != "arrete", or_(
        Prestataire.metier_principal_fin_le < jour,
        Prestataire.id.in_(select(MetierSecondaire.prestataire_id).where(MetierSecondaire.fin_le < jour)),
    ))
    for prestataire in db.scalars(avec_fin_passee).all():
        exerces = metiers_exerces(db, prestataire, jour)
        en_ligne = select(Annonce).where(Annonce.prestataire_id == prestataire.id, Annonce.statut == "en_ligne")
        for annonce in db.scalars(en_ligne).all():
            if annonce.metier_id not in exerces:
                annonce.statut, annonce.statut_change_le = "en_pause", maintenant
                journal.noter(
                    db, auteur_id=None, action="annonce_pause_metier_arrete", table_cible="annonce", ligne_id=annonce.id,
                    avant={"statut": "en_ligne"}, apres={"statut": "en_pause"}, maintenant=maintenant,
                )


def appliquer_fins_de_metier(db: Session, maintenant: datetime) -> int:
    """Lancé toutes les heures. 1) Les annonces d'un métier arrêté passent en pause. 2) Métier principal dont la date
    de fin est passée : un métier secondaire encore exercé devient principal (celui choisi, sinon le 1er ajouté) ;
    l'ancien reste dans le profil comme métier arrêté. Renvoie le nombre de métiers principaux remplacés."""
    jour = aujourd_hui(maintenant)
    _mettre_en_pause_annonces_arretees(db, jour, maintenant)
    traites = 0
    requete = select(Prestataire).where(Prestataire.metier_principal_fin_le < jour, Prestataire.statut != "arrete")
    for prestataire in db.scalars(requete).all():
        actives = [ligne for ligne in lignes_secondaires(db, prestataire) if en_cours(ligne.fin_le, jour)]
        choix = next((ligne for ligne in actives if ligne.metier_id == prestataire.metier_principal_suivant_id), None)
        choix = choix or (actives[0] if actives else None)
        if choix is None:
            continue  # seul métier arrêté (ex. Léa) : le profil reste affiché, sans annonce
        ancien, fin, nouveau = prestataire.metier_principal_id, prestataire.metier_principal_fin_le, choix.metier_id
        db.delete(choix)
        db.flush()
        db.add(MetierSecondaire(prestataire_id=prestataire.id, metier_id=ancien, fin_le=fin))
        prestataire.metier_principal_id = nouveau
        prestataire.metier_principal_fin_le = None
        prestataire.metier_principal_suivant_id = None
        journal.noter(
            db, auteur_id=None, action="changer_metier_principal_apres_fin", table_cible="prestataire",
            ligne_id=prestataire.id, avant={"metier_principal_id": ancien}, apres={"metier_principal_id": nouveau},
            maintenant=maintenant,
        )
        traites += 1
    return traites


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
    if action == "arreter" and communs.actifs_a_venir(db, prestataire, maintenant):
        raise ErreurRegle("Vous avez des rendez-vous à venir : annulez-les d'abord (« Mon agenda › Rendez-vous »), "
                          "puis arrêtez votre activité.")
    departs, arrivee = _TRANSITIONS_PRESTATAIRE[action]
    if prestataire.statut not in departs:
        messages = {"pause": "Votre profil est déjà en pause.", "reprendre": "Votre profil est déjà actif."}
        raise ErreurRegle(messages.get(action, "Ce changement n'est pas possible."))
    _changer_statut(db, prestataire, arrivee, prestataire.compte_id, f"prestataire_{action}", maintenant)
    return prestataire


def bloquer(db: Session, administrateur: Compte, prestataire_id: int, *, bloque: bool, maintenant: datetime) -> Prestataire:
    """Par un administrateur. Bloquer annule ses rendez-vous à venir (clients prévenus) ; débloquer remet le profil actif."""
    prestataire = db.get(Prestataire, prestataire_id)
    if prestataire is None:
        raise ErreurRegle("Ce prestataire n'existe pas.", 404)
    if prestataire.statut == "arrete":
        raise ErreurRegle("Ce prestataire a arrêté son activité : il ne peut être ni bloqué ni débloqué.")
    if bloque and prestataire.statut != "bloque":
        _changer_statut(db, prestataire, "bloque", administrateur.id, "bloquer_prestataire", maintenant)
        # RM-PRESTATAIRES : ses rendez-vous à venir sont annulés et les clients prévenus
        for rdv in communs.actifs_a_venir(db, prestataire, maintenant):
            communs.annuler_par_rafals(db, rdv, "Ce prestataire n'est plus disponible sur rafals.", administrateur.id, maintenant)
    elif not bloque and prestataire.statut == "bloque":
        _changer_statut(db, prestataire, "actif", administrateur.id, "debloquer_prestataire", maintenant)
    return prestataire
