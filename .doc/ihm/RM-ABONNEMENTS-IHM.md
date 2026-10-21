# Mes abonnements et bouton [S'abonner] — Interface

> Demande de Raphael du 21/10/2026. Règles : `regles-metier/RM-ABONNEMENTS.md`. Maquette validée le 21/10/2026 (« oui ») : https://claude.ai/artifact/2UDS81V5SaGwk2bn9zwgKH (`ihm/maquette-abonnements.html`).
> Fichiers : `frontend/src/pages/MesAbonnementsPage.vue`, `frontend/src/components/prestataire/BoutonAbonnement.vue`, `frontend/src/outils/abonnements.ts` ; le bouton est posé dans `components/recherche/CarteResultat.vue` et `pages/PrestatairePage.vue` ; l'entrée est dans `components/AppEntete.vue`.

## Bouton [S'abonner] / [Abonné ✓] (`BoutonAbonnement`, un seul pour tous les écrans)
- Pas abonné : fond vert, « S'abonner ». Abonné : fond vert clair, « Abonné ✓ ». Un clic bascule, avec le message court « Vous suivez Karim Benali » ou « Vous ne suivez plus Karim Benali » ; le nombre d'abonnés à côté change tout de suite.
- Pas connecté : message « Connectez-vous pour suivre Karim Benali : vous reviendrez ici. », puis la page de connexion, puis retour.
- Petit (36 px) sur les cartes de « Trouver un prestataire », normal (42 px) sur la fiche.
- Jamais sur sa propre carte ni sa propre fiche.

## Nombre d'abonnés
« 1 abonné », « 12 abonnés » : sous la ville sur la carte (rien quand il n'y en a aucun) ; à côté du bouton sur la fiche (« Aucun abonné pour l'instant » quand il n'y en a aucun). Visible par tous, même sans compte.

## Page `/mes-abonnements`
- On y arrive par la liste sous le prénom : « Mon profil », **« Mes abonnements »**, « Paramètres ».
- Titre « Mes abonnements », phrase « Les prestataires que vous suivez. La cloche choisit ce qui vous est envoyé sur votre téléphone. »
- Grille de petites cartes, le plus récent d'abord : photo ronde ou initiales, nom, métier principal, ville, « ★ 4,8 » s'il a des avis, « 12 abonnés ». Un clic sur le haut de la carte ouvre sa fiche.
- Profil en pause, bloqué ou arrêté : carte grisée, étiquette orange « Profil en pause », pas de lien (sa fiche est cachée).
- [🔔 Notifications · 2/3] : ouvre sous la carte les 3 cases (une seule carte ouverte à la fois) : « Créneau libre », « Nouveau métier », « Retour après une absence », chacune avec un exemple au nom du prestataire. Chaque clic est enregistré tout de suite (« Enregistré ») ; en cas d'échec, la case revient comme avant et le message d'erreur s'affiche.
- [Se désabonner] (secondaire) : la carte disparaît, message « Vous ne suivez plus Karim Benali ».
- Liste vide : « Vous ne suivez encore personne. Sur la carte d'un prestataire, appuyez sur [S'abonner]. » et [Trouver un prestataire].
- Pas connecté : bandeau rouge « Vous n'êtes pas connecté. ».
