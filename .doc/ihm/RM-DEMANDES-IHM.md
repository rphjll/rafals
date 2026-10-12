# Demandes — Interface (carte d'une demande, « Mes demandes », « Demandes près de chez moi »)

> Fichiers : `frontend/src/components/demandes/CarteDemande.vue`, `frontend/src/pages/MesDemandesPage.vue`, `frontend/src/pages/DemandesPresPage.vue`, `frontend/src/outils/demandes.ts`. Construit le 07/10/2026 (lot 8.4), d'après la maquette validée `maquette-niveau-8-demandes.html`. Règles : `RM-DEMANDES.md`. Publier une demande : `RM-ACCUEIL-IHM.md`.

## Carte d'une demande (la même partout)
**Redessinée le 07/10/2026 en style « chaleureux »** (carte blanche à ombre, classe `carte`). De haut en bas :
1. Une ligne « qui demande » : un rond vert clair avec les initiales du client (« MD »), son nom (« Marie D. ») et dessous, en gris, « Pessac · 07/10/2026 » (ville et jour de publication) ; à droite, le budget dans une pastille verte (« 40 € »), ou une pastille claire « Prix à proposer » s'il n'y en a pas.
2. Le titre en gras, puis la description en gris.
3. Les photos en vignettes de 96 px, cliquables (seulement connecté).
4. Des badges gris : « Plombier », « Dès que possible » (ou « samedi 10 octobre »), « Chez le client » (ou « Chez le prestataire »), « 2 réponses sur 10 » ; un badge vert « Ma demande » sur les siennes ; sans compte et avec des photos : « 2 photos (connectez-vous pour les voir) ». La ville n'est plus un badge (elle est en haut).
5. Les boutons :
   - prestataire qui peut répondre (son métier, son rayon, pas complète) : **[Répondre]** → ouvre la conversation avec le client (`RM-MESSAGES-IHM.md`) ;
   - prestataire qui a déjà répondu : [Voir la conversation] ;
   - prestataire **sans SIRET** que la demande concerne mais qu'une limite arrête (ajouté le 12/10/2026) : [Répondre] verrouillé 🔒 avec la raison, ex. « « Plombier » demande un SIRET : créez votre auto-entreprise… », « Sans SIRET, avant de répondre : indiquez votre adresse et cochez « Mon activité est occasionnelle… » dans « Mon profil ». », « Vous avez atteint la limite des particuliers (1 000,00 € sur 12 mois)… » ;
   - prestataire, demande complète : [Répondre] verrouillé 🔒 « Cette demande est complète : 10 prestataires ont déjà répondu. » ;
   - les autres (clients, prestataires d'un autre métier ou trop loin) : aucun bouton ;
   - puis les boutons propres à la page (« Mes demandes »).
7. Réponse refusée : bandeau rouge dans la carte.

## Mes demandes (`/mes-demandes`)
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
1. Titre, puis « Les demandes de vos métiers, dans votre rayon. Répondre est gratuit ; rafals garde 5 % seulement si le client paie par carte. »
2. Une carte par demande à laquelle ce prestataire peut répondre, la plus récente en haut.
3. Liste vide : « Aucune demande ouverte pour vos métiers près de chez vous en ce moment. »

Pas encore fait : la distance (« à 5 km »), [Signaler] une demande, la note du client (lots 8.5 et 8.6).

## Note du client sur la carte d'une demande (ajoutée le 12/10/2026, lot 8.6)
Sous le nom du client : « 5,0 ★ · 1 avis » en orange et le lien « Voir les avis » → `/clients/12/avis` (`RM-AVIS-CLIENTS-IHM.md`). Rien si le client n'a aucun avis.

## [Signaler…] une demande (ajouté le 12/10/2026, lot 8.5)
Sur la carte d'une demande, pour un prestataire (jamais sur sa propre demande) : bouton secondaire [Signaler…], après [Répondre]. Il ouvre la fenêtre à un seul texte « Signaler « Fuite sous l'évier » » : « Demande fausse, hors sujet ou contraire à la loi : l'administrateur de rafals la regarde. Votre nom n'est pas donné au client. », « Que se passe-t-il ? * » (10 à 1000 caractères) → message « Demande signalée : l'administrateur va regarder. » ; déjà signalée par lui : « Vous l'avez déjà signalée : l'administrateur va regarder. »
