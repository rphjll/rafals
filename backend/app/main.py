"""Serveur de rafals."""

import asyncio
import logging
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import reglages
from app.db import moteur
from app.routes import (
    abonnements, accords, activite, administration, agenda, avis, clients, comptes, creation_entreprise, demandes, devis, factures, messagerie, metiers,
    notifications, paiements, propositions,
    prestataires, recherche, rendez_vous, services_en_plus, avis_clients,
)
from app.services import abonnements as service_abonnements
from app.services import alertes as service_alertes
from app.services import avis as service_avis
from app.services import clients as service_clients
from app.services import creation_entreprise as service_creation
from app.services import demarches as service_demarches
from app.services import devis as service_devis
from app.services import factures as service_factures
from app.services import messagerie as service_messagerie
from app.services import paiements as service_paiements
from app.services import prestataires as service_prestataires
from app.services import propositions as service_propositions
from app.services import rendez_vous as service_rendez_vous
from app.services.erreurs import ErreurRegle

journal_serveur = logging.getLogger("rafals")


def _dans_une_session(travail: Callable[[Session, datetime], object]) -> Callable[[], object]:
    """Lance un travail de fond avec sa propre session de base, puis valide (commit)."""

    def lancer() -> object:
        with Session(moteur) as db:
            resultat = travail(db, datetime.now(UTC))
            db.commit()
        return resultat

    return lancer


async def _tache_periodique(nom: str, intervalle_secondes: int, travail: Callable[[], object]) -> None:
    """Refait un travail à intervalle régulier ; une erreur est notée mais n'arrête jamais le serveur."""
    while True:
        await asyncio.sleep(intervalle_secondes)
        try:
            resultat = await asyncio.to_thread(travail)
            journal_serveur.info("%s : %s", nom, resultat)
        except Exception:
            journal_serveur.exception("Échec de la tâche « %s »", nom)


@asynccontextmanager
async def cycle_de_vie(_app: FastAPI) -> AsyncIterator[None]:
    taches = [
        # SIRET restés « à vérifier » (service de l'État en panne) : nouvel essai (lot 2.4)
        asyncio.create_task(_tache_periodique(
            "revérification des SIRET", reglages.SIRET_REVERIFICATION_MINUTES * 60,
            _dans_une_session(service_prestataires.reverifier_sirets_en_attente),
        )),
        # Comptes inactifs depuis 3 ans : mail, puis fermeture 30 jours après (lot 2.6)
        asyncio.create_task(_tache_periodique(
            "comptes inactifs (prévenus, fermés)", 24 * 60 * 60, _dans_une_session(service_clients.traiter_inactifs),
        )),
        # Métier principal arrivé à sa date de fin : un métier secondaire devient principal (lot 3.1)
        asyncio.create_task(_tache_periodique(
            "fins de métier", 60 * 60, _dans_une_session(service_prestataires.appliquer_fins_de_metier),
        )),
        # Demandes sans réponse après 24 h, rappels (lot 4.3)
        asyncio.create_task(_tache_periodique(
            "rendez-vous (expirations, rappels)", reglages.TACHE_RENDEZ_VOUS_MINUTES * 60,
            _dans_une_session(service_rendez_vous.traiter),
        )),
        # Paiements par carte : remboursements, versements 48 h après, paiements jamais terminés (lot 5.1)
        asyncio.create_task(_tache_periodique(
            "paiements (remboursements, versements)", reglages.TACHE_PAIEMENTS_MINUTES * 60,
            _dans_une_session(service_paiements.traiter),
        )),
        # Messages pas lus au bout de 15 minutes : un mail ; conversations sans message depuis 3 ans : effacées (lot 8.1)
        asyncio.create_task(_tache_periodique(
            "messagerie (mails, effacement)", reglages.TACHE_MESSAGERIE_MINUTES * 60,
            _dans_une_session(service_messagerie.traiter),
        )),
        # Demandes arrivées à leur fin : expirées ; 3 jours avant, un mail « prolongez-la » ; propositions dont l'heure
        # est passée : expirées (lot 8.3)
        asyncio.create_task(_tache_periodique(
            "demandes et propositions (expirations, rappels)", reglages.TACHE_DEMANDES_MINUTES * 60,
            _dans_une_session(service_propositions.traiter),
        )),
        # Résumé de 18 h des demandes du jour, pour les prestataires qui l'ont choisi (lot 8.5)
        asyncio.create_task(_tache_periodique(
            "alertes (résumé de 18 h)", 15 * 60, _dans_une_session(service_alertes.envoyer_resumes),
        )),
        # Devis sans réponse après « Valable jusqu'au », rappels du solde (lot 5.3)
        asyncio.create_task(_tache_periodique(
            "devis (expirations, rappels du solde)", 60 * 60, _dans_une_session(service_devis.traiter),
        )),
        # Commissions du mois passé : une facture de rafals par prestataire, faite une seule fois (lot 5.5)
        asyncio.create_task(_tache_periodique(
            "factures de commission", 60 * 60, _dans_une_session(service_factures.facturer_les_commissions),
        )),
        # Rappels de déclaration URSSAF : 7 jours avant la date limite, puis la veille (lot 6.3)
        asyncio.create_task(_tache_periodique(
            "rappels URSSAF", 60 * 60, _dans_une_session(service_demarches.envoyer_rappels),
        )),
        # Dossiers de création d'auto-entreprise : réponse du guichet de l'État, rappels, brouillons abandonnés (lot 7.1)
        asyncio.create_task(_tache_periodique(
            "dossiers de création d'entreprise", 60 * 60, _dans_une_session(service_creation.suivre),
        )),
        # Rappel « Comment s'est passé votre rendez-vous ? » le lendemain (lot 4.7)
        asyncio.create_task(_tache_periodique(
            "rappels d'avis", 60 * 60, _dans_une_session(service_avis.envoyer_rappels),
        )),
        # Abonnements : « Léa reprend son activité » à 8 h le jour où son absence se termine (demande du 21/10/2026)
        asyncio.create_task(_tache_periodique(
            "retours d'absence pour les abonnés", 60 * 60, _dans_une_session(service_abonnements.traiter),
        )),
    ]
    yield
    for tache in taches:
        tache.cancel()


app = FastAPI(title="rafals", lifespan=cycle_de_vie)
app.include_router(comptes.routeur)
app.include_router(accords.routeur)
app.include_router(administration.routeur)
app.include_router(metiers.routeur)
app.include_router(prestataires.routeur)
app.include_router(agenda.routeur)
app.include_router(recherche.routeur)
app.include_router(rendez_vous.routeur)
app.include_router(avis.routeur)
app.include_router(avis_clients.routeur)
app.include_router(clients.routeur)
app.include_router(paiements.routeur)
app.include_router(devis.routeur)
app.include_router(factures.routeur)
app.include_router(services_en_plus.routeur)
app.include_router(creation_entreprise.routeur)
app.include_router(messagerie.routeur)
app.include_router(demandes.routeur)
app.include_router(propositions.routeur)
app.include_router(activite.routeur)
app.include_router(notifications.routeur)
app.include_router(abonnements.routeur)


@app.exception_handler(ErreurRegle)
def regle_non_respectee(_requete: Request, erreur: ErreurRegle) -> JSONResponse:
    """Une règle refuse l'action : le message est montré tel quel à l'utilisateur."""
    return JSONResponse(status_code=erreur.code_http, content={"detail": erreur.message})


@app.get("/api/etat")
def etat() -> dict[str, str]:
    """Répond pour prouver que le serveur tourne (lu par la page d'accueil provisoire)."""
    return {"message": "Le serveur de rafals répond."}


@app.get("/health")
def health() -> JSONResponse:
    """Adresse de contrôle : le serveur tourne-t-il, et joint-il la base avec le bon compte ?"""
    try:
        with moteur.connect() as connexion:
            compte = connexion.execute(text("SELECT current_user")).scalar_one()
    except Exception as erreur:  # la base ne répond pas : on le dit au lieu de planter
        return JSONResponse(
            status_code=503,
            content={"serveur": "ok", "base": "injoignable", "detail": str(erreur)},
        )
    return JSONResponse(content={"serveur": "ok", "base": "ok", "compte": compte})
