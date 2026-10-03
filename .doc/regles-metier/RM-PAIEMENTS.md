# Paiements et commission — Règles métier (sujet 12)

> Rédigé au lot 5.0, à partir des réponses de Raphael. En cours d'écriture.

## Service de paiement (choix de Raphael le 02/10/2026)
- **Stripe Connect**, formule « Stripe gère la tarification » : chaque prestataire a son propre compte Stripe, relié à rafals. Stripe vérifie son identité.
- **rafals ne garde jamais l'argent des clients** : il va du client au compte Stripe du prestataire ; rafals ne reçoit que sa commission.
- **Aucun frais fixe pour rafals** (pas d'abonnement, rien à payer sans vente).
- **Frais de Stripe** sur chaque paiement par carte : 1,5 % + 0,25 € pour une carte européenne courante (2,8 % + 0,25 € pour une carte « premium »).
  - Exemple : un rendez-vous à 50 € → 0,75 € + 0,25 € = **1,00 €** de frais.
  - Exemple : un rendez-vous à 120 € → 1,80 € + 0,25 € = **2,05 €** de frais.
- Écartés : Mollie (tarif pour les plateformes non publié, sur devis) ; Stripe « rafals gère la tarification » (2 € par prestataire actif et par mois).
- Sources (lues le 02/10/2026) : https://stripe.com/fr/pricing, https://stripe.com/fr/connect/pricing, https://www.mollie.com/fr/pricing

## Commission de rafals (choix de Raphael le 02/10/2026)
- rafals garde **5 %** du prix de chaque rendez-vous payé par carte sur le site.
  - Exemple : Paul paie 50 € à Léa Martin → rafals garde 2,50 €, Stripe 1,00 €, Léa reçoit 46,50 €.
  - Exemple : 120 € → rafals garde 6,00 €, Stripe 2,05 €, le prestataire reçoit 111,95 €.
- **Aucune commission sur les rendez-vous payés en espèces** (choix de Raphael le 02/10/2026) : l'argent ne passe ni par Stripe ni par rafals.
  - Exemple : Paul paie 50 € en liquide à Léa Martin → Léa garde 50 €, rafals ne touche rien.

## Paiement par carte : quand le client paie (choix de Raphael le 02/10/2026)
- Le client paie **dès la réservation** : le prix complet est pris sur sa carte quand il réserve.
- Si le prestataire refuse le rendez-vous, ou si le client annule dans le délai permis (`RM-RENDEZ-VOUS.md`), il est **remboursé automatiquement**.
  - Exemple : Paul réserve le 02/10 un rendez-vous à 50 € pour le 15/10 → 50 € pris le 02/10.
  - Exemple : Léa refuse le rendez-vous le 03/10 → Paul est remboursé de 50 € le 03/10.
- Les frais de Stripe d'un paiement remboursé ne sont pas rendus par Stripe (1,00 € sur 50 €).

## Paiement par carte : quand le prestataire reçoit l'argent (choix de Raphael le 02/10/2026)
- L'argent attend chez Stripe jusqu'au rendez-vous ; il est versé au prestataire **une fois le rendez-vous passé** (Stripe le met sur son compte en banque quelques jours plus tard).
  - Exemple : Paul paie 50 € le 02/10 pour le 15/10 → Léa reçoit 46,50 € à partir du 15/10.
  - Exemple : Léa annule le 10/10 → l'argent n'a pas bougé, Paul est remboursé de 50 € le 10/10.
- Ainsi, rafals n'a jamais à avancer d'argent pour rembourser un client.

## Client absent (choix de Raphael le 02/10/2026)
- Le prestataire marque [Client absent] (`RM-RENDEZ-VOUS.md`) → **il garde l'argent**, comme si le client était venu : il a bloqué son horaire pour rien.
- L'argent attend chez Stripe pendant les **7 jours** laissés au client pour contester. Si l'administrateur donne raison au client (« ne compte pas »), le client est remboursé.
  - Exemple : Paul ne vient pas le 15/10 → sans contestation, Léa reçoit 46,50 € le 22/10.
  - Exemple : Paul conteste le 16/10, l'administrateur lui donne raison le 18/10 → Paul est remboursé de 50 € le 18/10, Léa ne touche rien.

## Délai avant le versement et prestataire absent (choix de Raphael le 02/10/2026)
- L'argent est versé au prestataire **48 heures après la fin du rendez-vous**, si personne n'a signalé d'absence (réglage).
- Le client clique [Prestataire absent] → il est **remboursé** ; si le prestataire conteste et que l'administrateur lui donne raison, le prestataire est payé.
  - Exemple : rendez-vous le 15/10 de 10 h à 11 h, rien de signalé → Léa reçoit 46,50 € le 17/10 à 11 h.
  - Exemple : Paul signale le 16/10 que Léa n'est pas venue → l'argent reste chez Stripe ; sans contestation de Léa au 23/10, Paul est remboursé de 50 €.
- **Rendez-vous payé par carte : le client a 48 heures** après la fin pour signaler l'absence du prestataire (choix de Raphael le 02/10/2026) ; ensuite : « Le délai de 48 heures pour signaler une absence est passé. » Pour les espèces, et pour [Client absent], les 7 jours de `RM-RENDEZ-VOUS.md` ne changent pas.
  - Exemple : rendez-vous par carte le 15/10 à 11 h → Paul peut signaler jusqu'au 17/10 à 11 h.
  - Exemple : même rendez-vous payé en espèces → Paul peut signaler jusqu'au 22/10.

## Frais de Stripe d'un remboursement (choix de Raphael le 02/10/2026)
Lors d'un remboursement, Stripe garde ses frais. **Celui qui annule les paie** ; rafals rend toujours ses 5 %.
- Le prestataire refuse, laisse expirer la demande (24 h), annule, ou est absent → le client est remboursé en entier ; les frais sont retirés du prochain versement du prestataire.
  - Exemple : Léa refuse la demande de Paul (50 €) → Paul récupère 50 € ; 1,00 € est retiré du prochain versement de Léa.
- Le client annule dans le délai permis → il est remboursé moins les frais.
  - Exemple : Paul annule son rendez-vous de 50 € dans le délai → il récupère 49,00 €.
- Absence contestée et donnée au client (« ne compte pas ») → comme une erreur du prestataire : remboursement entier, frais pour le prestataire.

## Prix à l'heure
Le client choisit le nombre d'heures en réservant et voit le total (`RM-ANNONCES.md`) : ce total est payé à la réservation, comme un prix fixe.
- Exemple : Karim, 40 € de l'heure, Paul choisit 3 h → 120 € payés à la réservation ; rafals garde 6,00 €.
- Exemple : même annonce, 2 h → 80 € ; rafals garde 4,00 €.

## Mise en œuvre (lot 5.1, 02/10/2026)
- **Activer la carte** (prestataire) : SIRET vérifié + case « J'accepte que rafals fasse mes factures à ma place » (mandat de facturation, date gardée) → page de Stripe (identité, RIB). Ses annonces proposent « carte » seulement une fois que Stripe a tout vérifié.
- **30 minutes pour payer** (réglage, proposé dans le MLD 5.1 et validé par Raphael) : la réservation par carte attend son paiement ; le prestataire ne la voit pas encore et aucun mail ne part. Sans paiement au bout de 30 minutes, elle est annulée (« Paiement non terminé ») et l'horaire se libère.
  - Exemple : Paul réserve à 14 h 00 et ferme la page de Stripe → à 14 h 30, la réservation est annulée : « Rien n'a été pris sur votre carte. »
  - Exemple : un paiement qui arrive quand même après l'annulation est remboursé en entier.
- **Un rendez-vous déplacé garde son paiement** : rien à repayer.
- **Les frais retenus** sur le versement suivant se voient dans le mail du prestataire.
  - Exemple : « 45,50 € versés vers votre compte en banque (1,00 € de frais de remboursement retenus) ».
- **Panne de Stripe** : les remboursements et les versements sont réessayés toutes les 5 minutes, sans jamais être faits deux fois.
- **Sans clés Stripe** dans le fichier `.env`, le paiement par carte est simplement fermé : « Le paiement par carte n'est pas encore ouvert sur rafals. »
- **Devis (lot 5.3)** : les arrhes et le solde payés par carte sont versés sans attendre (voir `RM-DEVIS.md`). Un paiement remboursé après avoir été versé garde sa date de versement (`schema_v14.sql`, décision de Raphael du 03/10/2026).
