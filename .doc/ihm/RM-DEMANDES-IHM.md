# Demandes — Interface (carte d'une demande, « Mes demandes », « Demandes près de chez moi »)

## Depuis le 10/11/2026 : identique à la grande maquette (lots 14.5 et 14.6)

Demande de Raphael, mot pour mot : « je veux que ca soit exactement pareil que la maquette et tu fais l'agenda pareil que la maquette ». Maquette : `.doc/ihm/maquette-site-complet.html`. Les styles de la maquette sont recopiés dans `frontend/src/style.css` ; les sections plus bas décrivent le fonctionnement, qui ne change pas sauf mention ici.

- Haut : « Demandes », « Les besoins publiés près de chez vous. Tout le monde peut les voir. », bouton vert **[+ Publier une demande]** (→ /demandes/nouvelle).
- **Carte d'une demande publique** : pastille orange du métier et date ; titre ; « 📍 Pessac · Dès que possible · chez le client · prix à proposer » ; le texte ; les photos (connecté) ; en bas, le rond et le nom du client (« particulier · 0 réponse sur 10 ») et [Répondre], [🔒 Répondre] ou [Voir la conversation], puis « Signaler… » en lien discret.
- **Mes demandes** : « En cours » puis « Terminées » ; chaque demande repliée en une ligne (état, titre, « métier · ville · publiée le », « 2 réponses », ›) ; ouverte : le texte, « Pour quand », la phrase en gras (ouverte jusqu'au…, rendez-vous pris…), « 2 prestataires vous ont répondu » + [Lire leurs messages], puis [Modifier…] [Prolonger de 30 jours] [Fermer ma demande…] (ou [Rouvrir pour 30 jours]).
- **Page « Publier une demande »** (/demandes/nouvelle, `pages/NouvelleDemandePage.vue`, formulaire `CartePublierDemande.vue`) : « ‹ Mes demandes », titre, puis le formulaire : **« De quoi avez-vous besoin ? »** et dessous **« ✓ Métier trouvé : Plombier · [Changer] »**, trouvé tout seul d'après les mots écrits (`outils/devineMetier.ts`, la liste de mots de la maquette reliée aux vrais métiers ; ex. « Fuite sous l'évier » → Plombier, « Réparer mon PC » → Dépannage informatique) ; aucun mot reconnu : « Nous n'avons pas reconnu le métier. [Choisir le métier] ». Puis Détails (20 caractères au moins), Pour quand ?, Où ? (adresse et plan), Le service a lieu (Chez moi / Chez le prestataire), Budget, Photos, [Publier ma demande] → « Mes demandes ».


> **Changé le 22/10/2026** (demande de Raphael : « fait en sort que le site resemble a ce que t'a fais dans la maquette », maquette https://claude.ai/artifact/Qix7D7jo4vJ9kpWotB59Q2, `.doc/ihm/maquette-site-complet.html`) : sur la carte d'une demande, le rond des initiales (quand il n'y a pas de photo) prend une teinte propre au nom, la même partout (composant `AppInitiales`, ex. « Marie D. » toujours dans la même couleur) ; avant : toujours vert clair.

> **Changé le 21/10/2026** (Raphael : « faudrai quand meme que y'ai le bouton grisé avec un cadenas et les explications ») : sur une carte de demande, un prestataire qui ne peut pas répondre voit toujours **[🔒 Répondre]** grisé ; un clic affiche la raison (`services/propositions.py`, `raison_verrou`) : autre métier (« Cette demande est pour « Coiffeur / Coiffeuse » : vous ne répondez qu'aux demandes de vos métiers (Électricien). Si vous exercez aussi ce métier, ajoutez-le dans « Mon profil ». »), trop loin (« Cette demande est à 38 km de Pessac : vous vous déplacez jusqu'à 15 km. Vous pouvez agrandir cette distance dans « Mon profil ». »), activité en pause (« Votre activité est en pause : reprenez-la dans « Mon profil » pour répondre aux demandes. »), pas d'adresse, limites sans SIRET, demande complète. Avant : pas de bouton du tout pour un autre métier ou trop loin.

> Fichiers : `frontend/src/components/demandes/CarteDemande.vue`, `frontend/src/pages/MesDemandesPage.vue`, `frontend/src/pages/DemandesPresPage.vue`, `frontend/src/outils/demandes.ts`. Construit le 07/10/2026 (lot 8.4), d'après la maquette validée `maquette-niveau-8-demandes.html`. Règles : `RM-DEMANDES.md`. Publier une demande : `RM-ACCUEIL-IHM.md`.

## Onglet « Demandes » (`/demandes`, lot 14.2, 10/11/2026, grande maquette)
Remplace les pages « Mes demandes » et « Demandes près de chez moi » décrites plus bas : leurs adresses y mènent (`/mes-demandes` → onglet « Mes demandes », `/demandes-pres-de-chez-moi` → « Près de chez moi »). Entrée « Demandes » dans le menu et la barre du bas, entre « Trouver » et « Messages », visible même sans compte.
1. Titre « Demandes », phrase « Les besoins publiés près de chez vous. Tout le monde peut les voir. », bouton orange [Publier une demande] → l'accueil (carte « Publier une demande ») ou la connexion.
2. Deux sous-onglets (`AppOnglets`, `?onglet=miennes`) :
   - **« Près de chez moi »** : « 4 demandes en ligne. » (+ « Vous pouvez répondre à celles de vos métiers, dans votre zone. » pour un prestataire), puis les cartes des demandes des autres (`CarteDemande`, la même que l'accueil : [Répondre] ou [🔒 Répondre] avec la raison). **Ses propres demandes n'y sont pas** (demande de Raphael du 09/11/2026 sur la maquette).
   - **« Mes demandes (3) »** : sans compte, « Connectez-vous pour voir vos demandes. » ; sinon la liste `ListeMesDemandes` **repliée** : une ligne par demande (état, titre, « Peintre · Nantes · publiée le 03/11/2026 », « 2 réponses », ›) ; un clic la remplace par la carte entière avec ses boutons (Modifier, Prolonger, Fermer…) et un lien « ‹ Replier » au-dessus. Une seule ouverte à la fois. L'accueil garde la liste dépliée.
3. Dans « Mon activité », la tuile « Mes demandes » est retirée (elle est dans l'onglet) ; « Demandes près de chez moi » et les chiffres mènent à l'onglet.

## Carte d'une demande (la même partout)
**Redessinée le 07/10/2026 en style « chaleureux »** (carte blanche à ombre, classe `carte`). De haut en bas :
1. Une ligne « qui demande » : un rond vert clair avec les initiales du client (« MD »), son nom (« Marie D. ») et dessous, en gris, « Pessac · 07/10/2026 » (ville et jour de publication) ; à droite, le budget dans une pastille verte (« 40 € »), ou une pastille claire « Prix à proposer » s'il n'y en a pas.
2. Le titre en gras, puis la description en gris.
3. Les photos en vignettes de 96 px, cliquables (seulement connecté).
4. Des badges gris : « Plombier », « Dès que possible » (ou « samedi 10 octobre »), « Chez le client » (ou « Chez le prestataire »), « 2 réponses sur 10 » ; un badge vert « Ma demande » sur les siennes ; sans compte et avec des photos : « 2 photos (connectez-vous pour les voir) ». La ville n'est plus un badge (elle est en haut).
5. Les boutons :
   - prestataire qui peut répondre (son métier, son rayon, pas complète) : **[Répondre]** → ouvre la conversation avec le client (`RM-MESSAGES-IHM.md`) ;
   - prestataire qui a déjà répondu : [Voir la conversation] ;
   - prestataire **sans adresse** dans son compte, pour une demande de ses métiers (15/10/2026) : [Répondre] verrouillé 🔒 « Ajoutez votre adresse dans « Mon profil » : les demandes près de chez vous se calculent depuis elle. » ;
   - prestataire **sans SIRET** que la demande concerne mais qu'une limite arrête (ajouté le 12/10/2026) : [Répondre] verrouillé 🔒 avec la raison, ex. « « Plombier » demande un SIRET : créez votre auto-entreprise… », « Sans SIRET, avant de répondre : indiquez votre adresse et cochez « Mon activité est occasionnelle… » dans « Mon profil ». », « Vous avez atteint la limite des particuliers (1 000,00 € sur 12 mois)… » ;
   - prestataire, demande complète : [Répondre] verrouillé 🔒 « Cette demande est complète : 10 prestataires ont déjà répondu. » ;
   - les autres (clients, prestataires d'un autre métier ou trop loin) : aucun bouton ;
   - puis les boutons propres à la page (« Mes demandes »).
7. Réponse refusée : bandeau rouge dans la carte.

## Mes demandes (`/mes-demandes`)

> 21/10/2026 : la liste est le composant `ListeMesDemandes`, montré aussi dans l'onglet « Mes demandes » de l'accueil (`RM-ACCUEIL-IHM.md`).
Sous-menu « Mes réservations », premier onglet. Contenu centré, 760 px au plus.
1. Titre « Mes demandes » et, à droite, [Publier une demande] → l'accueil.
2. Une carte par demande, la plus récente en haut, avec en plus :
   - un badge d'état : ouverte (vert), pourvue : prestataire choisi (vert), fermée (gris), expirée (orange), cachée par l'administrateur (rouge) ;
   - **ouverte** : « Ouverte jusqu'au 06/11/2026 à 11 h 40. », [Prolonger de 30 jours] → « Demande prolongée de 30 jours. », [Fermer ma demande…] (rouge) → fenêtre « Fermer « Tondre ma pelouse » ? Les prestataires ne la verront plus et ne pourront plus y répondre. Elle reste dans « Mes demandes ». » → « Demande fermée. » ;
   - **expirée** : [Rouvrir pour 30 jours] ;
   - **pourvue** : [Voir le rendez-vous] → « Mes réservations », et [Rouvrir (rendez-vous annulé)] (refusé avec le message de la règle si le rendez-vous est toujours prévu).
3. Liste vide : « Aucune demande pour l'instant. Publiez-en une depuis l'accueil : les prestataires proches vous répondent. »
4. Pas connecté : bandeau gris « Connectez-vous pour voir vos demandes. » et [Se connecter].

**[Modifier…]** (ajouté le 12/10/2026) : sur une demande ouverte, à gauche de [Prolonger de 30 jours]. Fenêtre « Modifier ma demande » (`FenetreModifierDemande.vue`) : rappel « Plombier · Pessac. Pour changer le métier, l'adresse ou les photos, fermez cette demande et publiez-en une autre. », puis « Titre * », « Décrivez votre besoin * », « Pour quand ? * » (et « Quel jour ? * »), « Budget en euros (facultatif) », [Enregistrer] et [Annuler] → message « Demande modifiée. » ; refus de la règle en bandeau rouge dans la fenêtre. Dès qu'un prestataire a répondu, le bouton est verrouillé 🔒 : « Un prestataire a déjà répondu : pour changer cette demande, fermez-la et publiez-en une autre. »

## Demandes près de chez moi (`/demandes-pres-de-chez-moi`)
Sous-menu « Mon activité », deuxième onglet ; réservée aux prestataires (même gardien que « Mon agenda »).
1. Titre, puis « Les demandes de vos métiers, dans votre rayon autour de votre adresse. Répondre est gratuit ; rafals garde 5 % seulement si le client paie par carte. »
   - **Sans adresse dans son compte** (15/10/2026) : à la place de la liste, cadre en pointillés « Vous n'avez pas encore d'adresse : rafals ne sait pas où vous êtes, donc ne peut pas vous montrer les demandes près de chez vous. » + bouton **[Ajouter votre adresse]** → « Mon profil » (carte « Mon adresse »).
2. Une carte par demande à laquelle ce prestataire peut répondre, la plus récente en haut.
3. Liste vide : « Aucune demande ouverte pour vos métiers près de chez vous en ce moment. »

Pas encore fait : la distance (« à 5 km »), [Signaler] une demande, la note du client (lots 8.5 et 8.6).

## Note du client sur la carte d'une demande (ajoutée le 12/10/2026, lot 8.6)
Sous le nom du client : « 5,0 ★ · 1 avis » en orange et le lien « Voir les avis » → `/clients/12/avis` (`RM-AVIS-CLIENTS-IHM.md`). Rien si le client n'a aucun avis.

## [Signaler…] une demande (ajouté le 12/10/2026, lot 8.5)
Sur la carte d'une demande, pour un prestataire (jamais sur sa propre demande) : bouton secondaire [Signaler…], après [Répondre]. Il ouvre la fenêtre à un seul texte « Signaler « Fuite sous l'évier » » : « Demande fausse, hors sujet ou contraire à la loi : l'administrateur de rafals la regarde. Votre nom n'est pas donné au client. », « Que se passe-t-il ? * » (10 à 1000 caractères) → message « Demande signalée : l'administrateur va regarder. » ; déjà signalée par lui : « Vous l'avez déjà signalée : l'administrateur va regarder. »
