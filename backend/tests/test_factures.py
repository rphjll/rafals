"""Factures : créées toutes seules après un paiement, avoirs, [Payé] en espèces, devis (arrhes, solde, en direct),
commission mensuelle de rafals, PDF (RM-FACTURES.md ; lot 5.5). Stripe est simulé (conftest.py)."""

from datetime import UTC, datetime

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import config
from app.services import factures
from tests.test_absences import passe
from tests.test_agenda import MARDI, lea  # noqa: F401 (fixtures)
from tests.test_annonces import AUJOURD_HUI, fabrique_prestataire, menage, metiers, publier, siret_verifie  # noqa: F401
from tests.test_devis import accepte_carte, au_debut_des_travaux, envoye, paul, paul_carte  # noqa: F401 (fixtures)
from tests.test_paiements import lea_carte, paye, traiter  # noqa: F401 (fixtures)
from tests.test_rendez_vous import a, dupont, reserver  # noqa: F401 (fixtures)

ANNEE = AUJOURD_HUI.year


def du_client(compte) -> list[dict]:
    return compte.client.get("/api/moi/factures").json()


def du_prestataire(compte) -> list[dict]:
    return compte.client.get("/api/moi/prestataire/factures").json()


# ---------- Rendez-vous ----------


def test_facture_creee_apres_un_paiement_par_carte(paye, lea_carte, dupont, fabrique_compte) -> None:  # noqa: F811
    facture = du_client(dupont)[0]
    pdf = dupont.client.get(f"/api/factures/{facture['id']}/pdf")
    curieux = fabrique_compte().client.get(f"/api/factures/{facture['id']}/pdf")

    assert (facture["numero"], facture["sorte"], facture["ttc_centimes"]) == (f"F-{ANNEE}-0001", "vente", 5000)
    assert facture["moyen_paiement"] == "carte" and facture["objet"].startswith("Coupe carte")
    assert facture["acheteur"] == "Essai ZZTEST" and "Karim Benali" in facture["vendeur"]
    assert [f["id"] for f in du_prestataire(lea_carte)] == [facture["id"]]
    assert pdf.status_code == 200 and pdf.headers["content-type"] == "application/pdf" and pdf.content.startswith(b"%PDF-1.4")
    assert f"F-{ANNEE}-0001".encode() in pdf.content and b"293 B" in pdf.content and b"au nom et pour le compte de" in pdf.content
    assert curieux.status_code == 404


@pytest.mark.parametrize(("qui_annule", "rendu"), [("client", -4900), ("prestataire", -5000)])
def test_un_remboursement_donne_un_avoir(qui_annule, rendu, paye, lea_carte, dupont, base: Session) -> None:  # noqa: F811
    if qui_annule == "client":
        dupont.client.post(f"/api/moi/rendez-vous/{paye}/annuler")
    else:
        lea_carte.client.post(f"/api/moi/prestataire/rendez-vous/{paye}/annuler", json={"motif": "Malade"})
    traiter(base)

    avoir, facture = du_client(dupont)[:2]
    assert (avoir["sorte"], avoir["numero"], avoir["ttc_centimes"]) == ("avoir", f"F-{ANNEE}-0002", rendu)
    assert avoir["avoir_de"] == facture["numero"] == f"F-{ANNEE}-0001"
    traiter(base)
    assert len(du_client(dupont)) == 2  # un seul avoir, même si la tâche repasse


def test_paye_en_especes_seulement_avec_un_siret(lea, dupont, base: Session) -> None:  # noqa: F811
    rdv = reserver(dupont, lea.annonce, a(MARDI, 10)).json()["id"]
    passe(base, rdv)
    sans_siret = lea.client.post(f"/api/moi/prestataire/rendez-vous/{rdv}/paye", json={"moyen": "especes"})
    siret_verifie(base, lea)
    paye_ = lea.client.post(f"/api/moi/prestataire/rendez-vous/{rdv}/paye", json={"moyen": "especes"})
    deux_fois = lea.client.post(f"/api/moi/prestataire/rendez-vous/{rdv}/paye", json={"moyen": "especes"})

    assert sans_siret.status_code == 400 and "SIRET vérifié" in sans_siret.json()["detail"]
    assert paye_.status_code == 200 and paye_.json()["paye_direct_moyen"] == "especes"
    assert deux_fois.status_code == 400 and "déjà" in deux_fois.json()["detail"]
    facture = du_client(dupont)[0]
    assert (facture["ttc_centimes"], facture["moyen_paiement"]) == (5000, "especes")
    assert "esp" in dupont.client.get(f"/api/factures/{facture['id']}/pdf").content.decode("cp1252", errors="replace")


def test_avec_tva_le_total_reste_le_prix_paye(lea, dupont, base: Session) -> None:  # noqa: F811
    siret_verifie(base, lea)
    lea.client.post("/api/moi/prestataire/tva", json={"facture_tva": True})
    rdv = reserver(dupont, lea.annonce, a(MARDI, 10)).json()["id"]
    passe(base, rdv)
    lea.client.post(f"/api/moi/prestataire/rendez-vous/{rdv}/paye", json={"moyen": "cheque"})

    facture = base.get_one(factures.Facture, du_client(dupont)[0]["id"])
    t = factures.totaux(base, facture)
    assert facture.mention_tva is None and (t.ht, t.tva, t.ttc) == (4167, 833, 5000)


# ---------- Devis ----------


def test_devis_par_carte_facture_d_arrhes_puis_de_solde(accepte_carte, paul_carte, dupont, base: Session, faux_stripe, client) -> None:  # noqa: F811
    au_debut_des_travaux(base, accepte_carte)
    paul_carte.client.post(f"/api/moi/prestataire/devis/{accepte_carte}/termine")
    dupont.client.post(f"/api/moi/devis/{accepte_carte}/payer-solde")
    faux_stripe.envoyer(client, faux_stripe.payer())

    solde, arrhes = du_client(dupont)[:2]
    assert (arrhes["numero"], arrhes["ttc_centimes"]) == (f"F-{ANNEE}-0001", 35700) and arrhes["objet"].startswith("Arrhes")
    assert (solde["numero"], solde["ttc_centimes"]) == (f"F-{ANNEE}-0002", 83300) and solde["objet"].startswith("Solde")
    lignes = [ligne.libelle for ligne in factures.lignes_de(base, base.get_one(factures.Facture, solde["id"]))]
    assert lignes[:3] == ["Parpaings", "Main-d'œuvre", "Enduit"] and lignes[3].startswith("Arrhes déjà payées")


def test_devis_paye_en_direct_une_facture_du_total(paul, dupont, envoye, base: Session) -> None:  # noqa: F811
    dupont.client.post(f"/api/moi/devis/{envoye}/accepter", json={"mode_paiement": "direct"})
    paul.client.post(f"/api/moi/prestataire/devis/{envoye}/paye", json={"moyen": "cheque"})

    facture = du_client(dupont)[0]
    assert (facture["ttc_centimes"], facture["moyen_paiement"]) == (119000, "cheque") and "Devis D-" in facture["objet"]


# ---------- Commission de rafals ----------


def test_commissions_du_mois_passe_une_seule_facture(paye, lea_carte, base: Session, monkeypatch) -> None:  # noqa: F811
    base.execute(text("UPDATE paiement SET paye_le = date_trunc('month', now()) - interval '10 days' WHERE rendez_vous_id = :id"),
                 {"id": paye})
    base.commit()
    sans_identite = factures.facturer_les_commissions(base, datetime.now(UTC))
    monkeypatch.setattr(config, "RAFALS_NOM", "ZZTEST rafals")
    monkeypatch.setattr(config, "RAFALS_SIRET", "12345678900012")
    monkeypatch.setattr(config, "RAFALS_ADRESSE", "1 rue ZZTEST, 33000 Bordeaux")
    premiere = factures.facturer_les_commissions(base, datetime.now(UTC))
    seconde = factures.facturer_les_commissions(base, datetime.now(UTC))
    base.commit()

    assert sans_identite["factures"] == 0  # rafals n'est pas encore une entreprise : rien n'est facturé
    assert premiere["factures"] == 1 and seconde["factures"] == 0
    commission = next(f for f in du_prestataire(lea_carte) if f["sorte"] == "commission")
    assert commission["numero"].startswith(f"R-{ANNEE}-") and commission["ttc_centimes"] == 250
    assert commission["objet"].startswith("Commissions d") and commission["vendeur"] == "ZZTEST rafals"


def test_mois_passe_en_janvier() -> None:
    debut, fin = factures._mois_passe(datetime(2027, 1, 3, 12, tzinfo=UTC))

    assert (debut.isoformat(), fin.isoformat()) == ("2026-12-01", "2027-01-01")
