# Règle métier — Agenda et disponibilités (sujet 06)

> Validé et formalisé le 29/09/2026 (lot 3.0).

## Objectif
Quand un prestataire travaille, et donc quels horaires un client peut réserver.

## Déjà décidé
- **Un seul agenda par prestataire**, même pour une société (`GLOSSAIRE-METIER.md`).
- Chaque annonce à prix fixe ou à l'heure a une **durée** qui bloque l'agenda ; « sur devis » n'utilise pas l'agenda (`RM-ANNONCES.md`).
- **Arrêter un métier** se fait par une date de fin dans le calendrier (`RM-ANNONCES.md`).

## Une semaine type (décidé le 29/09/2026)
Le prestataire remplit une fois ses horaires pour chaque jour de la semaine, avec plusieurs plages possibles par jour ; ils se répètent chaque semaine.
- Exemple 1 : Léa — mardi à vendredi 9 h-12 h et 14 h-19 h ; samedi 9 h-12 h ; dimanche et lundi fermé.
- Exemple 2 : Karim — lundi à vendredi 8 h-18 h, sans coupure.
Les exceptions (congés…) se gèrent à part (voir plus bas).
**Pourquoi :** rapide à remplir pour quelqu'un qui a toujours les mêmes horaires.

## Congés et absences : bloquer des dates (décidé le 29/09/2026)
Dans son calendrier, le prestataire bloque une période (plusieurs jours, ou quelques heures) ; ces horaires ne sont plus réservables.
- Exemple 1 : Léa bloque « du 04/08 au 24/08 » (congés).
- Exemple 2 : Karim bloque « mardi 14/10 de 14 h à 16 h » (dentiste).
- **Rendez-vous déjà pris pendant la période : le prestataire choisit** (décidé le 29/09/2026). rafals affiche d'abord la liste (ex. « 1 rendez-vous pendant cette période : Mme Dupont, 12/08 à 10 h »), puis :
  - [Annuler ces rendez-vous et bloquer] → chaque client est prévenu par mail, et remboursé s'il a payé en ligne ;
  - [Bloquer autour] → les rendez-vous restent, tout le reste de la période est bloqué.

## Heures de début proposées : pas choisi par le prestataire (décidé le 29/09/2026)
Le prestataire choisit l'écart entre deux heures de début proposées : 15 min, 30 min ou 1 h (15 min au départ, tant qu'il n'a rien choisi). Un horaire n'est proposé que si le service finit avant la fin de la plage.
- Exemple 1 : Léa, pas de 15 min, ouverte 9 h-12 h, coupe de 45 min → 9 h 00, 9 h 15, 9 h 30… 11 h 15.
- Exemple 2 : Léa passe à 30 min → 9 h 00, 9 h 30, 10 h 00, 10 h 30, 11 h 00.

## Pause entre deux rendez-vous : choisie par le prestataire (décidé le 29/09/2026)
Le prestataire règle un temps de pause après chaque rendez-vous (0 min au départ), pendant lequel rien n'est réservable.
- Exemple 1 : Julie règle 30 min. Elle finit chez Mme Dupont à 11 h → le prochain horaire proposé est 11 h 30 (trajet vers Rezé).
- Exemple 2 : Léa, au salon, garde 0 min → les coupes s'enchaînent.

## Délais de réservation : choisis par le prestataire (décidé le 29/09/2026)
Le prestataire règle « au plus tôt X avant » et « au plus tard Y à l'avance » (au départ : 2 h et 2 mois).
- Exemple 1 : lundi 13/10 à 8 h, Léa (2 h / 2 mois) → Mme Dupont peut réserver à partir de 10 h aujourd'hui, et jusqu'au 13/12.
- Exemple 2 : Karim, dépannage, règle « au plus tôt 1 h avant » → une fuite à 8 h peut être réservée pour 9 h.

## Changer sa semaine type : comme pour les congés (décidé le 29/09/2026)
Si des rendez-vous déjà pris tombent en dehors des nouveaux horaires, rafals les liste d'abord ; le prestataire choisit [Annuler ces rendez-vous] (clients prévenus par mail, remboursés s'ils ont payé en ligne) ou [Les garder] (les nouveaux horaires valent seulement pour les nouvelles réservations).
- Exemple : Léa ne travaille plus le samedi ; M. Petit a réservé samedi 18/10 à 10 h → « 1 rendez-vous en dehors de vos nouveaux horaires : M. Petit, samedi 18/10 à 10 h ».

## Toute annulation par le prestataire : client prévenu et remboursé
Qu'elle vienne d'un blocage, d'un changement d'horaires ou de la date de fin d'un métier (`RM-ANNONCES.md`), chaque rendez-vous annulé par le prestataire est signalé au client par mail, et remboursé en entier s'il avait payé en ligne (détail avec les sujets 08 Rendez-vous et 12 Paiements).

## Ce que voit le client
Seulement les horaires libres, jamais les autres rendez-vous ni le nom des autres clients, ni la raison d'un blocage (appliqué d'office : règle des données personnelles, `RM-CLIENTS.md`).
- Exemple : Mme Dupont voit « mardi 14/10 : 9 h 00, 9 h 15, 11 h 00… » ; elle ne sait pas que 9 h 30-10 h 45 est pris par M. Petit.

## Qui peut faire quoi
| Action | Qui | Condition |
|---|---|---|
| Remplir sa semaine type, bloquer des dates, régler le pas, la pause et les délais | Le prestataire | Son propre agenda seulement |
| Voir les horaires libres | Tout le monde, même sans compte | Annonce en ligne |
| Voir les rendez-vous pris (nom du client, adresse) | Le prestataire | Ses rendez-vous seulement (`RM-CLIENTS.md`) |

## Valeurs par défaut (réglages, modifiables sans toucher au code)
Pas entre deux heures de début : 15 min · pause entre deux rendez-vous : 0 min · au plus tôt : 2 h avant · au plus tard : 2 mois à l'avance.

## Questions ouvertes
- (aucune)

## Références
- `GLOSSAIRE-METIER.md`, `RM-ANNONCES.md`, `RM-PRESTATAIRES.md`
