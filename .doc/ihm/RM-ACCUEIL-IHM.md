# Accueil et « Bientôt disponible » — Interface

> Fichiers : `frontend/src/pages/AccueilPage.vue`, `frontend/src/pages/BientotPage.vue`, `frontend/src/router.ts`. Construit au lot 0.4 (28/09/2026).
> **Refait le 04/10/2026** (nouvelle présentation, maquette https://claude.ai/artifact/8GvhAaZ5x1m7Kyv1dLMQb3).
> **Changé le 05/10/2026** (demande de Raphael) : l'accueil sert à publier une demande ; la recherche et les dossiers de métiers sont repartis sur leur page « Trouver un prestataire » (`/trouver`, `RM-TROUVER-IHM.md`).
> **Redessiné le 07/10/2026 en style « chaleureux »** (choix « A » de Raphael, maquette https://claude.ai/artifact/3GejTyBQFa9dZXbrmmChQc). Ce que fait la page ne change pas, sauf les bulles de services (nouveau). **Ce paragraphe remplace, pour la présentation, les points 1 et 2 ci-dessous** :
> 1. **En haut**, sur deux colonnes (une seule sur téléphone) : à gauche le titre « Bonjour Julie ! » suivi, en vert, de « De quoi avez-vous besoin ? » (pour un prestataire : « Qui pouvez-vous aider ? »), 32 à 56 px, très gras ; une phrase grise « Un voisin ou un professionnel du quartier s'en occupe, souvent dès cette semaine. » ; la barre de recherche en forme de pastille blanche avec un rond orange et une loupe à droite (texte gris « ex. pelouse, ménage, robinet, Pessac… », elle filtre toujours la liste à chaque lettre) ; (personne n'est connecté) [Créer mon compte]. À droite, le dessin d'une rue avec trois maisons (`assets/quartier.svg`), caché sur téléphone.
> 2. **Les bulles de services** (nouveau) : une ligne de ronds de couleur avec un pictogramme et le nom dessous — « Tout », puis **un rond par dossier de métiers qui a au moins une demande** (ex. « Jardin & extérieur »). Un clic ne garde que les demandes de ce dossier ; la bulle choisie a un anneau vert ; « Tout » les remontre toutes. La ligne défile sur le côté si elle est trop longue ; pas de bulles tant qu'il n'y a aucune demande. Liste vide après un clic : « Aucune demande dans ce type de service. »
> 3. **Dessous, deux colonnes** : à gauche « Les demandes des clients » avec le nombre (« 4 demandes ») ; à droite la carte « Publier une demande » (380 px), qui commence maintenant **à la hauteur de la liste** et non plus à celle du « Bonjour ». Sur téléphone : la carte, puis la liste. La carte garde ses 8 rubriques (elle reste blanche : la carte vert foncé à 3 champs de la maquette ne suffisait pas pour les 8 rubriques demandées par les règles).
> 4. « Comment ça marche » : 3 cartes à ombre, numéro dans un rond de couleur. Bandeau orange : coins de 26 px.

## Page Accueil (`/`)
**Ordre des éléments, de haut en bas :**

0. (connecté, adresse pas encore vérifiée) bandeau orange « Vérifiez votre adresse mail pour pouvoir réserver. » avec un bouton secondaire [Renvoyer le lien] → message vert « Si un compte non vérifié existe… ».
1. **Bonjour, la barre, les demandes** (demande de Raphael du 05/10/2026, mot pour mot : « sur la page d'acceuille je veux que y'ai ecrit bonjour avec le prénom de la personne puis une barre de recherche ou y'a ecrit de quoi avez vous besoin ? et en dessous toute les demandes faites par des clients ») :
   1. Titre « Bonjour Julie ! » (le prénom du compte) ; personne n'est connecté : « Bonjour ! ». 30 à 44 px selon l'écran.
   2. La barre : un champ sur toute la largeur (petite étiquette « Chercher dans les demandes », texte gris dans le champ « De quoi avez-vous besoin ? », 80 caractères au plus). **Elle filtre la liste du dessous à chaque lettre tapée** (choix « b » de Raphael le 05/10/2026) : ne restent que les demandes dont le titre ou la description contient le texte, sans tenir compte des majuscules. Ex. « pelouse » → « Tondre ma pelouse » reste, « Fuite sous l'évier » disparaît.
   3. (personne n'est connecté) bouton secondaire [Créer mon compte] → `/inscription`.
2. **Deux colonnes sur ordinateur** (demandes de Raphael du 05/10/2026, mot pour mot : « sur le coté a droite comme sur allo voisin il faut que je puisse mettre mon texte pour publier ma demande », puis « ca doit prendre toute la place de haut en bas la demande et faut que on pussie metre l'adresse et que y'ai une carte google maps qui aparaise et on puisse mettre des photos ») : à gauche le bonjour, la barre et la liste ; à droite la carte « Publier une demande », 380 px de large, **de haut en bas** (elle commence à la hauteur du « Bonjour » et fait au moins la hauteur de l'écran). **Sur téléphone** : le bonjour et la barre, la carte, puis la liste.
   - **À gauche, « Les demandes des clients »** : les demandes ouvertes lues sur le serveur (`/api/demandes`), la plus récente en haut (`RM-DEMANDES.md` § « L'accueil montre toutes les demandes »). **Branché le 06/10/2026.**
     - Une carte par demande : le composant commun `CarteDemande` (`RM-DEMANDES-IHM.md`), avec **[Répondre]** pour un prestataire qui peut répondre et [Voir la conversation] s'il l'a déjà fait (branché le 07/10/2026).
     - La barre filtre sur le titre, la description, le métier et la ville. Ex. « pessac » ne garde que les demandes de Pessac.
     - Liste vide : « Aucune demande pour l'instant. » dans un cadre (ou « Aucune demande ne contient « pelouse ». ») ; serveur injoignable : bandeau rouge avec le message.
   - **À droite, carte blanche « Publier une demande »** (`frontend/src/components/demandes/CartePublierDemande.vue`), de haut en bas. **Branchée le 06/10/2026** : elle publie vraiment.
     1. « Quel métier ? * » : choix par les premières lettres (`RM-CHOIX-METIER-IHM.md`).
     2. « Titre * » (ex. « Tondre ma pelouse », 80 caractères au plus).
     3. Zone de texte « Décrivez votre besoin * » (1000 caractères au plus, compteur, aide « ex. 200 m², terrain plat, j'ai une prise dehors. Au moins 20 caractères, sans téléphone ni mail. »).
     4. « Adresse * » : champ avec propositions dès 3 lettres (ex. « 12 rue de lille merignac » → « 12 Rue de Lille 33700 Mérignac »), aide « Seul le prestataire que vous choisirez verra la rue ; les autres voient la ville. » Une adresse choisie → bandeau vert « ✓ 12 Rue de Lille 33700 Mérignac [Changer] » et, dessous, **un plan avec un repère sur l'adresse** (224 px de haut ; OpenStreetMap, voir `API-EXTERNES.md` § 3). Dessous, deux cases collées « Chez moi | Chez le prestataire ».
     5. « Pour quand ? * » : liste « Dès que possible » (choisi au départ), « Dans les 7 jours », « Un jour précis », « Pas pressé » ; « Un jour précis » fait apparaître « Quel jour ? * » (calendrier).
     6. « Budget en euros (facultatif) » (ex. 40).
     7. « Photos (2 / 5) » : zone « Choisir un fichier », JPG ou PNG, 5 Mo au plus ; chaque photo choisie s'affiche en vignette carrée avec [Enlever] ; à 5 photos la zone disparaît. Mauvais format : « Choisissez une photo JPG ou PNG. » ; trop lourde : « Cette photo dépasse 5 Mo. »
     8. Tout en bas de la carte : bouton orange [Publier ma demande] (variante `accent`) sur toute la largeur. **Personne n'est connecté** : à la place, « Il faut un compte pour publier une demande. C'est gratuit. » et le bouton orange [Se connecter pour publier] → `/connexion`.
     - Publiée : message vert « Votre demande « Tondre ma pelouse » est publiée. », elle apparaît en haut de la liste, le titre, le texte, le budget et les photos se vident (le métier et l'adresse restent, pour en publier une autre).
     - Refusée : bandeau rouge au-dessus du bouton, avec le message de la règle (ex. « Choisissez un métier : il dit quels prestataires prévenir. », « Le titre doit faire entre 5 et 80 caractères. », « Ne mettez pas vos coordonnées ici : le prestataire que vous choisirez les recevra. », « Vous avez déjà 5 demandes ouvertes : fermez-en une pour publier celle-ci. »).
3. **« Comment ça marche »** : 3 cartes numérotées — 1 Publiez votre demande, 2 Recevez des propositions, 3 Payez et donnez votre avis (changé le 05/10/2026 : plus de réservation directe, annonces retirées).
4. **Bandeau orange** (`accent-vif`), caché pour un prestataire : « Vous proposez vos services ? », texte, boutons [Proposer mes services] → `/proposer` et [Créer mon auto-entreprise] → `/creer-mon-auto-entreprise`, et 3 atouts cochés.
5. Ligne pour le développement, sous un trait : badge d'état du serveur (lit `/api/etat` : neutre « Vérification du serveur… », vert « Le serveur de rafals répond. », rouge « Le serveur ne répond pas. Relance demarrer.bat. ») et bouton secondaire [Voir le catalogue des composants] → `/catalogue`.

Pas encore fait : la liste « Près de chez vous » de la maquette (il faut connaître la ville du visiteur).

## Page « Bientôt disponible »
Utilisée pour toute adresse inconnue.

| Adresse | Titre | Texte |
|---|---|---|
| toute adresse inconnue | Page introuvable | Cette adresse ne correspond à aucune page de rafals. |

Puis un bouton principal [Retour à l'accueil].
