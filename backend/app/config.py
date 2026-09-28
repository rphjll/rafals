"""Réglages techniques du serveur, lus dans les variables d'environnement (fichier .env).

Les valeurs des règles métier (10 caractères, 30 jours…) sont dans reglages.py.
"""

import os

DB_HOTE = os.environ.get("DB_HOTE", "db")
DB_PORT = int(os.environ.get("DB_PORT", "5432"))
DB_NOM = os.environ["POSTGRES_DB"]

# Le serveur se connecte TOUJOURS avec le compte application (jamais l'administrateur)
DB_UTILISATEUR = os.environ["RAFALS_APP_USER"]
DB_MOT_DE_PASSE = os.environ["RAFALS_APP_PASSWORD"]

# Envoi des mails : sur le PC, la boîte « mailpit » les attrape (http://localhost:8025)
SMTP_HOTE = os.environ.get("SMTP_HOTE", "mailpit")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "1025"))
MAIL_EXPEDITEUR = os.environ.get("MAIL_EXPEDITEUR", "rafals <ne-pas-repondre@rafals.fr>")

# Stockage de fichiers compatible S3 : Garage sur le PC, stockage d'OVH en ligne
S3_ADRESSE = os.environ.get("S3_ADRESSE", "http://garage:3900")
S3_REGION = os.environ.get("S3_REGION", "garage")
S3_COMPARTIMENT = os.environ.get("S3_COMPARTIMENT", "rafals")
S3_CLE_ACCES = os.environ.get("S3_CLE_ACCES", "")
S3_CLE_SECRETE = os.environ.get("S3_CLE_SECRETE", "")

# Adresse des écrans, pour fabriquer les liens envoyés par mail
ADRESSE_SITE = os.environ.get("ADRESSE_SITE", "http://localhost:5174")

# En ligne (https), le cookie de connexion ne doit voyager que chiffré
COOKIE_SECURISE = os.environ.get("COOKIE_SECURISE", "non") == "oui"
