# rafals — Suivi de l'écriture des règles métier

À lire en premier avant toute discussion sur une règle.

## Méthode
1. Un sujet à la fois, par questions / réponses (une question à la fois pour Raphael).
2. Sujet validé → écrit dans `regles-metier/RM-<SUJET>.md` (et `ihm/RM-<SUJET>-IHM.md` si besoin).
3. Tout brouillon venu d'une autre IA est un point de départ à interroger, jamais une décision.
4. Pour le plan (phase 8), il faut les règles **validées** des niveaux 1 et 2 ; les autres sujets sont traités plus tard, juste avant leurs lots.

## Statuts
à faire · à vérifier ou compléter · validé et formalisé

## Avancement (liste validée par Raphael le 27/09/2026)
| # | Niveau | Sujet | Ce que ça couvre | Statut | Fichier produit |
|---|---|---|---|---|---|
| 01 | 1 — Fondations | Comptes et connexion | Inscription, connexion, mot de passe oublié, un seul compte client + prestataire, rôle administrateur | validé et formalisé (27/09/2026) | `regles-metier/RM-COMPTES.md` |
| 02 | 2 — Objets communs | Prestataires | Profil, SIRET, « en création », visibilité, désactivation | en cours (27/09/2026) | `regles-metier/RM-PRESTATAIRES.md` |
| 03 | 2 — Objets communs | Clients et données personnelles | Profil du particulier, ce qu'on garde, effacement (RGPD) | à faire | — |
| 04 | 2 — Objets communs | Métiers et catégories | La grande liste, les dossiers, la recherche par lettres | à faire | — |
| 05 | 3 — Cœur | Annonces | Contenu, prix, ville, modes de paiement (espèces seulement sans SIRET) | à faire | — |
| 06 | 3 — Cœur | Agenda et disponibilités | Horaires, congés, créneaux libres | à faire | — |
| 07 | 4 — Action principale | Recherche | Métier + ville, ordre des résultats | à faire | — |
| 08 | 4 — Action principale | Rendez-vous | Réservation, confirmation, annulation, absence | à faire | — |
| 09 | 4 — Action principale | Avis | Qui note, quand, modération | à faire | — |
| 10 | 5 — Argent | Devis | Création, acceptation, passage en facture | à faire | — |
| 11 | 5 — Argent | Factures | Numérotation, mentions obligatoires, facture électronique / e-reporting | à faire | — |
| 12 | 5 — Argent | Paiements et commission | Carte sur le site, espèces, pourcentage de rafals, remboursements | à faire | — |
| 13 | 6 — Services | Sites vitrines | Modèles (vitrine-express), sous-domaine, prix (abonnement ou à vie) | à faire | — |
| 14 | 6 — Services | Aide à la création d'auto-entreprise | Parcours de Karim jusqu'au SIRET | à faire | — |
| 15 | 6 — Services | Démarches administratives | Déclarations URSSAF, rappels, automatisation | à faire | — |
| 16 | 6 — Services | Administration de la plateforme | Validation des prestataires, litiges, signalements | à faire | — |

## Décisions en attente
- ⚠️ Prestataires sans SIRET payés en espèces : à faire vérifier juridiquement (sujets 02, 05, 12).
- Prix du site vitrine et pourcentage de la commission (sujets 12, 13).
