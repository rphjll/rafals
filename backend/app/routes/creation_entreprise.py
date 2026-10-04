"""Adresses du lot 7.1 : créer une auto-entreprise depuis rafals (RM-CREATION-AUTO-ENTREPRISE.md), et « j'ai déjà une
entreprise » (ajouter son SIRET sans rien créer)."""

from datetime import date, datetime

from fastapi import APIRouter, Response, UploadFile
from pydantic import BaseModel

from app import reglages
from app.modeles.comptes import Compte
from app.modeles.creation import DossierCreation
from app.modeles.metiers import Metier
from app.modeles.prestataires import Commune
from app.routes.dependances import Base, CompteConnecte, maintenant
from app.routes.prestataires import CommuneVisible, commune_visible, mon_profil_ou_404
from app.services import creation_entreprise as service
from app.services import guichet
from app.services import prestataires as service_prestataires

routeur = APIRouter(prefix="/api")


class PieceVisible(BaseModel):
    sorte: str
    nom: str  # « la pièce d'identité »
    deposee_par_rafals: bool  # le pouvoir et l'attestation sont écrits par rafals
    depose_le: datetime | None
    a_refaire: bool
    efface: bool


class DossierVisible(BaseModel):
    id: int
    statut: str  # brouillon · envoye · en_examen · a_corriger · accepte · refuse · ferme
    demonstration: bool  # rien n'a été envoyé à l'État (pas d'identifiants INPI)
    # Étape 1
    civilite: str | None
    nom_naissance: str | None
    nom_usage: str | None
    prenoms: str | None
    naissance_le: date | None
    naissance_commune: CommuneVisible | None
    naissance_pays: str | None
    nationalite: str | None
    situation_famille: str | None
    numero_secu: str | None
    adresse_rue: str | None
    commune: CommuneVisible | None
    code_postal: str | None
    mail: str | None
    telephone: str | None
    pere_nom: str | None
    mere_nom: str | None
    # Étape 2
    metier_id: int | None
    metier: str | None
    metier_reglemente: bool
    description: str | None
    debut_le: date | None
    lieu_travail: str | None
    local_adresse: str | None
    local_commune: CommuneVisible | None
    local_code_postal: str | None
    nom_commercial: str | None
    activite_en_meme_temps: str | None
    ancien_siren: str | None
    # Étape 3
    periodicite: str | None
    impot_avec_cotisations: bool | None
    acre_demandee: bool | None
    adresse_non_publique: bool | None
    # Papiers, envoi et suivi
    pieces: list[PieceVisible]
    manque: dict[str, list[str]]  # par étape : vous, activite, choix, papiers
    envoye_le: datetime | None
    guichet_numero: str | None
    motif: str | None
    corriger_avant_le: date | None
    siret_recu: str | None
    statut_change_le: datetime


class MaSituation(BaseModel):
    peut_commencer: bool
    raison: str | None  # « Vous avez déjà une entreprise (SIRET …) : il n'y a rien à créer. »
    a_un_profil: bool
    dossier: DossierVisible | None


class ReglesMetiers(BaseModel):
    reglementes: list[int]  # il faut un diplôme ou 3 ans d'expérience
    renvoyes: list[int]  # la démarche se fait sur le site de l'État
    debut_max: date


class VousDemande(BaseModel):
    civilite: str
    nom_naissance: str
    nom_usage: str | None = None
    prenoms: str
    naissance_le: date
    naissance_commune_id: int | None = None
    naissance_pays: str | None = None
    nationalite: str
    situation_famille: str
    conjoint_travaille: bool = False
    numero_secu: str
    adresse_rue: str
    commune_id: int
    code_postal: str
    mail: str
    telephone: str


class ActiviteDemande(BaseModel):
    metier_id: int
    description: str
    debut_le: date
    lieu_travail: str
    local_adresse: str | None = None
    local_commune_id: int | None = None
    local_code_postal: str | None = None
    nom_commercial: str | None = None
    activite_en_meme_temps: str
    ancien_siren: str | None = None


class ChoixDemande(BaseModel):
    periodicite: str
    impot_avec_cotisations: bool
    acre_demandee: bool
    adresse_non_publique: bool


class ParentsDemande(BaseModel):
    pere_nom: str
    mere_nom: str


class EnvoiDemande(BaseModel):
    certifie: bool
    pouvoir: bool


class SiretDemande(BaseModel):
    siret: str


class Texte(BaseModel):
    texte: str


def _commune(db: Base, identifiant: int | None) -> CommuneVisible | None:
    return commune_visible(db.get_one(Commune, identifiant)) if identifiant else None


def visible(db: Base, d: DossierCreation) -> DossierVisible:
    jour = service.aujourd_hui(maintenant())
    metier = db.get(Metier, d.metier_id) if d.metier_id else None
    deposees = service.pieces(db, d)
    sortes = [*service.pieces_attendues(db, d, jour), *(s for s in ("attestation", "pouvoir") if s in deposees)]
    pieces = []
    for sorte in sortes:
        piece = deposees.get(sorte)
        pieces.append(PieceVisible(
            sorte=sorte, nom=service.PIECES[sorte][0], deposee_par_rafals=sorte not in service.PIECES_DEPOSEES,
            depose_le=piece.depose_le if piece and piece.fichier_id else None,
            a_refaire=bool(piece and piece.a_refaire), efface=bool(piece and piece.efface_le),
        ))
    return DossierVisible(
        id=d.id, statut=d.statut, demonstration=guichet.en_demonstration(d.guichet_id) or (d.guichet_id is None and not guichet.disponible()),
        civilite=d.civilite, nom_naissance=d.nom_naissance, nom_usage=d.nom_usage, prenoms=d.prenoms, naissance_le=d.naissance_le,
        naissance_commune=_commune(db, d.naissance_commune_id), naissance_pays=d.naissance_pays, nationalite=d.nationalite,
        situation_famille=d.situation_famille, numero_secu=d.numero_secu, adresse_rue=d.adresse_rue,
        commune=_commune(db, d.commune_id), code_postal=d.code_postal, mail=d.mail, telephone=d.telephone,
        pere_nom=d.pere_nom, mere_nom=d.mere_nom,
        metier_id=d.metier_id, metier=metier.nom if metier else None, metier_reglemente=bool(metier and service.metier_reglemente(metier)),
        description=d.description, debut_le=d.debut_le, lieu_travail=d.lieu_travail, local_adresse=d.local_adresse,
        local_commune=_commune(db, d.local_commune_id), local_code_postal=d.local_code_postal, nom_commercial=d.nom_commercial,
        activite_en_meme_temps=d.activite_en_meme_temps, ancien_siren=d.ancien_siren,
        periodicite=d.periodicite, impot_avec_cotisations=d.impot_avec_cotisations, acre_demandee=d.acre_demandee,
        adresse_non_publique=d.adresse_non_publique,
        pieces=pieces, manque=service.manque(db, d, jour) if d.statut in service.MODIFIABLES else {},
        envoye_le=d.envoye_le, guichet_numero=d.guichet_numero, motif=d.motif, corriger_avant_le=d.corriger_avant_le,
        siret_recu=d.siret_recu, statut_change_le=d.statut_change_le,
    )


def _situation(db: Base, compte: Compte) -> MaSituation:
    raison = service.empechement(db, compte)
    dossier = service.dernier(db, compte)
    return MaSituation(peut_commencer=raison is None, raison=raison, a_un_profil=service.profil_de(db, compte) is not None,
                       dossier=visible(db, dossier) if dossier else None)


# ---------- Pour tous ----------


@routeur.get("/creation-entreprise/metiers")
def regles_des_metiers(db: Base) -> ReglesMetiers:
    reglementes, renvoyes = service.regles_des_metiers(db)
    return ReglesMetiers(reglementes=reglementes, renvoyes=renvoyes,
                         debut_max=service.aujourd_hui(maintenant()) + reglages.CREATION_DEBUT_MAX)


# ---------- Mon dossier ----------


@routeur.get("/moi/creation-entreprise")
def ma_situation(db: Base, compte: CompteConnecte) -> MaSituation:
    return _situation(db, compte)


@routeur.post("/moi/creation-entreprise", status_code=201)
def commencer(db: Base, compte: CompteConnecte) -> MaSituation:
    service.commencer(db, compte, maintenant())
    db.commit()
    return _situation(db, compte)


@routeur.post("/moi/creation-entreprise/effacer")
def abandonner(db: Base, compte: CompteConnecte) -> MaSituation:
    service.abandonner(db, compte, maintenant())
    db.commit()
    return _situation(db, compte)


@routeur.post("/moi/creation-entreprise/vous")
def vous(donnees: VousDemande, db: Base, compte: CompteConnecte) -> MaSituation:
    service.enregistrer_vous(db, compte, service.Vous(**donnees.model_dump()), maintenant())
    db.commit()
    return _situation(db, compte)


@routeur.post("/moi/creation-entreprise/activite")
def activite(donnees: ActiviteDemande, db: Base, compte: CompteConnecte) -> MaSituation:
    service.enregistrer_activite(db, compte, service.Activite(**donnees.model_dump()), maintenant())
    db.commit()
    return _situation(db, compte)


@routeur.post("/moi/creation-entreprise/choix")
def choix(donnees: ChoixDemande, db: Base, compte: CompteConnecte) -> MaSituation:
    service.enregistrer_choix(db, compte, service.Choix(**donnees.model_dump()), maintenant())
    db.commit()
    return _situation(db, compte)


@routeur.post("/moi/creation-entreprise/parents")
def parents(donnees: ParentsDemande, db: Base, compte: CompteConnecte) -> MaSituation:
    service.enregistrer_parents(db, compte, donnees.pere_nom, donnees.mere_nom, maintenant())
    db.commit()
    return _situation(db, compte)


@routeur.post("/moi/creation-entreprise/pieces/{sorte}")
async def deposer_piece(sorte: str, fichier: UploadFile, db: Base, compte: CompteConnecte) -> MaSituation:
    service.deposer_piece(db, compte, sorte, type_mime=fichier.content_type or "", contenu=await fichier.read(), maintenant=maintenant())
    db.commit()
    return _situation(db, compte)


@routeur.get("/moi/creation-entreprise/pieces/{sorte}")
def lire_piece(sorte: str, db: Base, compte: CompteConnecte) -> Response:
    return Response(content=service.lire_piece(db, compte, sorte), media_type="application/pdf",
                    headers={"Cache-Control": "no-store", "Content-Disposition": f'inline; filename="{sorte}.pdf"'})


@routeur.get("/moi/creation-entreprise/pouvoir")
def pouvoir(db: Base, compte: CompteConnecte) -> Texte:
    """Le texte du pouvoir, à lire avant de cocher la case (celui qui a été accepté, une fois le dossier envoyé)."""
    dossier = service.dernier(db, compte)
    if dossier is None:
        return Texte(texte="")
    return Texte(texte=dossier.pouvoir_texte or service.texte_pouvoir(db, dossier, maintenant()))


@routeur.post("/moi/creation-entreprise/envoi")
def envoyer(donnees: EnvoiDemande, db: Base, compte: CompteConnecte) -> MaSituation:
    service.envoyer(db, compte, certifie=donnees.certifie, pouvoir=donnees.pouvoir, maintenant=maintenant())
    db.commit()
    return _situation(db, compte)


@routeur.post("/moi/creation-entreprise/correction")
def corriger(db: Base, compte: CompteConnecte) -> MaSituation:
    service.envoyer_correction(db, compte, maintenant())
    db.commit()
    return _situation(db, compte)


@routeur.post("/moi/creation-entreprise/actualiser")
def actualiser(db: Base, compte: CompteConnecte) -> MaSituation:
    """[Actualiser] : demande tout de suite au guichet où en est le dossier (sinon, rafals regarde toutes les heures)."""
    dossier = service.dernier(db, compte)
    if dossier is not None:
        try:
            service.actualiser(db, dossier, maintenant())
        except guichet.GuichetIndisponible:
            db.rollback()
        db.commit()
    return _situation(db, compte)


# ---------- « J'ai déjà une entreprise » ----------


@routeur.post("/moi/prestataire/siret")
def ajouter_siret(donnees: SiretDemande, db: Base, compte: CompteConnecte) -> MaSituation:
    """Sans profil de prestataire : 404, l'écran emmène créer le profil (le SIRET y est déjà demandé)."""
    service_prestataires.ajouter_siret(db, compte, mon_profil_ou_404(db, compte), donnees.siret, maintenant())
    db.commit()
    return _situation(db, compte)
