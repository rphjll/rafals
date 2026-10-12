"""Devis : demande du client (avec photos), devis en lignes du prestataire, autre date, acceptation (arrhes par carte
ou paiement en direct), travaux terminés, solde, problème, annulations, expiration.
Règles : .doc/regles-metier/RM-DEVIS.md (validé par Raphael le 02/10/2026), MLD du lot 5.3 (03/10/2026).
Un devis n'est jamais effacé ; ses lignes ne changent plus après l'envoi (seules les dates peuvent changer)."""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.agenda import Blocage
from app.modeles.comptes import Compte
from app.modeles.devis import DemandeDevis, Devis, LigneDevis, PhotoDemande
from app.modeles.metiers import Metier
from app.modeles.paiements import Paiement
from app.modeles.prestataires import Prestataire
from app.modeles.rendez_vous import RendezVous
from app.services import absences, clients, droits, fichiers, journal, locaux, mails, paiements, stripe_api
from app.services import prestataires as service_prestataires
from app.services import rendez_vous_communs as communs
from app.services.erreurs import ErreurRegle

PARIS = reglages.FUSEAU_AFFICHAGE
numero = paiements.numero_devis
euros = paiements.euros
EN_COURS = ("envoye", "autre_date")  # le client peut encore répondre


def aujourd_hui(maintenant: datetime) -> date:
    return maintenant.astimezone(PARIS).date()


def jour(d: date) -> str:
    """« 19/10/2026 »"""
    return f"{d:%d/%m/%Y}"


# ---------- Calculs ----------


@dataclass
class Ligne:
    libelle: str
    quantite_centiemes: int  # 4000 = 40 ; 250 = 2,5
    prix_unitaire_centimes: int  # hors taxe si le prestataire facture la TVA
    tva_pour_mille: int | None = None  # 55, 100 ou 200


@dataclass
class Totaux:
    ht: int
    tva: int
    ttc: int
    arrhes: int
    solde: int


def montant_ligne(quantite_centiemes: int, prix_unitaire_centimes: int) -> int:
    """Ex. 40 × 3,50 € = 140,00 € ; 2,5 × 12,00 € = 30,00 €."""
    return (quantite_centiemes * prix_unitaire_centimes + 50) // 100


def totaux(lignes: list[Ligne] | list[LigneDevis], arrhes_pourcent: int) -> Totaux:
    """Ex. 1 000,00 € HT + 100,00 € de TVA à 10 % = 1 100,00 € TTC ; arrhes 30 % = 330,00 € ; solde 770,00 €.
    Sans TVA : HT = TTC (une seule somme, avec la mention 293 B)."""
    ht = tva = 0
    for ligne in lignes:
        montant = montant_ligne(ligne.quantite_centiemes, ligne.prix_unitaire_centimes)
        ht += montant
        tva += (montant * ligne.tva_pour_mille + 500) // 1000 if ligne.tva_pour_mille else 0
    ttc = ht + tva
    arrhes = (ttc * arrhes_pourcent + 50) // 100
    return Totaux(ht, tva, ttc, arrhes, ttc - arrhes)


def lignes_de(db: Session, devis: Devis) -> list[LigneDevis]:
    return list(db.scalars(select(LigneDevis).where(LigneDevis.devis_id == devis.id).order_by(LigneDevis.ordre)))


def totaux_du_devis(db: Session, devis: Devis) -> Totaux:
    return totaux(lignes_de(db, devis), devis.arrhes_pourcent)


# ---------- Qui voit quoi ----------


def demande_de(db: Session, devis: Devis) -> DemandeDevis:
    return db.get_one(DemandeDevis, devis.demande_devis_id)


def devis_de(db: Session, demande: DemandeDevis) -> Devis | None:
    return db.scalar(select(Devis).where(Devis.demande_devis_id == demande.id))


def demande_du_client(db: Session, client: Compte, demande_id: int) -> DemandeDevis:
    demande = db.get(DemandeDevis, demande_id)
    if demande is None or demande.client_id != client.id:
        raise ErreurRegle("Cette demande de devis n'existe pas.", 404)
    return demande


def demande_du_prestataire(db: Session, prestataire: Prestataire, demande_id: int) -> DemandeDevis:
    demande = db.get(DemandeDevis, demande_id)
    if demande is None or demande.prestataire_id != prestataire.id:
        raise ErreurRegle("Cette demande de devis n'existe pas.", 404)
    return demande


def devis_du_client(db: Session, client: Compte, devis_id: int) -> Devis:
    devis = db.get(Devis, devis_id)
    if devis is None or demande_de(db, devis).client_id != client.id:
        raise ErreurRegle("Ce devis n'existe pas.", 404)
    return devis


def devis_du_prestataire(db: Session, prestataire: Prestataire, devis_id: int) -> Devis:
    devis = db.get(Devis, devis_id)
    if devis is None or demande_de(db, devis).prestataire_id != prestataire.id:
        raise ErreurRegle("Ce devis n'existe pas.", 404)
    return devis


def _titre(db: Session, demande: DemandeDevis) -> str:
    """Le métier concerné, ex. « Maçon » (avant le retrait des annonces : le titre de l'annonce)."""
    return db.get_one(Metier, demande.metier_id).nom


def _prevenir(db: Session, demande: DemandeDevis, *, objet: str, client: str | None = None, prestataire: str | None = None) -> None:
    if client:
        mails.envoyer_mail(db.get_one(Compte, demande.client_id).email, objet, client)
    if prestataire:
        compte = db.get_one(Compte, db.get_one(Prestataire, demande.prestataire_id).compte_id)
        mails.envoyer_mail(compte.email, objet, prestataire)


def _noter(db: Session, auteur_id: int | None, action: str, table: str, ligne_id: int, maintenant: datetime, **apres) -> None:
    journal.noter(db, auteur_id=auteur_id, action=action, table_cible=table, ligne_id=ligne_id, apres=apres or None,
                  maintenant=maintenant)


# ---------- Le client demande un devis ----------


def demander(db: Session, client: Compte, prestataire_id: int, metier_id: int, texte: str, maintenant: datetime) -> DemandeDevis:
    """[Demander un devis] sur le profil d'un prestataire au SIRET vérifié, pour un de ses métiers.
    Ex. Mme Dupont écrit à Paul, maçon : « Muret de 5 mètres au fond du jardin » (photos ensuite, 5 au plus)."""
    if not droits.peut_reserver_ou_publier(db, client, maintenant):
        raise ErreurRegle("Vérifiez d'abord votre adresse mail (ou l'accord de vos parents) pour demander un devis.", 403)
    suspendu = absences.reservation_suspendue_jusqu_au(db, client.id, maintenant)
    if suspendu is not None:
        raise ErreurRegle(f"Vous ne pouvez plus réserver ni demander de devis jusqu'au {suspendu.astimezone(PARIS):%d/%m/%Y}.", 403)
    prestataire = db.get(Prestataire, prestataire_id)
    if prestataire is None or prestataire.statut != "actif":
        raise ErreurRegle("Ce prestataire n'existe pas.", 404)
    if prestataire.compte_id == client.id:
        raise ErreurRegle("Vous ne pouvez pas vous demander un devis à vous-même.")
    if prestataire.siret_statut != "verifie":
        raise ErreurRegle("Ce prestataire ne peut pas faire de devis en ce moment (SIRET pas vérifié).")
    if metier_id not in service_prestataires.metiers_exerces(db, prestataire, maintenant.astimezone(PARIS).date()):
        raise ErreurRegle("Choisissez un des métiers de ce prestataire.")
    texte = (texte or "").strip()
    mini, maxi = reglages.DEMANDE_DEVIS_TEXTE
    if not mini <= len(texte) <= maxi:
        raise ErreurRegle(f"Décrivez votre besoin en {mini} à {maxi} caractères (ex. « Muret de 5 mètres au fond du jardin »).")

    # Lieu des travaux : l'adresse du client, recopiée (obligatoire si le prestataire ne reçoit pas chez lui)
    adresse = clients.adresse_de(db, client) if prestataire.lieu in ("chez_client", "les_deux") else None
    if prestataire.lieu == "chez_client" and adresse is None:
        raise ErreurRegle("Indiquez d'abord votre adresse : le prestataire vient chez vous.", 400)
    demande = DemandeDevis(
        client_id=client.id, annonce_id=None, prestataire_id=prestataire.id, metier_id=metier_id, texte=texte,
        statut="envoyee",
        commune_id=adresse.commune_id if adresse else None, adresse_ligne=adresse.ligne if adresse else None,
        adresse_complement=adresse.complement if adresse else None, code_postal=adresse.code_postal if adresse else None,
        cree_le=maintenant, statut_change_le=maintenant,
    )
    db.add(demande)
    db.flush()
    titre = _titre(db, demande)
    _noter(db, client.id, "demander_devis", "demande_devis", demande.id, maintenant, metier_id=metier_id)
    _prevenir(db, demande, objet=f"rafals : demande de devis « {titre} »",
              prestataire=f"Nouvelle demande de devis pour « {titre} » : « {texte[:200]} ». Répondez sur rafals "
                          "(« Mes devis »).")
    return demande


def photos_de(db: Session, demande: DemandeDevis) -> list[PhotoDemande]:
    return list(db.scalars(select(PhotoDemande).where(PhotoDemande.demande_devis_id == demande.id).order_by(PhotoDemande.ordre)))


def ajouter_photo(db: Session, client: Compte, demande: DemandeDevis, *, nom_fichier: str, type_mime: str, contenu: bytes,
                  maintenant: datetime) -> PhotoDemande:
    if demande.statut != "envoyee":
        raise ErreurRegle("Le prestataire a déjà répondu : vous ne pouvez plus ajouter de photo.")
    deja = photos_de(db, demande)
    if len(deja) >= reglages.DEMANDE_DEVIS_PHOTOS_MAX:
        raise ErreurRegle(f"Au plus {reglages.DEMANDE_DEVIS_PHOTOS_MAX} photos par demande.")
    fichiers.verifier(contenu, type_mime, types_acceptes=reglages.PHOTO_TYPES_ACCEPTES,
                      taille_max_octets=reglages.PHOTO_TAILLE_MAX_OCTETS)
    fichier = fichiers.enregistrer(db, client, nom_fichier=nom_fichier, type_mime=type_mime, contenu=contenu, maintenant=maintenant)
    photo = PhotoDemande(demande_devis_id=demande.id, fichier_id=fichier.id, ordre=len(deja) + 1)
    db.add(photo)
    db.flush()
    _noter(db, client.id, "ajouter_photo_demande", "demande_devis", demande.id, maintenant, fichier_id=fichier.id, ordre=photo.ordre)
    return photo


def annuler_demande(db: Session, client: Compte, demande: DemandeDevis, maintenant: datetime) -> DemandeDevis:
    if demande.statut != "envoyee":
        raise ErreurRegle("Le prestataire a déjà répondu à cette demande.")
    demande.statut, demande.statut_change_le = "annulee", maintenant
    _noter(db, client.id, "annuler_demande_devis", "demande_devis", demande.id, maintenant)
    _prevenir(db, demande, objet="rafals : demande de devis annulée",
              prestataire=f"Le client a annulé sa demande de devis « {_titre(db, demande)} ».")
    return demande


def decliner(db: Session, prestataire: Prestataire, demande: DemandeDevis, motif: str | None, maintenant: datetime) -> DemandeDevis:
    """Ex. « Je ne fais pas ce genre de travaux » (motif facultatif, envoyé au client)."""
    if demande.statut != "envoyee":
        raise ErreurRegle("Cette demande n'attend plus de réponse.")
    demande.statut, demande.statut_change_le, demande.motif = "declinee", maintenant, (motif or "").strip()[:500] or None
    _noter(db, prestataire.compte_id, "decliner_demande_devis", "demande_devis", demande.id, maintenant)
    raison = f" Motif : « {demande.motif} »." if demande.motif else ""
    _prevenir(db, demande, objet="rafals : demande de devis déclinée",
              client=f"{prestataire.nom_affiche} ne peut pas faire de devis pour « {_titre(db, demande)} ».{raison}")
    return demande


# ---------- Le prestataire envoie son devis ----------


def _verifier_lignes(prestataire: Prestataire, lignes: list[Ligne]) -> list[Ligne]:
    if not lignes:
        raise ErreurRegle("Ajoutez au moins une ligne (ex. « Main-d'œuvre — 16 h × 45,00 € »).")
    if len(lignes) > reglages.DEVIS_LIGNES_MAX:
        raise ErreurRegle(f"Au plus {reglages.DEVIS_LIGNES_MAX} lignes par devis.")
    mini, maxi = reglages.DEVIS_LIBELLE
    propres = []
    for rang, ligne in enumerate(lignes, start=1):
        libelle = " ".join((ligne.libelle or "").split())
        if not mini <= len(libelle) <= maxi:
            raise ErreurRegle(f"Ligne {rang} : écrivez ce que c'est (ex. « Parpaings »).")
        if ligne.quantite_centiemes <= 0:
            raise ErreurRegle(f"Ligne {rang} : la quantité doit être plus grande que 0.")
        if ligne.prix_unitaire_centimes < 0:
            raise ErreurRegle(f"Ligne {rang} : le prix ne peut pas être négatif.")
        taux = ligne.tva_pour_mille
        if prestataire.facture_tva and taux not in reglages.DEVIS_TAUX_TVA_POUR_MILLE:
            raise ErreurRegle(f"Ligne {rang} : choisissez le taux de TVA (5,5 %, 10 % ou 20 %).")
        propres.append(Ligne(libelle, ligne.quantite_centiemes, ligne.prix_unitaire_centimes,
                             taux if prestataire.facture_tva else None))
    return propres


def _limites(debut: date, fin: date) -> tuple[datetime, datetime]:
    """Les jours des travaux, de minuit (heure de Paris) au lendemain du dernier jour à minuit."""
    return datetime.combine(debut, time(0), tzinfo=PARIS), datetime.combine(fin + timedelta(days=1), time(0), tzinfo=PARIS)


def _verifier_dates(db: Session, prestataire: Prestataire, debut: date, fin: date, maintenant: datetime,
                    sauf_blocage_id: int | None = None) -> None:
    """Jours des travaux pas passés, dans l'ordre, et libres dans l'agenda (ni rendez-vous, ni congés)."""
    if debut < aujourd_hui(maintenant):
        raise ErreurRegle("Les travaux ne peuvent pas commencer dans le passé.")
    if fin < debut:
        raise ErreurRegle("Le dernier jour des travaux doit être après le premier.")
    de, a = _limites(debut, fin)
    rdv = db.scalar(select(RendezVous).where(RendezVous.prestataire_id == prestataire.id, RendezVous.statut.in_(communs.ACTIFS),
                                             RendezVous.debut < a, RendezVous.fin > de).order_by(RendezVous.debut).limit(1))
    blocage = db.scalar(select(Blocage).where(Blocage.prestataire_id == prestataire.id, Blocage.debut < a, Blocage.fin > de,
                                              Blocage.id != (sauf_blocage_id or 0)).order_by(Blocage.debut).limit(1))
    occupe = rdv.debut if rdv else (max(blocage.debut, de) if blocage else None)
    if occupe is not None:
        raise ErreurRegle(f"Le {jour(occupe.astimezone(PARIS).date())} n'est pas libre dans votre agenda (rendez-vous ou "
                          "congés) : choisissez d'autres jours.")


def envoyer(db: Session, prestataire: Prestataire, demande: DemandeDevis, lignes: list[Ligne], *, arrhes_pourcent: int,
            travaux_debut: date, travaux_fin: date, valable_jusqu_au: date, maintenant: datetime) -> Devis:
    """Ex. devis D-2026-0002 de Paul : 3 lignes, 1 190 €, arrhes 30 %, travaux du 19/10 au 20/10, valable jusqu'au 01/11."""
    locaux.verifier_modifiable(prestataire)
    if demande.statut != "envoyee":
        raise ErreurRegle("Cette demande n'attend plus de devis.")
    if prestataire.siret_statut != "verifie":
        raise ErreurRegle("Il faut un SIRET vérifié pour envoyer un devis.")
    propres = _verifier_lignes(prestataire, lignes)
    if not 0 <= arrhes_pourcent <= 100:
        raise ErreurRegle("Les arrhes vont de 0 à 100 % du total.")
    if totaux(propres, arrhes_pourcent).ttc <= 0:
        raise ErreurRegle("Le total du devis doit être plus grand que 0 €.")
    if valable_jusqu_au < aujourd_hui(maintenant):
        raise ErreurRegle("La date « Valable jusqu'au » est déjà passée.")
    # Verrou sur le prestataire : deux devis envoyés en même temps n'ont jamais le même numéro
    db.scalar(select(Prestataire).where(Prestataire.id == prestataire.id).with_for_update())
    _verifier_dates(db, prestataire, travaux_debut, travaux_fin, maintenant)
    annee = aujourd_hui(maintenant).year
    dernier = db.scalar(select(func.max(Devis.numero)).join(DemandeDevis, DemandeDevis.id == Devis.demande_devis_id)
                        .where(DemandeDevis.prestataire_id == prestataire.id, Devis.annee == annee)) or 0
    devis = Devis(demande_devis_id=demande.id, annee=annee, numero=dernier + 1, facture_tva=prestataire.facture_tva,
                  arrhes_pourcent=arrhes_pourcent, travaux_debut=travaux_debut, travaux_fin=travaux_fin,
                  valable_jusqu_au=valable_jusqu_au, statut="envoye", envoye_le=maintenant, statut_change_le=maintenant)
    db.add(devis)
    db.flush()
    for rang, ligne in enumerate(propres, start=1):
        db.add(LigneDevis(devis_id=devis.id, ordre=rang, libelle=ligne.libelle, quantite_centiemes=ligne.quantite_centiemes,
                          prix_unitaire_centimes=ligne.prix_unitaire_centimes, tva_pour_mille=ligne.tva_pour_mille))
    demande.statut, demande.statut_change_le = "devis_recu", maintenant
    db.flush()
    t = totaux_du_devis(db, devis)
    _noter(db, prestataire.compte_id, "envoyer_devis", "devis", devis.id, maintenant, numero=numero(devis), ttc_centimes=t.ttc)
    _prevenir(db, demande, objet=f"rafals : devis {numero(devis)} reçu",
              client=f"{prestataire.nom_affiche} vous envoie le devis {numero(devis)} pour « {_titre(db, demande)} » : "
                     f"{euros(t.ttc)}, travaux du {jour(travaux_debut)} au {jour(travaux_fin)}. Valable jusqu'au "
                     f"{jour(valable_jusqu_au)} : acceptez-le ou refusez-le sur rafals (« Mes devis »).")
    return devis


# ---------- Le client répond ----------


def _encore_valable(devis: Devis, maintenant: datetime) -> None:
    if aujourd_hui(maintenant) > devis.valable_jusqu_au:
        raise ErreurRegle(f"Ce devis a expiré le {jour(devis.valable_jusqu_au)} : demandez-en un nouveau.")


def demander_autre_date(db: Session, client: Compte, devis: Devis, message: str, maintenant: datetime) -> Devis:
    """Ex. « Je suis absente cette semaine-là, plutôt fin octobre » : le prestataire change les dates et le devis revient."""
    if devis.statut != "envoye":
        raise ErreurRegle("Ce devis n'attend pas votre réponse.")
    _encore_valable(devis, maintenant)
    message = (message or "").strip()
    if len(message) < 5:
        raise ErreurRegle("Écrivez quelles dates vous iraient (ex. « Plutôt fin octobre »).")
    devis.statut, devis.statut_change_le, devis.message = "autre_date", maintenant, message[:500]
    demande = demande_de(db, devis)
    _noter(db, client.id, "demander_autre_date_devis", "devis", devis.id, maintenant)
    _prevenir(db, demande, objet=f"rafals : autre date demandée, devis {numero(devis)}",
              prestataire=f"Le client demande une autre date pour le devis {numero(devis)} : « {devis.message} ». "
                          "Proposez de nouvelles dates sur rafals.")
    return devis


def changer_dates(db: Session, prestataire: Prestataire, devis: Devis, travaux_debut: date, travaux_fin: date,
                  maintenant: datetime) -> Devis:
    """Le reste du devis ne change pas ; il revient au client."""
    if devis.statut not in EN_COURS:
        raise ErreurRegle("Les dates ne se changent plus : le devis n'attend plus de réponse.")
    _verifier_dates(db, prestataire, travaux_debut, travaux_fin, maintenant)
    devis.travaux_debut, devis.travaux_fin = travaux_debut, travaux_fin
    devis.statut, devis.statut_change_le, devis.message = "envoye", maintenant, None
    _noter(db, prestataire.compte_id, "changer_dates_devis", "devis", devis.id, maintenant,
           travaux_debut=travaux_debut.isoformat(), travaux_fin=travaux_fin.isoformat())
    _prevenir(db, demande_de(db, devis), objet=f"rafals : nouvelles dates, devis {numero(devis)}",
              client=f"{prestataire.nom_affiche} propose de nouvelles dates pour le devis {numero(devis)} : du "
                     f"{jour(travaux_debut)} au {jour(travaux_fin)}. Acceptez-le ou refusez-le sur rafals.")
    return devis


def refuser(db: Session, client: Compte, devis: Devis, motif: str | None, maintenant: datetime) -> Devis:
    if devis.statut not in EN_COURS:
        raise ErreurRegle("Ce devis n'attend pas votre réponse.")
    devis.statut, devis.statut_change_le, devis.message = "refuse", maintenant, (motif or "").strip()[:500] or None
    _noter(db, client.id, "refuser_devis", "devis", devis.id, maintenant)
    raison = f" Motif : « {devis.message} »." if devis.message else ""
    _prevenir(db, demande_de(db, devis), objet=f"rafals : devis {numero(devis)} refusé",
              prestataire=f"Le client a refusé le devis {numero(devis)}.{raison}")
    return devis


def modes_possibles(db: Session, devis: Devis) -> list[str]:
    """« carte » si le prestataire a un SIRET vérifié et la carte activée chez Stripe ; « direct » toujours
    (choix de Claude au lot 9.2 : aucune rubrique nouvelle dans le devis)."""
    prestataire = db.get_one(Prestataire, demande_de(db, devis).prestataire_id)
    carte = prestataire.siret_statut == "verifie" and prestataire.stripe_pret and stripe_api.disponible()
    return (["carte"] if carte else []) + ["direct"]


def accepter(db: Session, client: Compte, devis: Devis, mode_paiement: str, maintenant: datetime) -> str | None:
    """« Par carte » avec des arrhes : renvoie la page de paiement de Stripe (le devis est accepté quand les arrhes sont
    payées). Sans arrhes, ou « en direct » : accepté tout de suite (None)."""
    if devis.statut == "autre_date":
        raise ErreurRegle("Vous avez demandé une autre date : attendez la réponse du prestataire.")
    if devis.statut != "envoye":
        raise ErreurRegle("Ce devis n'attend pas votre réponse.")
    _encore_valable(devis, maintenant)
    if mode_paiement not in modes_possibles(db, devis):
        raise ErreurRegle("Ce mode de paiement n'est pas accepté par ce prestataire.")
    demande = demande_de(db, devis)
    _verifier_dates(db, db.get_one(Prestataire, demande.prestataire_id), devis.travaux_debut, devis.travaux_fin, maintenant)
    t = totaux_du_devis(db, devis)
    if mode_paiement == "carte" and t.arrhes > 0:
        return paiements.commencer_devis(db, devis, "arrhes", t.arrhes, client, maintenant)
    _accepte(db, devis, mode_paiement, maintenant)
    return None


def _accepte(db: Session, devis: Devis, mode_paiement: str, maintenant: datetime) -> None:
    """Accepté : les jours des travaux sont bloqués dans l'agenda du prestataire (« Travaux D-2026-0002 »)."""
    demande = demande_de(db, devis)
    de, a = _limites(devis.travaux_debut, devis.travaux_fin)
    blocage = Blocage(prestataire_id=demande.prestataire_id, metier_id=demande.metier_id,
                      debut=de, fin=a, motif=f"Travaux {numero(devis)}", cree_le=maintenant)
    db.add(blocage)
    db.flush()
    devis.blocage_id = blocage.id
    devis.statut, devis.statut_change_le, devis.accepte_le, devis.mode_paiement = "accepte", maintenant, maintenant, mode_paiement
    _noter(db, demande.client_id, "accepter_devis", "devis", devis.id, maintenant, mode_paiement=mode_paiement)
    t = totaux_du_devis(db, devis)
    paye = f" Arrhes payées : {euros(t.arrhes)}." if mode_paiement == "carte" and t.arrhes else ""
    _prevenir(db, demande, objet=f"rafals : devis {numero(devis)} accepté",
              prestataire=f"Le client a accepté le devis {numero(devis)} ({euros(t.ttc)}).{paye} Travaux du "
                          f"{jour(devis.travaux_debut)} au {jour(devis.travaux_fin)} (jours bloqués dans votre agenda).",
              client=f"Vous avez accepté le devis {numero(devis)} ({euros(t.ttc)}).{paye}")


def apres_paiement(db: Session, devis: Devis, paiement: Paiement, maintenant: datetime) -> bool:
    """Stripe confirme les arrhes (→ devis accepté) ou le solde (→ devis payé). False : trop tard (devis expiré,
    refusé…), le paiement sera remboursé en entier."""
    if paiement.sorte == "arrhes":
        if devis.statut != "envoye" or aujourd_hui(maintenant) > devis.valable_jusqu_au:
            return False
        _accepte(db, devis, "carte", maintenant)
        return True
    if devis.statut != "termine":
        return False
    _paye(db, devis, maintenant)
    return True


def _paye(db: Session, devis: Devis, maintenant: datetime, moyen_direct: str | None = None) -> None:
    devis.statut, devis.statut_change_le, devis.paye_le, devis.moyen_direct = "paye", maintenant, maintenant, moyen_direct
    demande = demande_de(db, devis)
    _noter(db, demande.client_id, "payer_devis", "devis", devis.id, maintenant, moyen=moyen_direct or "carte")
    _prevenir(db, demande, objet=f"rafals : devis {numero(devis)} payé",
              prestataire=f"Le devis {numero(devis)} est entièrement payé.",
              client=f"Le devis {numero(devis)} est entièrement payé. Merci !")


# ---------- Travaux terminés, solde ----------


def terminer(db: Session, prestataire: Prestataire, devis: Devis, maintenant: datetime) -> Devis:
    """[Travail terminé] : le client vérifie puis paie le solde (par carte), ou le règle directement."""
    if devis.statut != "accepte":
        raise ErreurRegle("Seul un devis accepté peut être déclaré terminé.")
    if aujourd_hui(maintenant) < devis.travaux_debut:
        raise ErreurRegle(f"Vous pourrez déclarer le travail terminé à partir du {jour(devis.travaux_debut)}.")
    devis.statut, devis.statut_change_le, devis.termine_le = "termine", maintenant, maintenant
    _noter(db, prestataire.compte_id, "terminer_devis", "devis", devis.id, maintenant)
    t = totaux_du_devis(db, devis)
    if devis.mode_paiement == "carte" and t.solde == 0:  # tout était payé en arrhes
        _paye(db, devis, maintenant)
        return devis
    suite = (f"Vérifiez le travail, puis payez le solde de {euros(t.solde)} sur rafals (« Mes devis »)."
             if devis.mode_paiement == "carte" else f"Réglez le montant restant directement à {prestataire.nom_affiche}.")
    _prevenir(db, demande_de(db, devis), objet=f"rafals : travaux terminés, devis {numero(devis)}",
              client=f"{prestataire.nom_affiche} a terminé : « {_titre(db, demande_de(db, devis))} ». {suite} En cas de "
                     "souci, cliquez [Signaler un problème].")
    return devis


def payer_solde(db: Session, client: Compte, devis: Devis, maintenant: datetime) -> str:
    """Renvoie la page de paiement de Stripe pour le solde. Ex. 1 200 € - 360 € d'arrhes = 840 €."""
    if devis.statut != "termine" or devis.mode_paiement != "carte":
        raise ErreurRegle("Il n'y a pas de solde à payer par carte sur ce devis.")
    return paiements.commencer_devis(db, devis, "solde", totaux_du_devis(db, devis).solde, client, maintenant)


def paye_en_direct(db: Session, prestataire: Prestataire, devis: Devis, moyen: str, maintenant: datetime) -> Devis:
    """[Payé] : le prestataire a reçu l'argent hors de rafals (espèces, chèque, virement) ; rafals ne touche rien."""
    if devis.mode_paiement != "direct" or devis.statut not in ("accepte", "termine"):
        raise ErreurRegle("Ce devis ne se paie pas en direct, ou il est déjà payé.")
    if moyen not in ("especes", "cheque", "virement"):
        raise ErreurRegle("Choisissez comment vous avez été payé : espèces, chèque ou virement.")
    if devis.termine_le is None:
        devis.termine_le = maintenant
    _paye(db, devis, maintenant, moyen)
    from app.services import factures  # (import ici : factures dépend de ce module)

    factures.pour_devis_en_direct(db, devis, maintenant)  # la facture du total, « Payé par chèque »
    return devis


def signaler_probleme(db: Session, client: Compte, devis: Devis, texte: str, maintenant: datetime) -> Devis:
    """Ex. « Le muret penche de 5 cm » : l'administrateur regarde."""
    if devis.statut not in ("accepte", "termine"):
        raise ErreurRegle("On ne peut signaler un problème que sur des travaux acceptés, avant le paiement final.")
    if devis.probleme is not None:
        raise ErreurRegle("Vous avez déjà signalé un problème : l'administrateur va le regarder.")
    texte = (texte or "").strip()
    if len(texte) < 10:
        raise ErreurRegle("Décrivez le problème (ex. « Le muret penche de 5 cm »).")
    devis.probleme, devis.probleme_le = texte[:1000], maintenant
    _noter(db, client.id, "signaler_probleme_devis", "devis", devis.id, maintenant)
    _prevenir(db, demande_de(db, devis), objet=f"rafals : problème signalé, devis {numero(devis)}",
              prestataire=f"Le client signale un problème sur le devis {numero(devis)} : « {devis.probleme} ». "
                          "L'administrateur de rafals va regarder.")
    return devis


def problemes_a_traiter(db: Session) -> list[Devis]:
    return list(db.scalars(select(Devis).where(Devis.probleme_le.is_not(None), Devis.probleme_traite_le.is_(None))
                           .order_by(Devis.probleme_le)))


def traiter_probleme(db: Session, administrateur: Compte, devis_id: int, maintenant: datetime) -> Devis:
    devis = db.get(Devis, devis_id)
    if devis is None or devis.probleme is None:
        raise ErreurRegle("Aucun problème à traiter sur ce devis.", 404)
    if devis.probleme_traite_le is not None:
        raise ErreurRegle("Ce problème est déjà traité.")
    devis.probleme_traite_le = maintenant
    _noter(db, administrateur.id, "traiter_probleme_devis", "devis", devis.id, maintenant)
    return devis


# ---------- Annuler ----------


def _liberer_jours(db: Session, devis: Devis) -> None:
    """Les jours des travaux redeviennent libres dans l'agenda."""
    if devis.blocage_id is not None:
        blocage = db.get_one(Blocage, devis.blocage_id)
        devis.blocage_id = None
        db.flush()
        db.delete(blocage)


def annuler_par_client(db: Session, client: Compte, devis: Devis, maintenant: datetime) -> Devis:
    """Le prestataire garde les arrhes ; le client ne doit rien de plus (RM-DEVIS)."""
    if devis.statut != "accepte":
        raise ErreurRegle("Seul un devis accepté, pas encore terminé, peut être annulé.")
    devis.statut, devis.statut_change_le = "annule_client", maintenant
    _liberer_jours(db, devis)
    _noter(db, client.id, "annuler_devis_client", "devis", devis.id, maintenant)
    _prevenir(db, demande_de(db, devis), objet=f"rafals : devis {numero(devis)} annulé par le client",
              prestataire=f"Le client a annulé le devis {numero(devis)}. Vous gardez les arrhes ; les jours des travaux "
                          "sont de nouveau libres.")
    return devis


def annuler_par_prestataire(db: Session, prestataire: Prestataire, devis: Devis, motif: str, maintenant: datetime) -> Devis:
    """Motif obligatoire ; arrhes payées par carte rendues en entier au client (tâche des paiements)."""
    motif = (motif or "").strip()
    if not motif:
        raise ErreurRegle("Écrivez le motif : il est envoyé au client.")
    if devis.statut != "accepte":
        raise ErreurRegle("Seul un devis accepté, pas encore terminé, peut être annulé.")
    devis.statut, devis.statut_change_le, devis.message = "annule_prestataire", maintenant, motif[:500]
    _liberer_jours(db, devis)
    _noter(db, prestataire.compte_id, "annuler_devis_prestataire", "devis", devis.id, maintenant)
    rendues = " Vos arrhes vous sont rendues en entier." if devis.mode_paiement == "carte" and totaux_du_devis(db, devis).arrhes else ""
    _prevenir(db, demande_de(db, devis), objet=f"rafals : devis {numero(devis)} annulé",
              client=f"{prestataire.nom_affiche} a annulé le devis {numero(devis)}. Motif : « {motif} ».{rendues}")
    return devis


# ---------- Tâche automatique : expirations, relances du solde ----------


def traiter(db: Session, maintenant: datetime) -> dict[str, int]:
    """Lancée toutes les heures : devis sans réponse après « Valable jusqu'au » → expirés ; client qui n'a pas payé le
    solde 3 jours, puis 10 jours après les travaux → rappel."""
    compte = {"expires": 0, "relances": 0}
    for devis in db.scalars(select(Devis).where(Devis.statut.in_(EN_COURS), Devis.valable_jusqu_au < aujourd_hui(maintenant))):
        devis.statut, devis.statut_change_le = "expire", maintenant
        _noter(db, None, "expirer_devis", "devis", devis.id, maintenant)
        _prevenir(db, demande_de(db, devis), objet=f"rafals : devis {numero(devis)} expiré",
                  client=f"Le devis {numero(devis)} a expiré le {jour(devis.valable_jusqu_au)} : demandez-en un nouveau "
                         "si vous êtes toujours intéressé.")
        compte["expires"] += 1
    heure = timedelta(hours=1)
    for devis in db.scalars(select(Devis).where(Devis.statut == "termine", Devis.mode_paiement == "carte")):
        attente = maintenant - (devis.termine_le or maintenant)
        if any(delai <= attente < delai + heure for delai in reglages.DEVIS_RELANCES_SOLDE):
            _prevenir(db, demande_de(db, devis), objet=f"rafals : rappel, solde du devis {numero(devis)}",
                      client=f"Rappel : le solde du devis {numero(devis)} ({euros(totaux_du_devis(db, devis).solde)}) "
                             "reste à payer sur rafals (« Mes devis »). En cas de souci, cliquez [Signaler un problème].")
            compte["relances"] += 1
    return compte
