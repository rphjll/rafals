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
| 05 | 3 — Cœur | Annonces | Contenu, prix, ville, modes de paiement (espèces seulement sans SIRET) | validé et formalisé (29/09/2026) ; **annonces retirées par Raphael le 04/10/2026** (pas encore construit) : remplacées par `RM-PRESTATAIRES.md` § « Sans annonces » | `regles-metier/RM-ANNONCES.md` |
| 06 | 3 — Cœur | Agenda et disponibilités | Horaires, congés, créneaux libres | validé et formalisé (29/09/2026), modifié le 03/10/2026 (un calendrier par métier, ouvertures exceptionnelles) | `regles-metier/RM-AGENDA.md` |
| 07 | 4 — Action principale | Recherche | Métier + ville, ordre des résultats | validé et formalisé (30/09/2026) | `regles-metier/RM-RECHERCHE.md` |
| 08 | 4 — Action principale | Rendez-vous | Réservation, confirmation, annulation, absence | validé et formalisé (30/09/2026) | `regles-metier/RM-RENDEZ-VOUS.md` |
| 09 | 4 — Action principale | Avis | Qui note, quand, modération | validé et formalisé (30/09/2026) | `regles-metier/RM-AVIS.md` |
| 10 | 5 — Argent | Devis | Création, acceptation, passage en facture | validé et formalisé (02/10/2026) | `regles-metier/RM-DEVIS.md` |
| 11 | 5 — Argent | Factures | Numérotation, mentions obligatoires, facture électronique / e-reporting | validé et formalisé (02/10/2026) | `regles-metier/RM-FACTURES.md` |
| 12 | 5 — Argent | Paiements et commission | Carte sur le site, espèces, pourcentage de rafals, remboursements | validé et formalisé (02/10/2026) | `regles-metier/RM-PAIEMENTS.md` |
| 13 | 6 — Services | Sites vitrines | Modèles (vitrine-express), sous-domaine, prix (abonnement ou à vie) | rédigé, **reporté par Raphael le 04/10/2026** (pas construit pour l'instant) | `regles-metier/RM-SITES-VITRINES.md` |
| 14 | 6 — Services | Aide à la création d'auto-entreprise | Parcours de Karim jusqu'au SIRET | validé et formalisé (04/10/2026) | `regles-metier/RM-CREATION-AUTO-ENTREPRISE.md` |
| 15 | 6 — Services | Démarches administratives | Déclarations URSSAF, rappels, automatisation | validé et formalisé (04/10/2026) | `regles-metier/RM-DEMARCHES.md` |
| 16 | 6 — Services | Administration de la plateforme | Validation des prestataires, litiges, signalements | validé et formalisé (04/10/2026) | `regles-metier/RM-ADMINISTRATION.md` |
| 17 | 8 — Comme AlloVoisins | Demandes publiées par les clients | Le client écrit son besoin (« Tondre ma pelouse samedi à Pessac, 40 € »), les prestataires du coin répondent | validé et formalisé (04/10/2026) | `regles-metier/RM-DEMANDES.md` |
| 18 | 8 — Comme AlloVoisins | Alertes des prestataires | Prévenir un prestataire dès qu'une demande de son métier est publiée près de chez lui | validé et formalisé (04/10/2026) | `regles-metier/RM-ALERTES.md` |
| 19 | 8 — Comme AlloVoisins | Messagerie | Messages privés entre un client et un prestataire | validé et formalisé (04/10/2026) | `regles-metier/RM-MESSAGERIE.md` |
| 20 | 8 — Comme AlloVoisins | Notation dans les deux sens | Le prestataire note aussi le client | validé et formalisé (04/10/2026) | `regles-metier/RM-AVIS.md` (section « Notation dans les deux sens ») |
| 21 | 8 — Comme AlloVoisins | Application à installer | rafals sur l'écran d'accueil du téléphone, avec les notifications | validé et formalisé (04/10/2026) | `regles-metier/RM-APPLICATION.md` |

## Décisions en attente
- ⚠️ Prestataires sans SIRET payés en espèces : à faire vérifier juridiquement (sujets 02, 05, 12).
- Prix du site vitrine et pourcentage de la commission (sujets 12, 13).
