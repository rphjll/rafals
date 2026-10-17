"""Test de fiche du lot 3.1 : local (l'adresse où le prestataire reçoit). Les tables annonce et photo_annonce ont été
supprimées au lot 9.4 (db/schema_v29.sql) avec leur test.
Ici aussi : le décor commun des tests de fiche (un compte et un prestataire d'essai) et la proposition d'essai dont
naît tout rendez-vous depuis le lot 9.4."""

from datetime import timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modeles.comptes import Compte
from app.modeles.demandes import Proposition
from app.modeles.locaux import Local
from app.modeles.messagerie import Conversation
from app.modeles.metiers import Metier
from app.modeles.prestataires import Commune, Prestataire
from tests.fiches.outils import relire_et_comparer, valeurs


def _supprimer(base: Session, modele: type, identifiant: int) -> None:
    base.delete(base.get_one(modele, identifiant))
    base.commit()
    base.expire_all()
    assert base.get(modele, identifiant) is None


def proposition_d_essai(base: Session, client: Compte, prestataire: Prestataire, metier: Metier,
                        conversation_id: int | None = None) -> Proposition:
    """Une proposition acceptée (et sa conversation si on n'en donne pas) : un rendez-vous vient toujours d'une
    proposition depuis le lot 9.4. À effacer avec effacer_proposition_d_essai."""
    if conversation_id is None:
        conversation = Conversation(**valeurs(Conversation, 1, {
            "client_id": client.id, "prestataire_id": prestataire.id, "bloquee_par_id": None, "bloquee_le": None}))
        base.add(conversation)
        base.commit()
        conversation_id = conversation.id
    ajout = valeurs(Proposition, 1, {"conversation_id": conversation_id, "remplace_id": None, "demande_id": None,
                                     "metier_id": metier.id, "lieu": "chez_client", "statut": "acceptee", "paiement_especes": True})
    ajout["fin"] = ajout["debut"] + timedelta(hours=1)
    proposition = Proposition(**ajout)
    base.add(proposition)
    base.commit()
    return proposition


def effacer_proposition_d_essai(base: Session, *propositions: Proposition) -> None:
    conversations = {p.conversation_id for p in propositions}
    for proposition in propositions:
        _supprimer(base, Proposition, proposition.id)
    for conversation_id in conversations:
        _supprimer(base, Conversation, conversation_id)


@pytest.fixture
def decor(base: Session):
    """Un compte et un prestataire d'essai (plombier à Pessac), effacés à la fin."""
    compte = Compte(**valeurs(Compte, 1))
    base.add(compte)
    base.commit()
    plombier = base.scalar(select(Metier).where(Metier.code == "plombier"))
    electricien = base.scalar(select(Metier).where(Metier.code == "electricien"))
    pessac = base.scalar(select(Commune).where(Commune.code_insee == "33318"))
    talence = base.scalar(select(Commune).where(Commune.code_insee == "33522"))
    assert plombier and electricien and pessac and talence
    prestataire = Prestataire(**valeurs(Prestataire, 1, {
        "compte_id": compte.id, "metier_principal_id": plombier.id, "commune_id": pessac.id, "photo_id": None,
        "siret": None, "siret_statut": "absent", "statut": "actif", "metier_principal_suivant_id": None, "agenda_pas_minutes": 15, "annulation_delai_heures": 24,
        "declaration_periodicite": None, "lieu": "chez_client", "alerte_mail": "chaque_demande",
    }))
    base.add(prestataire)
    base.commit()
    yield compte, prestataire, (plombier, electricien), (pessac, talence)
    base.rollback()
    for modele, identifiant in ((Prestataire, prestataire.id), (Compte, compte.id)):
        _supprimer(base, modele, identifiant)


def test_fiche_local(base: Session, decor) -> None:
    _, prestataire, _, (pessac, talence) = decor
    ajout = valeurs(Local, 1, {"prestataire_id": prestataire.id, "commune_id": pessac.id, "code_postal": "33600"})
    local = Local(**ajout)
    base.add(local)
    base.commit()
    relire_et_comparer(base, Local, local.id, ajout)

    modification = valeurs(Local, 2, {"prestataire_id": prestataire.id, "commune_id": talence.id, "code_postal": "33400"})
    for rubrique, valeur in modification.items():
        setattr(local, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, Local, local.id, modification)

    # Le prestataire ne peut pas disparaître tant que son local existe
    base.delete(base.get_one(Prestataire, prestataire.id))
    with pytest.raises(IntegrityError):
        base.commit()
    base.rollback()
    _supprimer(base, Local, local.id)
