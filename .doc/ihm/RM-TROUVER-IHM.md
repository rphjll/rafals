# Trouver un prestataire — Interface

> Fichiers : `frontend/src/pages/TrouverPage.vue`, `frontend/src/components/recherche/CarteResultat.vue`, `frontend/src/components/prestataire/AvatarPrestataire.vue`, `frontend/src/outils/recherche.ts`. Construit au lot 2.2 (choix du métier), complété au lot 4.2 (30/09/2026). Règles : `RM-RECHERCHE.md`. Maquette : `maquette-lot-4.2-recherche.html`.

## Page « Trouver un prestataire » (`/trouver`)
Ouverte à tous, même sans compte. Contenu sur toute la largeur de la page (1080 px au plus). **Présentation refaite le 04/10/2026** (nouvelle présentation du site ; ce que fait la page n'a pas changé). **Toute la recherche est dans l'adresse** : `/trouver?metier=3&ville=12768&tri=distance&chez_moi=1&carte=1&libre=1&prix_max=60&page=2` ; un lien partagé montre les mêmes résultats, et le bouton « retour » revient à la recherche précédente.

**Ordre des éléments :**
1. Bandeau vert foncé (`fonce`) avec le titre « Trouver un prestataire » en blanc, et dedans la carte blanche de recherche.
2. Carte de recherche (bouton [Chercher] orange, variante `accent`) : « Quel métier ? * » (choix par lettres ou par dossier, `RM-CHOIX-METIER-IHM.md`) et « Votre ville * » (nom ou code postal) côte à côte sur ordinateur, [Chercher] ; aide « Métier : par les premières lettres ou par dossier ; ville : par le nom ou le code postal. » ; sans métier ou sans ville : bandeau rouge « Choisissez un métier. » / « Choisissez votre ville. »
3. (après une recherche) Titre « 12 prestataires « Plombier » pour Talence » + choix de l'ordre [Les mieux notés | Les plus proches].
4. Filtres (pastilles rondes : blanche à contour vert, verte et pleine quand le filtre est actif) : « Vient chez moi », « Paiement par carte », « Libre dans les 7 jours », et une pastille « Prix maximum [ex. 60] € » ; un clic sur une pastille relance aussitôt, le prix après une courte pause de frappe ; chaque changement revient à la page 1.
5. Résultats : une carte par prestataire, cliquable → `/prestataires/12`. Carte : photo ronde ou initiales ; nom ; badge orange « Nouveau sur rafals » ou « ★ 4,5 (8 avis) » ; « Plombier » (ou « aussi plombier » quand c'est un métier secondaire) · ville de départ · « à 5 km » ; badges « vient chez vous » (vert) et « carte acceptée » (gris) ; à droite (dessous sur téléphone) « à partir de 40 €/h » / « à partir de 45 € » / « Sur devis » en grand (police des titres, vert) et « 3 annonces · voir la fiche › ». Survol : contour vert et fond `primaire-doux`.
6. Aucun résultat : avec des filtres, « Aucun résultat avec ces filtres. » + [Enlever les filtres] ; sinon « Aucun prestataire « Plombier » ne vient à Libourne pour l'instant. », « Essayez un métier voisin : » et un bouton par métier voisin (relance la recherche avec ce métier).
7. Pages (au-delà de 30) : [‹ Précédente] [1] [2] … [Suivante ›], la page en cours en bouton principal.
