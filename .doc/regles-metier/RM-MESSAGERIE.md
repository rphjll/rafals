# Règle métier — Messagerie (sujet 19)

> Rédigé par Claude le 04/10/2026 sur le modèle d'AlloVoisins, corrigé avec Raphael sur la maquette `maquette-niveau-8-demandes.html` (8 versions), **validé par Raphael le 04/10/2026** (« oui »). Les lignes « (choix de Claude) » sont donc validées avec le reste.

## Objectif
Des messages privés entre un client et un prestataire, pour se mettre d'accord avant un rendez-vous et se parler après.
- Exemple 1 : Karim répond à la demande de M. Petit : « Bonjour, la fuite vient du siphon ou du robinet ? »
- Exemple 2 : Mme Dupont, sur la page de Léa : [Écrire à Léa] → « Faites-vous les chignons de mariage ? »

## Une conversation par couple client / prestataire (choix de Claude)
Tout ce que Mme Dupont et Karim se disent est dans une seule conversation, même s'il y a plusieurs demandes ou rendez-vous. La demande ou le rendez-vous dont on parle est rappelé par une carte dans le fil.
- Exemple : en mars, Karim répond à « Fuite sous l'évier » ; en juin, Mme Dupont lui écrit pour un chauffe-eau : même conversation, deux cartes.
**Pourquoi :** on retrouve tout de suite « mes échanges avec Karim » ; pas dix fils à moitié vides.

## Qui peut commencer une conversation (choix de Claude)
- **Le client**, avec n'importe quel prestataire visible : bouton [Écrire à Karim] sur sa page publique et sur ses annonces (annonces retirées le 04/10/2026 : sur sa page publique seulement, voir `RM-PRESTATAIRES.md` § « Sans annonces »).
- **Le prestataire**, seulement dans deux cas : il **répond à une demande** du client (`RM-DEMANDES.md`), ou ce client **a déjà un rendez-vous ou un devis avec lui**.
- Exemple refusé : Karim ne peut pas écrire à tous les clients de Pessac pour se faire de la publicité.
**Pourquoi :** aucun client ne reçoit de message qu'il n'a pas cherché.

## Ce qu'on peut envoyer
- Un **texte** de 1 à 2000 caractères ; jusqu'à **5 photos** par message.
- Le prestataire : une **proposition** (prix, jour, heure, durée, lieu, paiement), que le client accepte d'un clic (`RM-DEMANDES.md`).
- Même filtre que les avis (mots interdits + IA) : un message injurieux est refusé à l'envoi.

## Coordonnées masquées avant le premier rendez-vous (choix de Claude)
Tant que ce client et ce prestataire n'ont aucun rendez-vous ensemble, un numéro de téléphone ou une adresse mail écrit dans un message est remplacé par « (coordonnées masquées jusqu'à la réservation) ». Dès qu'un rendez-vous existe entre eux, les coordonnées s'écrivent librement, et le téléphone s'affiche comme le prévoit `RM-CLIENTS.md`.
- Exemple 1 : Tom écrit « appelez-moi au 06 12 34 56 78 » avant tout rendez-vous → Mme Dupont lit « appelez-moi au (coordonnées masquées jusqu'à la réservation) ».
- Exemple 2 : après avoir accepté la proposition de Tom, Mme Dupont voit son téléphone dans le rendez-vous.
**Pourquoi :** c'est déjà la règle de rafals (téléphone seulement après réservation), et sans rendez-vous il n'y a ni avis vérifié ni recours en cas de problème.

## Lu, non lu, et prévenir (choix de Claude)
- Chaque message est « envoyé » puis « lu » (quand l'autre ouvre la conversation). Un compteur rouge dans le menu « Messages » donne le nombre de conversations non lues.
- Un nouveau message prévient l'autre par le compteur rouge de l'onglet « Messages » et, si l'application est installée, par une notification (`RM-ALERTES.md`, `RM-APPLICATION.md`).
- **Mail seulement si le message n'est pas lu au bout de 15 minutes**, et au plus un mail par conversation et par heure. Le mail dit « Karim vous a écrit sur rafals » sans recopier le message.
**Pourquoi :** pas de boîte mail noyée quand on discute en direct.

## Bloquer et signaler (choix de Claude)
- Chacun peut **bloquer** l'autre : plus aucun message ne passe dans les deux sens (les rendez-vous déjà pris restent).
- Chacun peut **signaler** une conversation avec une raison. **L'administrateur ne lit une conversation que si elle a été signalée** ; sinon les messages ne sont lus par personne d'autre que les deux personnes.
- Exemple : Mme Dupont signale « il insiste pour être payé avant de venir » → l'administrateur lit le fil, prévient ou bloque le prestataire (`RM-ADMINISTRATION.md`).

## Données personnelles (choix de Claude)
- Une conversation sans nouveau message depuis **3 ans** est effacée (même durée que les comptes inactifs, `RM-CLIENTS.md`).
- Compte fermé : ses messages restent chez l'autre, signés « Personne ayant quitté rafals » ; plus rien ne peut y être écrit.
- « Télécharger mes données » contient ses conversations.
- Les messages ne sortent jamais de rafals (l'IA qui les relit est installée dans rafals).

## Précisions prises au lot 8.1 (proposées par Claude, à relire par Raphael)
- **« Rendez-vous entre eux »** (fin du masquage des coordonnées) : un rendez-vous **confirmé**, passé ou à venir. Une demande encore en attente de réponse ne suffit pas.
- **Ce qui est masqué** : les numéros français (« 06 12 34 56 78 », « 0612345678 », « +33 6 12 34 56 78 ») et les adresses mail. Le texte est gardé tel quel ; il est masqué à l'affichage, y compris dans l'aperçu de la liste. Une heure, un prix ou une date ne sont pas masqués.
- **Message** : un texte, ou des photos sans texte (aperçu « Photo »), ou les deux.
- **Le prestataire voit le client** sous la forme « Marie D. » dans la messagerie, même après un rendez-vous (le nom complet et le téléphone restent sur le rendez-vous, comme le prévoit `RM-CLIENTS.md`).
- **[Écrire à Karim]** est refusé si Karim est en pause, bloqué ou arrêté (« Ce prestataire n'est pas joignable en ce moment. »), sauf si la conversation existe déjà.
- **Mail après 15 minutes** : un seul mail pour tous les messages en attente d'une conversation ; plus de mail pour un message vieux de plus de 2 jours.
- **Débloquer** : seule la personne qui a bloqué peut débloquer.
- **Signalement d'une conversation** : il rejoint les signalements de l'administrateur (`RM-ADMINISTRATION.md`). Signalée par le client, elle vise le prestataire (classer, prévenir, bloquer le prestataire) ; signalée par le prestataire, elle vise le client (classer ou **prévenir** : un mail d'avertissement avec le texte de l'administrateur). L'administrateur lit alors le fil en clair, coordonnées comprises.
- **Effacement après 3 ans** : une conversation signalée n'est pas effacée (un signalement n'est jamais effacé).
- **Effacement après 3 ans, conversation avec une proposition ou une réponse à une demande** (précision du 07/10/2026, lot 8.3) : ses messages et leurs photos sont effacés, mais la conversation reste, vide, avec ses propositions (un rendez-vous peut en venir ; une proposition n'est jamais effacée). Ex. Karim et Mme Dupont ne se sont plus écrit depuis octobre 2026 : en octobre 2029 leurs messages disparaissent, la carte « Proposition acceptée · 60,00 € » reste.
- **Compte fermé** : on ne peut plus écrire dans la conversation (« Cette personne a quitté rafals : on ne peut plus lui écrire. »).

## Qui peut faire quoi
| Action | Qui | Condition |
|---|---|---|
| Commencer une conversation | Client | Prestataire visible, pas bloqué |
| Commencer une conversation | Prestataire | Réponse à une demande, ou rendez-vous / devis avec ce client |
| Écrire, envoyer des photos | Les deux | Conversation ouverte, pas bloquée |
| Envoyer une proposition | Prestataire | Voir `RM-DEMANDES.md` |
| Bloquer, signaler | Les deux | — |
| Lire une conversation | Administrateur | Seulement si elle est signalée |

## Valeurs par défaut (réglages)
Texte : 2000 caractères · photos par message : 5 · mail après : 15 minutes sans lecture · au plus un mail par conversation et par heure · effacement : 3 ans sans message.

## Questions ouvertes
- (aucune)

## Références
- `RM-DEMANDES.md`, `RM-ALERTES.md`, `RM-CLIENTS.md`, `RM-AVIS.md`, `RM-ADMINISTRATION.md`
