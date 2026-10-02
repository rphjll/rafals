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

# Comptes inactifs (RM-CLIENTS.md, validé le 28/09/2026) : mail après 3 ans sans connexion, fermeture 30 jours après
INACTIVITE_DUREE = timedelta(days=3 * 365)
INACTIVITE_PREAVIS = timedelta(days=30)
ADRESSE_LIGNE_LONGUEUR = (3, 120)

# Annonces (RM-ANNONCES.md, validé le 29/09/2026 ; longueur du titre proposée par Claude dans le MLD du lot 3.1)
ANNONCE_TITRE_LONGUEUR = (3, 80)
ANNONCE_DESCRIPTION_MAX = 1000
ANNONCE_PHOTOS_MAX = 5
ANNONCES_EN_LIGNE_MAX = 20

# Agenda (RM-AGENDA.md, validé le 29/09/2026). Valeurs au départ : aussi dans db/schema_v8.sql (DEFAULT)
AGENDA_PAS_CHOIX = (15, 30, 60)
AGENDA_PAS_DEFAUT = 15
AGENDA_PAUSE_DEFAUT = 0
RESERVATION_DELAI_MIN_DEFAUT_MINUTES = 120
RESERVATION_DELAI_MAX_DEFAUT_MOIS = 2
# Bornes des réglages (proposées par Claude au lot 3.3, validées par Raphael le 30/09/2026)
AGENDA_PAUSE_MAX_MINUTES = 180
RESERVATION_DELAI_MIN_MAX_MINUTES = 7 * 24 * 60
RESERVATION_DELAI_MAX_MAX_MOIS = 12

# Recherche (RM-RECHERCHE.md, validé le 30/09/2026) : note pondérée = (somme + 5 × 4 ★) ÷ (nombre d'avis + 5)
RECHERCHE_AVIS_FICTIFS = 5
RECHERCHE_NOTE_FICTIVE = 4
RECHERCHE_RESULTATS_PAR_PAGE = 30
RECHERCHE_METIERS_VOISINS = 5

# Rendez-vous (RM-RENDEZ-VOUS.md, validé le 30/09/2026). Valeurs au départ : aussi dans db/schema_v9.sql (DEFAULT)
ANNULATION_DELAI_CHOIX_HEURES = (2, 12, 24, 48)
DEMANDE_REPONSE_DELAI = timedelta(hours=24)
DEMANDE_RAPPEL_AVANT_FIN = timedelta(hours=2)
RAPPEL_VEILLE_HEURE = 18  # la veille à 18 h (heure de Paris)
RAPPEL_JOUR_MEME_AVANT = timedelta(hours=2)
COORDONNEES_CLIENT_VISIBLES = 3  # mois après le dernier rendez-vous (RM-CLIENTS)
TACHE_RENDEZ_VOUS_MINUTES = 5

# Absences (RM-RENDEZ-VOUS.md, validé le 30/09/2026)
ABSENCE_CONTESTATION_DELAI = timedelta(days=7)
ABSENCE_SIGNALEMENT_DELAI = timedelta(days=7)  # après la fin du rendez-vous (validé par Raphael le 01/10/2026)
ANNULATION_TARDIVE = timedelta(hours=24)
ABSENCES_FENETRE_MOIS = 6
ABSENCES_AVANT_SUSPENSION = 3
SUSPENSION_MOIS = 1
CONTESTATION_LONGUEUR_MIN = 10

# Avis (RM-AVIS.md, validé le 30/09/2026)
AVIS_DELAI = timedelta(days=30)
AVIS_TEXTE_MIN = 10
AVIS_TEXTE_MAX = 1000
REPONSE_TEXTE_MIN = 2
SIGNALEMENT_TEXTE_MIN = 5
AVIS_RAPPEL_HEURE = 10  # le lendemain du rendez-vous, à partir de 10 h (heure de Paris)
# IA de modération (lot 4.8) : au-dessus de cette note (0 à 1), l'avis ou la réponse est refusé comme injurieux.
# Réglage de départ, à ajuster après des essais en français.
AVIS_SEUIL_TOXICITE = 0.7

# SIRET resté « à vérifier » (service de l'État en panne) : nouvel essai automatique (lot 2.4)
SIRET_REVERIFICATION_MINUTES = 30

SESSION_DUREE = timedelta(days=30)
LIEN_MOT_DE_PASSE_DUREE = timedelta(hours=1)
# Non fixé par les règles : choix de Claude le 28/09/2026 (voir journal de SUIVI-DEV.md)
LIEN_VERIFICATION_DUREE = timedelta(days=7)

ECHECS_AVANT_BLOCAGE = 5
BLOCAGE_DUREE = timedelta(minutes=15)

NOM_COOKIE_SESSION = "rafals_session"
