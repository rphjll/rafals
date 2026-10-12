"""Alertes des prestataires (RM-ALERTES.md ; lot 8.5) : mail à chaque nouvelle demande de son métier dans son rayon,
réglages par métier, résumé de 18 h, plafond de 20 mails par jour, compteur rouge de « Demandes près de chez moi »."""

from datetime import datetime, time, timedelta

from sqlalchemy import text
from sqlalchemy.orm import Session

from app import reglages
from app.services import alertes
from tests.test_demandes import AUJOURD_HUI, pelouse, publier
from tests.test_prestataires import fabrique_prestataire, metiers  # noqa: F401 (fixtures)
from tests.test_propositions import LIBOURNE

PARIS = reglages.FUSEAU_AFFICHAGE


def alertes_de(mails_envoyes, compte) -> list[str]:
    return [m["sujet"] for m in mails_envoyes if m["a"] == compte.email and "nouvelle demande" in m["sujet"]]


def regler(prestataire, mail: str = "chaque_demande", coupes: list[int] | None = None):
    return prestataire.client.post("/api/moi/prestataire/alertes", json={"alerte_mail": mail, "metiers_coupes": coupes or []})


def test_un_mail_a_chaque_demande_de_son_metier_dans_son_rayon(fabrique_prestataire, fabrique_compte, metiers, mails_envoyes) -> None:  # noqa: F811
    karim = fabrique_prestataire()  # plombier et électricien à Pessac, 15 km
    coiffeuse = fabrique_prestataire("Coiffeur", ())
    dupont = fabrique_compte()

    publier(dupont, pelouse(metiers["Plombier"], titre="Fuite sous l'évier"))
    publier(dupont, pelouse(metiers["Plombier"], titre="Fuite à Libourne", **LIBOURNE))
    publier(karim, pelouse(metiers["Plombier"], titre="Fuite chez moi"))

    recus = alertes_de(mails_envoyes, karim)
    assert recus == ["rafals : nouvelle demande, Fuite sous l'évier, Pessac (0 km)"]  # ni Libourne (trop loin), ni la sienne
    assert alertes_de(mails_envoyes, coiffeuse) == []  # pas son métier
    # Jamais le nom, le téléphone ni l'adresse dans le mail
    corps = next(m["texte"] for m in mails_envoyes if m["a"] == karim.email and "nouvelle demande" in m["sujet"])
    assert "ZZTEST" not in corps and "Allée des Pins" not in corps and "Plombier" in corps


def test_ne_pas_me_prevenir_pour_un_metier(fabrique_prestataire, fabrique_compte, metiers, mails_envoyes) -> None:  # noqa: F811
    karim = fabrique_prestataire()
    dupont = fabrique_compte()

    avant = karim.client.get("/api/moi/prestataire/alertes").json()
    pas_le_sien = regler(karim, coupes=[metiers["Coiffeur"]])
    inconnu = regler(karim, mail="jamais")
    regle = regler(karim, coupes=[metiers["Électricien"]])
    publier(dupont, pelouse(metiers["Électricien"], titre="Prise qui disjoncte"))
    publier(dupont, pelouse(metiers["Plombier"], titre="Fuite sous l'évier"))

    assert avant["alerte_mail"] == "chaque_demande" and avant["ville"] == "Pessac" and avant["distance_km"] == 15
    assert {m["nom"]: m["prevenu"] for m in avant["metiers"]} == {"Plombier": True, "Électricien": True}
    assert pas_le_sien.status_code == 400 and inconnu.status_code == 400
    assert {m["nom"]: m["prevenu"] for m in regle.json()["metiers"]} == {"Plombier": True, "Électricien": False}
    assert alertes_de(mails_envoyes, karim) == ["rafals : nouvelle demande, Fuite sous l'évier, Pessac (0 km)"]
    # La demande d'électricité reste dans « Demandes près de chez moi »
    assert {d["titre"] for d in karim.client.get("/api/moi/prestataire/demandes").json()} >= {"Prise qui disjoncte", "Fuite sous l'évier"}


def test_aucun_mail_et_plafond_du_jour(fabrique_prestataire, fabrique_compte, metiers, mails_envoyes, monkeypatch) -> None:  # noqa: F811
    monkeypatch.setattr(reglages, "ALERTE_MAILS_PAR_JOUR", 2)  # 20 dans la règle
    karim, muet = fabrique_prestataire(), fabrique_prestataire()
    regler(muet, mail="aucun")

    for n in (1, 2, 3):
        publier(fabrique_compte(), pelouse(metiers["Plombier"], titre=f"Fuite numéro {n}"))

    assert len(alertes_de(mails_envoyes, karim)) == 2  # la 3e ira dans le résumé de 18 h
    assert alertes_de(mails_envoyes, muet) == []


def test_resume_de_18_h(fabrique_prestataire, fabrique_compte, metiers, mails_envoyes, base: Session, monkeypatch) -> None:  # noqa: F811
    monkeypatch.setattr(reglages, "ALERTE_MAILS_PAR_JOUR", 1)
    julie, karim, muet = fabrique_prestataire(), fabrique_prestataire(), fabrique_prestataire()
    regler(julie, mail="resume")
    regler(muet, mail="aucun")
    for n in (1, 2):
        publier(fabrique_compte(), pelouse(metiers["Plombier"], titre=f"Fuite numéro {n}"))
    midi = datetime.combine(AUJOURD_HUI, time(12), tzinfo=PARIS)
    soir = datetime.combine(AUJOURD_HUI, time(18, 5), tzinfo=PARIS)
    # (les demandes viennent d'être publiées : on fait comme s'il était 18 h 05 ce jour-là, ou plus tard si c'est déjà passé)
    soir = max(soir, datetime.now(PARIS) + timedelta(minutes=1))

    trop_tot = alertes.envoyer_resumes(base, midi) if midi < datetime.now(PARIS) else 0
    premier = alertes.envoyer_resumes(base, soir)
    second = alertes.envoyer_resumes(base, soir + timedelta(minutes=15))
    base.commit()

    assert trop_tot == 0 and premier >= 2 and second == 0  # une seule fois par jour
    resumes = lambda compte: [m for m in mails_envoyes if m["a"] == compte.email and "près de chez vous aujourd'hui" in m["sujet"]]  # noqa: E731
    assert len(resumes(julie)) == 1 and "Fuite numéro 1" in resumes(julie)[0]["texte"] and "Fuite numéro 2" in resumes(julie)[0]["texte"]
    assert alertes_de(mails_envoyes, julie) == []  # elle a choisi le résumé : aucun mail à chaque demande
    # Karim a eu un mail pour la 1re (plafond de 1 ici) : seule la 2e est dans son résumé
    assert len(alertes_de(mails_envoyes, karim)) == 1 and len(resumes(karim)) == 1
    assert "Fuite numéro 2" in resumes(karim)[0]["texte"] and "Fuite numéro 1" not in resumes(karim)[0]["texte"]
    assert resumes(muet) == []


def test_compteur_rouge_des_nouvelles_demandes(fabrique_prestataire, fabrique_compte, metiers) -> None:  # noqa: F811
    karim = fabrique_prestataire()
    nouvelles = lambda: karim.client.get("/api/moi/prestataire/demandes/nouvelles").json()["nombre"]  # noqa: E731
    karim.client.get("/api/moi/prestataire/demandes")  # il ouvre l'onglet : tout ce qui existait est vu
    assert nouvelles() == 0

    publier(fabrique_compte(), pelouse(metiers["Plombier"], titre="Fuite sous l'évier"))
    publier(fabrique_compte(), pelouse(metiers["Coiffeur"], titre="Coupe à domicile"))
    avant = nouvelles()
    karim.client.get("/api/moi/prestataire/demandes")

    assert avant == 1 and nouvelles() == 0


def test_mails_des_etapes_d_une_proposition(fabrique_prestataire, fabrique_compte, metiers, mails_envoyes) -> None:  # noqa: F811
    from tests.test_propositions import APRES_DEMAIN_10H

    karim, dupont = fabrique_prestataire(), fabrique_compte()
    demande = publier(dupont, pelouse(metiers["Plombier"], titre="Fuite sous l'évier")).json()["id"]
    conversation = karim.client.post(f"/api/demandes/{demande}/repondre").json()["conversation_id"]
    proposition = karim.client.post(f"/api/conversations/{conversation}/propositions", json={
        "prix_centimes": 6000, "debut": APRES_DEMAIN_10H.isoformat(), "duree_minutes": 60, "demande_id": demande}).json()
    negociee = dupont.client.post(f"/api/propositions/{proposition['id']}/negocier", json={"prix_centimes": 5000}).json()
    karim.client.post(f"/api/negociations/{negociee['negociation']['id']}/accepter")

    sujets = lambda compte: [m["sujet"] for m in mails_envoyes if m["a"] == compte.email]  # noqa: E731
    assert "rafals : Karim Benali a répondu à votre demande" in sujets(dupont)
    assert "rafals : Karim Benali vous fait une proposition" in sujets(dupont)
    assert "rafals : Essai Z. vous propose un autre prix" in sujets(karim)
    assert "rafals : Karim Benali accepte votre prix" in sujets(dupont)
    assert not [m for m in mails_envoyes if "ZZTEST" in m["texte"] or "06 " in m["texte"]]  # ni nom complet ni téléphone
