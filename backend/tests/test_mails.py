"""Envoi des mails : sans identifiant (Mailpit) ou avec (Brevo, en ligne). Préparé le 17/10/2026."""

import pytest

from app import config
from app.services import mails


class FauxServeur:
    """Remplace smtplib.SMTP : note ce que le serveur de mails aurait reçu, sans rien envoyer."""

    appels: list[tuple] = []

    def __init__(self, hote: str, port: int, timeout: int) -> None:
        FauxServeur.appels.append(("ouvrir", hote, port))

    def __enter__(self):
        return self

    def __exit__(self, *erreur) -> None:
        pass

    def starttls(self) -> None:
        FauxServeur.appels.append(("chiffrer",))

    def login(self, utilisateur: str, mot_de_passe: str) -> None:
        FauxServeur.appels.append(("connexion", utilisateur, mot_de_passe))

    def send_message(self, message) -> None:
        FauxServeur.appels.append(("envoi", message["To"], message["Subject"]))


@pytest.fixture
def faux_serveur(monkeypatch: pytest.MonkeyPatch) -> list[tuple]:
    FauxServeur.appels = []
    monkeypatch.setattr(mails.smtplib, "SMTP", FauxServeur)
    return FauxServeur.appels


def test_sur_le_pc_envoi_sans_connexion(faux_serveur, monkeypatch) -> None:
    # Mailpit : ni chiffrement ni mot de passe
    monkeypatch.setattr(config, "SMTP_UTILISATEUR", "")

    mails.envoyer_mail("zztest.julie@example.com", "Bienvenue", "Bonjour Julie")

    assert faux_serveur == [("ouvrir", config.SMTP_HOTE, config.SMTP_PORT), ("envoi", "zztest.julie@example.com", "Bienvenue")]


def test_en_ligne_liaison_chiffree_puis_connexion(faux_serveur, monkeypatch) -> None:
    # Brevo : smtp-relay.brevo.com, port 587, liaison chiffrée avant de donner le mot de passe
    monkeypatch.setattr(config, "SMTP_HOTE", "smtp-relay.brevo.com")
    monkeypatch.setattr(config, "SMTP_PORT", 587)
    monkeypatch.setattr(config, "SMTP_UTILISATEUR", "zztest@example.com")
    monkeypatch.setattr(config, "SMTP_MOT_DE_PASSE", "cle-smtp-essai")

    mails.envoyer_mail("zztest.karim@example.com", "Rendez-vous confirmé", "Mardi à 10 h")

    assert faux_serveur == [("ouvrir", "smtp-relay.brevo.com", 587), ("chiffrer",),
                            ("connexion", "zztest@example.com", "cle-smtp-essai"),
                            ("envoi", "zztest.karim@example.com", "Rendez-vous confirmé")]
