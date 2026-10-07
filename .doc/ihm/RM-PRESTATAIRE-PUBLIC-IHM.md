# Page publique d'un prestataire — Interface

> Fichiers : `frontend/src/pages/PrestatairePage.vue`, `frontend/src/components/prestataire/AvatarPrestataire.vue`. Construit au lot 4.2 (30/09/2026). Règles : `RM-RECHERCHE.md` (précisions du lot 4.1). Maquette : `maquette-lot-4.2-recherche.html` (écran 3).

## Présentation depuis le 07/10/2026 (style « chaleureux »)
Ce que fait la page ne change pas ; pour la présentation, ce paragraphe remplace le début de « Page `/prestataires/12` » ci-dessous.
- La page prend toute la largeur (1080 px) au lieu de 880 px.
- **En haut, deux colonnes sur ordinateur** : à gauche la photo de profil ronde (ou les initiales), le nom en très grand, « ★ 4,8 · 23 avis », les badges « Nouveau sur rafals » / « SIRET vérifié », puis le métier, la ville et la distance, l'alerte des absences, la présentation. À droite, une **carte vert foncé « Besoin de Karim ? »** (340 px) avec le bouton orange [Écrire à Karim] sur toute la largeur et la phrase « Son téléphone et son adresse vous sont donnés après une réservation. » ; elle reste visible quand on fait défiler. Sur téléphone, elle vient juste sous la présentation. Sur sa propre page, pas de carte.
- Dessous, sur toute la largeur : « Ses annonces », « Avis » (note en très grand), puis [Signaler ce prestataire…].
- Pas encore fait : les photos du prestataire en grand (elles n'existent pas encore dans la base : prévues au niveau 9).

## Page `/prestataires/12`
Ouverte à tous, même sans compte. Visible seulement si l'activité du prestataire est active (sinon « Ce prestataire n'existe pas. ») ; son auteur la voit toujours. On y arrive depuis les résultats de recherche ou le nom du prestataire sur la page d'une annonce.

1. [‹ Retour] : la page d'avant (les résultats) ; ouverte directement par un lien : la recherche.
2. (auteur) bandeau orange « Votre page, telle que les clients la voient. » + lien « Mon activité ».
3. Carte du profil : grande photo ronde (ou initiales) ; nom + badge vert « SIRET vérifié » ; « ★ 4,5 (8 avis) » ou badge « Nouveau sur rafals » ; « Plombier · aussi Électricien » (métiers exercés) ; « Part de Pessac, se déplace jusqu'à 20 km » ; (s'il y en a, lot 4.6) bandeau orange « 1 absence sans prévenir ces 6 derniers mois » ; présentation.
4. Carte « Ses annonces » : une ligne par annonce en ligne — titre, « **50 € · 2 h** · Chez vous (Marc vient de Pessac) · carte bancaire ou espèces », [Voir l'annonce] → `/annonces/12` ; aucune : « Marc n'a pas d'annonce en ligne pour l'instant. »
5. Carte « Avis » (lot 4.8) : voir `RM-AVIS-IHM.md`.
6. « Le téléphone et l'adresse sont donnés après une réservation. » — jamais de téléphone, de mail ni de rue sur cette page.

## [Signaler ce prestataire…] (lot 6.4, 04/10/2026)
En bas de la page, à droite (absent sur son propre profil) : voir `RM-SIGNALEMENTS-IHM.md`.

## [Écrire à Karim] (ajouté le 07/10/2026, lot 8.2)
Sous la présentation, un bouton principal **[Écrire à Karim]** (le prénom du nom affiché), absent sur sa propre page. Il ouvre la conversation avec ce prestataire dans « Messages » (`RM-MESSAGES-IHM.md`), ou la retrouve si elle existe déjà. Pas connecté → page de connexion. Refus de la règle (ex. « Ce prestataire n'est pas joignable en ce moment. ») : bandeau rouge sous le bouton.
