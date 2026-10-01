# Mon agenda — Interface

> Fichiers : `frontend/src/pages/AgendaPage.vue` (onglets, chargement), un fichier par onglet dans `frontend/src/components/agenda/` (`OngletCalendrier`, `OngletSemaine`, `OngletReglages`, `OngletHoraires`), `frontend/src/outils/agenda.ts` (heures, jours, périodes), composant commun `AppOnglets`. Construit au lot 3.4 (30/09/2026). Règles : `RM-AGENDA.md`, `RM-ANNONCES.md` (dates de fin de métier). Maquette : `maquette-lot-3.4-agenda.html`.

## Accès
Menu « Mon agenda » (`/mon-agenda`), seulement pour un prestataire (même gardien que « Mes annonces » : se connecter / proposer ses services). Contenu centré, 720 px au plus. Titre « Mon agenda », puis 5 onglets : Calendrier, Rendez-vous (lot 4.4, voir `RM-RENDEZ-VOUS-IHM.md`, compteur orange des demandes), Semaine type, Réglages, Horaires libres ; l'onglet choisi est dans l'adresse (`?onglet=rendez-vous`, `semaine`, `reglages`, `horaires` ; rien = Calendrier).

## Onglet « Calendrier »
1. Carte du mois : [‹ septembre] « octobre 2026 » [novembre ›] ; grille lun → dim ; chaque jour : numéro + « 9-12 · 14-19 » (sur ordinateur) ; couleurs : vert = ouvert (semaine type), gris = fermé, hachuré orange + « bloqué » = période bloquée ; « 2 rdv » en vert foncé les jours qui ont des rendez-vous (confirmés ou demandés, lot 4.4) ; « fin Plombier » en rouge le dernier jour d'un métier ; jours passés pâlis ; le jour choisi est entouré (aujourd'hui au départ). Légende dessous.
2. Carte du jour choisi, ex. « mardi 13 octobre » + badge (ouvert vert / fermé gris / bloqué orange) : « 9 h 00 – 12 h 00 · 14 h 00 – 19 h 00 (semaine type) », ou la période bloquée et son motif, ou « Fermé ce jour-là (semaine type). » ; la liste des rendez-vous du jour (« **10 h 00 – 10 h 45** · Coupe femme · Marie Dupont », « (demande en attente) ») ; « Dernier jour du métier Plombier. » si c'est le cas. Boutons (jour pas passé) : [Bloquer ce jour] et [Bloquer quelques heures…] ; si bloqué : [Débloquer cette période] (danger).
3. Carte « Périodes bloquées à venir » + [Bloquer une période…] (principal) : une ligne par période (« Du 20/10/2026 au 24/10/2026 · Congés », « 03/11/2026, de 14 h 00 à 16 h 00 ») avec [Débloquer] (danger) → « Période débloquée : ces horaires sont de nouveau réservables. » ; vide : « Aucune période bloquée. » ; « Le motif n'est jamais montré aux clients : ils voient seulement moins d'horaires. »
4. Carte « Dates de fin de métier » (s'il y en a) : « **Plombier** : dernier jour le 15/10/2026. » + lien vers « Mon activité › Mes métiers », où elles se règlent.

**Fenêtre « Bloquer une période »** : case « Seulement quelques heures » ; décochée : « Du * » et « Au (inclus) * » (dates, pas avant aujourd'hui) ; cochée : « Le * », « De * », « À * » ; « Motif (pour vous seul) » (120 caractères) ; « Les clients ne verront plus d'horaires pendant cette période. (Rendez-vous déjà pris : …quand les rendez-vous existeront.) » ; erreur du serveur dans la fenêtre (ex. « Cette période est déjà passée. », « La fin doit être après le début. ») ; [Bloquer] → « Période bloquée : du 20/10/2026 au 24/10/2026. » ; [Annuler].

## Onglet « Semaine type »
« Vos horaires de chaque semaine, heure de Paris. Plusieurs plages possibles par jour (ex. une pause déjeuner). Un jour sans plage est fermé. » Puis lundi → dimanche : « Fermé », ou une ligne par plage (champs « De * » et « À * » en heures, bouton rond × pour la retirer) ; [+ Ajouter une plage] (9 h-12 h, ou 14 h-19 h après une plage du matin). Erreur du serveur en bandeau rouge (ex. « Deux plages se chevauchent le mardi : 9 h 00-12 h 00 et 11 h 00-13 h 00. ») ; [Enregistrer la semaine] → « Semaine type enregistrée. » ; [Annuler] remet la semaine enregistrée. Note : rendez-vous déjà pris hors des nouveaux horaires, choix « annuler ou garder » au niveau 4.

## Onglet « Réglages »
**Carte « Réservations »** (lot 4.4) : « Quand un client réserve * » [Confirmé aussitôt — l'horaire libre est pris | J'accepte chaque demande — 24 h pour répondre] ; « Annulation gratuite par le client jusqu'à * » (2, 12, 24 ou 48 h avant) ; [Enregistrer] → « Réglages des réservations enregistrés. »
**Carte « Horaires »** :
- « Heures de début proposées aux clients * » en 3 cases : toutes les 15 min / toutes les 30 min / toutes les heures ; « Ex. ouvert à 9 h, service de 45 min : 9 h 00, 9 h 15, 9 h 30… »
- « Pause après chaque rendez-vous * » : aucune, 15 min, 30 min, 45 min, 1 h, 1 h 30, 2 h, 3 h ; « Pour le trajet ou le rangement. »
- « Réservation au plus tôt * » : à tout moment, 30 min, 1 h, 2 h, 4 h, 24 h, 2 jours, 7 jours avant.
- « Réservation au plus tard * » : 1, 2, 3, 6 ou 12 mois à l'avance.
- [Enregistrer] → « Réglages enregistrés. » ; erreur en bandeau rouge.

## Onglet « Horaires libres »
« Ce que voit un client qui veut réserver (la réservation arrive au niveau 4). » Liste « Annonce » (seulement celles en ligne, à prix fixe ou à l'heure : « Coupe femme — 35 € · 45 min ») et « Jour » (aujourd'hui au départ) ; pour une annonce à l'heure, « Nombre d'heures choisi par le client ». Résultat : « Mardi 13 octobre : 10 horaires » puis des pastilles « 9 h 00 », « 9 h 15 »… ; ou « Aucun horaire libre ce jour-là (fermé, bloqué, trop tôt ou trop loin, ou métier arrêté). » Sans annonce utilisable : « Aucune annonce en ligne avec un prix fixe ou à l'heure : les annonces « sur devis » n'utilisent pas l'agenda. »
