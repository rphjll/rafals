# Nouveau mot de passe — Interface

> Fichier : `frontend/src/pages/NouveauMotDePassePage.vue`. Construit au lot 1.2 (28/09/2026). Règles : `RM-COMPTES.md`.

## Page ouverte par le lien du mail « mot de passe oublié » (`/nouveau-mot-de-passe?jeton=…`)
Carte centrée (460 px au maximum).

**Ordre des éléments :**
1. Titre « Nouveau mot de passe ».
2. Rubriques : Nouveau mot de passe * (aide « Au moins 10 caractères. »), Le même, encore une fois *.
3. (erreur) bandeau rouge : « Les deux mots de passe ne sont pas identiques. » (vérifié par l'écran avant l'envoi), ou le message du serveur (trop court, lien expiré, déjà utilisé).
4. Bouton principal [Enregistrer le nouveau mot de passe] (inactif pendant l'envoi) → `/connexion` + message vert « Votre mot de passe est changé. Vous pouvez vous connecter. » Tous les appareils sont déconnectés, celui-ci aussi.
5. Bouton secondaire [Mon lien a expiré : en demander un autre] → `/mot-de-passe-oublie`.
