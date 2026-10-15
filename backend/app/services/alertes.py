"""Alertes des prestataires : être prévenu d'une nouvelle demande de son métier près de chez soi.
Règles : .doc/regles-metier/RM-ALERTES.md (validé par Raphael le 04/10/2026).
- Qui est prévenu : prestataire en activité, métier exercé, ville dans son rayon, alerte du métier pas coupée ;
  jamais l'auteur de la demande, ni un prestataire sans SIRET pour un métier qui en demande un.
- Mail : à chaque demande (au départ, 20 par jour au plus), un seul mail le soir à 18 h, ou aucun.
- Compteur rouge de « Demandes près de chez moi » : les demandes arrivées depuis sa dernière visite.
(Les notifications sur le téléphone : lot 8.7.)"""

from datetime import datetime, time, timedelta

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.comptes import Compte
from app.modeles.demandes import Demande
from app.modeles.metiers import Metier
from app.modeles.prestataires import AlerteCoupee, Commune, Prestataire
from app.services import communes, journal, mails, particuliers
from app.services import demandes as service_demandes
from app.services import prestataires as service_prestataires
from app.services import propositions
from app.services.erreurs import ErreurRegle

PARIS = reglages.FUSEAU_AFFICHAGE
MAILS = ("chaque_demande", "resume", "aucun")


# ---------- Réglages : onglet « Alertes » ----------


def metiers_coupes(db: Session, prestataire: Prestataire) -> set[int]:
    return set(db.scalars(select(AlerteCoupee.metier_id).where(AlerteCoupee.prestataire_id == prestataire.id)))


def regler(db: Session, prestataire: Prestataire, alerte_mail: str, coupes: list[int], maintenant: datetime) -> None:
    """Ex. Karim : « Me prévenir » pour Plombier, « Ne pas me prévenir » pour Jardinier, un seul mail le soir."""
    if alerte_mail not in MAILS:
        raise ErreurRegle("Choisissez : un mail à chaque demande, un seul mail le soir, ou aucun mail.")
    jour = maintenant.astimezone(PARIS).date()
    exerces = set(service_prestataires.metiers_exerces(db, prestataire, jour))
    if not set(coupes) <= exerces:
        raise ErreurRegle("Ce métier n'est pas dans votre profil.")
    avant = {"alerte_mail": prestataire.alerte_mail, "coupes": sorted(metiers_coupes(db, prestataire))}
    prestataire.alerte_mail = alerte_mail
    db.execute(delete(AlerteCoupee).where(AlerteCoupee.prestataire_id == prestataire.id))
    for metier_id in sorted(set(coupes)):
        db.add(AlerteCoupee(prestataire_id=prestataire.id, metier_id=metier_id, cree_le=maintenant))
    journal.noter(db, auteur_id=prestataire.compte_id, action="regler_alertes", table_cible="prestataire", ligne_id=prestataire.id,
                  avant=avant, apres={"alerte_mail": alerte_mail, "coupes": sorted(set(coupes))}, maintenant=maintenant)
    db.flush()


# ---------- Qui prévenir ----------


def _a_prevenir(db: Session, prestataire: Prestataire, demande: Demande, maintenant: datetime) -> bool:
    if not propositions.concerne(db, prestataire, demande, maintenant):
        return False
    if particuliers.metier_interdit(db, prestataire, demande.metier_id) is not None:
        return False  # sans SIRET, il ne pourrait pas répondre : pas d'alerte
    return demande.metier_id not in metiers_coupes(db, prestataire)


def _texte(db: Session, prestataire: Prestataire, demande: Demande) -> str:
    """« Fuite sous l'évier, Talence (5 km) » : jamais le nom, le téléphone ni l'adresse."""
    ville = db.get_one(Commune, demande.commune_id)
    depart = propositions.commune_de_depart(db, prestataire) or db.get_one(Commune, prestataire.commune_id)
    km = round(communes.distance_km(depart, ville))
    return f"{demande.titre}, {ville.nom} ({km} km)"


def prevenir_nouvelle_demande(db: Session, demande: Demande, maintenant: datetime) -> int:
    """À la publication : un mail aux prestataires concernés qui ont choisi « un mail à chaque demande », dans la limite
    de 20 par jour (les suivants vont dans le résumé de 18 h). Rend le nombre de mails envoyés."""
    jour = maintenant.astimezone(PARIS).date()
    envoyes = 0
    for prestataire in db.scalars(select(Prestataire).where(Prestataire.statut == "actif", Prestataire.alerte_mail == "chaque_demande")):
        if not _a_prevenir(db, prestataire, demande, maintenant):
            continue
        if prestataire.alertes_mail_jour != jour:
            prestataire.alertes_mail_jour, prestataire.alertes_mail_nombre = jour, 0
        if prestataire.alertes_mail_nombre >= reglages.ALERTE_MAILS_PAR_JOUR:
            continue
        compte = db.get_one(Compte, prestataire.compte_id)
        if compte.ferme_le is not None:
            continue
        metier = db.get_one(Metier, demande.metier_id).nom
        mails.envoyer_mail(compte.email, f"rafals : nouvelle demande, {_texte(db, prestataire, demande)}",
                           f"Un client cherche « {metier} » près de chez vous : {_texte(db, prestataire, demande)}. "
                           "Pour la lire et répondre : « Demandes près de chez moi ».")
        prestataire.alertes_mail_nombre += 1
        envoyes += 1
    db.flush()
    return envoyes


# ---------- Le résumé de 18 h ----------


def envoyer_resumes(db: Session, maintenant: datetime) -> int:
    """À partir de 18 h (heure de Paris), une fois par jour : un seul mail avec les demandes du jour, pour ceux qui ont
    choisi le résumé, et pour ceux qui ont dépassé 20 mails dans la journée (les demandes en trop)."""
    local = maintenant.astimezone(PARIS)
    if local.hour < reglages.ALERTE_RESUME_HEURE:
        return 0
    debut_du_jour = datetime.combine(local.date(), time(0), tzinfo=PARIS)
    heure_du_resume = datetime.combine(local.date(), time(reglages.ALERTE_RESUME_HEURE), tzinfo=PARIS)
    du_jour = [d for d in service_demandes.ouvertes(db, maintenant) if d.cree_le >= debut_du_jour - timedelta(hours=6)]
    envoyes = 0
    for prestataire in db.scalars(select(Prestataire).where(Prestataire.statut == "actif", Prestataire.alerte_mail != "aucun")):
        if prestataire.resume_envoye_le is not None and prestataire.resume_envoye_le >= heure_du_resume:
            continue  # déjà envoyé aujourd'hui
        depuis = max(prestataire.resume_envoye_le or debut_du_jour, heure_du_resume - timedelta(days=1))
        # (pas les demandes publiées avant son inscription : il n'a reçu aucun mail pour elles)
        depuis = max(depuis, prestataire.cree_le)
        siennes = sorted((d for d in du_jour if d.cree_le > depuis and _a_prevenir(db, prestataire, d, maintenant)),
                         key=lambda d: d.cree_le)
        if prestataire.alerte_mail == "chaque_demande":
            # Les premières ont déjà eu leur mail : seules celles au-delà du plafond vont dans le résumé
            deja = prestataire.alertes_mail_nombre if prestataire.alertes_mail_jour == local.date() else 0
            siennes = siennes[deja:] if deja >= reglages.ALERTE_MAILS_PAR_JOUR else []
        prestataire.resume_envoye_le = maintenant
        compte = db.get_one(Compte, prestataire.compte_id)
        if not siennes or compte.ferme_le is not None:
            continue
        lignes = "\n".join(f"- {_texte(db, prestataire, d)}" for d in siennes)
        nombre = len(siennes)
        mails.envoyer_mail(compte.email, f"rafals : {nombre} demande{'s' if nombre > 1 else ''} près de chez vous aujourd'hui",
                           f"Les demandes du jour dans vos métiers :\n{lignes}\n\nPour les lire et répondre : « Demandes près de chez moi ».")
        envoyes += 1
    db.flush()
    return envoyes


# ---------- Le compteur rouge de « Demandes près de chez moi » ----------


def nouvelles_demandes(db: Session, prestataire: Prestataire, maintenant: datetime) -> int:
    """Demandes de ses métiers et de son rayon arrivées depuis sa dernière visite (toutes s'il n'est jamais venu)."""
    vues = prestataire.demandes_vues_le
    return sum(1 for d in service_demandes.ouvertes(db, maintenant)
               if (vues is None or d.cree_le > vues) and propositions.concerne(db, prestataire, d, maintenant))


def marquer_vues(prestataire: Prestataire, maintenant: datetime) -> None:
    prestataire.demandes_vues_le = maintenant
