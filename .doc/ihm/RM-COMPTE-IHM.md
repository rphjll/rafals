# Mon compte — Interface

> Fichiers : `frontend/src/pages/ComptePage.vue`, `frontend/src/components/ui/AppChampFichier.vue`. Construit au lot 1.4 (28/09/2026). Règles : `RM-COMPTES.md`. Maquette : `maquette-lot-1.4-compte-administration.html`.

## Page « Mon compte » (`/compte`)
**(pas connecté)** carte « Mon compte » — « Connectez-vous pour voir votre compte. » — bouton principal [Se connecter] → `/connexion`.

**(connecté) Ordre des éléments :**
1. Titre « Mon compte ».
2. Carte « Mes informations » (lecture seule) :
   - Nom : prénom + nom
   - Adresse mail + badge vert « vérifiée », ou badge orange « pas encore vérifiée » + bouton secondaire [Renvoyer le lien]
   - Téléphone
   - Date de naissance, ex. « 04/05/2010 (16 ans) »
   - Texte « Modifier vos informations ou fermer votre compte : bientôt disponible. » (lot 2.7)
3. Carte « Accord de tes parents » — **seulement pour un compte de 16 ou 17 ans** (tutoiement : public jeune). États :
   - (aucun accord, ou refusé) bandeau orange « Tu as 16 ans : pour réserver ou publier une annonce, il faut l'accord signé de tes parents, vérifié par rafals. » ; (refusé) bandeau rouge « Ton accord a été refusé : « motif ». Tu peux en envoyer un nouveau. » ; zone [Choisir un fichier] (PDF, JPG ou PNG, 5 Mo au maximum) ; (erreur) bandeau rouge au-dessus du bouton ; bouton principal [Envoyer l'accord] → message vert « Accord envoyé : il attend la vérification de l'administrateur. »
   - (en attente) badge orange « En attente de vérification », « Envoyé le 28/09/2026 à 18 h 40. Tu verras la réponse ici. », bouton secondaire [Actualiser].
   - (accepté) badge vert « Accepté », « Tu peux réserver et publier des annonces. »
