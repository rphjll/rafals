"""Rendez-vous : annuler, rappels, coordonnées. Un rendez-vous naît seulement d'une proposition acceptée
(services/propositions.py ; RM-RENDEZ-VOUS § « Sans annonces ») : plus de réservation directe ni de déplacement.
Règles : .doc/regles-metier/RM-RENDEZ-VOUS.md (validé le 30/09/2026). Un rendez-vous n'est jamais effacé.
(Absences et contestations : lot 4.5. Paiement par carte : lot 5.1, services/paiements.py.)"""

from datetime import datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.comptes import Compte
from app.modeles.paiements import Paiement
from app.modeles.prestataires import Commune, Prestataire
from app.modeles.rendez_vous import RendezVous
from app.services import journal, locaux
from app.services import rendez_vous_communs as communs
from app.services.erreurs import ErreurRegle

PARIS = reglages.FUSEAU_AFFICHAGE
ACTIFS = communs.ACTIFS
_texte_moment, _journal, _changer, _prevenir = communs.texte_moment, communs.noter, communs.changer, communs.prevenir


# ---------- Annoncer un nouveau rendez-vous ----------


def annoncer_reservation(db: Session, rdv: RendezVous, maintenant: datetime) -> None:
    """Les mails d'un nouveau rendez-vous (une proposition acceptée : il est confirmé aussitôt)."""
    quand = _texte_moment(rdv.debut)
    _prevenir(db, rdv, sujet=f"rafals : rendez-vous confirmé, {quand}",
              client=f"Votre rendez-vous « {rdv.titre} » est confirmé : {quand}.",
              prestataire=f"Nouveau rendez-vous « {rdv.titre} » : {quand}.")


# ---------- Le prestataire répond ----------


def pas_encore_paye(db: Session, rdv_id: int) -> bool:
    """Réservation par carte dont le paiement n'est pas terminé (ou ne l'a jamais été) : le prestataire ne la voit pas."""
    return db.scalar(select(Paiement.id).where(Paiement.rendez_vous_id == rdv_id,
                                               Paiement.statut.in_(("a_payer", "abandonne")))) is not None


def rendez_vous_du_prestataire(db: Session, prestataire: Prestataire, rdv_id: int) -> RendezVous:
    rdv = db.get(RendezVous, rdv_id)
    if rdv is None or rdv.prestataire_id != prestataire.id or pas_encore_paye(db, rdv.id):
        raise ErreurRegle("Ce rendez-vous n'existe pas.", 404)
    return rdv


def rendez_vous_du_client(db: Session, client: Compte, rdv_id: int) -> RendezVous:
    rdv = db.get(RendezVous, rdv_id)
    if rdv is None or rdv.client_id != client.id:
        raise ErreurRegle("Ce rendez-vous n'existe pas.", 404)
    return rdv


# ---------- Annuler, déplacer ----------


def limite_annulation(prestataire: Prestataire, rdv: RendezVous) -> datetime:
    """Ex. Léa (24 h), rendez-vous mardi 14/10 à 10 h → annulation gratuite jusqu'au lundi 13/10 à 10 h."""
    return rdv.debut - timedelta(hours=prestataire.annulation_delai_heures)


def _dans_le_delai(db: Session, rdv: RendezVous, maintenant: datetime) -> Prestataire:
    prestataire = db.get_one(Prestataire, rdv.prestataire_id)
    if rdv.statut not in ACTIFS:
        raise ErreurRegle("Ce rendez-vous n'est plus actif.")
    if rdv.statut == "confirme" and maintenant > limite_annulation(prestataire, rdv):
        telephone = db.get_one(Compte, prestataire.compte_id).telephone or ""
        raise ErreurRegle(f"Moins de {prestataire.annulation_delai_heures} h avant : appelez {prestataire.nom_affiche}"
                          f"{' au ' + telephone if telephone else ''}.")
    return prestataire


def annuler_par_client(db: Session, client: Compte, rdv: RendezVous, maintenant: datetime) -> RendezVous:
    """Une demande en attente s'annule à tout moment ; un rendez-vous confirmé, jusqu'au délai du prestataire."""
    jamais_paye = pas_encore_paye(db, rdv.id)
    if not jamais_paye:  # pas encore payée : le client peut toujours renoncer (le prestataire ne l'a pas vue)
        _dans_le_delai(db, rdv, maintenant)
    elif rdv.statut not in ACTIFS:
        raise ErreurRegle("Ce rendez-vous n'est plus actif.")
    _changer(rdv, "annule_client", maintenant, "Paiement non terminé" if jamais_paye else None)
    _journal(db, client.id, "annuler_rendez_vous_client", rdv, maintenant)
    if jamais_paye:  # le prestataire n'a jamais vu cette réservation : rien à lui dire
        return rdv
    _prevenir(db, rdv, sujet="rafals : rendez-vous annulé par le client",
              prestataire=f"Le client a annulé « {rdv.titre} », {_texte_moment(rdv.debut)}. L'horaire est de nouveau libre.")
    return rdv


def annuler_par_prestataire(db: Session, prestataire: Prestataire, rdv: RendezVous, motif: str, maintenant: datetime) -> RendezVous:
    """À tout moment, motif obligatoire, envoyé au client (payé par carte : remboursé en entier, services/paiements.py)."""
    motif = (motif or "").strip()
    if not motif:
        raise ErreurRegle("Écrivez le motif : il est envoyé au client (ex. « Malade, désolée »).")
    if rdv.statut not in ACTIFS:
        raise ErreurRegle("Ce rendez-vous n'est plus actif.")
    if rdv.fin <= maintenant:
        raise ErreurRegle("Ce rendez-vous est déjà passé.")
    _changer(rdv, "annule_prestataire", maintenant, motif)
    _journal(db, prestataire.compte_id, "annuler_rendez_vous_prestataire", rdv, maintenant,
             moins_de_24_h=rdv.debut - maintenant < timedelta(hours=24))
    _prevenir(db, rdv, sujet="rafals : rendez-vous annulé par le prestataire",
              client=f"{prestataire.nom_affiche} a annulé « {rdv.titre} », {_texte_moment(rdv.debut)}. Motif : « {motif} ».")
    return rdv


# ---------- Réglages du prestataire ----------


def modifier_reglages(db: Session, prestataire: Prestataire, *, annulation_delai_heures: int, maintenant: datetime) -> Prestataire:
    """Délai d'annulation gratuite : 2, 12, 24 ou 48 h."""
    locaux.verifier_modifiable(prestataire)
    if annulation_delai_heures not in reglages.ANNULATION_DELAI_CHOIX_HEURES:
        raise ErreurRegle("Choisissez le délai d'annulation : 2 h, 12 h, 24 h ou 48 h.")
    avant = {"delai": prestataire.annulation_delai_heures}
    prestataire.annulation_delai_heures = annulation_delai_heures
    journal.noter(db, auteur_id=prestataire.compte_id, action="modifier_reglages_rendez_vous", table_cible="prestataire",
                  ligne_id=prestataire.id, avant=avant, apres={"delai": annulation_delai_heures}, maintenant=maintenant)
    return prestataire


# ---------- Tâche automatique : demandes expirées et rappels ----------


def moment_du_rappel(rdv: RendezVous) -> datetime:
    """La veille à 18 h ; pour un rendez-vous pris après ce moment (ex. le jour même), 2 h avant."""
    veille = datetime.combine(rdv.debut.astimezone(PARIS).date() - timedelta(days=1), time(reglages.RAPPEL_VEILLE_HEURE), tzinfo=PARIS)
    return veille if rdv.cree_le < veille else rdv.debut - reglages.RAPPEL_JOUR_MEME_AVANT


def traiter(db: Session, maintenant: datetime) -> dict[str, int]:
    """Lancé toutes les 5 minutes : demandes sans réponse → expirées ; rappel au prestataire 2 h avant la fin des 24 h ;
    rappel au client et au prestataire la veille d'un rendez-vous confirmé."""
    compte = {"expirees": 0, "rappels": 0}
    for rdv in db.scalars(select(RendezVous).where(RendezVous.statut == "en_attente")).all():
        if rdv.reponse_avant and rdv.reponse_avant <= maintenant:
            _changer(rdv, "expire", maintenant)
            _journal(db, None, "expirer_demande", rdv, maintenant)
            nom = db.get_one(Prestataire, rdv.prestataire_id).nom_affiche
            _prevenir(db, rdv, sujet="rafals : demande sans réponse",
                      client=f"{nom} n'a pas répondu à votre demande « {rdv.titre} », {_texte_moment(rdv.debut)}. "
                             "Elle est annulée : choisissez un autre horaire ou un autre prestataire.")
            compte["expirees"] += 1
        elif rdv.reponse_avant and rdv.rappel_envoye_le is None and maintenant >= rdv.reponse_avant - reglages.DEMANDE_RAPPEL_AVANT_FIN:
            rdv.rappel_envoye_le = maintenant
            _prevenir(db, rdv, sujet="rafals : une demande attend votre réponse",
                      prestataire=f"Plus que 2 h pour accepter ou refuser « {rdv.titre} », {_texte_moment(rdv.debut)}.")
            compte["rappels"] += 1
    a_rappeler = select(RendezVous).where(
        RendezVous.statut == "confirme", RendezVous.rappel_envoye_le.is_(None), RendezVous.debut > maintenant
    )
    for rdv in db.scalars(a_rappeler).all():
        if maintenant >= moment_du_rappel(rdv):
            rdv.rappel_envoye_le = maintenant
            quand = _texte_moment(rdv.debut)
            _prevenir(db, rdv, sujet=f"rafals : rappel, rendez-vous {quand}",
                      client=f"Rappel : « {rdv.titre} », {quand}.", prestataire=f"Rappel : « {rdv.titre} », {quand}.")
            compte["rappels"] += 1
    return compte


# ---------- Ce que chacun voit ----------


def coordonnees_client_visibles(db: Session, prestataire: Prestataire, client_id: int, maintenant: datetime) -> bool:
    """Le prestataire voit le téléphone et l'adresse d'un client tant qu'ils ont un rendez-vous confirmé à venir,
    ou jusqu'à 3 mois après le dernier (RM-CLIENTS). Ex. dernier rendez-vous le 16/10/2026 → visibles jusqu'au 16/01/2027."""
    dernier = db.scalar(
        select(RendezVous.fin).where(RendezVous.prestataire_id == prestataire.id, RendezVous.client_id == client_id,
                                     RendezVous.statut.in_(ACTIFS)).order_by(RendezVous.fin.desc()).limit(1)
    )
    if dernier is None:
        return False
    limite = dernier.astimezone(PARIS)
    mois = limite.month - 1 + reglages.COORDONNEES_CLIENT_VISIBLES
    try:
        limite = limite.replace(year=limite.year + mois // 12, month=mois % 12 + 1)
    except ValueError:  # ex. 30/11 + 3 mois : le 30/02 n'existe pas → le 28/02
        limite = limite.replace(year=limite.year + mois // 12, month=mois % 12 + 1, day=28)
    return maintenant <= limite


def commune_nom(db: Session, rdv: RendezVous) -> str | None:
    return db.get_one(Commune, rdv.commune_id).nom if rdv.commune_id else None
