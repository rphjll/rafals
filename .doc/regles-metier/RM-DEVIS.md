# Devis — Règles métier (sujet 10)

> Rédigé au lot 5.0, à partir des réponses de Raphael. En cours d'écriture. Point de départ : `RM-ANNONCES.md` § « Sur devis » (le client envoie une demande écrite, avec photos, et le prestataire répond par un devis).

## Sans annonces (décision de Raphael du 04/10/2026 ; porte d'entrée « profil » construite le 09/10/2026, lot 9.2)
Les annonces sont retirées (`RM-PRESTATAIRES.md` § « Sans annonces »). Après les lots 8.3 et 8.4, seule la **porte d'entrée** du devis change (choix de Claude, proposés avec le MLD `MLD-retrait-annonces.html`) :
- Le client clique **[Demander un devis]** sur le profil d'un prestataire avec SIRET vérifié, et choisit un de ses métiers.
  - Exemple : Mme Dupont ouvre le profil de Paul, maçon, choisit « Maçon » et écrit « Muret de 5 mètres au fond du jardin », avec 2 photos.
- Ou le prestataire répond à une **demande publiée** par un devis au lieu d'une proposition simple.
  - Exemple : M. Petit publie « Refaire ma salle de bain » ; Karim clique [Répondre], puis [Faire un devis] : 1 800 €, arrhes de 30 %.
- **Moyens de paiement** : le prestataire les choisit en écrivant le devis (avant, ils venaient de l'annonce).
- Tout le reste ne change pas : lignes, arrhes, acceptation, jours de travaux, facture.
- **Préparé le 08/10/2026 (lot 9.1, `db/schema_v25.sql`)** : une demande de devis porte maintenant son métier (recopié de l'annonce, ex. demande n° 5 → « Plombier ») et peut porter la demande publiée dont elle vient ; l'annonce n'y est plus obligatoire. Les deux nouvelles portes d'entrée ci-dessus sont au lot 9.2.

**Construit le 09/10/2026 (lot 9.2)** : [Demander un devis] sur la page d'un prestataire au SIRET vérifié, avec le choix du métier s'il en a plusieurs. Le titre d'une demande de devis est le nom du métier (ex. « Maçon »).
- Refus : pas de SIRET vérifié ; métier que le prestataire n'exerce pas ; devis demandé à soi-même.
- **Moyens de paiement d'un devis (choix de Claude, différent de la ligne ci-dessus)** : « carte » si le prestataire a un SIRET vérifié et le paiement par carte activé, « en direct » toujours. Le choix par le prestataire en écrivant le devis demanderait une rubrique nouvelle dans la base (MLD à valider par Raphael).
- **Pas encore construit** : répondre à une demande publiée par un devis ([Faire un devis] dans la conversation). La rubrique `demande_id` existe déjà dans la base (lot 9.1).

## Paiement d'un devis accepté : arrhes, puis solde (choix de Raphael le 02/10/2026)
- Le prestataire fixe des **arrhes** dans son devis (un pourcentage du total). Elles sont payées par carte **dès que le client accepte** le devis, et versées au prestataire sans attendre, pour qu'il puisse acheter ses matériaux.
- Le **reste (le solde)** est payé quand le prestataire déclare le travail terminé.
- rafals garde 5 % de chaque paiement (`RM-PAIEMENTS.md`).
  - Exemple : devis de Paul, maçon, 1 200 € avec 30 % d'arrhes → Mme Dupont paie 360 € en acceptant (rafals garde 18 €), puis 840 € à la fin (rafals garde 42 €).
  - Exemple : devis de 400 € avec 50 % d'arrhes → 200 € en acceptant, 200 € à la fin.
- **Le solde, le client le paie lui-même** après avoir vérifié le travail (choix de Raphael le 02/10/2026) : quand le prestataire clique [Travail terminé], le client reçoit un mail « Paul a terminé. [Payer 840 €] ». S'il n'est pas d'accord, il clique [Signaler un problème] et l'administrateur regarde. rafals relance un client qui tarde.
  - Exemple : Paul clique [Travail terminé] le 20/10 → Mme Dupont vérifie le muret et paie 840 € le 21/10.
  - Exemple : le muret penche → Mme Dupont clique [Signaler un problème] : « Le muret penche de 5 cm » → l'administrateur regarde.

## Durée de validité (choix de Raphael le 02/10/2026)
- Le prestataire choisit la date « Valable jusqu'au », **remplie d'avance à 30 jours** (réglage). Après cette date, le devis est « expiré » : le client ne peut plus l'accepter et doit en redemander un.
  - Exemple : devis envoyé le 02/10 → « Valable jusqu'au 01/11 » ; Paul peut mettre le 17/10 si le prix des matériaux bouge.
  - Exemple : Mme Dupont ouvre le devis le 05/11 → « Ce devis a expiré le 01/11 : demandez-en un nouveau. »

## Contenu : des lignes détaillées (choix de Raphael le 02/10/2026)
- Le devis est fait de **lignes** : libellé, quantité, prix à l'unité ; rafals calcule chaque ligne et le total (la loi demande un devis détaillé pour la plupart des travaux).
  - Exemple : « Parpaings — 40 × 3,50 € = 140,00 € » ; « Main-d'œuvre — 16 h × 45,00 € = 720,00 € ».
  - Exemple : « Déplacement — 1 × 30,00 € = 30,00 € ».

## TVA (choix de Raphael le 02/10/2026, vaut aussi pour les factures)
- Le prestataire coche ou non **« Je facture la TVA »** dans son profil.
- Non coché : une seule somme, avec la mention « TVA non applicable, art. 293 B du CGI ».
  - Exemple : Léa, coiffeuse auto-entrepreneuse → « Coupe et brushing — 50,00 € » + la mention.
- Coché : un taux par ligne (5,5 %, 10 % ou 20 %), et rafals affiche le total hors taxe (HT), la TVA et le total toutes taxes comprises (TTC).
  - Exemple : société de Paul → 1 000,00 € HT + 100,00 € de TVA à 10 % = 1 100,00 € TTC.
- Le client paie toujours le TTC ; les 5 % de rafals se calculent sur ce que paie le client (1 100 € → 55 €).

## Réservé aux prestataires avec un SIRET (choix de Raphael le 02/10/2026)
- Un devis est un document d'entreprise : seul un prestataire avec un SIRET vérifié peut publier une annonce « sur devis » et envoyer des devis. Pour les autres, le choix « sur devis » est grisé : « Réservé aux prestataires avec un SIRET. »
  - Exemple : Tom, 17 ans, sans SIRET → « Tonte — 20 € de l'heure » (espèces) possible, « Taille de haie — sur devis » impossible.
  - Exemple : Paul, maçon avec SIRET → « Muret de jardin — sur devis » possible.

## Modes de paiement d'un devis (choix de Raphael le 02/10/2026)
- Si l'annonce accepte les espèces, le client choisit en acceptant le devis : « Par carte sur rafals » (arrhes puis solde, rafals garde 5 %) ou « En direct avec le prestataire » (espèces, chèque… ; rafals ne touche rien, le prestataire clique [Payé] quand il a reçu l'argent).
  - Exemple : Mme Dupont choisit la carte → 360 € en acceptant, 840 € à la fin.
  - Exemple : M. Leroy choisit « En direct » et paie Paul par chèque → Paul clique [Payé] ; rafals ne touche rien.
- Si l'annonce n'accepte que la carte, seul « Par carte sur rafals » est proposé.

## Date des travaux : le prestataire la propose dans le devis (décidé le 02/10/2026)
Réponses de Raphael, mot pour mot : « dans le calendrié de reservation », puis « paul et apres ils voient si tout est bon et si mme dupont refuse pour la date ils se mettent ok pour changer la date ».
- En écrivant le devis, le prestataire choisit les jours des travaux dans son calendrier de réservation (seulement des jours libres).
- Le client peut accepter le devis, ou cliquer [Demander une autre date] avec un message ; le prestataire change alors les dates et le devis revient au client (le reste du devis ne change pas).
- Les jours sont bloqués dans l'agenda quand le client accepte ; si le devis est refusé ou expire, rien n'est bloqué.
  - Exemple : Paul propose « du lundi 19/10 au mardi 20/10 » → Mme Dupont accepte → le 19 et le 20 sont bloqués dans l'agenda de Paul.
  - Exemple : Mme Dupont écrit « Je suis absente cette semaine-là, plutôt fin octobre » → Paul propose « du 26/10 au 27/10 » → elle accepte.

## Annulation d'un devis accepté (choix de Raphael le 02/10/2026)
- **Le client annule** → le prestataire **garde les arrhes**, et le client ne doit rien de plus.
  - Exemple : Mme Dupont annule le 10/10 → Paul garde 360 € ; les 19 et 20/10 se libèrent dans son agenda.
- **Le prestataire annule** → le client est **remboursé des arrhes**, repris sur les prochains versements du prestataire (frais de Stripe à sa charge, `RM-PAIEMENTS.md`).
  - Exemple : Paul annule le 15/10 → Mme Dupont récupère 360 €.
- **Le mot affiché : « arrhes », toujours expliqué** (décidé le 02/10/2026). Réponse de Raphael, mot pour mot : « bah un truc facile a comprendre ». En droit français, une somme que le client perd s'il annule s'appelle des « arrhes » (un « acompte » l'engagerait à payer tout le prix) ; pour qu'elle soit facile à comprendre, chaque fois qu'elle s'affiche, une explication l'accompagne.
  - Exemple sur le devis : « Arrhes : 360 € — payées maintenant, gardées par Paul si vous annulez. »
  - Exemple sur le bouton : [Accepter et payer 360 € d'arrhes].

## Le parcours d'un devis (résumé des choix ci-dessus)
1. Le client envoie une **demande écrite** depuis une annonce « sur devis » (texte, photos) — `RM-ANNONCES.md`.
2. Le prestataire répond par un **devis** : lignes, TVA, arrhes en %, dates des travaux, « Valable jusqu'au ». Numéros par prestataire : D-2026-0001, D-2026-0002…
3. Le client **accepte** (et paie les arrhes s'il paie par carte), **refuse**, ou **demande une autre date**.
4. Le prestataire clique **[Travail terminé]** → le client paie le solde (ou le prestataire clique [Payé] s'il a été payé en direct).
- **États d'un devis** : envoyé → accepté → terminé → payé ; ou refusé, expiré, annulé (par le client ou le prestataire). Un devis n'est jamais effacé.
- Exemple : D-2026-0002 de Paul (1 200 €, arrhes 30 %) : envoyé le 02/10, accepté le 03/10 (360 €), terminé le 20/10, payé le 21/10 (840 €).
- Exemple : D-2026-0003 de Paul, envoyé le 02/10, sans réponse → expiré le 01/11.

## Mise en œuvre (lot 5.3, 03/10/2026 ; MLD `MLD-lot-5.3-devis.html` validé avec 5 choix)
- **Le prestataire peut décliner une demande** (motif facultatif, envoyé au client). Ex. « Je ne fais pas ce genre de travaux ».
- **Un seul devis par demande** ; refusé ou expiré : le client fait une nouvelle demande.
- **Les jours des travaux sont bloqués** dans l'agenda dès l'acceptation (« Travaux D-2026-0002 ») ; on ne peut pas les débloquer à la main (« pour les libérer, annulez le devis ») ; une annulation les libère. Un devis ne peut proposer que des jours libres (ni rendez-vous, ni congés).
- **« En direct »** : pas d'arrhes par rafals ; le prestataire clique [Payé] (espèces, chèque ou virement) quand il a tout reçu.
- **Au plus 5 photos par demande et 20 lignes par devis** ; demande de 10 à 2000 caractères.
- **Arrhes par carte** : le devis n'est accepté qu'une fois les arrhes payées (30 minutes pour payer, puis on peut recommencer) ; payées trop tard (devis refusé ou expiré entre-temps) : remboursées en entier.
- **Arrhes et solde** partent vers le prestataire sans attendre (pas de délai de 48 h : le client a vérifié le travail avant de payer le solde). Si le prestataire annule après avoir reçu les arrhes, Stripe les reprend sur son compte pour les rendre au client.
- **Rappels du solde** (choix de Claude, réglage) : 3 jours puis 10 jours après [Travail terminé], si le client n'a pas payé.
  - Exemple : travaux déclarés terminés le 20/10 → rappels les 23/10 et 30/10.
- **Numéros** : D-2026-0001, D-2026-0002… par prestataire et par année ; le taux de TVA (ou la mention 293 B) est figé dans le devis à l'envoi.
- Le client voit le téléphone du prestataire une fois le devis accepté.
