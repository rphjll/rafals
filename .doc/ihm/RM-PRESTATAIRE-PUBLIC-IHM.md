# Page publique d'un prestataire — Interface

> **Changé le 09/10/2026** (lot 9.3) : dans la carte « Besoin de Karim ? », sous [Écrire à Karim], un bouton secondaire **[Demander un devis]**, actif seulement si le prestataire a un SIRET vérifié ; sinon (15/10/2026) il reste visible, **verrouillé 🔒** : « Ce prestataire n'a pas de SIRET vérifié : il ne fait pas de devis. Écrivez-lui pour vous mettre d'accord. » Pas connecté → page de connexion puis retour. Il ouvre la fenêtre « Demander un devis à Karim » (`RM-DEVIS-IHM.md`) ; après l'envoi : « Demande envoyée : Karim vous répond par un devis. » et la page « Mes devis ». La phrase du bas devient « Son téléphone et son adresse vous sont donnés après un rendez-vous. »

> Fichiers : `frontend/src/pages/PrestatairePage.vue`, `frontend/src/components/prestataire/AvatarPrestataire.vue`. Construit au lot 4.2 (30/09/2026). Règles : `RM-RECHERCHE.md` (précisions du lot 4.1). Maquette : `maquette-lot-4.2-recherche.html` (écran 3).

## Présentation depuis le 07/10/2026 (style « chaleureux »)
Ce que fait la page ne change pas ; pour la présentation, ce paragraphe remplace le début de « Page `/prestataires/12` » ci-dessous.
- La page prend toute la largeur (1080 px) au lieu de 880 px.
- **En haut, deux colonnes sur ordinateur** : à gauche la photo de profil ronde (ou les initiales), le nom en très grand, « ★ 4,8 · 23 avis », les badges « Nouveau sur rafals » / « SIRET vérifié », puis le métier, la ville et la distance, l'alerte des absences, la présentation. À droite, une **carte vert foncé « Besoin de Karim ? »** (340 px) avec le bouton orange [Écrire à Karim] sur toute la largeur et la phrase « Son téléphone et son adresse vous sont donnés après une réservation. » ; elle reste visible quand on fait défiler. Sur téléphone, elle vient juste sous la présentation. Sur sa propre page, pas de carte.
- Dessous, sur toute la largeur : « Avis » (note en très grand), puis [Signaler ce prestataire…].
- Pas encore fait : les photos du prestataire en grand (elles n'existent pas encore dans la base : prévues au niveau 9).

## « Son travail en photos » (ajouté le 07/10/2026)
Entre la présentation et « Avis », seulement s'il a au moins une photo : une grille de vignettes 4/3 (160 px au moins), dans l'ordre choisi par le prestataire ; un clic ouvre la photo en grand dans un nouvel onglet. Les photos s'ajoutent depuis « Mon profil » (`RM-PROPOSER-IHM.md`).

## Page `/prestataires/12`
Ouverte à tous, même sans compte. Visible seulement si l'activité du prestataire est active (sinon « Ce prestataire n'existe pas. ») ; son auteur la voit toujours. On y arrive depuis les résultats de recherche ou le nom du prestataire sur la page d'une annonce.

1. [‹ Retour] : la page d'avant (les résultats) ; ouverte directement par un lien : la recherche.
2. (auteur) bandeau orange « Votre page, telle que les clients la voient. » + lien « Mon activité ».
3. Carte du profil : grande photo ronde (ou initiales) ; nom + badge vert « SIRET vérifié » ; « ★ 4,5 (8 avis) » ou badge « Nouveau sur rafals » ; « Plombier · aussi Électricien » (métiers exercés) ; le lieu des services, selon le profil (lot 9.1, 08/10/2026 ; texte dans `outils/prestataires.ts`) : « Part de Pessac, se déplace jusqu'à 20 km » (chez le client), « Vous reçoit à Pessac (adresse donnée après un rendez-vous) » (chez lui), ou « Part de Pessac, se déplace jusqu'à 20 km, ou vous reçoit à Pessac » (les deux) ; (s'il y en a, lot 4.6) bandeau orange « 1 absence sans prévenir ces 6 derniers mois » ; présentation.
4. ~~Carte « Ses annonces »~~ **retirée le 08/10/2026** (Raphael : « sur le profil je ne comprend pas ce que c'est ses annoces du coup » ; les annonces sont retirées, `RM-PRESTATAIRES.md` § « Sans annonces »). La page d'une annonce existe encore par son adresse `/annonces/12` jusqu'au lot 9.3.
5. Carte « Avis » (lot 4.8) : voir `RM-AVIS-IHM.md`.
6. « Le téléphone et l'adresse sont donnés après une réservation. » — jamais de téléphone, de mail ni de rue sur cette page.

## [Signaler ce prestataire…] (lot 6.4, 04/10/2026)
En bas de la page, à droite (absent sur son propre profil) : voir `RM-SIGNALEMENTS-IHM.md`.

## [Écrire à Karim] (ajouté le 07/10/2026, lot 8.2)
Sous la présentation, un bouton principal **[Écrire à Karim]** (le prénom du nom affiché), absent sur sa propre page. Il ouvre la conversation avec ce prestataire dans « Messages » (`RM-MESSAGES-IHM.md`), ou la retrouve si elle existe déjà. Pas connecté → page de connexion. Refus de la règle (ex. « Ce prestataire n'est pas joignable en ce moment. ») : bandeau rouge sous le bouton.

## Étiquette « Particulier, non professionnel » (ajoutée le 12/10/2026, lot 11.2)
À côté du nom : badge vert « SIRET vérifié », ou sinon badge orange « Particulier, non professionnel » (règle 6 de `RM-PRESTATAIRES.md` § « Limites d'un prestataire sans SIRET »).
