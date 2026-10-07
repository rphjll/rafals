# Messages — Interface

> Fichiers : `frontend/src/pages/MessagesPage.vue`, `frontend/src/components/messagerie/CarteProposition.vue`, `frontend/src/components/messagerie/FenetreProposition.vue`, `frontend/src/composables/useNonLus.ts`, `frontend/src/outils/messagerie.ts`. Construit le 07/10/2026 (lots 8.2 et 8.4), d'après la maquette validée `maquette-niveau-8-demandes.html`. Règles : `RM-MESSAGERIE.md`, `RM-DEMANDES.md`.

## Où
Entrée « Messages » de l'en-tête (seulement connecté), avec un **compteur rouge** : le nombre de conversations qui ont du nouveau. Il est relu toutes les minutes et à chaque ouverture d'une conversation. Contenu centré, 760 px au plus.

Pas connecté : titre « Messages », bandeau gris « Connectez-vous pour lire vos messages. », bouton [Se connecter].

## Liste (`/messages`)
1. Titre « Messages », puis « Une seule conversation par personne : tous vos échanges au même endroit. »
2. Un cadre, une ligne par conversation, la plus récente en haut. Chaque ligne est cliquable en entier → `/messages/12`.
   - À gauche : le nom en gras (« Karim Benali » pour le client, « Marie D. » pour le prestataire), une pastille rouge avec le nombre de messages non lus, un badge gris « bloquée » si elle l'est ; dessous, le dernier message sur une ligne (coupé par « … »).
   - À droite : « 07/10/2026 à 11 h 40 › ».
3. Liste vide : « Aucune conversation. Publiez une demande sur l'accueil, ou répondez à une demande si vous proposez vos services. »

## Conversation (`/messages/12`)
**Ordre des éléments :**
1. Ligne de boutons : à gauche [‹ Messages] ; à droite [Signaler…] et [Bloquer…] (rouge). Conversation bloquée par moi : [Débloquer] à la place de [Bloquer…] ; bloquée par l'autre : aucun des deux.
2. Un cadre blanc :
   1. Le nom de l'autre personne, en titre.
   2. Une ligne en pointillés par demande dont on parle : « Demande : **Fuite sous l'évier** · Pessac · Dès que possible · budget 40 € ».
   3. **Le fil**, du plus ancien au plus récent ; il se relit tout seul toutes les 15 secondes et descend au dernier message.
      - Mes messages : bulle verte à droite ; ceux de l'autre : bulle grise à gauche. Sous le texte : les photos en vignettes de 96 px (clic → la photo en grand), puis « 07/10/2026 à 11 h 40 · lu » (ou « envoyé ») sur les miens.
      - Lignes de rafals : petit texte gris centré (ex. « Karim Benali a répondu à la demande « Fuite sous l'évier ». », « Essai D. a choisi un autre prestataire… »). Celles qu'une carte de proposition montre déjà ne sont pas répétées.
      - **Cartes de proposition** (voir plus bas), à leur place dans le temps.
      - Fil vide : « Aucun message pour l'instant : écrivez le premier. »
   4. Zone pour écrire : « Votre message » (2000 caractères au plus), les photos choisies en pastilles avec ×, puis les boutons [Envoyer], [Joindre une photo (0 / 5)] et, **pour le prestataire seulement**, [Faire une proposition…]. Message refusé (injure, trop long…) : bandeau rouge au-dessus des boutons, le texte reste.
      - Conversation bloquée : à la place, bandeau gris « Conversation bloquée : plus aucun message ne passe. »
   5. Tant qu'il n'y a pas de rendez-vous entre les deux : « Téléphone et mail sont masqués dans les messages tant qu'il n'y a pas de rendez-vous entre vous. »

**Fenêtres :**
- [Bloquer…] → « Bloquer cette personne ? Plus aucun message ne passera, dans les deux sens. Les rendez-vous déjà pris restent. » [Bloquer] [Annuler] → message « Personne bloquée : plus aucun message ne passe. »
- [Signaler…] → fenêtre à un texte (« Que se passe-t-il ? », 10 à 1000 caractères) → « Conversation signalée : l'administrateur va regarder. »

## Carte d'une proposition
Bord vert tant qu'elle attend une réponse, grisée ensuite. De haut en bas :
1. « Proposition de Karim Benali · « Fuite sous l'évier » » (le prestataire lit « Votre proposition ») et, à droite, un badge : en attente (orange), prix en négociation (orange), acceptée (vert), refusée (rouge), retirée / remplacée / non retenue / expirée (gris).
2. Le prix en grand : « 60,00 € ».
3. « 12/10/2026 à 8 h 30 · 1 h · chez vous » (le prestataire lit « chez le client »).
4. « Paiement : carte ou espèces ».
5. **Le client, proposition en attente** : [Accepter 60,00 € · 12/10/2026 à 8 h 30] · [Négocier le prix] · [Refuser] (rouge), dans cet ordre.
   - [Accepter…] ouvre « Confirmer le rendez-vous » : le rappel, « Comment payez-vous ? » (Espèces, le jour même / Carte, maintenant ; un mode impossible est verrouillé 🔒 avec la raison), puis le même bouton [Accepter 60,00 € · …]. Espèces → message « Rendez-vous confirmé · 12/10/2026 à 8 h 30 ». Carte → la page de paiement de Stripe.
   - [Négocier le prix] ouvre « Votre prix (€) » → [Proposer ce prix]. Tant que le prestataire n'a pas répondu, le bouton est verrouillé 🔒 : « Vous avez déjà proposé 50,00 € : attendez la réponse de Karim Benali. »
   - [Refuser] agit tout de suite, sans raison à donner.
6. **Prix proposé par le client** (encadré orange dans la carte) : « Prix proposé par Marie D. : **50,00 €** au lieu de 60,00 €. Le jour, l'heure et le reste ne changent pas. » Le prestataire a [Accepter 50,00 €] et [Refuser ce prix] ; le client lit « En attente de la réponse de Karim Benali. »
7. **Le prestataire, proposition en attente** : [Retirer ma proposition] (rouge).
8. Proposition acceptée : [Voir le rendez-vous] → « Mes réservations » (client) ou « Mon agenda » (prestataire).
9. Une action refusée (ex. « Vous avez déjà un rendez-vous à cette heure-là… ») : bandeau rouge dans la carte, ou dans la fenêtre si elle est ouverte.

## Fenêtre « Faire une proposition » (prestataire)
1. « Pour quelle demande ? * » : les demandes encore ouvertes auxquelles il a répondu dans cette conversation. **S'il n'y en a pas** (le client a écrit en premier) : « Pour quel métier ? * » (ses métiers) et deux cases collées « Chez le client | Chez moi ».
2. Sur deux colonnes : « Prix (€) * », « Durée * » (30 min, 45 min, 1 h, 1 h 30, 2 h, 3 h, 4 h), « Jour * », « Heure de début * ».
3. « Paiement accepté * » : deux cases à cocher, « Espèces, le jour même » (cochée au départ) et « Carte sur rafals (SIRET vérifié et paiement par carte activé) ».
4. « Si Marie D. accepte, un rendez-vous confirmé est créé dans votre agenda, même hors de votre semaine type. Par carte : 5 % pour rafals, versement 48 h après. »
5. [Fermer] · [Envoyer la proposition] → message « Proposition envoyée à Marie D. » ; refus de la règle en bandeau rouge dans la fenêtre.

## Pas encore fait
- La carte « Rendez-vous passé : noter » et la moyenne à côté des noms (lots 8.5 et 8.6).
- Un devis à la place d'une proposition simple (niveau 9).
