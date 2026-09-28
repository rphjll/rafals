"""Garde-fou et outils communs des tests.

Garde-fou : les tests ne tournent QUE sur rafals_test_db, avec le compte rafals_app.
Vérifié deux fois : dans les réglages, puis auprès de la base elle-même
(au cas où un réglage mentirait). Sinon, les tests s'arrêtent avant d'avoir rien écrit.
"""

import re
from collections.abc import Iterator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

BASE_DE_TEST = "rafals_test_db"
COMPTE_APPLICATION = "rafals_app"
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


@pytest.fixture
def mails_envoyes(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, str]]:
    """Remplace l'envoi réel : les mails sont gardés dans une liste que le test peut lire."""
    from app.services import mails

    envoyes: list[dict[str, str]] = []
    monkeypatch.setattr(
        mails, "envoyer_mail", lambda a, sujet, texte: envoyes.append({"a": a, "sujet": sujet, "texte": texte})
    )
    return envoyes
