# Règle métier — Clients et données personnelles (sujet 03)

> Validé et formalisé le 28/09/2026 (phase 6 du démarrage).

## Objectif
Ce que rafals demande et garde sur les clients, qui peut le voir, et ce qui se passe quand un client ferme son compte (loi sur les données personnelles, RGPD).

## Principes
- Un seul compte par personne, client et/ou prestataire (voir `RM-COMPTES.md`).
- On ne demande et on ne garde que ce qui sert (règle du RGPD).

## Informations demandées (décidé le 28/09/2026)
- À l'inscription : prénom, nom, adresse mail, téléphone.
- L'adresse postale est demandée **seulement** au moment de réserver un service « chez le client », puis gardée pour les réservations suivantes (le client peut la modifier ou l'effacer).
- Exemple 1 : Mme Dupont réserve une coupe au salon de Léa → aucune adresse demandée.
- Exemple 2 : Mme Dupont réserve Karim pour une fuite → rafals demande « 8 allée des Pins, 33400 Talence » ; à sa réservation suivante chez Julie (ménage à domicile), l'adresse est déjà remplie.
**Pourquoi :** la loi demande de ne garder que les informations utiles.

## Avis d'un client qui ferme son compte : gardés sans son nom (décidé le 28/09/2026)
Quand un client ferme son compte, ses avis restent visibles, mais signés « Client ayant quitté rafals ». Plus rien ne permet de savoir qui les a écrits.
- Exemple : « ★★★★★ Mme Dupont : ponctuel et soigneux » sur la page de Karim devient « ★★★★★ Client ayant quitté rafals : ponctuel et soigneux ».
**Pourquoi :** Karim ne perd pas une note méritée à cause d'un départ qu'il ne contrôle pas.
**Cas limite tranché :** si le texte de l'avis contient lui-même le nom ou le téléphone du client, l'administrateur peut l'effacer du texte.

## Qui voit les informations d'un client (proposé par Claude, validé par Raphael le 28/09/2026)
- Le client voit et modifie toutes ses informations.
- Un prestataire voit le nom, le téléphone et (si besoin) l'adresse d'un client **seulement pour les rendez-vous pris avec lui**, et jusqu'à 3 mois après le dernier rendez-vous.
  - Ex. Mme Dupont réserve Karim le 16/10/2026 → Karim voit son téléphone et son adresse ; il ne les voit plus à partir du 16/01/2027 (sauf nouveau rendez-vous). Ses factures, elles, gardent le nom et l'adresse (obligation légale).
- L'administrateur voit tout, pour régler les problèmes.

## Télécharger ses données (proposé par Claude, validé par Raphael le 28/09/2026)
Un bouton « Télécharger mes données » donne au client un fichier avec tout ce que rafals sait sur lui (profil, rendez-vous, avis, factures). **Pourquoi :** c'est un droit prévu par la loi (droit d'accès).

## Fermer son compte (proposé par Claude, validé par Raphael le 28/09/2026)
- Le client clique « Fermer mon compte » et confirme. Son nom, son mail, son téléphone et son adresse sont effacés ; ses rendez-vous passés restent, sans son nom (pour les statistiques du prestataire).
- Exception légale : les **factures** gardent le nom et l'adresse du client pendant 10 ans (obligation comptable du prestataire).
- Refusé tant qu'il a un rendez-vous à venir : il doit d'abord l'annuler. Ex. Mme Dupont a un ménage prévu le 05/11 → « Annulez d'abord votre rendez-vous du 05/11 ».
- Si la personne est aussi prestataire en activité, elle doit d'abord arrêter son activité (voir `RM-PRESTATAIRES.md`).

## Comptes inactifs (proposé par Claude, validé par Raphael le 28/09/2026)
Un compte sans aucune connexion depuis 3 ans reçoit un mail « Votre compte sera fermé dans 30 jours sauf si vous vous connectez » ; sans réponse, il est fermé comme ci-dessus. **Pourquoi :** la loi interdit de garder des données personnelles sans limite de temps (3 ans est la durée conseillée par la CNIL, le gendarme français des données personnelles).
- Ex. dernière connexion le 10/01/2027 → mail le 10/01/2030 → fermeture le 09/02/2030.

## Qui peut faire quoi
| Action | Qui | Condition |
|---|---|---|
| Modifier ses informations | Le client | — |
| Voir le téléphone et l'adresse d'un client | Un prestataire | Rendez-vous avec lui, jusqu'à 3 mois après le dernier |
| Fermer son compte | Le client | Aucun rendez-vous à venir ; activité de prestataire arrêtée |
| Effacer un nom écrit dans un avis | Administrateur | — |

## Désactivation / clôture / suppression
- Désactiver : par l'administrateur (blocage, voir sujet 16).
- Clôturer : « Fermer mon compte » (définitif, données effacées sauf factures).
- Supprimer entièrement : interdit dès que le client a eu un rendez-vous ou une facture (on efface les données personnelles, on garde la trace sans nom).

## Valeurs figées
Le nom et l'adresse du client sont recopiés sur la facture au moment où elle est émise.

## Questions ouvertes
- (aucune)

## Références
- `GLOSSAIRE-METIER.md`, `RM-COMPTES.md`, `RM-PRESTATAIRES.md`
