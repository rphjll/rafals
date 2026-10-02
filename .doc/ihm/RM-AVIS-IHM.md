# Avis — Interface

> Fichiers : `frontend/src/components/avis/` (`FenetreAvis`, `AvisAffiche`), `frontend/src/components/FenetreTexte.vue` (fenêtre commune à un seul texte), `frontend/src/components/admin/OngletAvisSignales.vue`, `OngletMotsInterdits.vue`, `frontend/src/outils/avis.ts` ; branchés dans `RendezVousPage.vue`, `agenda/OngletRendezVous.vue`, `PrestatairePage.vue`. Construit au lot 4.8 (02/10/2026). Règles : `RM-AVIS.md`. Maquette : `maquette-lot-4.8-avis.html`.

## Client, « Mes rendez-vous › Passés et annulés »
- Rendez-vous tenu, dans les 30 jours, sans avis : [Donner mon avis] (principal).
- Fenêtre « Votre avis sur Léa Martin » : rappel du rendez-vous ; « Note * » : 5 étoiles cliquables (grises, orange jusqu'à celle choisie) ; « Votre avis * » (compteur « 0 / 1000 », aide « De 10 à 1000 caractères. Signé de votre prénom et de l'initiale de votre nom. ») ; sans note : « Choisissez une note de 1 à 5 étoiles. » ; refus du serveur dans la fenêtre (ex. « Votre avis contient un mot interdit… », « Votre avis semble injurieux : reformulez-le calmement, s'il vous plaît. ») ; [Publier mon avis] → « Merci : votre avis est publié. » / [Annuler].
- Avis déjà donné : encadré « ★★☆☆☆ **Votre avis :** … », la réponse du prestataire en retrait (« **Réponse de Karim Benali :** … ») ; [Modifier] (même fenêtre, bouton [Enregistrer] → « Votre avis est modifié. ») tant que c'est permis + « Modifiable jusqu'au jeudi 12/11 à 10 h 45. » ; [Retirer] (danger) → « Avis retiré : il n'est plus affiché. » ; caché : bandeau rouge « Avis caché par rafals : « motif ». » ; retiré : « Avis retiré : il n'est plus affiché. »

## Prestataire, « Mon agenda › Rendez-vous › Passés et annulés »
Le bloc s'ouvre tout seul s'il y a un avis sans réponse. Encadré « ★★☆☆☆ **Avis de Paul P. :** … » ; [Répondre…] (une fois) → fenêtre « Répondre à Paul P. » (« Votre réponse sera affichée sous l'avis, pour tous. Une seule réponse ; la note ne change pas. ») → [Publier ma réponse] → « Réponse publiée. » ; [Signaler…] (danger, une fois) → fenêtre « Signaler cet avis ? » (« Pourquoi ? * », ex. « Fausse accusation ») → « Avis signalé : l'administrateur va le regarder. » ; signalé : bandeau orange « Signalé : l'administrateur va le regarder. »

## Page publique d'un prestataire › carte « Avis »
Sans avis : « Pas encore d'avis. » Sinon : la note en grand (« 4,2 ») + « ★★★★☆ » + « 30 avis de clients ayant eu un rendez-vous » ; les 10 plus récents (« ★★★★★ **Marie D.** · octobre 2026 », le texte, la réponse en retrait) ; [Voir plus d'avis] (10 de plus).

## Administration
- **« Avis signalés »** (compteur orange) : « Avis sur Karim Benali » + badge « signalé », l'avis, bandeau « Signalé par Karim Benali le 02/10/2026 à 9 h 12 : « Fausse accusation » » ; [Le laisser] → « Avis laissé : le signalement est traité. » ; [Le cacher…] (danger) → fenêtre « Cacher cet avis ? » (« Motif * ») → « Avis caché : le client est prévenu. » Vide : « Aucun avis signalé. »
- **« Mots interdits (50) »** : « Une IA lit déjà chaque avis et chaque réponse. Cette liste est un filet de secours… » ; champ « Ajouter un mot » + [Ajouter] → « « abruti » ajouté à la liste. » (erreurs : « Un seul mot, d'au moins 2 lettres (sans espace). », « déjà dans la liste ») ; les mots en pastilles avec × → « « abruti » retiré de la liste. »
