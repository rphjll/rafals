# Ma carte de visite — Interface

> Lot 10.4, construit le 22/10/2026. Maquette validée par Raphael (« oui ») : https://claude.ai/artifact/GonnHbitA34ASGJ1kj2TCB (`.doc/ihm/maquette-carte-visite.html`). Règles : `regles-metier/RM-CARTE-VISITE.md`. Fichier : `frontend/src/pages/MaCarteVisitePage.vue`, adresse `/ma-carte-de-visite`.

## D'où on vient
La tuile « Ma carte de visite » de « Mon activité » (groupe « Me faire connaître » ; avant : « bientôt »). Elle est aussi dans le sous-menu des pages de ce groupe. Réservée aux prestataires (`GardePrestataire`).

## Ce qu'on voit, de haut en bas (720 px au plus)
1. Titre « Ma carte de visite ».
2. « Donnez-la à vos clients : en scannant le carré, ils arrivent sur votre page rafals, avec vos avis et vos photos. »
3. Verrouillé : bandeau orange avec la raison donnée par le serveur, ex. « Les cartes de visite sont réservées aux prestataires avec un SIRET vérifié. » ou « Votre profil est en pause : sa page publique est fermée, le carré à scanner ne mènerait nulle part. Reprenez votre activité d'abord. »
4. **L'aperçu** de la carte (8,5 × 5,5 cm, papier blanc même en mode sombre : couleurs `papier` / `encre`) : « Karim Benali », « Plombier · Chauffagiste », « Pessac », « 4,8/5 · 23 avis sur rafals », le téléphone si la case est cochée, « rafals. », et à droite le vrai carré à scanner (image `GET /api/moi/prestataire/carte-de-visite/carre.svg`) avec « Mes avis et mes photos ».
5. Seulement si rien n'est verrouillé : la case **« Mettre mon téléphone sur la carte »** (décochée à l'arrivée) et dessous « Le numéro de votre compte : 06 12 34 56 78. ». Sans numéro dans le compte : case verrouillée 🔒 « Ajoutez d'abord votre téléphone dans Mon profil › Mon compte › Mes informations. »
6. **[Télécharger la planche à découper]** (principal) et **[Télécharger pour un imprimeur]** (secondaire). Le PDF s'ouvre dans un nouvel onglet, comme une facture (`GET /api/moi/prestataire/carte-de-visite/pdf?forme=planche|carte&telephone=true|false`) ; nom du fichier : `carte-de-visite-karim-benali-planche.pdf` / `carte-de-visite-karim-benali.pdf`. Verrouillés : 🔒, la raison dans la bulle ; sans SIRET, en plus [Créer mon auto-entreprise].
7. Carte « Comment l'imprimer » (seulement si rien n'est verrouillé) : planche A4 de 10 cartes sur papier épais (250 g), à couper le long des petits traits gris ; carte seule au format exact pour un imprimeur.

## Décisions prises par Claude, à confirmer
- La case du téléphone est cachée tant que la carte est verrouillée (la raison est déjà dans le bandeau).
- La planche n'a pas d'aperçu réduit sur la page (la maquette en avait un) : le PDF s'ouvre en un clic.
