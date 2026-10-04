"""Déclarer à l'URSSAF depuis rafals (RM-DEMARCHES.md ; lot 7.3). L'URSSAF est simulé (conftest : FauxUrssaf)."""

from datetime import date, datetime, timedelta

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app import config, reglages
from app.modeles.prestataires import Prestataire
from app.modeles.urssaf import DeclarationUrssaf, MandatUrssaf
from app.services import declarations_urssaf as service
from app.services import demarches, urssaf
from tests.test_absences import passe
from tests.test_agenda import MARDI, lea  # noqa: F401 (fixtures)
from tests.test_annonces import fabrique_prestataire, menage, metiers, publier, siret_verifie  # noqa: F401 (fixtures)
from tests.test_rendez_vous import a, dupont, reserver  # noqa: F401 (fixtures)

PARIS = reglages.FUSEAU_AFFICHAGE
SECU = "2 95 07 33 063 045 12"
URL = "/api/moi/prestataire/urssaf"


def secu_valide() -> str:
    """Un numéro d'essai dont la clé est juste (les 2 derniers chiffres sont calculés)."""
    corps = "2950733063045"
    return f"{corps}{97 - int(corps) % 97:02d}"


def profil(base: Session, compte) -> Prestataire:
    base.expire_all()
    return base.scalar(select(Prestataire).where(Prestataire.compte_id == compte.id))


def lea_prete(base: Session, lea, periodicite: str = "mois"):  # noqa: F811
    """Léa a un SIRET vérifié, déclare chaque mois, et a donné son accord."""
    siret_verifie(base, lea)
    lea.client.post("/api/moi/prestataire/demarches/periodicite", json={"periodicite": periodicite})
    reponse = lea.client.post(f"{URL}/mandat", json={"numero_secu": secu_valide(), "accepte": True})
    assert reponse.status_code == 200, reponse.text
    return reponse.json()


def encaisser_le_mois_dernier(base: Session, lea, dupont) -> date:  # noqa: F811
    """Un rendez-vous de 50,00 € payé en espèces, dont la facture est datée du 15 du mois dernier (la période à déclarer)."""
    rdv = reserver(dupont, lea.annonce, a(MARDI, 10)).json()["id"]
    passe(base, rdv)
    assert lea.client.post(f"/api/moi/prestataire/rendez-vous/{rdv}/paye", json={"moyen": "especes"}).status_code == 200
    debut, _, _ = demarches.periode_a_declarer("mois", datetime.now(PARIS).date())
    base.execute(text("UPDATE facture SET emise_le = :quand WHERE prestataire_id = :id"),
                 {"quand": datetime(debut.year, debut.month, 15, 12, tzinfo=PARIS), "id": profil(base, lea).id})
    base.commit()
    return debut


# ---------- L'accord ----------


def test_donner_puis_retirer_son_accord(lea, base: Session, faux_urssaf) -> None:  # noqa: F811
    sans_siret = lea.client.post(f"{URL}/mandat", json={"numero_secu": secu_valide(), "accepte": True})
    siret_verifie(base, lea)
    avant = lea.client.get("/api/moi/prestataire/demarches").json()["urssaf"]
    faux_numero = lea.client.post(f"{URL}/mandat", json={"numero_secu": SECU, "accepte": True})
    sans_case = lea.client.post(f"{URL}/mandat", json={"numero_secu": secu_valide(), "accepte": False})
    donne = lea.client.post(f"{URL}/mandat", json={"numero_secu": secu_valide(), "accepte": True})
    deux_fois = lea.client.post(f"{URL}/mandat", json={"numero_secu": secu_valide(), "accepte": True})
    retire = lea.client.post(f"{URL}/mandat/retirer")
    encore = lea.client.post(f"{URL}/mandat/retirer")
    mandat = base.scalar(select(MandatUrssaf).where(MandatUrssaf.prestataire_id == profil(base, lea).id))

    assert sans_siret.status_code == 400 and "SIRET vérifié" in sans_siret.json()["detail"]
    assert avant["mandat_le"] is None and avant["demonstration"] is False and "Je donne mandat à rafals" in avant["texte_mandat"]
    assert faux_numero.status_code == 400 and "sécurité sociale" in faux_numero.json()["detail"]
    assert sans_case.status_code == 400 and "Cochez" in sans_case.json()["detail"]
    assert donne.status_code == 200 and donne.json()["urssaf"]["mandat_le"] is not None
    assert deux_fois.status_code == 400 and "déjà donné" in deux_fois.json()["detail"]
    # L'URSSAF a été prévenu de l'accord puis de son retrait, avec le SIRET et le numéro de sécurité sociale
    assert [x["chemin"] for x in faux_urssaf.appels] == ["/mandats", "/mandats/annulation"]
    assert faux_urssaf.appels[0]["donnees"] == {"siret": "44306184100047", "nir": secu_valide()}
    # Retiré : la ligne reste (la preuve), le numéro de sécurité sociale est effacé
    assert retire.status_code == 200 and retire.json()["urssaf"]["mandat_le"] is None and encore.status_code == 400
    assert mandat.retire_le is not None and mandat.numero_secu is None and mandat.texte == service.TEXTE_MANDAT


def test_l_urssaf_refuse_l_accord_ou_ne_repond_pas(lea, base: Session, faux_urssaf) -> None:  # noqa: F811
    siret_verifie(base, lea)
    faux_urssaf.refus = "Cotisant inconnu."
    refuse = lea.client.post(f"{URL}/mandat", json={"numero_secu": secu_valide(), "accepte": True})
    faux_urssaf.refus, faux_urssaf.panne = None, True
    panne = lea.client.post(f"{URL}/mandat", json={"numero_secu": secu_valide(), "accepte": True})

    assert refuse.status_code == 400 and "Cotisant inconnu." in refuse.json()["detail"]
    assert panne.status_code == 503 and "ne répond pas" in panne.json()["detail"]
    assert lea.client.get("/api/moi/prestataire/demarches").json()["urssaf"]["mandat_le"] is None  # rien n'est enregistré


# ---------- La déclaration ----------


def test_lea_declare_le_mois_dernier(lea, dupont, base: Session, faux_urssaf, mails_envoyes) -> None:  # noqa: F811
    lea_prete(base, lea)
    debut = encaisser_le_mois_dernier(base, lea, dupont)
    a_declarer = lea.client.get("/api/moi/prestataire/demarches", params={"annee": debut.year}).json()["urssaf"]["a_declarer"]
    estimation = lea.client.post(f"{URL}/estimation", json={"ailleurs_centimes": 20000})
    sans_case = lea.client.post(f"{URL}/declaration", json={"ailleurs_centimes": 20000, "certifie": False})
    declare = lea.client.post(f"{URL}/declaration", json={"ailleurs_centimes": 20000, "certifie": True})
    deux_fois = lea.client.post(f"{URL}/declaration", json={"ailleurs_centimes": 0, "certifie": True})
    apres = lea.client.get("/api/moi/prestataire/demarches", params={"annee": debut.year}).json()
    mois = apres["mois"][debut.month - 1]
    envoi = next(x for x in faux_urssaf.appels if x["chemin"] == "/declarations")
    # Les rappels de cette période s'arrêtent : 7 jours avant la date limite, aucun mail
    limite = demarches.limite_du_mois(debut.year, debut.month)
    demarches.envoyer_rappels(base, datetime(limite.year, limite.month, limite.day, 12, tzinfo=PARIS) - timedelta(days=7))
    base.commit()
    rappels = [m for m in mails_envoyes if m["a"] == lea.email and "à déclarer avant" in m["texte"]]
    ligne = base.scalar(select(DeclarationUrssaf).where(DeclarationUrssaf.prestataire_id == profil(base, lea).id))

    assert a_declarer["periodicite"] == "mois" and a_declarer["debut"] == debut.isoformat()
    assert (a_declarer["montant_rafals_centimes"], a_declarer["nombre_factures"]) == (5000, 1)
    # 50,00 € sur rafals + 200,00 € ailleurs = 250,00 € ; cotisations 21,2 % = 53,00 €
    assert estimation.json() == {"total_centimes": 25000, "cotisations_centimes": 5300}
    assert sans_case.status_code == 400 and "certifiez" in sans_case.json()["detail"]
    assert declare.status_code == 200 and declare.json()["urssaf"]["a_declarer"] is None
    assert (mois["declaree_centimes"], mois["cotisations_centimes"]) == (25000, 5300) and mois["declaree_le"] is not None
    assert deux_fois.status_code == 400 and "rien à déclarer" in deux_fois.json()["detail"]
    assert envoi["donnees"]["chiffreAffaires"] == {"prestationsServices": 250.0} and envoi["donnees"]["dateDebut"] == debut.isoformat()
    assert envoi["cle"] == f"rafals-{ligne.prestataire_id}-mois-{debut:%Y%m%d}"
    assert (ligne.montant_rafals_centimes, ligne.montant_ailleurs_centimes, ligne.nature) == (5000, 20000, "services")
    assert ligne.reference_urssaf.startswith("ZZTEST-") and ligne.demonstration is False
    mail = next(m for m in mails_envoyes if m["a"] == lea.email and "est envoyée" in m["sujet"])
    assert "250,00 €" in mail["texte"] and "53,00 €" in mail["texte"] and "n'a pas payé" in mail["texte"]
    assert rappels == []


def test_refus_ou_panne_rien_n_est_declare(lea, base: Session, faux_urssaf) -> None:  # noqa: F811
    sans_accord = lea.client.post(f"{URL}/declaration", json={"ailleurs_centimes": 0, "certifie": True})
    siret_verifie(base, lea)
    lea.client.post(f"{URL}/mandat", json={"numero_secu": secu_valide(), "accepte": True})
    sans_choix = lea.client.post(f"{URL}/declaration", json={"ailleurs_centimes": 0, "certifie": True})
    lea.client.post("/api/moi/prestataire/demarches/periodicite", json={"periodicite": "mois"})
    negatif = lea.client.post(f"{URL}/declaration", json={"ailleurs_centimes": -100, "certifie": True})
    faux_urssaf.refus = "La période est déjà déclarée."
    refuse = lea.client.post(f"{URL}/declaration", json={"ailleurs_centimes": 0, "certifie": True})
    faux_urssaf.refus, faux_urssaf.panne = None, True
    panne = lea.client.post(f"{URL}/declaration", json={"ailleurs_centimes": 0, "certifie": True})
    faux_urssaf.panne = False
    rien = base.scalar(select(DeclarationUrssaf.id).where(DeclarationUrssaf.prestataire_id == profil(base, lea).id))
    zero = lea.client.post(f"{URL}/declaration", json={"ailleurs_centimes": 0, "certifie": True})  # 0 € se déclare aussi

    assert sans_accord.status_code == 400 and "accord" in sans_accord.json()["detail"]
    assert sans_choix.status_code == 400 and "chaque mois ou chaque trimestre" in sans_choix.json()["detail"]
    assert negatif.status_code == 400 and "positif" in negatif.json()["detail"]
    assert refuse.status_code == 400 and "déjà déclarée" in refuse.json()["detail"] and "Rien n'a été envoyé" in refuse.json()["detail"]
    assert panne.status_code == 503 and rien is None
    assert zero.status_code == 200
    # Après un mois déclaré, passer à « chaque trimestre » ne permet pas de redéclarer les mêmes jours
    lea.client.post("/api/moi/prestataire/demarches/periodicite", json={"periodicite": "trimestre"})
    assert lea.client.get("/api/moi/prestataire/demarches").json()["urssaf"]["a_declarer"] is None


def test_periode_a_declarer_par_trimestre(lea, base: Session) -> None:  # noqa: F811
    lea_prete(base, lea, "trimestre")
    prestataire = profil(base, lea)
    octobre = service.a_declarer(base, prestataire, datetime(2026, 10, 24, 10, tzinfo=PARIS))
    novembre = service.a_declarer(base, prestataire, datetime(2026, 11, 5, 10, tzinfo=PARIS))

    assert (octobre.debut, octobre.fin, octobre.limite, octobre.nom) == (date(2026, 7, 1), date(2026, 9, 30), date(2026, 10, 31),
                                                                        "3e trimestre 2026")
    assert novembre is None  # la date limite du 31/10 est passée : il faut passer par le site de l'URSSAF


def test_mode_demonstration_rien_n_est_envoye(lea, base: Session, faux_urssaf, monkeypatch) -> None:  # noqa: F811
    monkeypatch.setattr(config, "URSSAF_IDENTIFIANT", "")  # pas d'accès à l'URSSAF : comme sur le PC de Raphael aujourd'hui
    etat = lea_prete(base, lea)
    declare = lea.client.post(f"{URL}/declaration", json={"ailleurs_centimes": 145000, "certifie": True})
    ligne = base.scalar(select(DeclarationUrssaf).where(DeclarationUrssaf.prestataire_id == profil(base, lea).id))

    assert etat["urssaf"]["demonstration"] is True and declare.status_code == 200 and faux_urssaf.appels == []
    assert ligne.demonstration is True and ligne.cotisations_centimes == 30740  # 1 450,00 € × 21,2 %, estimé par rafals
    personne = urssaf.Personne("44306184100047", secu_valide())
    assert urssaf.estimer(personne, "liberale", date(2026, 7, 1), date(2026, 9, 30), 100000).cotisations_centimes == 25600


def test_il_faut_etre_prestataire(dupont, client) -> None:  # noqa: F811
    assert dupont.client.post(f"{URL}/mandat", json={"numero_secu": secu_valide(), "accepte": True}).status_code == 404
    assert client.post(f"{URL}/declaration", json={"ailleurs_centimes": 0, "certifie": True}).status_code == 401
