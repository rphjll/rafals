"""Adresses des métiers : recherche et dossiers (pour tous), propositions (connecté),
gestion et décisions (administrateur). Écrans au lot 2.2."""

from datetime import datetime
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import select

from app.modeles.comptes import Compte
from app.modeles.metiers import CategorieMetier, Metier, PropositionMetier
from app.routes.dependances import Administrateur, Base, CompteConnecte, maintenant
from app.services import metiers as service

routeur = APIRouter(prefix="/api")


class MetierVisible(BaseModel):
    id: int
    code: str
    nom: str
    categorie: str


class MetierComplet(BaseModel):
    id: int
    code: str
    nom: str
    categorie_id: int
    mots_cles: list[str]
    est_active: bool


class Dossier(BaseModel):
    id: int
    code: str
    nom: str
    metiers: list[MetierVisible]


class NouvelleProposition(BaseModel):
    nom: str


class PropositionVisible(BaseModel):
    id: int
    nom_propose: str
    statut: str
    propose_le: datetime
    propose_par: str


class Decision(BaseModel):
    decision: Literal["acceptee", "remplacee", "refusee"]
    categorie_id: int | None = None
    metier_id: int | None = None


class NouveauMetier(BaseModel):
    nom: str
    categorie_id: int


class ModificationMetier(BaseModel):
    nom: str
    categorie_id: int
    mots_cles: list[str]
    est_active: bool


def complet(metier: Metier) -> MetierComplet:
    return MetierComplet(
        id=metier.id, code=metier.code, nom=metier.nom, categorie_id=metier.categorie_id,
        mots_cles=metier.mots_cles, est_active=metier.est_active,
    )


# ---------- Pour tous ----------


@routeur.get("/metiers/recherche")
def recherche(q: str, db: Base) -> list[MetierVisible]:
    return [MetierVisible(id=m.id, code=m.code, nom=m.nom, categorie=c.nom) for m, c in service.rechercher(db, q)]


@routeur.get("/metiers/dossiers")
def dossiers(db: Base) -> list[Dossier]:
    return [
        Dossier(
            id=c.id, code=c.code, nom=c.nom,
            metiers=[MetierVisible(id=m.id, code=m.code, nom=m.nom, categorie=c.nom) for m in metiers],
        )
        for c, metiers in service.categories_avec_metiers(db)
    ]


# ---------- Personne connectée ----------


@routeur.post("/metiers/propositions", status_code=201)
def proposer(donnees: NouvelleProposition, db: Base, compte: CompteConnecte) -> dict[str, str]:
    service.proposer(db, compte, donnees.nom, maintenant())
    db.commit()
    return {"message": "Merci : votre proposition sera étudiée. En attendant, choisissez « Autre »."}


# ---------- Administrateur ----------


@routeur.get("/admin/metiers")
def tous_les_metiers(db: Base, _admin: Administrateur) -> list[MetierComplet]:
    return [complet(m) for m in db.scalars(select(Metier).order_by(Metier.nom))]


@routeur.post("/admin/metiers", status_code=201)
def creer(donnees: NouveauMetier, db: Base, admin: Administrateur) -> MetierComplet:
    metier = service.creer_metier(db, admin, nom=donnees.nom, categorie_id=donnees.categorie_id, maintenant=maintenant())
    db.commit()
    return complet(metier)


@routeur.post("/admin/metiers/{metier_id}")
def modifier(metier_id: int, donnees: ModificationMetier, db: Base, admin: Administrateur) -> MetierComplet:
    metier = service.modifier_metier(db, admin, metier_id, **donnees.model_dump(), maintenant=maintenant())
    db.commit()
    return complet(metier)


@routeur.get("/admin/dossiers")
def tous_les_dossiers(db: Base, _admin: Administrateur) -> list[dict]:
    return [
        {"id": c.id, "code": c.code, "nom": c.nom, "ordre": c.ordre, "est_active": c.est_active}
        for c in db.scalars(select(CategorieMetier).order_by(CategorieMetier.ordre))
    ]


@routeur.get("/admin/propositions")
def propositions(db: Base, _admin: Administrateur, statut: str = "en_attente") -> list[PropositionVisible]:
    lignes = db.execute(
        select(PropositionMetier, Compte)
        .join(Compte, Compte.id == PropositionMetier.propose_par_id)
        .where(PropositionMetier.statut == statut)
        .order_by(PropositionMetier.propose_le)
    ).all()
    return [
        PropositionVisible(
            id=p.id, nom_propose=p.nom_propose, statut=p.statut, propose_le=p.propose_le,
            propose_par=f"{c.prenom} {c.nom}",
        )
        for p, c in lignes
    ]


@routeur.post("/admin/propositions/{proposition_id}/decision")
def decider(proposition_id: int, donnees: Decision, db: Base, admin: Administrateur) -> dict[str, str | int | None]:
    proposition = service.decider_proposition(
        db, admin, proposition_id, decision=donnees.decision, categorie_id=donnees.categorie_id,
        metier_id=donnees.metier_id, maintenant=maintenant(),
    )
    db.commit()
    return {"statut": proposition.statut, "metier_retenu_id": proposition.metier_retenu_id}
