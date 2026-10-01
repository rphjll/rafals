# Règle métier — Avis (sujet 09)

> Validé et formalisé le 30/09/2026 (lot 4.0).

## Objectif
Qui note un prestataire, quand, ce qui est montré, et ce qu'on fait d'un avis qui pose problème.

## Déjà décidé (glossaire, sujets 03 et 07)
- Un avis = une **note de 1 à 5 ★** et un **petit texte**, laissé par un client **après un vrai rendez-vous** (ce qui évite les faux avis).
- Un client qui ferme son compte : ses avis restent, signés « Client ayant quitté rafals » ; l'administrateur peut effacer un nom écrit dans le texte (`RM-CLIENTS.md`).
- Les avis servent au classement de la recherche (note pondérée, badge « Nouveau » sans avis : `RM-RECHERCHE.md`).

## 30 jours pour laisser un avis, avec un rappel (décidé le 30/09/2026)
Le lendemain du rendez-vous, le client reçoit « Comment s'est passé votre rendez-vous avec Karim ? » ; il peut noter pendant 30 jours après le rendez-vous.
- Exemple : rendez-vous mardi 14/10 → mail le 15/10 → avis possible jusqu'au 13/11.
**Pourquoi :** un avis doit parler d'un souvenir frais.

## Le prestataire répond publiquement (décidé le 30/09/2026)
Le prestataire peut écrire **une seule réponse** par avis, affichée dessous ; il ne peut pas changer la note.
- Exemple : « ★★ En retard d'une heure » → réponse de Karim : « Bouchon sur la rocade, j'avais prévenu par SMS. »

## Filtre de gros mots à l'envoi (décidé le 30/09/2026)
rafals refuse dès l'envoi un avis (ou une réponse du prestataire) qui contient un mot d'une liste de gros mots ; l'auteur doit le réécrire. La liste est modifiable par l'administrateur, sans toucher au code.
- Exemple : « Karim est un [gros mot] » → « Votre avis contient un mot interdit : reformulez-le, s'il vous plaît. »

## Signaler un avis : l'administrateur décide (décidé le 30/09/2026)
En plus du filtre, le prestataire peut cliquer [Signaler cet avis] avec une raison (fausse accusation, coordonnées personnelles…). L'avis reste affiché pendant l'examen ; l'administrateur le laisse, ou le **cache** (sa note ne compte plus) avec un motif envoyé au client. Rien n'est effacé.
- Exemple : « Karim m'a volé un bijou » → Karim signale → l'administrateur demande des preuves, puis cache l'avis : « Accusation grave sans élément : avis caché. »

## Nom affiché : prénom et initiale (décidé le 30/09/2026)
- Exemple : Marie Dupont → « ★★★★★ Marie D., octobre 2026 : ponctuel et soigneux ». (Compte fermé : « Client ayant quitté rafals ».)
**Pourquoi :** l'avis a l'air vrai, sans permettre de retrouver la personne (données personnelles).

## Précisions proposées par Claude (validées par Raphael le 30/09/2026)
- **Un avis par rendez-vous tenu** (pas pour un rendez-vous annulé, expiré, refusé ou marqué absent) ; un client qui revient 3 fois peut laisser 3 avis.
- **Modifier son avis** : possible pendant les 30 jours ; ensuite il est figé. Le client peut le **retirer** à tout moment (il est caché, pas effacé).
- **Texte** : de 10 à 1000 caractères ; la note seule ne suffit pas.
- **Où** : sur la page publique du prestataire (les plus récents d'abord) et, en résumé, dans les résultats de recherche (« 4,5 ★ · 8 avis ») ; la note moyenne compte tous les avis du prestataire, tous métiers confondus.
- La **liste des gros mots** de départ est écrite par Claude et relue par Raphael avant la mise en ligne.

## Précisions prises au lot 4.7 (proposées par Claude, à valider par Raphael)
- **Filtre** : un mot interdit compte seulement s'il est entier, sans tenir compte des accents ni des majuscules (« Connard » refusé ; « conserve », « concours » acceptés). Il s'applique aussi à la réponse du prestataire. Liste de départ : 50 injures courantes (`backend/app/donnees/mots_interdits.json`, `charger-mots-interdits.bat`), **à relire par Raphael avant la mise en ligne**.
- **Pas d'avis** sur un rendez-vous où une absence a été signalée.
- **Signaler** : une fois par avis, avec une raison d'au moins 5 caractères ; l'administrateur le **laisse** (le signalement est traité) ou le **cache** avec un motif d'au moins 5 caractères envoyé au client.
- **Réponse du prestataire** : de 2 à 1000 caractères.
- **Note affichée** : moyenne des avis visibles (ni retirés, ni cachés) ; un avis modifié, retiré ou caché change aussitôt la note et le classement de la recherche.
- **Rappel** : le lendemain du rendez-vous, à partir de 10 h, une seule fois, s'il n'y a pas encore d'avis ni d'absence.
- Les avis d'un prestataire se voient seulement si sa page publique est visible (activité active).

## Qui peut faire quoi
| Action | Qui | Condition |
|---|---|---|
| Laisser, modifier un avis | Client | Rendez-vous tenu, dans les 30 jours |
| Retirer son avis | Client | À tout moment |
| Répondre une fois | Prestataire | Sur un avis le concernant |
| Signaler un avis | Prestataire | Sur un avis le concernant |
| Cacher un avis, modifier la liste des gros mots, effacer un nom dans un texte | Administrateur | — |

## Questions ouvertes
- (aucune)

## Références
- `GLOSSAIRE-METIER.md`, `RM-CLIENTS.md`, `RM-RECHERCHE.md`, `RM-RENDEZ-VOUS.md`
