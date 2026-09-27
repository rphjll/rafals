# Règle métier — Comptes et connexion (sujet 01)

> Phase 6 du démarrage. Règles « décidé le » : validées par Raphael. Règles « proposé par Claude » : à valider à la relecture.

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

## Âge minimum : 16 ans, avec l'accord des parents avant 18 ans (décidé le 27/09/2026)
On peut créer un compte dès 16 ans. Entre 16 et 18 ans, il faut l'accord écrit des parents, vérifié avant que le compte puisse réserver ou publier. Moins de 16 ans : inscription refusée.
- Exemple 1 : Lucas, 16 ans, veut proposer du soutien scolaire → il s'inscrit, envoie l'accord signé de ses parents ; tant que l'accord n'est pas vérifié, il ne peut rien publier.
- Exemple 2 : Emma, 15 ans → inscription refusée.
- Exemple 3 : Mme Dupont, 54 ans → aucune démarche en plus.
**Pourquoi :** un mineur ne peut pas signer seul un contrat ni payer seul ; devenir auto-entrepreneur avant 18 ans demande une autorisation des parents.

## Administrateurs (décidé le 27/09/2026)
Au départ, Raphael est le seul administrateur. Il pourra donner ce rôle à d'autres personnes plus tard depuis son compte (Raphael : « je vais peut etre ajouter quelques potes mais ca je suis pas sur »), et le leur retirer.
- Exemple 1 : à la mise en ligne, seul le compte de Raphael voit l'écran « Administration ».
- Exemple 2 : en 2027, Raphael nomme son ami Tom administrateur → Tom voit l'écran « Administration » ; Raphael peut le lui retirer à tout moment.
**Cas limite tranché :** il reste toujours au moins un administrateur ; on ne peut pas retirer le rôle au dernier.

## Mot de passe (proposé par Claude, à valider à la relecture)
- Au moins 10 caractères. Ex. `soleil` est refusé ; `MaisonBleue44` est accepté.
- Mot de passe oublié : on tape son adresse mail, rafals envoie un lien valable 1 heure pour en choisir un nouveau. Ex. lien envoyé à 14 h 00, cliqué à 15 h 10 → expiré, il faut en redemander un.
- Après 5 mauvais mots de passe de suite, la connexion est bloquée 15 minutes. **Pourquoi :** empêche un pirate d'essayer des milliers de mots de passe.
- Le mot de passe n'est jamais stocké en clair : même l'administrateur ne peut pas le lire.

## Rester connecté (proposé par Claude, à valider à la relecture)
On reste connecté 30 jours sur son appareil, sauf si on clique « Se déconnecter ». Ex. Julie se connecte sur son téléphone le 01/10 ; le 20/10 elle ouvre rafals → toujours connectée.

## Qui peut faire quoi
| Action | Qui | Condition |
|---|---|---|
| Créer un compte | Toute personne | 16 ans ou plus ; accord des parents vérifié avant 18 ans pour réserver ou publier |
| Réserver | Titulaire d'un compte | Adresse mail vérifiée |
| Devenir prestataire (« Proposer mes services ») | Titulaire d'un compte | Adresse mail vérifiée |
| Nommer ou retirer un administrateur | Administrateur | Jamais retirer le dernier |

## Désactivation / clôture / suppression
- Désactiver un compte (réversible) : l'administrateur peut bloquer un compte (ex. faux prestataire). Détail dans le sujet 16.
- Fermer son compte et effacer ses données : traité dans le sujet 03 « Clients et données personnelles ».

## Valeurs figées
Aucune pour ce sujet.

## Questions ouvertes
- Comment l'accord des parents est envoyé et vérifié (document déposé puis contrôlé par l'administrateur ?) — à trancher avec le sujet 16 « Administration ».

## Références
- `GLOSSAIRE-METIER.md`, `PRESENTATION.md`
