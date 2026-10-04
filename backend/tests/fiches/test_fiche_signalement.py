"""Tests de fiche du lot 6.3 : signalement et rappel de déclaration URSSAF.
Ajout → modification → suppression du prestataire refusée tant que la fiche existe → suppression."""

from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modeles.prestataires import Prestataire
from app.modeles.signalements import RappelDeclaration, Signalement
from tests.fiches.outils import relire_et_comparer, valeurs
from tests.fiches.test_fiche_annonce import _supprimer, decor  # noqa: F401 (le décor est une fixture)


def test_fiche_signalement(base: Session, decor) -> None:  # noqa: F811
    compte, prestataire, _, _ = decor
    liens = {"auteur_id": compte.id, "prestataire_id": prestataire.id, "annonce_id": None}
    # Valeurs imposées : motif de 10 à 1000 caractères, statut dans la liste, traitement cohérent (date + auteur)
    ajout = valeurs(Signalement, 1, {**liens, "statut": "a_traiter", "traite_par_id": None, "traite_le": None, "decision": None,
                                     "motif": "Prix mensonger, il demande 80 € sur place"})
    signalement = Signalement(**ajout)
    base.add(signalement)
    base.commit()
    relire_et_comparer(base, Signalement, signalement.id, ajout)

    modification = valeurs(Signalement, 2, {**liens, "statut": "suivi", "traite_par_id": compte.id,
                                            "motif": "Faux profil, la photo est volée"})
    for rubrique, valeur in modification.items():
        setattr(signalement, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, Signalement, signalement.id, modification)

    # Fiche liée : le prestataire signalé ne peut pas être effacé tant que le signalement existe
    base.delete(base.get_one(Prestataire, prestataire.id))
    with pytest.raises(IntegrityError):
        base.commit()
    base.rollback()
    _supprimer(base, Signalement, signalement.id)


def test_fiche_rappel_declaration(base: Session, decor) -> None:  # noqa: F811
    _, prestataire, _, _ = decor
    ajout = valeurs(RappelDeclaration, 1, {"prestataire_id": prestataire.id, "sorte": "sept_jours", "periode_debut": date(2026, 10, 1)})
    rappel = RappelDeclaration(**ajout)
    base.add(rappel)
    base.commit()
    relire_et_comparer(base, RappelDeclaration, rappel.id, ajout)

    modification = valeurs(RappelDeclaration, 2, {"prestataire_id": prestataire.id, "sorte": "veille", "periode_debut": date(2026, 11, 1)})
    for rubrique, valeur in modification.items():
        setattr(rappel, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, RappelDeclaration, rappel.id, modification)

    base.delete(base.get_one(Prestataire, prestataire.id))
    with pytest.raises(IntegrityError):
        base.commit()
    base.rollback()
    _supprimer(base, RappelDeclaration, rappel.id)
