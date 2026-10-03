# Factures — Règles métier (sujet 11)

> Rédigé au lot 5.0, à partir des réponses de Raphael. En cours d'écriture. TVA : voir `RM-DEVIS.md` § « TVA » (vaut aussi pour les factures).

## rafals crée les factures tout seul (choix de Raphael le 02/10/2026)
- Après chaque paiement par carte, rafals crée la facture **au nom du prestataire** (son nom, son SIRET, la mention de TVA), en PDF, rangée dans « Mes factures » du client et du prestataire.
- Numéros qui se suivent, sans trou, **par prestataire** et par année : F-2026-0001, F-2026-0002…
- Le prestataire donne son accord une fois, en activant le paiement par carte : c'est un **« mandat de facturation »** (il autorise rafals à faire ses factures à sa place).
  - Exemple : Paul paie 50 € à Léa → facture F-2026-0001 de Léa Martin à Paul, « Coupe et brushing — 50,00 € — TVA non applicable, art. 293 B du CGI ».
  - Exemple : la facture suivante de Léa, pour Mme Dupont → F-2026-0002.
- Une facture n'est **jamais modifiée ni effacée** ; une erreur ou un remboursement se corrige par un **avoir** (une facture « en moins »).

## Paiements en direct (espèces, chèque) : facture aussi (choix de Raphael le 02/10/2026)
- Quand un prestataire avec SIRET clique [Payé] (argent reçu en direct), rafals crée la facture comme pour la carte, avec le moyen de paiement (« Payé par chèque », « Payé en espèces »). Le prestataire garde **une seule suite de numéros**.
  - Exemple : Mme Dupont paie 1 200 € par chèque → Paul clique [Payé] → facture F-2026-0003 « Payé par chèque ».
  - Exemple : Léa (SIRET) reçoit 50 € en espèces pour une coupe → elle clique [Payé] → facture F-2026-0004 « Payé en espèces ». (Le bouton [Payé] vaut donc aussi pour un rendez-vous payé en espèces.)
- Les prestataires **sans SIRET** n'ont pas de factures sur rafals.

## Devis : une facture par paiement
- Les arrhes donnent une **facture d'arrhes**, et le solde une **facture de solde** qui rappelle les arrhes déjà payées (obligation légale).
  - Exemple : F-2026-0005 « Arrhes de 30 % sur le devis D-2026-0002 — 360,00 € », puis F-2026-0006 « Solde — total 1 200,00 €, arrhes déjà payées 360,00 €, reste 840,00 € ».

## Facture de la commission de rafals : une par mois (choix de Raphael le 02/10/2026)
Réponse de Raphael, mot pour mot : « j'ai pas compris juste quand il pay un truc j'ai une comition direct de 5pourcents » — c'est bien le cas : les 5 % sont pris à chaque paiement. La question portait seulement sur la facture que rafals doit donner au prestataire pour ces 5 %. Raphael a d'abord demandé « un papier par trimestre », que la loi ne permet pas (une facture qui regroupe plusieurs ventes couvre au plus un mois, article 289 du Code général des impôts), puis a choisi « un par mois ».
- Le 1er de chaque mois, rafals crée tout seul la facture de ses commissions du mois passé, pour chaque prestataire qui a eu au moins un paiement par carte. Numéros propres à rafals : R-2026-0001, R-2026-0002…
  - Exemple : le 01/11, Léa reçoit R-2026-0001 « Commissions d'octobre 2026 — 12 paiements — 30,00 € ».
  - Exemple : Karim n'a eu aucun paiement par carte en octobre → pas de facture.
- ⚠️ Pour émettre ces factures, rafals doit être une entreprise (avec un SIRET) : à voir avec le professionnel du droit (étape 3 du lot 5.0).

## Facture électronique (à prévoir)
- La réforme française de la facture électronique oblige les petites entreprises à émettre leurs factures entre entreprises par une plateforme agréée à partir du 01/09/2027, et à déclarer les ventes aux particuliers (« e-reporting »). Dates et détail à revérifier avant le niveau 5 ; ça concerne surtout la facture de commission de rafals (de rafals à une entreprise).

## Mise en œuvre (lot 5.5, 03/10/2026 ; MLD `MLD-lot-5.5-factures.html` validé avec 6 choix)
- **Tout est figé** sur la facture le jour où elle est créée : nom du vendeur (la personne, et son enseigne si elle est différente, ex. « Léa Martin — Net & Clair »), SIRET, adresse (son local, sinon sa commune), nom et adresse du client, mention de TVA, lignes.
- **Le PDF est fabriqué à la demande** à partir de ces rubriques figées : toujours le même, rien d'autre n'est stocké. Il porte la phrase « Facture établie par rafals au nom et pour le compte de … (mandat de facturation). »
- **Avoirs dans la même suite de numéros** que les factures du prestataire. Ex. F-2026-0001 (facture), F-2026-0002 (son avoir).
- **Remboursement entier** (le prestataire refuse, annule, est absent) : l'avoir reprend chaque ligne en négatif (−50,00 €). **Le client annule à temps** : avoir du montant rendu (−49,00 €), ligne « Remboursement (frais de paiement non rendus) ».
- **[Payé] sur un rendez-vous** : pour un prestataire avec SIRET vérifié, à partir de l'heure du rendez-vous, une seule fois ; il choisit espèces, chèque ou virement. Sans SIRET : pas de bouton, pas de facture.
- **Facture de solde d'un devis** : les lignes du devis, puis une ligne négative « Arrhes déjà payées (30 % du devis D-2026-0002) ».
- **Commission de rafals** : vérifiée toutes les heures, la facture du mois passé est créée une seule fois par prestataire (R-2026-0001…), sur les paiements par carte du mois qui n'ont pas été remboursés. **Tant que le nom, le SIRET et l'adresse de rafals ne sont pas dans le fichier `.env`, aucune facture de commission n'est créée** (les commissions restent comptées).
  - Exemple : Léa a 12 paiements par carte en octobre, dont 1 remboursé → « Commission de 5 % sur 11 paiements par carte ».
- ⚠️ À confirmer par un comptable avant la mise en ligne (seulement pour les prestataires qui facturent la TVA) : (1) la TVA d'un rendez-vous est calculée à 20 % à partir du prix payé (50,00 € = 41,67 € HT + 8,33 € de TVA), car les annonces n'ont pas de taux ; (2) la facture d'arrhes répartit la TVA comme le devis.
