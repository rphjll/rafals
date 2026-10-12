"""Devis : demande avec photos, devis en lignes et numéroté, TVA, autre date, acceptation (en direct ou arrhes par carte),
travaux terminés, solde, problème, annulations, expiration (RM-DEVIS.md ; lot 5.3). Stripe est simulé (conftest.py)."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.modeles.agenda import Blocage
from app.modeles.devis import Devis
from app.services import devis as service
from app.services import paiements
from tests.test_prestataires import AUJOURD_HUI, fabrique_prestataire, metiers, siret_verifie  # noqa: F401
from tests.test_prestataires import JPG
from tests.test_rendez_vous import dupont  # noqa: F401 (fixture)

DEBUT = AUJOURD_HUI + timedelta(days=10)
FIN = DEBUT + timedelta(days=1)
LIGNES = [  # 140 € + 720 € + 330 € = 1 190 €
    {"libelle": "Parpaings", "quantite_centiemes": 4000, "prix_unitaire_centimes": 350},
    {"libelle": "Main-d'œuvre", "quantite_centiemes": 1600, "prix_unitaire_centimes": 4500},
    {"libelle": "Enduit", "quantite_centiemes": 100, "prix_unitaire_centimes": 33000},
]


def un_devis(**modifs) -> dict:
    return {"lignes": LIGNES, "arrhes_pourcent": 30, "travaux_debut": DEBUT.isoformat(), "travaux_fin": FIN.isoformat(),
            "valable_jusqu_au": (AUJOURD_HUI + timedelta(days=30)).isoformat()} | modifs


@pytest.fixture
def paul(fabrique_prestataire, base: Session):  # noqa: F811
    """Paul, maçon avec SIRET vérifié : on peut lui demander un devis depuis son profil. Il vient chez le client."""
    compte = fabrique_prestataire("Maçon", ())
    siret_verifie(base, compte)
    return compte


@pytest.fixture
def paul_carte(paul, faux_stripe, client):
    """Paul a activé la carte et Stripe a vérifié son compte."""
    assert paul.client.post("/api/moi/prestataire/paiement-carte", json={"mandat": True}).status_code == 200
    paul.compte_stripe = list(faux_stripe.comptes)[-1]
    faux_stripe.envoyer(client, faux_stripe.compte_verifie(paul.compte_stripe))
    return paul


def demander(compte, prestataire, texte: str = "Muret de 5 mètres au fond du jardin", metier_id: int | None = None):
    """[Demander un devis] sur le profil du prestataire, pour un de ses métiers (sans précision : son métier principal)."""
    profil = prestataire.client.get("/api/moi/prestataire").json()
    return compte.client.post("/api/devis/demandes", json={
        "prestataire_id": profil["id"], "metier_id": metier_id or profil["metier_principal"]["id"], "texte": texte})


def envoyer(prestataire, demande_id: int, **modifs):
    return prestataire.client.post(f"/api/moi/prestataire/demandes-devis/{demande_id}/devis", json=un_devis(**modifs))


@pytest.fixture
def envoye(paul, dupont):  # noqa: F811
    """Le devis de Paul (1 190 €, arrhes 30 %) envoyé à Mme Dupont ; renvoie son numéro (id)."""
    demande = demander(dupont, paul).json()
    return envoyer(paul, demande["id"]).json()["demande"]["devis"]["id"]


def etat(base: Session, devis_id: int) -> Devis:
    base.expire_all()
    return base.get_one(Devis, devis_id)


def traiter(base: Session, quand: datetime | None = None) -> None:
    base.expire_all()
    paiements.traiter(base, quand or datetime.now(UTC))
    service.traiter(base, quand or datetime.now(UTC))
    base.commit()


def au_debut_des_travaux(base: Session, devis_id: int) -> None:
    """Fait comme si les travaux avaient commencé aujourd'hui (pour pouvoir les déclarer terminés)."""
    base.execute(text("UPDATE devis SET travaux_debut = CURRENT_DATE, travaux_fin = CURRENT_DATE WHERE id = :id"), {"id": devis_id})
    base.commit()


# ---------- Calculs ----------


def test_totaux_sans_et_avec_tva() -> None:
    sans = service.totaux([service.Ligne(**ligne) for ligne in LIGNES], 30)
    avec = service.totaux([service.Ligne("Muret", 100, 100000, 100)], 30)

    assert (sans.ht, sans.tva, sans.ttc, sans.arrhes, sans.solde) == (119000, 0, 119000, 35700, 83300)
    assert (avec.ht, avec.tva, avec.ttc, avec.arrhes, avec.solde) == (100000, 10000, 110000, 33000, 77000)
    assert service.montant_ligne(250, 1200) == 3000  # 2,5 × 12,00 € = 30,00 €


# ---------- La demande ----------


def test_devis_reserve_aux_prestataires_avec_siret_et_a_leurs_metiers(fabrique_prestataire, paul, dupont, metiers) -> None:  # noqa: F811
    tom = fabrique_prestataire("Plombier", ())  # sans SIRET

    sans_siret = demander(dupont, tom)
    autre_metier = demander(dupont, paul, metier_id=metiers["Coiffeur"])
    a_soi_meme = demander(paul, paul)

    assert sans_siret.status_code == 400 and "SIRET" in sans_siret.json()["detail"]
    assert autre_metier.status_code == 400 and "métiers de ce prestataire" in autre_metier.json()["detail"]
    assert a_soi_meme.status_code == 400 and "vous-même" in a_soi_meme.json()["detail"]


def test_demande_avec_photos_vue_par_le_prestataire(paul, dupont, fabrique_compte, mails_envoyes) -> None:  # noqa: F811
    trop_court = demander(dupont, paul, "Muret")
    demande = demander(dupont, paul).json()
    for _ in range(5):
        dupont.client.post(f"/api/moi/demandes-devis/{demande['id']}/photos", files={"fichier": ("muret.jpg", JPG, "image/jpeg")})
    sixieme = dupont.client.post(f"/api/moi/demandes-devis/{demande['id']}/photos",
                                 files={"fichier": ("muret.jpg", JPG, "image/jpeg")})
    recue = paul.client.get("/api/moi/prestataire/devis").json()[0]
    photo_paul = paul.client.get(f"/api/demandes-devis/{demande['id']}/photos/1")
    photo_curieux = fabrique_compte().client.get(f"/api/demandes-devis/{demande['id']}/photos/1")

    assert trop_court.status_code == 400
    assert demande["statut"] == "envoyee" and demande["lieu"].startswith("8 allée des Pins") and demande["titre"] == "Maçon"
    assert sixieme.status_code == 400 and "5 photos" in sixieme.json()["detail"]
    assert recue["nombre_photos"] == 5 and recue["autre"]["nom"] == "Essai ZZTEST"
    assert photo_paul.status_code == 200 and photo_curieux.status_code == 404
    assert any("demande de devis" in m["sujet"] for m in mails_envoyes if m["a"] == paul.email)


def test_le_prestataire_peut_decliner(paul, dupont, mails_envoyes) -> None:  # noqa: F811
    demande = demander(dupont, paul).json()

    decline = paul.client.post(f"/api/moi/prestataire/demandes-devis/{demande['id']}/decliner",
                               json={"motif": "Je ne fais pas ce genre de travaux"}).json()

    assert decline["statut"] == "declinee"
    assert any("ce genre de travaux" in m["texte"] for m in mails_envoyes if m["a"] == dupont.email)


# ---------- Le devis ----------


def test_devis_numerotes_qui_se_suivent(paul, dupont, mails_envoyes) -> None:  # noqa: F811
    premier = envoyer(paul, demander(dupont, paul).json()["id"]).json()["demande"]["devis"]
    second = envoyer(paul, demander(dupont, paul).json()["id"], travaux_debut=(FIN + timedelta(days=3)).isoformat(),
                     travaux_fin=(FIN + timedelta(days=3)).isoformat()).json()["demande"]["devis"]

    annee = AUJOURD_HUI.year
    assert (premier["numero"], second["numero"]) == (f"D-{annee}-0001", f"D-{annee}-0002")
    assert premier["ttc_centimes"] == 119000 and premier["arrhes_centimes"] == 35700 and premier["solde_centimes"] == 83300
    assert premier["mention_tva"] == "TVA non applicable, art. 293 B du CGI"
    assert any("1190,00 €" in m["texte"] for m in mails_envoyes if m["a"] == dupont.email)


def test_avec_tva_un_taux_par_ligne(paul, dupont) -> None:  # noqa: F811
    paul.client.post("/api/moi/prestataire/tva", json={"facture_tva": True})
    demande = demander(dupont, paul).json()
    sans_taux = envoyer(paul, demande["id"])
    avec_taux = envoyer(paul, demande["id"], lignes=[{"libelle": "Muret", "quantite_centiemes": 100,
                                                      "prix_unitaire_centimes": 100000, "tva_pour_mille": 100}]).json()

    assert sans_taux.status_code == 400 and "taux de TVA" in sans_taux.json()["detail"]
    devis = avec_taux["demande"]["devis"]
    assert devis["facture_tva"] is True and devis["mention_tva"] is None
    assert (devis["ht_centimes"], devis["tva_centimes"], devis["ttc_centimes"]) == (100000, 10000, 110000)


@pytest.mark.parametrize(("modifs", "morceau"), [
    ({"lignes": []}, "au moins une ligne"),
    ({"arrhes_pourcent": 120}, "0 à 100 %"),
    ({"travaux_debut": (AUJOURD_HUI - timedelta(days=1)).isoformat()}, "passé"),
    ({"travaux_fin": (DEBUT - timedelta(days=1)).isoformat()}, "après le premier"),
])
def test_devis_verifies(paul, dupont, modifs, morceau) -> None:  # noqa: F811
    reponse = envoyer(paul, demander(dupont, paul).json()["id"], **modifs)

    assert reponse.status_code == 400 and morceau in reponse.json()["detail"]


def test_jours_des_travaux_libres_dans_l_agenda(paul, dupont) -> None:  # noqa: F811
    paul.client.post("/api/moi/agenda/blocages", json={"debut": f"{DEBUT}T00:00", "fin": f"{DEBUT}T23:00",
                                                       "motif": "ZZTEST congés", "rendez_vous": "annuler"})

    reponse = envoyer(paul, demander(dupont, paul).json()["id"])

    assert reponse.status_code == 400 and "n'est pas libre" in reponse.json()["detail"]


def test_autre_date_puis_nouvelles_dates(paul, dupont, envoye, mails_envoyes) -> None:  # noqa: F811
    autre = dupont.client.post(f"/api/moi/devis/{envoye}/autre-date", json={"texte": "Plutôt fin octobre"}).json()
    bloque = dupont.client.post(f"/api/moi/devis/{envoye}/accepter", json={"mode_paiement": "direct"})
    plus_tard = (FIN + timedelta(days=7)).isoformat()
    nouvelles = paul.client.post(f"/api/moi/prestataire/devis/{envoye}/dates",
                                 json={"travaux_debut": plus_tard, "travaux_fin": plus_tard}).json()

    assert autre["demande"]["devis"]["statut"] == "autre_date" and autre["demande"]["devis"]["message"] == "Plutôt fin octobre"
    assert bloque.status_code == 400 and "autre date" in bloque.json()["detail"]
    assert nouvelles["demande"]["devis"]["statut"] == "envoye" and nouvelles["demande"]["devis"]["travaux_debut"] == plus_tard
    assert nouvelles["demande"]["devis"]["ttc_centimes"] == 119000  # le reste ne change pas


def test_le_client_refuse(paul, dupont, envoye) -> None:  # noqa: F811
    refuse = dupont.client.post(f"/api/moi/devis/{envoye}/refuser", json={"motif": "Trop cher"}).json()

    assert refuse["demande"]["devis"]["statut"] == "refuse"


def test_expire_apres_la_date(paul, dupont, envoye, base: Session) -> None:  # noqa: F811
    base.execute(text("UPDATE devis SET valable_jusqu_au = CURRENT_DATE - 1 WHERE id = :id"), {"id": envoye})
    base.commit()
    trop_tard = dupont.client.post(f"/api/moi/devis/{envoye}/accepter", json={"mode_paiement": "direct"})
    traiter(base)

    assert trop_tard.status_code == 400 and "expiré" in trop_tard.json()["detail"]
    assert etat(base, envoye).statut == "expire"


# ---------- En direct ----------


def test_accepte_en_direct_jours_bloques_puis_paye(paul, dupont, envoye, base: Session) -> None:  # noqa: F811
    accepte = dupont.client.post(f"/api/moi/devis/{envoye}/accepter", json={"mode_paiement": "direct"}).json()
    blocage = base.get(Blocage, etat(base, envoye).blocage_id)
    trop_tot = paul.client.post(f"/api/moi/prestataire/devis/{envoye}/termine")
    retirer = paul.client.post(f"/api/moi/agenda/blocages/{blocage.id}/retirer") if blocage else None
    au_debut_des_travaux(base, envoye)
    termine = paul.client.post(f"/api/moi/prestataire/devis/{envoye}/termine").json()
    paye = paul.client.post(f"/api/moi/prestataire/devis/{envoye}/paye", json={"moyen": "cheque"}).json()

    assert accepte["paiement_adresse"] is None and accepte["demande"]["devis"]["statut"] == "accepte"
    assert accepte["demande"]["autre"]["telephone"] == "0600000000"  # le client voit le téléphone une fois accepté
    assert blocage is not None and blocage.motif.startswith("Travaux D-")
    assert trop_tot.status_code == 400 and "à partir du" in trop_tot.json()["detail"]
    assert retirer is not None and retirer.status_code == 400 and "annulez le devis" in retirer.json()["detail"]
    assert termine["demande"]["devis"]["statut"] == "termine"
    assert paye["demande"]["devis"]["statut"] == "paye" and paye["demande"]["devis"]["moyen_direct"] == "cheque"


def test_client_annule_les_jours_se_liberent(paul, dupont, envoye, base: Session) -> None:  # noqa: F811
    dupont.client.post(f"/api/moi/devis/{envoye}/accepter", json={"mode_paiement": "direct"})
    blocage_id = etat(base, envoye).blocage_id

    annule = dupont.client.post(f"/api/moi/devis/{envoye}/annuler").json()

    assert annule["demande"]["devis"]["statut"] == "annule_client"
    base.expire_all()
    assert base.get(Blocage, blocage_id) is None and etat(base, envoye).blocage_id is None


def test_probleme_signale_puis_traite_par_l_administrateur(paul, dupont, envoye, fabrique_compte) -> None:  # noqa: F811
    dupont.client.post(f"/api/moi/devis/{envoye}/accepter", json={"mode_paiement": "direct"})
    dupont.client.post(f"/api/moi/devis/{envoye}/probleme", json={"texte": "Le muret penche de 5 cm"})
    admin = fabrique_compte(administrateur=True)
    liste = admin.client.get("/api/admin/devis-problemes").json()
    admin.client.post(f"/api/admin/devis/{envoye}/probleme-traite")

    assert any(p["devis_id"] == envoye and p["probleme"] == "Le muret penche de 5 cm" for p in liste)
    assert all(p["devis_id"] != envoye for p in admin.client.get("/api/admin/devis-problemes").json())
    assert dupont.client.get("/api/admin/devis-problemes").status_code == 403


# ---------- Par carte : arrhes, solde ----------


@pytest.fixture
def accepte_carte(paul_carte, dupont, faux_stripe, client, base: Session):  # noqa: F811
    """Mme Dupont accepte le devis par carte et paie 357 € d'arrhes."""
    demande = demander(dupont, paul_carte).json()
    devis_id = envoyer(paul_carte, demande["id"]).json()["demande"]["devis"]["id"]
    reponse = dupont.client.post(f"/api/moi/devis/{devis_id}/accepter", json={"mode_paiement": "carte"}).json()
    paul_carte.avant_paiement = reponse
    faux_stripe.envoyer(client, faux_stripe.payer())
    return devis_id


def test_arrhes_par_carte_puis_solde(accepte_carte, paul_carte, dupont, base: Session, faux_stripe, client) -> None:  # noqa: F811
    avant = paul_carte.avant_paiement
    apres_arrhes = etat(base, accepte_carte).statut
    traiter(base)
    arrhes = paiements.du_devis(base, accepte_carte, "arrhes")
    au_debut_des_travaux(base, accepte_carte)
    paul_carte.client.post(f"/api/moi/prestataire/devis/{accepte_carte}/termine")
    page_solde = dupont.client.post(f"/api/moi/devis/{accepte_carte}/payer-solde").json()
    faux_stripe.envoyer(client, faux_stripe.payer())
    traiter(base)

    assert avant["paiement_adresse"].startswith("https://checkout.stripe.com/")
    assert avant["demande"]["devis"]["statut"] == "envoye"  # accepté seulement quand les arrhes sont payées
    assert apres_arrhes == "accepte"
    assert arrhes is not None and arrhes.montant_centimes == 35700 and arrhes.commission_centimes == 1785
    assert arrhes.statut == "verse"  # les arrhes partent sans attendre (matériaux)
    assert page_solde["paiement_adresse"].startswith("https://checkout.stripe.com/")
    solde = paiements.du_devis(base, accepte_carte, "solde")
    assert solde is not None and solde.montant_centimes == 83300 and solde.statut == "verse"
    assert etat(base, accepte_carte).statut == "paye"
    # Ce que voit Paul dans « Mon agenda › Paiements »
    titres = [p["titre"] for p in paul_carte.client.get("/api/moi/prestataire/paiements").json()]
    assert any("(arrhes)" in t for t in titres) and any("(solde)" in t for t in titres)


def test_client_annule_le_prestataire_garde_les_arrhes(accepte_carte, dupont, base: Session) -> None:  # noqa: F811
    dupont.client.post(f"/api/moi/devis/{accepte_carte}/annuler")
    traiter(base)

    assert etat(base, accepte_carte).statut == "annule_client"
    assert paiements.du_devis(base, accepte_carte, "arrhes").statut == "verse"


def test_prestataire_annule_les_arrhes_sont_rendues(accepte_carte, paul_carte, dupont, base: Session, mails_envoyes) -> None:  # noqa: F811
    traiter(base)  # arrhes déjà versées à Paul
    paul_carte.client.post(f"/api/moi/prestataire/devis/{accepte_carte}/annuler", json={"motif": "Chantier impossible"})
    traiter(base)
    arrhes = paiements.du_devis(base, accepte_carte, "arrhes")

    assert arrhes.statut == "rembourse" and arrhes.rembourse_centimes == 35700
    assert any("rendues" in m["texte"] for m in mails_envoyes if m["a"] == dupont.email)


def test_arrhes_payees_trop_tard_remboursees(paul_carte, dupont, faux_stripe, client, base: Session) -> None:  # noqa: F811
    devis_id = envoyer(paul_carte, demander(dupont, paul_carte).json()["id"]).json()["demande"]["devis"]["id"]
    dupont.client.post(f"/api/moi/devis/{devis_id}/accepter", json={"mode_paiement": "carte"})
    dupont.client.post(f"/api/moi/devis/{devis_id}/refuser", json={})
    faux_stripe.envoyer(client, faux_stripe.payer())

    arrhes = paiements.du_devis(base, devis_id, "arrhes")
    assert etat(base, devis_id).statut == "refuse" and arrhes.statut == "rembourse" and arrhes.rembourse_centimes == 35700


def test_page_d_arrhes_fermee_on_peut_recommencer(paul_carte, dupont, base: Session) -> None:  # noqa: F811
    devis_id = envoyer(paul_carte, demander(dupont, paul_carte).json()["id"]).json()["demande"]["devis"]["id"]
    dupont.client.post(f"/api/moi/devis/{devis_id}/accepter", json={"mode_paiement": "carte"})
    deux_fois = dupont.client.post(f"/api/moi/devis/{devis_id}/accepter", json={"mode_paiement": "carte"})
    traiter(base, datetime.now(UTC) + timedelta(minutes=31))
    encore = dupont.client.post(f"/api/moi/devis/{devis_id}/accepter", json={"mode_paiement": "carte"})

    assert deux_fois.status_code == 400 and "déjà en cours" in deux_fois.json()["detail"]
    assert encore.status_code == 200 and encore.json()["paiement_adresse"]


def test_rappel_du_solde_3_jours_apres(accepte_carte, paul_carte, dupont, base: Session, mails_envoyes) -> None:  # noqa: F811
    au_debut_des_travaux(base, accepte_carte)
    paul_carte.client.post(f"/api/moi/prestataire/devis/{accepte_carte}/termine")
    avant = len([m for m in mails_envoyes if "rappel, solde" in m["sujet"]])
    base.expire_all()
    termine_le = etat(base, accepte_carte).termine_le
    service.traiter(base, termine_le + timedelta(days=3, minutes=10))
    base.commit()

    assert len([m for m in mails_envoyes if "rappel, solde" in m["sujet"] and m["a"] == dupont.email]) == avant + 1


def test_relance_d_un_devis_sans_reponse_une_seule_fois(paul, dupont, envoye, base: Session, mails_envoyes) -> None:  # noqa: F811
    """Karim envoie un devis à Julie ; elle ne répond pas : au bout de 3 jours, rafals la prévient, une seule fois."""
    envoye_le = etat(base, envoye).envoye_le
    relances = lambda: [m for m in mails_envoyes if "attend votre réponse au devis" in m["sujet"] and m["a"] == dupont.email]  # noqa: E731

    service.traiter(base, envoye_le + timedelta(days=2))
    trop_tot = len(relances())
    service.traiter(base, envoye_le + timedelta(days=3, minutes=10))
    au_bout_de_3_jours = len(relances())
    service.traiter(base, envoye_le + timedelta(days=3, hours=2))
    service.traiter(base, envoye_le + timedelta(days=5))
    base.commit()

    assert trop_tot == 0 and au_bout_de_3_jours == 1 and len(relances()) == 1
    assert "acceptez-le ou refusez-le" in relances()[0]["texte"]


def test_un_curieux_ne_voit_pas_le_devis(paul, dupont, envoye, fabrique_compte) -> None:  # noqa: F811
    curieux = fabrique_compte()

    assert curieux.client.post(f"/api/moi/devis/{envoye}/accepter", json={"mode_paiement": "direct"}).status_code == 404
    assert curieux.client.get("/api/moi/devis").json() == []


def test_numero_unique_par_prestataire(paul, dupont, envoye, base: Session) -> None:  # noqa: F811
    devis = etat(base, envoye)
    autres = base.scalars(select(Devis).where(Devis.annee == devis.annee, Devis.numero == devis.numero)).all()

    assert service.numero(devis).startswith("D-")
    assert len([d for d in autres if service.demande_de(base, d).prestataire_id == service.demande_de(base, devis).prestataire_id]) == 1
