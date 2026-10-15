# Alertes — Interface

> Fichier : `frontend/src/pages/AlertesPage.vue`. Construit le 12/10/2026 (lot 8.6), d'après la maquette validée `maquette-niveau-8-demandes.html` (onglet « Alertes », réécrit en questions complètes à la demande de Raphael le 04/10/2026). Règles : `RM-ALERTES.md`.

## Où
« Mon activité » → « Alertes » (`/alertes`), réservée aux prestataires (même gardien que « Mon agenda »). Contenu centré, 720 px au plus.

## Ce qu'on voit, de haut en bas
1. Titre « Alertes : être prévenu des nouvelles demandes ».
2. Cadre **« Pour quels métiers voulez-vous être prévenu ? »** : pour chaque métier exercé,
   - la phrase « Un client cherche « Plombier » près de chez vous : » ;
   - deux cases collées [Me prévenir] | [Ne pas me prévenir] (la réponse en cours est en vert) ;
   - dessous, la conséquence : « Vous êtes prévenu de chaque demande « Plombier » dans votre rayon de 15 km autour de Pessac. » ou « Vous ne recevez rien pour « Jardinier ». Les demandes restent visibles dans « Demandes près de chez moi ». »
3. Cadre **« Comment voulez-vous être prévenu ? »** : « Par mail », trois cases côte à côte : [Un mail à chaque demande] (au départ), [Un seul mail le soir à 18 h — avec toutes les demandes du jour], [Aucun mail]. Dessous, la conséquence de la réponse en cours, par exemple « Vous recevez un seul mail à 18 h, avec toutes les demandes du jour. Ex. 15 demandes dans la journée : 1 mail au lieu de 15. », puis « Les mails qui concernent vos conversations, vos propositions et vos rendez-vous ne se coupent pas. »

**Chaque clic est enregistré tout de suite** : message vert « Alertes enregistrées. » ; un refus de la règle s'affiche en message rouge et la réponse revient à l'ancienne.

## Compteur rouge
Dans « Mon activité », la tuile « Demandes près de chez moi » porte une pastille rouge avec le nombre de demandes arrivées depuis la dernière visite de cette page ; l'ouvrir la remet à zéro. (Pas de pastille dans le sous-menu.)

## Sur ce téléphone
Entre les deux cartes, exemple « Une notification à chaque nouvelle demande de vos métiers près de chez vous, ex. « Nouvelle demande : Fuite sous l'évier, Talence (5 km) ». » La carte du mail s'appelle maintenant « Comment voulez-vous être prévenu par mail ? ».
« Sur ce téléphone » (lot 8.7, 15/10/2026, `CarteNotifications.vue`) : phrase d'exemple, puis « Le téléphone sonne même quand rafals est fermé. Jamais de nom complet, d'adresse ni le texte d'un message. » et, selon l'appareil :
- pas encore activées : [Activer les notifications sur cet appareil] → le navigateur demande « Autoriser / Bloquer » → message vert « Notifications activées sur cet appareil. » et, tout de suite, une notification d'essai « Les notifications sont activées sur cet appareil. » ;
- activées : badge vert « activées sur cet appareil » + [Couper les notifications] → « Notifications coupées sur cet appareil. » ;
- « Bloquer » choisi dans le navigateur : « Ce navigateur a bloqué les notifications de rafals. Pour les autoriser : cliquez sur le cadenas à gauche de l'adresse du site, puis « Notifications » → « Autoriser ». » ;
- navigateur qui ne sait pas (ex. iPhone sans rafals installé) : « … Sur iPhone : installez d'abord rafals (menu du compte → [Installer rafals]), puis ouvrez-le depuis son icône. » ;
- rafals pas encore branché (clés absentes de `.env` ou bibliothèque pas installée dans le serveur) : bouton verrouillé 🔒 « Les notifications ne sont pas encore branchées sur rafals : vous recevez les mails en attendant. »
Un clic sur une notification ouvre le bon écran : « Demandes près de chez moi », ou la conversation (`/messages/12`).
