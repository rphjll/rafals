# Inscription — Interface

> Fichier : `frontend/src/pages/InscriptionPage.vue`. Construit au lot 1.2 (28/09/2026). Règles : `RM-COMPTES.md`. Maquette : `maquette-lot-1.2-comptes.html`.

## Page « Créer mon compte » (`/inscription`)
Carte centrée (460 px au maximum).

**Ordre des éléments :**
1. Titre « Créer mon compte », texte « Pour réserver un prestataire, ou proposer vos services. »
2. Rubriques, dans cet ordre (* = obligatoire) :
   1. Prénom * et Nom * (côte à côte sur ordinateur, l'un sous l'autre sur téléphone)
   2. Adresse mail *
   3. Téléphone * — aide « Visible seulement des prestataires chez qui vous réservez. »
   4. Date de naissance * (calendrier du navigateur) — aide « Il faut avoir au moins 16 ans. »
   5. Mot de passe * — aide « Au moins 10 caractères (ex. MaisonBleue44). »
3. (erreur) bandeau rouge avec le message du serveur, juste au-dessus du bouton. Ex. « Un compte existe déjà avec cette adresse mail. », « Il faut avoir au moins 16 ans pour créer un compte sur rafals. »
4. Bouton principal [Créer mon compte] (grisé et inactif pendant l'envoi).
5. Séparateur « déjà inscrit ? », puis bouton secondaire [Se connecter] → `/connexion`.

## État « Vérifiez votre boîte mail » (après une inscription réussie)
1. Titre « Vérifiez votre boîte mail ».
2. « Un lien vient d'être envoyé à **adresse**. Cliquez dessus pour finir votre inscription (il est valable 7 jours). »
3. Bandeau orange « Tant que votre adresse n'est pas vérifiée, vous pouvez vous connecter, mais pas réserver ni publier. »
4. Bouton principal [Se connecter] → `/connexion`.
5. Bouton secondaire [Je n'ai rien reçu : renvoyer le lien] → message vert « Si un compte non vérifié existe avec cette adresse, un nouveau lien vient d'être envoyé. »
