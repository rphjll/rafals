"""Adresses de l'accord des parents : dépôt par le compte de 16-17 ans, décision par un administrateur.
(Écrans au lot 1.4.)"""

from datetime import date, datetime

from fastapi import APIRouter, Response, UploadFile
from pydantic import BaseModel
from sqlalchemy import select

from app.modeles.comptes import Compte
from app.modeles.fichiers import AccordParental, Fichier
from app.routes.dependances import Administrateur, Base, CompteConnecte, maintenant
from app.services import accords as service
from app.services import droits, stockage
from app.services.erreurs import ErreurRegle

routeur = APIRouter(prefix="/api")


class EtatAccord(BaseModel):
    necessaire: bool
    statut: str | None
    motif_refus: str | None
    depose_le: datetime | None


class AccordAVerifier(BaseModel):
    id: int
    statut: str
    depose_le: datetime
    compte_id: int
    prenom: str
    nom: str
    date_naissance: date
    nom_fichier: str


class Decision(BaseModel):
    accepte: bool
    motif_refus: str | None = None


def etat_accord(db: Base, compte: Compte) -> EtatAccord:
    accord = service.dernier_accord(db, compte)
    return EtatAccord(
        necessaire=droits.accord_parental_necessaire(compte, maintenant()),
        statut=accord.statut if accord else None,
        motif_refus=accord.motif_refus if accord else None,
        depose_le=accord.depose_le if accord else None,
    )


@routeur.get("/moi/accord-parental")
def mon_accord(db: Base, compte: CompteConnecte) -> EtatAccord:
    return etat_accord(db, compte)


@routeur.post("/moi/accord-parental", status_code=201)
async def deposer(fichier: UploadFile, db: Base, compte: CompteConnecte) -> EtatAccord:
    service.deposer_accord(
        db,
        compte,
        nom_fichier=fichier.filename or "accord",
        type_mime=fichier.content_type or "",
        contenu=await fichier.read(),
        maintenant=maintenant(),
    )
    db.commit()
    return etat_accord(db, compte)


@routeur.get("/admin/accords")
def accords_a_verifier(db: Base, _admin: Administrateur, statut: str = "en_attente") -> list[AccordAVerifier]:
    lignes = db.execute(
        select(AccordParental, Compte, Fichier)
        .join(Compte, Compte.id == AccordParental.compte_id)
        .join(Fichier, Fichier.id == AccordParental.fichier_id)
        .where(AccordParental.statut == statut)
        .order_by(AccordParental.depose_le)
    ).all()
    return [
        AccordAVerifier(
            id=accord.id,
            statut=accord.statut,
            depose_le=accord.depose_le,
            compte_id=compte.id,
            prenom=compte.prenom,
            nom=compte.nom,
            date_naissance=compte.date_naissance,
            nom_fichier=fichier.nom_origine,
        )
        for accord, compte, fichier in lignes
    ]


@routeur.get("/admin/accords/{accord_id}/fichier")
def voir_fichier(accord_id: int, db: Base, _admin: Administrateur) -> Response:
    accord = db.get(AccordParental, accord_id)
    if accord is None:
        raise ErreurRegle("Cet accord n'existe pas.", 404)
    fichier = db.get_one(Fichier, accord.fichier_id)
    return Response(
        content=stockage.lire(fichier.cle_stockage),
        media_type=fichier.type_mime,
        headers={"Content-Disposition": "inline"},
    )


@routeur.post("/admin/accords/{accord_id}/decision")
def decider(accord_id: int, decision: Decision, db: Base, admin: Administrateur) -> dict[str, str]:
    accord = service.decider_accord(
        db, admin, accord_id, accepte=decision.accepte, motif_refus=decision.motif_refus, maintenant=maintenant()
    )
    db.commit()
    return {"statut": accord.statut}
