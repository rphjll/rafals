# En-tête commun — Interface

> Fichiers : `frontend/src/components/AppEntete.vue`, `frontend/src/App.vue`. Construit au lot 0.4 (28/09/2026).

## Disposition
Bandeau blanc (`surface`) collé en haut de toutes les pages, bordure fine en bas, hauteur 60 px. Contenu centré sur 1080 px au maximum, marges de 16 px sur les côtés.

**Ordre des éléments, de gauche à droite :**
1. Logo « rafals. » (police des titres, vert `primaire`, point orange `accent`) → lien vers l'accueil `/`.
2. Menu principal, collé à droite :
   1. « Trouver un prestataire » → `/trouver`
   2. « Proposer mes services » → `/proposer`
   3. « Mes rendez-vous » → `/rendez-vous`
   4. « Mon compte » → `/compte`

L'entrée de la page affichée est surlignée (fond `primaire-doux`, texte `primaire`). Survol : même effet.

## Sous 768 px de large (téléphone, petite tablette)
- Le menu disparaît ; un bouton ☰ apparaît à droite (libellé lu à voix haute : « Ouvrir le menu » / « Fermer le menu »).
- Un clic sur ☰ déroule le menu sous l'en-tête, une entrée par ligne, sur toute la largeur.
- Le menu se referme tout seul quand on change de page.

## Particularités
Les entrées pas encore construites mènent à la page « Bientôt disponible » (voir `RM-ACCUEIL-IHM.md`).
