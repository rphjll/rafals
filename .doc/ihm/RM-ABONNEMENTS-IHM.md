# Mes abonnements et bouton [S'abonner] — Interface

## Depuis le 10/11/2026 : identique à la grande maquette (lots 14.5 et 14.6)

Demande de Raphael, mot pour mot : « je veux que ca soit exactement pareil que la maquette et tu fais l'agenda pareil que la maquette ». Maquette : `.doc/ihm/maquette-site-complet.html`. Les styles de la maquette sont recopiés dans `frontend/src/style.css` ; les sections plus bas décrivent le fonctionnement, qui ne change pas sauf mention ici.

- « Mes abonnements » : une ligne par prestataire suivi (rond, nom, « Métier · Ville · ★ 4,8 · muet »), à droite [Rendre muet] (ou [Réactiver]), [Se désabonner] (caché sur téléphone) et [›] vers sa page. Personne : « Vous ne suivez personne » + [Trouver un prestataire].
- [S'abonner] n'est plus sur les cartes de « Trouver » : il est sur la page du prestataire ([♡ S'abonner] blanc, [✓ Abonné] vert pâle).


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
- Titre « Mes abonnements », phrase « Les prestataires que vous suivez. Ce qui vous est envoyé se choisit dans **Paramètres**, pour tous à la fois. » (« Paramètres » est un lien vers `/parametres#abonnements`).
- Grille de petites cartes, le plus récent d'abord : photo ronde ou initiales, nom, métier principal, ville, « ★ 4,8 » s'il a des avis, « 12 abonnés ». Un clic sur le haut de la carte ouvre sa fiche.
- Profil en pause, bloqué ou arrêté : carte grisée, étiquette orange « Profil en pause », pas de lien (sa fiche est cachée).
- **21/10/2026** (Raphael : « on vas faire encore plus simple en gros dans parametre on coche par défaut et dans abonnement au lieux de choisir qui fais quoi ou quoi juste on met un bouton rendre muet ou un truc tres simple le plus compréhensible possible pour dire que je ne veux plus recevoir de notif de la par de cet personne ou de plusieurs si il en a mut plusieurs ») : la cloche et ses 3 cases par prestataire sont retirées. À la place, un seul bouton secondaire **[🔕 Rendre muet]**. Un clic : badge gris « 🔕 Muet » sous le nom, le bouton devient **[🔔 Réactiver les notifications]**, message « Karim Benali est en muet : plus aucune notification. » (ou « Notifications de Karim Benali réactivées. »). Effet immédiat ; en cas d'échec, le bouton revient comme avant et le message d'erreur s'affiche. Les 3 cases sont dans « Paramètres » (`RM-PARAMETRES-IHM.md`).
- [Se désabonner] (secondaire) : la carte disparaît, message « Vous ne suivez plus Karim Benali ».
- Liste vide : « Vous ne suivez encore personne. Sur la carte d'un prestataire, appuyez sur [S'abonner]. » et [Trouver un prestataire].
- Pas connecté : bandeau rouge « Vous n'êtes pas connecté. ».
