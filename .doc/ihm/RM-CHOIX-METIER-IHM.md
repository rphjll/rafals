# Choix d'un métier — Interface

> Fichiers : `frontend/src/components/AppChoixMetier.vue`, `frontend/src/composables/useMetiers.ts`. Construit au lot 2.2 (28/09/2026). Règles : `RM-METIERS.md`. Maquette : `maquette-lot-2.2-metiers.html`.
> Composant réutilisé : page « Trouver un prestataire », fenêtre « Remplacer » de l'Administration ; puis « Proposer mes services » (lot 2.5) et la recherche (niveau 4).

## Options
- `avec-dossiers` (oui par défaut) : affiche aussi les dossiers et le bouton « Proposer un métier ».
- `etiquette` : texte au-dessus du champ (par défaut « Tapez les premières lettres »).
- `v-model` : le métier choisi (nom, dossier), ou rien.

## Ordre des éléments
**(métier choisi)** bandeau vert « ✓ Plombier (Maison & travaux) » avec, à droite, bouton secondaire [Changer].

**(rien de choisi)**
1. Champ « Tapez les premières lettres » (exemple grisé « ex. plom, fuite, coiffeuse, piano… »). Propositions dès la 1re lettre, après une courte pause dans la frappe : 10 au maximum, « Nom » à gauche et dossier à droite, en petit. Flèches ↑ ↓ pour se déplacer, Entrée ou clic pour choisir.
2. (aucun résultat) « Aucun métier ne correspond. » + bouton secondaire [Proposer un métier].
3. Aide : « Flèches ↑ ↓ puis Entrée au clavier, ou un clic. Les accents ne comptent pas. »
4. (avec dossiers) « Ou parcourir par dossier » : cartes des 14 dossiers dans leur ordre (nom en gras, 3 premiers métiers dessous). Clic → liste des métiers du dossier, avec [← Tous les dossiers].
5. (avec dossiers) « Votre métier n'est pas dans la liste ? » + [Proposer un métier].

## Fenêtre « Proposer un métier »
- (connecté) « L'administrateur le vérifiera. En attendant, choisissez « Autre ». », champ « Nom du métier * » (prérempli avec le texte tapé), erreur du serveur dans la fenêtre (ex. « Ce métier existe déjà dans la liste : « Plombier ». ») ; [Envoyer] à gauche, [Annuler] à droite → message vert « Merci : votre proposition sera étudiée… ».
- (pas connecté) « Connectez-vous pour proposer un métier. » ; [Se connecter] → `/connexion`.
