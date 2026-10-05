# Règle métier — Application à installer (sujet 21)

> Rédigé par Claude le 04/10/2026 sur le modèle d'AlloVoisins, corrigé avec Raphael sur la maquette `maquette-niveau-8-demandes.html` (8 versions), **validé par Raphael le 04/10/2026** (« oui »). Les lignes « (choix de Claude) » sont donc validées avec le reste.

## Objectif
Avoir rafals sur l'écran d'accueil du téléphone, avec son icône, et recevoir les notifications même quand le site est fermé.

## Le site devient installable (proposé par Claude, choisi par Raphael le 04/10/2026 : « A »)
Il existe deux façons d'avoir une « application » :
- **A. Le site installable** (une *PWA*, « application web progressive » : le même site, que le téléphone sait poser sur l'écran d'accueil et ouvrir comme une application). C'est le choix de Raphael.
- **B. Deux vraies applications dans les magasins** (App Store d'Apple, Google Play), comme AlloVoisins.

| | A. Site installable | B. Applications des magasins |
|---|---|---|
| Ce que voit l'utilisateur | Bouton [Installer rafals] sur le site ; icône sur l'écran d'accueil ; s'ouvre sans barre d'adresse | Il cherche « rafals » dans l'App Store ou Google Play |
| Notifications | Oui (sur iPhone : seulement une fois l'application installée sur l'écran d'accueil, iOS 16.4 ou plus récent) | Oui |
| Coût | 0 € | Compte Apple 99 $ par an + compte Google 25 $ une fois (tarifs connus de Claude, à revérifier) |
| Travail | Le même code que le site : une seule chose à entretenir | Deux applications de plus à écrire et à entretenir |
| Mise à jour | Immédiate, comme le site | Chaque version attend l'accord d'Apple et de Google |
| Trouvable dans les magasins | Non | Oui |
- Exemple 1 : Karim ouvre rafals.fr sur son téléphone Android, touche [Installer rafals] : l'icône apparaît à côté de ses autres applications, et il reçoit les alertes de demandes.
- Exemple 2 : Mme Dupont, sur iPhone, touche « Partager » puis « Sur l'écran d'accueil » (rafals lui montre ces deux gestes en image) ; elle accepte ensuite les notifications.
**Pourquoi A d'abord :** un seul code à entretenir pour un développeur débutant, aucun abonnement, et les notifications marchent. La solution B reste possible plus tard, en emballant le même site.

## Ce que fait l'application installée (choix de Claude)
- Elle ouvre rafals en plein écran, avec l'icône et le nom « rafals ».
- Elle demande l'accord pour les notifications **au bon moment** : après la première demande publiée (client) ou à l'activation des alertes (prestataire), jamais à la première ouverture.
- Sans réseau, elle affiche « Pas de connexion : rafals a besoin d'Internet. » avec un bouton [Réessayer] ; rien n'est gardé sur le téléphone (ni messages, ni adresses).
- Le bouton [Installer rafals] est dans le menu du compte ; il disparaît une fois l'application installée.

## Notifications sur l'appareil
- Chaque appareil donne son accord séparément ; on peut le retirer dans « Alertes » ou « Mon compte » (`RM-ALERTES.md`).
- Se déconnecter sur un appareil coupe ses notifications.
- Une notification ouvre directement le bon écran (la demande, la conversation, le rendez-vous).

## Qui peut faire quoi
| Action | Qui | Condition |
|---|---|---|
| Installer rafals | Tout le monde | Téléphone ou ordinateur récent |
| Accepter ou couper les notifications d'un appareil | La personne connectée | — |

## Questions ouvertes
- (aucune)

## Références
- `RM-ALERTES.md`, `PRESENTATION.md` (« une application mobile à installer » restait possible)
