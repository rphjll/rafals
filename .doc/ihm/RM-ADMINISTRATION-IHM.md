# Administration — Interface

> Fichiers : `frontend/src/pages/AdministrationPage.vue` (onglets, par le composant commun `AppOnglets` depuis le lot 3.4, et accès) et un fichier par onglet dans `frontend/src/components/admin/`. Construit au lot 1.4, onglets des métiers au lot 2.2 (28/09/2026). Règles : `RM-COMPTES.md`. Maquette : `maquette-lot-1.4-compte-administration.html`.

## Page « Administration » (`/administration`)
Entrée de menu visible seulement des administrateurs. **(pas administrateur, ou pas connecté)** carte « Réservé aux administrateurs » — « Cette page n'est accessible qu'aux administrateurs de rafals. » — bouton [Retour à l'accueil]. (Le serveur refuse de toute façon : 403.)

**Ordre des éléments :**
1. Titre « Administration ».
2. Onglets : « Accords à vérifier » · « Comptes » · « Prestataires » (lot 2.5) · « Absences contestées » (lot 4.6, compteur orange) · « Avis signalés » (lot 4.8, compteur orange) · « Tableau de bord » (lot 6.2, en premier, ouvert à l'arrivée) · « Paiements » (lot 6.2, en dernier) · « Mots interdits » (lot 4.8) · « Problèmes de devis » (lot 5.4, compteur orange) · « Propositions de métiers » · « Métiers ». Détail des onglets du lot 4.8 : `RM-AVIS-IHM.md`. Compteur orange du nombre en attente sur « Accords à vérifier » et « Propositions de métiers », mis à jour après chaque décision. L'onglet choisi est dans l'adresse (ex. `?onglet=metiers`).
3. (erreur de chargement) bandeau rouge.

## Onglet « Accords à vérifier » (par défaut)
Liste des accords en attente, **du plus ancien au plus récent**. Vide : « Aucun accord à vérifier pour l'instant. »
Chaque ligne : « **Prénom Nom** · 16 ans · envoyé le 28/09/2026 à 18 h 40 », nom du fichier dessous ; boutons, de gauche à droite :
- [Voir le fichier] (secondaire) → ouvre le fichier dans un nouvel onglet ;
- [Accepter] (principal) → message vert « Accord de Lucas Martin accepté. », la ligne disparaît ;
- [Refuser…] (danger) → fenêtre « Refuser l'accord de Lucas Martin ? » : « Le motif sera montré à Lucas, qui pourra en renvoyer un. », champ « Motif du refus * » (aide « Ex. « Signature illisible » »), erreur du serveur dans la fenêtre ; [Refuser] (danger) à gauche, [Annuler] à droite.

## Onglet « Comptes »
Tableau (défile sur le côté sur téléphone), trié par nom puis prénom.
**Colonnes, dans cet ordre :** Nom (« Dupont Marie ») · Adresse mail · Adresse (badge « vérifiée » / « non vérifiée ») · Rôle (badge « administrateur ») · bouton.
**Bouton :** [Nommer administrateur] (secondaire) ou [Retirer le rôle] (danger) → fenêtre de confirmation (« Nommer Marie Dupont administrateur ? » / « Retirer le rôle d'administrateur à Tom Durand ? »), [Nommer]/[Retirer] à gauche, [Annuler] à droite. Refus du serveur affiché dans la fenêtre, ex. « Il doit toujours rester au moins un administrateur. » Si l'on retire son propre rôle, le menu perd l'entrée « Administration ».
**Compte fermé (lot 2.7) :** il reste dans la liste sous le nom « fermé Compte », adresse `compte-ferme-12@rafals.invalid`, badge gris « fermé » dans la colonne Rôle, **aucun bouton** (le serveur refuse aussi : « Ce compte est fermé : il ne peut pas devenir administrateur. »).

## Onglet « Propositions de métiers » (lot 2.2)
Liste des propositions en attente, de la plus ancienne à la plus récente. Vide : « Aucune proposition de métier pour l'instant. »
Chaque ligne : « **« Cerf-voliste »** · proposé par Nadia Leroy · le 28/09/2026 à 19 h 12 » ; boutons :
- [Accepter…] (principal) → fenêtre « Accepter « Cerf-voliste » ? » : « Le métier sera créé et proposé à tous. », liste « Dossier où le ranger * » ; [Accepter] / [Annuler] → message vert « « Cerf-voliste » ajouté à la liste des métiers. »
- [Remplacer…] (secondaire) → fenêtre « Remplacer « Plombier chauffagiste » » : « par un métier qui existe déjà. Le nom proposé deviendra un de ses mots-clés. », choix d'un métier (sans les dossiers) ; [Remplacer] / [Annuler] → « Remplacé par « Plombier ». »
- [Refuser] (danger) → message vert « Proposition « … » refusée. »
Erreurs du serveur affichées dans la fenêtre (ex. « Choisissez le dossier où ranger ce nouveau métier. »).

## Onglet « Métiers » (lot 2.2)
1. Champ « Filtrer » (sans accents, sur le nom et les mots-clés), case « Montrer les désactivés » (décochée : les métiers désactivés sont cachés ; ajoutée le 28/09/2026) et, à droite, bouton principal [+ Nouveau métier].
2. Tableau (défile sur le côté sur téléphone), trié par nom. **Colonnes :** Métier · Dossier · Mots-clés (en petit) · État (badge « actif » / « désactivé ») · boutons [Modifier] (secondaire) et [Désactiver] (danger) ou [Réactiver] (secondaire) → message vert « « Cordiste » désactivé : il n'est plus proposé. » / « … réactivé : il est de nouveau proposé. » (bouton visible ajouté le 28/09/2026 à la demande de Raphael : la case « Actif » cachée dans « Modifier » n'était pas trouvable).
3. « 12 métier(s) affiché(s) sur 128, triés par nom. Un métier ne se supprime jamais : on le désactive (il disparaît pour tout le monde, et d'ici tant que « Montrer les désactivés » n'est pas coché). »

**Fenêtre « Nouveau métier » :** Nom *, Dossier * ; [Créer] / [Annuler] → « Métier « Cordiste » créé. »
**Fenêtre « Modifier « Plombier » » :** Nom *, Dossier *, Mots-clés (séparés par des virgules) ; [Enregistrer] / [Annuler] → « Métier « Plombier » enregistré. »

## Onglet « Prestataires » (lot 2.5)
Tableau (défile sur le côté sur téléphone), du plus récent au plus ancien. Vide : « Aucun prestataire pour l'instant. »
**Colonnes :** Prestataire (nom affiché) · Métier (principal) · Ville · SIRET (badge : « SIRET vérifié », « À vérifier », « SIRET refusé », « Sans SIRET ») · État (badge : actif, en pause, bloqué, arrêté) · Compte (adresse mail) · boutons.
**Boutons :**
- [Valider le SIRET] (secondaire), seulement si le SIRET est « à vérifier » ou « refusé » → « SIRET de « … » validé à la main. » (à faire après avoir vu un justificatif) ;
- [Bloquer…] (danger) → fenêtre « Bloquer « … » ? » : « Il disparaît des recherches et ne peut plus rien changer. Vous seul pourrez le débloquer. » ; [Bloquer] / [Annuler] → « « … » est bloqué. » ;
- [Débloquer] (secondaire) si bloqué → « « … » est débloqué : il est de nouveau actif. » ;
- aucun bouton de blocage pour un prestataire arrêté.
Texte sous le tableau : « Du plus récent au plus ancien. « Valider le SIRET » : seulement après avoir vu un justificatif (avis de situation INSEE). »

## Onglet « Absences contestées » (lot 4.6)
Une carte par contestation à trancher, la plus ancienne d'abord : titre « Dépannage fuite · 13/10/2026 à 10 h 00 » + badge « à trancher » ; deux encadrés côte à côte (l'un sous l'autre sur téléphone) : « **Marie Dupont (client)** a signalé : « Karim Benali n'est pas venu ». » et « **Karim Benali (prestataire)** a contesté le 14/10/2026 à 9 h 12 : « … » » ; [L'absence compte] (danger) / [Elle ne compte pas] → « Décision enregistrée : l'absence compte. Les deux sont prévenus. » Vide : « Aucune absence contestée. »
Plus bas, carte « Annulations de dernière minute (6 mois) » : « Rendez-vous annulés par le prestataire moins de 24 h avant. », une ligne par prestataire (lien vers sa page) · nombre, les plus nombreux d'abord ; vide : « Aucune. »

## Onglet « Problèmes de devis » (lot 5.4, 03/10/2026)
Fichier : `frontend/src/components/admin/OngletProblemesDevis.vue`. Une carte par problème non traité : « D-2026-0001 · Terrasse en bois » + badge orange « problème » ; Client, Prestataire, Signalé le « 02/10/2026 à 9 h 12 » ; bandeau « « Le muret penche de 5 cm » » ; « Contactez le client et le prestataire (téléphones dans « Comptes »), puis : » [Marquer comme traité] → « Problème traité. » Vide : « Aucun problème signalé. »

## Onglets « Tableau de bord » et « Paiements » (lot 6.2, 03/10/2026 ; maquette `maquette-lot-6.2-services.html` à valider)
Fichiers : `frontend/src/components/admin/OngletTableauDeBord.vue`, `OngletTousLesPaiements.vue`, composant commun `ui/AppChiffre.vue`. Règles : `RM-ADMINISTRATION.md`.
- **Tableau de bord** (premier onglet, ouvert à l'arrivée ; les autres gardent `?onglet=…`) : carte « À traiter » — un bouton secondaire par onglet où quelque chose attend (« 2 accords à vérifier », « 1 absence contestée », « 1 avis signalé », « 1 problème de devis », « 3 propositions de métiers »), le clic ouvre l'onglet ; rien : « Rien à traiter pour l'instant. » Carte « Octobre 2026 » — chiffres : Nouveaux comptes · Rendez-vous pris · Paiements par carte (« 14 », dessous « 812,00 € ») · Commission de rafals (« 40,60 € », « 5 % des paiements ») · Remboursements ; puis « En ce moment » : Prestataires actifs · Annonces en ligne ; « Depuis le 1er du mois. Les paiements comptés sont ceux gardés (ni abandonnés, ni remboursés). »
- **Paiements** (`?onglet=paiements`) : tableau (défile sur le côté), le plus récent d'abord, 30 par page : Payé le · Quoi (« Coupe femme — mardi 13/10/2026 à 10 h 00 », dessous « Léa Martin · Paul Petit ») · Montant · Commission (« — » si le paiement n'est pas gardé) · État (gris « page de paiement ouverte » / « jamais payé », orange « payé (bloqué) », vert « versé », rouge « remboursé 120,00 € ») ; [← Plus récents] « Page 1 sur 3 · 74 paiements » [Plus anciens →] ; « Lecture seule : les remboursements et les versements sont automatiques. » ; vide : « Aucun paiement par carte pour l'instant. »
