# Une annonce (vue par un client) — Interface

> Fichiers : `frontend/src/pages/AnnoncePage.vue`, `frontend/src/outils/annonces.ts`. Construit au lot 3.2 (29/09/2026). Règles : `RM-ANNONCES.md`. Maquette : `maquette-lot-3.2-annonces.html` (écran 5).

## Page `/annonces/12`
Ouverte à tous, même sans compte. Une annonce cachée (en pause, retirée, métier arrêté, activité en pause ou bloquée) répond « Cette annonce n'existe pas. » — sauf pour son auteur, qui la voit quand même.

1. (auteur) bandeau orange « Aperçu de votre annonce, telle que les clients la voient. » + lien [Modifier].
2. Photos (s'il y en a) : la grande photo, puis les vignettes numérotées (clic = la montrer en grand).
3. Carte : titre + prix à droite (« 50 € », « 40 € de l'heure », « Sur devis ») ; « par **Karim Benali** · Plombier » (le nom mène à sa page publique `/prestataires/12`, lot 4.2) ; puis
   - Durée : « 2 h » (prix fixe) ou « au choix, de 1 h à 3 h » (à l'heure) ; rien pour « sur devis » ;
   - Où : « Chez vous (Karim Benali vient de Pessac) » ; « Chez Léa, à Mérignac (adresse donnée après réservation) » ; « Chez vous, ou chez Léa à Mérignac » — **jamais la rue** ;
   - Paiement : « Carte bancaire ou espèces » / « Espèces » (la carte seulement si le SIRET est vérifié en ce moment et le paiement par carte activé chez Stripe, lot 5.2) ;
   - la description ;
   - « sur devis » : bouton [Demander un devis] → fenêtre de demande (lot 5.4, voir `RM-DEVIS-IHM.md`).
4. (prix fixe ou à l'heure) Carte « Choisir un horaire » et fenêtre de réservation : voir `RM-RENDEZ-VOUS-IHM.md` (lot 4.4).

## [Signaler cette annonce…] (lot 6.4, 04/10/2026)
En bas de la carte de l'annonce, à droite (absent sur sa propre annonce) : voir `RM-SIGNALEMENTS-IHM.md`.
