"""Calculs des comptes et de la connexion. Règles : .doc/regles-metier/RM-COMPTES.md.

Chaque fonction reçoit « maintenant » (UTC) pour que les tests puissent jouer avec le temps.
Les routes valident (commit) ; seul un échec de connexion valide lui-même son compteur d'erreurs.
"""

from datetime import date, datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app import config, reglages
from app.modeles.comptes import Compte, JetonMail, SessionConnexion
from app.services import mails
from app.services.erreurs import ErreurRegle
from app.services.securite import hacher_jeton, hacher_mot_de_passe, mot_de_passe_correct, nouveau_jeton

MESSAGE_IDENTIFIANTS = "Adresse mail ou mot de passe incorrect."


def normaliser_email(email: str) -> str:
    return email.strip().lower()


def heure_affichee(moment: datetime) -> str:
    """Ex. 14 h 15, à l'heure de Paris."""
    local = moment.astimezone(reglages.FUSEAU_AFFICHAGE)
    return f"{local.hour} h {local.minute:02d}"


def age_le(date_naissance: date, jour: date) -> int:
    anniversaire_passe = (jour.month, jour.day) >= (date_naissance.month, date_naissance.day)
    return jour.year - date_naissance.year - (0 if anniversaire_passe else 1)


def verifier_mot_de_passe_acceptable(mot_de_passe: str) -> None:
    if len(mot_de_passe) < reglages.MOT_DE_PASSE_LONGUEUR_MIN:
        raise ErreurRegle(
            f"Le mot de passe doit contenir au moins {reglages.MOT_DE_PASSE_LONGUEUR_MIN} caractères "
            "(ex. MaisonBleue44)."
        )


# ---------- Inscription et vérification de l'adresse ----------


def inscrire(
    db: Session,
    *,
    email: str,
    mot_de_passe: str,
    prenom: str,
    nom: str,
    telephone: str,
    date_naissance: date,
    maintenant: datetime,
) -> Compte:
    email = normaliser_email(email)
    if "@" not in email or "." not in email.split("@")[-1]:
        raise ErreurRegle("Cette adresse mail n'est pas valide (ex. marie.dupont@gmail.com).")
    for valeur, libelle in ((prenom, "prénom"), (nom, "nom"), (telephone, "téléphone")):
        if not valeur.strip():
            raise ErreurRegle(f"Le {libelle} est obligatoire.")
    if age_le(date_naissance, maintenant.date()) < reglages.AGE_MINIMUM:
        raise ErreurRegle(f"Il faut avoir au moins {reglages.AGE_MINIMUM} ans pour créer un compte sur rafals.")
    verifier_mot_de_passe_acceptable(mot_de_passe)
    if db.scalar(select(Compte.id).where(Compte.email == email)) is not None:
        raise ErreurRegle("Un compte existe déjà avec cette adresse mail.", 409)

    compte = Compte(
        cree_le=maintenant,
        email=email,
        mot_de_passe_hache=hacher_mot_de_passe(mot_de_passe),
        prenom=prenom.strip(),
        nom=nom.strip(),
        telephone=telephone.strip(),
        date_naissance=date_naissance,
    )
    db.add(compte)
    db.flush()
    envoyer_lien_verification(db, compte, maintenant)
    return compte


def envoyer_lien_verification(db: Session, compte: Compte, maintenant: datetime) -> None:
    clair = _creer_jeton_mail(db, compte, "verification", maintenant, reglages.LIEN_VERIFICATION_DUREE)
    mails.envoyer_mail(
        compte.email,
        "rafals : vérifiez votre adresse mail",
        f"Bonjour {compte.prenom},\n\n"
        "Pour finir votre inscription sur rafals, cliquez sur ce lien :\n"
        f"{config.ADRESSE_SITE}/verifier-adresse?jeton={clair}\n\n"
        f"Ce lien est valable {reglages.LIEN_VERIFICATION_DUREE.days} jours et ne sert qu'une fois.\n"
        "Si vous n'êtes pas à l'origine de cette inscription, ignorez ce mail.",
    )


def renvoyer_lien_verification(db: Session, email: str, maintenant: datetime) -> None:
    """Toujours silencieux : ne dit jamais si l'adresse existe (un inconnu ne doit pas pouvoir le tester)."""
    compte = db.scalar(select(Compte).where(Compte.email == normaliser_email(email)))
    if compte is not None and compte.email_verifie_le is None:
        envoyer_lien_verification(db, compte, maintenant)


def verifier_adresse(db: Session, jeton: str, maintenant: datetime) -> Compte:
    lien = _utiliser_jeton_mail(db, jeton, "verification", maintenant)
    compte = db.get_one(Compte, lien.compte_id)
    if compte.email_verifie_le is None:
        compte.email_verifie_le = maintenant
    return compte


# ---------- Connexion, sessions, déconnexion ----------


def connecter(db: Session, *, email: str, mot_de_passe: str, appareil: str | None, maintenant: datetime) -> tuple[Compte, str]:
    """Renvoie (compte, jeton de session en clair à mettre dans le cookie)."""
    compte = db.scalar(select(Compte).where(Compte.email == normaliser_email(email)))
    if compte is None:
        raise ErreurRegle(MESSAGE_IDENTIFIANTS, 401)

    if compte.bloque_jusqu_au is not None and compte.bloque_jusqu_au > maintenant:
        raise ErreurRegle(
            f"Trop d'erreurs de mot de passe : réessayez après {heure_affichee(compte.bloque_jusqu_au)}.", 423
        )

    if not mot_de_passe_correct(mot_de_passe, compte.mot_de_passe_hache):
        compte.echecs_connexion += 1
        if compte.echecs_connexion >= reglages.ECHECS_AVANT_BLOCAGE:
            compte.echecs_connexion = 0
            compte.bloque_jusqu_au = maintenant + reglages.BLOCAGE_DUREE
            db.commit()  # le blocage doit être gardé même si la demande échoue
            raise ErreurRegle(
                f"{reglages.ECHECS_AVANT_BLOCAGE} erreurs de suite : connexion bloquée jusqu'à "
                f"{heure_affichee(compte.bloque_jusqu_au)}.",
                423,
            )
        db.commit()  # le compteur d'erreurs doit être gardé même si la demande échoue
        raise ErreurRegle(MESSAGE_IDENTIFIANTS, 401)

    compte.echecs_connexion = 0
    compte.bloque_jusqu_au = None
    compte.derniere_connexion_le = maintenant
    compte.inactivite_prevenue_le = None  # se reconnecter annule la fermeture prévue pour inactivité (RM-CLIENTS)
    clair, hache = nouveau_jeton()
    db.add(
        SessionConnexion(
            compte_id=compte.id,
            jeton_hache=hache,
            appareil=(appareil or "")[:200] or None,
            cree_le=maintenant,
            expire_le=maintenant + reglages.SESSION_DUREE,
        )
    )
    return compte, clair


def compte_connecte(db: Session, jeton: str | None, maintenant: datetime) -> Compte | None:
    if not jeton:
        return None
    session = db.scalar(
        select(SessionConnexion).where(
            SessionConnexion.jeton_hache == hacher_jeton(jeton),
            SessionConnexion.fermee_le.is_(None),
            SessionConnexion.expire_le > maintenant,
        )
    )
    compte = None if session is None else db.get(Compte, session.compte_id)
    return None if compte is None or compte.ferme_le is not None else compte


def deconnecter(db: Session, jeton: str | None, maintenant: datetime) -> None:
    if jeton:
        db.execute(
            update(SessionConnexion)
            .where(SessionConnexion.jeton_hache == hacher_jeton(jeton), SessionConnexion.fermee_le.is_(None))
            .values(fermee_le=maintenant)
        )


# ---------- Mot de passe oublié ----------


def demander_nouveau_mot_de_passe(db: Session, email: str, maintenant: datetime) -> None:
    """Toujours silencieux : ne dit jamais si l'adresse existe."""
    compte = db.scalar(select(Compte).where(Compte.email == normaliser_email(email)))
    if compte is None:
        return
    clair = _creer_jeton_mail(db, compte, "mot_de_passe", maintenant, reglages.LIEN_MOT_DE_PASSE_DUREE)
    minutes = int(reglages.LIEN_MOT_DE_PASSE_DUREE.total_seconds() // 60)
    mails.envoyer_mail(
        compte.email,
        "rafals : choisir un nouveau mot de passe",
        f"Bonjour {compte.prenom},\n\n"
        "Pour choisir un nouveau mot de passe, cliquez sur ce lien :\n"
        f"{config.ADRESSE_SITE}/nouveau-mot-de-passe?jeton={clair}\n\n"
        f"Ce lien est valable {minutes} minutes et ne sert qu'une fois.\n"
        "Si vous n'avez rien demandé, ignorez ce mail : votre mot de passe ne change pas.",
    )


def changer_mot_de_passe_oublie(db: Session, jeton: str, nouveau_mot_de_passe: str, maintenant: datetime) -> None:
    verifier_mot_de_passe_acceptable(nouveau_mot_de_passe)
    lien = _utiliser_jeton_mail(db, jeton, "mot_de_passe", maintenant)
    compte = db.get_one(Compte, lien.compte_id)
    compte.mot_de_passe_hache = hacher_mot_de_passe(nouveau_mot_de_passe)
    compte.echecs_connexion = 0
    compte.bloque_jusqu_au = None
    # Par sécurité, tous les appareils connectés doivent se reconnecter avec le nouveau mot de passe
    db.execute(
        update(SessionConnexion)
        .where(SessionConnexion.compte_id == compte.id, SessionConnexion.fermee_le.is_(None))
        .values(fermee_le=maintenant)
    )


# ---------- Liens envoyés par mail ----------


def _creer_jeton_mail(db: Session, compte: Compte, usage: str, cree_le: datetime, duree: timedelta) -> str:
    clair, hache = nouveau_jeton()
    db.add(JetonMail(compte_id=compte.id, usage=usage, jeton_hache=hache, cree_le=cree_le, expire_le=cree_le + duree))
    db.flush()
    return clair


def _utiliser_jeton_mail(db: Session, jeton: str, usage: str, maintenant: datetime) -> JetonMail:
    lien = db.scalar(
        select(JetonMail).where(JetonMail.jeton_hache == hacher_jeton(jeton), JetonMail.usage == usage)
    )
    if lien is None:
        raise ErreurRegle("Ce lien n'est pas valide. Vérifiez que vous avez copié toute l'adresse.")
    if lien.utilise_le is not None:
        raise ErreurRegle("Ce lien a déjà été utilisé. Demandez-en un nouveau.")
    if lien.expire_le <= maintenant:
        raise ErreurRegle("Ce lien a expiré. Demandez-en un nouveau.")
    lien.utilise_le = maintenant
    return lien
