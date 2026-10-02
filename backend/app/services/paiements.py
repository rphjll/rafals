"""Paiement par carte d'un rendez-vous (Stripe Connect). Règles : RM-PAIEMENTS.md (validé par Raphael le 02/10/2026).

Le chemin de l'argent : le client paie en réservant → l'argent est bloqué sur le compte Stripe du prestataire →
48 h après la fin du rendez-vous, rafals le fait partir vers sa banque (« versé »). Un remboursement prend l'argent
encore bloqué : rafals n'avance jamais d'argent. rafals garde 5 % ; rien sur les espèces.

Une seule tâche de fond (toutes les 5 minutes) regarde chaque paiement en cours et fait ce que l'état du rendez-vous
demande : rembourser (refusé, expiré, annulé, absence), verser, ou abandonner un paiement jamais terminé. Ainsi,
aucune action (annuler, refuser, bloquer un jour…) n'a besoin de connaître Stripe, et une panne de Stripe est
simplement réessayée au passage suivant."""

import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import config, reglages
from app.modeles.comptes import Compte
from app.modeles.paiements import Paiement
from app.modeles.prestataires import Prestataire
from app.modeles.rendez_vous import RendezVous
from app.services import absences, journal, stripe_api
from app.services import rendez_vous_communs as communs
from app.services.erreurs import ErreurRegle
from app.services.stripe_api import StripeIndisponible

journal_serveur = logging.getLogger("rafals")

EN_COURS = ("a_payer", "paye")  # paiements que la tâche de fond suit encore
CACHES_AU_PRESTATAIRE = ("a_payer", "abandonne")  # réservation pas encore payée (ou jamais) : le prestataire ne la voit pas
PAGE_PROFIL = "/proposer"
PAGE_RENDEZ_VOUS = "/rendez-vous"


def commission(montant_centimes: int) -> int:
    """5 %, arrondis au centime. Ex. 50,00 € → 2,50 € ; 120,00 € → 6,00 € ; 33,33 € → 1,67 €."""
    return (montant_centimes * reglages.COMMISSION_POURCENT + 50) // 100


def euros(centimes: int) -> str:
    """« 46,50 € »"""
    return f"{centimes // 100},{centimes % 100:02d} €"


def du_rendez_vous(db: Session, rdv_id: int) -> Paiement | None:
    return db.scalar(select(Paiement).where(Paiement.rendez_vous_id == rdv_id))


def net(paiement: Paiement) -> int:
    """Ce que reçoit le prestataire : le prix, moins les 5 % de rafals, moins les frais de Stripe."""
    return paiement.montant_centimes - paiement.commission_centimes - (paiement.frais_stripe_centimes or 0)


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


# ---------- Le client paie en réservant ----------


def commencer(db: Session, rdv: RendezVous, client: Compte, maintenant: datetime) -> str:
    """Après la réservation : le paiement « à payer » et l'adresse de la page de paiement de Stripe.
    Ex. coupe à 50 € → Stripe prend 50 € sur la carte de Paul, dont 2,50 € pour rafals."""
    prestataire = db.get_one(Prestataire, rdv.prestataire_id)
    if not prestataire.stripe_compte or rdv.prix_centimes is None:
        raise ErreurRegle("Ce mode de paiement n'est pas accepté pour cette annonce.")
    paiement = Paiement(rendez_vous_id=rdv.id, montant_centimes=rdv.prix_centimes, commission_centimes=commission(rdv.prix_centimes),
                        statut="a_payer", cree_le=maintenant)
    db.add(paiement)
    db.flush()
    page = f"{config.ADRESSE_SITE}{PAGE_RENDEZ_VOUS}?rdv={rdv.id}&paiement="
    # Stripe garde sa page ouverte au moins 30 minutes : une minute de plus que notre délai (un paiement arrivé
    # après l'annulation est remboursé en entier, voir marquer_paye)
    fin = int((maintenant + reglages.PAIEMENT_DELAI).timestamp()) + 60
    session = _stripe(lambda: stripe_api.appeler("POST", "/v1/checkout/sessions", {
        "mode": "payment", "customer_email": client.email, "expires_at": fin,
        "line_items": [{"quantity": 1, "price_data": {
            "currency": "eur", "unit_amount": paiement.montant_centimes,
            "product_data": {"name": f"{rdv.titre} — {communs.texte_moment(rdv.debut)}"},
        }}],
        "payment_intent_data": {"application_fee_amount": paiement.commission_centimes,
                                "metadata": {"paiement_id": paiement.id}},
        "metadata": {"paiement_id": paiement.id},
        "success_url": f"{page}fait", "cancel_url": f"{page}annule",
    }, compte=prestataire.stripe_compte, cle_unique=f"page-paiement-{paiement.id}"))
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
    """Stripe confirme le paiement : la réservation existe vraiment, les mails partent (confirmée ou demande).
    Payé trop tard (réservation déjà annulée) : remboursé en entier."""
    if paiement.statut not in ("a_payer", "abandonne"):
        return  # déjà traité (Stripe peut prévenir deux fois)
    from app.services import rendez_vous  # (import ici : rendez_vous ne doit pas dépendre de ce module)

    rdv = db.get_one(RendezVous, paiement.rendez_vous_id)
    prestataire = db.get_one(Prestataire, rdv.prestataire_id)
    trop_tard = paiement.statut == "abandonne" or rdv.statut not in communs.ACTIFS
    paiement.statut, paiement.stripe_paiement, paiement.paye_le = "paye", paiement_stripe, maintenant
    try:
        paiement.frais_stripe_centimes = _frais(prestataire, paiement_stripe)[0]
    except StripeIndisponible as erreur:  # connus plus tard (au remboursement ou au versement)
        journal_serveur.warning("Stripe : %s", erreur)
    journal.noter(db, auteur_id=rdv.client_id, action="payer_rendez_vous", table_cible="paiement", ligne_id=paiement.id,
                  apres={"montant_centimes": paiement.montant_centimes, "rendez_vous_id": rdv.id}, maintenant=maintenant)
    if trop_tard:
        _rembourser(db, paiement, rdv, paiement.montant_centimes, "le paiement est arrivé après l'annulation de la réservation",
                    maintenant)
    else:
        rendez_vous.annoncer_reservation(db, rdv, maintenant)


def _abandonner(db: Session, paiement: Paiement, rdv: RendezVous, maintenant: datetime) -> None:
    """Paiement jamais terminé : la réservation est annulée, l'horaire se libère."""
    paiement.statut = "abandonne"
    if rdv.statut in communs.ACTIFS:
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
            _abandonner(db, paiement, db.get_one(RendezVous, paiement.rendez_vous_id), maintenant)
            return "abandonné"
    elif sorte == "account.updated":
        prestataire = db.scalar(select(Prestataire).where(Prestataire.stripe_compte == objet.get("id")))
        if prestataire is not None:
            prestataire.stripe_pret = bool(objet.get("charges_enabled") and objet.get("payouts_enabled"))
            return "compte à jour"
    return "ignoré"


# ---------- Rembourser, verser ----------


def _rembourser(db: Session, paiement: Paiement, rdv: RendezVous, montant: int, raison: str, maintenant: datetime) -> None:
    """Rend `montant` au client, pris sur l'argent encore bloqué chez le prestataire ; rafals rend toujours ses 5 %.
    Les frais de Stripe restent à la charge du prestataire (Stripe les reprend sur ses prochains paiements) quand il
    en est la cause ; quand c'est le client qui annule, `montant` les a déjà retirés."""
    prestataire = db.get_one(Prestataire, rdv.prestataire_id)
    pi = paiement.stripe_paiement or ""
    rembourse = stripe_api.appeler("POST", "/v1/refunds", {"payment_intent": pi, "amount": montant,
                                                          "metadata": {"paiement_id": paiement.id}},
                                   compte=prestataire.stripe_compte, cle_unique=f"remboursement-{paiement.id}")
    if paiement.commission_centimes:
        commission_rafals = _frais(prestataire, pi)[1]
        if commission_rafals:
            stripe_api.appeler("POST", f"/v1/application_fees/{commission_rafals}/refunds", {},
                               cle_unique=f"commission-rendue-{paiement.id}")
    paiement.statut, paiement.rembourse_le, paiement.rembourse_centimes = "rembourse", maintenant, montant
    paiement.stripe_remboursement = rembourse.get("id")
    journal.noter(db, auteur_id=None, action="rembourser_paiement", table_cible="paiement", ligne_id=paiement.id,
                  apres={"rembourse_centimes": montant, "raison": raison}, maintenant=maintenant)
    communs.prevenir(db, rdv, sujet="rafals : vous êtes remboursé",
                     client=f"« {rdv.titre} », {communs.texte_moment(rdv.debut)} : {raison}. Vous êtes remboursé de "
                            f"{euros(montant)} ; l'argent revient sur votre carte sous 5 à 10 jours.")


def _verser(db: Session, paiement: Paiement, rdv: RendezVous, maintenant: datetime) -> bool:
    """Fait partir l'argent du rendez-vous vers la banque du prestataire. Si des frais de remboursement sont dus
    (son compte Stripe est en dessous de ce qu'il devrait contenir), ils sont retirés de ce versement.
    False : l'argent n'est pas encore disponible chez Stripe (quelques jours après le paiement) → on réessaiera."""
    prestataire = db.get_one(Prestataire, rdv.prestataire_id)
    if paiement.frais_stripe_centimes is None:
        paiement.frais_stripe_centimes = _frais(prestataire, paiement.stripe_paiement or "")[0]
    solde = stripe_api.appeler("GET", "/v1/balance", compte=prestataire.stripe_compte)
    disponible = sum(s["amount"] for s in solde.get("available", []) if s.get("currency") == "eur")
    en_route = sum(s["amount"] for s in solde.get("pending", []) if s.get("currency") == "eur")
    bloques = db.scalars(select(Paiement).join(RendezVous, RendezVous.id == Paiement.rendez_vous_id).where(
        RendezVous.prestataire_id == prestataire.id, Paiement.statut == "paye"))
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
    communs.prevenir(db, rdv, sujet="rafals : argent versé",
                     prestataire=f"« {rdv.titre} », {communs.texte_moment(rdv.debut)} : {euros(max(montant, 0))} versés "
                                 f"vers votre compte en banque{retenue}. Ils arrivent sous quelques jours.")
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


def _regler(db: Session, paiement: Paiement, maintenant: datetime) -> str | None:
    rdv = db.get_one(RendezVous, paiement.rendez_vous_id)
    if paiement.statut == "a_payer":
        if rdv.statut not in communs.ACTIFS or maintenant >= paiement.cree_le + reglages.PAIEMENT_DELAI:
            _abandonner(db, paiement, rdv, maintenant)
            return "abandonnes"
        return None
    while rdv.statut == "deplace":  # le paiement suit le rendez-vous qui remplace l'ancien : rien à payer de nouveau
        nouveau = db.scalar(select(RendezVous).where(
            RendezVous.remplace_id == rdv.id, RendezVous.statut.not_in(("refuse", "expire"))).order_by(RendezVous.id.desc()))
        if nouveau is None:
            return None
        paiement.rendez_vous_id, rdv = nouveau.id, nouveau
    action = _que_faire(rdv, maintenant)
    if action is None:
        return None
    sorte, raison = action
    if sorte == "verser":
        return "verses" if _verser(db, paiement, rdv, maintenant) else None
    if paiement.frais_stripe_centimes is None:
        paiement.frais_stripe_centimes = _frais(db.get_one(Prestataire, rdv.prestataire_id), paiement.stripe_paiement or "")[0]
    montant = paiement.montant_centimes - (paiement.frais_stripe_centimes if sorte == "moins_frais" else 0)
    _rembourser(db, paiement, rdv, montant, raison, maintenant)
    return "rembourses"


def traiter(db: Session, maintenant: datetime | None = None) -> dict[str, int]:
    """Lancé toutes les 5 minutes. Ex. Paul a annulé → remboursé de 49,00 € ; rendez-vous de Léa fini depuis 48 h →
    46,50 € versés ; page de paiement fermée depuis 30 minutes → réservation annulée."""
    maintenant = maintenant or datetime.now(UTC)
    compte = {"abandonnes": 0, "rembourses": 0, "verses": 0, "pannes_stripe": 0}
    for paiement in db.scalars(select(Paiement).where(Paiement.statut.in_(EN_COURS)).order_by(Paiement.id)).all():
        try:
            with db.begin_nested():  # une panne sur un paiement n'annule pas ce qui est fait pour les autres
                fait = _regler(db, paiement, maintenant)
        except StripeIndisponible as erreur:
            journal_serveur.warning("Stripe, paiement n° %s : %s", paiement.id, erreur)
            compte["pannes_stripe"] += 1
            continue
        if fait:
            compte[fait] += 1
    return compte
