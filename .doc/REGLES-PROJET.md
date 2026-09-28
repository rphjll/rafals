# rafals — Consignes pour Claude Code

> Ce fichier est dupliqué dans `.doc/REGLES-PROJET.md`. Toute modification ici est recopiée là-bas dans la même sauvegarde git.

## Démarrage du projet (à lire en premier, à chaque conversation)

Si `.doc/DEMARRAGE.md` existe et n'est pas marqué « Démarrage terminé » : le projet est en phase de démarrage. Lis `methode-projet.md` (partie 0) puis `.doc/DEMARRAGE.md`, et reprends à la question en attente ou à la prochaine action notée, quel que soit le premier message du développeur. Après chaque réponse, écris-la aussitôt dans le fichier concerné et dans `.doc/DEMARRAGE.md`.

## Langue et clarté (RÈGLE STRICTE)

- Réponds toujours en français simple, y compris dans les questions à choix, les titres et les messages de sauvegarde git.
- Un terme technique incontournable s'écrit d'abord en français, puis en anglais entre parenthèses avec une courte explication la première fois (ex. « enregistrer une sauvegarde dans git (un *commit*) »).
- Au moins 2 exemples concrets, avec de vraies valeurs, pour toute notion un peu abstraite.
- Changement d'infrastructure (Docker, base, configuration) : détail fichier par fichier, ligne avant / ligne après, et dire quels fichiers ne changent pas.
- Pendant le travail : 1 ou 2 lignes d'information au maximum. Le détail complet vient à la fin.
- Réponds à toutes mes questions avant de m'en poser une nouvelle.

## Questions (RÈGLE STRICTE)

- Une question se comprend sans relire le reste du message : situation concrète, vrais noms et vrais numéros.
- Sous forme de choix, avec pour chaque réponse ce qui se passera concrètement.
- Une seule décision par question.
- Si tu n'as pas compris une de mes phrases, cite-la mot pour mot et dis ce que tu n'y trouves pas.

## Qui utilise ce projet

Raphael, débutant en programmation. Explique le « pourquoi » de chaque choix technique. Raphael garde la main sur la structure de la base et sur tout ce qui touche à ses données ou à son ordinateur.

## Outils

- Serveur : Python + FastAPI
- Écrans : Vue 3 + TypeScript + Vite + Tailwind CSS, composants faits main
- Base : PostgreSQL, pilote psycopg version 3, SQLAlchemy 2
- Fichiers : Garage en local, stockage S3 d'OVH en ligne (MinIO abandonné par son éditeur en 2025)
- Tout tourne dans Docker : conteneurs `db`, `backend`, `frontend`, `mailpit` (mails de test), `garage` (fichiers)
- Ports côté PC : serveur 8001, écrans 5174, base 5433, mails de test 8025
- Hébergement prévu : OVHcloud, France (détail et portabilité : `.doc/technique/HEBERGEMENT.md`)
- Les fichiers `.bat` s'écrivent sans aucun accent ni tiret long.

## Base de données

- Base principale : `rafals_db` ; base des tests : `rafals_test_db` (même conteneur)
- Compte administrateur : `rafals_user` / `<mot de passe, fixé au lot 0.1>` (création des tables, inspection)
- Compte application : `rafals_app` / `<mot de passe, fixé au lot 0.1>` (serveur et tests ; aucun droit de créer une table)

## Ordre imposé à chaque évolution de données

1. Proposer un MLD (jamais de SQL à ce stade) et attendre ma validation.
2. Écrire `schema_v<N>.sql` (jamais modifié une fois exécuté ; une correction = le numéro suivant).
3. Mettre à jour les modèles : miroir pur des colonnes, aucun calcul.
4. Calculs dans `services/`, puis schémas et routes, puis tests.
Jamais de création automatique des tables par le code.

## Format du MLD (RÈGLE STRICTE)

Artifact HTML avec un schéma Mermaid `flowchart` sur fond blanc uni. Nom de table en MAJUSCULES ; dans les boîtes, seulement `id (PK)` et `xxx_id (FK)` ; autres rubriques listées à côté. Flèches avec cardinalités Merise `(1,1)` `(0,1)` `(0,n)` `(1,n)`. Une légende. Au moins 2 exemples de vraies lignes traduits en français. Si je demande le « MLD complet », toutes les rubriques dans les boîtes.

## Données de test (RÈGLE STRICTE)

- Tests lancés uniquement par `lancer-tests.bat`, sur `rafals_test_db`, avec le compte `rafals_app`. Les tests refusent de démarrer sur une autre base.
- Données saisies à la main dans l'application : marquées dès la création (`@example.com`, `ZZTEST `, `ZZ-`), nettoyées par `nettoyer-donnees-test.bat`.
- Un script Playwright ne touche que les lignes qu'il a créées et marquées.
- Jamais de suppression d'une donnée existante ou ambiguë sans mon accord explicite.
- Fin de tâche : vérifier par un comptage qu'il ne reste aucune donnée de test.
- Mot de passe des comptes de test : `123`.

## Tests de fiche

Chaque fiche a son test dans `backend/tests/fiches/test_fiche_<nom>.py` : ajout → modification → fiches liées (suppression de la fiche principale refusée tant qu'un lien existe) → suppression. Rubriques lues automatiquement, jamais listées à la main.

## Interface

Lire `.doc/technique/CONVENTIONS-IHM.md` et `CHARTE-VISUELLE.md` avant tout écran. Chaque écran a son `.doc/ihm/RM-<ECRAN>-IHM.md`, mis à jour dans la même sauvegarde que toute retouche visible. Maquettes en Artifact cliquable, après relecture des composants existants.

## Réutilisation

Dès la 2ᵉ apparition d'une même logique ou d'un même style, la regrouper à un seul endroit.

## Suivi

- `.doc/SUIVI-DEV.md` (pas de Notion, décidé le 28/09/2026) : états ⬜ à faire / 🟡 en cours / 🔎 à vérifier / ✅ fait.
- Claude met « à vérifier », jamais « fait ». Seul Raphael passe un lot à « fait ». Sans validation explicite, lui demander.
- Fin de chaque lot : repasser `.doc/INVARIANTS-TRANSVERSES.md`.
- Règles métier : lire `.doc/SUIVI_REGLES_METIER.md` avant de répondre sur une règle.

## Mots-clés

- **« continuer » / « reprends »** : dans l'ordre, et s'arrêter à la première qui s'applique : 1) une tâche inachevée dans cette conversation → la finir ; 2) la rubrique « Travail en cours » de `.doc/SUIVI-DEV.md` n'est pas vide → la reprendre ; 3) démarrage non terminé → reprendre `.doc/DEMARRAGE.md` ; 4) sinon, dire où on en est et proposer le prochain lot. En cas de doute entre deux possibilités, me demander avec 2 choix (détail : `methode-projet.md` § 0.8).
- **« Travail en cours »** (en haut de `.doc/SUIVI-DEV.md`) : rempli dès qu'une tâche dépasse une action (lot ou retouche hors lot), mis à jour à chaque étape, vidé une fois la tâche finie et sauvegardée.
- **« tout seul »** : pour la tâche demandée, aucune question en cours de route. Décider selon les règles, noter chaque décision dans le journal de `SUIVI-DEV.md`, aller jusqu'au bout (lot à « à vérifier »), puis faire un bilan avec les questions restantes. Exception : ne jamais supprimer une donnée ambiguë.
- **« dodo »** : relire le code, vérifier que les règles écrites correspondent au code et corriger les écarts, lancer tous les tests, mettre à jour le suivi, sauvegarder dans git et envoyer sur GitHub, sans poser de question.

## Façon de travailler

Étape par étape, une action à la fois. Expliquer le pourquoi. Diagnostiquer avant de conclure (quel compte est connecté, la demande est-elle arrivée au serveur).
