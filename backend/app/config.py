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

# IA de modération des avis (conteneur « moderation », lot 4.8)
MODERATION_ADRESSE = os.environ.get("MODERATION_ADRESSE", "http://moderation:8000")
MODERATION_DELAI_SECONDES = float(os.environ.get("MODERATION_DELAI_SECONDES", "10"))

# Stockage de fichiers compatible S3 : Garage sur le PC, stockage d'OVH en ligne
S3_ADRESSE = os.environ.get("S3_ADRESSE", "http://garage:3900")
S3_REGION = os.environ.get("S3_REGION", "garage")
S3_COMPARTIMENT = os.environ.get("S3_COMPARTIMENT", "rafals")
S3_CLE_ACCES = os.environ.get("S3_CLE_ACCES", "")
S3_CLE_SECRETE = os.environ.get("S3_CLE_SECRETE", "")

# Paiement par carte (Stripe, lot 5.1). Clés du tableau de bord de Stripe, dans le fichier .env (jamais dans git).
# Sans clé secrète, le paiement par carte est simplement indisponible (les espèces restent possibles).
STRIPE_CLE_SECRETE = os.environ.get("STRIPE_CLE_SECRETE", "")
STRIPE_SECRET_WEBHOOK = os.environ.get("STRIPE_SECRET_WEBHOOK", "")
STRIPE_VERSION = os.environ.get("STRIPE_VERSION", "")  # vide : la version choisie dans le compte Stripe

# Identité de rafals sur ses factures de commission (lot 5.5). Vides tant que rafals n'est pas une entreprise :
# les factures de commission ne sont alors pas créées (les commissions restent comptées).
RAFALS_NOM = os.environ.get("RAFALS_NOM", "")
RAFALS_SIRET = os.environ.get("RAFALS_SIRET", "")
RAFALS_ADRESSE = os.environ.get("RAFALS_ADRESSE", "")

# Guichet unique de l'État (API de l'INPI, lot 7.1) : compte e-procedures de rafals, dans le fichier .env (jamais dans git).
# Sans identifiants, rafals est en « démonstration » : rien n'est envoyé à l'État (services/guichet.py).
# Adresse par défaut : l'espace d'essai de l'INPI ; la vraie (https://guichet-unique.inpi.fr) se met à la mise en ligne.
INPI_ADRESSE = os.environ.get("INPI_ADRESSE", "https://guichet-unique-demo.inpi.fr")
INPI_IDENTIFIANT = os.environ.get("INPI_IDENTIFIANT", "")
INPI_MOT_DE_PASSE = os.environ.get("INPI_MOT_DE_PASSE", "")

# Adresse des écrans, pour fabriquer les liens envoyés par mail
ADRESSE_SITE = os.environ.get("ADRESSE_SITE", "http://localhost:5174")

# En ligne (https), le cookie de connexion ne doit voyager que chiffré
COOKIE_SECURISE = os.environ.get("COOKIE_SECURISE", "non") == "oui"
