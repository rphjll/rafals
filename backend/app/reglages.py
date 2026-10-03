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

# Paiement par carte (RM-PAIEMENTS.md, validé par Raphael le 02/10/2026)
COMMISSION_POURCENT = 5  # gardé par rafals sur chaque paiement par carte (rien sur les espèces)
PAIEMENT_DELAI = timedelta(minutes=30)  # pour payer sur la page de Stripe ; ensuite la réservation est annulée (MLD 5.1)
VERSEMENT_APRES_FIN = timedelta(hours=48)  # l'argent part vers le prestataire 48 h après la fin du rendez-vous
ABSENCE_SIGNALEMENT_DELAI_CARTE = timedelta(hours=48)  # payé par carte : 48 h pour signaler l'absence du prestataire
TACHE_PAIEMENTS_MINUTES = 5

# Devis (RM-DEVIS.md, validé par Raphael le 02/10/2026 ; maxima validés avec le MLD 5.3 le 03/10/2026)
DEMANDE_DEVIS_TEXTE = (10, 2000)
DEMANDE_DEVIS_PHOTOS_MAX = 5
DEVIS_LIGNES_MAX = 20
DEVIS_LIBELLE = (2, 200)
DEVIS_VALIDITE_DEFAUT = timedelta(days=30)  # « Valable jusqu'au » rempli d'avance, modifiable
DEVIS_TAUX_TVA_POUR_MILLE = (55, 100, 200)  # 5,5 %, 10 %, 20 %
DEVIS_MENTION_SANS_TVA = "TVA non applicable, art. 293 B du CGI"
DEVIS_RELANCES_SOLDE = (timedelta(days=3), timedelta(days=10))  # rappels au client qui n'a pas payé le solde (choix de Claude)

# Factures (RM-FACTURES.md, validé par Raphael le 02/10/2026 ; MLD 5.5 du 03/10/2026)
FACTURE_MENTION_SANS_TVA = DEVIS_MENTION_SANS_TVA
# ⚠️ À confirmer par un comptable : taux appliqué aux rendez-vous d'un prestataire qui facture la TVA (les annonces
# n'ont pas de taux ; le prix affiché est toutes taxes comprises). Choix de Claude : le taux normal, 20 %.
FACTURE_TVA_RENDEZ_VOUS_POUR_MILLE = 200
FACTURE_MOYENS_DIRECTS = ("especes", "cheque", "virement")

# SIRET resté « à vérifier » (service de l'État en panne) : nouvel essai automatique (lot 2.4)
SIRET_REVERIFICATION_MINUTES = 30

SESSION_DUREE = timedelta(days=30)
LIEN_MOT_DE_PASSE_DUREE = timedelta(hours=1)
# Non fixé par les règles : choix de Claude le 28/09/2026 (voir journal de SUIVI-DEV.md)
LIEN_VERIFICATION_DUREE = timedelta(days=7)

ECHECS_AVANT_BLOCAGE = 5
BLOCAGE_DUREE = timedelta(minutes=15)

NOM_COOKIE_SESSION = "rafals_session"
