"""Test de fiche du lot 4.3 : rendez-vous (client, prestataire, annonce, commune), puis fiche liée : un rendez-vous
qui en remplace un autre (déplacement). Suppression du rendez-vous remplacé refusée tant que le lien existe."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modeles.annonces import Annonce
from app.modeles.comptes import Compte
from app.modeles.prestataires import Commune
from app.modeles.rendez_vous import RendezVous
from tests.fiches.outils import relire_et_comparer, valeurs
from tests.fiches.test_fiche_annonce import _supprimer, decor  # noqa: F401 (le décor est une fixture)

LE_14 = datetime(2027, 10, 14, 8, 0, tzinfo=UTC)


def test_fiche_rendez_vous(base: Session, decor) -> None:  # noqa: F811
    compte, prestataire, (plombier, _), _ = decor
    annonce = Annonce(**valeurs(Annonce, 1, {
        "prestataire_id": prestataire.id, "metier_id": plombier.id, "forme_prix": "fixe", "prix_centimes": 5000,
        "duree_minutes": 60, "heures_min": None, "heures_max": None, "lieu": "chez_client", "paiement_especes": True,
        "statut": "en_ligne"}))
    base.add(annonce)
    base.commit()
    talence = base.scalar(select(Commune).where(Commune.code_insee == "33522"))
    liens = {"client_id": compte.id, "prestataire_id": prestataire.id, "annonce_id": annonce.id, "remplace_id": None}
    # Valeurs imposées par les contraintes : fin après début, listes de valeurs, adresse complète, attente limitée
    imposees = [
        {**liens, "commune_id": talence.id, "code_postal": "33400", "debut": LE_14, "fin": LE_14 + timedelta(hours=1),
         "prix_centimes": 5000, "heures": None, "lieu": "chez_client", "mode_paiement": "especes", "statut": "en_attente"},
        {**liens, "commune_id": None, "adresse_ligne": None, "code_postal": None, "debut": LE_14 + timedelta(days=1),
         "fin": LE_14 + timedelta(days=1, hours=3), "prix_centimes": 7500, "heures": 3, "lieu": "chez_moi",
         "mode_paiement": "carte", "statut": "confirme"},
    ]

    ajout = valeurs(RendezVous, 1, imposees[0])
    rdv = RendezVous(**ajout)
    base.add(rdv)
    base.commit()
    relire_et_comparer(base, RendezVous, rdv.id, ajout)

    modification = valeurs(RendezVous, 2, imposees[1])
    for rubrique, valeur in modification.items():
        setattr(rdv, rubrique, valeur)
    base.commit()
    relire_et_comparer(base, RendezVous, rdv.id, modification)

    # Fiche liée : le rendez-vous qui le remplace (déplacement)
    nouveau = RendezVous(**valeurs(RendezVous, 2, {**imposees[1], "remplace_id": rdv.id}))
    base.add(nouveau)
    base.commit()
    base.delete(base.get_one(RendezVous, rdv.id))
    with pytest.raises(IntegrityError):
        base.commit()
    base.rollback()

    for modele, identifiant in ((RendezVous, nouveau.id), (RendezVous, rdv.id), (Annonce, annonce.id)):
        _supprimer(base, modele, identifiant)
    assert base.get(Compte, compte.id) is not None
