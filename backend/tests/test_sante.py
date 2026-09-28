"""Le serveur tourne, joint la base avec le bon compte, et ce compte ne peut pas toucher à la structure."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError

from app.db import moteur
from app.main import app

client = TestClient(app)


def test_health_repond_ok_avec_le_compte_application() -> None:
    reponse = client.get("/health")

    assert reponse.status_code == 200
    assert reponse.json() == {"serveur": "ok", "base": "ok", "compte": "rafals_app"}


def test_le_compte_application_ne_peut_pas_creer_de_table() -> None:
    with moteur.connect() as connexion:
        with pytest.raises(ProgrammingError, match="permission denied"):
            connexion.execute(text("CREATE TABLE zz_essai (id int)"))
