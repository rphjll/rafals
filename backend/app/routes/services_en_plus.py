"""Adresses du niveau 6 (lots 6.1 et 6.3) : tableau de bord, paiements et signalements de l'administrateur
(RM-ADMINISTRATION.md) ; chiffre d'affaires à déclarer et rappels URSSAF (RM-DEMARCHES.md)."""

from dataclasses import asdict
from datetime import date, datetime
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import func, select

from app.modeles.comptes import Compte
from app.modeles.prestataires import Prestataire
from app.modeles.messagerie import Conversation
from app.modeles.signalements import Signalement
from app.routes.dependances import Administrateur, Base, CompteConnecte, maintenant
from app.routes.prestataires import mon_profil_ou_404
from app.services import declarations_urssaf, demarches, paiements, signalements, tableau_de_bord, urssaf
from app.services.erreurs import ErreurRegle

routeur = APIRouter(prefix="/api")


# ---------- Administration ----------


class TableauDeBord(BaseModel):
    a_traiter: dict[str, int]  # par onglet : accords, absences, avis, devis, propositions, signalements
    activite: dict[str, int | str]


class PaiementAdministre(BaseModel):
    id: int
    sorte: str  # rendez_vous · arrhes · solde
    titre: str
    quand: str  # « mardi 13/10/2026 à 10 h 00 » ou « devis D-2026-0002 (arrhes) »
    prestataire: str
    client: str
    montant_centimes: int
    commission_centimes: int
    statut: str
    paye_le: str | None
    verse_le: str | None
    rembourse_le: str | None
    rembourse_centimes: int | None


class PagePaiements(BaseModel):
    paiements: list[PaiementAdministre]
    total: int
    par_page: int


@routeur.get("/admin/tableau-de-bord")
def tableau(db: Base, _admin: Administrateur) -> TableauDeBord:
    return TableauDeBord(a_traiter=asdict(tableau_de_bord.a_traiter(db)), activite=asdict(tableau_de_bord.activite(db, maintenant())))


@routeur.get("/admin/paiements")
def tous_les_paiements(db: Base, _admin: Administrateur, page: int = 1) -> PagePaiements:
    """Lecture seule : les remboursements et les versements restent automatiques."""
    lignes, total = tableau_de_bord.paiements(db, page)
    resultat = []
    for p in lignes:
        s = paiements.sujet(db, p)
        client = db.get_one(Compte, s.client_id)
        resultat.append(PaiementAdministre(
            id=p.id, sorte=p.sorte, titre=s.titre, quand=s.quand, prestataire=s.prestataire.nom_affiche,
            client=f"{client.prenom} {client.nom}", montant_centimes=p.montant_centimes, commission_centimes=p.commission_centimes,
            statut=p.statut, paye_le=p.paye_le.isoformat() if p.paye_le else None,
            verse_le=p.verse_le.isoformat() if p.verse_le else None,
            rembourse_le=p.rembourse_le.isoformat() if p.rembourse_le else None, rembourse_centimes=p.rembourse_centimes,
        ))
    return PagePaiements(paiements=resultat, total=total, par_page=tableau_de_bord.PAIEMENTS_PAR_PAGE)


# ---------- Mes démarches ----------


class PeriodeVisible(BaseModel):
    rang: int  # mois 1 à 12, ou trimestre 1 à 4
    debut: date
    fin: date
    encaisse_centimes: int
    nombre_factures: int
    a_declarer_avant: date
    terminee: bool
    # Déclarée à l'URSSAF depuis rafals (lot 7.3) : total envoyé, cotisations répondues, date
    declaree_centimes: int | None = None
    cotisations_centimes: int | None = None
    declaree_le: datetime | None = None


class PeriodeADeclarer(BaseModel):
    periodicite: str
    debut: date
    nom: str  # « 3e trimestre 2026 »
    limite: date
    montant_rafals_centimes: int
    nombre_factures: int


class Urssaf(BaseModel):
    """Déclarer d'un clic depuis rafals (lot 7.3)."""

    mandat_le: datetime | None  # l'accord en cours, ou vide
    texte_mandat: str
    demonstration: bool  # rafals n'est pas branché à l'URSSAF : rien n'est envoyé
    a_declarer: PeriodeADeclarer | None


class Demarches(BaseModel):
    annee: int
    siret_verifie: bool
    facture_tva: bool  # le chiffre est alors hors taxe
    periodicite: str | None  # « mois », « trimestre », ou vide (pas de rappel)
    mois: list[PeriodeVisible]
    trimestres: list[PeriodeVisible]
    urssaf: Urssaf


@routeur.get("/moi/prestataire/demarches")
def mes_demarches(db: Base, compte: CompteConnecte, annee: int | None = None) -> Demarches:
    """Le chiffre d'affaires à déclarer à l'URSSAF, d'après les factures faites par rafals (ventes moins avoirs)."""
    prestataire = mon_profil_ou_404(db, compte)
    maintenant_ = maintenant()
    annee = annee or maintenant_.astimezone(demarches.PARIS).year
    if not 2026 <= annee <= maintenant_.year + 1:
        raise ErreurRegle("Choisissez une année entre 2026 et l'an prochain.")
    mois, trimestres = demarches.chiffre_d_affaires(db, prestataire, annee, maintenant_)
    declarees = {(d.periodicite, d.periode_debut): d for d in declarations_urssaf.declarations(db, prestataire)}

    def visible(periode: demarches.Periode, periodicite: str) -> PeriodeVisible:
        d = declarees.get((periodicite, periode.debut))
        return PeriodeVisible(**asdict(periode), declaree_centimes=d.montant_rafals_centimes + d.montant_ailleurs_centimes if d else None,
                              cotisations_centimes=d.cotisations_centimes if d else None, declaree_le=d.declaree_le if d else None)

    mandat = declarations_urssaf.mandat_en_cours(db, prestataire)
    periode = declarations_urssaf.a_declarer(db, prestataire, maintenant_)
    return Demarches(
        annee=annee, siret_verifie=prestataire.siret_statut == "verifie", facture_tva=prestataire.facture_tva,
        periodicite=prestataire.declaration_periodicite,
        mois=[visible(m, "mois") for m in mois], trimestres=[visible(t, "trimestre") for t in trimestres],
        urssaf=Urssaf(
            mandat_le=mandat.donne_le if mandat else None, texte_mandat=declarations_urssaf.TEXTE_MANDAT,
            demonstration=not urssaf.disponible(),
            a_declarer=PeriodeADeclarer(periodicite=periode.periodicite, debut=periode.debut, nom=periode.nom, limite=periode.limite,
                                        montant_rafals_centimes=periode.montant_rafals_centimes,
                                        nombre_factures=periode.nombre_factures) if periode else None,
        ),
    )


class Periodicite(BaseModel):
    periodicite: Literal["mois", "trimestre"] | None


@routeur.post("/moi/prestataire/demarches/periodicite")
def choisir_periodicite(donnees: Periodicite, db: Base, compte: CompteConnecte) -> Periodicite:
    """« Je déclare chaque mois / chaque trimestre » : rafals envoie alors les rappels (7 jours avant, puis la veille)."""
    prestataire = demarches.choisir_periodicite(db, mon_profil_ou_404(db, compte), donnees.periodicite, maintenant())
    db.commit()
    return Periodicite(periodicite=prestataire.declaration_periodicite)  # type: ignore[arg-type]


# ---------- Déclarer à l'URSSAF depuis rafals (lot 7.3) ----------


class MandatDemande(BaseModel):
    numero_secu: str
    accepte: bool


class DeclarationDemande(BaseModel):
    ailleurs_centimes: int = 0
    certifie: bool = False


class Estimation(BaseModel):
    total_centimes: int
    cotisations_centimes: int


@routeur.post("/moi/prestataire/urssaf/mandat")
def donner_mandat(donnees: MandatDemande, db: Base, compte: CompteConnecte) -> Demarches:
    """L'accord donné à rafals pour déclarer à la place du prestataire ; signalé à l'URSSAF."""
    declarations_urssaf.donner_mandat(db, compte, mon_profil_ou_404(db, compte), numero_secu=donnees.numero_secu,
                                      accepte=donnees.accepte, maintenant=maintenant())
    db.commit()
    return mes_demarches(db, compte)


@routeur.post("/moi/prestataire/urssaf/mandat/retirer")
def retirer_mandat(db: Base, compte: CompteConnecte) -> Demarches:
    declarations_urssaf.retirer_mandat(db, compte, mon_profil_ou_404(db, compte), maintenant())
    db.commit()
    return mes_demarches(db, compte)


@routeur.post("/moi/prestataire/urssaf/estimation")
def estimer(donnees: DeclarationDemande, db: Base, compte: CompteConnecte) -> Estimation:
    """Le total et les cotisations, montrés avant d'envoyer. Rien n'est déclaré."""
    total, cotisations = declarations_urssaf.estimer(db, mon_profil_ou_404(db, compte), donnees.ailleurs_centimes, maintenant())
    return Estimation(total_centimes=total, cotisations_centimes=cotisations)


@routeur.post("/moi/prestataire/urssaf/declaration")
def declarer(donnees: DeclarationDemande, db: Base, compte: CompteConnecte) -> Demarches:
    """[Envoyer à l'URSSAF] : la déclaration de la dernière période finie."""
    declarations_urssaf.declarer(db, compte, mon_profil_ou_404(db, compte), ailleurs_centimes=donnees.ailleurs_centimes,
                                 certifie=donnees.certifie, maintenant=maintenant())
    db.commit()
    return mes_demarches(db, compte)


# ---------- Signalements (lot 6.3) ----------


class NouveauSignalement(BaseModel):
    prestataire_id: int
    motif: str


class DecisionSignalement(BaseModel):
    action: Literal["classer", "bloquer_prestataire", "prevenir"]
    decision: str = ""


class SignalementAdministre(BaseModel):
    id: int
    cree_le: datetime
    auteur: str
    prestataire_id: int | None  # vide : conversation signalée par un prestataire (c'est le client qui est visé)
    prestataire: str  # ou le nom du client visé
    prestataire_statut: str
    conversation_id: int | None = None  # conversation signalée : l'administrateur peut la lire (lot 8.1)
    motif: str
    deja_signale: int  # nombre d'autres signalements sur ce prestataire (traités ou non)


@routeur.post("/signalements", status_code=201)
def signaler(donnees: NouveauSignalement, db: Base, compte: CompteConnecte) -> dict[str, int]:
    """Signaler un prestataire, avec un motif (une conversation se signale depuis les messages)."""
    signalement = signalements.signaler(db, compte, prestataire_id=donnees.prestataire_id, motif=donnees.motif,
                                        maintenant=maintenant())
    db.commit()
    return {"id": signalement.id}


@routeur.get("/admin/signalements")
def signalements_a_traiter(db: Base, _admin: Administrateur) -> list[SignalementAdministre]:
    resultat = []
    for s in signalements.a_traiter(db):
        auteur = db.get_one(Compte, s.auteur_id)
        prestataire = db.get_one(Prestataire, s.prestataire_id) if s.prestataire_id else None
        if prestataire is None:  # conversation signalée par le prestataire : le client est visé
            client = db.get_one(Compte, db.get_one(Conversation, s.conversation_id).client_id)
            resultat.append(SignalementAdministre(
                id=s.id, cree_le=s.cree_le, auteur=f"{auteur.prenom} {auteur.nom}", prestataire_id=None,
                prestataire=f"{client.prenom} {client.nom} (client)", prestataire_statut="client",
                conversation_id=s.conversation_id, motif=s.motif,
                deja_signale=0,
            ))
            continue
        autres = db.scalar(select(func.count()).select_from(Signalement).where(Signalement.prestataire_id == prestataire.id,
                                                                              Signalement.id != s.id)) or 0
        resultat.append(SignalementAdministre(
            id=s.id, cree_le=s.cree_le, auteur=f"{auteur.prenom} {auteur.nom}", prestataire_id=prestataire.id,
            conversation_id=s.conversation_id,
            prestataire=prestataire.nom_affiche, prestataire_statut=prestataire.statut, motif=s.motif,
            deja_signale=autres,
        ))
    return resultat


@routeur.post("/admin/signalements/{signalement_id}")
def traiter_signalement(signalement_id: int, donnees: DecisionSignalement, db: Base, admin: Administrateur) -> dict[str, str]:
    signalement = signalements.traiter(db, admin, signalement_id, action=donnees.action, decision=donnees.decision,
                                       maintenant=maintenant())
    db.commit()
    return {"statut": signalement.statut}
