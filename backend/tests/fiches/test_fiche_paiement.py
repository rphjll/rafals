"""Test de fiche du lot 5.1 : paiement par carte (sur un rendez-vous).
Ajout → modification → suppression du rendez-vous refusée tant que le paiement existe → suppression."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modeles.annonces import Annonce
from app.modeles.paiements import Paiement
from app.modeles.rendez_vous import RendezVous
from tests.fiches.outils import relire_et_comparer, valeurs
from tests.fiches.test_fiche_annonce import _supprimer, decor  # noqa: F401 (le décor est une fixture)

LE_14 = datetime(2027, 10, 14, 8, 0, tzinfo=UTC)


def test_fiche_paiement(base: Session, decor) -> None:  # noqa: F811
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
        "prix_centimes": 5000, "heures": None, "lieu": "chez_moi", "mode_paiement": "carte", "statut": "confirme",
        "absent": None, "absence_signalee_le": None, "contestation": None, "contestee_le": None, "absence_decision": None,
        "absence_decide_par_id": None, "absence_decide_le": None}))
    base.add(rdv)
    base.commit()
    # Valeurs imposées par les contraintes : versé (date de versement, pas de remboursement), puis remboursé
    imposees = [
        {"rendez_vous_id": rdv.id, "devis_id": None, "sorte": "rendez_vous", "montant_centimes": 5000, "commission_centimes": 250, "statut": "verse",
         "rembourse_le": None, "rembourse_centimes": None},
        {"rendez_vous_id": rdv.id, "devis_id": None, "sorte": "rendez_vous", "montant_centimes": 12000, "commission_centimes": 600, "statut": "rembourse",
         "verse_le": None, "rembourse_centimes": 11795},
    ]

    ajout = valeurs(Paiement, 1, imposees[0])
    p = Paiement(**ajout)
    base.add(p)
    base.commit()
    relire_et_comparer(base, Paiement, p.id, ajout)

    modification = valeurs(Paiement, 2, imposees[1])
    for rubrique, valeur in modification.items():
        setattr(p, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, Paiement, p.id, modification)

    base.delete(base.get_one(RendezVous, rdv.id))
    with pytest.raises(IntegrityError):
        base.commit()
    base.rollback()
    for modele, identifiant in ((Paiement, p.id), (RendezVous, rdv.id), (Annonce, annonce.id)):
        _supprimer(base, modele, identifiant)
