# Rendez-vous — Interface

> Fichiers : `frontend/src/pages/RendezVousPage.vue` (client), `frontend/src/components/agenda/OngletRendezVous.vue` (prestataire), `frontend/src/components/rendez-vous/` (`ChoixHoraire`, `FenetreReservation`, `LigneRendezVous`), `frontend/src/outils/rendez_vous.ts`. Construit au lot 4.4 (01/10/2026). Règles : `RM-RENDEZ-VOUS.md`. Maquette : `maquette-lot-4.4-rendez-vous.html`.

## Réserver (page d'une annonce, voir `RM-ANNONCE-IHM.md`)
Carte « Choisir un horaire » sous l'annonce (pas pour « sur devis ») :
- (à l'heure) « Combien d'heures ? » : « 2 h · 50 € », « 3 h · 75 € »… (le minimum au départ).
- Bande des 14 prochains jours (« mar. **13** oct. ») ; un jour sans horaire est pâli avec « complet » ; au départ, le 1er jour qui a des horaires.
- « mardi 13 octobre » puis les heures libres en pastilles (« 9 h 00 », « 9 h 15 »…) ; aucune : « Aucun horaire libre ce jour-là : essayez un autre jour. »
- Clic sur une heure : pas connecté → message « Connectez-vous pour réserver : vous reviendrez ici. » et page de connexion, qui revient sur l'annonce ; sa propre annonce → « Vous ne pouvez pas réserver votre propre annonce. » ; sinon la fenêtre.

**Fenêtre « Réserver ce rendez-vous ? »** : Service (« Coupe femme, avec Léa Martin »), Quand (« Mardi 13/10/2026, 10 h 45 – 11 h 30 »), Prix (« 75 € (3 h à 25 €) ») ; « Où ? » [Chez moi | Chez Léa — Mérignac] si l'annonce a lieu des deux façons ; « chez le prestataire » seul : « Chez Léa, à Mérignac : l'adresse exacte vous sera donnée dès la confirmation. » ; chez le client : carte « Votre adresse » (la carte d'adresse commune ; sans adresse : « Le prestataire vient chez vous : indiquez votre adresse (elle sera gardée pour les prochaines fois). ») ; « Paiement * » [Espèces, le jour même | 🔒 Carte] (« Le paiement par carte sur rafals arrive bientôt. ») ; erreur dans la fenêtre (ex. « Cet horaire vient d'être pris ou n'est plus disponible : choisissez-en un autre. ») ; [Réserver mardi 13/10 à 10 h 45] (verrouillé 🔒 tant qu'il manque l'adresse) / [Annuler]. Réussite : « Rendez-vous confirmé. » ou « Demande envoyée : le prestataire a 24 h pour répondre. », puis `/rendez-vous`.

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
