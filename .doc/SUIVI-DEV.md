# rafals — Suivi du développement

On avance lot par lot, dans l'ordre de `PLAN-DEV.md`. Un lot ne démarre que si ses dépendances sont ✅.

## Travail en cours (tenu à jour par Claude à chaque étape, vidé quand la tâche est finie)

- **Demande** : Lot 1.1 — Comptes : inscription, mail de vérification, connexion, rester connecté 30 jours, mot de passe oublié, blocage après 5 erreurs (Raphael : « je valide le lot 0.4 », suite du plan)
- **Commencé le** : 28/09/2026
- **Étapes** :
  - [ ] 1. MLD proposé à Raphael (Artifact) et validé  ← on en est là
  - [ ] 2. Plan du lot (boîte de mails de test, fichiers) validé
  - [ ] 3. `db/schema_v2.sql` exécuté avec l'accord de Raphael
  - [ ] 4. Modèles, calculs (`services/`), routes
  - [ ] 5. Tests (dont test de fiche du compte)
  - [ ] 6. Essais à la main, invariants, sauvegarde
- **Question en attente** : validation du MLD du lot 1.1 (https://claude.ai/artifact/Vcb7r3fXum38tJguPJmGYc, fichier `.doc/mld/MLD-lot-1.1-comptes.html`)
- **En pause** : aucune

## Définition de « terminé »

**Lot Serveur (7 cases)** : 1. SQL validé par Raphael · 2. Modèles · 3. Routes · 4. Tests automatiques OK · 5. Test de fiche (si fiche) · 6. Test à la main · 7. Sauvegarde git
**Lot Écrans (4 cases)** : 1. Écran selon CONVENTIONS-IHM et la charte · 2. Branché sur les vraies routes · 3. Test à la main sur 4 formats · 4. Sauvegarde git + `RM-<ECRAN>-IHM.md` à jour
**Tous les lots** : `INVARIANTS-TRANSVERSES.md` repassé.

Toutes les cases cochées → 🔎 à vérifier (jamais ✅ directement). ✅ seulement quand Raphael a vérifié et validé.

États : ⬜ à faire · 🟡 en cours · 🔎 à vérifier · ✅ fait

## Règle : une retouche compte aussi
Toute modification visible par l'utilisateur met à jour le `RM-<ECRAN>-IHM.md` dans la même sauvegarde git.

## Niveau 0 — Amorçage
| Lot | Type | Description | Règle source | Dépend de | État |
|---|---|---|---|---|---|
| 0.1 | Serveur | Conteneurs Docker (`db`, `backend`, `frontend` ; le « placard » à fichiers plus tard), fichier `.env` (mots de passe, jamais sur GitHub), `demarrer.bat`, `arreter.bat`, `sauver.bat` | CLAUDE.md | — | ✅ |
| 0.2 | Serveur | Connexion à la base avec les 2 comptes (`rafals_user`, `rafals_app`), adresse de contrôle `/health` | CLAUDE.md | 0.1 | ✅ |
| 0.3 | Serveur | Squelette de tests, base `rafals_test_db`, `lancer-tests.bat`, `nettoyer-donnees-test.bat`, `restaurer_base.bat` | CLAUDE.md, méthode étape 10 | 0.2 | ✅ |
| 0.4 | Écrans | Squelette Vue + Tailwind avec la charte Vert sauge, en-tête + menu ☰, composants `AppBouton`, `AppChamp`, `AppFenetre`, `AppBadge`, `AppMessage` | CHARTE-VISUELLE, CONVENTIONS-IHM | 0.1 | ✅ |

## Niveau 1 — Fondations
| Lot | Type | Description | Règle source | Dépend de | État |
|---|---|---|---|---|---|
| 1.1 | Serveur | Comptes : inscription, mail de vérification (conteneur de mails de test en local), connexion, rester connecté 30 jours, mot de passe oublié (lien 1 h), blocage après 5 erreurs | RM-COMPTES | 0.3 | 🟡 |
| 1.2 | Écrans | Pages Inscription, Connexion, Mot de passe oublié | RM-COMPTES | 1.1, 0.4 | ⬜ |
| 1.3 | Serveur | ⚠️ Avant de commencer : faire choisir à Raphael le « placard » à fichiers (Garage recommandé, ou RustFS ; MinIO abandonné), reporté 2 fois (« encore plus tard », 28/09/2026). Âge (16 ans) et accord des parents (document déposé), rôle administrateur (jamais retirer le dernier), journal des actions | RM-COMPTES | 1.1 | ⬜ |
| 1.4 | Écrans | Mon compte (premiers éléments, accord des parents) ; Administration : comptes et administrateurs | RM-COMPTES | 1.3, 1.2 | ⬜ |

## Niveau 2 — Objets communs
| Lot | Type | Description | Règle source | Dépend de | État |
|---|---|---|---|---|---|
| 2.1 | Serveur | Métiers et catégories : liste triée (relue par Raphael), mots-clés, recherche sans accents, propositions de métier | RM-METIERS | 1.3 | ⬜ |
| 2.2 | Écrans | Choix d'un métier (recherche par lettres, dossiers) ; Administration des métiers et des propositions | RM-METIERS | 2.1, 1.4 | ⬜ |
| 2.3 | Serveur | Profil prestataire : « Proposer mes services », métier principal et secondaires, ville + distance (liste officielle des communes avec coordonnées), pause / blocage / arrêt | RM-PRESTATAIRES | 2.1 | ⬜ |
| 2.4 | Serveur | Vérification automatique du SIRET (répertoire de l'État), « en attente » si panne | RM-PRESTATAIRES | 2.3 | ⬜ |
| 2.5 | Écrans | Proposer mes services / mon profil prestataire / SIRET ; Administration : prestataires, blocage | RM-PRESTATAIRES | 2.4, 2.2 | ⬜ |
| 2.6 | Serveur | Clients : adresse, « Télécharger mes données », « Fermer mon compte », comptes inactifs après 3 ans | RM-CLIENTS | 1.3 | ⬜ |
| 2.7 | Écrans | Mon compte : adresse, télécharger mes données, fermer mon compte | RM-CLIENTS | 2.6, 1.4 | ⬜ |

## Niveaux 3 à 6 — à découper après l'écriture de leurs règles
| Lot | Type | Description | Règle source | Dépend de | État |
|---|---|---|---|---|---|
| 3.0 | Règles | Écrire les règles des sujets 05 Annonces et 06 Agenda, puis découper le niveau 3 en lots | SUIVI_REGLES_METIER | 2.7 | ⬜ |
| 4.0 | Règles | Écrire les règles des sujets 07 Recherche, 08 Rendez-vous, 09 Avis, puis découper le niveau 4 | SUIVI_REGLES_METIER | niveau 3 | ⬜ |
| 5.0 | Règles | Vérification juridique (sans SIRET), choix du service de paiement, sujets 10 Devis, 11 Factures, 12 Paiements, puis découper le niveau 5 | SUIVI_REGLES_METIER | niveau 4 | ⬜ |
| 6.0 | Règles | Sujets 13 à 16 (sites vitrines, aide à la création, démarches, administration), puis découper le niveau 6 | SUIVI_REGLES_METIER | niveau 5 | ⬜ |

## Journal
- **28/09/2026** — Démarrage — Plan de développement écrit (phase 8). Décisions : niveaux 3 à 6 découpés plus tard, juste après l'écriture de leurs règles (méthode § 0.5, précision phase 6) ; mails de test en local par un conteneur dédié (détail au lot 1.1).
- **28/09/2026** — Démarrage terminé — Plan validé par Raphael. Pas de Notion : le suivi reste dans ce fichier. Prochain lot : 0.1.
- **28/09/2026** — Lot 0.1 — Boîtes `db` (PostgreSQL 18), `backend` (Python 3.13 + FastAPI), `frontend` (Node 24 + Vue + Vite) ; `.env` hors de git ; `demarrer.bat`, `arreter.bat`, `sauver.bat`. Essais : serveur et page répondent, `pg_dump` marche. Décisions : MinIO abandonné par son éditeur (12/2025) → boîte de stockage reportée au choix de Raphael (Garage ou RustFS), au plus tard avant le lot 1.3 ; la page lit le serveur via le relais `/api` de Vite (pas de réglage CORS). Invariants : architecture OK (aucune table ; outils standards seulement) ; sécurité, données, tests : sans objet à ce lot (tests au lot 0.3) ; interface : page provisoire, charte complète au lot 0.4 ; réutilisation OK ; documentation : `CLAUDE.md` = `REGLES-PROJET.md`, la ligne « minio » sera mise à jour au choix du stockage. Reste à noter : `package-lock.json` à générer au lot 0.4 pour figer les versions des écrans.
- **28/09/2026** — Lot 0.1 validé par Raphael (« je valide le lot 0.1 ») après essai de `demarrer.bat` → ✅. Lot 0.2 commencé.
- **28/09/2026** — Lot 0.2 — `db/schema_v1.sql` exécuté (compte `rafals_app` : lire/écrire les lignes, jamais créer de table ; droits par défaut sur les futures tables de `rafals_user`). Serveur branché avec SQLAlchemy 2 + psycopg 3, toujours avec `rafals_app`. `/health` répond 503 avec « base injoignable » si la base ne répond pas (au lieu de planter). Essais : `/health` OK ; création de table refusée. Invariants : architecture OK (aucune table, aucune création automatique) ; sécurité OK (compte application sans droit de structure) ; données, interface : sans objet ; tests : au lot 0.3 ; documentation : `CLAUDE.md` inchangé, identique à `REGLES-PROJET.md`. Remarque : la base de test `rafals_test_db` recevra les mêmes droits au lot 0.3.
- **28/09/2026** — Lot 0.2 validé par Raphael (« je valide le lot 0.2 ») → ✅. Lot 0.3 commencé.
- **28/09/2026** — Lot 0.3 — Base `rafals_test_db` effacée et recréée à chaque `lancer-tests.bat`, avec la structure de `rafals_db` (sans données). Garde-fou vérifié deux fois (réglages + base réelle). Tests : `test_sante.py` (2 tests OK). `nettoyer-donnees-test.bat` : sauvegarde puis classement protégée / marquée / douteuse, accord « OUI » avant effacement ; liste des marques à compléter à chaque nouvelle table. `restaurer_base.bat` : copie de sécurité, « OUI » obligatoire, recrée le compte `rafals_app` si absent (PC neuf). Décisions : `httpx` remplacé par `httpx2` (avertissement d'obsolescence de Starlette) ; copies de sécurité dans `db-sync/securite/`, ignorées par git (elles restent sur le PC). Invariants : architecture OK ; sécurité OK ; tests OK (base de test seule, garde-fou) ; données : vraie base 0 table, 0 donnée de test (comptage) ; interface : sans objet ; documentation : `CLAUDE.md` inchangé et identique à `REGLES-PROJET.md`.
- **28/09/2026** — Lot 0.3 validé par Raphael (« 2 passed » chez lui, puis « Oui, je valide ») → ✅. Lot 0.4 commencé.
- **28/09/2026** — Lot 0.4 — Tailwind 4 (couleurs de la charte dans `frontend/src/style.css`, seul endroit où une couleur est écrite ; mode sombre selon l'appareil), polices Bricolage Grotesque et Figtree installées dans rafals (pas chez Google, RGPD), vue-router, en-tête avec menu ☰ sous 768 px, 5 composants communs, pages Accueil (provisoire), Catalogue, Bientôt disponible. `package-lock.json` créé, `npm ci` dans l'image. Décisions : 2 couleurs techniques ajoutées à la charte (`sur-etat`, `voile`) pour ne jamais écrire « blanc » ou « noir » en dur ; `AppCarteResultat` reporté au niveau 4 (recherche) ; la page Catalogue sera retirée ou réservée aux administrateurs avant la mise en ligne. Avertissement npm : script d'installation d'esbuild non lancé (sans effet : construction OK). Invariants : interface OK (chaque clic → résultat visible, couleurs de la charte seulement, composants uniques, `RM-*-IHM.md` écrits) ; 4 formats : à vérifier par Raphael ; architecture, sécurité, données, tests : sans objet (aucune table, aucune route nouvelle) ; documentation : `CLAUDE.md` inchangé et identique à `REGLES-PROJET.md`.
- **28/09/2026** — Lot 0.4 validé par Raphael (« je valide le lot 0.4 ») → ✅. **Niveau 0 terminé.** Lot 1.1 commencé.
