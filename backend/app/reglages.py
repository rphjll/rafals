"""Valeurs des règles métier, à un seul endroit (jamais écrites en dur dans les calculs).

Source : .doc/regles-metier/RM-COMPTES.md (validé le 27/09/2026).
"""

from datetime import timedelta
from zoneinfo import ZoneInfo

# Heure affichée aux utilisateurs (les dates sont enregistrées en UTC)
FUSEAU_AFFICHAGE = ZoneInfo("Europe/Paris")

AGE_MINIMUM = 16
# Entre AGE_MINIMUM et AGE_MAJORITE : accord des parents vérifié avant de réserver ou publier
AGE_MAJORITE = 18
MOT_DE_PASSE_LONGUEUR_MIN = 10

# Accord des parents : formats et taille acceptés (validé par Raphael le 28/09/2026)
ACCORD_TYPES_ACCEPTES = {"application/pdf": "PDF", "image/jpeg": "JPG", "image/png": "PNG"}
ACCORD_TAILLE_MAX_OCTETS = 5 * 1024 * 1024

# Profil prestataire (RM-PRESTATAIRES.md ; valeurs choisies par Claude le 28/09/2026 en mode « tout seul », à valider)
PRESTATAIRE_DISTANCE_MAX_KM = 100
PRESTATAIRE_METIERS_SECONDAIRES_MAX = 5
PRESTATAIRE_NOM_LONGUEUR = (2, 80)
PRESTATAIRE_PRESENTATION_MAX = 1000
PHOTO_TYPES_ACCEPTES = {"image/jpeg", "image/png"}
PHOTO_TAILLE_MAX_OCTETS = 5 * 1024 * 1024

SESSION_DUREE = timedelta(days=30)
LIEN_MOT_DE_PASSE_DUREE = timedelta(hours=1)
# Non fixé par les règles : choix de Claude le 28/09/2026 (voir journal de SUIVI-DEV.md)
LIEN_VERIFICATION_DUREE = timedelta(days=7)

ECHECS_AVANT_BLOCAGE = 5
BLOCAGE_DUREE = timedelta(minutes=15)

NOM_COOKIE_SESSION = "rafals_session"
