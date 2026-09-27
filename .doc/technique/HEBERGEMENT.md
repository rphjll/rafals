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
- `rafals.fr` : **semble libre** (aucune fiche au registre français AFNIC). Environ 7 à 12 € par an. À réserver avant que quelqu'un d'autre le prenne.
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
