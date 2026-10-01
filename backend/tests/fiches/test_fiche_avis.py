"""Tests de fiche du lot 4.7 : avis (sur un rendez-vous) et mot interdit.
Avis : ajout → modification → suppression du rendez-vous refusée tant que l'avis existe → suppression."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modeles.annonces import Annonce
from app.modeles.avis import Avis, MotInterdit
from app.modeles.rendez_vous import RendezVous
from tests.fiches.outils import relire_et_comparer, valeurs
from tests.fiches.test_fiche_annonce import _supprimer, decor  # noqa: F401 (le décor est une fixture)

LE_14 = datetime(2027, 10, 14, 8, 0, tzinfo=UTC)


def test_fiche_avis(base: Session, decor) -> None:  # noqa: F811
    compte, prestataire, (plombier, _), _ = decor
    annonce = Annonce(**valeurs(Annonce, 1, {
        "prestataire_id": prestataire.id, "metier_id": plombier.id, "forme_prix": "fixe", "prix_centimes": 5000,
        "duree_minutes": 60, "heures_min": None, "heures_max": None, "lieu": "chez_moi", "paiement_especes": True,
        "statut": "en_ligne"}))
    base.add(annonce)
    base.commit()
    rdv = RendezVous(**valeurs(RendezVous, 1, {
        "client_id": compte.id, "prestataire_id": prestataire.id, "annonce_id": annonce.id, "remplace_id": None,
        "commune_id": None, "adresse_ligne": None, "code_postal": None, "debut": LE_14, "fin": LE_14 + timedelta(hours=1),
        "prix_centimes": 5000, "heures": None, "lieu": "chez_moi", "mode_paiement": "especes", "statut": "confirme",
        "absent": None, "absence_signalee_le": None, "contestation": None, "contestee_le": None, "absence_decision": None,
        "absence_decide_par_id": None, "absence_decide_le": None}))
    base.add(rdv)
    base.commit()
    liens = {"rendez_vous_id": rdv.id, "client_id": compte.id, "prestataire_id": prestataire.id, "cache_par_id": compte.id}

    ajout = valeurs(Avis, 1, {**liens, "note": 5})
    avis = Avis(**ajout)
    base.add(avis)
    base.commit()
    relire_et_comparer(base, Avis, avis.id, ajout)

    modification = valeurs(Avis, 2, {**liens, "note": 2})
    for rubrique, valeur in modification.items():
        setattr(avis, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, Avis, avis.id, modification)

    base.delete(base.get_one(RendezVous, rdv.id))
    with pytest.raises(IntegrityError):
        base.commit()
    base.rollback()
    for modele, identifiant in ((Avis, avis.id), (RendezVous, rdv.id), (Annonce, annonce.id)):
        _supprimer(base, modele, identifiant)


def test_fiche_mot_interdit(base: Session, decor) -> None:  # noqa: F811
    compte, *_ = decor
    ajout = valeurs(MotInterdit, 1, {"ajoute_par_id": compte.id})
    mot = MotInterdit(**ajout)
    base.add(mot)
    base.commit()
    relire_et_comparer(base, MotInterdit, mot.id, ajout)
    modification = valeurs(MotInterdit, 2, {"ajoute_par_id": None})
    for rubrique, valeur in modification.items():
        setattr(mot, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, MotInterdit, mot.id, modification)
    _supprimer(base, MotInterdit, mot.id)
