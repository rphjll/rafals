# rafals — Hébergement

> Phase 5 du démarrage (27/09/2026). Rien n'est acheté à ce stade : l'hébergeur sert à la mise en ligne, bien après les premiers lots.

## Type de projet
**Application** (comptes, données enregistrées, paiements, règles de calcul) : il faut des écrans, un serveur qui tourne en permanence et une base de données qui garde ses données. Un hébergement de simple site vitrine (Netlify, comme pour vitrine-express) ne suffit pas.

## Besoins propres à rafals
- Docker sans restriction, PostgreSQL qui garde ses données.
- Serveurs en France ou dans l'Union européenne (données personnelles).
- Stockage de fichiers compatible S3 (photos des annonces et des sites vitrines, factures PDF).
- Sous-domaines illimités pour les sites vitrines (`julie-menage.rafals.fr`) : il faut pouvoir régler le nom de domaine pour que **toutes** les adresses `*.rafals.fr` arrivent sur le serveur.

## Nom de domaine (vérifié le 27/09/2026)
- `rafals.fr` : **semble libre** (aucune fiche au registre français AFNIC). Environ 7 à 12 € par an. Raphael choisit de le réserver **plus tard**, avant la mise en ligne (27/09/2026). Risque accepté : s'il est pris entre-temps, il faudra un autre nom.
- `rafals.com` : **déjà pris**.

## Hébergeurs comparés (prix relevés le 27/09/2026, hors taxes, à revérifier au moment d'acheter)
| Hébergeur | Pays des serveurs | Plus petite offre | Remarque |
|---|---|---|---|
| OVHcloud (VPS-1) | France | environ 7,79 € / mois | Hausse de prix en avril 2026. Choix de Teorem. Support en français. |
| Hetzner (CX23) | Allemagne, Finlande | environ 5 à 6 € / mois | Hausses en avril et juin 2026 ; petites offres souvent en rupture de stock. |

Sources : [Next, hausse des VPS OVHcloud 2026](https://next.ink/225720/ovhcloud-augmente-fortement-le-prix-de-ses-vps-2026-et-ipv4/), [Northflank, hausses Hetzner 2026](https://northflank.com/blog/hetzner-cloud-server-price-increases), [Hetzner, ajustement de prix du 15/06/2026](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/).

## Décision
**OVHcloud** (Raphael, 27/09/2026 : « pour l'instant on vas partir sur ovh »), avec la possibilité d'en changer.

## Pouvoir changer d'hébergeur (règle de portabilité)
rafals n'utilise que des briques standards, acceptées par tous les hébergeurs : Docker, PostgreSQL, stockage de fichiers S3. Changer d'hébergeur = louer un autre serveur, y copier les données et les fichiers, faire pointer `rafals.fr` vers la nouvelle adresse. Aucun code à réécrire.
Interdit donc : tout service propre à OVH (base de données « maison », outils OVH dans le code).

## Remarque : antivirus du PC de développement (29/09/2026)
L'antivirus Avast du PC de Raphael intercepte les connexions HTTPS (« bouclier web ») : depuis Docker, rafals refuse ces connexions (certificat « Avast Web/Mail Shield Root » inconnu). Conséquence locale : la vérification du SIRET auprès de l'État reste « à vérifier ». Décision de Raphael : ne rien changer. Sur le serveur OVH, pas d'antivirus au milieu : rien à faire.

## IA de modération des avis (lot 4.8, 02/10/2026)
Conteneur `moderation` : IA libre Detoxify (licence Apache 2.0, gratuite pour toujours), sur le processeur, sans carte graphique. Les avis ne quittent jamais rafals.
- **Taille** : image de 3,9 Go (bibliothèque d'IA + modèle de 1 Go), téléchargée une fois à la construction ; au démarrage, l'IA met environ 1 minute à se charger (pendant ce temps, seule la liste des mots filtre).
- **Mémoire** : prévoir environ 1,5 Go de mémoire vive en plus sur le serveur OVH (un avis est lu en moins d'une seconde).
- **Sur le PC** : la construction a demandé de couper un moment l'analyse HTTPS d'Avast (même cause que pour le SIRET), choix de Raphael le 02/10/2026.
- Si l'IA est arrêtée ou trop lente (10 s), les avis passent avec la seule liste des mots interdits (rien n'est bloqué).

## Paiement par carte : Stripe (lot 5.1, 02/10/2026)
Service extérieur choisi par Raphael (Stripe Connect, « Stripe gère la tarification ») ; rien de propre à OVH, la portabilité est gardée.
- **Clés** : `STRIPE_CLE_SECRETE` et `STRIPE_SECRET_WEBHOOK` dans le fichier `.env` (jamais dans git). Sur le PC : les clés du **mode test** de Stripe (cartes d'essai, aucun argent réel).
- **Messages de Stripe** (« webhook ») : Stripe appelle `https://<site>/api/stripe/evenements`, qui vérifie la signature. Sur le PC, Stripe ne peut pas joindre `localhost` : on utilise l'outil « Stripe CLI » (`stripe listen --forward-to localhost:8001/api/stripe/evenements`), à installer au moment de l'essai à la main.
- **Pas de bibliothèque Stripe** dans le serveur : quelques appels web suffisent, donc aucune reconstruction du conteneur `backend`.

## Identité de rafals sur ses factures (lot 5.5, 03/10/2026)
`RAFALS_NOM`, `RAFALS_SIRET`, `RAFALS_ADRESSE` dans le fichier `.env` : à remplir quand rafals sera une entreprise. Vides : les factures de commission (R-…) ne sont pas créées. Les PDF sont fabriqués par le serveur lui-même (aucune bibliothèque ajoutée, aucune reconstruction du conteneur).

## Guichet unique de l'État (API de l'INPI, lot 7.1, 04/10/2026)
- **Sur le PC, rien à régler** : sans identifiants, rafals est en « démonstration » (rien n'est envoyé à l'État, faux SIRET jamais recopié dans un profil).
- **À la mise en ligne** (à la charge de Raphael) : créer le compte e-procedures de l'INPI au nom de l'entreprise rafals, accepter ses conditions d'utilisation, puis ajouter dans `.env` (jamais dans git) : `INPI_IDENTIFIANT`, `INPI_MOT_DE_PASSE`, et `INPI_ADRESSE=https://guichet-unique.inpi.fr`. Sans `INPI_ADRESSE`, c'est l'espace d'essai de l'INPI (`https://guichet-unique-demo.inpi.fr`) qui est utilisé.
- **Avant d'ouvrir au public** : faire un dossier complet dans l'espace d'essai de l'INPI (le contenu envoyé suit leur dictionnaire de données mais n'a encore jamais été envoyé pour de vrai) ; faire relire par un professionnel les listes de métiers réglementés et renvoyés (`backend/app/reglages.py`, `CREATION_*`), les frais, et la conservation des données sensibles (RGPD).
- Fichiers concernés : `backend/app/config.py` (3 réglages lus dans `.env`), `backend/app/services/guichet.py`. `docker-compose.yml` et `.env` ne changent pas aujourd'hui.

## URSSAF, « API Tierce Déclaration auto-entrepreneur » (lot 7.3, 04/10/2026)
- **Sur le PC, rien à régler** : sans identifiants, rafals est en « démonstration » (rien n'est envoyé à l'URSSAF, les cotisations sont estimées par rafals avec les taux de `reglages.py`).
- **À la mise en ligne** (à la charge de Raphael) : demander l'accès à l'URSSAF (portailapi.urssaf.fr, contact-api@urssaf.fr ; il faut très probablement que rafals soit une entreprise), obtenir la documentation technique, puis ajouter dans `.env` (jamais dans git) : `URSSAF_IDENTIFIANT`, `URSSAF_SECRET`, et si besoin `URSSAF_ADRESSE` et `URSSAF_ADRESSE_JETON`.
- ⚠️ **Un fichier à adapter ce jour-là : `backend/app/services/urssaf.py`.** Les adresses et les noms de champs y sont provisoires (la documentation n'est pas publique). Le reste de rafals n'appelle que ses 4 fonctions : `enregistrer_mandat`, `annuler_mandat`, `estimer`, `declarer`.
- `docker-compose.yml` et `.env` ne changent pas aujourd'hui.
