"""Paiement par carte d'un rendez-vous, et des arrhes et du solde d'un devis (Stripe Connect).
Règles : RM-PAIEMENTS.md (validé par Raphael le 02/10/2026), RM-DEVIS.md.

Le chemin de l'argent : le client paie en réservant → l'argent est bloqué sur le compte Stripe du prestataire →
48 h après la fin du rendez-vous, rafals le fait partir vers sa banque (« versé »). Un remboursement prend l'argent
encore bloqué : rafals n'avance jamais d'argent. rafals garde 5 % ; rien sur les espèces.

Une seule tâche de fond (toutes les 5 minutes) regarde chaque paiement en cours et fait ce que l'état du rendez-vous
demande : rembourser (refusé, expiré, annulé, absence), verser, ou abandonner un paiement jamais terminé. Ainsi,
aucune action (annuler, refuser, bloquer un jour…) n'a besoin de connaître Stripe, et une panne de Stripe est
simplement réessayée au passage suivant.

Devis (lot 5.3) : les arrhes partent vers le prestataire sans attendre (pour ses matériaux), le solde aussi (le client
l'a payé après avoir vérifié le travail) ; si le prestataire annule un devis accepté, les arrhes sont rendues."""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Select, or_, select
from sqlalchemy.orm import Session

from app import config, reglages
from app.modeles.comptes import Compte
from app.modeles.devis import DemandeDevis, Devis
from app.modeles.metiers import Metier
from app.modeles.paiements import Paiement
from app.modeles.prestataires import Prestataire
from app.modeles.rendez_vous import RendezVous
from app.services import absences, journal, mails, stripe_api
from app.services import rendez_vous_communs as communs
from app.services.erreurs import ErreurRegle
from app.services.stripe_api import StripeIndisponible

journal_serveur = logging.getLogger("rafals")

EN_COURS = ("a_payer", "paye")  # paiements que la tâche de fond suit encore
CACHES_AU_PRESTATAIRE = ("a_payer", "abandonne")  # réservation pas encore payée (ou jamais) : le prestataire ne la voit pas
PAGE_PROFIL = "/profil"
PAGE_RENDEZ_VOUS = "/rendez-vous"
PAGE_DEVIS = "/devis"


def commission(montant_centimes: int) -> int:
    """5 %, arrondis au centime. Ex. 50,00 € → 2,50 € ; 120,00 € → 6,00 € ; 33,33 € → 1,67 €."""
    return (montant_centimes * reglages.COMMISSION_POURCENT + 50) // 100


def euros(centimes: int) -> str:
    """« 46,50 € »"""
    return f"{centimes // 100},{centimes % 100:02d} €"


def du_rendez_vous(db: Session, rdv_id: int) -> Paiement | None:
    return db.scalar(select(Paiement).where(Paiement.rendez_vous_id == rdv_id))


def du_devis(db: Session, devis_id: int, sorte: str) -> Paiement | None:
    return db.scalar(select(Paiement).where(Paiement.devis_id == devis_id, Paiement.sorte == sorte))


def net(paiement: Paiement) -> int:
    """Ce que reçoit le prestataire : le prix, moins les 5 % de rafals, moins les frais de Stripe."""
    return paiement.montant_centimes - paiement.commission_centimes - (paiement.frais_stripe_centimes or 0)


def numero_devis(devis: Devis) -> str:
    """« D-2026-0002 »"""
    return f"D-{devis.annee}-{devis.numero:04d}"


@dataclass
class Sujet:
    """Ce que paie un paiement : un rendez-vous, ou les arrhes / le solde d'un devis. Ex. « Coupe femme »,
    « mardi 13/10/2026 à 10 h 00 » ; « Muret de jardin », « devis D-2026-0002 (arrhes) »."""

    prestataire: Prestataire
    client_id: int
    titre: str
    quand: str
    rdv: RendezVous | None = None
    devis: Devis | None = None


def sujet(db: Session, paiement: Paiement) -> Sujet:
    if paiement.rendez_vous_id is not None:
        rdv = db.get_one(RendezVous, paiement.rendez_vous_id)
        return Sujet(db.get_one(Prestataire, rdv.prestataire_id), rdv.client_id, rdv.titre, communs.texte_moment(rdv.debut),
                     rdv=rdv)
    devis = db.get_one(Devis, paiement.devis_id)
    demande = db.get_one(DemandeDevis, devis.demande_devis_id)
    quoi = "arrhes" if paiement.sorte == "arrhes" else "solde"
    return Sujet(db.get_one(Prestataire, demande.prestataire_id), demande.client_id,
                 db.get_one(Metier, demande.metier_id).nom, f"devis {numero_devis(devis)} ({quoi})", devis=devis)


def _prevenir(db: Session, s: Sujet, *, objet: str, client: str | None = None, prestataire: str | None = None) -> None:
    if client:
        mails.envoyer_mail(db.get_one(Compte, s.client_id).email, objet, client)
    if prestataire:
        mails.envoyer_mail(db.get_one(Compte, s.prestataire.compte_id).email, objet, prestataire)


def _avec_leur_sujet() -> Select[tuple[Paiement]]:
    """Les paiements avec leur rendez-vous ou leur demande de devis, pour les filtrer par client ou par prestataire."""
    return (select(Paiement).outerjoin(RendezVous, RendezVous.id == Paiement.rendez_vous_id)
            .outerjoin(Devis, Devis.id == Paiement.devis_id).outerjoin(DemandeDevis, DemandeDevis.id == Devis.demande_devis_id))


def du_prestataire(db: Session, prestataire_id: int, statuts: tuple[str, ...] | None = None) -> list[Paiement]:
    requete = _avec_leur_sujet().where(or_(RendezVous.prestataire_id == prestataire_id,
                                           DemandeDevis.prestataire_id == prestataire_id))
    if statuts:
        requete = requete.where(Paiement.statut.in_(statuts))
    return list(db.scalars(requete.order_by(Paiement.id.desc())))


def du_client(db: Session, client_id: int) -> list[Paiement]:
    requete = _avec_leur_sujet().where(or_(RendezVous.client_id == client_id, DemandeDevis.client_id == client_id))
    return list(db.scalars(requete.order_by(Paiement.id.desc())))


def _stripe(appel: Any) -> Any:
    """Une panne de Stripe pendant une action de l'utilisateur : message clair, rien n'est enregistré."""
    try:
        return appel()
    except StripeIndisponible as erreur:
        journal_serveur.warning("Stripe : %s", erreur)
        raise ErreurRegle("Le service de paiement ne répond pas : réessayez dans quelques minutes.", 503) from erreur


# ---------- Le prestataire active le paiement par carte ----------


def activer(db: Session, prestataire: Prestataire, compte: Compte, mandat: bool, maintenant: datetime) -> str:
    """Crée son compte Stripe (la première fois) et renvoie l'adresse de la page de Stripe où il donne son identité et
    son RIB. Il faut un SIRET vérifié, et son accord pour que rafals fasse ses factures (mandat de facturation)."""
    if not stripe_api.disponible():
        raise ErreurRegle("Le paiement par carte n'est pas encore ouvert sur rafals.")
    if prestataire.siret_statut != "verifie":
        raise ErreurRegle("Le paiement par carte demande un SIRET vérifié.")
    if prestataire.mandat_facturation_le is None:
        if not mandat:
            raise ErreurRegle("Cochez la case : vous acceptez que rafals fasse vos factures à votre place.")
        prestataire.mandat_facturation_le = maintenant
        journal.noter(db, auteur_id=compte.id, action="accepter_mandat_facturation", table_cible="prestataire",
                      ligne_id=prestataire.id, apres={"mandat_facturation_le": maintenant.isoformat()}, maintenant=maintenant)
    if prestataire.stripe_compte is None:
        cree = _stripe(lambda: stripe_api.appeler("POST", "/v1/accounts", {
            "country": "FR", "email": compte.email,
            # « Stripe gère la tarification » : le prestataire paie les frais de Stripe, Stripe vérifie son identité
            "controller": {"fees": {"payer": "account"}, "losses": {"payments": "stripe"},
                           "stripe_dashboard": {"type": "full"}, "requirement_collection": "stripe"},
            "capabilities": {"card_payments": {"requested": True}, "transfers": {"requested": True}},
            # rafals décide quand l'argent part vers la banque du prestataire (48 h après le rendez-vous)
            "settings": {"payouts": {"schedule": {"interval": "manual"}}},
            "metadata": {"prestataire_id": prestataire.id},
        }, cle_unique=f"compte-prestataire-{prestataire.id}"))
        prestataire.stripe_compte = cree["id"]
        journal.noter(db, auteur_id=compte.id, action="creer_compte_stripe", table_cible="prestataire", ligne_id=prestataire.id,
                      apres={"stripe_compte": cree["id"]}, maintenant=maintenant)
    retour = f"{config.ADRESSE_SITE}{PAGE_PROFIL}?stripe="
    lien = _stripe(lambda: stripe_api.appeler("POST", "/v1/account_links", {
        "account": prestataire.stripe_compte, "type": "account_onboarding",
        "refresh_url": f"{retour}recommencer", "return_url": f"{retour}retour",
    }))
    return lien["url"]


def actualiser(db: Session, prestataire: Prestataire) -> Prestataire:
    """Demande à Stripe si le prestataire peut être payé (identité vérifiée, RIB donné). Stripe le dit aussi tout seul
    (message « account.updated ») ; ceci sert quand il revient de la page de Stripe."""
    if prestataire.stripe_compte and stripe_api.disponible():
        try:
            infos = stripe_api.appeler("GET", f"/v1/accounts/{prestataire.stripe_compte}")
            prestataire.stripe_pret = bool(infos.get("charges_enabled") and infos.get("payouts_enabled"))
        except StripeIndisponible as erreur:
            journal_serveur.warning("Stripe : %s", erreur)
    return prestataire


# ---------- Le client paie ----------


def commencer(db: Session, rdv: RendezVous, client: Compte, maintenant: datetime) -> str:
    """Après la réservation : le paiement « à payer » et l'adresse de la page de paiement de Stripe.
    Ex. coupe à 50 € → Stripe prend 50 € sur la carte de Paul, dont 2,50 € pour rafals."""
    prestataire = db.get_one(Prestataire, rdv.prestataire_id)
    if not prestataire.stripe_compte or rdv.prix_centimes is None:
        raise ErreurRegle("Ce mode de paiement n'est pas accepté pour ce rendez-vous.")
    paiement = Paiement(rendez_vous_id=rdv.id, sorte="rendez_vous", montant_centimes=rdv.prix_centimes,
                        commission_centimes=commission(rdv.prix_centimes), statut="a_payer", cree_le=maintenant)
    db.add(paiement)
    db.flush()
    return _page_de_paiement(paiement, client, prestataire, f"{rdv.titre} — {communs.texte_moment(rdv.debut)}",
                             f"{PAGE_RENDEZ_VOUS}?rdv={rdv.id}&paiement=", maintenant)


def commencer_devis(db: Session, devis: Devis, sorte: str, montant: int, client: Compte, maintenant: datetime) -> str:
    """Arrhes (en acceptant) ou solde (après les travaux) d'un devis. Un paiement jamais terminé est simplement repris
    (un seul paiement d'arrhes et un seul de solde par devis). Ex. arrhes de 30 % sur 1 200 € → 360 €."""
    demande = db.get_one(DemandeDevis, devis.demande_devis_id)
    prestataire = db.get_one(Prestataire, demande.prestataire_id)
    if not prestataire.stripe_compte or not prestataire.stripe_pret:
        raise ErreurRegle("Ce prestataire ne peut pas encore être payé par carte : choisissez « En direct ».")
    paiement = du_devis(db, devis.id, sorte)
    if paiement is not None and paiement.statut != "abandonne":
        if paiement.statut == "a_payer":
            raise ErreurRegle("Un paiement est déjà en cours : terminez-le sur la page de Stripe, ou attendez 30 minutes.")
        raise ErreurRegle("C'est déjà payé.")
    if paiement is None:
        paiement = Paiement(devis_id=devis.id, sorte=sorte, montant_centimes=montant, commission_centimes=commission(montant),
                            statut="a_payer", cree_le=maintenant)
        db.add(paiement)
    else:  # repris : nouvelle page de paiement, même ligne
        paiement.statut, paiement.cree_le = "a_payer", maintenant
        paiement.montant_centimes, paiement.commission_centimes = montant, commission(montant)
    db.flush()
    titre = db.get_one(Metier, demande.metier_id).nom
    quoi = "arrhes" if sorte == "arrhes" else "solde"
    return _page_de_paiement(paiement, client, prestataire, f"{titre} — devis {numero_devis(devis)} ({quoi})",
                             f"{PAGE_DEVIS}?devis={devis.id}&paiement=", maintenant)


def _page_de_paiement(paiement: Paiement, client: Compte, prestataire: Prestataire, libelle: str, retour: str,
                      maintenant: datetime) -> str:
    """La page de paiement de Stripe, sur le compte du prestataire, avec la commission de rafals."""
    page = f"{config.ADRESSE_SITE}{retour}"
    # Stripe garde sa page ouverte au moins 30 minutes : une minute de plus que notre délai (un paiement arrivé
    # après l'annulation est remboursé en entier, voir marquer_paye). La clé change si la page est reprise.
    fin = int((maintenant + reglages.PAIEMENT_DELAI).timestamp()) + 60
    session = _stripe(lambda: stripe_api.appeler("POST", "/v1/checkout/sessions", {
        "mode": "payment", "customer_email": client.email, "expires_at": fin,
        "line_items": [{"quantity": 1, "price_data": {
            "currency": "eur", "unit_amount": paiement.montant_centimes, "product_data": {"name": libelle},
        }}],
        "payment_intent_data": {"application_fee_amount": paiement.commission_centimes,
                                "metadata": {"paiement_id": paiement.id}},
        "metadata": {"paiement_id": paiement.id},
        "success_url": f"{page}fait", "cancel_url": f"{page}annule",
    }, compte=prestataire.stripe_compte, cle_unique=f"page-paiement-{paiement.id}-{int(maintenant.timestamp())}"))
    return session["url"]


def _frais(prestataire: Prestataire, paiement_stripe: str) -> tuple[int, str | None]:
    """Les frais pris par Stripe sur ce paiement (ex. 100 = 1,00 €), et le numéro de la commission de rafals."""
    infos = stripe_api.appeler("GET", f"/v1/payment_intents/{paiement_stripe}",
                               {"expand": ["latest_charge.balance_transaction"]}, compte=prestataire.stripe_compte)
    charge = infos.get("latest_charge") or {}
    details = (charge.get("balance_transaction") or {}).get("fee_details") or []
    frais = sum(d["amount"] for d in details if d.get("type") == "stripe_fee")
    commission_rafals = charge.get("application_fee")
    return frais, commission_rafals if isinstance(commission_rafals, str) else (commission_rafals or {}).get("id")


def marquer_paye(db: Session, paiement: Paiement, paiement_stripe: str, maintenant: datetime) -> None:
    """Stripe confirme le paiement : la réservation (ou l'acceptation du devis, ou le solde) est enregistrée et les
    mails partent. Payé trop tard (réservation déjà annulée, devis plus acceptable) : remboursé en entier."""
    if paiement.statut not in ("a_payer", "abandonne"):
        return  # déjà traité (Stripe peut prévenir deux fois)
    s = sujet(db, paiement)
    deja_abandonne = paiement.statut == "abandonne"
    paiement.statut, paiement.stripe_paiement, paiement.paye_le = "paye", paiement_stripe, maintenant
    try:
        paiement.frais_stripe_centimes = _frais(s.prestataire, paiement_stripe)[0]
    except StripeIndisponible as erreur:  # connus plus tard (au remboursement ou au versement)
        journal_serveur.warning("Stripe : %s", erreur)
    journal.noter(db, auteur_id=s.client_id, action=f"payer_{paiement.sorte}", table_cible="paiement", ligne_id=paiement.id,
                  apres={"montant_centimes": paiement.montant_centimes}, maintenant=maintenant)
    if s.rdv is not None:
        from app.services import rendez_vous  # (import ici : rendez_vous ne doit pas dépendre de ce module)

        if deja_abandonne or s.rdv.statut not in communs.ACTIFS:
            _rembourser(db, paiement, s, paiement.montant_centimes,
                        "le paiement est arrivé après l'annulation de la réservation", maintenant)
        else:
            rendez_vous.annoncer_reservation(db, s.rdv, maintenant)
            _facturer(db, paiement, maintenant)
        return
    from app.services import devis as service_devis  # (même raison)

    assert s.devis is not None
    if not service_devis.apres_paiement(db, s.devis, paiement, maintenant):
        _rembourser(db, paiement, s, paiement.montant_centimes,
                    "le paiement est arrivé trop tard, le devis n'est plus valable", maintenant)
    else:
        _facturer(db, paiement, maintenant)


def _facturer(db: Session, paiement: Paiement, maintenant: datetime) -> None:
    """Après chaque paiement par carte, rafals crée la facture au nom du prestataire (RM-FACTURES)."""
    from app.services import factures  # (import ici : factures dépend des devis, qui dépendent de ce module)

    factures.pour_paiement(db, paiement, maintenant)


def _abandonner(db: Session, paiement: Paiement, rdv: RendezVous | None, maintenant: datetime) -> None:
    """Paiement jamais terminé : la réservation est annulée, l'horaire se libère. (Devis : rien d'autre ne change,
    le client peut payer de nouveau.)"""
    paiement.statut = "abandonne"
    if rdv is not None and rdv.statut in communs.ACTIFS:
        communs.changer(rdv, "annule_client", maintenant, "Paiement non terminé")
        communs.noter(db, None, "abandonner_paiement", rdv, maintenant)
        communs.prevenir(db, rdv, sujet="rafals : réservation annulée",
                         client=f"Votre réservation « {rdv.titre} », {communs.texte_moment(rdv.debut)}, est annulée : "
                                "le paiement n'a pas été terminé. Rien n'a été pris sur votre carte.")


# ---------- Messages de Stripe (webhook) ----------


def recevoir(db: Session, evenement: dict[str, Any], maintenant: datetime) -> str:
    """Stripe prévient rafals : paiement terminé, page de paiement expirée, compte d'un prestataire vérifié."""
    sorte, objet = evenement.get("type", ""), (evenement.get("data") or {}).get("object") or {}
    if sorte in ("checkout.session.completed", "checkout.session.expired"):
        identifiant = str((objet.get("metadata") or {}).get("paiement_id", ""))
        paiement = db.get(Paiement, int(identifiant)) if identifiant.isdigit() else None
        if paiement is None:
            return "paiement inconnu"
        if sorte == "checkout.session.completed" and objet.get("payment_status") == "paid":
            marquer_paye(db, paiement, objet["payment_intent"], maintenant)
            return "payé"
        if sorte == "checkout.session.expired" and paiement.statut == "a_payer":
            _abandonner(db, paiement, sujet(db, paiement).rdv, maintenant)
            return "abandonné"
    elif sorte == "account.updated":
        prestataire = db.scalar(select(Prestataire).where(Prestataire.stripe_compte == objet.get("id")))
        if prestataire is not None:
            prestataire.stripe_pret = bool(objet.get("charges_enabled") and objet.get("payouts_enabled"))
            return "compte à jour"
    return "ignoré"


# ---------- Rembourser, verser ----------


def _rembourser(db: Session, paiement: Paiement, s: Sujet, montant: int, raison: str, maintenant: datetime) -> None:
    """Rend `montant` au client, pris sur l'argent encore bloqué chez le prestataire ; rafals rend toujours ses 5 %.
    Les frais de Stripe restent à la charge du prestataire (Stripe les reprend sur ses prochains paiements) quand il
    en est la cause ; quand c'est le client qui annule, `montant` les a déjà retirés."""
    pi = paiement.stripe_paiement or ""
    rembourse = stripe_api.appeler("POST", "/v1/refunds", {"payment_intent": pi, "amount": montant,
                                                          "metadata": {"paiement_id": paiement.id}},
                                   compte=s.prestataire.stripe_compte, cle_unique=f"remboursement-{paiement.id}")
    if paiement.commission_centimes:
        commission_rafals = _frais(s.prestataire, pi)[1]
        if commission_rafals:
            stripe_api.appeler("POST", f"/v1/application_fees/{commission_rafals}/refunds", {},
                               cle_unique=f"commission-rendue-{paiement.id}")
    paiement.statut, paiement.rembourse_le, paiement.rembourse_centimes = "rembourse", maintenant, montant
    paiement.stripe_remboursement = rembourse.get("id")
    journal.noter(db, auteur_id=None, action="rembourser_paiement", table_cible="paiement", ligne_id=paiement.id,
                  apres={"rembourse_centimes": montant, "raison": raison}, maintenant=maintenant)
    from app.services import factures  # (import ici : voir _facturer)

    factures.avoir_pour_remboursement(db, paiement, maintenant)  # un avoir du montant rendu
    _prevenir(db, s, objet="rafals : vous êtes remboursé",
              client=f"« {s.titre} », {s.quand} : {raison}. Vous êtes remboursé de {euros(montant)} ; l'argent revient "
                     "sur votre carte sous 5 à 10 jours.")


def _verser(db: Session, paiement: Paiement, s: Sujet, maintenant: datetime) -> bool:
    """Fait partir l'argent vers la banque du prestataire. Si des frais de remboursement sont dus (son compte Stripe
    est en dessous de ce qu'il devrait contenir), ils sont retirés de ce versement.
    False : l'argent n'est pas encore disponible chez Stripe (quelques jours après le paiement) → on réessaiera."""
    prestataire = s.prestataire
    if paiement.frais_stripe_centimes is None:
        paiement.frais_stripe_centimes = _frais(prestataire, paiement.stripe_paiement or "")[0]
    solde = stripe_api.appeler("GET", "/v1/balance", compte=prestataire.stripe_compte)
    disponible = sum(x["amount"] for x in solde.get("available", []) if x.get("currency") == "eur")
    en_route = sum(x["amount"] for x in solde.get("pending", []) if x.get("currency") == "eur")
    bloques = du_prestataire(db, prestataire.id, ("paye",))
    manque = max(0, sum(net(p) for p in bloques) - disponible - en_route)
    montant = net(paiement) - manque
    if 0 < montant and disponible < montant:
        return False
    if montant > 0:
        versement = stripe_api.appeler("POST", "/v1/payouts", {"amount": montant, "currency": "eur",
                                                              "metadata": {"paiement_id": paiement.id}},
                                       compte=prestataire.stripe_compte, cle_unique=f"versement-{paiement.id}")
        paiement.stripe_versement = versement.get("id")
    paiement.statut, paiement.verse_le = "verse", maintenant
    journal.noter(db, auteur_id=None, action="verser_paiement", table_cible="paiement", ligne_id=paiement.id,
                  apres={"verse_centimes": max(montant, 0), "frais_retenus_centimes": manque}, maintenant=maintenant)
    retenue = f" ({euros(min(manque, net(paiement)))} de frais de remboursement retenus)" if manque else ""
    _prevenir(db, s, objet="rafals : argent versé",
              prestataire=f"« {s.titre} », {s.quand} : {euros(max(montant, 0))} versés vers votre compte en "
                          f"banque{retenue}. Ils arrivent sous quelques jours.")
    return True


def _que_faire(rdv: RendezVous, maintenant: datetime) -> tuple[str, str] | None:
    """Ce que demande l'état du rendez-vous pour un paiement « payé » : ("verser" | "tout" | "moins_frais", raison),
    ou None pour attendre."""
    raisons = {"refuse": "le prestataire a refusé la demande", "expire": "le prestataire n'a pas répondu à temps",
               "annule_prestataire": "le prestataire a annulé le rendez-vous"}
    if rdv.statut in raisons:
        return "tout", raisons[rdv.statut]
    if rdv.statut == "annule_client":
        return "moins_frais", "vous avez annulé le rendez-vous (les frais de paiement ne sont pas rendus)"
    if rdv.statut != "confirme":
        return None
    if rdv.absent is None:
        return ("verser", "") if maintenant >= rdv.fin + reglages.VERSEMENT_APRES_FIN else None
    retenue = rdv.absence_decision != "ne_compte_pas" and absences.compte_deja(rdv, maintenant)
    # Client absent : le prestataire garde l'argent, sauf si l'administrateur donne raison au client
    if rdv.absent == "client":
        if rdv.absence_decision == "ne_compte_pas":
            return "tout", "l'administrateur a décidé que votre absence ne compte pas"
        return ("verser", "") if retenue else None
    # Prestataire absent : le client est remboursé, sauf si l'administrateur donne raison au prestataire
    if rdv.absence_decision == "ne_compte_pas":
        return "verser", ""
    return ("tout", "le prestataire n'est pas venu") if retenue else None


def _regler_devis(db: Session, paiement: Paiement, s: Sujet, maintenant: datetime) -> str | None:
    """Arrhes ou solde payés : versés sans attendre ; arrhes d'un devis annulé par le prestataire : rendues."""
    assert s.devis is not None
    if paiement.sorte == "arrhes" and s.devis.statut == "annule_prestataire":
        # Déjà versées au prestataire : Stripe les reprend sur son compte (ses prochains paiements) — rafals n'avance rien
        _rembourser(db, paiement, s, paiement.montant_centimes, "le prestataire a annulé le devis", maintenant)
        return "rembourses"
    if paiement.statut != "paye":
        return None
    return "verses" if _verser(db, paiement, s, maintenant) else None


def _regler(db: Session, paiement: Paiement, maintenant: datetime) -> str | None:
    s = sujet(db, paiement)
    if paiement.statut == "a_payer":
        delai_fini = maintenant >= paiement.cree_le + reglages.PAIEMENT_DELAI
        if delai_fini or (s.rdv is not None and s.rdv.statut not in communs.ACTIFS):
            _abandonner(db, paiement, s.rdv, maintenant)
            return "abandonnes"
        return None
    if s.rdv is None:
        return _regler_devis(db, paiement, s, maintenant)
    rdv = s.rdv
    while rdv.statut == "deplace":  # le paiement suit le rendez-vous qui remplace l'ancien : rien à payer de nouveau
        nouveau = db.scalar(select(RendezVous).where(
            RendezVous.remplace_id == rdv.id, RendezVous.statut.not_in(("refuse", "expire"))).order_by(RendezVous.id.desc()))
        if nouveau is None:
            return None
        paiement.rendez_vous_id, rdv = nouveau.id, nouveau
        s = sujet(db, paiement)
    action = _que_faire(rdv, maintenant)
    if action is None:
        return None
    sorte, raison = action
    if sorte == "verser":
        return "verses" if _verser(db, paiement, s, maintenant) else None
    if paiement.frais_stripe_centimes is None:
        paiement.frais_stripe_centimes = _frais(s.prestataire, paiement.stripe_paiement or "")[0]
    montant = paiement.montant_centimes - (paiement.frais_stripe_centimes if sorte == "moins_frais" else 0)
    _rembourser(db, paiement, s, montant, raison, maintenant)
    return "rembourses"


def traiter(db: Session, maintenant: datetime | None = None) -> dict[str, int]:
    """Lancé toutes les 5 minutes. Ex. Paul a annulé → remboursé de 49,00 € ; rendez-vous de Léa fini depuis 48 h →
    46,50 € versés ; page de paiement fermée depuis 30 minutes → réservation annulée."""
    maintenant = maintenant or datetime.now(UTC)
    compte = {"abandonnes": 0, "rembourses": 0, "verses": 0, "pannes_stripe": 0, "erreurs": 0}
    # (+ les arrhes déjà versées d'un devis que le prestataire vient d'annuler : à rendre au client)
    arrhes_a_rendre = select(Paiement.id).join(Devis, Devis.id == Paiement.devis_id).where(
        Paiement.sorte == "arrhes", Paiement.statut == "verse", Devis.statut == "annule_prestataire")
    a_suivre = select(Paiement).where(or_(Paiement.statut.in_(EN_COURS), Paiement.id.in_(arrhes_a_rendre))).order_by(Paiement.id)
    for paiement in db.scalars(a_suivre).all():
        try:
            with db.begin_nested():  # une panne sur un paiement n'annule pas ce qui est fait pour les autres
                fait = _regler(db, paiement, maintenant)
        except StripeIndisponible as erreur:
            journal_serveur.warning("Stripe, paiement n° %s : %s", paiement.id, erreur)
            compte["pannes_stripe"] += 1
            continue
        except Exception:  # un paiement en erreur ne bloque jamais les autres ; noté pour être corrigé
            journal_serveur.exception("Paiement n° %s : erreur inattendue", paiement.id)
            compte["erreurs"] += 1
            continue
        if fait:
            compte[fait] += 1
    return compte
