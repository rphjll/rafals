# Rendez-vous — Interface

> **Changé le 09/10/2026** (lot 9.3, retrait des annonces ; ce paragraphe passe avant le reste du document) : le bouton [Déplacer] disparaît partout (calendrier du client) ; la fenêtre « Déplacer » et le choix d'un horaire (`ChoixHoraire`, `FenetreReservation`) sont supprimés ; dans l'onglet « Rendez-vous » du prestataire, la carte « Demandes à accepter » ([Accepter], [Refuser…]) est retirée : un rendez-vous est confirmé dès que le client accepte la proposition. Pour changer d'heure, le client écrit au prestataire dans « Messages ».

> **Changé le 07/10/2026** (demande de Raphael, mot pour mot : « l'onglet mes rdv il faut l'enlever et aussi quand y'a un rdv ca doit aparaitre dans le planing mais si c'est un client il faut qu'il ai un a=calendrier clien par contre si c'est un prestataire il faut que ca soit un calendrier par metier et si c'est les 2 il faut tout » ; puis son choix « Enlever la page client »). **La page « Mes rendez-vous » du client (`/rendez-vous`) n'existe plus** : elle est remplacée par le calendrier du client, dans « Mon agenda » (`frontend/src/components/rendez-vous/CalendrierClient.vue`, décrit dans `RM-AGENDA-IHM.md` § « Calendrier du client »). Tout ce que ce document dit des boutons du client (annuler, déplacer, donner un avis, absence, retour du paiement) reste vrai : ils sont maintenant sous le calendrier. L'adresse `/rendez-vous` renvoie vers `/mon-agenda?calendrier=client` en gardant ses réglages (retour du paiement par carte compris). L'onglet « Rendez-vous » du prestataire, dans « Mon agenda », ne change pas.

> Fichiers : `frontend/src/pages/RendezVousPage.vue` (client), `frontend/src/components/agenda/OngletRendezVous.vue` (prestataire), `frontend/src/components/rendez-vous/` (`ChoixHoraire`, `FenetreReservation`, `LigneRendezVous`), `frontend/src/outils/rendez_vous.ts`. Construit au lot 4.4 (01/10/2026). Règles : `RM-RENDEZ-VOUS.md`. Maquette : `maquette-lot-4.4-rendez-vous.html`.

## Réserver (page d'une annonce, voir `RM-ANNONCE-IHM.md`)
Carte « Choisir un horaire » sous l'annonce (pas pour « sur devis ») :
- (à l'heure) « Combien d'heures ? » : « 2 h · 50 € », « 3 h · 75 € »… (le minimum au départ).
- Bande des 14 prochains jours (« mar. **13** oct. ») ; un jour sans horaire est pâli avec « complet » ; au départ, le 1er jour qui a des horaires.
- « mardi 13 octobre » puis les heures libres en pastilles (« 9 h 00 », « 9 h 15 »…) ; aucune : « Aucun horaire libre ce jour-là : essayez un autre jour. »
- Clic sur une heure : pas connecté → message « Connectez-vous pour réserver : vous reviendrez ici. » et page de connexion, qui revient sur l'annonce ; sa propre annonce → « Vous ne pouvez pas réserver votre propre annonce. » ; sinon la fenêtre.

**Fenêtre « Réserver ce rendez-vous ? »** : Service (« Coupe femme, avec Léa Martin »), Quand (« Mardi 13/10/2026, 10 h 45 – 11 h 30 »), Prix (« 75 € (3 h à 25 €) ») ; « Où ? » [Chez moi | Chez Léa — Mérignac] si l'annonce a lieu des deux façons ; « chez le prestataire » seul : « Chez Léa, à Mérignac : l'adresse exacte vous sera donnée dès la confirmation. » ; chez le client : carte « Votre adresse » (la carte d'adresse commune ; sans adresse : « Le prestataire vient chez vous : indiquez votre adresse (elle sera gardée pour les prochaines fois). ») ; « Paiement * » [Espèces, le jour même | Carte, maintenant] (lot 5.2 : choisi d'avance selon l'annonce ; un mode refusé par l'annonce est 🔒 : « Léa Martin se fait payer en espèces pour ce service. ») ; carte choisie : bandeau « Vous payez 50 € maintenant sur la page sécurisée de Stripe (30 minutes pour payer). Remboursé en entier si Léa Martin refuse ou annule ; si vous annulez à temps, remboursé moins les frais de paiement (environ 1 €). » et le bouton devient [Payer 50 € et réserver] → la page de paiement de Stripe ; erreur dans la fenêtre (ex. « Cet horaire vient d'être pris ou n'est plus disponible : choisissez-en un autre. ») ; [Réserver mardi 13/10 à 10 h 45] (verrouillé 🔒 tant qu'il manque l'adresse) / [Annuler]. Réussite : « Rendez-vous confirmé. » ou « Demande envoyée : le prestataire a 24 h pour répondre. », puis `/rendez-vous`.

## « Mes rendez-vous » (client, `/rendez-vous`)
Pas connecté : carte « Connectez-vous pour voir vos rendez-vous. » + [Se connecter] (revient ici). Onglets « À venir » (le plus proche d'abord) et « Passés et annulés » (`?onglet=passes`, le plus récent d'abord).

**Un rendez-vous** : titre (+ « · 3 h »), badge (confirmé vert, en attente orange, refusé rouge, annulé par le prestataire rouge, passé / sans réponse / annulé par le client / déplacé gris), « Mardi 13/10/2026, 10 h 00 – 10 h 45 », « Avec » le nom du prestataire (lien vers sa page) et son téléphone une fois confirmé, « Où » (« Chez vous : 8 allée des Pins, 33400 Talence », ou l'adresse du local une fois confirmé), « Prix » (« 35 € · espèces »), « Motif » s'il y en a.
- En attente : « Léa Martin doit accepter avant le lundi 12/10 à 18 h 00. » + [Annuler la demande].
- Confirmé, dans le délai : [Déplacer] [Annuler…] + « Annulation gratuite jusqu'au lundi 12/10 à 10 h 00. »
- Confirmé, hors délai : 🔒 [Déplacer] 🔒 [Annuler] : « Le délai d'annulation gratuite est passé : appelez Léa Martin au 06 12 34 56 78. »
- Vide : « Aucun rendez-vous pour l'instant. » + [Trouver un prestataire].

Fenêtre « Annuler ce rendez-vous ? » : « Coupe femme avec Léa Martin, mardi 13/10/2026, 10 h 00 – 10 h 45. Léa Martin est prévenu par mail et l'horaire redevient libre. » ; [Annuler le rendez-vous] (danger) / [Garder] → « Rendez-vous annulé. »
Fenêtre « Déplacer « Coupe femme » » : « Actuellement : … Choisissez un nouvel horaire (même prix). », le même choix d'horaire ; un clic déplace → « Rendez-vous déplacé au 15/10 à 14 h 00. » ou « Demande envoyée : votre rendez-vous actuel reste valable tant que Léa Martin n'a pas accepté. » ; [Fermer].

## Rendez-vous reçus (prestataire, « Mon agenda › Rendez-vous », `?onglet=rendez-vous`)
Compteur orange sur l'onglet : le nombre de demandes à accepter.
1. Carte « Demandes à accepter » (s'il y en a) : chaque demande (nom, téléphone et adresse du client visibles) + [Accepter] → « Rendez-vous accepté : Marie Dupont est prévenu. », [Refuser…], « Répondez avant le lundi 12/10 à 18 h 00. »
2. Carte « À venir » : les rendez-vous confirmés + [Annuler…] ; vide : « Aucun rendez-vous à venir. »
3. « Passés et annulés (5) » : bloc replié.
Fenêtre « Refuser la demande de Marie Dupont ? » (motif facultatif, « ex. Déjà pris ce jour-là ») ou « Annuler le rendez-vous de Marie Dupont ? » (motif obligatoire, « ex. Malade, désolée » ; à moins de 24 h : « l'annulation est comptée et visible par l'administrateur ») ; erreur dans la fenêtre ; [Refuser] / [Annuler le rendez-vous] (danger), [Revenir] / [Garder].

## Absences (lot 4.6, 01/10/2026 ; maquette `maquette-lot-4.6-absences.html`)
Fichiers en plus : `components/rendez-vous/FenetreContestation.vue`, `components/compte/CarteAbsences.vue`, `components/admin/OngletAbsences.vue`.
- **Badge** d'un rendez-vous avec absence : « client absent » / « prestataire absent » (rouge).
- **Bandeau** sous le rendez-vous (orange pour la personne visée, vert pour celle qui a signalé) : « Léa Martin indique que vous n'êtes pas venu. Si c'est faux, contestez avant le lundi 19/10 à 10 h 40. » ; « Vous avez signalé : Karim Benali n'est pas venu. Elle comptera le …, sauf contestation. » ; « Contestée : « … ». rafals va trancher. » ; « Décision de rafals : l'absence compte / ne compte pas. »
- **Client, « Passés et annulés »** : sur un rendez-vous confirmé, de son heure de début à 7 jours après la fin : [Karim Benali n'est pas venu…] (danger) → fenêtre « Karim Benali n'est pas venu ? » (« … est prévenu et a 7 jours pour contester ; sinon, l'absence apparaîtra sur sa page. ») → [Signaler l'absence] → « Absence signalée : Karim Benali a 7 jours pour contester. » ; marqué absent : [Je suis venu…].
- **Prestataire, « Mon agenda › Rendez-vous »** : le bloc « Passés et annulés » s'ouvre tout seul s'il y a quelque chose à faire ; [Client absent] (danger, même délai) → « Absence signalée : Marie Dupont a 7 jours pour contester. » ; marqué absent : [Je suis venu…] ; sur une demande, badge rouge « 2 absences en 6 mois » à côté du nom du client.
- **Fenêtre « Contester l'absence »** : « Expliquez ce qui s'est passé : l'administrateur de rafals lira les deux versions et tranchera. En attendant, rien n'est compté ni affiché. » ; zone « Ce qui s'est passé * » (1000 caractères, aide « ex. « Je suis venu à 10 h, personne n'a ouvert, j'ai appelé 2 fois. » ») ; erreur dans la fenêtre (ex. « Expliquez ce qui s'est passé… ») ; [Envoyer] → « Contestation envoyée : rafals va trancher. » / [Annuler].
- **Mon compte › Absences** (seulement s'il y en a) : « 2 absences sans prévenir en 6 mois » + « À 3 absences en 6 mois, vous ne pouvez plus réserver pendant 1 mois… » ; suspendu : bandeau rouge « 3 absences sans prévenir en 6 mois : vous ne pouvez plus réserver jusqu'au 10/12/2026. »
- **Page publique d'un prestataire** : bandeau orange « 1 absence sans prévenir ces 6 derniers mois » (rien s'il n'y en a pas).

## Paiement par carte (lot 5.2, 02/10/2026 ; maquette `maquette-lot-5.2-paiements.html`)
Fichiers en plus : `frontend/src/outils/paiements.ts` (types, sommes « 46,50 € », textes des paiements). Règles : `RM-PAIEMENTS.md`.
- **Retour de Stripe sur « Mes rendez-vous »** (`?rdv=40&paiement=fait`) : bandeau vert « Paiement reçu : votre rendez-vous est confirmé. » (ou « Paiement reçu : Léa Martin a 24 h pour accepter. ») ; tant que Stripe n'a pas prévenu rafals : bandeau orange « Paiement en cours de confirmation… », la page se relit toutes les 2 secondes (30 secondes au plus), puis « Le paiement n'est pas encore confirmé : actualisez la page dans quelques minutes. » Revenu sans payer (`paiement=annule`) : la réservation est annulée aussitôt (sans prévenir le prestataire, qui ne l'a jamais vue), bandeau orange « Paiement non terminé : rien n'a été pris, la réservation est annulée. »
- **Ligne « Prix »**, client : « 50 € · payé par carte le 02/10/2026 », « 120 € · par carte · remboursé 120,00 € le 05/10/2026 », « 50 € · paiement par carte en attente » ; prestataire : « 50 € par carte · pour vous 46,50 €, versés le 15/10 », « 50 € par carte · 46,50 € versés le 15/10 », « … · remboursé au client ».
- **Annuler un rendez-vous payé** : dans la fenêtre, bandeau « Payé par carte : vous serez remboursé de 49,00 € (50,00 € moins 1,00 € de frais de paiement), sous 5 à 10 jours. » ; réussite : « Rendez-vous annulé : remboursement en cours. »
- **Absence du prestataire** : payé par carte, le bouton [Léa Martin n'est pas venue…] reste 48 h après la fin (7 jours en espèces).
- Une réservation par carte pas encore payée n'apparaît pas chez le prestataire.

## [Payé…] et facture (lot 5.6, 03/10/2026)
Voir `RM-FACTURES-IHM.md` : bouton [Payé…] du prestataire sur un rendez-vous en espèces, ligne « Prix » « … · payé en espèces le 13/10/2026 · facture F-2026-0003 », bouton [Facture (PDF)].

## Rendez-vous venu d'une proposition (ajouté le 07/10/2026, lot 8.3)
Un rendez-vous créé quand le client accepte une proposition (`RM-DEMANDES.md`) s'affiche comme les autres, avec le titre de la demande (ex. « Fuite sous l'évier »). Seule différence : le bouton **[Déplacer] est verrouillé 🔒**, « Ce rendez-vous vient d'une proposition : demandez un autre horaire à Karim Benali dans vos messages. » [Annuler…] ne change pas.
