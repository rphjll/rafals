# rafals — Conventions d'interface (valables pour tous les écrans)

> Reprises de la méthode (règles nées de vrais problèmes sur Teorem), adaptées à rafals le 28/09/2026. Couleurs et formes : `CHARTE-VISUELLE.md`.
> Chaque écran a en plus son propre `ihm/RM-<ECRAN>-IHM.md` (obligatoire), mis à jour dans la même sauvegarde git que toute retouche visible.

## RÈGLE ABSOLUE — un clic produit toujours quelque chose de visible, à l'endroit du clic
1. Le clic fait l'action, ou son étape intermédiaire s'affiche sans avoir à faire défiler. Ex. « Réserver » ouvre aussitôt la fenêtre de confirmation.
2. S'il échoue, le message s'affiche là où l'utilisateur regarde. Ex. « Ce créneau vient d'être pris, choisissez-en un autre » juste au-dessus des créneaux.
3. S'il est interdit, le bouton reste visible, grisé, avec un cadenas et une bulle qui dit pourquoi et quoi faire. Ex. « 🔒 Payer par carte » chez Karim : « Karim n'a pas encore de SIRET : il ne peut être payé qu'en espèces… ».

## Structure des pages
- En-tête fixe en haut : logo « rafals. » à gauche (retour à l'accueil), menu à droite (Accueil · Trouver un prestataire · Messages · Mon activité · Mon profil / Proposer mes services · pastille du compte ; refait le 07/10/2026). Sous l'en-tête, sur les pages rangées dans « Mon activité », un sous-menu les montre (`AppSousMenu`) ; la liste des fonctions est écrite une seule fois, dans `frontend/src/outils/activite.ts` (tuiles de la page et sous-menu) ; détail : `ihm/RM-ENTETE-IHM.md` et `ihm/RM-MON-ACTIVITE-IHM.md`. Sur téléphone, les entrées sont dans la barre du bas (`AppBarreBas`).
- Contenu centré, largeur maximale 1080 px, marges d'au moins 16 px sur les côtés.
- Fil d'Ariane en haut des pages profondes. Ex. « Accueil › Électricien › Pessac › Karim Benali ».
- Écrans d'administration : même en-tête ; l'entrée « Administration » est dans la liste du compte (sous le prénom), visible seulement des administrateurs.

## Formats d'écran
Ordinateur, tablette, téléphone debout, téléphone couché. Sous 768 px : menu burger (☰). Un tableau trop large défile sur le côté au lieu d'écraser ses colonnes. Zones cliquables d'au moins 42 px de haut.

## Listes et tableaux
- Clic sur une ligne ou une carte = ouvre la fiche.
- Tri par défaut indiqué dans le `RM-<ECRAN>-IHM.md` de chaque écran (ex. résultats de recherche : métier principal d'abord, puis mieux notés).
- Au-delà de 30 lignes : filtres et pagination.
- Liste vide : une phrase qui dit quoi faire. Ex. « Aucun rendez-vous pour l'instant. Trouvez un prestataire → ».

## Fenêtres
Jamais de fenêtre du navigateur (alert/confirm) : toujours la fenêtre de confirmation de rafals. La touche Échap la ferme.
Un pied de fenêtre à boutons de navigation (« Suivant ») garde la même hauteur à chaque étape.
Après une action réussie : un message court en bas de l'écran pendant 3 secondes. Ex. « Rendez-vous confirmé · mardi 14/10 à 10 h 00 ».

## Champs
Étiquette au-dessus. Obligatoire = astérisque, décidé par la base de données. Le curseur se place dans le premier champ d'une ligne ajoutée. Recherche de métier : propositions dès la 1re lettre, sans tenir compte des accents.

## Boutons
Une action = un bouton, jamais un lien souligné. Actions fréquentes à gauche, rares (annuler, supprimer) à droite. Le texte du bouton dit exactement ce qui va se passer (« Réserver mardi 14/10 à 10 h 00 », pas « Valider »).

## Composants communs
Un seul composant par élément répété (dossier `frontend/src/components/ui/`). Liste de départ :
- `AppBouton` — 5 variantes : principal, secondaire, danger, verrouillé (avec cadenas et bulle), accent (orange, sur le bandeau foncé de l'accueil).
- `AppChamp` — étiquette au-dessus, astérisque si obligatoire, message d'erreur dessous.
- `AppFenetre` — fenêtre de confirmation de rafals.
- `AppBadge` — étiquette d'état (OK, en attente, erreur, neutre).
- `AppCarteResultat` — carte d'un prestataire dans les résultats.
- `AppMessage` — message court après une action.
- `AppCarte` — carte centrée des formulaires courts (lot 1.2).
- `AppAlerte` — bandeau d'erreur ou d'information posé là où l'on regarde (lot 1.2).
- `AppSeparateur` — trait avec un petit texte au milieu (lot 1.2).
- `AppChampFichier` — zone « Choisir un fichier » (lot 1.4).
- `AppSelection` — liste déroulante (lot 2.2).
- `AppRecherche` — champ de recherche avec propositions (un seul pour toutes les recherches), `AppElementChoisi` — élément choisi, `AppZoneTexte` — texte long avec compteur (lot 2.5).
- `AppChoixCommune` (dans `components/`) — choix d'une commune (lot 2.5).
- `AppSection` — bloc d'une page avec titre et bouton facultatif à droite ; `danger` = bord rouge (lot 2.7).
- `ChampsAdresse` (dans `components/`) — les 3 champs d'une adresse (rue, ville, code postal seulement si la ville en a plusieurs) ; utilisé par `CarteAdresse` et par le dossier de création d'auto-entreprise (lot 7.2).
- `CarteAdresse` (dans `components/`) — carte d'une adresse unique (ajouter, modifier, effacer) : adresse du client, local du prestataire (lot 3.2).
- `AppChoix` — une réponse parmi quelques-unes, en cases côte à côte, case verrouillée 🔒 possible ; `AppCase` — case à cocher, verrouillable (lot 3.2).
- `AppOnglets` — onglets d'une page, l'onglet choisi est dans l'adresse (`?onglet=…`) : Administration, Mon agenda (lot 3.4).
- `AppSegment` — cases collées pour basculer entre deux ou trois vues, effet immédiat (« 1 mois | 2 mois », « Plombier | Électricien ») ; `AppFenetre` a une variante `large` (640 px) et `GardePrestataire` une variante `large` (1080 px) (refonte du calendrier, 03/10/2026). Les 3 boutons à deux états du calendrier (« Fermeture exceptionnelle »…) sont propres à `OngletCalendrier`.
- `AppPages` — numéros de page sous une longue liste : [‹ Précédente] [1] [2] [Suivante ›], la page en cours en bouton principal ; rien s'il n'y a qu'une page (résultats de recherche, [Voir tout] d'une rubrique ; 07/10/2026).
- Heures, jours et périodes de l'agenda : toujours par `frontend/src/outils/agenda.ts` (« 9 h 00 », « Du 20/10/2026 au 24/10/2026 ») (lot 3.4).
- `AvatarPrestataire` (dans `components/prestataire/`) — photo ronde ou initiales d'un prestataire ; `CarteResultat` (dans `components/recherche/`) — carte d'un prestataire dans les résultats (remplace l'`AppCarteResultat` prévu) ; textes de la recherche : `frontend/src/outils/recherche.ts` (lot 4.2).
- Rendez-vous (dans `components/rendez-vous/`) : `ChoixHoraire` (14 jours + heures libres, pour réserver et déplacer), `FenetreReservation`, `LigneRendezVous` ; textes et états : `frontend/src/outils/rendez_vous.ts` ; une fenêtre trop haute défile (`AppFenetre`) (lot 4.4).
- `FenetreTexte` (dans `components/`) — fenêtre à un seul texte : contester une absence, répondre à un avis, le signaler, le cacher ; `AvisAffiche` et `FenetreAvis` (dans `components/avis/`) ; types et étoiles : `frontend/src/outils/avis.ts` (lot 4.8).
- Paiements par carte : types, sommes (« 46,50 € », toujours avec les centimes) et textes par `frontend/src/outils/paiements.ts` ; `AppAlerte` a un état « neutre » pour une simple explication (ex. ce qui se passe si l'on paie par carte) (lot 5.2).
- Devis (dans `components/devis/`) : `TableauDevis` (le même tableau pour le client et le prestataire), `FenetreDemandeDevis`, `FenetreEcrireDevis`, `FenetreAccepterDevis` ; types, états et quantités : `frontend/src/outils/devis.ts` ; `FenetreTexte` accepte un texte facultatif (motif d'un refus) (lot 5.4).
- Factures : `TableauFactures` (dans `components/factures/`), `FenetrePayeDirect` (dans `components/`, commune aux rendez-vous en espèces et aux devis en direct) ; types, moyens de paiement et ouverture du PDF : `frontend/src/outils/factures.ts` (lot 5.6).
- `AppChiffre` — un chiffre mis en avant (titre, grande valeur, détail) : Mon agenda › Paiements, tableau de bord de l'administration (lot 6.2).
- `BoutonSignaler` (dans `components/`) — [Signaler cette annonce…] / [Signaler ce prestataire…], avec la connexion si besoin et la fenêtre du motif (lot 6.4).
- Demandes (dans `components/demandes/`) : `CarteDemande` (la même carte sur l'accueil, « Mes demandes » et « Demandes près de chez moi », avec [Répondre]), `CartePublierDemande` ; types et textes : `frontend/src/outils/demandes.ts` (lots 8.3 et 8.4).
- Messagerie (dans `components/messagerie/`) : `CarteProposition` (accepter, négocier, refuser, retirer), `FenetreProposition` ; types, durées et textes : `frontend/src/outils/messagerie.ts` ; compteur rouge de « Messages » : `composables/useNonLus.ts` (lots 8.2 et 8.4).
- Style « chaleureux » (07/10/2026) : une carte s'écrit avec la classe `carte` ; `AppPicto` — pictogramme d'un dossier de métiers (tracés et teintes : `frontend/src/outils/pictos.ts`) ; initiales d'un nom dans un rond : `frontend/src/outils/noms.ts` (`AvatarPrestataire`, `CarteDemande`) ; `AvatarPrestataire` a une taille « moyenne » (92 px) pour les petites cartes de résultat. Détail des formes : `CHARTE-VISUELLE.md` § « Formes ».
- `GardePrestataire` (dans `components/prestataire/`) — pages réservées aux prestataires (lot 3.2).
- Prix, durées, lieux et paiements des annonces : toujours par `frontend/src/outils/annonces.ts` (« 50 € · 2 h », « 40 €/h · de 1 h à 3 h ») (lot 3.2).
- Libellés et couleurs des états du prestataire : `frontend/src/outils/prestataires.ts`.
- `AppChoixMetier` (dans `components/`) — choix d'un métier par recherche ou par dossier, avec « Proposer un métier » (lot 2.2).
- Écrans d'administration : un fichier par onglet dans `components/admin/`.
- Dates : toujours par `frontend/src/outils/dates.ts` (« 28/09/2026 à 18 h 40 », heure de Paris ; âge).
- Appels au serveur : toujours par `frontend/src/api.ts` (messages d'erreur du serveur montrés tels quels).
