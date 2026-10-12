"""Répondre à une demande, propositions, négociation du prix, rendez-vous (RM-DEMANDES.md ; suite du lot 8.3)."""

from datetime import UTC, datetime, time, timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import reglages
from app.services import messagerie, propositions
from tests.test_prestataires import carte_activee, fabrique_prestataire, metiers, siret_verifie  # noqa: F401 (fixtures)
from tests.test_demandes import AUJOURD_HUI, pelouse, publier, sur_l_accueil
from tests.test_messagerie import id_prestataire
from tests.test_prestataires import id_commune

PARIS = reglages.FUSEAU_AFFICHAGE
APRES_DEMAIN_10H = datetime.combine(AUJOURD_HUI + timedelta(days=2), time(10), tzinfo=PARIS)
LIBOURNE = {"adresse_ligne": "3 rue Gambetta", "code_postal": "33500", "code_insee": "33243", "latitude": "44.915", "longitude": "-0.243"}


@pytest.fixture
def fuite(fabrique_compte, metiers):  # noqa: F811
    """Mme Dupont a publié « Fuite sous l'évier » (Plombier), chez elle, 8 allée des Pins à Pessac."""
    dupont = fabrique_compte()
    reponse = publier(dupont, pelouse(metiers["Plombier"], titre="Fuite sous l'évier",
                                      description="Le siphon goutte depuis hier soir, sous l'évier."))
    assert reponse.status_code == 201, reponse.text
    dupont.demande = reponse.json()["id"]
    return dupont


def repondre(prestataire, demande_id: int):
    return prestataire.client.post(f"/api/demandes/{demande_id}/repondre")


def proposer(prestataire, conversation_id: int, **modifs):
    donnees = {"prix_centimes": 6000, "debut": APRES_DEMAIN_10H.isoformat(), "duree_minutes": 60, "paiement_especes": True} | modifs
    return prestataire.client.post(f"/api/conversations/{conversation_id}/propositions", json=donnees)


def proposition_de_karim(karim, fuite, **modifs) -> dict:  # noqa: F811
    """Karim répond à la fuite et propose 60 € · après-demain à 10 h · 1 h · espèces."""
    conversation = repondre(karim, fuite.demande).json()["conversation_id"]
    reponse = proposer(karim, conversation, demande_id=fuite.demande, **modifs)
    assert reponse.status_code == 201, reponse.text
    return reponse.json()


def accepter(client, proposition_id: int, mode: str = "especes"):
    return client.client.post(f"/api/propositions/{proposition_id}/accepter", json={"mode_paiement": mode})


def propositions_vues(compte, conversation_id: int) -> list[dict]:
    return compte.client.get(f"/api/conversations/{conversation_id}/propositions").json()


def infos(compte, conversation_id: int) -> list[str]:
    """Les lignes écrites par rafals dans le fil."""
    fil = compte.client.get(f"/api/conversations/{conversation_id}").json()["messages"]
    return [m["texte"] for m in fil if m["genre"] == "information"]


# ---------- Qui peut répondre ----------


def test_qui_peut_repondre(fabrique_prestataire, fabrique_compte, metiers, fuite) -> None:  # noqa: F811
    karim = fabrique_prestataire()  # plombier et électricien à Pessac, 15 km
    electricien = fabrique_prestataire("Électricien", ())
    loin = publier(fabrique_compte(), pelouse(metiers["Plombier"], titre="Fuite à Libourne", **LIBOURNE)).json()["id"]

    assert sur_l_accueil(karim.client, fuite.demande)["peut_repondre"] is True
    assert sur_l_accueil(electricien.client, fuite.demande)["peut_repondre"] is False  # pas son métier
    assert sur_l_accueil(karim.client, loin)["peut_repondre"] is False  # 40 km, hors de ses 15 km
    assert sur_l_accueil(fuite.client, fuite.demande)["peut_repondre"] is False  # une cliente, pas un prestataire
    pres_de_chez_moi = [d["id"] for d in karim.client.get("/api/moi/prestataire/demandes").json()]
    assert fuite.demande in pres_de_chez_moi and loin not in pres_de_chez_moi
    trop_loin = repondre(karim, loin)
    pas_son_metier = repondre(electricien, fuite.demande)
    assert trop_loin.status_code == 403 and pas_son_metier.status_code == 403 and "trop loin" in trop_loin.json()["detail"]
    assert repondre(fuite, fuite.demande).status_code == 404  # « Vous ne proposez pas encore vos services »


def test_repondre_ouvre_la_conversation_une_seule_fois(fabrique_prestataire, fuite) -> None:  # noqa: F811
    karim = fabrique_prestataire()

    premiere = repondre(karim, fuite.demande)
    seconde = repondre(karim, fuite.demande)

    assert premiere.status_code == 201 and premiere.json() == seconde.json()
    conversation = premiere.json()["conversation_id"]
    vue = sur_l_accueil(karim.client, fuite.demande)
    assert vue["nombre_reponses"] == 1 and vue["conversation_id"] == conversation and vue["peut_repondre"] is True
    assert sur_l_accueil(fuite.client, fuite.demande)["conversation_id"] is None
    assert infos(fuite, conversation) == ["Karim Benali a répondu à la demande « Fuite sous l'évier »."]
    # La demande est rappelée en haut du fil, chez les deux ; un étranger ne voit rien
    assert [d["id"] for d in fuite.client.get(f"/api/conversations/{conversation}/demandes").json()] == [fuite.demande]
    assert karim.client.get(f"/api/conversations/{conversation}/demandes").json()[0]["titre"] == "Fuite sous l'évier"
    assert fabrique_prestataire().client.get(f"/api/conversations/{conversation}/demandes").status_code == 404
    # Il peut maintenant écrire à la cliente, sans rendez-vous ni devis
    assert karim.client.post(f"/api/conversations/{conversation}/messages", data={"texte": "Bonjour, le siphon est en PVC ?"}).status_code == 201


def test_pas_de_reponse_a_sa_propre_demande(fabrique_prestataire, metiers) -> None:  # noqa: F811
    karim = fabrique_prestataire()
    la_sienne = publier(karim, pelouse(metiers["Plombier"], titre="Fuite chez moi")).json()["id"]

    refus = repondre(karim, la_sienne)

    assert refus.status_code == 400 and "votre propre demande" in refus.json()["detail"]
    assert sur_l_accueil(karim.client, la_sienne)["peut_repondre"] is False


def test_demande_complete(fabrique_prestataire, fuite, monkeypatch) -> None:  # noqa: F811
    monkeypatch.setattr(reglages, "DEMANDE_REPONSES_MAX", 1)  # 10 dans la règle
    karim, sophie = fabrique_prestataire(), fabrique_prestataire()
    assert repondre(karim, fuite.demande).status_code == 201

    trop_tard = repondre(sophie, fuite.demande)

    assert trop_tard.status_code == 400 and "complète" in trop_tard.json()["detail"]
    vue = sur_l_accueil(sophie.client, fuite.demande)
    assert vue["complete"] is True and vue["peut_repondre"] is False
    assert sur_l_accueil(karim.client, fuite.demande)["peut_repondre"] is True  # il a déjà répondu : il retrouve sa conversation


def test_une_demande_avec_reponse_ne_se_modifie_plus(fabrique_prestataire, metiers, fuite) -> None:  # noqa: F811
    karim = fabrique_prestataire()
    repondre(karim, fuite.demande)

    refus = fuite.client.put(f"/api/demandes/{fuite.demande}", json=pelouse(metiers["Plombier"], titre="Fuite et robinet") | {"latitude": None, "longitude": None})

    assert refus.status_code == 400 and "a déjà répondu" in refus.json()["detail"]


# ---------- Faire une proposition ----------


def test_proposition_vue_par_les_deux(fabrique_prestataire, fuite) -> None:  # noqa: F811
    karim = fabrique_prestataire()

    proposition = proposition_de_karim(karim, fuite)

    assert proposition["statut"] == "en_attente" and proposition["prix_centimes"] == 6000 and proposition["lieu"] == "chez_client"
    assert proposition["metier"] == "Plombier" and proposition["demande_titre"] == "Fuite sous l'évier"
    assert proposition["modes_de_paiement"] == ["especes"] and proposition["negociation"] is None
    assert datetime.fromisoformat(proposition["fin"]) - datetime.fromisoformat(proposition["debut"]) == timedelta(hours=1)
    conversation = proposition["conversation_id"]
    assert [p["id"] for p in propositions_vues(fuite, conversation)] == [proposition["id"]]
    assert "Karim Benali propose : 60,00 €" in infos(fuite, conversation)[-1] and "chez vous · espèces" in infos(fuite, conversation)[-1]


def test_controles_d_une_proposition(fabrique_prestataire, fabrique_compte, fuite) -> None:  # noqa: F811
    karim, sophie = fabrique_prestataire(), fabrique_prestataire()
    conversation = repondre(karim, fuite.demande).json()["conversation_id"]
    autre = fuite.client.post("/api/conversations", json={"prestataire_id": id_prestataire(sophie)}).json()["id"]

    sans_repondre = proposer(sophie, autre, demande_id=fuite.demande)
    hier = proposer(karim, conversation, demande_id=fuite.demande, debut=(datetime.now(UTC) - timedelta(hours=1)).isoformat())
    gratuit = proposer(karim, conversation, demande_id=fuite.demande, prix_centimes=0)
    trop_court = proposer(karim, conversation, demande_id=fuite.demande, duree_minutes=5)
    carte_sans_siret = proposer(karim, conversation, demande_id=fuite.demande, paiement_carte=True)
    sans_paiement = proposer(karim, conversation, demande_id=fuite.demande, paiement_especes=False)
    par_un_autre = proposer(sophie, conversation, demande_id=fuite.demande)
    par_la_cliente = proposer(fuite, conversation, demande_id=fuite.demande)

    assert sans_repondre.status_code == 403 and "[Répondre]" in sans_repondre.json()["detail"]
    assert hier.status_code == 400 and "à venir" in hier.json()["detail"]
    assert gratuit.status_code == 400 and trop_court.status_code == 400 and sans_paiement.status_code == 400
    assert carte_sans_siret.status_code == 400 and "SIRET vérifié" in carte_sans_siret.json()["detail"]
    assert par_un_autre.status_code == 404 and par_la_cliente.status_code == 404
    assert propositions_vues(karim, conversation) == []


def test_refuser_puis_nouvelle_proposition_qui_remplace(fabrique_prestataire, fuite) -> None:  # noqa: F811
    karim = fabrique_prestataire()
    premiere = proposition_de_karim(karim, fuite)
    conversation = premiere["conversation_id"]

    par_karim = karim.client.post(f"/api/propositions/{premiere['id']}/refuser")
    refusee = fuite.client.post(f"/api/propositions/{premiere['id']}/refuser")
    deux_fois = fuite.client.post(f"/api/propositions/{premiere['id']}/refuser")
    seconde = proposer(karim, conversation, demande_id=fuite.demande, prix_centimes=5000).json()
    troisieme = proposer(karim, conversation, demande_id=fuite.demande, prix_centimes=4500).json()

    assert par_karim.status_code == 404  # ce n'est pas à lui de refuser sa proposition
    assert refusee.status_code == 200 and refusee.json()["statut"] == "refusee" and deux_fois.status_code == 400
    assert "Essai Z. a refusé la proposition de 60,00 €." in infos(karim, conversation)
    # La 2e n'avait rien à remplacer (la 1re était refusée) ; la 3e remplace la 2e, qui attendait encore
    assert seconde["remplace_id"] is None and troisieme["remplace_id"] == seconde["id"]
    assert [p["statut"] for p in propositions_vues(fuite, conversation)] == ["refusee", "remplacee", "en_attente"]


def test_retirer_sa_proposition(fabrique_prestataire, fuite) -> None:  # noqa: F811
    karim = fabrique_prestataire()
    proposition = proposition_de_karim(karim, fuite)

    par_la_cliente = fuite.client.post(f"/api/propositions/{proposition['id']}/retirer")
    retiree = karim.client.post(f"/api/propositions/{proposition['id']}/retirer")

    assert par_la_cliente.status_code == 404
    assert retiree.status_code == 200 and retiree.json()["statut"] == "retiree"
    assert accepter(fuite, proposition["id"]).status_code == 400


# ---------- Négocier le prix ----------


def test_negocier_le_prix(fabrique_prestataire, fuite) -> None:  # noqa: F811
    karim = fabrique_prestataire()
    proposition = proposition_de_karim(karim, fuite)
    negocier = lambda prix: fuite.client.post(f"/api/propositions/{proposition['id']}/negocier", json={"prix_centimes": prix})  # noqa: E731

    plus_cher = negocier(7000)
    premiere = negocier(4000)
    deja_une = negocier(4500)
    refus = karim.client.post(f"/api/negociations/{premiere.json()['negociation']['id']}/refuser")
    seconde = negocier(5000)
    par_la_cliente = fuite.client.post(f"/api/negociations/{seconde.json()['negociation']['id']}/accepter")
    accord = karim.client.post(f"/api/negociations/{seconde.json()['negociation']['id']}/accepter")

    assert plus_cher.status_code == 400 and "plus bas que 60,00 €" in plus_cher.json()["detail"]
    assert premiere.status_code == 201 and premiere.json()["negociation"]["prix_centimes"] == 4000
    assert deja_une.status_code == 400 and "attendez la réponse" in deja_une.json()["detail"]
    # Karim garde son prix : sa proposition à 60 € attend de nouveau, sans négociation en cours
    assert refus.status_code == 200 and (refus.json()["id"], refus.json()["statut"], refus.json()["negociation"]) == (proposition["id"], "en_attente", None)
    assert par_la_cliente.status_code == 404
    # Karim accepte 50 € : une nouvelle proposition à 50 € remplace celle à 60 €
    nouvelle = accord.json()
    assert accord.status_code == 200 and nouvelle["prix_centimes"] == 5000 and nouvelle["remplace_id"] == proposition["id"]
    assert (nouvelle["debut"], nouvelle["lieu"], nouvelle["statut"]) == (proposition["debut"], proposition["lieu"], "en_attente")
    conversation = proposition["conversation_id"]
    assert [p["statut"] for p in propositions_vues(fuite, conversation)] == ["remplacee", "en_attente"]
    fil = infos(fuite, conversation)
    assert "Prix proposé par Essai Z. : 40,00 € au lieu de 60,00 €." in fil and "Karim Benali garde son prix de 60,00 €." in fil
    assert accepter(fuite, nouvelle["id"]).status_code == 201


# ---------- Accepter : le rendez-vous ----------


def test_accepter_cree_un_rendez_vous_confirme(fabrique_prestataire, fuite, client, base: Session, mails_envoyes) -> None:  # noqa: F811
    karim = fabrique_prestataire()
    proposition = proposition_de_karim(karim, fuite)

    par_karim = accepter(karim, proposition["id"])
    acceptee = accepter(fuite, proposition["id"])
    deux_fois = accepter(fuite, proposition["id"])

    assert par_karim.status_code == 404
    assert acceptee.status_code == 201 and acceptee.json()["proposition"]["statut"] == "acceptee"
    assert acceptee.json()["paiement_adresse"] is None and deux_fois.status_code == 400
    rdv_id = acceptee.json()["rendez_vous_id"]
    assert acceptee.json()["proposition"]["rendez_vous_id"] == rdv_id
    rdv = next(r for r in fuite.client.get("/api/moi/rendez-vous").json() if r["id"] == rdv_id)
    assert (rdv["statut"], rdv["titre"], rdv["prix_centimes"]) == ("confirme", "Fuite sous l'évier", 6000)
    assert rdv["lieu"] == "chez_client" and rdv["mode_paiement"] == "especes" and rdv["debut"] == proposition["debut"]
    # L'adresse est celle écrite dans la demande, et Karim la voit maintenant ; le calendrier est celui du métier
    recu = next(r for r in karim.client.get("/api/moi/prestataire/rendez-vous").json() if r["id"] == rdv_id)
    assert "8 Allée des Pins" in recu["adresse"] and "Pessac" in recu["adresse"]
    metier = base.execute(text("SELECT m.nom FROM rendez_vous r JOIN metier m ON m.id = r.metier_id WHERE r.id = :id"), {"id": rdv_id}).scalar_one()
    assert metier == "Plombier"
    # La demande est pourvue : elle quitte l'accueil
    assert sur_l_accueil(client, fuite.demande) is None
    assert next(d for d in fuite.client.get("/api/moi/demandes").json() if d["id"] == fuite.demande)["statut"] == "pourvue"
    assert any("rendez-vous confirmé" in m["sujet"] for m in mails_envoyes if m["a"] == fuite.email)
    assert any("rendez-vous confirmé" in m["sujet"] for m in mails_envoyes if m["a"] == karim.email)
    assert "Essai Z. a accepté : rendez-vous « Fuite sous l'évier »" in infos(karim, proposition["conversation_id"])[-1]
    # Un rendez-vous ne se déplace plus tout seul : le client écrit au prestataire, qui fait une nouvelle proposition
    deplace = fuite.client.post(f"/api/moi/rendez-vous/{rdv_id}/deplacer", json={"debut": (APRES_DEMAIN_10H + timedelta(hours=2)).isoformat()})
    assert deplace.status_code == 404


def test_les_autres_prestataires_sont_prevenus(fabrique_prestataire, fuite) -> None:  # noqa: F811
    karim, sophie = fabrique_prestataire(), fabrique_prestataire()
    de_karim = proposition_de_karim(karim, fuite)
    de_sophie = proposition_de_karim(sophie, fuite, prix_centimes=5500)
    seulement_repondu = fabrique_prestataire()
    sa_conversation = repondre(seulement_repondu, fuite.demande).json()["conversation_id"]

    assert accepter(fuite, de_karim["id"]).status_code == 201

    assert propositions_vues(sophie, de_sophie["conversation_id"])[0]["statut"] == "non_retenue"
    message = "Essai Z. a choisi un autre prestataire pour « Fuite sous l'évier »."
    assert infos(sophie, de_sophie["conversation_id"])[-1] == message and infos(seulement_repondu, sa_conversation)[-1] == message
    assert message not in infos(karim, de_karim["conversation_id"])
    assert accepter(fuite, de_sophie["id"]).status_code == 400
    assert repondre(fabrique_prestataire(), fuite.demande).status_code == 404  # la demande n'est plus ouverte


def test_pas_deux_rendez_vous_a_la_meme_heure(fabrique_prestataire, fabrique_compte, metiers, fuite) -> None:  # noqa: F811
    karim = fabrique_prestataire()
    petit = fabrique_compte()
    petit.demande = publier(petit, pelouse(metiers["Plombier"], titre="Robinet qui goutte")).json()["id"]
    pour_dupont = proposition_de_karim(karim, fuite)
    pour_petit = proposition_de_karim(karim, petit, debut=(APRES_DEMAIN_10H + timedelta(minutes=30)).isoformat())

    assert accepter(fuite, pour_dupont["id"]).status_code == 201
    trop_tard = accepter(petit, pour_petit["id"])
    meme_heure = proposer(karim, pour_petit["conversation_id"], demande_id=petit.demande)
    juste_apres = proposer(karim, pour_petit["conversation_id"], demande_id=petit.demande, debut=(APRES_DEMAIN_10H + timedelta(hours=1)).isoformat())

    assert trop_tard.status_code == 409 and "déjà un rendez-vous" in trop_tard.json()["detail"]
    assert meme_heure.status_code == 409 and juste_apres.status_code == 201


def test_une_proposition_expire_a_l_heure_proposee(fabrique_prestataire, fuite, base: Session) -> None:  # noqa: F811
    karim = fabrique_prestataire()
    proposition = proposition_de_karim(karim, fuite)
    base.execute(text("UPDATE proposition SET debut = now() - interval '2 hours', fin = now() - interval '1 hour' WHERE id = :id"),
                 {"id": proposition["id"]})
    base.commit()

    trop_tard = accepter(fuite, proposition["id"])
    expirees = propositions.expirer(base, datetime.now(UTC))
    base.commit()

    assert trop_tard.status_code == 400 and expirees >= 1
    assert propositions_vues(fuite, proposition["conversation_id"])[0]["statut"] == "expiree"


def test_rouvrir_sa_demande_apres_une_annulation(fabrique_prestataire, fuite, client) -> None:  # noqa: F811
    karim = fabrique_prestataire()
    rdv_id = accepter(fuite, proposition_de_karim(karim, fuite)["id"]).json()["rendez_vous_id"]

    trop_tot = fuite.client.post(f"/api/demandes/{fuite.demande}/rouvrir")
    annule = karim.client.post(f"/api/moi/prestataire/rendez-vous/{rdv_id}/annuler", json={"motif": "Je suis malade, désolé."})
    rouverte = fuite.client.post(f"/api/demandes/{fuite.demande}/rouvrir")

    assert trop_tot.status_code == 400 and "toujours prévu" in trop_tot.json()["detail"]
    assert annule.status_code == 200, annule.text
    assert rouverte.status_code == 200 and rouverte.json()["statut"] == "ouverte"
    assert sur_l_accueil(client, fuite.demande) is not None
    # Karim a déjà répondu : il retrouve sa conversation et peut refaire une proposition
    assert proposer(karim, repondre(karim, fuite.demande).json()["conversation_id"], demande_id=fuite.demande).status_code == 201


# ---------- Sans demande publiée, et par carte ----------


def test_proposition_a_un_client_qui_a_ecrit_en_premier(fabrique_prestataire, fabrique_compte, metiers, client) -> None:  # noqa: F811
    karim, petit = fabrique_prestataire(), fabrique_compte()
    conversation = petit.client.post("/api/conversations", json={"prestataire_id": id_prestataire(karim)}).json()["id"]

    sans_metier = proposer(karim, conversation, lieu="chez_client")
    pas_son_metier = proposer(karim, conversation, lieu="chez_client", metier_id=metiers["Coiffeur"])
    sans_lieu = proposer(karim, conversation, metier_id=metiers["Plombier"])
    sans_local = proposer(karim, conversation, metier_id=metiers["Plombier"], lieu="chez_moi")
    proposition = proposer(karim, conversation, metier_id=metiers["Plombier"], lieu="chez_client")

    assert sans_metier.status_code == 400 and pas_son_metier.status_code == 400 and sans_lieu.status_code == 400
    assert sans_local.status_code == 400 and "votre adresse" in sans_local.json()["detail"]
    assert proposition.status_code == 201 and proposition.json()["demande_id"] is None
    # Pas de demande, donc pas d'adresse : il faut celle du compte
    sans_adresse = accepter(petit, proposition.json()["id"])
    assert sans_adresse.status_code == 400 and "votre adresse" in sans_adresse.json()["detail"]
    petit.client.post("/api/moi/adresse", json={"ligne": "8 allée des Pins", "commune_id": id_commune(client, "33400", "Talence"),
                                                 "code_postal": "33400"})
    acceptee = accepter(petit, proposition.json()["id"])
    assert acceptee.status_code == 201
    rdv = next(r for r in petit.client.get("/api/moi/rendez-vous").json() if r["id"] == acceptee.json()["rendez_vous_id"])
    assert rdv["titre"] == "Plombier" and rdv["statut"] == "confirme"


def test_proposition_payee_par_carte(fabrique_prestataire, fuite, base: Session, faux_stripe) -> None:  # noqa: F811
    karim = fabrique_prestataire()
    siret_verifie(base, karim)
    carte_activee(base, karim)
    proposition = proposition_de_karim(karim, fuite, paiement_carte=True)

    acceptee = accepter(fuite, proposition["id"], "carte")

    assert proposition["modes_de_paiement"] == ["carte", "especes"]
    assert acceptee.status_code == 201 and acceptee.json()["paiement_adresse"].startswith("https://checkout.stripe.com/")
    assert faux_stripe.sessions  # la page de paiement de Stripe a été ouverte, pour 60 €
    assert int(list(faux_stripe.sessions.values())[-1]["line_items"][0]["price_data"]["unit_amount"]) == 6000


def test_conversation_de_3_ans_videe_mais_gardee_avec_sa_proposition(fabrique_prestataire, fuite, base: Session) -> None:  # noqa: F811
    """Sans message depuis 3 ans : les messages sont effacés ; la conversation et la proposition restent (RM-MESSAGERIE)."""
    karim = fabrique_prestataire()
    proposition = proposition_de_karim(karim, fuite)
    conversation = proposition["conversation_id"]
    karim.client.post(f"/api/conversations/{conversation}/messages", data={"texte": "Bonjour, le siphon est en PVC ?"})
    dans_3_ans = datetime.now(UTC) + reglages.MESSAGE_CONSERVATION + timedelta(days=1)

    premier_passage = messagerie.effacer_les_anciennes(base, dans_3_ans)
    base.commit()

    assert premier_passage >= 1
    assert karim.client.get(f"/api/conversations/{conversation}").json()["messages"] == []
    assert [p["id"] for p in propositions_vues(karim, conversation)] == [proposition["id"]]
    assert base.execute(text("SELECT count(*) FROM conversation WHERE id = :id"), {"id": conversation}).scalar_one() == 1


def test_signaler_une_demande_puis_l_administrateur_la_cache(fabrique_prestataire, fabrique_compte, fuite, client, mails_envoyes) -> None:  # noqa: F811
    karim, admin = fabrique_prestataire(), fabrique_compte(administrateur=True)

    trop_court = karim.client.post(f"/api/demandes/{fuite.demande}/signaler", json={"motif": "non"})
    par_une_cliente = fuite.client.post(f"/api/demandes/{fuite.demande}/signaler", json={"motif": "Je signale ma propre demande."})
    signalee = karim.client.post(f"/api/demandes/{fuite.demande}/signaler", json={"motif": "Elle demande de ne rien déclarer."})
    deux_fois = karim.client.post(f"/api/demandes/{fuite.demande}/signaler", json={"motif": "Elle demande de ne rien déclarer."})
    vue = next(s for s in admin.client.get("/api/admin/signalements").json() if s["id"] == signalee.json()["id"])
    sans_motif = admin.client.post(f"/api/admin/signalements/{vue['id']}", json={"action": "cacher_demande"})
    cachee = admin.client.post(f"/api/admin/signalements/{vue['id']}", json={"action": "cacher_demande", "decision": "Demande contraire à la loi."})

    assert trop_court.status_code == 400 and par_une_cliente.status_code == 404  # une cliente n'est pas prestataire
    assert signalee.status_code == 201 and deux_fois.status_code == 400
    assert vue["demande_id"] == fuite.demande and vue["demande_titre"] == "Fuite sous l'évier" and vue["prestataire_statut"] == "client"
    assert sans_motif.status_code == 400 and cachee.status_code == 200 and cachee.json() == {"statut": "suivi"}
    # Cachée : elle quitte l'accueil ; la cliente la voit encore dans « Mes demandes », marquée cachée, et reçoit le motif
    assert sur_l_accueil(client, fuite.demande) is None
    assert next(d for d in fuite.client.get("/api/moi/demandes").json() if d["id"] == fuite.demande)["cachee"] is True
    recu = [m for m in mails_envoyes if m["a"] == fuite.email and "votre demande a été cachée" in m["sujet"]]
    assert len(recu) == 1 and "Demande contraire à la loi." in recu[0]["texte"] and "Karim" not in recu[0]["texte"]
