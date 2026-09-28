"""Réglages du serveur, lus dans les variables d'environnement (fichier .env)."""

import os

DB_HOTE = os.environ.get("DB_HOTE", "db")
DB_PORT = int(os.environ.get("DB_PORT", "5432"))
DB_NOM = os.environ["POSTGRES_DB"]

# Le serveur se connecte TOUJOURS avec le compte application (jamais l'administrateur)
DB_UTILISATEUR = os.environ["RAFALS_APP_USER"]
DB_MOT_DE_PASSE = os.environ["RAFALS_APP_PASSWORD"]
