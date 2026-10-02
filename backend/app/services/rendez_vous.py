"""Rendez-vous : réserver, accepter / refuser / expirer, annuler, déplacer, rappels.
Règles : .doc/regles-metier/RM-RENDEZ-VOUS.md (validé le 30/09/2026). Un rendez-vous n'est jamais effacé.
(Absences et contestations : lot 4.5. Paiement par carte : lot 5.1, services/paiements.py.)"""

from dataclasses import dataclass
from datetime import datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.annonces import Annonce
from app.modeles.comptes import Compte
from app.modeles.paiements import Paiement
from app.modeles.prestataires import Commune, Prestataire
from app.modeles.rendez_vous import RendezVous
from app.services import absences, agenda, annonces, clients, droits, journal, stripe_api
from app.services import rendez_vous_communs as communs
from app.services.erreurs import ErreurRegle

PARIS = reglages.FUSEAU_AFFICHAGE
ACTIFS = communs.ACTIFS
_texte_moment, _journal, _changer, _prevenir = communs.texte_moment, communs.noter, communs.changer, communs.prevenir


# ---------- Réserver ----------


@dataclass
class Demande:
    annonce_id: int
    debut: datetime
    heures: int | None = None
    lieu: str | None = None  # obligatoire si l'annonce a lieu « chez le client ou chez moi »
    mode_paiement: str = "especes"


def _libre(db: Session, prestataire: Prestataire, annonce: Annonce, debut: datetime, heures: int | None, maintenant: datetime,
           ignorer: int | None = None) -> None:
    jour = debut.astimezone(PARIS).date()
    libres = agenda.horaires_libres(db, prestataire, annonce, jour, maintenant, heures, ignorer_rendez_vous_id=ignorer)
    if debut not in libres:
        raise ErreurRegle("Cet horaire vient d'être pris ou n'est plus disponible : choisissez-en un autre.", 409)


def reserver(db: Session, client: Compte, demande: Demande, maintenant: datetime) -> RendezVous:
    """Ex. Mme Dupont réserve « Coupe femme » chez Léa mardi 14/10 à 10 h : confirmé aussitôt (confirmation automatique),
    ou « en attente » 24 h au plus si Léa accepte chaque demande."""
    if not droits.peut_reserver_ou_publier(db, client, maintenant):
        raise ErreurRegle("Vérifiez d'abord votre adresse mail (ou l'accord de vos parents) pour réserver.", 403)
    suspendu = absences.reservation_suspendue_jusqu_au(db, client.id, maintenant)
    if suspendu is not None:
        raise ErreurRegle(f"Vous ne pouvez plus réserver jusqu'au {suspendu.astimezone(PARIS):%d/%m/%Y} : "
                          f"{reglages.ABSENCES_AVANT_SUSPENSION} absences sans prévenir en {reglages.ABSENCES_FENETRE_MOIS} mois.", 403)
    annonce = db.get(Annonce, demande.annonce_id)
    if annonce is None:
        raise ErreurRegle("Cette annonce n'existe pas.", 404)
    # Verrou sur le prestataire : deux clients ne peuvent pas prendre le même horaire en même temps
    prestataire = db.scalar(select(Prestataire).where(Prestataire.id == annonce.prestataire_id).with_for_update())
    assert prestataire is not None
    if prestataire.compte_id == client.id:
        raise ErreurRegle("Vous ne pouvez pas réserver votre propre annonce.")
    if annonces.raison_cachee(db, annonce, prestataire, maintenant) is not None:
        raise ErreurRegle("Cette annonce n'existe pas.", 404)
    if annonce.forme_prix == "devis":
        raise ErreurRegle("Cette annonce est sur devis : écrivez votre demande au prestataire (bientôt disponible).")
    if demande.debut.tzinfo is None:
        demande.debut = demande.debut.replace(tzinfo=PARIS)
    duree = agenda.duree_reservee(annonce, demande.heures)
    heures = demande.heures if annonce.forme_prix == "heure" and demande.heures else annonce.heures_min
    _libre(db, prestataire, annonce, demande.debut, heures if annonce.forme_prix == "heure" else None, maintenant)

    lieu = annonce.lieu if annonce.lieu != "les_deux" else demande.lieu
    if lieu not in ("chez_client", "chez_moi"):
        raise ErreurRegle("Choisissez où a lieu le service : chez vous, ou chez le prestataire.")
    if demande.mode_paiement not in annonces.modes_de_paiement(annonce, prestataire):
        raise ErreurRegle("Ce mode de paiement n'est pas accepté pour cette annonce.")
    if demande.mode_paiement == "carte" and not stripe_api.disponible():
        raise ErreurRegle("Le paiement par carte n'est pas encore ouvert sur rafals : choisissez les espèces.")

    # Adresse recopiée : celle du client (chez lui), ou le local du prestataire
    if lieu == "chez_client":
        adresse = clients.adresse_de(db, client)
        if adresse is None:
            raise ErreurRegle("Indiquez d'abord votre adresse : le prestataire vient chez vous.", 400)
        ligne, complement, commune_id, code_postal = adresse.ligne, adresse.complement, adresse.commune_id, adresse.code_postal
    else:
        local = annonces.local_de(db, prestataire)
        if local is None:
            raise ErreurRegle("Ce prestataire n'a pas encore indiqué l'adresse de son local.")
        ligne, complement, commune_id, code_postal = local.ligne, local.complement, local.commune_id, local.code_postal

    prix = annonce.prix_centimes * (heures or 1) if annonce.forme_prix == "heure" and annonce.prix_centimes else annonce.prix_centimes
    automatique = prestataire.confirmation_automatique
    rdv = RendezVous(
        client_id=client.id, prestataire_id=prestataire.id, annonce_id=annonce.id, commune_id=commune_id,
        debut=demande.debut, fin=demande.debut + duree, titre=annonce.titre, prix_centimes=prix,
        heures=heures if annonce.forme_prix == "heure" else None, lieu=lieu, adresse_ligne=ligne, adresse_complement=complement,
        code_postal=code_postal, mode_paiement=demande.mode_paiement, statut="confirme" if automatique else "en_attente",
        cree_le=maintenant, statut_change_le=maintenant,
        reponse_avant=None if automatique else min(maintenant + reglages.DEMANDE_REPONSE_DELAI, demande.debut),
    )
    db.add(rdv)
    db.flush()
    _journal(db, client.id, "reserver", rdv, maintenant, debut=rdv.debut.isoformat())
    if rdv.mode_paiement != "carte":  # par carte : les mails partent quand Stripe confirme le paiement
        annoncer_reservation(db, rdv, maintenant)
    return rdv


def annoncer_reservation(db: Session, rdv: RendezVous, maintenant: datetime) -> None:
    """Les mails d'une nouvelle réservation : confirmée, ou demande à accepter."""
    quand = _texte_moment(rdv.debut)
    if rdv.statut == "confirme":
        _prevenir(db, rdv, sujet=f"rafals : rendez-vous confirmé, {quand}",
                  client=f"Votre rendez-vous « {rdv.titre} » est confirmé : {quand}.",
                  prestataire=f"Nouveau rendez-vous « {rdv.titre} » : {quand}.")
    else:
        _prevenir(db, rdv, sujet=f"rafals : demande de rendez-vous, {quand}",
                  client=f"Votre demande « {rdv.titre} » pour {quand} attend l'accord du prestataire (24 h au plus).",
                  prestataire=f"Nouvelle demande « {rdv.titre} » pour {quand} : acceptez-la ou refusez-la sur rafals "
                              f"avant {_texte_moment(rdv.reponse_avant or maintenant)}.")


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


def _en_attente(rdv: RendezVous, maintenant: datetime) -> None:
    if rdv.statut != "en_attente":
        raise ErreurRegle("Cette demande n'attend plus de réponse.")
    if rdv.reponse_avant and rdv.reponse_avant <= maintenant:
        raise ErreurRegle("Le délai de 24 h pour répondre est dépassé.")


def accepter(db: Session, prestataire: Prestataire, rdv: RendezVous, maintenant: datetime) -> RendezVous:
    _en_attente(rdv, maintenant)
    _changer(rdv, "confirme", maintenant)
    rdv.rappel_envoye_le = None
    if rdv.remplace_id:  # un déplacement accepté : l'ancien horaire se libère
        _changer(db.get_one(RendezVous, rdv.remplace_id), "deplace", maintenant)
    _journal(db, prestataire.compte_id, "accepter_rendez_vous", rdv, maintenant)
    _prevenir(db, rdv, sujet="rafals : rendez-vous confirmé",
              client=f"Le prestataire a accepté : « {rdv.titre} », {_texte_moment(rdv.debut)}.")
    return rdv


def refuser(db: Session, prestataire: Prestataire, rdv: RendezVous, motif: str | None, maintenant: datetime) -> RendezVous:
    """Motif facultatif. Un déplacement refusé : l'ancien rendez-vous reste confirmé."""
    _en_attente(rdv, maintenant)
    _changer(rdv, "refuse", maintenant, (motif or "").strip() or None)
    _journal(db, prestataire.compte_id, "refuser_rendez_vous", rdv, maintenant)
    raison = f" Motif : « {rdv.motif} »." if rdv.motif else ""
    _prevenir(db, rdv, sujet="rafals : demande de rendez-vous refusée",
              client=f"Le prestataire ne peut pas « {rdv.titre} » {_texte_moment(rdv.debut)}.{raison}")
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


def deplacer(db: Session, client: Compte, rdv: RendezVous, nouveau_debut: datetime, maintenant: datetime) -> RendezVous:
    """Dans le délai d'annulation. Le nouveau rendez-vous garde le prix recopié. Confirmation automatique : fait aussitôt ;
    sinon le nouvel horaire attend l'accord du prestataire et l'ancien reste valable jusque-là."""
    prestataire = _dans_le_delai(db, rdv, maintenant)
    if rdv.statut != "confirme":
        raise ErreurRegle("Seul un rendez-vous confirmé se déplace ; une demande en attente s'annule puis se refait.")
    if pas_encore_paye(db, rdv.id):
        raise ErreurRegle("Terminez d'abord le paiement de ce rendez-vous.")
    if db.scalar(select(RendezVous).where(RendezVous.remplace_id == rdv.id, RendezVous.statut == "en_attente")):
        raise ErreurRegle("Un déplacement de ce rendez-vous attend déjà la réponse du prestataire.")
    if nouveau_debut.tzinfo is None:
        nouveau_debut = nouveau_debut.replace(tzinfo=PARIS)
    annonce = db.get_one(Annonce, rdv.annonce_id)
    _libre(db, prestataire, annonce, nouveau_debut, rdv.heures, maintenant, ignorer=rdv.id)
    automatique = prestataire.confirmation_automatique
    nouveau = RendezVous(
        client_id=rdv.client_id, prestataire_id=rdv.prestataire_id, annonce_id=rdv.annonce_id, commune_id=rdv.commune_id,
        remplace_id=rdv.id, debut=nouveau_debut, fin=nouveau_debut + (rdv.fin - rdv.debut), titre=rdv.titre,
        prix_centimes=rdv.prix_centimes, heures=rdv.heures, lieu=rdv.lieu, adresse_ligne=rdv.adresse_ligne,
        adresse_complement=rdv.adresse_complement, code_postal=rdv.code_postal, mode_paiement=rdv.mode_paiement,
        statut="confirme" if automatique else "en_attente", cree_le=maintenant, statut_change_le=maintenant,
        reponse_avant=None if automatique else min(maintenant + reglages.DEMANDE_REPONSE_DELAI, nouveau_debut),
    )
    db.add(nouveau)
    db.flush()
    if automatique:
        _changer(rdv, "deplace", maintenant)
    _journal(db, client.id, "deplacer_rendez_vous", nouveau, maintenant, remplace_id=rdv.id)
    avant, apres = _texte_moment(rdv.debut), _texte_moment(nouveau_debut)
    _prevenir(db, nouveau, sujet="rafals : rendez-vous déplacé" if automatique else "rafals : demande de déplacement",
              prestataire=f"« {rdv.titre} » : le client demande de passer du {avant} au {apres}."
              + ("" if automatique else " Acceptez ou refusez sur rafals."),
              client=f"« {rdv.titre} » : {'déplacé' if automatique else 'demande envoyée pour passer'} du {avant} au {apres}.")
    return nouveau


# ---------- Réglages du prestataire ----------


def modifier_reglages(
    db: Session, prestataire: Prestataire, *, confirmation_automatique: bool, annulation_delai_heures: int, maintenant: datetime
) -> Prestataire:
    """« Confirmation automatique » ou « j'accepte chaque demande » ; délai d'annulation gratuite : 2, 12, 24 ou 48 h."""
    annonces.verifier_modifiable(prestataire)
    if annulation_delai_heures not in reglages.ANNULATION_DELAI_CHOIX_HEURES:
        raise ErreurRegle("Choisissez le délai d'annulation : 2 h, 12 h, 24 h ou 48 h.")
    avant = {"confirmation_automatique": prestataire.confirmation_automatique, "delai": prestataire.annulation_delai_heures}
    prestataire.confirmation_automatique = confirmation_automatique
    prestataire.annulation_delai_heures = annulation_delai_heures
    journal.noter(db, auteur_id=prestataire.compte_id, action="modifier_reglages_rendez_vous", table_cible="prestataire",
                  ligne_id=prestataire.id, avant=avant,
                  apres={"confirmation_automatique": confirmation_automatique, "delai": annulation_delai_heures},
                  maintenant=maintenant)
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
