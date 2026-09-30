"""Données du client : adresse, informations, export, fermeture du compte, comptes inactifs.
Règles : .doc/regles-metier/RM-CLIENTS.md (RGPD)."""

import secrets
from datetime import datetime
from typing import Any

from sqlalchemy import or_, select, update
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.agenda import Blocage, PlageHoraire
from app.modeles.annonces import Annonce, Local
from app.modeles.clients import Adresse
from app.modeles.comptes import Compte, SessionConnexion
from app.modeles.fichiers import AccordParental, Fichier
from app.modeles.journal import JournalAction
from app.modeles.metiers import Metier, PropositionMetier
from app.modeles.prestataires import Commune, MetierSecondaire, Prestataire
from app.modeles.rendez_vous import RendezVous
from app.services import communes, journal, mails
from app.services.erreurs import ErreurRegle
from app.services.securite import hacher_mot_de_passe, mot_de_passe_correct

# ---------- Adresse ----------


def adresse_de(db: Session, compte: Compte) -> Adresse | None:
    return db.scalar(select(Adresse).where(Adresse.compte_id == compte.id))


def enregistrer_adresse(
    db: Session, compte: Compte, *, ligne: str, complement: str | None, commune_id: int, code_postal: str, maintenant: datetime
) -> Adresse:
    """Ex. « 8 allée des Pins », Talence, 33400 → accepté ; Talence avec 33600 (code de Pessac) → refusé."""
    controle = communes.controler_adresse(db, ligne=ligne, complement=complement, commune_id=commune_id, code_postal=code_postal)
    ligne, complement, commune, code_postal = controle.ligne, controle.complement, controle.commune, controle.code_postal

    adresse = adresse_de(db, compte)
    avant = None if adresse is None else {"ligne": adresse.ligne, "commune_id": adresse.commune_id}
    if adresse is None:
        adresse = Adresse(compte_id=compte.id, commune_id=commune.id, ligne=ligne, complement=complement, code_postal=code_postal)
        db.add(adresse)
    else:
        adresse.commune_id, adresse.ligne, adresse.complement, adresse.code_postal = commune.id, ligne, complement, code_postal
    adresse.modifiee_le = maintenant
    db.flush()
    journal.noter(
        db, auteur_id=compte.id, action="enregistrer_adresse", table_cible="adresse", ligne_id=adresse.id,
        avant=avant, apres={"ligne": ligne, "commune_id": commune.id}, maintenant=maintenant,
    )
    return adresse


def effacer_adresse(db: Session, compte: Compte, maintenant: datetime) -> None:
    adresse = adresse_de(db, compte)
    if adresse is None:
        return
    journal.noter(
        db, auteur_id=compte.id, action="effacer_adresse", table_cible="adresse", ligne_id=adresse.id,
        avant={"commune_id": adresse.commune_id}, maintenant=maintenant,
    )
    db.delete(adresse)


# ---------- Informations ----------


def modifier_informations(db: Session, compte: Compte, *, prenom: str, nom: str, telephone: str, maintenant: datetime) -> Compte:
    """Prénom, nom, téléphone. (Changer d'adresse mail demandera une nouvelle vérification : plus tard.)"""
    valeurs = {"prénom": prenom.strip(), "nom": nom.strip(), "téléphone": telephone.strip()}
    for libelle, valeur in valeurs.items():
        if not valeur:
            raise ErreurRegle(f"Le {libelle} est obligatoire.")
    avant = {"prenom": compte.prenom, "nom": compte.nom, "telephone": compte.telephone}
    compte.prenom, compte.nom, compte.telephone = valeurs["prénom"], valeurs["nom"], valeurs["téléphone"]
    journal.noter(
        db, auteur_id=compte.id, action="modifier_informations", table_cible="compte", ligne_id=compte.id,
        avant=avant, apres={"prenom": compte.prenom, "nom": compte.nom, "telephone": compte.telephone}, maintenant=maintenant,
    )
    return compte


# ---------- Télécharger mes données (droit d'accès) ----------


def _date(valeur: datetime | Any) -> str | None:
    return None if valeur is None else valeur.isoformat()


def exporter(db: Session, compte: Compte, maintenant: datetime) -> dict[str, Any]:
    """Tout ce que rafals sait sur la personne, lisible (pas de mot de passe ni de jeton secret)."""
    adresse = adresse_de(db, compte)
    commune = db.get(Commune, adresse.commune_id) if adresse else None
    prestataire = db.scalar(select(Prestataire).where(Prestataire.compte_id == compte.id))
    donnees: dict[str, Any] = {
        "exporte_le": _date(maintenant),
        "compte": {
            "email": compte.email, "prenom": compte.prenom, "nom": compte.nom, "telephone": compte.telephone,
            "date_naissance": _date(compte.date_naissance), "adresse_verifiee_le": _date(compte.email_verifie_le),
            "cree_le": _date(compte.cree_le), "derniere_connexion_le": _date(compte.derniere_connexion_le),
            "est_administrateur": compte.est_administrateur,
        },
        "adresse": None if adresse is None else {
            "ligne": adresse.ligne, "complement": adresse.complement, "code_postal": adresse.code_postal,
            "commune": commune.nom if commune else None,
        },
        "appareils_connectes": [
            {"appareil": s.appareil, "depuis": _date(s.cree_le), "jusqu_au": _date(s.expire_le), "fermee_le": _date(s.fermee_le)}
            for s in db.scalars(select(SessionConnexion).where(SessionConnexion.compte_id == compte.id))
        ],
        "profil_prestataire": None,
        "accords_parentaux": [
            {"statut": a.statut, "depose_le": _date(a.depose_le), "decide_le": _date(a.decide_le), "motif_refus": a.motif_refus}
            for a in db.scalars(select(AccordParental).where(AccordParental.compte_id == compte.id))
        ],
        "fichiers_deposes": [
            {"nom": f.nom_origine, "type": f.type_mime, "taille_octets": f.taille_octets, "depose_le": _date(f.depose_le)}
            for f in db.scalars(select(Fichier).where(Fichier.depose_par_id == compte.id))
        ],
        "propositions_de_metier": [
            {"nom": p.nom_propose, "statut": p.statut, "propose_le": _date(p.propose_le)}
            for p in db.scalars(select(PropositionMetier).where(PropositionMetier.propose_par_id == compte.id))
        ],
        "mes_rendez_vous": [
            {"titre": r.titre, "debut": _date(r.debut), "fin": _date(r.fin), "prix_centimes": r.prix_centimes,
             "statut": r.statut, "adresse": r.adresse_ligne}
            for r in db.scalars(select(RendezVous).where(RendezVous.client_id == compte.id).order_by(RendezVous.debut))
        ],
        "journal_de_mes_actions": [
            {"action": j.action, "le": _date(j.fait_le), "avant": j.avant, "apres": j.apres}
            for j in db.scalars(
                select(JournalAction).where(JournalAction.auteur_id == compte.id).order_by(JournalAction.fait_le)
            )
        ],
    }
    if prestataire is not None:
        secondaires = db.scalars(
            select(Metier.nom).join(MetierSecondaire, MetierSecondaire.metier_id == Metier.id)
            .where(MetierSecondaire.prestataire_id == prestataire.id)
        ).all()
        donnees["profil_prestataire"] = {
            "nom_affiche": prestataire.nom_affiche, "presentation": prestataire.presentation,
            "metier_principal": db.get_one(Metier, prestataire.metier_principal_id).nom,
            "metiers_secondaires": list(secondaires),
            "ville": db.get_one(Commune, prestataire.commune_id).nom, "distance_km": prestataire.distance_km,
            "siret": prestataire.siret, "siret_statut": prestataire.siret_statut, "statut": prestataire.statut,
            "cree_le": _date(prestataire.cree_le),
            "local": [
                {"ligne": local.ligne, "complement": local.complement, "code_postal": local.code_postal,
                 "commune": db.get_one(Commune, local.commune_id).nom}
                for local in db.scalars(select(Local).where(Local.prestataire_id == prestataire.id))
            ],
            "annonces": [
                {"titre": a.titre, "metier": db.get_one(Metier, a.metier_id).nom, "description": a.description,
                 "forme_prix": a.forme_prix, "prix_centimes": a.prix_centimes, "duree_minutes": a.duree_minutes,
                 "heures_min": a.heures_min, "heures_max": a.heures_max, "lieu": a.lieu, "statut": a.statut,
                 "cree_le": _date(a.cree_le)}
                for a in db.scalars(select(Annonce).where(Annonce.prestataire_id == prestataire.id).order_by(Annonce.cree_le))
            ],
            "agenda": {
                "semaine_type": [
                    {"jour": p.jour_semaine, "debut": p.debut.isoformat(), "fin": p.fin.isoformat()}
                    for p in db.scalars(select(PlageHoraire).where(PlageHoraire.prestataire_id == prestataire.id))
                ],
                "periodes_bloquees": [
                    {"debut": _date(b.debut), "fin": _date(b.fin), "motif": b.motif}
                    for b in db.scalars(select(Blocage).where(Blocage.prestataire_id == prestataire.id))
                ],
                "pas_minutes": prestataire.agenda_pas_minutes, "pause_minutes": prestataire.agenda_pause_minutes,
                "delai_min_minutes": prestataire.reservation_delai_min_minutes,
                "delai_max_mois": prestataire.reservation_delai_max_mois,
            },
        }
    journal.noter(
        db, auteur_id=compte.id, action="telecharger_mes_donnees", table_cible="compte", ligne_id=compte.id, maintenant=maintenant
    )
    return donnees


# ---------- Fermer le compte ----------


def _effacer_donnees_personnelles(db: Session, compte: Compte, maintenant: datetime) -> None:
    """Efface tout ce qui est personnel ; la ligne reste (sans rien de personnel) pour l'historique."""
    adresse = adresse_de(db, compte)
    if adresse is not None:
        db.delete(adresse)
    # L'adresse du local d'un ancien prestataire peut être son domicile : effacée aussi (ses annonces restent, sans adresse)
    prestataire = db.scalar(select(Prestataire).where(Prestataire.compte_id == compte.id))
    if prestataire is not None:
        for local in db.scalars(select(Local).where(Local.prestataire_id == prestataire.id)):
            db.delete(local)
    # Un compte d'essai garde sa marque @example.com : le nettoyage des données d'essai le retrouvera
    domaine = "example.com" if compte.email.endswith("@example.com") else "rafals.invalid"
    compte.email = f"compte-ferme-{compte.id}@{domaine}"
    compte.prenom, compte.nom = "Compte", "fermé"
    compte.telephone = None
    compte.date_naissance = None
    compte.mot_de_passe_hache = hacher_mot_de_passe(secrets.token_urlsafe(32))  # plus personne ne peut s'y connecter
    compte.est_administrateur = False
    compte.ferme_le = maintenant
    db.execute(
        update(SessionConnexion)
        .where(SessionConnexion.compte_id == compte.id, SessionConnexion.fermee_le.is_(None))
        .values(fermee_le=maintenant)
    )


def _verifier_fermeture_possible(db: Session, compte: Compte) -> None:
    prestataire = db.scalar(select(Prestataire).where(Prestataire.compte_id == compte.id))
    if prestataire is not None and prestataire.statut != "arrete":
        raise ErreurRegle("Arrêtez d'abord votre activité de prestataire (page « Mon activité »), puis fermez votre compte.")
    if compte.est_administrateur:
        autres = db.scalar(select(Compte.id).where(Compte.est_administrateur, Compte.id != compte.id).limit(1))
        if autres is None:
            raise ErreurRegle("Vous êtes le seul administrateur : nommez-en un autre avant de fermer votre compte.")
    # Quand les rendez-vous existeront (niveau 4) : refuser s'il y a un rendez-vous à venir (RM-CLIENTS).


def fermer(db: Session, compte: Compte, mot_de_passe: str, maintenant: datetime) -> None:
    if not mot_de_passe_correct(mot_de_passe, compte.mot_de_passe_hache):
        raise ErreurRegle("Mot de passe incorrect : votre compte n'a pas été fermé.", 403)
    _verifier_fermeture_possible(db, compte)
    identifiant = compte.id
    _effacer_donnees_personnelles(db, compte, maintenant)
    journal.noter(db, auteur_id=identifiant, action="fermer_compte", table_cible="compte", ligne_id=identifiant, maintenant=maintenant)


# ---------- Comptes inactifs (tâche de fond, une fois par jour) ----------


def traiter_inactifs(db: Session, maintenant: datetime) -> tuple[int, int]:
    """1) Prévient par mail les comptes sans connexion depuis 3 ans ; 2) ferme ceux prévenus il y a 30 jours ou plus
    et toujours absents. Ex. dernière connexion le 10/01/2027 → mail le 10/01/2030 → fermé le 09/02/2030.
    Renvoie (prévenus, fermés)."""
    limite = maintenant - reglages.INACTIVITE_DUREE
    derniere = select(Compte).where(
        Compte.ferme_le.is_(None),
        # jamais connecté : on compte depuis l'inscription
        or_(Compte.derniere_connexion_le < limite, (Compte.derniere_connexion_le.is_(None)) & (Compte.cree_le < limite)),
    )
    prevenus = fermes = 0
    for compte in db.scalars(derniere.where(Compte.inactivite_prevenue_le.is_(None))).all():
        date_fermeture = (maintenant + reglages.INACTIVITE_PREAVIS).astimezone(reglages.FUSEAU_AFFICHAGE)
        mails.envoyer_mail(
            compte.email,
            "rafals : votre compte sera fermé dans 30 jours",
            f"Bonjour {compte.prenom},\n\n"
            "Vous ne vous êtes pas connecté à rafals depuis 3 ans. Pour protéger vos données, votre compte sera fermé "
            f"le {date_fermeture:%d/%m/%Y} et vos informations personnelles effacées.\n\n"
            "Pour le garder, il suffit de vous connecter avant cette date.",
        )
        compte.inactivite_prevenue_le = maintenant
        journal.noter(db, auteur_id=None, action="prevenir_inactivite", table_cible="compte", ligne_id=compte.id, maintenant=maintenant)
        prevenus += 1
    for compte in db.scalars(derniere.where(Compte.inactivite_prevenue_le <= maintenant - reglages.INACTIVITE_PREAVIS)).all():
        try:
            _verifier_fermeture_possible(db, compte)
        except ErreurRegle:
            continue  # ex. prestataire encore en activité, seul administrateur : on ne ferme pas automatiquement
        identifiant = compte.id
        _effacer_donnees_personnelles(db, compte, maintenant)
        journal.noter(db, auteur_id=None, action="fermer_compte_inactif", table_cible="compte", ligne_id=identifiant, maintenant=maintenant)
        fermes += 1
    return prevenus, fermes
