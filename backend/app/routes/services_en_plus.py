"""Adresses du niveau 6 sans nouvelle table (lot 6.1) : tableau de bord et paiements de l'administrateur
(RM-ADMINISTRATION.md), chiffre d'affaires à déclarer (RM-DEMARCHES.md)."""

from dataclasses import asdict
from datetime import date

from fastapi import APIRouter
from pydantic import BaseModel

from app.modeles.comptes import Compte
from app.routes.dependances import Administrateur, Base, CompteConnecte, maintenant
from app.routes.prestataires import mon_profil_ou_404
from app.services import demarches, paiements, tableau_de_bord
from app.services.erreurs import ErreurRegle

routeur = APIRouter(prefix="/api")


# ---------- Administration ----------


class TableauDeBord(BaseModel):
    a_traiter: dict[str, int]  # par onglet : accords, absences, avis, devis, propositions
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


class Demarches(BaseModel):
    annee: int
    siret_verifie: bool
    facture_tva: bool  # le chiffre est alors hors taxe
    mois: list[PeriodeVisible]
    trimestres: list[PeriodeVisible]


@routeur.get("/moi/prestataire/demarches")
def mes_demarches(db: Base, compte: CompteConnecte, annee: int | None = None) -> Demarches:
    """Le chiffre d'affaires à déclarer à l'URSSAF, d'après les factures faites par rafals (ventes moins avoirs)."""
    prestataire = mon_profil_ou_404(db, compte)
    maintenant_ = maintenant()
    annee = annee or maintenant_.astimezone(demarches.PARIS).year
    if not 2026 <= annee <= maintenant_.year + 1:
        raise ErreurRegle("Choisissez une année entre 2026 et l'an prochain.")
    mois, trimestres = demarches.chiffre_d_affaires(db, prestataire, annee, maintenant_)
    return Demarches(annee=annee, siret_verifie=prestataire.siret_statut == "verifie", facture_tva=prestataire.facture_tva,
                     mois=[PeriodeVisible(**asdict(m)) for m in mois], trimestres=[PeriodeVisible(**asdict(t)) for t in trimestres])
