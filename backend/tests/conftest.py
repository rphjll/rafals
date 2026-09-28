"""Garde-fou : les tests ne tournent QUE sur rafals_test_db, avec le compte rafals_app.

Vérifié deux fois : dans les réglages, puis auprès de la base elle-même
(au cas où un réglage mentirait). Sinon, les tests s'arrêtent avant d'avoir rien écrit.
"""

import pytest
from sqlalchemy import text

BASE_DE_TEST = "rafals_test_db"
COMPTE_APPLICATION = "rafals_app"


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
