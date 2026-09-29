# Mon compte — Interface

> Fichiers : `frontend/src/pages/ComptePage.vue` (assemble les cartes) et une carte par fichier dans `frontend/src/components/compte/` (`CarteInformations`, `CarteAccordParental`, `CarteDonnees`, `CarteFermeture`) ; « Mon adresse » est la carte commune `components/CarteAdresse.vue` (aussi utilisée pour le local du prestataire, lot 3.2) ; cadre commun `components/ui/AppSection.vue`. Construit au lot 1.4 (28/09/2026), complété au lot 2.7 (29/09/2026). Règles : `RM-COMPTES.md`, `RM-CLIENTS.md`. Maquettes : `maquette-lot-1.4-compte-administration.html`, `maquette-lot-2.7-mon-compte.html`.

## Page « Mon compte » (`/compte`)
**(pas connecté)** carte « Mon compte » — « Connectez-vous pour voir votre compte. » — bouton principal [Se connecter] → `/connexion`.

**(connecté) Ordre des éléments :**
1. Titre « Mon compte ».
2. Carte « Mes informations », bouton secondaire [Modifier] à droite du titre :
   - Nom : prénom + nom
   - Adresse mail + badge vert « vérifiée », ou badge orange « pas encore vérifiée » + bouton secondaire [Renvoyer le lien]
   - Téléphone
   - Date de naissance, ex. « 12/03/1972 (54 ans) » (absente si le compte n'en a pas)
   - Texte « Changer d'adresse mail : bientôt disponible. »
   - [Modifier] → la carte devient « Modifier mes informations » : Prénom * et Nom * côte à côte (l'un sous l'autre sur téléphone), Téléphone * ; erreur du serveur en bandeau rouge (ex. « Le nom est obligatoire. ») ; [Enregistrer] (principal) → message vert « Vos informations sont enregistrées. » ; [Annuler] (secondaire) → retour sans rien changer.
3. Carte « Accord de tes parents » — **seulement pour un compte de 16 ou 17 ans** (tutoiement : public jeune). États :
   - (aucun accord, ou refusé) bandeau orange « Tu as 16 ans : pour réserver ou publier une annonce, il faut l'accord signé de tes parents, vérifié par rafals. » ; (refusé) bandeau rouge « Ton accord a été refusé : « motif ». Tu peux en envoyer un nouveau. » ; zone [Choisir un fichier] (PDF, JPG ou PNG, 5 Mo au maximum) ; (erreur) bandeau rouge au-dessus du bouton ; bouton principal [Envoyer l'accord] → message vert « Accord envoyé : il attend la vérification de l'administrateur. »
   - (en attente) badge orange « En attente de vérification », « Envoyé le 28/09/2026 à 18 h 40. Tu verras la réponse ici. », bouton secondaire [Actualiser].
   - (accepté) badge vert « Accepté », « Tu peux réserver et publier des annonces. »
4. Carte « Mon adresse » :
   - (aucune) « Aucune adresse enregistrée : elle vous sera demandée quand vous réserverez un service à domicile. » + [Ajouter mon adresse] (secondaire).
   - (enregistrée) sur 3 lignes, ex. « 8 allée des Pins / Bâtiment B, 2e étage / 33400 Talence » ; [Modifier] (secondaire) ; [Effacer mon adresse] (danger) → message vert « Votre adresse est effacée. »
   - Formulaire (ajout ou modification, dans la carte) : Numéro et rue * (ex. « 8 allée des Pins ») ; Complément (« Bâtiment, étage, code… ») ; Ville * (recherche par nom ou code postal, comme sur « Proposer mes services ») ; **Code postal *** en liste seulement si la ville en a plusieurs (ex. Marseille : 13001 à 13016), sinon pris tout seul (Talence → 33400) ; erreur en bandeau rouge (ex. « Choisissez le code postal. », « Le code postal 33600 ne correspond pas à Talence (33400). ») ; [Enregistrer] → « Adresse enregistrée. » ; [Annuler].
5. Carte « Mes données » : « Un fichier avec tout ce que rafals sait sur vous (compte, adresse, profil de prestataire, historique de vos actions). C'est un droit prévu par la loi. » + [Télécharger mes données] (secondaire) → le navigateur enregistre `mes-donnees-rafals.json`, sans quitter la page.
6. Carte « Fermer mon compte » (bord rouge) : « Vos informations personnelles seront effacées. C'est définitif. » + [Fermer mon compte…] (danger) → fenêtre « Fermer votre compte ? » : « Votre nom, votre adresse mail, votre téléphone, votre date de naissance et votre adresse seront effacés, et vous serez déconnecté. C'est définitif. », champ « Votre mot de passe * » ; refus du serveur en rouge dans la fenêtre (mot de passe incorrect ; « Arrêtez d'abord votre activité de prestataire… » ; seul administrateur) ; [Fermer définitivement] (danger) à gauche, [Annuler] à droite. Réussite → retour à l'accueil, déconnecté, message vert « Votre compte est fermé et vos informations personnelles sont effacées. »
