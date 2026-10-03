# Règle métier — Agenda et disponibilités (sujet 06)

> Validé et formalisé le 29/09/2026 (lot 3.0). Modifié le 03/10/2026 (refonte du calendrier : un calendrier par métier, ouvertures exceptionnelles).

## Objectif
Quand un prestataire travaille, et donc quels horaires un client peut réserver.

## Déjà décidé
- **Un calendrier par métier** (décidé par Raphael le 03/10/2026 ; remplace « un seul agenda par prestataire » du 29/09/2026). Réponse de Raphael, mot pour mot : « y'aura un agenda par metier […] si le prestataire a plusieurs métiers il a le nombre de calendriers correspondant au metiers ». Chaque métier a sa semaine type, ses fermetures, ses ouvertures et sa date d'arrêt ; les réglages (pas, pause, délais, confirmation) restent les mêmes pour tous les métiers.
  - Exemple 1 : Léa coiffe du mardi au samedi et maquille le samedi après-midi et le dimanche : 2 calendriers.
  - Exemple 2 : Karim (un seul métier, plombier) a un seul calendrier, sans choix à l'écran.
- Chaque annonce à prix fixe ou à l'heure a une **durée** qui bloque l'agenda ; « sur devis » n'utilise pas l'agenda (`RM-ANNONCES.md`).
- **Arrêter un métier** se fait par une **date d'arrêt** dans son calendrier (`RM-ANNONCES.md`) : bouton [Date d'arrêt], un seul jour (le dernier jour de travail) ; tous les jours d'après sont fermés dans ce calendrier (décidé le 03/10/2026 ; ce bouton n'est plus dans « Mon activité »).

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

À l'écran, un blocage s'appelle une **fermeture exceptionnelle** (03/10/2026). Elle ne ferme que le calendrier du métier où elle est posée ; seuls les rendez-vous de ce métier sont concernés par le choix « annuler ou garder ».

## Ouverture exceptionnelle (décidé le 03/10/2026)
Dans le calendrier d'un métier, le prestataire ouvre une période en plus de sa semaine type ; ces heures deviennent réservables.
- Exemple 1 : Léa, fermée le dimanche, ouvre le dimanche 18/10 de 10 h à 13 h (mariage).
- Exemple 2 : Karim, fermé le samedi, ouvre le samedi 07/11 de 8 h à 18 h.
- **Sur plusieurs jours, l'ouverture vaut sans arrêt du début à la fin** (choix B de Raphael, 03/10/2026). Ex. « du 01/11 à 9 h jusqu'au 30/11 à 18 h » : un client peut réserver le 15/11 à 3 h du matin.
- **Une fermeture passe avant une ouverture, et la coupe** (Raphael : « si une ouverture est sur 1 mois par exemple et que une fermeture est en plein milieux ca doit faire 2 ouvertures différentes »). Ex. ouverture 10 h-13 h, fermeture 11 h-12 h → deux ouvertures, 10 h-11 h et 12 h-13 h. Retirer ensuite la fermeture ne recolle pas les deux. Une ouverture posée par-dessus une fermeture existante est enregistrée coupée ; entièrement couverte par une fermeture, elle est refusée.
- Retirer une ouverture où des rendez-vous ont été pris : même choix « annuler ou garder » que pour une fermeture.
- Même forme qu'une fermeture : refusée si déjà passée, motif facultatif de 120 caractères jamais montré aux clients.

## Un rendez-vous dans un métier et les autres calendriers : au choix du prestataire (décidé le 03/10/2026)
Réponse de Raphael, mot pour mot : « bah le prestataire doit avoir le choix ». Réglage « Un rendez-vous dans un métier bloque mes autres calendriers » : **oui au départ** (jamais deux rendez-vous en même temps) ou non (chaque calendrier est indépendant).
- Exemple 1 (oui) : Léa a une coupe samedi de 15 h à 16 h → personne ne peut réserver un maquillage samedi à 15 h.
- Exemple 2 (non) : la même coupe ne retire rien au calendrier Maquilleuse : un maquillage à 15 h reste réservable.
- Les jours de travaux d'un devis accepté comptent comme un rendez-vous : avec « oui », ils ferment aussi les autres calendriers.
- La pause après chaque rendez-vous s'applique de la même façon.

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

## Précisions prises au lot 3.3 (proposées par Claude, validées par Raphael le 30/09/2026)
- **Semaine type** : enregistrée en entier d'un coup ; deux plages qui se chevauchent le même jour sont refusées (ex. mardi 9 h-12 h et 11 h-13 h) ; une plage doit finir après son début.
- **Bornes des réglages** : pause de 0 à 3 h ; « au plus tôt » de 0 à 7 jours ; « au plus tard » de 1 à 12 mois (modifiables sans toucher au code).
- **Blocage** : refusé s'il est déjà entièrement passé ; motif facultatif de 120 caractères au plus, jamais montré aux clients. Des congés « du 04/08 au 24/08 inclus » vont du 04/08 0 h au 25/08 0 h. Plusieurs blocages peuvent se chevaucher.
- **Prix à l'heure** : tant que le client n'a pas choisi, les horaires sont calculés pour le nombre d'heures minimum.
- **Pas d'horaire** : prestataire en pause, bloqué ou arrêté ; annonce pas en ligne ; métier arrêté ce jour-là ; annonce « sur devis ».
- Le choix « annuler ou garder les rendez-vous déjà pris » (blocage, changement d'horaires) sera branché au niveau 4, avec les rendez-vous.

## Précisions prises à la refonte du 03/10/2026 (proposées par Claude, à relire par Raphael)
- **Sans métier précisé**, une demande au serveur vise le calendrier du métier principal.
- **Un métier hors du profil** : son calendrier n'existe pas (refus).
- **Jours de travaux d'un devis accepté** : fermeture posée dans le calendrier du métier de l'annonce du devis.
- **Semaine type et ouverture collées** (ex. 9 h-12 h puis ouverture 12 h-14 h) : une seule période, un service peut passer de l'une à l'autre.
- **Date d'arrêt** : les rendez-vous de ce métier pris après la date sont annulés d'office, clients prévenus (règle de `RM-ANNONCES.md`, inchangée : pas de choix « garder »).

## Qui peut faire quoi
| Action | Qui | Condition |
|---|---|---|
| Remplir la semaine type d'un métier, poser ou retirer une fermeture ou une ouverture exceptionnelle, mettre une date d'arrêt, régler le pas, la pause, les délais et le blocage entre métiers | Le prestataire | Ses propres calendriers seulement |
| Voir les horaires libres | Tout le monde, même sans compte | Annonce en ligne |
| Voir les rendez-vous pris (nom du client, adresse) | Le prestataire | Ses rendez-vous seulement (`RM-CLIENTS.md`) |

## Valeurs par défaut (réglages, modifiables sans toucher au code)
Pas entre deux heures de début : 15 min · pause entre deux rendez-vous : 0 min · au plus tôt : 2 h avant · au plus tard : 2 mois à l'avance · un rendez-vous dans un métier bloque les autres calendriers : oui.

## Questions ouvertes
- (aucune)

## Références
- `GLOSSAIRE-METIER.md`, `RM-ANNONCES.md`, `RM-PRESTATAIRES.md`
