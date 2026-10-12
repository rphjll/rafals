# Mon activité — Interface

> Fichiers : `frontend/src/pages/MonActivitePage.vue`, `frontend/src/outils/activite.ts` (la liste des fonctions), `frontend/src/composables/useMenu.ts`. Construit le 07/10/2026 (hors lot), d'après la maquette `maquette-mon-activite.html` (https://claude.ai/artifact/DURJoPoweoC7WLU7RUh4wu).
> Demande de Raphael du 07/10/2026, mot pour mot : « tu vois l'onglet abonnement de allo voisin avec beacoup de trucs dedans et bah tout ces trucs qui y'a dans mon compte bah je veux le mettre aussi dans 1 seul onglet qui s'appelera mon activité et l'onglet actuel mon activité il vas s'appeler mon profil », puis « y'en a quelques uns qui ne doivent pas etre dans mon activité par exemple messages c'est un onglet a pars », puis, sur la liste des 12 fonctions : « la cb la liste que tu m'a donné est bonne ».

## Où
- Entrée « Mon activité » du menu → `/mon-activite`. Elle remplace « Mes réservations » (choix de Raphael le 07/10/2026 : « Elle disparaît »).
- L'ancienne entrée « Mon activité » (la fiche du prestataire, `/proposer`) s'appelle **« Mon profil »** ; pour un compte sans profil de prestataire, elle s'appelle toujours « Proposer mes services ».
- « Messages » et « Mon profil » ne sont pas dans la page : ce sont des onglets à part.

## La page
De haut en bas :
1. Titre « Mon activité » et la phrase « Tout ce que vous faites sur rafals, au même endroit. »
2. Personne n'est connecté : bandeau gris « Connectez-vous pour voir votre activité. » et [Se connecter] (qui ramène ici après la connexion).
2 bis. **Les chiffres** (lot 10.1, construit le 07/10/2026 ; règles : `RM-MON-ACTIVITE.md`), lus sur `/api/moi/activite` à chaque ouverture de la page. Une petite carte par chiffre, le nombre en très gros et le texte en gris dessous ; 2 par ligne sur téléphone, 4 sur ordinateur ; un clic ouvre la page du détail. Si le serveur ne répond pas, la page s'affiche sans les chiffres.
   - Prestataire : « 3 » demandes près de chez vous → Demandes près de chez moi ; « 2 » rendez-vous d'ici dimanche → Mon agenda, onglet Rendez-vous ; « 1 » devis en attente de réponse → Devis ; « 640,00 € » encaissés en octobre → Mon agenda, onglet Paiements. Le texte s'accorde (« 1 demande près de chez vous »).
   - Dessous, pour un prestataire, une carte « Encaissé en 2026 » avec la somme à droite (« 5 320,00 € ») ; s'il ne facture pas la TVA, une barre verte remplie à la part du seuil atteinte et « Il vous reste 32 180,00 € avant le seuil de TVA (37 500,00 €). » ; seuil dépassé : barre pleine orange et « Vous avez dépassé le seuil de TVA (37 500,00 €) : parlez-en à votre comptable ou à votre service des impôts. » ; toujours la ligne « Seulement ce qui est passé par rafals : ajoutez vous-même ce que vous avez encaissé ailleurs. »
   - Client : « 1 » demande en ligne → Mes demandes ; « 2 » conversations à lire → Messages ; « 1 » rendez-vous à venir → Rendez-vous.
3. Des groupes de tuiles. Une tuile = un rond de couleur avec un pictogramme, le nom en gras, une ligne grise. Un clic ouvre la page. Survol : anneau vert.

| Groupe | Tuile | Ligne grise | Ouvre | Qui la voit |
|---|---|---|---|---|
| Trouver des clients | Demandes près de chez moi | Les clients qui cherchent mon métier | `/demandes-pres-de-chez-moi` | prestataire |
| | Alertes | Un mail à chaque nouvelle demande | *bientôt* (lot 8.6) | prestataire |
| | Être mis en avant | Apparaître en premier dans les résultats | *bientôt* (à construire) | prestataire |
| Gérer mon activité (pour un client : « Mes services ») | Mes demandes | Ce que j'ai publié, et les réponses | `/mes-demandes` | tous |
| | Mon agenda | Mes rendez-vous, mes horaires, mes jours fermés | `/mon-agenda` | prestataire |
| | Mon agenda | Le calendrier de mes rendez-vous | `/mon-agenda` | client |
| | Devis | Demandes de devis et devis envoyés | `/devis` | tous |
| | Factures | Toutes mes factures en PDF | `/factures` | tous |
| | Paiements | Ce que j'ai encaissé, par carte et en espèces | `/mon-agenda?onglet=paiements` | prestataire |
| | Paiements | Ce que j'ai payé par carte | `/compte` | client |
| | Mes clients | Les personnes pour qui j'ai déjà travaillé | `/mes-clients` (lot 10.2, 07/10/2026) | prestataire |
| | Mes avis | À donner après un rendez-vous passé | `/mon-agenda` | client |
| Me faire connaître | Mes avis | Ce que mes clients disent de moi | sa page publique `/prestataires/12` | prestataire |
| | Ma carte de visite | À imprimer, avec un carré à scanner | *bientôt* (à construire) | prestataire |
| | Mon site | Une page à mon nom, visible sur Google | *bientôt* (lots 6.5 et 6.6) | prestataire |
| Mes démarches | Déclarer à l'URSSAF | Mes déclarations et leurs rappels | `/demarches` | prestataire |
| | Mon auto-entreprise | La créer et suivre mon dossier | `/creer-mon-auto-entreprise` | prestataire |

4. **Tuile « bientôt »** (fonction pas encore construite) : contour en pointillés, badge orange « bientôt ». Un clic affiche le message court « « Alertes » n'est pas encore disponible : bientôt. » (un clic produit toujours quelque chose de visible).
5. Pour un compte sans profil de prestataire, en bas : bandeau gris « Vous proposez vos services ? Créez votre profil : les demandes des clients, l'agenda et les démarches s'ajoutent ici. » et [Proposer mes services].

Exemples : Julie (cliente) voit un seul groupe « Mes services » avec 6 tuiles (Mes demandes, Rendez-vous, Devis, Factures, Paiements, Mes avis). Karim (prestataire) voit 4 groupes et 15 tuiles, dont 4 « bientôt ».

**Changé le 07/10/2026** : la tuile « Rendez-vous » est retirée (demande de Raphael) ; les rendez-vous se voient dans « Mon agenda », en calendrier (`RM-AGENDA-IHM.md`). Julie voit donc toujours 6 tuiles (« Mon agenda » à la place de « Rendez-vous ») et Karim 14, dont 4 « bientôt ».

## Sous-menu
Sur une page de « Mon activité » (Rendez-vous, Devis, Mon agenda…), le sous-menu sous l'en-tête montre : « ‹ Mon activité » (retour à la page d'ensemble), puis Mes demandes, Rendez-vous, Devis, Factures, et pour un prestataire Demandes près de chez moi, Mon agenda, Déclarer à l'URSSAF. Pas de sous-menu sur la page d'ensemble.

## Page « Mes clients » (`/mes-clients`, lot 10.2)
> Fichier : `frontend/src/pages/MesClientsPage.vue`. Construit le 07/10/2026. Règles : `RM-MON-ACTIVITE.md` § « Mes clients ». Raphael a choisi « Tout le résumé » sur un dessin en texte de la liste (pas de maquette cliquable).

Réservée aux prestataires (pas connecté : [Se connecter] ; pas prestataire : [Proposer mes services]). Largeur 720 px. De haut en bas :
1. Titre « Mes clients » et, à droite, « 3 clients ».
2. Phrase grise : « Les personnes qui ont eu un rendez-vous ou un devis avec vous sur rafals. Le nom complet et le téléphone restent visibles 3 mois après le dernier rendez-vous. »
3. Au-delà de 10 clients : champ « Chercher un client » (ex. « Julie »), qui filtre sur le nom à chaque lettre. Aucun trouvé : « Aucun client ne s'appelle « zoé ». »
4. Une carte par client, le plus récent d'abord :
   - un rond vert clair avec ses initiales (« JM ») ;
   - son nom en gras (« Julie Martin », ou « Julie M. » quand les coordonnées ne sont plus visibles, ou « Personne ayant quitté rafals ») ;
   - une ligne « 2 rendez-vous · 1 devis (1 en attente) · 85,00 € payés » (les rendez-vous et les devis à zéro ne sont pas écrits ; la somme l'est toujours) ;
   - une ligne grise « Prochain rendez-vous : 10/10/2026 » (ou « Dernier rendez-vous : 28/05/2026 », ou « Pas encore de rendez-vous »), suivie de « · Tél. 06 12 34 56 78 » quand il est visible ;
   - à droite (dessous sur téléphone), le bouton secondaire **[Écrire à Julie]** → ouvre la conversation `/messages/12`. Refus (ex. conversation bloquée) : bandeau rouge sous la ligne de ce client. Pas de bouton pour un compte fermé.
4 bis. **Changé le 07/10/2026 : la ligne d'un client s'ouvre** (remplace les deux derniers tirets du point 4). Toute la ligne est un bouton, avec « ▾ » à droite ; le téléphone et [Écrire] ne sont plus sur la ligne. Un clic ouvre le détail dessous (« ▴ »), un 2ᵉ clic le referme ; un seul client ouvert à la fois ; le détail est lu sur le serveur au 1er clic (« Lecture… »). Le détail (`components/clients/DetailClient.vue`) montre :
   - « Téléphone », « Adresse », « Payé par rafals » ; téléphone caché : « caché (plus de 3 mois après le dernier rendez-vous, ou pas encore de rendez-vous) » ; adresse : « cachée », ou « pas de rendez-vous chez ce client » ;
   - « Vos rendez-vous ensemble » : une ligne par rendez-vous « 16/10/2026 · Plombier · 35,00 € · [à venir] » (badge vert « à venir », gris « passé ») ; aucun : « Pas encore de rendez-vous. » ;
   - « Vos devis pour Julie » (s'il y en a) : « 07/10/2026 · Devis D-2026-0001 · 315,00 € · [en attente de réponse] » ;
   - les boutons **[Écrire à Julie]** (principal ; pas pour un compte fermé) et **[Voir le profil]** (secondaire) → `/clients/12`.
5. Au-delà de 30 clients affichés : bouton [Voir les 30 suivants].
6. Liste vide : cadre en pointillés « Pas encore de client. Dès qu'un client confirme un rendez-vous ou reçoit un devis de votre part, il apparaît ici. »
Tri : fixé par le serveur (rendez-vous ou devis le plus récent d'abord).

## Page « Profil d'un client » (`/clients/12`)
> Fichier : `frontend/src/pages/ClientPage.vue`. Construit le 07/10/2026. Même mise en page que la page publique d'un prestataire (`RM-PRESTATAIRE-PUBLIC-IHM.md`), réservée aux prestataires qui ont ce client.

1. Lien « ‹ Mes clients ». Refus du serveur : bandeau rouge « Cette personne ne fait pas partie de vos clients. »
2. À gauche : un grand rond avec les initiales, le nom en très grand, « Client · sur rafals depuis octobre 2026 », puis la carte « Avec vous » qui reprend le même détail que dans « Mes clients ».
3. À droite (dessous sur téléphone), la carte vert foncé « Joindre Julie », qui reste visible : bouton orange [Écrire à Julie], le téléphone en gras s'il est visible, et la phrase « Son nom complet, son téléphone et son adresse restent visibles 3 mois après votre dernier rendez-vous. » Pas de carte pour un compte fermé.
4. Dessous : « Ses demandes en ligne » — une ligne par demande (« Tondre ma pelouse · Pessac », [Voir sur l'accueil]) ou « Julie n'a pas de demande en ligne en ce moment. »
« Mon activité » reste surlignée dans le menu, et le sous-menu est affiché.

## Pas encore fait (décidé par Raphael le 07/10/2026, une question par fonction)
- **Relance d'un devis sans réponse** (« Prévenir Julie tout seul ») : un seul mail au client au bout de 3 jours.
- **Ma carte de visite** (« Oui, carte de visite ») : un PDF à imprimer avec le nom, le métier, la ville, la note et un carré à scanner vers la page publique ; pas de prospectus.
- **Être mis en avant** (« Oui, maintenant ») : payer pour apparaître en premier ; règles (prix, durée, étiquette), MLD et paiement à écrire d'abord.
