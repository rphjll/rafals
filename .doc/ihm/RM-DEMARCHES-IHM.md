# Mes démarches — Interface

> Fichiers : `frontend/src/pages/DemarchesPage.vue`. Construit au lot 6.2 (03/10/2026, pendant l'absence de Raphael : maquette `maquette-lot-6.2-services.html` **à valider**). Règles : `RM-DEMARCHES.md`.

## Page « Mes démarches » (`/demarches`, menu « Mes démarches », seulement pour un prestataire)
Même gardien que « Mes annonces » (se connecter / proposer ses services). Contenu centré, 720 px au plus. Titre « Mes démarches ».

**Sans SIRET vérifié** : carte « Déclaration à l'URSSAF » — « Les démarches concernent les prestataires avec un SIRET vérifié : sans lui, rafals ne fait pas de facture. » + [Créer mon auto-entreprise] → la création d'auto-entreprise par rafals (lot 7.2).

**Avec un SIRET vérifié**, carte « Déclaration à l'URSSAF » :
1. « Un auto-entrepreneur déclare à l'URSSAF ce qu'il a encaissé, chaque mois ou chaque trimestre, même 0 €. rafals prépare le chiffre d'après vos factures ; la déclaration se fait sur le site de l'URSSAF. »
2. Bandeau orange, s'il y a une période finie dont la date limite n'est pas passée : « À déclarer pour septembre 2026 : **1 250,00 €**, avant le 31/10/2026. »
3. [Aller sur le site de l'URSSAF] (principal) : ouvre autoentrepreneur.urssaf.fr dans un nouvel onglet.
4. Bascules « Par mois | Par trimestre » et, à partir de 2027, l'année (« 2026 | 2027 »).
5. Tableau (défile sur le côté sur téléphone), la période la plus récente d'abord, seulement les périodes commencées : Période (« Octobre 2026 », « 3e trimestre 2026 ») · Encaissé (« 1 250,00 € », « (HT) » si TVA) · Factures (le nombre) · À déclarer avant le (« 30/11/2026 ») · badge gris « en cours », orange « à déclarer », ou « date passée ».
6. « Seulement ce qui est passé par rafals : ajoutez ce que vous avez encaissé ailleurs. La commission de rafals et les frais de paiement ne se déduisent pas. » (+ « Vous facturez la TVA : les montants sont hors taxe. »)

## Carte « Rappels par mail » (lot 6.4, 04/10/2026 ; maquette validée `maquette-lot-6.4-signalements-rappels.html`)
Sous la carte « Déclaration à l'URSSAF », seulement avec un SIRET vérifié : « Dites à rafals comment vous déclarez à l'URSSAF : vous recevrez un mail 7 jours avant la date limite, puis la veille, avec le montant à déclarer. » ; bascule « Chaque mois | Chaque trimestre | Pas de rappel » (enregistrée au clic) → « Rappels activés : chaque trimestre. » / « Rappels arrêtés. » ; avec un choix et une période à déclarer : « Prochain rappel : 7 jours avant le 31/10/2026, puis la veille, pour 3e trimestre 2026. » La bascule « Par mois | Par trimestre » du tableau se cale sur ce choix.

## Déclarer d'un clic depuis rafals (lot 7.3, 04/10/2026 ; maquette validée `maquette-lot-7.3-declarer-urssaf.html`)
Fichier : `frontend/src/components/demarches/DeclarerUrssaf.vue`, dans la carte « Déclaration à l'URSSAF » à la place du seul bouton [Aller sur le site de l'URSSAF]. Le texte du haut devient : « … vous déclarez sur le site de l'URSSAF, ou d'un clic depuis rafals. »
- **Sans accord** : encadré gris « Déclarer d'un clic depuis rafals » — « Donnez votre accord une fois : rafals enverra ensuite vos déclarations à l'URSSAF quand vous cliquerez sur [Déclarer]. Rien ne part sans votre clic. » ; « Vous gardez votre espace sur le site de l'URSSAF… » ; [Donner mon accord…] et [Aller sur le site de l'URSSAF].
  - Fenêtre « Donner mon accord à rafals ? » : « Numéro de sécurité sociale * » (« L'URSSAF le demande pour vous reconnaître… rafals l'efface si vous retirez votre accord. ») ; case « Je donne mandat à rafals pour déclarer mon chiffre d'affaires à l'URSSAF… » ; [Donner mon accord] verrouillé 🔒 tant que la case n'est pas cochée → « Accord enregistré. » Erreurs dans la fenêtre (ex. « L'URSSAF n'a pas accepté : « Cotisant inconnu. » Si vous n'avez pas encore d'espace sur autoentrepreneur.urssaf.fr, créez-le d'abord. »).
- **Avec accord** : badge vert « accord donné le 04/10/2026 » + lien rouge « Retirer mon accord… » ; [Déclarer à l'URSSAF…] s'il y a une période à déclarer (verrouillé 🔒 tant que « chaque mois / chaque trimestre » n'est pas choisi dans « Rappels par mail ») ; [Aller sur le site de l'URSSAF]. Sans période : « Rien à déclarer depuis rafals pour le moment : la dernière période est déjà déclarée, ou sa date limite est passée. »
  - Fenêtre « Déclarer le 3e trimestre 2026 ? » : « Encaissé sur rafals : 1 250,00 € (12 factures) » ; « Encaissé ailleurs que sur rafals (en euros) » (0 au départ) ; bandeau gris « Total déclaré : 1 450,00 € / Cotisations estimées par l'URSSAF : 307,40 € » (mis à jour pendant la frappe) ; case « Je certifie que ce montant est exact. » ; « À déclarer avant le 31/10/2026. Une période déclarée ne se corrige plus depuis rafals. » ; [Envoyer à l'URSSAF] verrouillé 🔒 sans la case → « Déclaration envoyée à l'URSSAF. »
  - Fenêtre « Retirer mon accord ? » : « rafals ne pourra plus envoyer vos déclarations… Les déclarations déjà envoyées restent valables. » ; [Retirer mon accord] (danger) → « Accord retiré. »
- **Période déclarée** : le bandeau orange « À déclarer… » devient un bandeau vert « 3e trimestre 2026 déclaré le 24/10/2026 : 1 450,00 €. Cotisations à payer à l'URSSAF : 307,40 €. » + « rafals a déclaré, il n'a pas payé… Pour corriger cette déclaration, passez aussi par le site de l'URSSAF. » ; dans le tableau, badge vert « déclaré : 1 450,00 € ».
- **Refus de l'URSSAF** : bandeau rouge dans la fenêtre, puis dans la carte : « L'URSSAF n'a pas accepté la déclaration : « La période est déjà déclarée. » Rien n'a été envoyé. Vérifiez sur autoentrepreneur.urssaf.fr. » ; panne : « L'URSSAF ne répond pas : réessayez dans quelques minutes. Rien n'est envoyé deux fois. »
- **Mode démonstration** (avant la mise en ligne) : bandeau orange « Mode démonstration : rafals n'est pas encore branché à l'URSSAF. Rien n'est envoyé ; déclarez aussi sur le site de l'URSSAF. » ; les cotisations sont « estimées par rafals ».
