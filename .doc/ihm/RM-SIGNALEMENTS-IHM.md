# Signalements — Interface

> **Changé le 09/10/2026** (lot 9.3, retrait des annonces) : on ne signale plus une annonce. `BoutonSignaler` n'a plus qu'une forme, [Signaler ce prestataire…], en bas de la page publique. Dans Administration › Signalements : plus de ligne « Annonce », plus de bouton [Retirer l'annonce…] ; il reste [Rien à faire] et [Bloquer le prestataire…] (et [Prévenir…] pour une conversation).

> Fichiers : `frontend/src/components/BoutonSignaler.vue` (commun à l'annonce et à la page du prestataire), `frontend/src/components/admin/OngletSignalements.vue` ; fenêtre commune `FenetreTexte`. Construit au lot 6.4 (04/10/2026). Règles : `RM-ADMINISTRATION.md`. Maquette validée : `maquette-lot-6.4-signalements-rappels.html`.

## Signaler une annonce (page d'une annonce) ou un prestataire (sa page publique)
Bouton danger, en bas à droite : [Signaler cette annonce…] (sous la carte de l'annonce ; absent sur sa propre annonce) ou [Signaler ce prestataire…] (en bas de la page ; absent sur son propre profil). Pas connecté : « Connectez-vous pour signaler une annonce : vous reviendrez ici. » puis la connexion.
Fenêtre « Signaler cette annonce ? » / « Signaler Léa Martin ? » : « L'administrateur de rafals regardera. Karim Benali ne saura pas qui a signalé. » ; « Le problème * » (compteur « 0 / 1000 », aide « ex. « Prix mensonger, il demande 80 € sur place ». De 10 à 1000 caractères. ») ; erreur du serveur dans la fenêtre (ex. « Vous l'avez déjà signalé : l'administrateur va regarder. ») ; [Signaler] (danger) → « Merci : l'administrateur va regarder. » ; [Annuler].

## Administration › « Signalements » (`?onglet=signalements`, compteur orange)
Une carte par signalement à traiter, le plus ancien d'abord : titre « Annonce « Plomberie » · Karim Benali » (ou « Léa Martin ») + badge orange « annonce signalée » / « prestataire signalé » ; « Signalé par » (« Paul Petit, le 04/10/2026 à 9 h 12 ») ; « Annonce » (« en ligne » + [Voir l'annonce]) ; « Prestataire » (« actif · déjà signalé 1 fois » + [Voir sa page]) ; bandeau orange avec le motif.
- [Rien à faire] (secondaire) → « Signalement classé. »
- [Retirer l'annonce…] (danger, si l'annonce n'est pas déjà retirée) → fenêtre « Retirer l'annonce « Plomberie » ? » (« Elle ne sera plus visible. Le motif est envoyé à Karim Benali (sans le nom de celui qui a signalé). Rien n'est effacé. » ; « Motif * ») → « Annonce retirée : Karim Benali est prévenu. »
- [Bloquer le prestataire…] (danger, s'il n'est ni bloqué ni arrêté) → fenêtre « Bloquer Karim Benali ? » (« Son profil et ses annonces disparaissent des recherches, ses rendez-vous à venir sont annulés et ses clients prévenus. Le motif lui est envoyé. » ; « Motif * ») → « Prestataire bloqué. »
- Vide : « Aucun signalement à traiter. » Le tableau de bord affiche aussi le bouton « 2 signalements ».

## Demande signalée (ajouté le 12/10/2026, lot 8.5)
Dans Administration › Signalements, une demande signalée par un prestataire a sa carte : titre « Marie Dupont (client) », badge orange « demande signalée », « Signalé par Karim Benali, le 12/10/2026 à 22 h 10 », puis dans un encadré gris le titre et le texte de la demande, puis le motif entre guillemets.
- [Rien à faire] : le signalement est classé, la demande reste en ligne.
- [Cacher la demande…] (rouge) : fenêtre « Cacher « Fuite sous l'évier » ? » avec le motif à écrire (5 caractères au moins) → « Demande cachée. » La demande quitte l'accueil ; le client la voit encore dans « Mes demandes » avec le badge rouge « cachée par l'administrateur » et reçoit le motif par mail, jamais le nom de celui qui a signalé.
- Le badge dit maintenant « prestataire signalé », « client signalé » (conversation) ou « demande signalée » ; [Voir sa page] n'apparaît que pour un prestataire.
