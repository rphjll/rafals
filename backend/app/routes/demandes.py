"""Adresses des demandes publiées par les clients (lot 8.3, première partie). Règles : RM-DEMANDES.md."""

from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Form, Response, UploadFile
from pydantic import BaseModel

from app.modeles.comptes import Compte
from app.modeles.demandes import Demande
from app.modeles.fichiers import Fichier
from app.modeles.metiers import Metier
from app.modeles.prestataires import Commune
from app.routes.dependances import Base, CompteConnecte, CompteOuPersonne, maintenant
from app import reglages
from app.services import alertes, avis_clients
from app.services import demandes as service
from app.services import prestataires as service_prestataires
from app.services import propositions as service_propositions
from app.services import stockage
from app.services.erreurs import ErreurRegle
from app.services.messagerie import Photo, nom_du_client

routeur = APIRouter(prefix="/api")


class DemandeVisible(BaseModel):
    """Ce que tout le monde lit sur l'accueil : jamais le nom complet, le téléphone, le mail ni la rue."""

    id: int
    titre: str
    description: str
    metier_id: int
    metier: str
    ville: str
    quand: str
    jour: date | None
    lieu: str
    budget_centimes: int | None
    client: str  # « Marie D. »
    client_id: int  # pour [Voir les avis] : /clients/12/avis
    client_note: float | None  # moyenne des avis laissés par des prestataires (ex. 4.8) ; vide sans avis
    client_avis: int  # nombre d'avis
    cree_le: datetime
    nombre_photos: int
    a_moi: bool
    nombre_reponses: int
    complete: bool  # 10 prestataires ont déjà répondu
    peut_repondre: bool  # pour un prestataire connecté : son métier, son rayon, pas complète (ou déjà répondu)
    conversation_id: int | None  # pour un prestataire qui a déjà répondu : sa conversation avec le client
    raison_verrou: str | None  # prestataire sans SIRET : pourquoi [Répondre] est verrouillé (métier, adresse, case, plafond)


class MaDemande(DemandeVisible):
    """Ce que le client relit dans « Mes demandes » : avec son adresse et l'état de la demande."""

    statut: str
    expire_le: datetime
    adresse_ligne: str | None
    adresse_complement: str | None
    code_postal: str | None
    latitude: float | None
    longitude: float | None
    cachee: bool


class Modification(BaseModel):
    metier_id: int
    titre: str
    description: str
    quand: str
    jour: date | None = None
    lieu: str = "chez_moi"
    budget_centimes: int | None = None
    adresse_ligne: str | None = None
    adresse_complement: str | None = None
    code_postal: str | None = None
    code_insee: str | None = None
    latitude: float | None = None
    longitude: float | None = None


def _visible(db: Base, compte: Compte | None, demande: Demande) -> DemandeVisible:
    reponses = service_propositions.nombre_reponses(db, demande.id)
    prestataire = service_prestataires.profil_de(db, compte) if compte is not None else None
    ma_reponse = service_propositions.reponse_de(db, prestataire, demande.id) if prestataire is not None else None
    complete = reponses >= reglages.DEMANDE_REPONSES_MAX
    peut = prestataire is not None and service_propositions.demande_sur_l_accueil(demande, maintenant()) and (
        ma_reponse is not None or (not complete and service_propositions.peut_repondre(db, prestataire, demande, maintenant())))
    verrou = None
    if prestataire is not None and ma_reponse is None and not peut and service_propositions.demande_sur_l_accueil(demande, maintenant()):
        verrou = service_propositions.raison_verrou(db, prestataire, demande, maintenant())
    note, nombre_avis = avis_clients.note_de(db, demande.client_id)
    return DemandeVisible(
        client_id=demande.client_id, client_note=note, client_avis=nombre_avis,
        nombre_reponses=reponses, complete=complete, peut_repondre=peut, raison_verrou=verrou,
        conversation_id=ma_reponse.conversation_id if ma_reponse is not None else None,
        id=demande.id, titre=demande.titre, description=demande.description, metier_id=demande.metier_id,
        metier=db.get_one(Metier, demande.metier_id).nom, ville=db.get_one(Commune, demande.commune_id).nom,
        quand=demande.quand, jour=demande.jour, lieu=demande.lieu, budget_centimes=demande.budget_centimes,
        client=nom_du_client(db.get_one(Compte, demande.client_id)), cree_le=demande.cree_le,
        nombre_photos=len(service.photos_de(db, demande.id)), a_moi=compte is not None and demande.client_id == compte.id,
    )


def _mienne(db: Base, compte: Compte, demande: Demande) -> MaDemande:
    return MaDemande(
        **_visible(db, compte, demande).model_dump(), statut=demande.statut, expire_le=demande.expire_le,
        adresse_ligne=demande.adresse_ligne, adresse_complement=demande.adresse_complement,
        code_postal=demande.code_postal, latitude=demande.latitude, longitude=demande.longitude,
        cachee=demande.cachee_le is not None,
    )


def _jour(texte: str | None) -> date | None:
    if not texte:
        return None
    try:
        return date.fromisoformat(texte)
    except ValueError:
        raise ErreurRegle("Le jour voulu n'est pas une date (ex. 2026-10-10).") from None


@routeur.get("/demandes")
def demandes_ouvertes(db: Base, compte: CompteOuPersonne) -> list[DemandeVisible]:
    """La liste de l'accueil : ouverte à tous, même sans compte ; la plus récente en haut."""
    return [_visible(db, compte, d) for d in service.ouvertes(db, maintenant())]


@routeur.post("/demandes", status_code=201)
async def publier(
    db: Base, compte: CompteConnecte,
    metier_id: Annotated[int, Form()], titre: Annotated[str, Form()], description: Annotated[str, Form()],
    quand: Annotated[str, Form()] = "des_que_possible", jour: Annotated[str | None, Form()] = None,
    lieu: Annotated[str, Form()] = "chez_moi", budget_centimes: Annotated[int | None, Form()] = None,
    adresse_ligne: Annotated[str | None, Form()] = None, adresse_complement: Annotated[str | None, Form()] = None,
    code_postal: Annotated[str | None, Form()] = None, code_insee: Annotated[str | None, Form()] = None,
    latitude: Annotated[float | None, Form()] = None, longitude: Annotated[float | None, Form()] = None,
    photos: list[UploadFile] | None = None,
) -> MaDemande:
    """Un formulaire (pas du JSON), à cause des photos : les rubriques de la demande et jusqu'à 5 fichiers « photos »."""
    saisie = service.Saisie(
        metier_id=metier_id, titre=titre, description=description, quand=quand, jour=_jour(jour), lieu=lieu,
        budget_centimes=budget_centimes, adresse_ligne=adresse_ligne, adresse_complement=adresse_complement,
        code_postal=code_postal, code_insee=code_insee, latitude=latitude, longitude=longitude,
    )
    jointes = [Photo(nom_fichier=p.filename or "photo", type_mime=p.content_type or "", contenu=await p.read())
               for p in photos or []]
    demande = service.publier(db, compte, saisie, jointes, maintenant())
    alertes.prevenir_nouvelle_demande(db, demande, maintenant())  # RM-ALERTES : un mail aux prestataires concernés
    db.commit()
    return _mienne(db, compte, demande)


@routeur.get("/moi/demandes")
def mes_demandes(db: Base, compte: CompteConnecte) -> list[MaDemande]:
    return [_mienne(db, compte, d) for d in service.mes_demandes(db, compte)]


@routeur.put("/demandes/{demande_id}")
def modifier(demande_id: int, donnees: Modification, db: Base, compte: CompteConnecte) -> MaDemande:
    demande = service.ma_demande_ou_404(db, compte, demande_id)
    service.modifier(db, compte, demande, service.Saisie(**donnees.model_dump()), maintenant())
    db.commit()
    return _mienne(db, compte, demande)


@routeur.post("/demandes/{demande_id}/fermer")
def fermer(demande_id: int, db: Base, compte: CompteConnecte) -> MaDemande:
    demande = service.ma_demande_ou_404(db, compte, demande_id)
    service.fermer(db, compte, demande, maintenant())
    db.commit()
    return _mienne(db, compte, demande)


@routeur.post("/demandes/{demande_id}/prolonger")
def prolonger(demande_id: int, db: Base, compte: CompteConnecte) -> MaDemande:
    demande = service.ma_demande_ou_404(db, compte, demande_id)
    service.prolonger(db, compte, demande, maintenant())
    db.commit()
    return _mienne(db, compte, demande)


@routeur.get("/demandes/{demande_id}/photos/{ordre}")
def voir_photo(demande_id: int, ordre: int, db: Base, compte: CompteConnecte) -> Response:
    """Il faut être connecté : les photos montrent souvent l'intérieur d'un logement."""
    demande = service.visible_ou_404(db, compte, demande_id, maintenant())
    photo = next((p for p in service.photos_de(db, demande.id) if p.ordre == ordre), None)
    if photo is None:
        raise ErreurRegle("Cette photo n'existe pas.", 404)
    fichier = db.get_one(Fichier, photo.fichier_id)
    return Response(content=stockage.lire(fichier.cle_stockage), media_type=fichier.type_mime)
