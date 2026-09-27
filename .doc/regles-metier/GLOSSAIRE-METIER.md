# rafals — Glossaire métier

Un mot = une définition = un seul sens dans tout le projet. Ce fichier ne décrit pas les tables : un objet peut s'étendre sur plusieurs tables.

> Phase 4 du démarrage : définitions **proposées par Claude le 27/09/2026, en cours de validation** par Raphael. Les points marqués « question en attente » ne sont pas tranchés.

## Les grands objets
Prestataire, Client, Prestation, Rendez-vous, Facture, Paiement, Site vitrine, Démarche administrative.
Liste de départ : d'autres objets seront ajoutés (voir `PRESENTATION.md`).

## Prestataire
Personne ou société qui propose des services aux clients via rafals : un auto-entrepreneur (ex. Julie Martin, ménage à domicile) ou une société (ex. « Plomberie Martin SARL »). Il a des Prestations, un agenda de Rendez-vous, émet des Factures, peut avoir un Site vitrine et suivre des Démarches administratives.
Exemple : Julie Martin, auto-entrepreneuse à Nantes, propose « Ménage 2 h — 50 € » et « Repassage 1 h — 20 € ».
À ne pas confondre avec : **Client** (celui qui achète le service). Question en attente : un même compte peut-il être les deux ? Une société peut-elle avoir plusieurs intervenants ? Un futur auto-entrepreneur est-il déjà un Prestataire ?

## Client
Particulier qui cherche un prestataire, prend rendez-vous et paie une prestation. Il a des Rendez-vous, reçoit des Factures, fait des Paiements.
Exemple : Mme Dupont, Nantes, prend rendez-vous avec Julie Martin le mardi 14/10 à 9 h.
À ne pas confondre avec : **Prestataire**.

## Prestation
Un service qu'un Prestataire propose, avec un nom, une durée, un prix et les modes de paiement qu'il accepte pour ce service. Appartient à un seul Prestataire.
Exemple 1 : « Ménage 2 h — 50 € — paiement en ligne, espèces ou chèque » (Julie Martin).
Exemple 2 : « Repassage 1 h — 20 € — espèces ou chèque seulement » (Julie Martin).
À ne pas confondre avec : **Rendez-vous** (la prestation réalisée pour un client à une date donnée).

## Rendez-vous
Un créneau dans l'agenda d'un Prestataire, réservé par un Client pour une Prestation.
Exemple : « Mme Dupont — Ménage 2 h — mardi 14/10/2026 de 9 h à 11 h — chez Julie Martin ».
À ne pas confondre avec : **Prestation** (le service proposé, sans date ni client).

## Facture
Document émis par un Prestataire à un Client pour une ou plusieurs prestations réalisées, avec un numéro qui se suit sans trou.
Exemple : « F-2026-0012 — Julie Martin → Mme Dupont — Ménage 2 h du 14/10/2026 — 50 € ».
À ne pas confondre avec : **Paiement** (l'argent reçu ; une facture peut être payée en plusieurs fois, ou pas encore payée).

## Paiement
Somme versée par un Client à un Prestataire pour une Facture ou un Rendez-vous, avec son mode (en ligne, espèces, chèque, virement…). En ligne, l'argent passe par un service de paiement agréé et va directement au Prestataire : rafals ne le garde jamais.
Exemple : « 50 € — carte bancaire en ligne — 14/10/2026 — facture F-2026-0012 ».
À ne pas confondre avec : **Facture**.

## Site vitrine
Site internet d'un Prestataire, créé à partir d'un modèle (repris de vitrine-express) et publié sur un sous-domaine de rafals.
Exemple : « julie-menage.rafals.fr », modèle « Classique », style bleu.
À ne pas confondre avec : la **page profil** du prestataire dans les résultats de recherche de rafals.

## Démarche administrative
Une tâche administrative qu'un Prestataire (ou futur auto-entrepreneur) doit faire, que rafals l'aide à préparer ou fait à sa place quand c'est autorisé.
Exemple 1 : « Déclaration URSSAF du chiffre d'affaires de septembre 2026 — à faire avant le 31/10/2026 ».
Exemple 2 : « Création de l'auto-entreprise de Karim — étape 2 sur 5 : choix de l'activité ».

## Cycle de vie (valable pour tous les objets)
- **Désactiver** : réversible (ex. Julie met en pause sa prestation « Repassage » pendant l'été).
- **Clôturer** : définitif (ex. un rendez-vous passé et payé).
- **Supprimer** : interdit dès que l'objet a servi (ex. une prestation qui a déjà eu un rendez-vous ne se supprime pas, elle se désactive).
