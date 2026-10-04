# Mes annonces / Écrire une annonce — Interface

> Fichiers : `frontend/src/pages/MesAnnoncesPage.vue`, `AnnonceFormulairePage.vue`, `frontend/src/components/annonces/LigneAnnonce.vue`, `PhotosAnnonce.vue`, `frontend/src/components/prestataire/GardePrestataire.vue`, `frontend/src/outils/annonces.ts` (prix, durée, lieu, paiement), composants `AppChoix`, `AppCase`. Construit au lot 3.2 (29/09/2026). Règles : `RM-ANNONCES.md`. Maquette : `maquette-lot-3.2-annonces.html`.

## Accès
Menu « Mes annonces » (seulement pour un prestataire), ou la carte « Mes annonces » de « Mon activité ». Contenu centré, 720 px au plus.
- (pas connecté) carte « Connectez-vous pour gérer vos annonces. » + [Se connecter].
- (connecté sans profil de prestataire) carte « Créez d'abord votre profil de prestataire. » + [Proposer mes services].

## Page `/mes-annonces`
1. Fil d'Ariane « Mon activité › Mes annonces ».
2. Titre « Mes annonces » + [Écrire une annonce] (principal) à droite.
3. « 3 annonces en ligne sur 20 au plus. »
4. Carte des annonces en ligne ou en pause, les plus récentes d'abord, séparées par un trait. Vide : « Aucune annonce pour l'instant : écrivez la première pour que les clients vous trouvent. »
5. « Annonces retirées (1) » : bloc replié, qui s'ouvre au clic, mêmes lignes.

**Une ligne d'annonce** : photo n° 1 (ou « sans photo »), titre, badge (« en ligne » vert, « en pause » / « retirée » gris) ; « **50 € · 2 h** · Plombier · chez le client · carte bancaire ou espèces » (à l'heure : « 40 €/h · de 1 h à 3 h » ; « Sur devis ») ; si en ligne mais cachée : « Cachée aux clients : Votre activité est en pause. » (orange) ; si son métier est arrêté : « Cachée : vous avez arrêté le métier Chauffagiste. » ; erreur du serveur dans la ligne. Boutons :
- [Modifier] → `/mes-annonces/12` ;
- en ligne : [Voir comme un client] → `/annonces/12`, [Mettre en pause] → « Annonce mise en pause. » ;
- en pause ou retirée : [Republier] → « Annonce republiée. » — verrouillé 🔒 si le métier est arrêté : « Reprenez d'abord le métier Chauffagiste (page « Mon activité »), puis republiez. » ;
- [Retirer…] (danger, à droite, sauf si déjà retirée) → fenêtre « Retirer « Dépannage fuite » ? » : « Elle ne sera plus proposée aux clients et passera dans « Annonces retirées ». Vous pourrez la republier plus tard. Les rendez-vous déjà pris restent. » ; [Retirer] (danger) / [Annuler] → « Annonce retirée. »
Jamais de bouton « Supprimer » (une annonce n'est jamais effacée).

## Pages `/mes-annonces/nouvelle` (écrire) et `/mes-annonces/12` (modifier)
Fil d'Ariane « Mon activité › Mes annonces › Écrire une annonce » (ou « Modifier « Dépannage fuite » »), puis le titre.

**Carte « Le service »** : Métier * (liste des métiers encore exercés du profil ; aide « Seulement les métiers de votre profil. ») · Titre * (80 caractères au plus, « ex. Ménage 2 h ») · Description (compteur « 92 / 1000 », facultative).

**Carte « Le prix »** : « Forme du prix * » en 3 cases : [Prix fixe — ex. 50 € pour 2 h] [À l'heure — le client choisit ses heures] [Sur devis — le client vous écrit]. Selon le choix :
- fixe : Prix (€) * et Durée * (liste : 15 min, 30 min, 45 min, 1 h, 1 h 30, 2 h, 2 h 30, 3 h, 4 h, 5 h, 6 h, 8 h ; 1 h au départ) + « La durée bloque votre agenda : jamais deux clients en même temps. » ;
- à l'heure : Prix de l'heure (€) *, Au moins (heures) *, Au plus (heures) * + « Le client choisit entre 1 h et 3 h et voit le total avant de réserver (ex. 1 h → 40 €). » ;
- sur devis : « Pas de prix ni de durée : le client vous décrit son besoin (avec photos), vous répondez par un devis (bientôt disponible). »
Un prix s'écrit « 50 » ou « 45,50 ».

**Carte « Où et comment payer »** : « Lieu * » en 3 cases [Chez le client] [Chez moi — à votre local] [Les deux] ; sans local, « Chez moi » et « Les deux » sont verrouillés 🔒, un clic affiche « Ajoutez d'abord l'adresse de votre local (page « Mon activité »). » · « Paiement * (au moins un) » : case « Carte bancaire, sur rafals » (verrouillée 🔒 sans SIRET vérifié, raison dessous : « Le paiement par carte demande un SIRET vérifié (page « Mon activité ») : sans lui, espèces seulement. ») et case « Espèces, le jour du service » (cochée au départ).

**Carte « Photos »** : à l'écriture, « Vous pourrez ajouter jusqu'à 5 photos juste après avoir publié. » ; en modification : « 3 / 5 », les photos numérotées avec × (retirer → « Photo retirée. », les suivantes remontent d'un rang), case [+ Ajouter une photo] (jusqu'à 5) → choix d'un fichier → « Photo ajoutée. » ; erreur dans la carte (ex. « Au plus 5 photos… », fichier qui n'est pas une photo) ; « JPG ou PNG, 5 Mo au plus. La n° 1 est montrée en premier. »

**Bas de page** : erreur du serveur en bandeau rouge (ex. « Indiquez la durée du service (ex. 2 h) : elle bloque votre agenda. », « Vous avez déjà 20 annonces en ligne : mettez-en une en pause pour publier celle-ci. ») ; [Publier l'annonce] → « Annonce publiée : les clients peuvent la voir. Ajoutez des photos. » et la page passe en modification (pour ajouter les photos) ; en modification [Enregistrer] → « Annonce enregistrée. » et retour à la liste ; [Annuler] → la liste.

## Annonce retirée par l'administrateur (lot 6.4, 04/10/2026)
Dans « Annonces retirées » : bandeau rouge « Retirée par l'administrateur de rafals : elle ne peut pas être remise en ligne. » ; [Republier] est verrouillé 🔒 : « Cette annonce a été retirée par l'administrateur de rafals : vous ne pouvez pas la remettre en ligne. » [Modifier] reste possible, sans effet sur son état.
