# Administration — Interface

> Fichiers : `frontend/src/pages/AdministrationPage.vue` (onglets et accès) et un fichier par onglet dans `frontend/src/components/admin/`. Construit au lot 1.4, onglets des métiers au lot 2.2 (28/09/2026). Règles : `RM-COMPTES.md`. Maquette : `maquette-lot-1.4-compte-administration.html`.

## Page « Administration » (`/administration`)
Entrée de menu visible seulement des administrateurs. **(pas administrateur, ou pas connecté)** carte « Réservé aux administrateurs » — « Cette page n'est accessible qu'aux administrateurs de rafals. » — bouton [Retour à l'accueil]. (Le serveur refuse de toute façon : 403.)

**Ordre des éléments :**
1. Titre « Administration ».
2. Onglets : « Accords à vérifier » · « Comptes » · « Propositions de métiers » · « Métiers ». Compteur orange du nombre en attente sur « Accords à vérifier » et « Propositions de métiers », mis à jour après chaque décision. L'onglet choisi est dans l'adresse (ex. `?onglet=metiers`).
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

## Onglet « Propositions de métiers » (lot 2.2)
Liste des propositions en attente, de la plus ancienne à la plus récente. Vide : « Aucune proposition de métier pour l'instant. »
Chaque ligne : « **« Cerf-voliste »** · proposé par Nadia Leroy · le 28/09/2026 à 19 h 12 » ; boutons :
- [Accepter…] (principal) → fenêtre « Accepter « Cerf-voliste » ? » : « Le métier sera créé et proposé à tous. », liste « Dossier où le ranger * » ; [Accepter] / [Annuler] → message vert « « Cerf-voliste » ajouté à la liste des métiers. »
- [Remplacer…] (secondaire) → fenêtre « Remplacer « Plombier chauffagiste » » : « par un métier qui existe déjà. Le nom proposé deviendra un de ses mots-clés. », choix d'un métier (sans les dossiers) ; [Remplacer] / [Annuler] → « Remplacé par « Plombier ». »
- [Refuser] (danger) → message vert « Proposition « … » refusée. »
Erreurs du serveur affichées dans la fenêtre (ex. « Choisissez le dossier où ranger ce nouveau métier. »).

## Onglet « Métiers » (lot 2.2)
1. Champ « Filtrer » (sans accents, sur le nom et les mots-clés) et, à droite, bouton principal [+ Nouveau métier].
2. Tableau (défile sur le côté sur téléphone), trié par nom. **Colonnes :** Métier · Dossier · Mots-clés (en petit) · État (badge « actif » / « désactivé ») · [Modifier].
3. « 12 métier(s) sur 128, triés par nom. Un métier ne se supprime jamais : on le désactive. »

**Fenêtre « Nouveau métier » :** Nom *, Dossier * ; [Créer] / [Annuler] → « Métier « Cordiste » créé. »
**Fenêtre « Modifier « Plombier » » :** Nom *, Dossier *, Mots-clés (séparés par des virgules), case « Actif (proposé pour les nouvelles annonces) » ; [Enregistrer] / [Annuler] → « Métier « Plombier » enregistré. »
