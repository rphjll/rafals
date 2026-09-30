# Règle métier — Rendez-vous (sujet 08)

> Validé et formalisé le 30/09/2026 (lot 4.0).

## Objectif
Réserver un horaire, le confirmer, l'annuler, et ce qui se passe si quelqu'un ne vient pas.

## Déjà décidé (sujets 03, 05, 06)
- Réserver demande une **adresse mail vérifiée** (et l'accord des parents avant 18 ans) : `RM-COMPTES.md`.
- On réserve une **annonce** à prix fixe ou à l'heure, sur un **horaire libre** de l'agenda (`RM-AGENDA.md`) ; « sur devis » = demande écrite, pas de rendez-vous.
- Le **titre, le prix et la durée** sont recopiés sur le rendez-vous au moment de la réservation (`RM-ANNONCES.md`).
- « Chez le client » : l'adresse est demandée à la réservation, puis gardée (`RM-CLIENTS.md`).
- Après réservation, le client voit le **téléphone** du prestataire et la **rue du local** ; le prestataire voit ceux du client jusqu'à 3 mois après le dernier rendez-vous (`RM-CLIENTS.md`).
- Toute annulation par le prestataire (blocage, changement d'horaires, date de fin d'un métier, blocage par l'administrateur) : client prévenu par mail et **remboursé** s'il a payé en ligne (`RM-AGENDA.md`, `RM-PRESTATAIRES.md`).
- Un client ne peut pas fermer son compte avec un rendez-vous à venir (`RM-CLIENTS.md`).

## Confirmation : au choix du prestataire (décidé le 30/09/2026)
Chaque prestataire choisit dans ses réglages : **« confirmation automatique »** (l'horaire libre est réservé aussitôt) ou **« j'accepte chaque demande »** (le rendez-vous attend qu'il clique [Accepter]).
- Exemple 1 : Léa, confirmation automatique → Mme Dupont réserve mardi 14/10 à 10 h : confirmé aussitôt, mail aux deux.
- Exemple 2 : Karim accepte chaque demande → la réservation de M. Petit est « en attente » jusqu'à ce que Karim accepte.

## Demande sans réponse : annulée après 24 h (décidé le 30/09/2026)
Pendant l'attente, l'horaire est gardé pour le client. Sans réponse après 24 h, la demande est annulée, le client reçoit « Karim n'a pas répondu » et l'horaire redevient libre. Le prestataire reçoit un rappel 2 h avant la fin du délai.
- Exemple : M. Petit demande jeudi 16/10 à 9 h le lundi 13/10 à 18 h → rappel à Karim mardi 14/10 à 16 h → annulée mardi 14/10 à 18 h.
- Cas limite (proposé par Claude, validé) : si le rendez-vous commence avant la fin des 24 h, la demande est annulée à l'heure du rendez-vous.

## Annulation par le client : délai choisi par le prestataire (décidé le 30/09/2026)
Le prestataire règle « annulation gratuite jusqu'à X avant » : 2 h, 12 h, 24 h ou 48 h (24 h au départ). Avant ce délai, le client annule lui-même d'un clic ; après, le bouton [Annuler] est verrouillé 🔒 avec la raison : « Moins de 24 h avant : appelez Léa au 06 12 34 56 78. »
- Exemple : Léa (24 h), rendez-vous mardi 14/10 à 10 h → Mme Dupont peut annuler jusqu'au lundi 13/10 à 10 h.
- Remboursement d'un paiement en ligne : détail avec le sujet 12 (Paiements).

## Client absent : marqué, compté, visible (décidé le 30/09/2026)
Réponse de Raphael, mot pour mot : « la marquer absente compteur et y'aura ecrit dans son compte en vers les clients » ; précisé : visible par la cliente ET par les prestataires.
- Après l'heure du rendez-vous, le prestataire clique [Client absent] ; le client reçoit un mail.
- **Compteur** : « 2 absences sans prévenir en 6 mois » écrit dans « Mon compte » du client, et montré à chaque prestataire qui reçoit une réservation de lui.
- **3 absences en 6 mois** → le client ne peut plus réserver pendant 1 mois (réglages).
- Exemple : Mme Dupont ne vient pas chez Léa mardi 14/10 à 10 h → Léa clique [Client absent] → Mme Dupont voit « 1 absence sans prévenir en 6 mois » ; Karim, qui reçoit sa prochaine demande, voit aussi « 1 absence ».

## Prestataire absent : signalé par le client, visible de tous (décidé le 30/09/2026)
Réponse de Raphael, mot pour mot : « bah c'est le client qui le met et a ce moment la c'est ecrit dans son compte donc tout le monde pourras voir ca ».
- Après l'heure du rendez-vous, le client clique [Karim n'est pas venu] ; il est remboursé s'il avait payé en ligne (détail : sujet 12).
- **Compteur** « 2 absences sans prévenir en 6 mois » affiché sur la **page publique** du prestataire, vu de tous.
- Exemple : Karim ne vient pas chez Mme Dupont mardi 14/10 à 10 h → elle clique [Karim n'est pas venu] → la page de Karim affiche « 1 absence sans prévenir ».

## Contester une absence : l'administrateur tranche (décidé le 30/09/2026)
La personne marquée absente (client ou prestataire) peut cliquer [Je suis venu] sous 7 jours, avec une explication. Pendant ce temps, l'absence n'est ni affichée ni comptée. L'administrateur lit les deux versions et décide si l'absence compte.
- Exemple : Mme Dupont clique [Karim n'est pas venu] ; Karim répond « Je suis venu à 10 h, personne n'a ouvert, j'ai appelé 2 fois » → rien n'est affiché ; l'administrateur tranche.
- Sans contestation au bout de 7 jours, l'absence compte.

## Déplacer un rendez-vous : oui, dans le délai d'annulation (décidé le 30/09/2026)
Tant que le client peut annuler gratuitement, [Déplacer] lui montre les horaires libres ; le nouvel horaire remplace l'ancien, qui se libère. Si le prestataire accepte chaque demande, le nouvel horaire attend son accord et l'ancien est gardé jusque-là. Le prix recopié ne change pas.
- Exemple : Mme Dupont déplace mardi 14/10 10 h → jeudi 16/10 14 h (Léa, confirmation automatique) : fait aussitôt, mail aux deux.

## Annulation par le prestataire : à tout moment, avec un motif (décidé le 30/09/2026)
Le prestataire peut annuler un rendez-vous à tout moment, avec un **motif obligatoire** envoyé au client par mail ; le client est remboursé s'il avait payé en ligne. Chaque annulation à moins de 24 h est comptée et visible par l'administrateur.
- Exemple : Léa, malade, annule mardi 14/10 à 8 h le rendez-vous de 10 h : « Malade, désolée » → Mme Dupont reçoit le mail avec le motif.

## Précisions proposées par Claude (validées par Raphael le 30/09/2026)
- **États d'un rendez-vous** : en attente (demande à accepter) → confirmé → passé ; ou refusé (par le prestataire), expiré (24 h sans réponse), annulé (par le client ou le prestataire), client absent, prestataire absent. Un rendez-vous n'est jamais effacé.
- **Refuser une demande** : le prestataire qui accepte chaque demande peut aussi [Refuser], avec un motif facultatif ; l'horaire redevient libre.
- **Rappel** : mail au client et au prestataire la veille à 18 h (ou 2 h avant pour un rendez-vous pris le jour même).
- **Réserver** : le client voit le récapitulatif (titre, date, heure, durée, prix, lieu, paiement) puis clique « Réserver mardi 14/10 à 10 h 00 ». Si l'horaire vient d'être pris : « Cet horaire vient d'être pris, choisissez-en un autre. »
- **Un client ne peut pas réserver chez lui-même** (Julie prestataire ne réserve pas sa propre annonce).
- **Chevauchement côté client** : autorisé (Mme Dupont peut avoir la coiffeuse et le plombier à la même heure, chez elle) ; rafals affiche seulement un avertissement.
- **Délais et compteurs** (réglages) : 24 h de réponse ; 3 absences en 6 mois → 1 mois sans réserver ; 7 jours pour contester.

## Précisions prises au lot 4.3 (proposées par Claude, validées par Raphael le 30/09/2026)
- **Paiement** : pour l'instant, espèces seulement ; « carte » répond « Le paiement par carte sur rafals arrive bientôt » (niveau 5).
- **Demande en attente** : elle garde l'horaire ; le client peut l'annuler à tout moment ; elle expire à la fin des 24 h, ou à l'heure du rendez-vous si c'est plus tôt.
- **Déplacer** : seulement un rendez-vous confirmé, un déplacement en attente à la fois ; son propre ancien horaire ne le gêne pas (ex. 10 h 00 → 10 h 15).
- **Pause du prestataire** : autour de chaque rendez-vous, avant et après (ex. pause 30 min, rendez-vous 10 h-10 h 45 : pas de nouveau début avant 11 h 15, et un rendez-vous précédent doit finir avant 9 h 30).
- **Coordonnées** : le client voit le téléphone du prestataire (et la rue du local) une fois le rendez-vous **confirmé** ; le prestataire voit le nom, le téléphone et l'adresse du client dès la demande (pour décider), puis jusqu'à 3 mois après le dernier rendez-vous (RM-CLIENTS).
- **Annulation par le prestataire** : impossible une fois le rendez-vous terminé.
- **Tâche automatique** toutes les 5 minutes : demandes expirées, rappels.

## Qui peut faire quoi
| Action | Qui | Condition |
|---|---|---|
| Réserver | Client | Peut réserver (`RM-COMPTES.md`) ; horaire libre ; pas en « 1 mois sans réserver » |
| Accepter / refuser une demande | Prestataire | Sa demande, pas encore expirée |
| Annuler, déplacer | Client | Avant le délai d'annulation du prestataire |
| Annuler | Prestataire | À tout moment, motif obligatoire |
| Marquer « client absent » / « prestataire absent » | L'autre partie | Après l'heure du rendez-vous |
| Trancher une contestation | Administrateur | — |

## Questions ouvertes
- (aucune)

## Références
- `RM-AGENDA.md`, `RM-ANNONCES.md`, `RM-CLIENTS.md`, `RM-COMPTES.md`, `RM-PRESTATAIRES.md`
