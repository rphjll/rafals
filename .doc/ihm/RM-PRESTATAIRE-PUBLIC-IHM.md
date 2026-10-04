# Page publique d'un prestataire — Interface

> Fichiers : `frontend/src/pages/PrestatairePage.vue`, `frontend/src/components/prestataire/AvatarPrestataire.vue`. Construit au lot 4.2 (30/09/2026). Règles : `RM-RECHERCHE.md` (précisions du lot 4.1). Maquette : `maquette-lot-4.2-recherche.html` (écran 3).

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
