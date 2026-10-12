# Application à installer — Interface

> Fichiers : `frontend/public/manifest.webmanifest` (nom, icônes, couleurs), `frontend/public/sw.js` (page sans réseau), `frontend/public/hors-ligne.html`, `frontend/public/icone-*.png`, `frontend/index.html`, `frontend/src/main.ts`, `frontend/src/composables/useInstallation.ts`, bouton dans `frontend/src/components/AppEntete.vue`. Construit le 12/10/2026 (lot 8.7, première partie). Règles : `RM-APPLICATION.md`.

## Le bouton [Installer rafals]
Dans la liste du compte (sous le prénom), juste au-dessus de [Se déconnecter] ; bouton secondaire sur toute la largeur.
- **Android, ordinateur (Chrome, Edge)** : il n'apparaît que si le navigateur sait installer le site. Un clic ouvre la fenêtre d'installation du navigateur ; acceptée → message « rafals est installé sur cet appareil. » et le bouton disparaît.
- **iPhone, iPad** : un clic ouvre la fenêtre « Installer rafals sur votre iPhone », avec les trois gestes numérotés : 1. le bouton **Partager** de Safari ; 2. **« Sur l'écran d'accueil »** ; 3. **Ajouter**. Bouton [J'ai compris].
- **Déjà installée** (rafals ouvert comme une application), ou navigateur qui ne sait pas installer : pas de bouton.
- Pas connecté : pas de bouton (il est dans le menu du compte).

## L'application installée
- Icône : carré vert aux coins ronds, « r » blanc et point orange du logo. Nom : « rafals ».
- Elle ouvre l'accueil en plein écran, sans barre d'adresse ; la barre du téléphone est verte.

## Sans réseau
Quand une page ne peut pas être chargée, la page « Pas de connexion » s'affiche : logo « rafals. », titre « Pas de connexion : rafals a besoin d'Internet. », « Vérifiez le Wi-Fi ou les données mobiles de votre appareil, puis réessayez. », bouton [Réessayer] (recharge la page). Rien d'autre n'est gardé sur l'appareil.

## Pas encore fait
- Les notifications sur l'appareil (accord par appareil, envoi à chaque événement de `RM-ALERTES.md`) : il faut une paire de clés à créer et une bibliothèque d'envoi à installer dans le serveur.
- Les gestes en image pour l'iPhone (ils sont écrits en texte).
- À vérifier par Raphael sur un vrai téléphone : l'installation ne marche que sur un site en « https » (ou sur `localhost`).
