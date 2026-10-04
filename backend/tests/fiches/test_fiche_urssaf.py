"""Tests de fiche du lot 7.3 : accord donné à rafals (mandat URSSAF) et déclaration envoyée (fiche liée).
Ajout → modification → suppression du mandat refusée tant qu'une déclaration existe → suppression."""

from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modeles.prestataires import Prestataire
from app.modeles.urssaf import DeclarationUrssaf, MandatUrssaf
from tests.fiches.outils import relire_et_comparer, valeurs
from tests.fiches.test_fiche_annonce import _supprimer, decor  # noqa: F401 (le décor est une fixture)


def test_fiche_mandat_et_declaration_urssaf(base: Session, decor) -> None:  # noqa: F811
    _, prestataire, _, _ = decor
    # Valeurs imposées : numéro de 15 caractères tant que l'accord est en cours, vide dès qu'il est retiré
    ajout = valeurs(MandatUrssaf, 1, {"prestataire_id": prestataire.id, "numero_secu": "295073306304512", "retire_le": None})
    mandat = MandatUrssaf(**ajout)
    base.add(mandat)
    base.commit()
    relire_et_comparer(base, MandatUrssaf, mandat.id, ajout)

    modification = valeurs(MandatUrssaf, 2, {"prestataire_id": prestataire.id, "numero_secu": None})
    for rubrique, valeur in modification.items():
        setattr(mandat, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, MandatUrssaf, mandat.id, modification)

    # Fiche liée : une déclaration (le 1er jour d'un mois ; pour un trimestre : janvier, avril, juillet ou octobre)
    liens = {"prestataire_id": prestataire.id, "mandat_id": mandat.id}
    ajout_declaration = valeurs(DeclarationUrssaf, 1, liens | {"periodicite": "mois", "periode_debut": date(2026, 9, 1), "nature": "services"})
    declaration = DeclarationUrssaf(**ajout_declaration)
    base.add(declaration)
    base.commit()
    relire_et_comparer(base, DeclarationUrssaf, declaration.id, ajout_declaration)
    modification_declaration = valeurs(DeclarationUrssaf, 2, liens | {"periodicite": "trimestre", "periode_debut": date(2026, 7, 1),
                                                                      "nature": "liberale"})
    for rubrique, valeur in modification_declaration.items():
        setattr(declaration, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, DeclarationUrssaf, declaration.id, modification_declaration)

    # Ni l'accord ni le prestataire ne peuvent être effacés tant qu'une déclaration existe
    for modele, identifiant in ((MandatUrssaf, mandat.id), (Prestataire, prestataire.id)):
        base.delete(base.get_one(modele, identifiant))
        with pytest.raises(IntegrityError):
            base.commit()
        base.rollback()
    for modele, identifiant in ((DeclarationUrssaf, declaration.id), (MandatUrssaf, mandat.id)):
        _supprimer(base, modele, identifiant)
