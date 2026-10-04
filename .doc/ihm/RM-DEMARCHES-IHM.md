# Mes démarches — Interface

> Fichiers : `frontend/src/pages/DemarchesPage.vue`. Construit au lot 6.2 (03/10/2026, pendant l'absence de Raphael : maquette `maquette-lot-6.2-services.html` **à valider**). Règles : `RM-DEMARCHES.md`.

## Page « Mes démarches » (`/demarches`, menu « Mes démarches », seulement pour un prestataire)
Même gardien que « Mes annonces » (se connecter / proposer ses services). Contenu centré, 720 px au plus. Titre « Mes démarches ».

**Sans SIRET vérifié** : carte « Déclaration à l'URSSAF » — « Les démarches concernent les prestataires avec un SIRET vérifié : sans lui, rafals ne fait pas de facture. » + [Créer mon auto-entreprise] → le guide.

**Avec un SIRET vérifié**, carte « Déclaration à l'URSSAF » :
1. « Un auto-entrepreneur déclare à l'URSSAF ce qu'il a encaissé, chaque mois ou chaque trimestre, même 0 €. rafals prépare le chiffre d'après vos factures ; la déclaration se fait sur le site de l'URSSAF. »
2. Bandeau orange, s'il y a une période finie dont la date limite n'est pas passée : « À déclarer pour septembre 2026 : **1 250,00 €**, avant le 31/10/2026. »
3. [Aller sur le site de l'URSSAF] (principal) : ouvre autoentrepreneur.urssaf.fr dans un nouvel onglet.
4. Bascules « Par mois | Par trimestre » et, à partir de 2027, l'année (« 2026 | 2027 »).
5. Tableau (défile sur le côté sur téléphone), la période la plus récente d'abord, seulement les périodes commencées : Période (« Octobre 2026 », « 3e trimestre 2026 ») · Encaissé (« 1 250,00 € », « (HT) » si TVA) · Factures (le nombre) · À déclarer avant le (« 30/11/2026 ») · badge gris « en cours », orange « à déclarer », ou « date passée ».
6. « Seulement ce qui est passé par rafals : ajoutez ce que vous avez encaissé ailleurs. La commission de rafals et les frais de paiement ne se déduisent pas. » (+ « Vous facturez la TVA : les montants sont hors taxe. »)

## Carte « Rappels par mail » (lot 6.4, 04/10/2026 ; maquette validée `maquette-lot-6.4-signalements-rappels.html`)
Sous la carte « Déclaration à l'URSSAF », seulement avec un SIRET vérifié : « Dites à rafals comment vous déclarez à l'URSSAF : vous recevrez un mail 7 jours avant la date limite, puis la veille, avec le montant à déclarer. » ; bascule « Chaque mois | Chaque trimestre | Pas de rappel » (enregistrée au clic) → « Rappels activés : chaque trimestre. » / « Rappels arrêtés. » ; avec un choix et une période à déclarer : « Prochain rappel : 7 jours avant le 31/10/2026, puis la veille, pour 3e trimestre 2026. » La bascule « Par mois | Par trimestre » du tableau se cale sur ce choix.
