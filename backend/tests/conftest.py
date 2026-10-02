"""Garde-fou et outils communs des tests.

Garde-fou : les tests ne tournent QUE sur rafals_test_db, avec le compte rafals_app.
Vérifié deux fois : dans les réglages, puis auprès de la base elle-même
(au cas où un réglage mentirait). Sinon, les tests s'arrêtent avant d'avoir rien écrit.
"""

import re
from collections import defaultdict
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import UTC, date, datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

BASE_DE_TEST = "rafals_test_db"
COMPTE_APPLICATION = "rafals_app"
COMPARTIMENT_DE_TEST = "rafals-test"
MOT_DE_PASSE_TEST = "MaisonBleue44"


def pytest_sessionstart(session: pytest.Session) -> None:
    from app import config
    from app.db import moteur

    if config.DB_NOM != BASE_DE_TEST or config.DB_UTILISATEUR != COMPTE_APPLICATION:
        pytest.exit(
            f"STOP : les tests doivent tourner sur {BASE_DE_TEST} avec {COMPTE_APPLICATION} "
            f"(réglages actuels : {config.DB_NOM} / {config.DB_UTILISATEUR}). "
            "Lance-les avec lancer-tests.bat.",
            returncode=2,
        )

    with moteur.connect() as connexion:
        base, compte = connexion.execute(text("SELECT current_database(), current_user")).one()
    if base != BASE_DE_TEST or compte != COMPTE_APPLICATION:
        pytest.exit(
            f"STOP : connecté à {base} avec {compte}, au lieu de {BASE_DE_TEST} avec {COMPTE_APPLICATION}.",
            returncode=2,
        )

    # Même protection pour le stockage : compartiment des tests seulement, vidé au début
    if config.S3_COMPARTIMENT != COMPARTIMENT_DE_TEST:
        pytest.exit(
            f"STOP : les tests doivent utiliser le compartiment {COMPARTIMENT_DE_TEST} "
            f"(réglage actuel : {config.S3_COMPARTIMENT}). Lance-les avec lancer-tests.bat.",
            returncode=2,
        )
    from app.services import stockage

    for cle in stockage.lister_cles():
        stockage.supprimer(cle)

    # Données de référence : la liste des métiers (la base de test ne reçoit que la structure)
    from scripts.charger_communes import charger as charger_communes
    from scripts.charger_metiers import charger
    from scripts.charger_mots_interdits import charger as charger_mots_interdits

    with Session(moteur) as db:
        charger(db)
        charger_communes(db)
        charger_mots_interdits(db)
        db.commit()


def email_essai() -> str:
    """Adresse d'essai unique, marquée @example.com (jamais une vraie adresse)."""
    return f"zztest.{uuid4().hex[:10]}@example.com"


def jeton_du_mail(mail: dict[str, str]) -> str:
    trouve = re.search(r"jeton=([\w-]+)", mail["texte"])
    assert trouve, f"Aucun lien dans le mail : {mail['texte']}"
    return trouve.group(1)


@pytest.fixture
def client() -> TestClient:
    from app.main import app

    return TestClient(app)


@pytest.fixture
def base() -> Iterator[Session]:
    from app.db import moteur

    with Session(moteur) as db:
        yield db


@dataclass
class CompteEssai:
    id: int
    email: str
    client: TestClient  # navigateur à part, déjà connecté avec ce compte


@pytest.fixture
def fabrique_compte(mails_envoyes, base: Session) -> Callable[..., CompteEssai]:
    """Crée un compte d'essai connecté. Ex. fabrique_compte(age=16) → Lucas, 16 ans, adresse vérifiée."""
    from app.main import app

    def fabriquer(*, age: int = 30, verifie: bool = True, administrateur: bool = False) -> CompteEssai:
        client = TestClient(app)
        email = email_essai()
        aujourd_hui = datetime.now(UTC).date()
        reponse = client.post(
            "/api/comptes",
            json={
                "email": email,
                "mot_de_passe": MOT_DE_PASSE_TEST,
                "prenom": "Essai",
                "nom": "ZZTEST",
                "telephone": "0600000000",
                "date_naissance": date(aujourd_hui.year - age, 1, 1).isoformat(),
            },
        )
        assert reponse.status_code == 201, reponse.text
        identifiant = reponse.json()["id"]
        base.execute(
            text("UPDATE compte SET email_verifie_le = CASE WHEN :v THEN now() END, est_administrateur = :a WHERE id = :id"),
            {"v": verifie, "a": administrateur, "id": identifiant},
        )
        base.commit()
        assert client.post("/api/connexion", json={"email": email, "mot_de_passe": MOT_DE_PASSE_TEST}).status_code == 200
        return CompteEssai(identifiant, email, client)

    return fabriquer


@pytest.fixture(autouse=True)
def repertoire_de_l_etat(monkeypatch: pytest.MonkeyPatch) -> dict[str, list]:
    """Les tests n'appellent jamais le vrai service de l'État (internet) : par défaut il est « en panne » ;
    un test y met la réponse voulue : repertoire_de_l_etat["reponse"] = [ {entreprise…} ]."""
    from app.services import siret

    faux: dict[str, list] = {}

    def interroger(_siret: str) -> list:
        if "reponse" not in faux:
            raise siret.ServiceIndisponible("service de l'État simulé en panne")
        return faux["reponse"]

    monkeypatch.setattr(siret, "interroger", interroger)
    return faux


@pytest.fixture(autouse=True)
def ia_de_moderation(monkeypatch: pytest.MonkeyPatch) -> dict[str, float]:
    """Les tests n'appellent jamais la vraie IA : un texte qui contient « ZZINJURE » reçoit 0,99, les autres 0,01 ;
    un test peut simuler une panne : ia_de_moderation["panne"] = 1."""
    from app.services import moderation

    reglage: dict[str, float] = {}

    def interroger(texte: str) -> float:
        if reglage.get("panne"):
            raise OSError("IA de modération simulée en panne")
        return 0.99 if "ZZINJURE" in texte else 0.01

    monkeypatch.setattr(moderation, "interroger", interroger)
    return reglage


@pytest.fixture
def mails_envoyes(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, str]]:
    """Remplace l'envoi réel : les mails sont gardés dans une liste que le test peut lire."""
    from app.services import mails

    envoyes: list[dict[str, str]] = []
    monkeypatch.setattr(
        mails, "envoyer_mail", lambda a, sujet, texte: envoyes.append({"a": a, "sujet": sujet, "texte": texte})
    )
    return envoyes


class FauxStripe:
    """Stripe simulé : comptes des prestataires, pages de paiement, paiements, remboursements, soldes, versements.
    Frais de carte comme le vrai : 1,5 % + 0,25 € (ex. 1,00 € sur 50 €). `appels` garde chaque demande faite à Stripe ;
    `panne = True` simule un Stripe injoignable."""

    SECRET = "whsec_zztest"

    def __init__(self) -> None:
        self.appels: list[dict] = []
        self.panne = False
        self.comptes: dict[str, dict] = {}
        self.sessions: dict[str, dict] = {}
        self.intents: dict[str, dict] = {}
        # compte → {"available": …, "pending": …} en centimes ; vide pour les comptes laissés par les tests d'avant
        self.soldes: dict[str, dict[str, int]] = defaultdict(lambda: {"available": 0, "pending": 0})
        self._deja: dict[str, dict] = {}
        self._numero = 0

    def _id(self, prefixe: str) -> str:
        self._numero += 1  # unique d'un test à l'autre : les lignes d'essai restent dans la base de test
        return f"{prefixe}_zztest{uuid4().hex[:8]}{self._numero}"

    @staticmethod
    def frais(montant: int) -> int:
        return (montant * 15 + 500) // 1000 + 25

    def appeler(self, methode: str, chemin: str, donnees: dict | None = None, *, compte: str | None = None,
                cle_unique: str | None = None) -> dict:
        from app.services.stripe_api import StripeIndisponible

        donnees = donnees or {}
        self.appels.append({"methode": methode, "chemin": chemin, "donnees": donnees, "compte": compte, "cle": cle_unique})
        if self.panne:
            raise StripeIndisponible("Stripe simulé en panne")
        if cle_unique and cle_unique in self._deja:  # même demande refaite : Stripe ne la refait pas
            return self._deja[cle_unique]
        reponse = self._repondre(methode, chemin, donnees, compte)
        if cle_unique:
            self._deja[cle_unique] = reponse
        return reponse

    def _repondre(self, methode: str, chemin: str, donnees: dict, compte: str | None) -> dict:
        morceaux = chemin.strip("/").split("/")
        if chemin == "/v1/accounts" and methode == "POST":
            identifiant = self._id("acct")
            self.comptes[identifiant] = {"id": identifiant, "charges_enabled": False, "payouts_enabled": False, **donnees}
            self.soldes[identifiant] = {"available": 0, "pending": 0}
            return self.comptes[identifiant]
        if chemin == "/v1/account_links":
            return {"url": f"https://connect.stripe.com/setup/zztest/{donnees['account']}"}
        if morceaux[:2] == ["v1", "accounts"] and methode == "GET":
            return self.comptes[morceaux[2]]
        if chemin == "/v1/checkout/sessions":
            identifiant = self._id("cs")
            self.sessions[identifiant] = {"id": identifiant, "compte": compte, **donnees}
            return {"id": identifiant, "url": f"https://checkout.stripe.com/c/pay/{identifiant}"}
        if morceaux[:2] == ["v1", "payment_intents"]:
            pi = self.intents.get(morceaux[2], {"id": morceaux[2], "frais": 0, "commission": 0})  # (d'un test d'avant)
            return {"id": pi["id"], "latest_charge": {"application_fee": f"fee_{pi['id']}", "balance_transaction": {
                "fee_details": [{"type": "stripe_fee", "amount": pi["frais"]},
                                {"type": "application_fee", "amount": pi["commission"]}]}}}
        if chemin == "/v1/refunds":
            self.soldes[compte or ""]["available"] -= int(donnees["amount"])
            return {"id": self._id("re"), "amount": donnees["amount"]}
        if morceaux[:2] == ["v1", "application_fees"]:
            pi = self.intents.get(morceaux[2].removeprefix("fee_"), {"compte": "", "commission": 0})
            self.soldes[pi["compte"]]["available"] += pi["commission"]
            return {"id": self._id("fr")}
        if chemin == "/v1/balance":
            solde = self.soldes[compte or ""]
            return {"available": [{"amount": solde["available"], "currency": "eur"}],
                    "pending": [{"amount": solde["pending"], "currency": "eur"}]}
        if chemin == "/v1/payouts":
            self.soldes[compte or ""]["available"] -= int(donnees["amount"])
            return {"id": self._id("po"), "amount": donnees["amount"]}
        raise AssertionError(f"Appel à Stripe non prévu dans le faux Stripe : {methode} {chemin}")

    # ---------- Ce que fait le client ou Stripe, pour les tests ----------

    def payer(self, session_id: str | None = None, *, en_attente: bool = False) -> dict:
        """Le client paie sur la page de Stripe (la dernière ouverte par défaut) : l'argent arrive sur le compte du
        prestataire (moins la commission de rafals et les frais). Renvoie le message que Stripe envoie à rafals."""
        session = self.sessions[session_id or list(self.sessions)[-1]]
        montant = int(session["line_items"][0]["price_data"]["unit_amount"])
        commission = int(session["payment_intent_data"]["application_fee_amount"])
        pi = self._id("pi")
        self.intents[pi] = {"id": pi, "compte": session["compte"], "montant": montant, "commission": commission,
                            "frais": self.frais(montant)}
        self.soldes[session["compte"]]["pending" if en_attente else "available"] += montant - commission - self.frais(montant)
        return self.evenement("checkout.session.completed", {
            "id": session["id"], "payment_status": "paid", "payment_intent": pi, "metadata": session["metadata"]})

    def compte_verifie(self, compte: str) -> dict:
        """Stripe a vérifié l'identité et le RIB du prestataire."""
        self.comptes[compte].update(charges_enabled=True, payouts_enabled=True)
        return self.evenement("account.updated", self.comptes[compte])

    @staticmethod
    def evenement(sorte: str, objet: dict) -> dict:
        return {"id": f"evt_zztest_{uuid4().hex[:8]}", "type": sorte, "data": {"object": objet}}

    def envoyer(self, client: TestClient, evenement: dict, *, secret: str | None = None):
        """Envoie le message à rafals comme Stripe : avec la signature calculée sur le secret partagé."""
        import hashlib
        import hmac
        import json
        import time

        corps = json.dumps(evenement).encode()
        horodatage = str(int(time.time()))
        signature = hmac.new((secret or self.SECRET).encode(), f"{horodatage}.".encode() + corps, hashlib.sha256).hexdigest()
        return client.post("/api/stripe/evenements", content=corps,
                           headers={"Stripe-Signature": f"t={horodatage},v1={signature}", "Content-Type": "application/json"})


@pytest.fixture(autouse=True)
def faux_stripe(monkeypatch: pytest.MonkeyPatch) -> FauxStripe:
    """Les tests n'appellent jamais le vrai Stripe ; les clés sont fausses (aucune vraie carte, aucun appel à internet)."""
    from app import config
    from app.services import stripe_api

    faux = FauxStripe()
    monkeypatch.setattr(config, "STRIPE_CLE_SECRETE", "sk_test_zztest")
    monkeypatch.setattr(config, "STRIPE_SECRET_WEBHOOK", FauxStripe.SECRET)
    monkeypatch.setattr(stripe_api, "appeler", faux.appeler)
    return faux
