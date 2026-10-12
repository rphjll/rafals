# Avis sur les clients — Interface (noter un client, page publique d'un client, « Mes avis reçus »)

> Fichiers : `frontend/src/pages/AvisClientPage.vue`, `frontend/src/pages/MesAvisRecusPage.vue`, `frontend/src/components/avis/FenetreAvis.vue` (la même fenêtre que pour noter un prestataire), carte « Rendez-vous passé » de `frontend/src/pages/MessagesPage.vue`, `frontend/src/outils/avis.ts`. Construit le 12/10/2026 (lot 8.6), d'après la maquette validée `maquette-niveau-8-demandes.html`. Règles : `RM-AVIS.md` § « Notation dans les deux sens ».

## La carte « Rendez-vous passé » dans une conversation
Dès qu'un rendez-vous entre les deux personnes est passé (et pendant 30 jours), une carte apparaît toute seule dans le fil de « Messages », chez le client et chez le prestataire, à la place du moment où le rendez-vous a fini :
1. En gris : « Rendez-vous passé · Fuite sous l'évier · 12/10/2026 ».
2. En gras : « Comment ça s'est passé avec Marie D. ? » (le client lit le nom du prestataire).
3. Bouton principal **[Noter Marie D.]** et, à côté, « encore 25 jours ». Une fois l'avis laissé : badge vert « avis laissé », carte grisée.

[Noter…] ouvre la fenêtre « Votre avis sur Marie D. » : les 5 étoiles cliquables, « Votre avis * » (10 à 500 caractères pour un client, avec l'aide « Signé de votre nom affiché, visible sur la page publique de ce client. »), [Publier mon avis] et [Annuler] → message « Merci : votre avis est publié. » ; refus de la règle en bandeau rouge dans la fenêtre.

## La note à côté d'un nom
- **Carte d'une demande** : sous « Marie D. », en orange « 5,0 ★ · 1 avis » et le lien « Voir les avis » → sa page publique. Sans avis : rien.
- **En haut d'une conversation** : sous le nom, « 4,8 ★ · 6 avis » et « Voir les avis » (la page publique du client pour le prestataire ; la fiche du prestataire pour le client). Sans avis : « Aucun avis pour l'instant », sans lien.

## Page publique d'un client (`/clients/12/avis`)
Ouverte à tous, même sans compte ; elle demande aux moteurs de recherche de ne pas l'enregistrer. Contenu centré, 760 px au plus.
1. [‹ Retour].
2. Un cadre : un rond avec les initiales, « Marie D. » en titre, « Membre depuis septembre 2026 », puis en gras « 5,0 ★ · 1 avis » (ou « Aucun avis pour l'instant »).
3. Cadre « Les avis des prestataires » : pour chaque avis, les étoiles en orange, « Karim Benali · octobre 2026 », le texte, et dans un encadré gris « Réponse de Marie D. : … » s'il y en a une. Sans avis : « Aucun avis pour l'instant. »
4. Compte fermé ou numéro inconnu : bandeau rouge « Cette personne n'est pas (ou plus) sur rafals. »

Jamais affichés : le nom complet, la ville, l'adresse, le téléphone, le mail, les demandes, les rendez-vous.

## Mes avis reçus (`/mes-avis-recus`)
« Mon activité » → « Mes avis reçus », pour tout le monde. Contenu centré, 760 px au plus.
1. Titre « Mes avis reçus » et, à droite, [Voir ma page publique].
2. « Après un rendez-vous, le prestataire peut vous noter, comme vous le notez. Ces avis sont visibles de tous, avec votre prénom et l'initiale de votre nom. »
3. Une carte par avis, le plus récent en haut : étoiles, « Karim Benali · octobre 2026 · « Fuite sous l'évier » », un badge orange « signalé » ou gris « caché par l'administrateur », le texte, « Votre réponse : … » s'il y en a une, puis [Répondre…] (une seule fois) et [Signaler…] (rouge). Un avis caché affiche « Cet avis n'est plus affiché ni compté. Motif : « … ». », sans bouton.
4. [Répondre…] et [Signaler…] ouvrent la fenêtre à un seul texte → « Réponse publiée. » / « Avis signalé : l'administrateur va le regarder. »
5. Liste vide : « Aucun avis pour l'instant. » ; pas connecté : « Connectez-vous pour voir vos avis reçus. » et [Se connecter].

## Pas encore fait
- (Fait le 12/10/2026 : dans « Mon activité », la tuile « Mes avis reçus » porte une pastille rouge avec le nombre d'avis arrivés depuis la dernière visite.)
- Le bouton [Noter Marie D.] sur la ligne du rendez-vous passé dans « Mon agenda › Rendez-vous » (la carte de la conversation le fait déjà).
- Pour le prestataire : modifier ou retirer son avis depuis l'écran (le serveur sait le faire).
- (Fait le 12/10/2026 : Administration › Avis signalés montre aussi les avis sur un client signalés, avec le badge « avis sur un client, signalé » ; [Le laisser] ou [Le cacher…], le motif part au prestataire qui l'a écrit.)
