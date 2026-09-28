# Vérifier l'adresse — Interface

> Fichier : `frontend/src/pages/VerifierAdressePage.vue`. Construit au lot 1.2 (28/09/2026). Règles : `RM-COMPTES.md`.

## Page ouverte par le lien du mail de vérification (`/verifier-adresse?jeton=…`)
La page vérifie toute seule à l'ouverture, sans rien demander. Carte centrée.

**États :**
1. (chargement) titre « Vérification de votre adresse… »
2. (réussi) titre « Adresse vérifiée », bandeau vert « Votre adresse mail est vérifiée. », bouton principal [Se connecter] → `/connexion`. Si la personne était déjà connectée, le bandeau orange de l'accueil disparaît.
3. (échec) titre « Ce lien ne marche pas », bandeau rouge avec le message du serveur (« Ce lien a expiré. Demandez-en un nouveau. », « Ce lien a déjà été utilisé. Demandez-en un nouveau. », « Ce lien n'est pas valide… »), puis rubrique Adresse mail * et bouton principal [Recevoir un nouveau lien] → message vert « Si un compte non vérifié existe avec cette adresse, un nouveau lien vient d'être envoyé. »

**Limite connue :** recharger la page après une vérification réussie affiche « Ce lien a déjà été utilisé » (le lien ne sert qu'une fois).
