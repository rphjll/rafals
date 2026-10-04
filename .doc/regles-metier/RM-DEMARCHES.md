# Démarches administratives — Règles métier (sujet 15)

> Rédigé au lot 6.0 le 03/10/2026, **pendant l'absence de Raphael**. Tout ce qui est marqué 🟡 est un choix **proposé par Claude, à valider**. ⚠️ Les dates et les règles de l'URSSAF sont à faire relire par un comptable avant la mise en ligne.

## À quoi ça sert
Un auto-entrepreneur doit déclarer à l'URSSAF l'argent qu'il a encaissé (son chiffre d'affaires), chaque mois ou chaque trimestre, même s'il n'a rien gagné. rafals lui prépare le chiffre et lui rappelle la date.
- Exemple : Léa a encaissé 1 250,00 € en octobre sur rafals → « À déclarer pour octobre 2026 : 1 250,00 €, avant le 30/11/2026 ».
- Exemple : Karim n'a rien encaissé en août → « À déclarer pour août 2026 : 0,00 € (la déclaration reste obligatoire) ».

## rafals prépare, il ne déclare pas 🟡 (COMPLÉTÉ le 04/10/2026 : voir « Déclarer d'un clic » en bas ; sans accord, cette règle reste vraie)
rafals **n'envoie rien à l'URSSAF** : déclarer à la place du prestataire demande une habilitation (« tierce déclaration », noté dans `PRESENTATION.md`). rafals donne le montant à recopier et un lien vers le site de l'URSSAF.
- Exemple : un bouton [Aller sur le site de l'URSSAF] ouvre autoentrepreneur.urssaf.fr dans un nouvel onglet.
- Exemple : rafals ne connaît jamais le mot de passe URSSAF du prestataire.

## Le chiffre à déclarer 🟡
C'est l'argent **encaissé** pendant la période, d'après les factures faites par rafals : les ventes, moins les avoirs (remboursements), à la date de la facture. Toutes taxes comprises pour un auto-entrepreneur sans TVA ; hors taxe s'il facture la TVA.
- Exemple : octobre : 3 factures (50,00 € + 1 190,00 € + 60,00 €) et 1 avoir (−50,00 €) → 1 250,00 €.
- Exemple : une facture d'arrhes de 357,00 € payée le 03/10 compte en octobre ; le solde de 833,00 € payé le 02/11 compte en novembre.
- **Seulement ce qui passe par rafals** : le prestataire doit ajouter lui-même ce qu'il a encaissé ailleurs (l'écran le rappelle).
- La commission de rafals et les frais de Stripe **ne se déduisent pas** : l'URSSAF calcule sur ce que le client a payé.

## Mois ou trimestre 🟡
Le prestataire a choisi à l'URSSAF de déclarer chaque mois ou chaque trimestre. rafals montre les deux présentations (par mois, et par trimestre) ; quand il aura dit son choix dans « Mes démarches », rafals lui enverra les rappels.
- Dates limites, par mois : la fin du mois suivant. Ex. octobre 2026 → avant le 30/11/2026.
- Dates limites, par trimestre : 30 avril, 31 juillet, 31 octobre, 31 janvier. Ex. juillet à septembre 2026 → avant le 31/10/2026.

## Les rappels 🟡 (à construire après validation : il faut une rubrique de plus dans la base)
Un mail 7 jours avant la date limite, puis la veille : « Déclaration URSSAF d'octobre : 1 250,00 € à déclarer avant le 30/11/2026. »
- Exemple : mensuel → mail le 23/11 et le 29/11.
- Exemple : trimestriel → mail le 24/10 et le 30/10.

## Qui est concerné 🟡
Les prestataires avec un SIRET vérifié (les autres n'ont pas de factures). Les sociétés (SARL, SAS) ont un comptable : la page leur sert seulement de récapitulatif.

## Ce que rafals ne fait pas
Ni la déclaration elle-même, ni le calcul des cotisations (le taux dépend de la situation de chacun), ni les impôts.

## Questions pour Raphael
1. Veux-tu les rappels par mail (il faudra ajouter au prestataire le choix « chaque mois / chaque trimestre ») ?
2. Plus tard : demander l'habilitation « tierce déclaration » pour déclarer à la place du prestataire ?

## Mise en œuvre des rappels (lots 6.3 et 6.4, 04/10/2026 ; validé par Raphael : « Oui, on ajoute »)
- Le prestataire choisit dans « Mes démarches » : « Chaque mois », « Chaque trimestre » ou « Pas de rappel » (au départ : pas de rappel).
- Rappels envoyés (vérifié toutes les heures) aux prestataires avec un SIRET vérifié, actifs ou en pause : un mail entre 7 jours et 2 jours avant la date limite, un autre la veille ou le jour même ; jamais deux fois le même.
  - Exemple, chaque mois : « Déclaration URSSAF d'octobre 2026 : 1 250,00 € à déclarer avant le 30/11/2026 » le 23/11, puis le 29/11.
  - Exemple, chaque trimestre : pour juillet à septembre 2026, le 24/10 puis le 30/10.

## Déclarer d'un clic depuis rafals (lot 7.3, 04/10/2026 ; demande de Raphael : « ils clicent sur un bonton et ca l'envoie a l'urasaf » ; maquette `maquette-lot-7.3-declarer-urssaf.html` validée : « oui je valide »)
rafals envoie la déclaration à l'URSSAF à la place du prestataire, par l'« API Tierce Déclaration auto-entrepreneur » (étude : `technique/API-EXTERNES.md`). ⚠️ La documentation technique de l'URSSAF n'est pas publique : construit avec un faux URSSAF, à brancher avant la mise en ligne.

### L'accord (le « mandat »)
- Le prestataire donne son accord une fois : numéro de sécurité sociale (15 caractères, clé vérifiée) et une case « Je donne mandat à rafals… ». rafals le signale à l'URSSAF. Il faut un SIRET vérifié.
  - Exemple : Léa donne son accord le 04/10/2026 → badge vert « accord donné le 04/10/2026 ».
  - Exemple : l'URSSAF répond qu'elle ne connaît pas Léa → « L'URSSAF ne vous connaît pas encore comme auto-entrepreneur : créez d'abord votre espace sur son site. » ; rien n'est enregistré.
- Il peut le retirer quand il veut : rafals le signale à l'URSSAF, efface le numéro de sécurité sociale, et la page redevient comme avant. Les déclarations déjà envoyées restent.
- Sans accord, rien ne change : rafals donne le montant, le prestataire déclare sur le site de l'URSSAF.

### La déclaration
- **Rien ne part sans un clic** : même avec l'accord, c'est le prestataire qui clique [Déclarer à l'URSSAF…] pour chaque période.
- On ne déclare qu'une période **finie**, dans l'ordre choisi dans « Rappels par mail » (chaque mois ou chaque trimestre) ; ce choix est obligatoire pour déclarer.
  - Exemple : le 24/10/2026, Léa (chaque trimestre) peut déclarer juillet à septembre ; pas encore octobre à décembre.
- Montant déclaré = encaissé sur rafals (calculé, non modifiable) + « encaissé ailleurs » (saisi, 0 par défaut).
  - Exemple : 1 250,00 € + 200,00 € = 1 450,00 € déclarés.
  - Exemple : rien encaissé du tout → 0,00 € déclaré (la déclaration reste obligatoire).
- Avant l'envoi, rafals montre les cotisations estimées par l'URSSAF ; il faut cocher « Je certifie que ce montant est exact. »
- **Une période déclarée ne se redéclare pas depuis rafals** : pour corriger, passer par le site de l'URSSAF.
- **rafals déclare, il ne paie pas** : les cotisations se paient sur le site de l'URSSAF.
- Après l'envoi : mail « Votre déclaration du 3e trimestre 2026 est envoyée : 1 450,00 €, cotisations 307,40 € », et les rappels de cette période s'arrêtent.
- Refus ou panne de l'URSSAF : le message est montré, rien n'est enregistré comme déclaré, on peut réessayer sans risque de double envoi.
- Nature de l'activité envoyée à l'URSSAF (« prestations de services » ou « activité libérale ») : d'après le métier principal, même correspondance que pour la création d'entreprise (`reglages.py`). ⚠️ À faire relire.

### Mode démonstration
Tant que rafals n'a pas d'accès à l'API de l'URSSAF : tout marche à l'écran, rien n'est envoyé, un bandeau le dit ; les cotisations affichées sont une estimation de rafals (taux dans `reglages.py`, ⚠️ à faire relire).
