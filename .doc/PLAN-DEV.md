# rafals — Plan de développement

> Écrit le 28/09/2026 (phase 8 du démarrage). Le tableau des lots et leur état sont dans `SUIVI-DEV.md`.

## Principe
Ordre des dépendances, jamais ordre des écrans : du plus fondamental au plus spécifique. Serveur et écrans avancent ensemble : dès qu'une structure est prête, ses écrans se construisent.

## Pour chaque module
Règles validées → MLD validé → SQL → modèles → calculs (services) → routes → tests → écrans.

## Erreurs à ne jamais commettre
Écrans avant les règles ; base avant le MLD validé ; factures avant les objets qu'elles décrivent ; partie publique avant le moteur métier.

## Niveaux
**Niveau 0 — Amorçage** : conteneurs Docker (`db`, `backend`, `frontend`, `minio`), connexion à la base, squelette de tests, base de test séparée, squelette des écrans avec la charte (Vert sauge) et les composants communs.

**Niveau 1 — Fondations** : comptes et connexion (inscription par mail vérifié, mot de passe, 16 ans avec accord des parents, administrateurs), journal des actions. → `RM-COMPTES.md`

**Niveau 2 — Objets communs** : métiers et catégories (liste triée relue par Raphael) → `RM-METIERS.md` ; prestataires (profil, métier principal et secondaires, zone ville + km, SIRET vérifié automatiquement) → `RM-PRESTATAIRES.md` ; clients et données personnelles (adresse, téléchargement des données, fermeture de compte, comptes inactifs) → `RM-CLIENTS.md`.

**Niveau 3 — Cœur** : annonces (prix fixe / à l'heure / sur devis, durée, lieu, modes de paiement ; espèces seulement sans SIRET), agenda et disponibilités. → `RM-ANNONCES.md`, `RM-AGENDA.md` (validées le 29/09/2026) ; lots 3.1 à 3.4 dans `SUIVI-DEV.md`.

**Niveau 4 — Action principale** : recherche (métier + ville, classement), rendez-vous (réservation, annulation, absences), avis. → `RM-RECHERCHE.md`, `RM-RENDEZ-VOUS.md`, `RM-AVIS.md` (validées le 30/09/2026) ; lots 4.1 à 4.8 dans `SUIVI-DEV.md`.

**Niveau 5 — Argent** : devis, factures (numérotation, facture électronique / e-reporting), paiements par carte et commission. → règles à écrire : sujets 10, 11, 12. ⚠️ Avant ce niveau : vérification juridique des prestataires sans SIRET ; choix du service de paiement ; pourcentage de la commission.

**Niveau 6 — Services** : sites vitrines (reprise de vitrine-express, sous-domaines `*.rafals.fr`), aide à la création d'auto-entreprise, démarches administratives, administration de la plateforme. → règles à écrire : sujets 13 à 16.

Les niveaux 3 à 6 sont découpés en lots précis **après** l'écriture de leurs règles (juste avant de les construire).

## Transverses (tout au long du projet)
Sécurité, journal des actions, tests écrits à partir des règles, données personnelles (RGPD), 4 formats d'écran.

## Mise en ligne (étape 12 de la méthode)
Quand l'application tourne correctement en local : plan dans `technique/DEPLOIEMENT.md`, serveur d'essai puis production chez OVHcloud ; réserver `rafals.fr` avant.
