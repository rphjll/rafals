"""Adresses des devis (écrans au lot 5.4). Règles : RM-DEVIS.md."""

from datetime import date, datetime
from typing import Literal

from fastapi import APIRouter, Response, UploadFile
from pydantic import BaseModel
from sqlalchemy import select

from app import reglages
from app.modeles.comptes import Compte
from app.modeles.devis import DemandeDevis, Devis
from app.modeles.fichiers import Fichier
from app.modeles.metiers import Metier
from app.modeles.prestataires import Commune, Prestataire
from app.routes.dependances import Administrateur, Base, CompteConnecte, maintenant
from app.routes.prestataires import mon_profil_ou_404
from app.services import devis as service
from app.services import journal, paiements, stockage
from app.services.erreurs import ErreurRegle

routeur = APIRouter(prefix="/api")


# ---------- Ce qui arrive ----------


class NouvelleDemande(BaseModel):
    prestataire_id: int
    metier_id: int
    texte: str


class Motif(BaseModel):
    motif: str | None = None


class Texte(BaseModel):
    texte: str


class LigneDemandee(BaseModel):
    libelle: str
    quantite_centiemes: int
    prix_unitaire_centimes: int
    tva_pour_mille: int | None = None


class DevisDemande(BaseModel):
    lignes: list[LigneDemandee]
    arrhes_pourcent: int
    travaux_debut: date
    travaux_fin: date
    valable_jusqu_au: date


class Dates(BaseModel):
    travaux_debut: date
    travaux_fin: date


class Acceptation(BaseModel):
    mode_paiement: Literal["carte", "direct"]


class PayeEnDirect(BaseModel):
    moyen: Literal["especes", "cheque", "virement"]


class ChoixTva(BaseModel):
    facture_tva: bool


# ---------- Ce que voient le client et le prestataire ----------


class LigneVisible(BaseModel):
    libelle: str
    quantite_centiemes: int
    prix_unitaire_centimes: int
    tva_pour_mille: int | None
    montant_centimes: int  # hors taxe si TVA


class DevisVisible(BaseModel):
    id: int
    numero: str  # « D-2026-0002 »
    statut: str  # envoye · autre_date · accepte · termine · paye · refuse · expire · annule_client · annule_prestataire
    facture_tva: bool
    mention_tva: str | None  # « TVA non applicable, art. 293 B du CGI » sans TVA
    lignes: list[LigneVisible]
    ht_centimes: int
    tva_centimes: int
    ttc_centimes: int
    arrhes_pourcent: int
    arrhes_centimes: int
    solde_centimes: int
    travaux_debut: date
    travaux_fin: date
    valable_jusqu_au: date
    mode_paiement: str | None
    modes_possibles: list[str]  # « carte », « direct »
    envoye_le: datetime
    accepte_le: datetime | None
    termine_le: datetime | None
    paye_le: datetime | None
    message: str | None
    probleme: str | None
    probleme_le: datetime | None
    moyen_direct: str | None
    arrhes_paiement: str | None  # statut du paiement des arrhes par carte (a_payer, paye, verse, rembourse…)
    solde_paiement: str | None


class DemandeVisible(BaseModel):
    id: int
    titre: str  # le métier concerné (« Maçon »)
    texte: str
    nombre_photos: int
    lieu: str | None  # « 8 allée des Pins, 33400 Talence »
    statut: str  # envoyee · devis_recu · declinee · annulee
    motif: str | None
    cree_le: datetime
    autre: dict  # le prestataire (vu par le client) ou le client (vu par le prestataire)
    devis: DevisVisible | None


def devis_visible(db: Base, devis: Devis) -> DevisVisible:
    lignes = service.lignes_de(db, devis)
    t = service.totaux(lignes, devis.arrhes_pourcent)
    arrhes, solde = paiements.du_devis(db, devis.id, "arrhes"), paiements.du_devis(db, devis.id, "solde")
    return DevisVisible(
        id=devis.id, numero=service.numero(devis), statut=devis.statut, facture_tva=devis.facture_tva,
        mention_tva=None if devis.facture_tva else reglages.DEVIS_MENTION_SANS_TVA,
        lignes=[LigneVisible(libelle=ligne.libelle, quantite_centiemes=ligne.quantite_centiemes,
                             prix_unitaire_centimes=ligne.prix_unitaire_centimes, tva_pour_mille=ligne.tva_pour_mille,
                             montant_centimes=service.montant_ligne(ligne.quantite_centiemes, ligne.prix_unitaire_centimes))
                for ligne in lignes],
        ht_centimes=t.ht, tva_centimes=t.tva, ttc_centimes=t.ttc, arrhes_pourcent=devis.arrhes_pourcent,
        arrhes_centimes=t.arrhes, solde_centimes=t.solde, travaux_debut=devis.travaux_debut, travaux_fin=devis.travaux_fin,
        valable_jusqu_au=devis.valable_jusqu_au, mode_paiement=devis.mode_paiement,
        modes_possibles=service.modes_possibles(db, devis), envoye_le=devis.envoye_le, accepte_le=devis.accepte_le,
        termine_le=devis.termine_le, paye_le=devis.paye_le, message=devis.message, probleme=devis.probleme,
        probleme_le=devis.probleme_le, moyen_direct=devis.moyen_direct,
        arrhes_paiement=arrhes.statut if arrhes else None, solde_paiement=solde.statut if solde else None,
    )


def demande_visible(db: Base, demande: DemandeDevis, *, cote: Literal["client", "prestataire"]) -> DemandeVisible:
    prestataire = db.get_one(Prestataire, demande.prestataire_id)
    client = db.get_one(Compte, demande.client_id)
    devis = service.devis_de(db, demande)
    accepte = devis is not None and devis.accepte_le is not None
    if cote == "client":
        # Le téléphone du prestataire, une fois le devis accepté (comme après une réservation confirmée)
        telephone = db.get_one(Compte, prestataire.compte_id).telephone if accepte else None
        autre = {"prestataire_id": prestataire.id, "nom": prestataire.nom_affiche, "telephone": telephone}
    else:
        autre = {"client_id": client.id, "nom": f"{client.prenom} {client.nom}", "telephone": client.telephone}
    lieu = None
    if demande.adresse_ligne:
        complement = f", {demande.adresse_complement}" if demande.adresse_complement else ""
        commune = db.get_one(Commune, demande.commune_id).nom if demande.commune_id else ""
        lieu = f"{demande.adresse_ligne}{complement}, {demande.code_postal} {commune}"
    return DemandeVisible(
        id=demande.id, titre=db.get_one(Metier, demande.metier_id).nom, texte=demande.texte,
        nombre_photos=len(service.photos_de(db, demande)), lieu=lieu, statut=demande.statut, motif=demande.motif,
        cree_le=demande.cree_le, autre=autre, devis=devis_visible(db, devis) if devis else None,
    )


class AvecPaiement(BaseModel):
    demande: DemandeVisible
    paiement_adresse: str | None = None  # la page de paiement de Stripe (arrhes ou solde)


class ProblemeAdministre(BaseModel):
    devis_id: int
    numero: str
    titre: str
    client: str
    prestataire: str
    probleme: str
    probleme_le: datetime


# ---------- Côté client ----------


@routeur.post("/devis/demandes", status_code=201)
def demander(donnees: NouvelleDemande, db: Base, compte: CompteConnecte) -> DemandeVisible:
    demande = service.demander(db, compte, donnees.prestataire_id, donnees.metier_id, donnees.texte, maintenant())
    db.commit()
    return demande_visible(db, demande, cote="client")


@routeur.post("/moi/demandes-devis/{demande_id}/photos")
async def ajouter_photo(demande_id: int, fichier: UploadFile, db: Base, compte: CompteConnecte) -> DemandeVisible:
    demande = service.demande_du_client(db, compte, demande_id)
    service.ajouter_photo(db, compte, demande, nom_fichier=fichier.filename or "photo", type_mime=fichier.content_type or "",
                          contenu=await fichier.read(), maintenant=maintenant())
    db.commit()
    return demande_visible(db, demande, cote="client")


@routeur.get("/demandes-devis/{demande_id}/photos/{ordre}")
def voir_photo(demande_id: int, ordre: int, db: Base, compte: CompteConnecte) -> Response:
    """Seulement le client qui a écrit la demande, et le prestataire qui l'a reçue."""
    demande = db.get(DemandeDevis, demande_id)
    prestataire = db.scalar(select(Prestataire).where(Prestataire.compte_id == compte.id))
    if demande is None or (demande.client_id != compte.id and (prestataire is None or prestataire.id != demande.prestataire_id)):
        raise ErreurRegle("Cette photo n'existe pas.", 404)
    photo = next((p for p in service.photos_de(db, demande) if p.ordre == ordre), None)
    if photo is None:
        raise ErreurRegle("Cette photo n'existe pas.", 404)
    fichier = db.get_one(Fichier, photo.fichier_id)
    return Response(content=stockage.lire(fichier.cle_stockage), media_type=fichier.type_mime)


@routeur.get("/moi/devis")
def mes_devis(db: Base, compte: CompteConnecte) -> list[DemandeVisible]:
    """Mes demandes de devis et leurs devis, les plus récentes d'abord."""
    lignes = db.scalars(select(DemandeDevis).where(DemandeDevis.client_id == compte.id).order_by(DemandeDevis.id.desc()))
    return [demande_visible(db, d, cote="client") for d in lignes]


def _client(db: Base, compte: Compte, devis_id: int) -> Devis:
    return service.devis_du_client(db, compte, devis_id)


def _apres(db: Base, devis: Devis, cote: Literal["client", "prestataire"], adresse: str | None = None) -> AvecPaiement:
    db.commit()
    return AvecPaiement(demande=demande_visible(db, service.demande_de(db, devis), cote=cote), paiement_adresse=adresse)


@routeur.post("/moi/demandes-devis/{demande_id}/annuler")
def annuler_demande(demande_id: int, db: Base, compte: CompteConnecte) -> DemandeVisible:
    demande = service.annuler_demande(db, compte, service.demande_du_client(db, compte, demande_id), maintenant())
    db.commit()
    return demande_visible(db, demande, cote="client")


@routeur.post("/moi/devis/{devis_id}/autre-date")
def autre_date(devis_id: int, donnees: Texte, db: Base, compte: CompteConnecte) -> AvecPaiement:
    return _apres(db, service.demander_autre_date(db, compte, _client(db, compte, devis_id), donnees.texte, maintenant()), "client")


@routeur.post("/moi/devis/{devis_id}/refuser")
def refuser(devis_id: int, donnees: Motif, db: Base, compte: CompteConnecte) -> AvecPaiement:
    return _apres(db, service.refuser(db, compte, _client(db, compte, devis_id), donnees.motif, maintenant()), "client")


@routeur.post("/moi/devis/{devis_id}/accepter")
def accepter(devis_id: int, donnees: Acceptation, db: Base, compte: CompteConnecte) -> AvecPaiement:
    """Par carte avec des arrhes : la réponse donne la page de paiement de Stripe (30 minutes pour payer)."""
    devis = _client(db, compte, devis_id)
    adresse = service.accepter(db, compte, devis, donnees.mode_paiement, maintenant())
    return _apres(db, devis, "client", adresse)


@routeur.post("/moi/devis/{devis_id}/payer-solde")
def payer_solde(devis_id: int, db: Base, compte: CompteConnecte) -> AvecPaiement:
    devis = _client(db, compte, devis_id)
    adresse = service.payer_solde(db, compte, devis, maintenant())
    return _apres(db, devis, "client", adresse)


@routeur.post("/moi/devis/{devis_id}/probleme")
def probleme(devis_id: int, donnees: Texte, db: Base, compte: CompteConnecte) -> AvecPaiement:
    return _apres(db, service.signaler_probleme(db, compte, _client(db, compte, devis_id), donnees.texte, maintenant()), "client")


@routeur.post("/moi/devis/{devis_id}/annuler")
def annuler_client(devis_id: int, db: Base, compte: CompteConnecte) -> AvecPaiement:
    return _apres(db, service.annuler_par_client(db, compte, _client(db, compte, devis_id), maintenant()), "client")


# ---------- Côté prestataire ----------


@routeur.get("/moi/prestataire/devis")
def devis_recus(db: Base, compte: CompteConnecte) -> list[DemandeVisible]:
    prestataire = mon_profil_ou_404(db, compte)
    lignes = db.scalars(select(DemandeDevis).where(DemandeDevis.prestataire_id == prestataire.id).order_by(DemandeDevis.id.desc()))
    return [demande_visible(db, d, cote="prestataire") for d in lignes]


@routeur.post("/moi/prestataire/demandes-devis/{demande_id}/decliner")
def decliner(demande_id: int, donnees: Motif, db: Base, compte: CompteConnecte) -> DemandeVisible:
    prestataire = mon_profil_ou_404(db, compte)
    demande = service.decliner(db, prestataire, service.demande_du_prestataire(db, prestataire, demande_id), donnees.motif,
                               maintenant())
    db.commit()
    return demande_visible(db, demande, cote="prestataire")


@routeur.post("/moi/prestataire/demandes-devis/{demande_id}/devis", status_code=201)
def envoyer(demande_id: int, donnees: DevisDemande, db: Base, compte: CompteConnecte) -> AvecPaiement:
    prestataire = mon_profil_ou_404(db, compte)
    demande = service.demande_du_prestataire(db, prestataire, demande_id)
    devis = service.envoyer(
        db, prestataire, demande, [service.Ligne(**ligne.model_dump()) for ligne in donnees.lignes],
        arrhes_pourcent=donnees.arrhes_pourcent, travaux_debut=donnees.travaux_debut, travaux_fin=donnees.travaux_fin,
        valable_jusqu_au=donnees.valable_jusqu_au, maintenant=maintenant(),
    )
    return _apres(db, devis, "prestataire")


def _prestataire(db: Base, compte: Compte, devis_id: int) -> tuple[Prestataire, Devis]:
    prestataire = mon_profil_ou_404(db, compte)
    return prestataire, service.devis_du_prestataire(db, prestataire, devis_id)


@routeur.post("/moi/prestataire/devis/{devis_id}/dates")
def changer_dates(devis_id: int, donnees: Dates, db: Base, compte: CompteConnecte) -> AvecPaiement:
    prestataire, devis = _prestataire(db, compte, devis_id)
    service.changer_dates(db, prestataire, devis, donnees.travaux_debut, donnees.travaux_fin, maintenant())
    return _apres(db, devis, "prestataire")


@routeur.post("/moi/prestataire/devis/{devis_id}/termine")
def terminer(devis_id: int, db: Base, compte: CompteConnecte) -> AvecPaiement:
    prestataire, devis = _prestataire(db, compte, devis_id)
    return _apres(db, service.terminer(db, prestataire, devis, maintenant()), "prestataire")


@routeur.post("/moi/prestataire/devis/{devis_id}/paye")
def paye(devis_id: int, donnees: PayeEnDirect, db: Base, compte: CompteConnecte) -> AvecPaiement:
    prestataire, devis = _prestataire(db, compte, devis_id)
    return _apres(db, service.paye_en_direct(db, prestataire, devis, donnees.moyen, maintenant()), "prestataire")


@routeur.post("/moi/prestataire/devis/{devis_id}/annuler")
def annuler_prestataire(devis_id: int, donnees: Motif, db: Base, compte: CompteConnecte) -> AvecPaiement:
    prestataire, devis = _prestataire(db, compte, devis_id)
    return _apres(db, service.annuler_par_prestataire(db, prestataire, devis, donnees.motif or "", maintenant()), "prestataire")


@routeur.post("/moi/prestataire/tva")
def choisir_tva(donnees: ChoixTva, db: Base, compte: CompteConnecte) -> ChoixTva:
    """Case « Je facture la TVA » (RM-DEVIS) : vaut pour les prochains devis, pas pour ceux déjà envoyés."""
    prestataire = mon_profil_ou_404(db, compte)
    avant = prestataire.facture_tva
    prestataire.facture_tva = donnees.facture_tva
    journal.noter(db, auteur_id=compte.id, action="choisir_tva", table_cible="prestataire", ligne_id=prestataire.id,
                  avant={"facture_tva": avant}, apres={"facture_tva": donnees.facture_tva}, maintenant=maintenant())
    db.commit()
    return ChoixTva(facture_tva=prestataire.facture_tva)


# ---------- Administration : problèmes signalés ----------


@routeur.get("/admin/devis-problemes")
def problemes(db: Base, _admin: Administrateur) -> list[ProblemeAdministre]:
    lignes = []
    for devis in service.problemes_a_traiter(db):
        demande = service.demande_de(db, devis)
        client = db.get_one(Compte, demande.client_id)
        lignes.append(ProblemeAdministre(
            devis_id=devis.id, numero=service.numero(devis), titre=db.get_one(Metier, demande.metier_id).nom,
            client=f"{client.prenom} {client.nom}", prestataire=db.get_one(Prestataire, demande.prestataire_id).nom_affiche,
            probleme=devis.probleme or "", probleme_le=devis.probleme_le or devis.envoye_le,
        ))
    return lignes


@routeur.post("/admin/devis/{devis_id}/probleme-traite")
def probleme_traite(devis_id: int, db: Base, admin: Administrateur) -> dict[str, str]:
    service.traiter_probleme(db, admin, devis_id, maintenant())
    db.commit()
    return {"resultat": "traité"}
