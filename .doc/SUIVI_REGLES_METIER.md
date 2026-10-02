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
| 02 | 2 — Objets communs | Prestataires | Profil, SIRET, « en création », visibilité, désactivation | validé et formalisé (28/09/2026) | `regles-metier/RM-PRESTATAIRES.md` |
| 03 | 2 — Objets communs | Clients et données personnelles | Profil du particulier, ce qu'on garde, effacement (RGPD) | validé et formalisé (28/09/2026) | `regles-metier/RM-CLIENTS.md` |
| 04 | 2 — Objets communs | Métiers et catégories | La grande liste, les dossiers, la recherche par lettres | validé et formalisé (28/09/2026) | `regles-metier/RM-METIERS.md` |
| 05 | 3 — Cœur | Annonces | Contenu, prix, ville, modes de paiement (espèces seulement sans SIRET) | validé et formalisé (29/09/2026) | `regles-metier/RM-ANNONCES.md` |
| 06 | 3 — Cœur | Agenda et disponibilités | Horaires, congés, créneaux libres | validé et formalisé (29/09/2026) | `regles-metier/RM-AGENDA.md` |
| 07 | 4 — Action principale | Recherche | Métier + ville, ordre des résultats | validé et formalisé (30/09/2026) | `regles-metier/RM-RECHERCHE.md` |
| 08 | 4 — Action principale | Rendez-vous | Réservation, confirmation, annulation, absence | validé et formalisé (30/09/2026) | `regles-metier/RM-RENDEZ-VOUS.md` |
| 09 | 4 — Action principale | Avis | Qui note, quand, modération | validé et formalisé (30/09/2026) | `regles-metier/RM-AVIS.md` |
| 10 | 5 — Argent | Devis | Création, acceptation, passage en facture | validé et formalisé (02/10/2026) | `regles-metier/RM-DEVIS.md` |
| 11 | 5 — Argent | Factures | Numérotation, mentions obligatoires, facture électronique / e-reporting | validé et formalisé (02/10/2026) | `regles-metier/RM-FACTURES.md` |
| 12 | 5 — Argent | Paiements et commission | Carte sur le site, espèces, pourcentage de rafals, remboursements | validé et formalisé (02/10/2026) | `regles-metier/RM-PAIEMENTS.md` |
| 13 | 6 — Services | Sites vitrines | Modèles (vitrine-express), sous-domaine, prix (abonnement ou à vie) | à faire | — |
| 14 | 6 — Services | Aide à la création d'auto-entreprise | Parcours de Karim jusqu'au SIRET | à faire | — |
| 15 | 6 — Services | Démarches administratives | Déclarations URSSAF, rappels, automatisation | à faire | — |
| 16 | 6 — Services | Administration de la plateforme | Validation des prestataires, litiges, signalements | à faire | — |

## Décisions en attente
- ⚠️ Prestataires sans SIRET payés en espèces : à faire vérifier juridiquement (sujets 02, 05, 12).
- Prix du site vitrine et pourcentage de la commission (sujets 12, 13).
