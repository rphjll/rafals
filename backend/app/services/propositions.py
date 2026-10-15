"""Répondre à une demande, puis faire une proposition (prix, jour, heure, lieu) que le client accepte, refuse ou négocie.
Une proposition acceptée crée un rendez-vous confirmé, et la demande devient « pourvue ».
Règles : .doc/regles-metier/RM-DEMANDES.md (validé par Raphael le 04/10/2026). Suite du lot 8.3."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.comptes import Compte
from app.modeles.demandes import Demande, Negociation, Proposition, ReponseDemande
from app.modeles.messagerie import Conversation
from app.modeles.metiers import Metier
from app.modeles.prestataires import Commune, Prestataire
from app.modeles.rendez_vous import RendezVous
from app.services import absences, mails, clients, communes, droits, journal, locaux, messagerie, notifications, stripe_api
from app.services import demandes as service_demandes
from app.services import particuliers
from app.services import paiements as service_paiements
from app.services import prestataires as service_prestataires
from app.services import rendez_vous as service_rendez_vous
from app.services import rendez_vous_communs as communs
from app.services.erreurs import ErreurRegle

PARIS = reglages.FUSEAU_AFFICHAGE
LIEUX = ("chez_client", "chez_moi")


def _euros(centimes: int) -> str:
    return service_paiements.euros(centimes)


def _duree(debut: datetime, fin: datetime) -> str:
    """« 1 h », « 45 min », « 1 h 30 »"""
    minutes = int((fin - debut).total_seconds() // 60)
    heures, reste = divmod(minutes, 60)
    return f"{reste} min" if not heures else f"{heures} h" + (f" {reste:02d}" if reste else "")


# ---------- Qui peut répondre ----------


def _prevenir(db: Session, compte_id: int, sujet: str, texte_mail: str, maintenant: datetime) -> None:
    """Un mail court, sans recopier de message ni de coordonnées (RM-ALERTES), et la même phrase en notification sur
    ses appareils (lot 8.7) ; rien pour un compte fermé."""
    compte = db.get_one(Compte, compte_id)
    if compte.ferme_le is None:
        mails.envoyer_mail(compte.email, f"rafals : {sujet}", f"{texte_mail} Pour répondre : rubrique « Messages ».")
        notifications.prevenir(db, compte_id, "rafals", sujet, "/messages", maintenant)


def demande_sur_l_accueil(demande: Demande, maintenant: datetime) -> bool:
    return demande.statut == "ouverte" and demande.cachee_le is None and demande.expire_le > maintenant


SANS_ADRESSE = ("Ajoutez votre adresse dans « Mon profil » : les demandes près de chez vous se calculent depuis elle.")


def commune_de_depart(db: Session, prestataire: Prestataire) -> Commune | None:
    """La ville de l'adresse écrite dans son compte (décision de Raphael du 15/10/2026) : c'est d'elle que se mesure
    « près de chez moi ». Sans adresse : None, il ne voit aucune demande et on lui demande d'en ajouter une."""
    adresse = clients.adresse_de(db, db.get_one(Compte, prestataire.compte_id))
    return db.get_one(Commune, adresse.commune_id) if adresse is not None else None


def peut_repondre(db: Session, prestataire: Prestataire, demande: Demande, maintenant: datetime) -> bool:
    """Prestataire en activité, qui exerce le métier de la demande (principal ou secondaire, pas arrêté) et dont le rayon
    couvre la ville de la demande. Ex. Karim, plombier à Pessac, 15 km → oui pour une fuite à Talence (6 km) ;
    non pour une pelouse (Jardinier), non pour une fuite à Libourne (40 km), non pour sa propre demande."""
    if prestataire.statut != "actif" or prestataire.compte_id == demande.client_id:
        return False
    jour = maintenant.astimezone(PARIS).date()
    if demande.metier_id not in service_prestataires.metiers_exerces(db, prestataire, jour):
        return False
    depart = commune_de_depart(db, prestataire)
    if depart is None or communes.distance_km(depart, db.get_one(Commune, demande.commune_id)) > prestataire.distance_km:
        return False
    # Sans SIRET vérifié : métier autorisé, plafond de l'année pas atteint, adresse et case remplies (RM-PRESTATAIRES)
    return particuliers.raison_de_ne_pas_repondre(db, prestataire, demande.metier_id, maintenant) is None


def concerne(db: Session, prestataire: Prestataire, demande: Demande, maintenant: datetime) -> bool:
    """La demande est dans ses métiers et dans son rayon, sans regarder les limites des particuliers : sert à lui dire
    pourquoi [Répondre] est verrouillé (ex. « Plombier demande un SIRET »)."""
    if prestataire.statut != "actif" or prestataire.compte_id == demande.client_id:
        return False
    if demande.metier_id not in service_prestataires.metiers_exerces(db, prestataire, maintenant.astimezone(PARIS).date()):
        return False
    depart = commune_de_depart(db, prestataire)
    return depart is not None and communes.distance_km(depart, db.get_one(Commune, demande.commune_id)) <= prestataire.distance_km


def raison_verrou(db: Session, prestataire: Prestataire, demande: Demande, maintenant: datetime) -> str | None:
    """Pourquoi [Répondre] est verrouillé : pas d'adresse dans son compte (pour une demande de ses métiers), ou une
    limite des prestataires sans SIRET ; None sinon."""
    exerce = (prestataire.statut == "actif" and prestataire.compte_id != demande.client_id and demande.metier_id in
              service_prestataires.metiers_exerces(db, prestataire, maintenant.astimezone(PARIS).date()))
    if exerce and commune_de_depart(db, prestataire) is None:
        return SANS_ADRESSE
    if not concerne(db, prestataire, demande, maintenant):
        return None
    return particuliers.raison_de_ne_pas_repondre(db, prestataire, demande.metier_id, maintenant)


def nombre_reponses(db: Session, demande_id: int) -> int:
    return db.scalar(select(func.count()).select_from(ReponseDemande).where(ReponseDemande.demande_id == demande_id)) or 0


def reponse_de(db: Session, prestataire: Prestataire, demande_id: int) -> ReponseDemande | None:
    return db.scalar(select(ReponseDemande).where(
        ReponseDemande.demande_id == demande_id, ReponseDemande.prestataire_id == prestataire.id))


def demandes_pour(db: Session, prestataire: Prestataire, maintenant: datetime) -> list[Demande]:
    """« Demandes près de chez moi » : les demandes de l'accueil de ses métiers, dans son rayon. Sans SIRET, celles
    auxquelles il ne peut pas répondre restent montrées, avec la raison sur le bouton verrouillé."""
    return [d for d in service_demandes.ouvertes(db, maintenant) if concerne(db, prestataire, d, maintenant)]


def demandes_de(db: Session, conversation_id: int) -> list[Demande]:
    """Les demandes auxquelles le prestataire a répondu dans cette conversation, la plus récente d'abord."""
    return list(db.scalars(select(Demande).join(ReponseDemande, ReponseDemande.demande_id == Demande.id).where(
        ReponseDemande.conversation_id == conversation_id).order_by(ReponseDemande.cree_le.desc(), Demande.id.desc())))


def repondre(db: Session, prestataire: Prestataire, demande_id: int, maintenant: datetime) -> Conversation:
    """[Répondre] : ouvre la conversation avec le client, la demande rappelée en haut. Une seule réponse par prestataire
    (un 2e clic rouvre la même conversation) ; 10 réponses au plus par demande."""
    demande = db.scalar(select(Demande).where(Demande.id == demande_id).with_for_update())
    if demande is None or not demande_sur_l_accueil(demande, maintenant):
        raise ErreurRegle("Cette demande n'est plus ouverte.", 404)
    deja = reponse_de(db, prestataire, demande.id)
    if deja is not None:
        return db.get_one(Conversation, deja.conversation_id)
    if prestataire.compte_id == demande.client_id:
        raise ErreurRegle("Vous ne pouvez pas répondre à votre propre demande.")
    if commune_de_depart(db, prestataire) is None:
        raise ErreurRegle(SANS_ADRESSE, 403)
    if concerne(db, prestataire, demande, maintenant):
        particuliers.verifier_reponse(db, prestataire, demande.metier_id, maintenant)
    if not peut_repondre(db, prestataire, demande, maintenant):
        raise ErreurRegle("Vous ne pouvez pas répondre à cette demande : elle n'est pas dans vos métiers, ou trop loin de chez vous.", 403)
    maxi = reglages.DEMANDE_REPONSES_MAX
    if nombre_reponses(db, demande.id) >= maxi:
        raise ErreurRegle(f"Cette demande est complète : {maxi} prestataires ont déjà répondu.")
    conversation = messagerie.creer(db, demande.client_id, prestataire, maintenant)
    if conversation.bloquee_le is not None:
        raise ErreurRegle("Votre conversation avec ce client est bloquée : vous ne pouvez pas lui répondre.")
    db.add(ReponseDemande(demande_id=demande.id, prestataire_id=prestataire.id, conversation_id=conversation.id, cree_le=maintenant))
    messagerie.informer(db, conversation, prestataire.compte_id,
                        f"{prestataire.nom_affiche} a répondu à la demande « {demande.titre} ».", maintenant)
    _prevenir(db, demande.client_id, f"{prestataire.nom_affiche} a répondu à votre demande",
              f"{prestataire.nom_affiche} a répondu à votre demande « {demande.titre} ».", maintenant)
    journal.noter(db, auteur_id=prestataire.compte_id, action="repondre_demande", table_cible="demande", ligne_id=demande.id,
                  apres={"prestataire_id": prestataire.id}, maintenant=maintenant)
    db.flush()
    return conversation


# ---------- Faire une proposition ----------


@dataclass
class Saisie:
    """Ex. Karim : 6000 · lundi 12/10/2026 à 8 h 30 · 60 minutes · carte ou espèces, pour la demande n° 1."""

    prix_centimes: int
    debut: datetime
    duree_minutes: int
    demande_id: int | None = None
    metier_id: int | None = None  # sans demande : un de ses métiers
    lieu: str | None = None  # sans demande : chez le client, ou chez lui
    paiement_carte: bool = False
    paiement_especes: bool = True


def _carte_possible(prestataire: Prestataire) -> bool:
    return prestataire.siret_statut == "verifie" and prestataire.stripe_pret and stripe_api.disponible()


def _verifier_libre(db: Session, prestataire: Prestataire, debut: datetime, fin: datetime) -> None:
    """Une proposition est refusée si elle tombe sur un autre de ses rendez-vous (même hors de sa semaine type : c'est
    lui qui choisit l'heure)."""
    pris = db.scalar(select(RendezVous.id).where(
        RendezVous.prestataire_id == prestataire.id, RendezVous.statut.in_(communs.ACTIFS),
        RendezVous.debut < fin, RendezVous.fin > debut,
    ).limit(1))
    if pris is not None:
        raise ErreurRegle("Vous avez déjà un rendez-vous à cette heure-là : proposez une autre heure.", 409)


def _conversation_du_prestataire(db: Session, prestataire: Prestataire, conversation_id: int) -> Conversation:
    conversation = db.get(Conversation, conversation_id)
    if conversation is None or conversation.prestataire_id != prestataire.id:
        raise ErreurRegle("Cette conversation n'existe pas.", 404)
    return conversation


def en_attente_de(db: Session, conversation_id: int, demande_id: int | None) -> Proposition | None:
    meme_demande = Proposition.demande_id.is_(None) if demande_id is None else Proposition.demande_id == demande_id
    return db.scalar(select(Proposition).where(
        Proposition.conversation_id == conversation_id, meme_demande, Proposition.statut == "en_attente"))


def negociation_en_attente(db: Session, proposition_id: int) -> Negociation | None:
    return db.scalar(select(Negociation).where(Negociation.proposition_id == proposition_id, Negociation.statut == "en_attente"))


def _clore_negociation(db: Session, proposition: Proposition, maintenant: datetime) -> None:
    negociation = negociation_en_attente(db, proposition.id)
    if negociation is not None:
        negociation.statut, negociation.repondu_le = "refusee", maintenant


def _changer(proposition: Proposition, statut: str, maintenant: datetime) -> None:
    proposition.statut, proposition.statut_change_le = statut, maintenant


def texte(db: Session, proposition: Proposition, pour_le_client: bool = True) -> str:
    """« 60 € · lundi 12/10/2026 à 8 h 30 · 1 h · chez vous · carte ou espèces »"""
    if proposition.lieu == "chez_client":
        lieu = "chez vous" if pour_le_client else "chez le client"
    else:
        lieu = "chez le prestataire" if pour_le_client else "chez vous"
    modes = [mode for mode, oui in (("carte", proposition.paiement_carte), ("espèces", proposition.paiement_especes)) if oui]
    return " · ".join([_euros(proposition.prix_centimes), communs.texte_moment(proposition.debut),
                       _duree(proposition.debut, proposition.fin), lieu, " ou ".join(modes)])


def proposer(db: Session, prestataire: Prestataire, conversation_id: int, saisie: Saisie, maintenant: datetime) -> Proposition:
    """Le prestataire propose un prix, un jour et une heure dans la conversation. Une nouvelle proposition remplace
    celle qui attendait encore (pour la même demande)."""
    conversation = _conversation_du_prestataire(db, prestataire, conversation_id)
    if prestataire.statut != "actif":
        raise ErreurRegle("Votre activité est en pause ou arrêtée : reprenez-la pour faire une proposition.")
    if conversation.bloquee_le is not None:
        raise ErreurRegle("Cette conversation est bloquée : plus aucune proposition ne passe.")
    client = db.get_one(Compte, conversation.client_id)
    if client.ferme_le is not None:
        raise ErreurRegle("Cette personne a quitté rafals.")

    jour = maintenant.astimezone(PARIS).date()
    if saisie.demande_id is not None:
        demande = db.get(Demande, saisie.demande_id)
        if demande is None or demande.client_id != conversation.client_id or not demande_sur_l_accueil(demande, maintenant):
            raise ErreurRegle("Cette demande n'est plus ouverte.")
        if reponse_de(db, prestataire, demande.id) is None:
            raise ErreurRegle("Cliquez d'abord [Répondre] sur cette demande.", 403)
        metier_id = demande.metier_id
        lieu = "chez_client" if demande.lieu == "chez_moi" else "chez_moi"
    else:
        if saisie.metier_id not in service_prestataires.metiers_exerces(db, prestataire, jour):
            raise ErreurRegle("Choisissez un de vos métiers pour cette proposition.")
        metier_id = saisie.metier_id
        lieu = saisie.lieu or ""
        if lieu not in LIEUX:
            raise ErreurRegle("Indiquez où a lieu le service : chez le client, ou chez vous.")
    if lieu == "chez_moi" and locaux.local_de(db, prestataire) is None:
        raise ErreurRegle("Indiquez d'abord votre adresse dans « Mon profil » : le client vient chez vous.")

    if saisie.prix_centimes <= 0:
        raise ErreurRegle("Indiquez un prix (ex. 60 €).")
    particuliers.verifier_proposition(db, prestataire, metier_id, saisie.prix_centimes, maintenant)
    debut = saisie.debut if saisie.debut.tzinfo is not None else saisie.debut.replace(tzinfo=PARIS)
    if debut <= maintenant:
        raise ErreurRegle("Proposez un jour et une heure à venir.")
    mini, maxi = reglages.PROPOSITION_DUREE_MINUTES
    if not mini <= saisie.duree_minutes <= maxi:
        raise ErreurRegle(f"La durée doit faire entre {mini} minutes et {maxi // 60} heures.")
    fin = debut + timedelta(minutes=saisie.duree_minutes)
    if not (saisie.paiement_carte or saisie.paiement_especes):
        raise ErreurRegle("Choisissez au moins un moyen de paiement.")
    if saisie.paiement_carte and not _carte_possible(prestataire):
        raise ErreurRegle("Le paiement par carte demande un SIRET vérifié et le paiement par carte activé : sans eux, espèces seulement.")
    _verifier_libre(db, prestataire, debut, fin)

    ancienne = en_attente_de(db, conversation.id, saisie.demande_id)
    if ancienne is not None:
        _changer(ancienne, "remplacee", maintenant)
        _clore_negociation(db, ancienne, maintenant)
    proposition = Proposition(
        conversation_id=conversation.id, demande_id=saisie.demande_id, metier_id=metier_id,
        remplace_id=ancienne.id if ancienne is not None else None, prix_centimes=saisie.prix_centimes, debut=debut, fin=fin,
        lieu=lieu, paiement_carte=saisie.paiement_carte, paiement_especes=saisie.paiement_especes, statut="en_attente",
        statut_change_le=maintenant, cree_le=maintenant,
    )
    db.add(proposition)
    db.flush()
    messagerie.informer(db, conversation, prestataire.compte_id,
                        f"{prestataire.nom_affiche} propose : {texte(db, proposition)}.", maintenant)
    _prevenir(db, conversation.client_id, f"{prestataire.nom_affiche} vous fait une proposition",
              f"{prestataire.nom_affiche} vous propose {_euros(proposition.prix_centimes)}, {communs.texte_moment(debut)}.", maintenant)
    journal.noter(db, auteur_id=prestataire.compte_id, action="proposer", table_cible="proposition", ligne_id=proposition.id,
                  apres={"prix_centimes": proposition.prix_centimes, "debut": debut.isoformat()}, maintenant=maintenant)
    return proposition


def _proposition(db: Session, proposition_id: int) -> tuple[Proposition, Conversation]:
    proposition = db.get(Proposition, proposition_id)
    if proposition is None:
        raise ErreurRegle("Cette proposition n'existe pas.", 404)
    return proposition, db.get_one(Conversation, proposition.conversation_id)


def proposition_du_prestataire(db: Session, prestataire: Prestataire, proposition_id: int) -> tuple[Proposition, Conversation]:
    proposition, conversation = _proposition(db, proposition_id)
    if conversation.prestataire_id != prestataire.id:
        raise ErreurRegle("Cette proposition n'existe pas.", 404)
    return proposition, conversation


def proposition_du_client(db: Session, client: Compte, proposition_id: int) -> tuple[Proposition, Conversation]:
    proposition, conversation = _proposition(db, proposition_id)
    if conversation.client_id != client.id:
        raise ErreurRegle("Cette proposition n'existe pas.", 404)
    return proposition, conversation


def _verifier_en_attente(proposition: Proposition, maintenant: datetime) -> None:
    if proposition.statut != "en_attente" or proposition.debut <= maintenant:
        raise ErreurRegle("Cette proposition n'attend plus de réponse.")


def propositions_de(db: Session, conversation_id: int) -> list[Proposition]:
    return list(db.scalars(select(Proposition).where(Proposition.conversation_id == conversation_id)
                           .order_by(Proposition.cree_le, Proposition.id)))


def retirer(db: Session, prestataire: Prestataire, proposition_id: int, maintenant: datetime) -> Proposition:
    proposition, conversation = proposition_du_prestataire(db, prestataire, proposition_id)
    _verifier_en_attente(proposition, maintenant)
    _changer(proposition, "retiree", maintenant)
    _clore_negociation(db, proposition, maintenant)
    messagerie.informer(db, conversation, prestataire.compte_id,
                        f"{prestataire.nom_affiche} a retiré sa proposition de {_euros(proposition.prix_centimes)}.", maintenant)
    return proposition


# ---------- Le client répond : refuser, négocier, accepter ----------


def refuser(db: Session, client: Compte, proposition_id: int, maintenant: datetime) -> Proposition:
    """Sans raison à donner ; la conversation reste ouverte et le prestataire peut en faire une autre."""
    proposition, conversation = proposition_du_client(db, client, proposition_id)
    _verifier_en_attente(proposition, maintenant)
    _changer(proposition, "refusee", maintenant)
    _clore_negociation(db, proposition, maintenant)
    messagerie.informer(db, conversation, client.id,
                        f"{messagerie.nom_du_client(client)} a refusé la proposition de {_euros(proposition.prix_centimes)}.", maintenant)
    # Pas de mail pour un refus (RM-ALERTES), seulement la notification
    notifications.prevenir(db, db.get_one(Prestataire, conversation.prestataire_id).compte_id, "rafals",
                           f"{messagerie.nom_du_client(client)} a refusé votre proposition", f"/messages/{conversation.id}", maintenant)
    return proposition


def negocier(db: Session, client: Compte, proposition_id: int, prix_centimes: int, maintenant: datetime) -> Negociation:
    """[Négocier le prix] : un prix plus bas ; le jour, l'heure, la durée et le lieu ne changent pas.
    Une seule négociation à la fois par proposition."""
    proposition, conversation = proposition_du_client(db, client, proposition_id)
    _verifier_en_attente(proposition, maintenant)
    if negociation_en_attente(db, proposition.id) is not None:
        raise ErreurRegle("Vous avez déjà proposé un prix : attendez la réponse du prestataire.")
    if not 0 < prix_centimes < proposition.prix_centimes:
        raise ErreurRegle(f"Proposez un prix plus bas que {_euros(proposition.prix_centimes)}.")
    negociation = Negociation(proposition_id=proposition.id, prix_centimes=prix_centimes, statut="en_attente", cree_le=maintenant)
    db.add(negociation)
    db.flush()
    messagerie.informer(db, conversation, client.id,
                        f"Prix proposé par {messagerie.nom_du_client(client)} : {_euros(prix_centimes)} au lieu de "
                        f"{_euros(proposition.prix_centimes)}.", maintenant)
    prestataire = db.get_one(Prestataire, conversation.prestataire_id)
    _prevenir(db, prestataire.compte_id, f"{messagerie.nom_du_client(client)} vous propose un autre prix",
              f"{messagerie.nom_du_client(client)} propose {_euros(prix_centimes)} au lieu de {_euros(proposition.prix_centimes)}.", maintenant)
    return negociation


def repondre_au_prix(db: Session, prestataire: Prestataire, negociation_id: int, accepte: bool, maintenant: datetime) -> Proposition:
    """Il accepte : sa proposition est remplacée par la même au nouveau prix (le client n'a plus qu'à l'accepter).
    Il refuse : sa proposition de départ attend de nouveau. Rend la proposition qui attend maintenant."""
    negociation = db.get(Negociation, negociation_id)
    if negociation is None:
        raise ErreurRegle("Cette négociation n'existe pas.", 404)
    proposition, conversation = proposition_du_prestataire(db, prestataire, negociation.proposition_id)
    if negociation.statut != "en_attente":
        raise ErreurRegle("Vous avez déjà répondu à ce prix.")
    _verifier_en_attente(proposition, maintenant)
    negociation.repondu_le = maintenant
    if not accepte:
        negociation.statut = "refusee"
        messagerie.informer(db, conversation, prestataire.compte_id,
                            f"{prestataire.nom_affiche} garde son prix de {_euros(proposition.prix_centimes)}.", maintenant)
        _prevenir(db, conversation.client_id, f"{prestataire.nom_affiche} garde son prix",
                  f"{prestataire.nom_affiche} garde son prix de {_euros(proposition.prix_centimes)}.", maintenant)
        return proposition
    negociation.statut = "acceptee"
    _changer(proposition, "remplacee", maintenant)
    nouvelle = Proposition(
        conversation_id=proposition.conversation_id, demande_id=proposition.demande_id, metier_id=proposition.metier_id,
        remplace_id=proposition.id, prix_centimes=negociation.prix_centimes, debut=proposition.debut, fin=proposition.fin,
        lieu=proposition.lieu, paiement_carte=proposition.paiement_carte, paiement_especes=proposition.paiement_especes,
        statut="en_attente", statut_change_le=maintenant, cree_le=maintenant,
    )
    db.add(nouvelle)
    db.flush()
    messagerie.informer(db, conversation, prestataire.compte_id,
                        f"{prestataire.nom_affiche} accepte {_euros(nouvelle.prix_centimes)} : {texte(db, nouvelle)}.", maintenant)
    _prevenir(db, conversation.client_id, f"{prestataire.nom_affiche} accepte votre prix",
              f"{prestataire.nom_affiche} accepte {_euros(nouvelle.prix_centimes)} : il ne vous reste qu'à confirmer.", maintenant)
    return nouvelle


def modes_de_paiement(proposition: Proposition, prestataire: Prestataire) -> list[str]:
    """La carte seulement si elle est toujours possible au moment d'accepter ; sinon espèces."""
    carte = proposition.paiement_carte and _carte_possible(prestataire)
    especes = proposition.paiement_especes or (proposition.paiement_carte and not carte)
    return [mode for mode, oui in (("carte", carte), ("especes", especes)) if oui]


def accepter(db: Session, client: Compte, proposition_id: int, mode_paiement: str, maintenant: datetime) -> RendezVous:
    """[Accepter 35 € · samedi à 10 h 00] : un rendez-vous confirmé est créé, la demande devient « pourvue », les autres
    prestataires lisent « Marie D. a choisi un autre prestataire ». Par carte : le paiement se fait juste après
    (30 minutes), comme pour une réservation."""
    proposition, conversation = proposition_du_client(db, client, proposition_id)
    _verifier_en_attente(proposition, maintenant)
    if not droits.peut_reserver_ou_publier(db, client, maintenant):
        raise ErreurRegle("Vérifiez d'abord votre adresse mail (ou l'accord de vos parents) pour réserver.", 403)
    suspendu = absences.reservation_suspendue_jusqu_au(db, client.id, maintenant)
    if suspendu is not None:
        raise ErreurRegle(f"Vous ne pouvez plus réserver jusqu'au {suspendu.astimezone(PARIS):%d/%m/%Y} : "
                          f"{reglages.ABSENCES_AVANT_SUSPENSION} absences sans prévenir en {reglages.ABSENCES_FENETRE_MOIS} mois.", 403)
    # Verrou sur le prestataire : deux clients ne peuvent pas prendre la même heure en même temps
    prestataire = db.scalar(select(Prestataire).where(Prestataire.id == conversation.prestataire_id).with_for_update())
    assert prestataire is not None
    if prestataire.statut != "actif":
        raise ErreurRegle("Ce prestataire n'est pas disponible en ce moment.")
    _verifier_libre(db, prestataire, proposition.debut, proposition.fin)
    particuliers.verifier_acceptation(db, prestataire, proposition, maintenant)
    if mode_paiement not in modes_de_paiement(proposition, prestataire):
        raise ErreurRegle("Ce mode de paiement n'est pas accepté pour cette proposition.")

    demande = db.get(Demande, proposition.demande_id) if proposition.demande_id is not None else None
    if demande is not None and demande.statut != "ouverte":
        raise ErreurRegle("Cette demande n'est plus ouverte.")
    # Adresse recopiée : celle de la demande (ou du compte du client), ou le local du prestataire
    if proposition.lieu == "chez_client":
        if demande is not None and demande.adresse_ligne:
            ligne, complement, commune_id, code_postal = (demande.adresse_ligne, demande.adresse_complement,
                                                          demande.commune_id, demande.code_postal)
        else:
            adresse = clients.adresse_de(db, client)
            if adresse is None:
                raise ErreurRegle("Indiquez d'abord votre adresse dans « Mon profil » : le prestataire vient chez vous.")
            ligne, complement, commune_id, code_postal = adresse.ligne, adresse.complement, adresse.commune_id, adresse.code_postal
    else:
        local = locaux.local_de(db, prestataire)
        if local is None:
            raise ErreurRegle("Ce prestataire n'a pas encore indiqué l'adresse de son local.")
        ligne, complement, commune_id, code_postal = local.ligne, local.complement, local.commune_id, local.code_postal

    titre = demande.titre if demande is not None else db.get_one(Metier, proposition.metier_id).nom
    rdv = RendezVous(
        client_id=client.id, prestataire_id=prestataire.id, annonce_id=None, proposition_id=proposition.id,
        metier_id=proposition.metier_id, commune_id=commune_id, debut=proposition.debut, fin=proposition.fin, titre=titre,
        prix_centimes=proposition.prix_centimes, heures=None, lieu=proposition.lieu, adresse_ligne=ligne,
        adresse_complement=complement, code_postal=code_postal, mode_paiement=mode_paiement, statut="confirme",
        cree_le=maintenant, statut_change_le=maintenant,
    )
    db.add(rdv)
    _changer(proposition, "acceptee", maintenant)
    db.flush()
    nom_client = messagerie.nom_du_client(client)
    messagerie.informer(db, conversation, client.id,
                        f"{nom_client} a accepté : rendez-vous « {titre} », {communs.texte_moment(rdv.debut)}, "
                        f"{_euros(proposition.prix_centimes)}.", maintenant)
    notifications.prevenir(db, db.get_one(Prestataire, conversation.prestataire_id).compte_id, "rafals",
                           f"{nom_client} a accepté votre proposition : rendez-vous {communs.texte_moment(rdv.debut)}",
                           f"/messages/{conversation.id}", maintenant)
    if demande is not None:
        demande.statut, demande.statut_change_le = "pourvue", maintenant
        autres = db.scalars(select(Proposition).where(
            Proposition.demande_id == demande.id, Proposition.statut == "en_attente", Proposition.id != proposition.id)).all()
        for autre in autres:
            _changer(autre, "non_retenue", maintenant)
            _clore_negociation(db, autre, maintenant)
        # Tous ceux qui avaient répondu sont prévenus dans leur conversation
        for reponse in db.scalars(select(ReponseDemande).where(ReponseDemande.demande_id == demande.id,
                                                               ReponseDemande.conversation_id != conversation.id)):
            messagerie.informer(db, db.get_one(Conversation, reponse.conversation_id), client.id,
                                f"{nom_client} a choisi un autre prestataire pour « {demande.titre} ».", maintenant)
    communs.noter(db, client.id, "accepter_proposition", rdv, maintenant, proposition_id=proposition.id)
    if rdv.mode_paiement != "carte":  # par carte : les mails partent quand Stripe confirme le paiement
        service_rendez_vous.annoncer_reservation(db, rdv, maintenant)
    return rdv


# ---------- Rouvrir une demande, tâche de fond ----------


def rouvrir(db: Session, client: Compte, demande: Demande, maintenant: datetime) -> Demande:
    """Rendez-vous annulé avant d'avoir lieu : le client peut rouvrir sa demande, qui repart pour 30 jours."""
    if demande.statut != "pourvue":
        raise ErreurRegle("Seule une demande pourvue dont le rendez-vous a été annulé se rouvre.")
    rdv = db.scalar(select(RendezVous).join(Proposition, Proposition.id == RendezVous.proposition_id).where(
        Proposition.demande_id == demande.id).order_by(RendezVous.id.desc()))
    if rdv is not None and rdv.statut in communs.ACTIFS:
        raise ErreurRegle("Le rendez-vous de cette demande est toujours prévu : annulez-le d'abord.")
    if rdv is not None and rdv.statut not in ("annule_client", "annule_prestataire"):
        raise ErreurRegle("Seule une demande dont le rendez-vous a été annulé se rouvre.")
    fin = service_demandes.fin_le(demande.jour, maintenant)
    if fin <= maintenant:
        raise ErreurRegle("Le jour voulu est passé : publiez une nouvelle demande avec un autre jour.")
    service_demandes.verifier_place(db, client)
    demande.statut, demande.statut_change_le, demande.expire_le = "ouverte", maintenant, fin
    demande.rappel_envoye_le = None
    journal.noter(db, auteur_id=client.id, action="rouvrir_demande", table_cible="demande", ligne_id=demande.id, maintenant=maintenant)
    db.flush()
    return demande


def expirer(db: Session, maintenant: datetime) -> int:
    """Une proposition non acceptée expire au début de l'heure proposée."""
    passees = db.scalars(select(Proposition).where(Proposition.statut == "en_attente", Proposition.debut <= maintenant)).all()
    for proposition in passees:
        _changer(proposition, "expiree", maintenant)
        _clore_negociation(db, proposition, maintenant)
    db.flush()
    return len(passees)


def traiter(db: Session, maintenant: datetime) -> tuple[int, int, int, int]:
    """La tâche de fond : (demandes expirées, rappels envoyés, propositions expirées, propositions retirées parce qu'un
    prestataire sans SIRET a atteint 1 000 € sur 12 mois)."""
    return (*service_demandes.traiter(db, maintenant), expirer(db, maintenant), particuliers.retirer_au_plafond(db, maintenant))
