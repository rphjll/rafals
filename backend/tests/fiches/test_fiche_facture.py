"""Test de fiche du lot 5.5 : facture (+ ligne liée, + avoir lié).
Ajout → modification → fiches liées (suppression de la facture refusée tant qu'une ligne ou un avoir existe) → suppression."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modeles.factures import Facture, LigneFacture
from tests.fiches.outils import relire_et_comparer, valeurs
from tests.fiches.test_fiche_local import _supprimer, decor  # noqa: F401 (le décor est une fixture)


def test_fiche_facture_ligne_et_avoir(base: Session, decor) -> None:  # noqa: F811
    compte, prestataire, _, _ = decor
    liens = {"prestataire_id": prestataire.id, "rendez_vous_id": None, "devis_id": None, "paiement_id": None}
    # Valeurs imposées : sorte et moyen de paiement dans leurs listes, année, client selon la sorte, avoir cohérent
    ajout = valeurs(Facture, 1, {**liens, "client_id": compte.id, "avoir_de_id": None, "sorte": "vente", "annee": 2027,
                                 "numero": 1, "moyen_paiement": "carte"})
    facture = Facture(**ajout)
    base.add(facture)
    base.commit()
    relire_et_comparer(base, Facture, facture.id, ajout)

    modification = valeurs(Facture, 2, {**liens, "client_id": None, "avoir_de_id": None, "sorte": "commission", "annee": 2027,
                                        "numero": 2, "moyen_paiement": None})
    for rubrique, valeur in modification.items():
        setattr(facture, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, Facture, facture.id, modification)

    # Fiches liées : une ligne, puis un avoir qui corrige la facture
    ajout_lie = valeurs(LigneFacture, 1, {"facture_id": facture.id, "quantite_centiemes": 100, "prix_unitaire_centimes": 5000,
                                          "tva_pour_mille": None})
    ligne = LigneFacture(**ajout_lie)
    base.add(ligne)
    base.commit()
    relire_et_comparer(base, LigneFacture, ligne.id, ajout_lie)
    modification_liee = valeurs(LigneFacture, 2, {"facture_id": facture.id, "quantite_centiemes": 250,
                                                  "prix_unitaire_centimes": -1200, "tva_pour_mille": 100})
    for rubrique, valeur in modification_liee.items():
        setattr(ligne, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, LigneFacture, ligne.id, modification_liee)

    avoir = Facture(**valeurs(Facture, 1, {**liens, "client_id": compte.id, "avoir_de_id": facture.id, "sorte": "avoir",
                                           "annee": 2027, "numero": 3, "moyen_paiement": "carte"}))
    base.add(avoir)
    base.commit()
    base.delete(base.get_one(Facture, facture.id))
    with pytest.raises(IntegrityError):
        base.commit()
    base.rollback()
    for modele, identifiant in ((Facture, avoir.id), (LigneFacture, ligne.id), (Facture, facture.id)):
        _supprimer(base, modele, identifiant)
