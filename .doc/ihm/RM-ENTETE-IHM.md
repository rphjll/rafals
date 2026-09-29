# En-tête commun — Interface

> Fichiers : `frontend/src/components/AppEntete.vue`, `frontend/src/App.vue`, `frontend/src/composables/useCompte.ts`. Construit au lot 0.4, zone du compte au lot 1.2 (28/09/2026).

## Disposition
Bandeau blanc (`surface`) collé en haut de toutes les pages, bordure fine en bas, hauteur 60 px. Contenu centré sur 1080 px au maximum, marges de 16 px sur les côtés.

**Ordre des éléments, de gauche à droite :**
1. Logo « rafals. » (police des titres, vert `primaire`, point orange `accent`) → lien vers l'accueil `/`.
2. Menu principal, collé à droite :
   1. « Trouver un prestataire » → `/trouver`
   2. « Proposer mes services » → `/proposer` — devient « Mon activité » quand le compte a un profil de prestataire (lot 2.5)
   3. « Mes annonces » → `/mes-annonces` — **seulement pour un prestataire** (lot 3.2)
   4. « Mes rendez-vous » → `/rendez-vous`
   5. « Mon compte » → `/compte`
   6. « Administration » → `/administration` — **seulement pour un administrateur** (lot 1.4)

3. Zone du compte, au bout du menu (affichée seulement une fois qu'on sait si quelqu'un est connecté, pour éviter un clignotement) :
   - personne n'est connecté : bouton principal [Se connecter] → `/connexion` ;
   - connecté : le prénom (ex. « Marie »), puis bouton secondaire [Se déconnecter] → accueil + message vert « Vous êtes déconnecté. ».
   (Ajouté au lot 1.2, 28/09/2026.)

L'entrée de la page affichée est surlignée (fond `primaire-doux`, texte `primaire`). Survol : même effet.

## Sous 768 px de large (téléphone, petite tablette)
- Le menu disparaît ; un bouton ☰ apparaît à droite (libellé lu à voix haute : « Ouvrir le menu » / « Fermer le menu »).
- Un clic sur ☰ déroule le menu sous l'en-tête, une entrée par ligne, sur toute la largeur.
- Le menu se referme tout seul quand on change de page.

## Particularités
Les entrées pas encore construites mènent à la page « Bientôt disponible » (voir `RM-ACCUEIL-IHM.md`).
