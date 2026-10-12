"""Adresses des avis d'un prestataire sur un client (lot 8.5). Règles : RM-AVIS.md § « Notation dans les deux sens »."""

from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

from app.modeles.avis import AvisClient
from app.modeles.comptes import Compte
from app.modeles.rendez_vous import RendezVous
from app.routes.avis import AvisDemande, Decision, Texte
from app.routes.dependances import Administrateur, Base, CompteConnecte, maintenant
from app.routes.prestataires import mon_profil_ou_404
from app.services import avis as service_avis
from app.services import avis_clients as service
from app.services import messagerie
from app.services import rendez_vous as service_rdv

routeur = APIRouter(prefix="/api")


class AvisClientPublic(BaseModel):
    """Ce que tout le monde lit sur la page publique d'un client."""

    id: int
    note: int
    texte: str
    auteur: str  # « Karim Benali »
    mois: str  # « octobre 2026 »
    reponse: str | None


class AvisClientDetaille(AvisClientPublic):
    """Pour le prestataire qui l'a écrit, et pour le client qui l'a reçu."""

    rendez_vous_id: int
    titre: str  # le rendez-vous : « Fuite sous l'évier »
    modifiable_jusqu_au: datetime
    retire: bool
    cache_motif: str | None
    signale: bool


class ClientPublic(BaseModel):
    """« Marie D. » : jamais le nom complet, la ville, l'adresse, le téléphone, le mail, ses demandes ni ses rendez-vous."""

    id: int
    nom: str
    membre_depuis: str  # « septembre 2026 »
    note: float | None
    nombre_avis: int
    avis: list[AvisClientPublic]


class AvisClientSignale(BaseModel):
    avis: AvisClientPublic
    client: str
    signalement: str
    signale_le: datetime


def public(db: Base, a: AvisClient) -> AvisClientPublic:
    return AvisClientPublic(id=a.id, note=a.note, texte=a.texte, auteur=service.auteur(db, a),
                            mois=service_avis.mois(a.cree_le), reponse=a.reponse)


def detaille(db: Base, a: AvisClient) -> AvisClientDetaille:
    rdv = db.get_one(RendezVous, a.rendez_vous_id)
    return AvisClientDetaille(**public(db, a).model_dump(), rendez_vous_id=rdv.id, titre=rdv.titre,
                              modifiable_jusqu_au=service_avis.limite(rdv), retire=a.retire_le is not None,
                              cache_motif=a.cache_motif, signale=a.signale_le is not None)


# ---------- Pour tous ----------


@routeur.get("/clients/{client_id}/avis")
def page_publique_d_un_client(client_id: int, db: Base) -> ClientPublic:
    """Visible même sans compte : « Marie D. », membre depuis, la moyenne, et tous ses avis avec les réponses."""
    client = service.client_public_ou_404(db, client_id)
    note, nombre = service.note_de(db, client.id)
    return ClientPublic(id=client.id, nom=service.nom_public(client), membre_depuis=service_avis.mois(client.cree_le),
                        note=note, nombre_avis=nombre, avis=[public(db, a) for a in service.visibles(db, client.id)])


# ---------- La carte « Rendez-vous passé : noter » d'une conversation ----------


class ANoter(BaseModel):
    """Un rendez-vous tenu entre les deux personnes de la conversation, encore notable (30 jours)."""

    rendez_vous_id: int
    titre: str
    debut: datetime
    jusqu_au: datetime
    deja_note: bool  # par moi
    quand: datetime  # la fin du rendez-vous : place de la carte dans le fil


@routeur.get("/conversations/{conversation_id}/a-noter")
def rendez_vous_a_noter(conversation_id: int, db: Base, compte: CompteConnecte) -> list[ANoter]:
    """Dès que le rendez-vous est passé, la carte apparaît chez les deux : [Noter Karim B.] / [Noter Marie D.]."""
    conversation = messagerie.conversation_ou_404(db, compte, conversation_id)
    cote = messagerie.cote(db, compte, conversation)
    resultat = []
    for rdv in service.tenus_entre(db, conversation.client_id, conversation.prestataire_id, maintenant()):
        mien = service_avis.avis_du_rendez_vous(db, rdv.id) if cote == "client" else service.du_rendez_vous(db, rdv.id)
        resultat.append(ANoter(rendez_vous_id=rdv.id, titre=rdv.titre, debut=rdv.debut, jusqu_au=service_avis.limite(rdv),
                               deja_note=mien is not None, quand=rdv.fin))
    return resultat


# ---------- Le prestataire ----------


@routeur.post("/moi/prestataire/rendez-vous/{rdv_id}/avis-client", status_code=201)
def noter_le_client(rdv_id: int, donnees: AvisDemande, db: Base, compte: CompteConnecte) -> AvisClientDetaille:
    prestataire = mon_profil_ou_404(db, compte)
    rdv = service_rdv.rendez_vous_du_prestataire(db, prestataire, rdv_id)
    a = service.laisser(db, prestataire, rdv, donnees.note, donnees.texte, maintenant())
    db.commit()
    return detaille(db, a)


@routeur.post("/moi/prestataire/avis-clients/{avis_id}/modifier")
def modifier(avis_id: int, donnees: AvisDemande, db: Base, compte: CompteConnecte) -> AvisClientDetaille:
    a = service.modifier(db, mon_profil_ou_404(db, compte), avis_id, donnees.note, donnees.texte, maintenant())
    db.commit()
    return detaille(db, a)


@routeur.post("/moi/prestataire/avis-clients/{avis_id}/retirer")
def retirer(avis_id: int, db: Base, compte: CompteConnecte) -> AvisClientDetaille:
    a = service.retirer(db, mon_profil_ou_404(db, compte), avis_id, maintenant())
    db.commit()
    return detaille(db, a)


# ---------- Le client ----------


@routeur.get("/moi/avis-recus")
def mes_avis_recus(db: Base, compte: CompteConnecte) -> list[AvisClientDetaille]:
    """Ouvrir « Mes avis reçus » remet le compteur rouge à zéro."""
    liste = [detaille(db, a) for a in service.recus(db, compte)]
    service.marquer_vus(compte, maintenant())
    db.commit()
    return liste


@routeur.get("/moi/avis-recus/non-vus")
def avis_recus_non_vus(db: Base, compte: CompteConnecte) -> dict[str, int]:
    return {"nombre": service.non_vus(db, compte)}


@routeur.post("/moi/avis-recus/{avis_id}/repondre")
def repondre(avis_id: int, donnees: Texte, db: Base, compte: CompteConnecte) -> AvisClientDetaille:
    a = service.repondre(db, compte, avis_id, donnees.texte, maintenant())
    db.commit()
    return detaille(db, a)


@routeur.post("/moi/avis-recus/{avis_id}/signaler")
def signaler(avis_id: int, donnees: Texte, db: Base, compte: CompteConnecte) -> AvisClientDetaille:
    a = service.signaler(db, compte, avis_id, donnees.texte, maintenant())
    db.commit()
    return detaille(db, a)


# ---------- L'administrateur ----------


@routeur.get("/admin/avis-clients-signales")
def avis_signales(db: Base, _admin: Administrateur) -> list[AvisClientSignale]:
    return [AvisClientSignale(avis=public(db, a), client=service.nom_public(db.get_one(Compte, a.client_id)),
                              signalement=a.signalement or "", signale_le=a.signale_le or a.cree_le)
            for a in service.signales(db)]


@routeur.post("/admin/avis-clients/{avis_id}/decision")
def decider(avis_id: int, donnees: Decision, db: Base, admin: Administrateur) -> dict[str, bool]:
    a = service.decider(db, admin, avis_id, donnees.cacher, donnees.motif, maintenant())
    db.commit()
    return {"cache": a.cache_le is not None}
