# Administration — Interface

> Fichier : `frontend/src/pages/AdministrationPage.vue`. Construit au lot 1.4 (28/09/2026). Règles : `RM-COMPTES.md`. Maquette : `maquette-lot-1.4-compte-administration.html`.

## Page « Administration » (`/administration`)
Entrée de menu visible seulement des administrateurs. **(pas administrateur, ou pas connecté)** carte « Réservé aux administrateurs » — « Cette page n'est accessible qu'aux administrateurs de rafals. » — bouton [Retour à l'accueil]. (Le serveur refuse de toute façon : 403.)

**Ordre des éléments :**
1. Titre « Administration ».
2. Onglets : « Accords à vérifier » (avec un compteur orange du nombre en attente) · « Comptes ». L'onglet choisi est dans l'adresse (`?onglet=comptes`).
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
