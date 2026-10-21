# Trouver un prestataire — Interface

> **Changé le 21/10/2026** (abonnements, `RM-ABONNEMENTS-IHM.md`) : chaque petite carte montre « 12 abonnés » sous la ville et un bouton [S'abonner] / [Abonné ✓] en bas à droite (absent sur sa propre carte). Le lien du nom couvre toute la carte : un clic ailleurs que sur le bouton ouvre toujours la fiche.

> **Changé le 09/10/2026** (lot 9.3, retrait des annonces) : dans les résultats d'une recherche par métier, les filtres sont réduits à deux pastilles, « Vient chez moi » et « Paiement par carte ». La pastille « Libre dans les 7 jours » et le champ « Prix maximum » sont retirés.

> Fichiers : `frontend/src/pages/TrouverPage.vue`, `frontend/src/components/recherche/CarteResultat.vue`, `frontend/src/components/prestataire/AvatarPrestataire.vue`, `frontend/src/outils/recherche.ts`. Construit au lot 2.2 (choix du métier), complété au lot 4.2 (30/09/2026). Règles : `RM-RECHERCHE.md`. Maquette : `maquette-lot-4.2-recherche.html`.

> Fichiers ajoutés le 07/10/2026 : `frontend/src/components/recherche/RubriquesPrestataires.vue`.

## Depuis le 07/10/2026 : une rubrique par service (cette partie décrit l'écran d'aujourd'hui)
Demande de Raphael, mot pour mot : « je veux que tu m'enelve toute ces bulles et que a la place tu me mette tout les prestataires mais dans une rubrique […] fait comme sur allo voisin » (avec une capture d'AlloVoisins). Maquette validée (« oui c'est parfait la ») : `maquette-trouver-par-service.html` (https://claude.ai/artifact/44ZCypQ8rS99w7zaCDBmNM). Règles : `RM-RECHERCHE.md` § « Une rubrique par dossier ».

**Les tuiles des dossiers (« De quoi avez-vous besoin ? ») n'existent plus.** La page a trois états, tous dans l'adresse :

1. **`/trouver` — ville inconnue.** Titre « Le bon prestataire, près de chez vous. », phrase grise, dessin de la rue, carte de recherche, puis une carte « Indiquez votre ville pour voir les prestataires près de chez vous. » avec l'aide « Tapez son nom ou son code postal dans « Où ? », puis [Rechercher]. Le service est facultatif… ». Si une ville a déjà été donnée sur cet appareil, la page passe toute seule à l'état 2.
2. **`/trouver?ville=12768` — par service.** Il ne reste en haut que la carte de recherche. Dessous, une rubrique par dossier : titre « Bricolage », ligne grise « 14 prestataires près de Pessac », **rangée de cartes qui défile de côté** (10 au plus, cartes de 318 px, 82 % de l'écran sur téléphone), puis [Voir tout] centré. Aucun prestataire dans la ville : carte « Aucun prestataire ne vient à Pessac pour l'instant. » + [Publier une demande] (→ accueil).
   - **`/trouver?ville=12768&dossier=3&page=2` — [Voir tout].** [← Tous les services], le titre et le compte de la rubrique, tous ses prestataires en grille (270 px au moins par carte), pages [‹ Précédente] [1] [2] [Suivante ›] au-delà de 30.
3. **`/trouver?metier=3&ville=12768` — un métier précis.** [← Tous les services] (→ état 2), puis le titre, le tri, les filtres et les résultats (points 3 à 7 plus bas), avec la même carte, en grille.

**Carte de recherche** : « Quel service ? » est devenu **facultatif** ; « Où ? » est obligatoire (bandeau rouge « Indiquez votre ville. »). [Rechercher] retient la ville sur l'appareil.

**Carte d'un prestataire** (`CarteResultat.vue`, la même dans la rangée, dans [Voir tout] et dans les résultats d'une recherche), de haut en bas :
- dans le coin en haut à droite : « SIRET vérifié » (vert) ou « Particulier » (gris) ;
- photo de profil ronde (ou initiales « KB ») à gauche ; à droite le nom, le métier en gras (« Plombier », ou « aussi plombier » pour un métier secondaire), « Pessac · à 2 km » ;
- les **2 premières photos de son travail** côte à côte (112 px de haut ; une seule : toute la largeur), ou un bandeau gris « Pas encore de photos » ;
- en bas « ★ 4,8/5 (23 avis) » ou l'étiquette « Nouveau sur rafals ».
- Enlevés de la carte : « à partir de 40 €/h », « vient chez vous », « carte acceptée » (les filtres existent toujours dans l'état 3).
- Clic → `/prestataires/12`. Survol : anneau vert.

Les paragraphes ci-dessous décrivent les états précédents ; ils ne restent vrais que pour le tri, les filtres, « aucun résultat » et les pages de l'état 3.

> **Redessiné le 07/10/2026 en style « chaleureux »** (choix « A » de Raphael, maquette https://claude.ai/artifact/3GejTyBQFa9dZXbrmmChQc). Ce que fait la page ne change pas. Ce qui change à l'écran :
> - **Haut de page** : plus de bandeau vert foncé. À gauche le titre « Le bon prestataire, » puis en vert « près de chez vous. », la phrase grise, et la carte blanche de recherche (« Quel service ? », « Où ? », [Rechercher] orange) ; à droite le dessin de la rue (caché sur téléphone). Pendant une recherche, il ne reste que la carte de recherche.
> - **Tuiles des dossiers** : cartes blanches avec, à gauche, un rond de couleur et le pictogramme du dossier (`AppPicto`), à droite le nom et ses 3 premiers métiers. Survol : anneau vert.
> - **Résultats en petites cartes** (demande de Raphael du 07/10/2026, mot pour mot : « au lieux que 1prestataire prenne toute la largeur il prenne que la taille d'une etiquette un peu et la possibilité de mettre des photots de profils ») : une grille, 2 cartes par ligne sur téléphone, 4 ou 5 sur ordinateur (190 px au moins chacune). Carte, de haut en bas, tout centré : **photo de profil ronde de 92 px** (ou initiales, ex. « KB ») ; nom ; « ★ 4,8 · 23 avis » ou badge « Nouveau sur rafals » ; « Plombier » (ou « aussi plombier ») puis « Pessac · à 2 km » ; badges « vient chez vous » / « carte acceptée » ; en bas, en vert, « à partir de 40 €/h » / « Sur devis ». La ligne « 3 annonces · voir la fiche › » est enlevée. Clic → `/prestataires/12`. Survol : anneau vert. **La photo de profil se met depuis « Mon activité »** (elle existait déjà). Ce paragraphe remplace le point 5 ci-dessous.

> **Depuis le 05/10/2026 (demande de Raphael : « crée un nouvel onglet acceuille et de laisser trouver un prestataire »), la recherche a de nouveau sa page `/trouver`**, avec sa propre entrée de menu ; l'accueil `/` sert à publier une demande (`RM-ACCUEIL-IHM.md`). La page (`frontend/src/pages/TrouverPage.vue`, réécrit) montre, de haut en bas : le bandeau vert foncé (titre « Le bon prestataire, près de chez vous. », texte, carte de recherche « Quel service ? » / « Où ? » / [Rechercher] orange), puis les tuiles « De quoi avez-vous besoin ? » (un dossier de métiers par tuile ; clic → ses métiers ; clic sur un métier → recherche si la ville est connue, sinon message « « Jardinage » choisi : indiquez votre ville. »). Après une recherche, **on reste sur cette page** : l'adresse devient `/trouver?metier=3&ville=12768…`, le bandeau se réduit à la carte de recherche, et les tuiles sont remplacées par [← Tous les métiers] puis les résultats (points 3 à 7 ci-dessous, `ResultatsRecherche.vue`). Le paragraphe suivant décrit l'état du 04/10/2026, qui n'est plus vrai.
>
> **Du 04/10 au 05/10/2026 (demande de Raphael), la recherche se faisait sur l'accueil** : il n'y a plus de page « Trouver un prestataire ». Le titre et la carte de recherche (points 1 et 2 ci-dessous) sont ceux de l'accueil (`RM-ACCUEIL-IHM.md`) ; les points 3 à 7 décrivent les résultats, affichés sur l'accueil par `frontend/src/components/recherche/ResultatsRecherche.vue`. L'adresse est `/?metier=3&ville=12768…` ; un ancien lien `/trouver?…` y est renvoyé avec les mêmes réglages. L'entrée « Trouver un prestataire » du menu mène à l'accueil. `frontend/src/pages/TrouverPage.vue` n'est plus utilisé (à supprimer par Raphael).

## Résultats de recherche (anciennement page `/trouver`)
Ouverte à tous, même sans compte. Contenu sur toute la largeur de la page (1080 px au plus). **Présentation refaite le 04/10/2026** (nouvelle présentation du site ; ce que fait la page n'a pas changé). **Toute la recherche est dans l'adresse** : `/trouver?metier=3&ville=12768&tri=distance&chez_moi=1&carte=1&libre=1&prix_max=60&page=2` ; un lien partagé montre les mêmes résultats, et le bouton « retour » revient à la recherche précédente.

**Ordre des éléments :**
1. Bandeau vert foncé (`fonce`) avec le titre « Trouver un prestataire » en blanc, et dedans la carte blanche de recherche.
2. Carte de recherche (bouton [Chercher] orange, variante `accent`) : « Quel métier ? * » (choix par lettres ou par dossier, `RM-CHOIX-METIER-IHM.md`) et « Votre ville * » (nom ou code postal) côte à côte sur ordinateur, [Chercher] ; aide « Métier : par les premières lettres ou par dossier ; ville : par le nom ou le code postal. » ; sans métier ou sans ville : bandeau rouge « Choisissez un métier. » / « Choisissez votre ville. »
3. (après une recherche) Titre « 12 prestataires « Plombier » pour Talence » + choix de l'ordre [Les mieux notés | Les plus proches].
4. Filtres (pastilles rondes : blanche à contour vert, verte et pleine quand le filtre est actif) : « Vient chez moi », « Paiement par carte », « Libre dans les 7 jours », et une pastille « Prix maximum [ex. 60] € » ; un clic sur une pastille relance aussitôt, le prix après une courte pause de frappe ; chaque changement revient à la page 1.
5. Résultats : une carte par prestataire, cliquable → `/prestataires/12`. Carte : photo ronde ou initiales ; nom ; badge orange « Nouveau sur rafals » ou « ★ 4,5 (8 avis) » ; « Plombier » (ou « aussi plombier » quand c'est un métier secondaire) · ville de départ · « à 5 km » ; badges « vient chez vous » (vert) et « carte acceptée » (gris) ; à droite (dessous sur téléphone) « à partir de 40 €/h » / « à partir de 45 € » / « Sur devis » en grand (police des titres, vert) et « 3 annonces · voir la fiche › ». Survol : contour vert et fond `primaire-doux`.
6. Aucun résultat : avec des filtres, « Aucun résultat avec ces filtres. » + [Enlever les filtres] ; sinon « Aucun prestataire « Plombier » ne vient à Libourne pour l'instant. », « Essayez un métier voisin : » et un bouton par métier voisin (relance la recherche avec ce métier).
7. Pages (au-delà de 30) : [‹ Précédente] [1] [2] … [Suivante ›], la page en cours en bouton principal.
