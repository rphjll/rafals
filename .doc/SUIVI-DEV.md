# rafals — Suivi du développement

On avance lot par lot, dans l'ordre de `PLAN-DEV.md`. Un lot ne démarre que si ses dépendances sont ✅.

## Travail en cours (tenu à jour par Claude à chaque étape, vidé quand la tâche est finie)

- (aucun)

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
| 0.1 | Serveur | Conteneurs Docker (`db`, `backend`, `frontend`, `minio`), fichier `.env` (mots de passe, jamais sur GitHub), `demarrer.bat`, `arreter.bat`, `sauver.bat` | CLAUDE.md | — | ⬜ |
| 0.2 | Serveur | Connexion à la base avec les 2 comptes (`rafals_user`, `rafals_app`), adresse de contrôle `/health` | CLAUDE.md | 0.1 | ⬜ |
| 0.3 | Serveur | Squelette de tests, base `rafals_test_db`, `lancer-tests.bat`, `nettoyer-donnees-test.bat`, `restaurer_base.bat` | CLAUDE.md, méthode étape 10 | 0.2 | ⬜ |
| 0.4 | Écrans | Squelette Vue + Tailwind avec la charte Vert sauge, en-tête + menu ☰, composants `AppBouton`, `AppChamp`, `AppFenetre`, `AppBadge`, `AppMessage` | CHARTE-VISUELLE, CONVENTIONS-IHM | 0.1 | ⬜ |

## Niveau 1 — Fondations
| Lot | Type | Description | Règle source | Dépend de | État |
|---|---|---|---|---|---|
| 1.1 | Serveur | Comptes : inscription, mail de vérification (conteneur de mails de test en local), connexion, rester connecté 30 jours, mot de passe oublié (lien 1 h), blocage après 5 erreurs | RM-COMPTES | 0.3 | ⬜ |
| 1.2 | Écrans | Pages Inscription, Connexion, Mot de passe oublié | RM-COMPTES | 1.1, 0.4 | ⬜ |
| 1.3 | Serveur | Âge (16 ans) et accord des parents (document déposé), rôle administrateur (jamais retirer le dernier), journal des actions | RM-COMPTES | 1.1 | ⬜ |
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
