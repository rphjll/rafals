"""Paiement par carte (Stripe Connect) : activer, payer en réservant, rembourser, verser 48 h après, absences
(RM-PAIEMENTS.md ; lot 5.1). Stripe est simulé (conftest.py, FauxStripe) : aucune vraie carte, aucun appel à internet."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.paiements import Paiement
from app.services import paiements
from tests.test_absences import passe, vieillir_signalement
from tests.test_agenda import MARDI, heures, lea  # noqa: F401 (fixtures)
from tests.test_prestataires import fabrique_prestataire, metiers, siret_verifie  # noqa: F401 (fixtures)
from tests.test_rendez_vous import a, dupont, reserver, statut  # noqa: F401 (fixtures)


def plus_tard(**duree) -> datetime:
    return datetime.now(UTC) + timedelta(**duree)


def traiter(base: Session, quand: datetime | None = None) -> dict[str, int]:
    """La tâche de fond des paiements, lancée « maintenant » ou plus tard."""
    base.expire_all()
    resultat = paiements.traiter(base, quand or datetime.now(UTC))
    base.commit()
    return resultat


def paiement(base: Session, rdv_id: int) -> Paiement:
    base.expire_all()
    p = paiements.du_rendez_vous(base, rdv_id)
    assert p is not None
    return p


def appels(faux_stripe, chemin: str) -> list[dict]:
    return [c for c in faux_stripe.appels if c["chemin"].startswith(chemin)]


@pytest.fixture
def lea_carte(lea, base: Session, faux_stripe, client):  # noqa: F811
    """Léa, SIRET vérifié, carte activée chez Stripe : ses propositions peuvent être payées par carte."""
    siret_verifie(base, lea)
    assert lea.client.post("/api/moi/prestataire/paiement-carte", json={"mandat": True}).status_code == 200
    compte = list(faux_stripe.comptes)[-1]
    assert faux_stripe.envoyer(client, faux_stripe.compte_verifie(compte)).status_code == 200
    lea.compte_stripe = compte
    return lea


@pytest.fixture
def paye(lea_carte, dupont, faux_stripe, client):  # noqa: F811
    """Mme Dupont a réservé mardi à 10 h et payé 50 € par carte."""
    rdv = reserver(dupont, lea_carte, a(MARDI, 10), mode_paiement="carte").json()
    assert faux_stripe.envoyer(client, faux_stripe.payer()).status_code == 200
    return rdv["id"]


# ---------- Activer la carte ----------


def test_commission_de_5_pourcent_arrondie() -> None:
    assert (paiements.commission(5000), paiements.commission(12000), paiements.commission(3333)) == (250, 600, 167)


def test_activer_demande_un_siret_verifie_puis_le_mandat(lea, base: Session, faux_stripe, client) -> None:  # noqa: F811
    sans_siret = lea.client.post("/api/moi/prestataire/paiement-carte", json={"mandat": True})
    siret_verifie(base, lea)
    sans_mandat = lea.client.post("/api/moi/prestataire/paiement-carte", json={"mandat": False})
    active = lea.client.post("/api/moi/prestataire/paiement-carte", json={"mandat": True})
    avant_verification = lea.client.get("/api/moi/prestataire/paiement-carte").json()
    faux_stripe.envoyer(client, faux_stripe.compte_verifie(list(faux_stripe.comptes)[-1]))
    apres_verification = lea.client.get("/api/moi/prestataire/paiement-carte").json()

    assert sans_siret.status_code == 400 and "SIRET vérifié" in sans_siret.json()["detail"]
    assert sans_mandat.status_code == 400 and "factures" in sans_mandat.json()["detail"]
    assert active.status_code == 200 and active.json()["adresse"].startswith("https://connect.stripe.com/")
    assert avant_verification["compte_cree"] is True and avant_verification["pret"] is False
    assert avant_verification["mandat_facturation_le"] is not None
    assert apres_verification["pret"] is True
    # « Stripe gère la tarification » : frais payés par le prestataire, versements décidés par rafals
    cree = appels(faux_stripe, "/v1/accounts")[0]["donnees"]
    assert cree["controller"]["fees"]["payer"] == "account"
    assert cree["settings"]["payouts"]["schedule"]["interval"] == "manual"


def test_la_carte_n_est_proposee_qu_une_fois_stripe_verifie(lea, dupont, base: Session) -> None:
    siret_verifie(base, lea)
    lea.client.post("/api/moi/prestataire/paiement-carte", json={"mandat": True})

    reponse = reserver(dupont, lea, a(MARDI, 10), mode_paiement="carte")

    assert reponse.status_code == 400 and "paiement par carte activé" in reponse.json()["detail"]


# ---------- Payer en réservant ----------


def test_reserver_par_carte_puis_payer(lea_carte, dupont, base: Session, faux_stripe, client, mails_envoyes) -> None:
    rdv = reserver(dupont, lea_carte, a(MARDI, 10), mode_paiement="carte").json()
    page = appels(faux_stripe, "/v1/checkout/sessions")[0]
    mails_avant_paiement = [m for m in mails_envoyes if "confirmé" in m["sujet"]]
    vu_par_lea_avant = [r["id"] for r in lea_carte.client.get("/api/moi/prestataire/rendez-vous").json()]
    faux_stripe.envoyer(client, faux_stripe.payer())
    p = paiement(base, rdv["id"])

    assert rdv["paiement_adresse"].startswith("https://checkout.stripe.com/")
    assert rdv["paiement"]["statut"] == "a_payer" and rdv["paiement"]["montant_centimes"] == 5000
    assert page["compte"] == lea_carte.compte_stripe and page["donnees"]["payment_intent_data"]["application_fee_amount"] == 250
    # Rien n'est annoncé avant le paiement, et Léa ne voit pas encore la réservation
    assert mails_avant_paiement == [] and rdv["id"] not in vu_par_lea_avant
    assert p.statut == "paye" and p.commission_centimes == 250 and p.frais_stripe_centimes == 100 and paiements.net(p) == 4650
    assert any("confirmé" in m["sujet"] for m in mails_envoyes if m["a"] == dupont.email)
    assert statut(lea_carte, rdv["id"], "prestataire") == "confirme"


def test_page_de_paiement_fermee_la_reservation_est_annulee_apres_30_minutes(
    lea_carte, dupont, base: Session, client, mails_envoyes,
) -> None:
    rdv = reserver(dupont, lea_carte, a(MARDI, 10), mode_paiement="carte").json()
    pris = "10:00" not in heures(lea_carte)
    traiter(base, plus_tard(minutes=29))
    encore_la = paiement(base, rdv["id"]).statut
    traiter(base, plus_tard(minutes=31))

    assert pris and encore_la == "a_payer"
    assert paiement(base, rdv["id"]).statut == "abandonne" and statut(dupont, rdv["id"]) == "annule_client"
    assert "10:00" in heures(lea_carte)
    assert any("Rien n'a été pris" in m["texte"] for m in mails_envoyes if m["a"] == dupont.email)


def test_paye_apres_l_annulation_rembourse_en_entier(lea_carte, dupont, base: Session, faux_stripe, client) -> None:
    rdv = reserver(dupont, lea_carte, a(MARDI, 10), mode_paiement="carte").json()
    traiter(base, plus_tard(minutes=31))
    faux_stripe.envoyer(client, faux_stripe.payer())

    assert paiement(base, rdv["id"]).statut == "rembourse" and paiement(base, rdv["id"]).rembourse_centimes == 5000


def test_message_sans_la_bonne_signature_refuse(lea_carte, dupont, base: Session, faux_stripe, client) -> None:
    rdv = reserver(dupont, lea_carte, a(MARDI, 10), mode_paiement="carte").json()

    reponse = faux_stripe.envoyer(client, faux_stripe.payer(), secret="whsec_faux")

    assert reponse.status_code == 400 and paiement(base, rdv["id"]).statut == "a_payer"


# ---------- Rembourser ----------


def test_client_annule_dans_le_delai_rembourse_moins_les_frais(paye, dupont, base: Session, faux_stripe, mails_envoyes) -> None:
    dupont.client.post(f"/api/moi/rendez-vous/{paye}/annuler")
    traiter(base)
    p = paiement(base, paye)

    assert p.statut == "rembourse" and p.rembourse_centimes == 4900  # 50,00 € - 1,00 € de frais
    assert appels(faux_stripe, "/v1/refunds")[0]["donnees"]["amount"] == 4900
    assert len(appels(faux_stripe, "/v1/application_fees")) == 1  # rafals rend ses 2,50 €
    assert any("49,00 €" in m["texte"] for m in mails_envoyes if m["a"] == dupont.email)


def test_la_faute_du_prestataire_rembourse_en_entier(lea_carte, dupont, base: Session, faux_stripe, client) -> None:
    rdv = reserver(dupont, lea_carte, a(MARDI, 10), mode_paiement="carte").json()
    faux_stripe.envoyer(client, faux_stripe.payer())
    assert lea_carte.client.post(f"/api/moi/prestataire/rendez-vous/{rdv['id']}/annuler",
                                 json={"motif": "Malade, désolée"}).status_code == 200
    traiter(base)

    assert paiement(base, rdv["id"]).rembourse_centimes == 5000
    # Les 1,00 € de frais restent à Léa : son compte Stripe est à -1,00 €, repris sur son prochain paiement


def test_panne_de_stripe_reessayee_au_passage_suivant(paye, dupont, base: Session, faux_stripe) -> None:
    dupont.client.post(f"/api/moi/rendez-vous/{paye}/annuler")
    faux_stripe.panne = True
    pendant = traiter(base)
    faux_stripe.panne = False
    apres = traiter(base)

    p = paiement(base, paye)
    essais = [c for c in appels(faux_stripe, "/v1/refunds") if c["cle"] == f"remboursement-{p.id}"]

    assert pendant["pannes_stripe"] >= 1 and apres["rembourses"] >= 1  # (d'autres tests ont laissé des paiements)
    assert len(essais) == 2 and p.statut == "rembourse"  # 2 essais, même clé : Stripe ne rembourse qu'une fois


# ---------- Verser au prestataire ----------


def test_verse_48_heures_apres_la_fin(paye, lea_carte, base: Session, faux_stripe, mails_envoyes) -> None:
    passe(base, paye, jours=1)
    traiter(base)
    trop_tot = paiement(base, paye).statut
    passe(base, paye, jours=3)
    traiter(base)

    assert trop_tot == "paye"
    assert paiement(base, paye).statut == "verse"
    assert appels(faux_stripe, "/v1/payouts")[0]["donnees"]["amount"] == 4650
    assert any("46,50 €" in m["texte"] for m in mails_envoyes if m["a"] == lea_carte.email)


def test_argent_pas_encore_disponible_chez_stripe_on_attend(lea_carte, dupont, base: Session, faux_stripe, client) -> None:
    rdv = reserver(dupont, lea_carte, a(MARDI, 10), mode_paiement="carte").json()
    faux_stripe.envoyer(client, faux_stripe.payer(en_attente=True))
    passe(base, rdv["id"], jours=3)

    traiter(base)

    assert paiement(base, rdv["id"]).statut == "paye" and appels(faux_stripe, "/v1/payouts") == []


def test_frais_d_un_remboursement_retenus_sur_le_versement_suivant(
    lea_carte, dupont, base: Session, faux_stripe, client,
) -> None:
    premier = reserver(dupont, lea_carte, a(MARDI, 10), mode_paiement="carte").json()
    faux_stripe.envoyer(client, faux_stripe.payer())
    lea_carte.client.post(f"/api/moi/prestataire/rendez-vous/{premier['id']}/annuler", json={"motif": "Malade"})
    second = reserver(dupont, lea_carte, a(MARDI, 14), mode_paiement="carte").json()
    faux_stripe.envoyer(client, faux_stripe.payer())
    traiter(base)
    passe(base, second["id"], jours=3)
    traiter(base)

    assert appels(faux_stripe, "/v1/payouts")[0]["donnees"]["amount"] == 4550  # 46,50 € - 1,00 € de frais retenus


# ---------- Absences ----------


def test_client_absent_le_prestataire_garde_l_argent_apres_7_jours(paye, lea_carte, base: Session) -> None:
    passe(base, paye, jours=3)
    lea_carte.client.post(f"/api/moi/prestataire/rendez-vous/{paye}/absent")
    traiter(base)
    pendant_la_contestation = paiement(base, paye).statut
    vieillir_signalement(base, paye, 8)
    traiter(base)

    assert pendant_la_contestation == "paye" and paiement(base, paye).statut == "verse"


def test_absence_du_client_non_retenue_il_est_rembourse(paye, lea_carte, dupont, fabrique_compte, base: Session) -> None:
    passe(base, paye, jours=3)
    lea_carte.client.post(f"/api/moi/prestataire/rendez-vous/{paye}/absent")
    dupont.client.post(f"/api/moi/rendez-vous/{paye}/contester", json={"explication": "J'étais là à 10 h, porte fermée."})
    admin = fabrique_compte(administrateur=True)
    admin.client.post(f"/api/admin/contestations/{paye}", json={"compte": False})
    traiter(base)

    assert paiement(base, paye).statut == "rembourse" and paiement(base, paye).rembourse_centimes == 5000


def test_prestataire_absent_client_rembourse_apres_7_jours(paye, dupont, base: Session) -> None:
    passe(base, paye, jours=1)
    dupont.client.post(f"/api/moi/rendez-vous/{paye}/absent")
    traiter(base, plus_tard(days=3))
    pendant_la_contestation = paiement(base, paye).statut
    vieillir_signalement(base, paye, 8)
    traiter(base)

    assert pendant_la_contestation == "paye"
    assert paiement(base, paye).statut == "rembourse" and paiement(base, paye).rembourse_centimes == 5000


def test_paye_par_carte_48_heures_pour_signaler_l_absence_du_prestataire(paye, dupont, base: Session) -> None:
    passe(base, paye, jours=3)

    reponse = dupont.client.post(f"/api/moi/rendez-vous/{paye}/absent")

    assert reponse.status_code == 400 and "48 heures" in reponse.json()["detail"]


# ---------- Mes paiements ----------


def test_mes_paiements_cote_client_et_cote_prestataire(paye, lea_carte, dupont) -> None:
    du_client = dupont.client.get("/api/moi/paiements").json()
    du_prestataire = lea_carte.client.get("/api/moi/prestataire/paiements").json()

    assert [(p["rendez_vous_id"], p["montant_centimes"], p["net_centimes"]) for p in du_client] == [(paye, 5000, None)]
    assert [(p["commission_centimes"], p["frais_stripe_centimes"], p["net_centimes"]) for p in du_prestataire] == [(250, 100, 4650)]
    assert du_client[0]["rembourse_si_annule_centimes"] == 4900 and du_client[0]["avec"] == "Karim Benali"
    assert du_prestataire[0]["versement_prevu_le"] is not None


def test_revenu_sans_payer_le_client_annule_sans_prevenir_le_prestataire(lea_carte, dupont, base: Session, mails_envoyes) -> None:
    rdv = reserver(dupont, lea_carte, a(MARDI, 10), mode_paiement="carte").json()
    deja = len(mails_envoyes)  # (le mail d'inscription de Léa est déjà parti)

    annule = dupont.client.post(f"/api/moi/rendez-vous/{rdv['id']}/annuler").json()
    traiter(base)

    assert annule["statut"] == "annule_client" and annule["motif"] == "Paiement non terminé"
    assert paiement(base, rdv["id"]).statut == "abandonne"
    assert [m for m in mails_envoyes[deja:] if m["a"] == lea_carte.email] == []


def test_delai_de_paiement_dans_les_reglages() -> None:
    assert reglages.PAIEMENT_DELAI == timedelta(minutes=30) and reglages.VERSEMENT_APRES_FIN == timedelta(hours=48)
