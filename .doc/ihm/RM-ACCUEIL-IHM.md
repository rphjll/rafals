# Accueil et « Bientôt disponible » — Interface

> Fichiers : `frontend/src/pages/AccueilPage.vue`, `frontend/src/pages/BientotPage.vue`, `frontend/src/router.ts`. Construit au lot 0.4 (28/09/2026).
> **Refait le 04/10/2026** (nouvelle présentation, maquette https://claude.ai/artifact/8GvhAaZ5x1m7Kyv1dLMQb3) : la recherche et les dossiers de métiers sont sur l'accueil.

## Page Accueil (`/`)
**Ordre des éléments, de haut en bas :**

0. (connecté, adresse pas encore vérifiée) bandeau orange « Vérifiez votre adresse mail pour pouvoir réserver. » avec un bouton secondaire [Renvoyer le lien] → message vert « Si un compte non vérifié existe… ».
1. **Bandeau vert foncé** (`fonce`) :
   1. Titre « Le bon prestataire, près de chez vous. » ; « près de chez vous. » en vert vif (`fonce-vif`). 32 à 54 px selon l'écran.
   2. Texte « Ménage, jardinage, plomberie, coiffure à domicile : réservez un créneau en quelques clics, ou demandez un devis. »
   3. Carte blanche de recherche, de gauche à droite : « Quel service ? » (choix d'un métier par les premières lettres), « Où ? » (choix d'une commune), bouton orange [Rechercher] (variante `accent`).
      - Les deux choisis → page « Trouver un prestataire » avec les résultats (`/trouver?metier=…&ville=…`).
      - Il manque le métier : « Choisissez un métier. » ; il manque la ville : « Choisissez votre ville. », sous les champs.
   4. (personne n'est connecté) bouton secondaire [Créer mon compte] → `/inscription`.
2. **« De quoi avez-vous besoin ? »** : une tuile par dossier de métiers (les vrais dossiers de la base), avec le nom du dossier et ses 3 premiers métiers. Couleurs dans l'ordre : orange, vert, jaune, bleu, rose, violet, puis on recommence.
   - Clic sur une tuile → les tuiles laissent la place aux métiers du dossier (un bouton par métier), avec [← Tous les dossiers].
   - Clic sur un métier → si la ville est déjà choisie, la recherche part ; sinon la page remonte en haut, le métier est rempli dans « Quel service ? » et un message dit « « Jardinage » choisi : indiquez votre ville. ».
   - Si les dossiers ne se chargent pas, ce bloc n'est pas affiché.
3. **« Comment ça marche »** : 3 cartes numérotées — 1 Cherchez, 2 Réservez, 3 Payez et donnez votre avis.
4. **Bandeau orange** (`accent-vif`), caché pour un prestataire : « Vous proposez vos services ? », texte, boutons [Proposer mes services] → `/proposer` et [Créer mon auto-entreprise] → `/creer-mon-auto-entreprise`, et 3 atouts cochés.
5. Ligne pour le développement, sous un trait : badge d'état du serveur (lit `/api/etat` : neutre « Vérification du serveur… », vert « Le serveur de rafals répond. », rouge « Le serveur ne répond pas. Relance demarrer.bat. ») et bouton secondaire [Voir le catalogue des composants] → `/catalogue`.

Pas encore fait (prévu dans la maquette) : la liste « Près de chez vous » (il faut connaître la ville du visiteur).

## Page « Bientôt disponible »
Utilisée pour toute adresse inconnue.

| Adresse | Titre | Texte |
|---|---|---|
| toute adresse inconnue | Page introuvable | Cette adresse ne correspond à aucune page de rafals. |

Puis un bouton principal [Retour à l'accueil].
