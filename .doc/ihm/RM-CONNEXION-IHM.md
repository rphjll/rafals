# Connexion — Interface

> Fichier : `frontend/src/pages/ConnexionPage.vue`. Construit au lot 1.2 (28/09/2026). Règles : `RM-COMPTES.md`.

## Page « Se connecter » (`/connexion`)
Carte centrée (460 px au maximum).

**Ordre des éléments :**
1. Titre « Se connecter ».
2. Rubriques : Adresse mail *, Mot de passe *.
3. (erreur) bandeau rouge avec le message du serveur, juste au-dessus du bouton :
   - « Adresse mail ou mot de passe incorrect. » (adresse inconnue ou mauvais mot de passe : même message)
   - « 5 erreurs de suite : connexion bloquée jusqu'à 14 h 15. » puis « Trop d'erreurs de mot de passe : réessayez après 14 h 15. »
4. Bouton principal [Se connecter] (inactif pendant l'envoi) → accueil + message vert « Bonjour Marie ! ».
5. Bouton secondaire [Mot de passe oublié ?] → `/mot-de-passe-oublie`.
6. Séparateur « pas encore de compte ? », puis bouton secondaire [Créer mon compte] → `/inscription`.

## Retour à la page d'avant (lot 4.4)
Une page peut envoyer à `/connexion?retour=/annonces/12` : après la connexion, on revient sur cette page (seulement une page de rafals, jamais un autre site) ; sinon l'accueil.
