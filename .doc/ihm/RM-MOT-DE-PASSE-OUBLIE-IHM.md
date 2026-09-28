# Mot de passe oublié — Interface

> Fichier : `frontend/src/pages/MotDePasseOubliePage.vue`. Construit au lot 1.2 (28/09/2026). Règles : `RM-COMPTES.md`.

## Page « Mot de passe oublié » (`/mot-de-passe-oublie`)
Carte centrée (460 px au maximum).

**Ordre des éléments :**
1. Titre « Mot de passe oublié », texte « Indiquez votre adresse : nous vous envoyons un lien pour en choisir un nouveau. »
2. Rubrique : Adresse mail *.
3. (erreur) bandeau rouge (ex. serveur injoignable).
4. (envoyé) bandeau vert « Si un compte existe avec cette adresse, un lien vient d'être envoyé (valable 1 heure). » — toujours le même texte, que l'adresse existe ou non.
5. Bouton principal [Recevoir un lien].
6. Bouton secondaire [Retour à la connexion] → `/connexion`.
