"""Connexion à la base PostgreSQL (SQLAlchemy 2 + psycopg 3)."""

from sqlalchemy import URL, create_engine

from app import config

adresse_base = URL.create(
    "postgresql+psycopg",
    username=config.DB_UTILISATEUR,
    password=config.DB_MOT_DE_PASSE,
    host=config.DB_HOTE,
    port=config.DB_PORT,
    database=config.DB_NOM,
)

# pool_pre_ping : vérifie la connexion avant de s'en servir (utile si la base a redémarré)
moteur = create_engine(adresse_base, pool_pre_ping=True)
