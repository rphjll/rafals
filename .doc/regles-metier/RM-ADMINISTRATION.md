# Administration de la plateforme — Règles métier (sujet 16)

> Rédigé au lot 6.0 le 03/10/2026, **pendant l'absence de Raphael**. Tout ce qui est marqué 🟡 est un choix **proposé par Claude, à valider**. Ce qui existe déjà est rappelé avec son lot.

## Sans annonces (décision de Raphael du 04/10/2026 ; construit le 09/10/2026, lot 9.2)
Les annonces sont retirées (`RM-PRESTATAIRES.md` § « Sans annonces »). Après les lots 8.3 et 8.4, ce fichier se lira ainsi (choix de Claude, proposés avec le MLD `MLD-retrait-annonces.html`) :
- **On signale** un prestataire, une demande ou une conversation ; plus une annonce.
  - Exemple 1 : Mme Dupont signale le profil « Plombier pas cher » : « Photos volées sur un autre site » → l'administrateur le bloque.
  - Exemple 2 : Karim signale la demande « Travail au noir, pas de facture » → l'administrateur la cache.
- **Décisions possibles** : « Rien à faire », « Bloquer le prestataire », « Cacher la demande ». « Retirer l'annonce » disparaît, avec la règle « le prestataire ne peut pas la remettre en ligne ».
- **Tableau de bord** : le chiffre « annonces en ligne » est remplacé par « demandes ouvertes ».
- Un prestataire est visible dès que son profil est rempli ; l'administrateur agit toujours après coup.

**Construit le 09/10/2026 (lot 9.2)** : on ne signale plus une annonce ; la décision « Retirer l'annonce » a disparu ; le tableau de bord montre « Demandes ouvertes ». « Cacher la demande » n'est pas encore construit (lot 8.5 : signalements étendus aux demandes).

## À quoi ça sert
L'administrateur (Raphael) surveille rafals et règle ce que les règles automatiques ne règlent pas.
- Exemple : un client signale une annonce mensongère → l'administrateur la regarde et la retire.
- Exemple : en ouvrant « Administration », Raphael voit « 3 choses attendent une décision ».

## Ce qui existe déjà
- Accords des parents à vérifier (lot 1.3) ; comptes et rôle d'administrateur (lot 1.4).
- Prestataires : SIRET validé à la main, blocage et déblocage (lots 2.4, 2.5).
- Métiers et propositions de métiers (lot 2.2).
- Absences contestées (lot 4.5), avis signalés et mots interdits (lot 4.7), problèmes de devis (lot 5.3).

## Validation des prestataires 🟡
Pas de validation avant publication : un prestataire est visible dès sa première annonce (règle déjà en place, `RM-PRESTATAIRES.md`). L'administrateur agit **après coup** : blocage, sur signalement ou de lui-même.
- Exemple : Julie crée son profil à 10 h et publie une annonce à 10 h 05 : elle est visible tout de suite.
- Exemple : un faux profil est signalé → l'administrateur le bloque ; ses annonces disparaissent des recherches.

## Tableau de bord 🟡
Le premier onglet de l'administration montre, en chiffres : ce qui attend une décision (avec un lien vers chaque onglet), et l'activité du mois (nouveaux comptes, prestataires actifs, annonces en ligne, rendez-vous, paiements par carte, commission de rafals).
- Exemple : « À traiter : 2 accords, 1 absence contestée, 0 avis signalé ».
- Exemple : « Octobre 2026 : 14 paiements par carte · 812,00 € · commission 40,60 € ».

## Suivi des paiements 🟡
Un onglet « Paiements » liste tous les paiements par carte (le plus récent d'abord) : date, prestataire, client, montant, commission, état. Lecture seule : les remboursements et les versements restent automatiques.
- Exemple : « 02/10 · Léa Martin · Paul Petit · 50,00 € · 2,50 € · versé ».
- Exemple : un paiement resté « payé » longtemps après son rendez-vous se repère d'un coup d'œil (Stripe en panne ?).

## Signalements 🟡 (à construire après validation : il faut une table de plus)
Tout utilisateur connecté peut signaler une annonce ou un prestataire, avec un motif d'au moins 10 caractères. L'administrateur voit le signalement et choisit : « rien à faire », ou agir (retirer l'annonce, bloquer le prestataire) ; celui qui a signalé n'est pas nommé au prestataire.
- Exemple : Paul signale l'annonce « Plomberie — 5 € » : « Prix mensonger, il demande 80 € sur place » → l'administrateur met l'annonce hors ligne avec un motif.
- Exemple : un signalement abusif → « rien à faire », le signalement est classé.

## Litiges 🟡
rafals ne tranche que ce qui est prévu : une absence contestée (lot 4.5), un avis signalé (lot 4.7), un problème sur des travaux (lot 5.3). Pour le reste (malfaçon, retard), rafals met en relation mais ne décide pas d'un remboursement à la place des deux personnes.
- Exemple : « le muret penche » → l'administrateur contacte Paul et Mme Dupont ; il n'impose pas de remboursement.
- Exemple : « Léa n'est pas venue » → règle des absences : remboursement automatique si l'absence compte.

## Journal 🟡
Chaque décision de l'administrateur est déjà inscrite au journal des actions (qui, quoi, quand). Un onglet « Journal » pour le lire viendra si besoin.

## Questions pour Raphael
1. Les signalements d'annonces et de prestataires : on les construit (une table de plus) ?
2. Le tableau de bord et le suivi des paiements te conviennent-ils tels quels ?

## Mise en œuvre des signalements (lots 6.3 et 6.4, 04/10/2026 ; validé par Raphael : « Oui, on ajoute »)
- Un même utilisateur ne peut pas signaler deux fois la même annonce (ou le même prestataire) tant que son signalement n'est pas traité : « Vous l'avez déjà signalé : l'administrateur va regarder. » On ne se signale pas soi-même.
- L'administrateur choisit : **Rien à faire** (classé), **Retirer l'annonce** ou **Bloquer le prestataire**, avec un motif d'au moins 5 caractères envoyé par mail au prestataire. Le nom de celui qui a signalé n'y figure jamais.
  - Exemple : « L'administrateur de rafals a retiré votre annonce « Plomberie ». Motif : « Prix mensonger ». »
  - Exemple : bloquer annule aussi les rendez-vous à venir du prestataire (règle déjà en place, `RM-PRESTATAIRES.md`).
- L'administrateur voit combien de fois le prestataire a déjà été signalé (« déjà signalé 1 fois »).
- Une annonce retirée par l'administrateur n'est plus visible ; rien n'est effacé. **Le prestataire ne peut pas la remettre en ligne** (correction demandée par Raphael le 04/10/2026 : « j'ai suprimé l'annonce de paul mais il peut la remettre en ligne »).
  - Exemple : Paul clique [Republier] sur « Plomberie — 5 € » retirée par l'administrateur → bouton 🔒 : « Cette annonce a été retirée par l'administrateur de rafals : vous ne pouvez pas la remettre en ligne. »
  - Exemple : une annonce que Paul a retirée lui-même reste republiable comme avant.
