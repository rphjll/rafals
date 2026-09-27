# Règle métier — Comptes et connexion (sujet 01)

> En cours d'écriture (phase 6 du démarrage). Chaque règle est validée par Raphael au fil des questions.

## Objectif
Comment on crée un compte sur rafals, comment on se connecte, et qui a quels droits (client, prestataire, administrateur).

## Principes
- Un seul compte par personne, qu'elle soit cliente, prestataire, ou les deux (voir `GLOSSAIRE-METIER.md`, décidé le 27/09/2026).

## Inscription par adresse mail et mot de passe (décidé le 27/09/2026)
On s'inscrit avec son adresse mail et un mot de passe. rafals envoie un mail avec un lien à cliquer, pour prouver que l'adresse appartient bien à la personne. Tant que le lien n'est pas cliqué, le compte ne peut rien réserver ni publier.
- Exemple 1 : Mme Dupont s'inscrit avec `dupont.marie@gmail.com` le 27/09 à 20 h, clique sur le lien reçu à 20 h 02 → compte utilisable.
- Exemple 2 : Karim s'inscrit avec `karim.plomb@gmial.com` (faute de frappe) → il ne reçoit jamais le mail, le compte reste inutilisable ; il peut se réinscrire avec la bonne adresse.
**Pourquoi :** sans adresse vérifiée, impossible d'envoyer les confirmations de rendez-vous, les factures ou le lien « mot de passe oublié ».
Pas de bouton « Continuer avec Google » pour commencer (pourra s'ajouter plus tard).

## Même inscription pour tous, puis « Proposer mes services » (décidé le 27/09/2026)
Tout le monde s'inscrit de la même façon. Un compte neuf est un compte **client**. Pour devenir prestataire, on clique dans son compte sur « Proposer mes services » et on remplit son profil de prestataire (métier, ville, SIRET s'il en a un). Le compte reste aussi client.
- Exemple 1 : Mme Dupont s'inscrit, réserve un ménage ; elle ne voit jamais les écrans prestataire.
- Exemple 2 : Julie s'inscrit, clique « Proposer mes services », choisit « Femme de ménage », « Nantes », SIRET 912 345 678 00014 → elle devient prestataire, et peut toujours réserver un plombier comme cliente.
**Pourquoi :** une seule porte d'entrée, plus simple ; et un client peut devenir prestataire plus tard sans rien recréer.

## Questions ouvertes
- Âge minimum.
- Qui est administrateur.

## Références
- `GLOSSAIRE-METIER.md`, `PRESENTATION.md`
