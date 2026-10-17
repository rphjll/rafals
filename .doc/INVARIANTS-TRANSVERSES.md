# rafals — Invariants transverses (à vérifier à la fin de CHAQUE lot)

Pour chaque point : respecté, ou pourquoi il ne s'applique pas.

## 1. Architecture
- [ ] SQL écrit dans un `schema_v*.sql` validé avant tout code ; jamais de création automatique des tables.
- [ ] Modèles = miroir des colonnes ; calculs dans `services/`.
- [ ] Ordre respecté : MLD → SQL → modèles → routes → tests.
- [ ] Portabilité : aucun service propre à OVH (seulement Docker, PostgreSQL, stockage S3).

## 2. Sécurité
- [ ] Chaque route vérifie qui est connecté.
- [ ] Chaque action sensible vérifie le rôle (client, prestataire, administrateur).
- [ ] Chaque modification importante est inscrite au journal des actions (qui, quoi, quand, avant/après).
- [ ] Un prestataire ne voit que ses propres propositions, rendez-vous, clients et factures ; un client ne voit que les siens (annonces supprimées au lot 9.4).

## 3. Données
- [ ] Les valeurs contractuelles (prix, commission, nom et SIRET du prestataire, nom et adresse du client) sont figées au moment où elles engagent.
- [ ] Aucun taux, délai ou texte légal écrit en dur (réglages).
- [ ] Dates enregistrées en temps universel (UTC), affichées à l'heure de Paris.
- [ ] Données personnelles : seulement ce qui sert ; coordonnées d'un client visibles par un prestataire seulement selon `RM-CLIENTS.md`.

## 4. Tests
- [ ] Tests écrits à partir des règles `RM-*` et au vert.
- [ ] Test de fiche à jour si une fiche est touchée.
- [ ] Aucune donnée de test restante dans la vraie base (vérifié par comptage).

## 5. Interface
- [ ] Chaque clic produit un résultat visible, à l'endroit du clic.
- [ ] Vérifié sur 4 formats d'écran.
- [ ] Couleurs et formes prises dans la charte, jamais tapées à la main.
- [ ] `RM-<ECRAN>-IHM.md` à jour.

## 6. Réutilisation
- [ ] Aucune logique ni aucun style recopié : ce qui apparaît 2 fois est regroupé.

## 7. Documentation
- [ ] Les règles écrites correspondent à ce que fait le code.
- [ ] `CLAUDE.md` et `.doc/REGLES-PROJET.md` identiques.
