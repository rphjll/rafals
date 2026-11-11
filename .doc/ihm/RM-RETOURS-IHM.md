# « Un problème ? Une idée ? » — Interface

> Lot 13.1, 09/11/2026. Règle : `regles-metier/RM-RETOURS.md`. Maquette validée par Raphael le 09/11/2026 (« oui ») : `.doc/ihm/maquette-retours.html` (https://claude.ai/artifact/1gLKTsqhgr7W2DywAwHKLR). Composant : `frontend/src/components/retours/FenetreRetour.vue`, ouvert depuis `AppEntete.vue`.

## Où on la trouve
- Seulement connecté. Dans la liste du compte : sous le prénom sur ordinateur, dans le menu ☰ sur téléphone, entre « Administration » (ou « Paramètres ») et [Installer rafals] / [Se déconnecter].
- Un clic referme la liste et ouvre la fenêtre par-dessus la page où l'on est. Cette page (ex. `/demandes/nouvelle`) part avec le message.

## La fenêtre « Un problème ? Une idée ? »
1. « Vous nous écrivez pour » : 2 cases côte à côte (`AppChoix`), **[Un problème]** « quelque chose ne marche pas » (choisie au départ) et **[Une idée]** « quelque chose à ajouter ».
2. Le texte (`AppZoneTexte`, obligatoire, compteur « 0 / 2000 ») : l'étiquette et l'exemple suivent la case choisie.
   - Problème : « Que s'est-il passé ? », « Ex. Le bouton Publier ne répond pas sur mon téléphone. »
   - Idée : « Quelle est votre idée ? », « Ex. Pouvoir mettre une vidéo de mon travail sur mon profil. »
3. « Capture d'écran (facultatif) » (`AppChampFichier`) : « JPG ou PNG, 5 Mo au plus » ; une fois choisie, son nom s'affiche et [Retirer la capture] apparaît dessous.
4. Phrase en petit : « La page où vous êtes, votre appareil et votre navigateur sont joints tout seuls pour nous aider. Rien d'autre. »
5. Pied : **[Envoyer le problème]** ou **[Envoyer l'idée]** (selon la case), puis [Annuler]. Échap ou un clic sur le fond ferme aussi.
- La fenêtre est vide à chaque ouverture.

## Après un clic sur [Envoyer…]
- Réussi : la fenêtre se ferme, message vert de 3 secondes « Merci, c'est envoyé. Nous regardons chaque soir. »
- Refusé : la fenêtre reste ouverte, le message du serveur en rouge juste au-dessus des boutons, tel quel :
  - « Décrivez un peu plus (10 caractères au moins). »
  - « Vous avez déjà envoyé 5 messages aujourd'hui, merci ! Vous pourrez en envoyer d'autres demain. »
  - « Ce fichier n'est pas accepté : envoyez un JPG, PNG. » / « Le fichier est trop lourd : 5 Mo au maximum (une photo de téléphone suffit). »
- Un message injurieux n'est pas refusé à l'écran : il est envoyé, puis gardé pour l'administrateur (règle 17).

## Pas encore fait
- La notification à l'auteur quand son message est traité (règle 12) : avec la routine du soir (lot 13.2) et la page « Corrections et idées » (lot 13.3).
- Aucun écran d'administration pour ces messages dans ce lot (lot 13.3).
