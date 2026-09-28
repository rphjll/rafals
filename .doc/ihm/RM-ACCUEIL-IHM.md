# Accueil (provisoire) et « Bientôt disponible » — Interface

> Fichiers : `frontend/src/pages/AccueilPage.vue`, `frontend/src/pages/BientotPage.vue`, `frontend/src/router.ts`. Construit au lot 0.4 (28/09/2026). L'accueil définitif (recherche métier + ville, dossiers de métiers) arrive au niveau 4.

## Page Accueil (`/`)
**Ordre des éléments :**
1. Titre « Le bon prestataire, près de chez vous. » (police des titres, 28 à 42 px selon l'écran).
2. Texte « Plombiers, femmes de ménage, coiffeuses à domicile… rafals est en construction : la recherche arrive bientôt. »
3. Badge d'état du serveur (lit `/api/etat`) :
   - (chargement) badge neutre « Vérification du serveur… »
   - (OK) badge vert avec le message du serveur « Le serveur de rafals répond. »
   - (erreur) badge rouge « Le serveur ne répond pas. Relance demarrer.bat. »
4. Bouton secondaire [Voir le catalogue des composants] → `/catalogue`.

## Page « Bientôt disponible »
Utilisée par les entrées du menu pas encore construites, et pour toute adresse inconnue.

| Adresse | Titre | Texte |
|---|---|---|
| `/trouver` | Trouver un prestataire | Cette page arrive avec la recherche (niveau 4). |
| `/proposer` | Proposer mes services | Cette page arrive au lot 2.5. |
| `/rendez-vous` | Mes rendez-vous | Cette page arrive avec les rendez-vous (niveau 4). |
| `/compte` | Mon compte | Cette page arrive aux lots 1.2 et 1.4. |
| toute autre adresse | Page introuvable | Cette adresse ne correspond à aucune page de rafals. |

Puis un bouton principal [Retour à l'accueil].
