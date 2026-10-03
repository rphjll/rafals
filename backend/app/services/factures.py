"""Factures : créées toutes seules par rafals au nom du prestataire (mandat de facturation), avoirs, facture mensuelle
de la commission de rafals. Règles : .doc/regles-metier/RM-FACTURES.md (validé par Raphael le 02/10/2026), MLD 5.5.
Une facture n'est jamais modifiée ni effacée : tout ce qui y est écrit est recopié et figé à l'émission ; une erreur
ou un remboursement se corrige par un avoir (une facture « en moins »)."""

import logging
from dataclasses import dataclass
from datetime import date, datetime

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app import config, reglages
from app.modeles.annonces import Annonce, Local
from app.modeles.clients import Adresse
from app.modeles.comptes import Compte
from app.modeles.devis import DemandeDevis, Devis
from app.modeles.factures import Facture, LigneFacture
from app.modeles.paiements import Paiement
from app.modeles.prestataires import Commune, Prestataire
from app.modeles.rendez_vous import RendezVous
from app.services import devis as service_devis
from app.services import journal
from app.services import rendez_vous_communs as communs
from app.services.erreurs import ErreurRegle

journal_serveur = logging.getLogger("rafals")
PARIS = reglages.FUSEAU_AFFICHAGE
MOIS = ("janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre")
MOYENS = {"carte": "carte", "especes": "espèces", "cheque": "chèque", "virement": "virement"}


@dataclass
class Ligne:
    libelle: str
    quantite_centiemes: int
    prix_unitaire_centimes: int  # hors taxe si TVA ; négatif pour des arrhes déjà payées ou un avoir
    tva_pour_mille: int | None = None


def numero(facture: Facture) -> str:
    """« F-2026-0001 » (prestataire : ventes et avoirs) ; « R-2026-0001 » (commission de rafals)"""
    return f"{'R' if facture.sorte == 'commission' else 'F'}-{facture.annee}-{facture.numero:04d}"


def lignes_de(db: Session, facture: Facture) -> list[LigneFacture]:
    return list(db.scalars(select(LigneFacture).where(LigneFacture.facture_id == facture.id).order_by(LigneFacture.ordre)))


def totaux(db: Session, facture: Facture) -> service_devis.Totaux:
    """Hors taxe, TVA, total : calculés à partir des lignes figées (même calcul que les devis)."""
    return service_devis.totaux(lignes_de(db, facture), 0)


# ---------- Ce qui est figé sur la facture ----------


def _adresse(db: Session, ligne: str, complement: str | None, code_postal: str, commune_id: int) -> str:
    suite = f", {complement}" if complement else ""
    return f"{ligne}{suite}, {code_postal} {db.get_one(Commune, commune_id).nom}"


def _vendeur(db: Session, prestataire: Prestataire) -> tuple[str, str, str]:
    """Nom (la personne, et son enseigne si elle est différente), SIRET, adresse (son local, sinon sa commune)."""
    compte = db.get_one(Compte, prestataire.compte_id)
    personne = f"{compte.prenom} {compte.nom}".strip()
    nom = personne if prestataire.nom_affiche.strip().lower() == personne.lower() else f"{personne} — {prestataire.nom_affiche}"
    local = db.scalar(select(Local).where(Local.prestataire_id == prestataire.id))
    if local is not None:
        adresse = _adresse(db, local.ligne, local.complement, local.code_postal, local.commune_id)
    else:
        commune = db.get_one(Commune, prestataire.commune_id)
        adresse = f"{(commune.codes_postaux or [''])[0]} {commune.nom}".strip()
    return nom, prestataire.siret or "", adresse


def _acheteur(db: Session, client: Compte) -> tuple[str, str | None]:
    a = db.scalar(select(Adresse).where(Adresse.compte_id == client.id))
    return f"{client.prenom} {client.nom}".strip(), _adresse(db, a.ligne, a.complement, a.code_postal, a.commune_id) if a else None


def _numero_suivant(db: Session, prestataire: Prestataire | None, annee: int) -> int:
    """Numéros qui se suivent, sans trou ni doublon : un verrou pendant qu'on prend le suivant."""
    if prestataire is not None:
        db.scalar(select(Prestataire.id).where(Prestataire.id == prestataire.id).with_for_update())
        requete = select(func.max(Facture.numero)).where(Facture.prestataire_id == prestataire.id, Facture.annee == annee,
                                                         Facture.sorte != "commission")
    else:
        db.execute(text("SELECT pg_advisory_xact_lock(550055)"))  # la suite R-… de rafals : une facture à la fois
        requete = select(func.max(Facture.numero)).where(Facture.annee == annee, Facture.sorte == "commission")
    return (db.scalar(requete) or 0) + 1


def _creer(db: Session, prestataire: Prestataire, *, sorte: str, objet: str, lignes: list[Ligne], maintenant: datetime,
           client: Compte | None = None, moyen: str | None = None, avec_tva: bool = False, rendez_vous_id: int | None = None,
           devis_id: int | None = None, paiement_id: int | None = None, avoir_de: Facture | None = None) -> Facture:
    annee = maintenant.astimezone(PARIS).year
    if sorte == "commission":
        vendeur = (config.RAFALS_NOM, config.RAFALS_SIRET, config.RAFALS_ADRESSE)
        nom, _, adresse = _vendeur(db, prestataire)
        acheteur: tuple[str, str | None] = (nom, adresse)
    elif avoir_de is not None:  # un avoir reprend exactement ce qui était figé sur la facture
        vendeur = (avoir_de.vendeur_nom, avoir_de.vendeur_siret, avoir_de.vendeur_adresse)
        acheteur = (avoir_de.acheteur_nom, avoir_de.acheteur_adresse)
    else:
        assert client is not None
        vendeur, acheteur = _vendeur(db, prestataire), _acheteur(db, client)
    facture = Facture(
        prestataire_id=prestataire.id, client_id=client.id if client else None, rendez_vous_id=rendez_vous_id,
        devis_id=devis_id, paiement_id=paiement_id, avoir_de_id=avoir_de.id if avoir_de else None, sorte=sorte, annee=annee,
        numero=_numero_suivant(db, None if sorte == "commission" else prestataire, annee), emise_le=maintenant, objet=objet,
        moyen_paiement=moyen, vendeur_nom=vendeur[0], vendeur_siret=vendeur[1], vendeur_adresse=vendeur[2],
        acheteur_nom=acheteur[0], acheteur_adresse=acheteur[1],
        mention_tva=None if avec_tva else reglages.FACTURE_MENTION_SANS_TVA,
    )
    db.add(facture)
    db.flush()
    for rang, ligne in enumerate(lignes, start=1):
        db.add(LigneFacture(facture_id=facture.id, ordre=rang, libelle=ligne.libelle[:200],
                            quantite_centiemes=ligne.quantite_centiemes, prix_unitaire_centimes=ligne.prix_unitaire_centimes,
                            tva_pour_mille=ligne.tva_pour_mille if avec_tva else None))
    db.flush()
    journal.noter(db, auteur_id=None, action=f"emettre_facture_{sorte}", table_cible="facture", ligne_id=facture.id,
                  apres={"numero": numero(facture), "ttc_centimes": totaux(db, facture).ttc}, maintenant=maintenant)
    return facture


# ---------- Ventes ----------


def _ligne_ttc(libelle: str, ttc: int, avec_tva: bool) -> Ligne:
    """Une ligne pour un prix connu toutes taxes comprises (rendez-vous). Avec TVA : le hors taxe est retrouvé à
    partir du prix payé (taux des réglages, ⚠️ à confirmer par un comptable)."""
    if not avec_tva:
        return Ligne(libelle, 100, ttc)
    taux = reglages.FACTURE_TVA_RENDEZ_VOUS_POUR_MILLE
    return Ligne(libelle, 100, (ttc * 1000 + (1000 + taux) // 2) // (1000 + taux), taux)


def _vente_rendez_vous(db: Session, rdv: RendezVous, moyen: str, maintenant: datetime, paiement_id: int | None = None) -> Facture:
    prestataire = db.get_one(Prestataire, rdv.prestataire_id)
    libelle = rdv.titre + (f" · {rdv.heures} h" if rdv.heures else "")
    return _creer(db, prestataire, sorte="vente", objet=f"{rdv.titre}, {communs.texte_moment(rdv.debut)}",
                  lignes=[_ligne_ttc(libelle, rdv.prix_centimes or 0, prestataire.facture_tva)], maintenant=maintenant,
                  client=db.get_one(Compte, rdv.client_id), moyen=moyen, avec_tva=prestataire.facture_tva,
                  rendez_vous_id=rdv.id, paiement_id=paiement_id)


def _lignes_du_devis(db: Session, devis: Devis) -> list[Ligne]:
    return [Ligne(ligne.libelle, ligne.quantite_centiemes, ligne.prix_unitaire_centimes, ligne.tva_pour_mille)
            for ligne in service_devis.lignes_de(db, devis)]


def _lignes_arrhes(db: Session, devis: Devis, signe: int = 1) -> list[Ligne]:
    """Les arrhes : un pourcentage du devis ; avec TVA, une ligne par taux (comme le devis, ⚠️ à confirmer par un
    comptable). signe = -1 : « arrhes déjà payées », retirées de la facture de solde."""
    quoi = "Arrhes" if signe == 1 else "Arrhes déjà payées"
    base = f"{quoi} ({devis.arrhes_pourcent} % du devis {service_devis.numero(devis)})"
    par_taux: dict[int | None, int] = {}
    for ligne in service_devis.lignes_de(db, devis):
        montant = service_devis.montant_ligne(ligne.quantite_centiemes, ligne.prix_unitaire_centimes)
        par_taux[ligne.tva_pour_mille] = par_taux.get(ligne.tva_pour_mille, 0) + montant
    return [Ligne(base if taux is None else f"{base}, TVA {str(taux / 10).replace('.', ',').removesuffix(',0')} %",
                  100, signe * ((montant * devis.arrhes_pourcent + 50) // 100), taux) for taux, montant in par_taux.items()]


def _parties_du_devis(db: Session, devis: Devis) -> tuple[Prestataire, Compte, str]:
    demande = db.get_one(DemandeDevis, devis.demande_devis_id)
    return (db.get_one(Prestataire, demande.prestataire_id), db.get_one(Compte, demande.client_id),
            db.get_one(Annonce, demande.annonce_id).titre)


def pour_paiement(db: Session, paiement: Paiement, maintenant: datetime) -> Facture | None:
    """Après un paiement par carte : la facture du rendez-vous, la facture d'arrhes ou la facture de solde d'un devis.
    Ex. Paul paie 50 € à Léa → F-2026-0001 « Coupe femme — 50,00 € — TVA non applicable, art. 293 B du CGI »."""
    deja = db.scalar(select(Facture).where(Facture.paiement_id == paiement.id, Facture.sorte == "vente"))
    if deja is not None:
        return deja
    if paiement.rendez_vous_id is not None:
        return _vente_rendez_vous(db, db.get_one(RendezVous, paiement.rendez_vous_id), "carte", maintenant, paiement.id)
    devis = db.get_one(Devis, paiement.devis_id)
    prestataire, client, titre = _parties_du_devis(db, devis)
    communs_devis = {"sorte": "vente", "maintenant": maintenant, "client": client, "moyen": "carte",
                     "avec_tva": devis.facture_tva, "devis_id": devis.id, "paiement_id": paiement.id}
    if paiement.sorte == "arrhes":
        return _creer(db, prestataire, objet=f"Arrhes sur le devis {service_devis.numero(devis)} — {titre}",
                      lignes=_lignes_arrhes(db, devis), **communs_devis)
    # Solde : les lignes du devis, moins les arrhes déjà payées (obligation légale de les rappeler)
    lignes = _lignes_du_devis(db, devis) + (_lignes_arrhes(db, devis, -1) if devis.arrhes_pourcent else [])
    return _creer(db, prestataire, objet=f"Solde du devis {service_devis.numero(devis)} — {titre}", lignes=lignes,
                  **communs_devis)


def pour_devis_en_direct(db: Session, devis: Devis, maintenant: datetime) -> Facture:
    """[Payé] sur un devis payé hors de rafals : une facture pour le total, avec le moyen de paiement."""
    prestataire, client, titre = _parties_du_devis(db, devis)
    return _creer(db, prestataire, sorte="vente", objet=f"Devis {service_devis.numero(devis)} — {titre}",
                  lignes=_lignes_du_devis(db, devis), maintenant=maintenant, client=client, moyen=devis.moyen_direct,
                  avec_tva=devis.facture_tva, devis_id=devis.id)


def encaisser_rendez_vous(db: Session, prestataire: Prestataire, rdv: RendezVous, moyen: str, maintenant: datetime) -> Facture:
    """[Payé] sur un rendez-vous payé en direct (espèces…) par un prestataire avec SIRET → facture « Payé en espèces »."""
    if prestataire.siret_statut != "verifie":
        raise ErreurRegle("Les factures demandent un SIRET vérifié : sans lui, rafals ne fait pas de facture.")
    if rdv.mode_paiement != "especes" or rdv.statut != "confirme":
        raise ErreurRegle("Ce rendez-vous ne se paie pas en direct, ou il n'est pas confirmé.")
    if rdv.paye_direct_le is not None:
        raise ErreurRegle("Ce rendez-vous est déjà noté comme payé.")
    if maintenant < rdv.debut:
        raise ErreurRegle("Vous pourrez noter le paiement à partir de l'heure du rendez-vous.")
    if moyen not in reglages.FACTURE_MOYENS_DIRECTS:
        raise ErreurRegle("Choisissez comment vous avez été payé : espèces, chèque ou virement.")
    if not rdv.prix_centimes:
        raise ErreurRegle("Ce rendez-vous n'a pas de prix.")
    rdv.paye_direct_le, rdv.paye_direct_moyen = maintenant, moyen
    communs.noter(db, prestataire.compte_id, "encaisser_rendez_vous", rdv, maintenant, moyen=moyen)
    return _vente_rendez_vous(db, rdv, moyen, maintenant)


# ---------- Avoirs ----------


def avoir_pour_remboursement(db: Session, paiement: Paiement, maintenant: datetime) -> Facture | None:
    """Un remboursement → un avoir du montant rendu, sur la facture du paiement. Remboursé en entier : chaque ligne
    en négatif ; en partie (le client a annulé à temps : 49,00 € sur 50,00 €) : une ligne du montant rendu."""
    facture = db.scalar(select(Facture).where(Facture.paiement_id == paiement.id, Facture.sorte == "vente"))
    if facture is None or db.scalar(select(Facture.id).where(Facture.avoir_de_id == facture.id)) is not None:
        return None
    avec_tva = facture.mention_tva is None
    rendu = paiement.rembourse_centimes or 0
    if rendu >= paiement.montant_centimes:
        lignes = [Ligne(f"{ligne.libelle} (remboursement)", ligne.quantite_centiemes, -ligne.prix_unitaire_centimes,
                        ligne.tva_pour_mille) for ligne in lignes_de(db, facture)]
    else:
        ligne = _ligne_ttc("Remboursement (frais de paiement non rendus)", rendu, avec_tva)
        lignes = [Ligne(ligne.libelle, 100, -ligne.prix_unitaire_centimes, ligne.tva_pour_mille)]
    return _creer(db, db.get_one(Prestataire, facture.prestataire_id), sorte="avoir",
                  objet=f"Avoir sur la facture {numero(facture)}", lignes=lignes, maintenant=maintenant,
                  client=db.get_one(Compte, facture.client_id), moyen=facture.moyen_paiement, avec_tva=avec_tva,
                  rendez_vous_id=facture.rendez_vous_id, devis_id=facture.devis_id, paiement_id=paiement.id, avoir_de=facture)


# ---------- Commission de rafals : une facture par mois et par prestataire ----------


def rafals_peut_facturer() -> bool:
    return bool(config.RAFALS_NOM and config.RAFALS_SIRET and config.RAFALS_ADRESSE)


def _mois_passe(maintenant: datetime) -> tuple[date, date]:
    """Le 1er du mois passé et le 1er de ce mois (heure de Paris). Ex. le 03/11/2026 → 01/10/2026 et 01/11/2026."""
    ce_mois = maintenant.astimezone(PARIS).date().replace(day=1)
    passe = (ce_mois.replace(year=ce_mois.year - 1, month=12) if ce_mois.month == 1 else ce_mois.replace(month=ce_mois.month - 1))
    return passe, ce_mois


def facturer_les_commissions(db: Session, maintenant: datetime) -> dict[str, int]:
    """Lancé une fois par jour : les commissions du mois passé, une facture R-… par prestataire payé par carte
    (faite une seule fois). Ex. le 01/11 : « Commissions d'octobre 2026 — 12 paiements par carte — 30,00 € ».
    Tant que rafals n'a pas son nom et son SIRET dans le fichier .env, rien n'est facturé."""
    compte = {"factures": 0}
    if not rafals_peut_facturer():
        return compte
    debut, fin = _mois_passe(maintenant)
    de = datetime.combine(debut, datetime.min.time(), tzinfo=PARIS)
    a = datetime.combine(fin, datetime.min.time(), tzinfo=PARIS)
    mois = MOIS[debut.month - 1]
    objet = f"Commissions {'d' + chr(39) if mois[0] in 'ao' else 'de '}{mois} {debut.year}"  # « d'octobre », « de mars »
    # Paiements par carte du mois, gardés (un paiement remboursé a rendu sa commission)
    from app.services import paiements  # (import ici : paiements appelle ce module)

    par_prestataire: dict[int, list[Paiement]] = {}
    lignes = db.scalars(select(Paiement).where(Paiement.statut.in_(("paye", "verse")), Paiement.paye_le >= de, Paiement.paye_le < a))
    for paiement in lignes:
        par_prestataire.setdefault(paiements.sujet(db, paiement).prestataire.id, []).append(paiement)
    for prestataire_id, payes in par_prestataire.items():
        total = sum(p.commission_centimes for p in payes)
        deja = db.scalar(select(Facture.id).where(Facture.prestataire_id == prestataire_id, Facture.sorte == "commission",
                                                  Facture.objet == objet))
        if deja is not None or total <= 0:
            continue
        pluriel = "s" if len(payes) > 1 else ""
        _creer(db, db.get_one(Prestataire, prestataire_id), sorte="commission", objet=objet, maintenant=maintenant,
               lignes=[Ligne(f"Commission de {reglages.COMMISSION_POURCENT} % sur {len(payes)} paiement{pluriel} par carte",
                             100, total)])
        compte["factures"] += 1
    return compte


# ---------- Qui voit quoi ----------


def du_client(db: Session, client_id: int) -> list[Facture]:
    return list(db.scalars(select(Facture).where(Facture.client_id == client_id).order_by(Facture.id.desc())))


def du_prestataire(db: Session, prestataire_id: int) -> list[Facture]:
    return list(db.scalars(select(Facture).where(Facture.prestataire_id == prestataire_id).order_by(Facture.id.desc())))


def visible_par(db: Session, compte: Compte, facture_id: int) -> Facture:
    """Le client de la facture, le prestataire concerné, ou un administrateur."""
    facture = db.get(Facture, facture_id)
    if facture is not None and not compte.est_administrateur and facture.client_id != compte.id:
        if db.get_one(Prestataire, facture.prestataire_id).compte_id != compte.id:
            facture = None
    if facture is None:
        raise ErreurRegle("Cette facture n'existe pas.", 404)
    return facture


def moyen_lisible(facture: Facture) -> str | None:
    return MOYENS.get(facture.moyen_paiement or "")


# ---------- Le PDF ----------


def _siret_lisible(siret: str) -> str:
    """« 443 061 841 00047 »"""
    return f"{siret[:3]} {siret[3:6]} {siret[6:9]} {siret[9:]}" if len(siret) == 14 else siret


def _nombre(centiemes: int) -> str:
    """4000 → « 40 » ; 250 → « 2,5 »"""
    return f"{centiemes / 100:g}".replace(".", ",")


def pdf(db: Session, facture: Facture) -> bytes:
    """La facture en PDF (une page A4), fabriquée à partir des rubriques figées : en-tête, vendeur, acheteur, lignes,
    totaux, mention de TVA, paiement, et la phrase du mandat de facturation."""
    from app.services import paiements, pdf_facture

    euros = paiements.euros
    page = pdf_facture.Page()
    droite = pdf_facture.LARGEUR - pdf_facture.MARGE
    titre = {"vente": "FACTURE", "avoir": "AVOIR", "commission": "FACTURE"}[facture.sorte]
    page.ligne(f"{titre} {numero(facture)}", taille=18, police="gras")
    page.descendre(4)
    page.ligne(f"Date : {facture.emise_le.astimezone(PARIS):%d/%m/%Y}")
    page.descendre(10)

    page.ligne("Vendeur", police="gras")
    page.ligne(facture.vendeur_nom)
    page.ligne(facture.vendeur_adresse)
    page.ligne(f"SIRET : {_siret_lisible(facture.vendeur_siret)}")
    page.descendre(8)
    page.ligne("Client", police="gras")
    page.ligne(facture.acheteur_nom)
    if facture.acheteur_adresse:
        page.ligne(facture.acheteur_adresse)
    page.descendre(8)
    for morceau in pdf_facture.couper(f"Objet : {facture.objet}", 90):
        page.ligne(morceau, police="gras")
    page.descendre(10)

    # Le tableau des lignes : désignation à gauche, chiffres alignés à droite
    avec_tva = facture.mention_tva is None
    colonnes = {"quantite": 330, "prix": 420, "tva": 465, "montant": droite}
    page.ecrire("Désignation", police="gras")
    page.ecrire("Quantité", x=colonnes["quantite"] - 42, police="gras")
    page.ecrire("Prix unit. HT" if avec_tva else "Prix unitaire", x=colonnes["prix"] - 62, police="gras")
    if avec_tva:
        page.ecrire("TVA", x=colonnes["tva"] - 20, police="gras")
    page.ecrire("Montant HT" if avec_tva else "Montant", x=colonnes["montant"] - 58, police="gras")
    page.descendre()
    page.trait()
    page.descendre(4)
    for ligne in lignes_de(db, facture):
        morceaux = pdf_facture.couper(ligne.libelle, 46)
        page.ecrire(morceaux[0])
        page.ecrire(_nombre(ligne.quantite_centiemes), droite=colonnes["quantite"])
        page.ecrire(euros(abs(ligne.prix_unitaire_centimes)) if ligne.prix_unitaire_centimes >= 0
                    else f"-{euros(-ligne.prix_unitaire_centimes)}", droite=colonnes["prix"])
        if avec_tva and ligne.tva_pour_mille:
            page.ecrire(f"{_nombre(ligne.tva_pour_mille * 10)} %", droite=colonnes["tva"], taille=9)
        montant = service_devis.montant_ligne(ligne.quantite_centiemes, abs(ligne.prix_unitaire_centimes))
        page.ecrire(euros(montant) if ligne.prix_unitaire_centimes >= 0 else f"-{euros(montant)}", droite=colonnes["montant"])
        page.descendre()
        for suite in morceaux[1:]:
            page.ligne(suite)
    page.trait()
    page.descendre(6)

    t = totaux(db, facture)

    def somme(centimes: int) -> str:
        return euros(centimes) if centimes >= 0 else f"-{euros(-centimes)}"

    if avec_tva:
        page.ecrire("Total HT", x=colonnes["prix"] - 62)
        page.ecrire(somme(t.ht), droite=droite)
        page.descendre()
        page.ecrire("TVA", x=colonnes["prix"] - 62)
        page.ecrire(somme(t.tva), droite=droite)
        page.descendre()
    page.ecrire("Total TTC" if avec_tva else "Total", x=colonnes["prix"] - 62, police="gras", taille=12)
    page.ecrire(somme(t.ttc), droite=droite, taille=12)
    page.descendre(22)

    if facture.mention_tva:
        page.ligne(facture.mention_tva)
    if facture.sorte == "commission":
        page.ligne("Commission déjà prélevée sur les paiements par carte : rien à régler.")
    elif facture.moyen_paiement:
        verbe = "Remboursé" if facture.sorte == "avoir" else "Payé"
        page.ligne(f"{verbe} par {MOYENS[facture.moyen_paiement]} le {facture.emise_le.astimezone(PARIS):%d/%m/%Y}.")
    if facture.sorte != "commission":
        page.descendre(10)
        for morceau in pdf_facture.couper(
            f"Facture établie par rafals au nom et pour le compte de {facture.vendeur_nom} (mandat de facturation).", 100,
        ):
            page.ligne(morceau, taille=8)
    return pdf_facture.assembler(page, f"{titre} {numero(facture)}")
