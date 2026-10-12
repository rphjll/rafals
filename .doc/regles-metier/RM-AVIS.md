# Règle métier — Avis (sujet 09)

> Validé et formalisé le 30/09/2026 (lot 4.0).

## Objectif
Qui note un prestataire, quand, ce qui est montré, et ce qu'on fait d'un avis qui pose problème.

## Déjà décidé (glossaire, sujets 03 et 07)
- Un avis = une **note de 1 à 5 ★** et un **petit texte**, laissé par un client **après un vrai rendez-vous** (ce qui évite les faux avis).
- Un client qui ferme son compte : ses avis restent, signés « Client ayant quitté rafals » ; l'administrateur peut effacer un nom écrit dans le texte (`RM-CLIENTS.md`).
- Les avis servent au classement de la recherche (note pondérée, badge « Nouveau » sans avis : `RM-RECHERCHE.md`).

## 30 jours pour laisser un avis, avec un rappel (décidé le 30/09/2026)
Le lendemain du rendez-vous, le client reçoit « Comment s'est passé votre rendez-vous avec Karim ? » ; il peut noter pendant 30 jours après le rendez-vous.
- Exemple : rendez-vous mardi 14/10 → mail le 15/10 → avis possible jusqu'au 13/11.
**Pourquoi :** un avis doit parler d'un souvenir frais.

## Le prestataire répond publiquement (décidé le 30/09/2026)
Le prestataire peut écrire **une seule réponse** par avis, affichée dessous ; il ne peut pas changer la note.
- Exemple : « ★★ En retard d'une heure » → réponse de Karim : « Bouchon sur la rocade, j'avais prévenu par SMS. »

## Filtre de gros mots à l'envoi (décidé le 30/09/2026)
rafals refuse dès l'envoi un avis (ou une réponse du prestataire) qui contient un mot d'une liste de gros mots ; l'auteur doit le réécrire. La liste est modifiable par l'administrateur, sans toucher au code.
- Exemple : « Karim est un [gros mot] » → « Votre avis contient un mot interdit : reformulez-le, s'il vous plaît. »

## Signaler un avis : l'administrateur décide (décidé le 30/09/2026)
En plus du filtre, le prestataire peut cliquer [Signaler cet avis] avec une raison (fausse accusation, coordonnées personnelles…). L'avis reste affiché pendant l'examen ; l'administrateur le laisse, ou le **cache** (sa note ne compte plus) avec un motif envoyé au client. Rien n'est effacé.
- Exemple : « Karim m'a volé un bijou » → Karim signale → l'administrateur demande des preuves, puis cache l'avis : « Accusation grave sans élément : avis caché. »

## Nom affiché : prénom et initiale (décidé le 30/09/2026)
- Exemple : Marie Dupont → « ★★★★★ Marie D., octobre 2026 : ponctuel et soigneux ». (Compte fermé : « Client ayant quitté rafals ».)
**Pourquoi :** l'avis a l'air vrai, sans permettre de retrouver la personne (données personnelles).

## Précisions proposées par Claude (validées par Raphael le 30/09/2026)
- **Un avis par rendez-vous tenu** (pas pour un rendez-vous annulé, expiré, refusé ou marqué absent) ; un client qui revient 3 fois peut laisser 3 avis.
- **Modifier son avis** : possible pendant les 30 jours ; ensuite il est figé. Le client peut le **retirer** à tout moment (il est caché, pas effacé).
- **Texte** : de 10 à 1000 caractères ; la note seule ne suffit pas.
- **Où** : sur la page publique du prestataire (les plus récents d'abord) et, en résumé, dans les résultats de recherche (« 4,5 ★ · 8 avis ») ; la note moyenne compte tous les avis du prestataire, tous métiers confondus.
- La **liste des gros mots** de départ est écrite par Claude et relue par Raphael avant la mise en ligne.

## Précisions prises au lot 4.7 (proposées par Claude, validées par Raphael le 01/10/2026)
- **Filtre** : un mot interdit compte seulement s'il est entier, sans tenir compte des accents ni des majuscules (« Connard » refusé ; « conserve », « concours » acceptés). Il s'applique aussi à la réponse du prestataire. Liste de départ : 50 injures courantes (`backend/app/donnees/mots_interdits.json`, `charger-mots-interdits.bat`), **à relire par Raphael avant la mise en ligne**.
- **Pas d'avis** sur un rendez-vous où une absence a été signalée.
- **Signaler** : une fois par avis, avec une raison d'au moins 5 caractères ; l'administrateur le **laisse** (le signalement est traité) ou le **cache** avec un motif d'au moins 5 caractères envoyé au client.
- **Réponse du prestataire** : de 2 à 1000 caractères.
- **Note affichée** : moyenne des avis visibles (ni retirés, ni cachés) ; un avis modifié, retiré ou caché change aussitôt la note et le classement de la recherche.
- **Rappel** : le lendemain du rendez-vous, à partir de 10 h, une seule fois, s'il n'y a pas encore d'avis ni d'absence.
- Les avis d'un prestataire se voient seulement si sa page publique est visible (activité active).

## Une IA gratuite lit chaque avis (demandé par Raphael le 02/10/2026, lot 4.8)
Réponse de Raphael, mot pour mot : « je vais pas taper a la main chaques mots incorretct donc tu vas me faire un truc automatique pour ca », puis « un service d'ia gratuit pour moi », et le choix « Une IA installée dans rafals ».
- Chaque avis et chaque réponse est lu par une IA libre installée dans rafals (conteneur `moderation`, Detoxify) qui donne une note de 0 à 1 ; à 0,7 ou plus (réglage), le texte est refusé : « Votre avis semble injurieux : reformulez-le calmement, s'il vous plaît. »
- Exemple : « Karim est un gros nul qui arnaque les vieux » est refusé, sans aucun gros mot.
- La liste des mots interdits reste en plus, comme filet de secours ; si l'IA est en panne, seule la liste s'applique (le client n'est jamais bloqué par une panne).
- Les avis ne sortent jamais de rafals (données personnelles).
- **Limite constatée** (essai du 02/10/2026, `scripts/essayer_moderation.py`) : les insultes sont bien refusées (« gros nul qui arnaque les vieux » 0,98 ; « espèce d'incapable » 0,80), les avis négatifs mais polis passent (« travail bâclé » 0,004) ; une **menace** sans insulte (« je vais te retrouver et tu vas le regretter » 0,01) n'est **pas** repérée : elle passe par le signalement à l'administrateur.

## Notation dans les deux sens : le prestataire note aussi le client (sujet 20 ; rédigé par Claude le 04/10/2026 sur le modèle d'AlloVoisins, **validé par Raphael le 04/10/2026** sur la maquette `maquette-niveau-8-demandes.html`)
Demandé par Raphael le 04/10/2026 (« je veux faire le 1,2,3,5,6 »). Sur AlloVoisins, les membres s'évaluent mutuellement après une prestation. Tout ce qui suit est un choix de Claude.
- **Après un rendez-vous tenu**, le prestataire peut noter le client : **1 à 5 ★** et un petit texte (10 à 500 caractères), pendant **30 jours**, comme le client. Un avis par rendez-vous ; mêmes filtres (mots interdits + IA) ; modifiable pendant les 30 jours.
  - Exemple 1 : Karim note Mme Dupont « ★★★★★ Accueillante, la fuite était bien décrite, payé tout de suite. »
  - Exemple 2 : Tom note M. Petit « ★★ Pelouse deux fois plus grande qu'annoncé, a discuté le prix sur place. »
- **Les avis sont sur le compte, avec la moyenne, et un bouton [Voir les avis]** (Raphael, 04/10/2026, mot pour mot : « les avis ils se meterons sur le compte et y'aura la moyenne et si les autres veulent voir il faut qu'il puissent clicer sur voir les avis et la y'a tout les avis »). Partout où le nom d'une personne est affiché à quelqu'un d'autre : « Marie D. · 4,8 ★ · 6 avis [Voir les avis] » ; le bouton ouvre la liste de tous ses avis (note, auteur, mois, texte, réponse), les plus récents d'abord. Sans avis : « Aucun avis pour l'instant », sans bouton.
  - Exemple 1 (prestataire) : dans la conversation, Mme Dupont lit « Karim B. · 4,7 ★ · 3 avis [Voir les avis] » ; c'est aussi ce que montre déjà sa page publique.
  - Exemple 2 (client) : sur la demande « Tondre ma pelouse », Karim lit « Marie D. · 5,0 ★ · 1 avis [Voir les avis] ».
  - Chacun voit sa propre moyenne et tous ses avis sur son compte (« Mes avis reçus »).
- **Les avis sur un client sont visibles de tout le monde** (décidé par Raphael le 04/10/2026 : choix « B. Tout le monde », contre la proposition de Claude « seulement les prestataires concernés »). Chaque client a une **page publique** (`/clients/12`), visible même sans compte.
  - Ce que la page montre (choix de Claude, pour montrer le moins possible) : « Marie D. » (prénom et initiale, jamais le nom complet), « membre depuis septembre 2026 », la moyenne, et tous les avis reçus avec les réponses. **Jamais** : nom complet, ville, adresse, téléphone, mail, demandes, rendez-vous.
  - Exemple 1 : un visiteur sans compte ouvre la page de Marie D. : « 5,0 ★ · 1 avis — ★★★★★ Léa M., coiffeuse, septembre 2026 : À l'heure, très agréable. »
  - Exemple 2 : Karim clique [Voir les avis] sur une demande : il arrive sur la même liste.
  - On arrive sur cette page par [Voir les avis] à côté du nom du client ; elle n'est pas dans la recherche de rafals (qui cherche des prestataires).
  - **Moteurs de recherche** (choix de Claude) : la page demande à Google de ne pas l'enregistrer (*noindex*), pour qu'on ne tombe pas dessus en tapant un prénom.
  - **Loi sur les données personnelles** (à vérifier avant la mise en ligne, comme les autres points juridiques) : rendre publique la note d'un particulier doit être annoncé clairement à l'inscription et dans la page « Données personnelles » ; le client garde le droit de répondre, de signaler un avis, et de tout effacer en fermant son compte.
- **Le client voit ses propres avis reçus** dans « Mon compte › Mes avis reçus », peut **répondre une fois** à chacun et le **signaler** à l'administrateur (qui le laisse ou le cache), exactement comme un prestataire le fait pour les siens.
- **Les deux avis sont indépendants** : chacun paraît dès qu'il est écrit, sans attendre l'autre. (AlloVoisins ne dit pas s'il attend les deux ; choix le plus simple, comme les avis actuels.)
- **Absence** : pas d'avis sur un rendez-vous où une absence a été signalée (règle actuelle) ; l'absence du client reste comptée à part (`RM-RENDEZ-VOUS.md`).
- **Compte fermé** : la page publique du client et les avis qu'il a reçus disparaissent avec lui ; ceux qu'il a écrits restent, signés « Client ayant quitté rafals » (règle actuelle).
- **Pas d'onglet « Noter mes clients »** (Raphael, 04/10/2026, mot pour mot : « noter les clients ca ne doit pas etre un onglet comme ca ca doit juste aparaitre quand un rdv est passé enfin il faut que ca fasse comme sur allo voisin »). Dès que le rendez-vous est passé, une carte apparaît toute seule **dans la conversation** des deux personnes : « Rendez-vous passé · Remplacer un robinet · mardi 29/09 — Comment ça s'est passé avec Marie D. ? [Noter Marie D.] · encore 25 jours ». Le client voit la même carte avec [Noter Karim B.]. Une fois l'avis laissé : « avis laissé ». Le même bouton est aussi sur la ligne du rendez-vous passé (« Mon agenda › Rendez-vous » pour le prestataire, « Mes rendez-vous » pour le client, comme aujourd'hui).
  - Exemple 1 : rendez-vous mardi 29/09 à 9 h → mardi à 9 h 45 (fin du rendez-vous), la carte apparaît chez Karim et chez Mme Dupont ; « Messages (1) » s'allume.
  - Exemple 2 : après 30 jours sans avis, la carte reste mais sans bouton : « Le délai pour noter est passé. »
- **Rappel** : le lendemain du rendez-vous, le prestataire reçoit « Comment s'est passé votre rendez-vous avec Mme D. ? » (une seule fois), comme le client.

## Qui peut faire quoi
| Action | Qui | Condition |
|---|---|---|
| Laisser, modifier un avis | Client | Rendez-vous tenu, dans les 30 jours |
| Retirer son avis | Client | À tout moment |
| Répondre une fois | Prestataire | Sur un avis le concernant |
| Signaler un avis | Prestataire | Sur un avis le concernant |
| Noter un client (sujet 20) | Prestataire | Rendez-vous tenu avec lui, dans les 30 jours |
| Voir la moyenne et les avis d'un client | Tout le monde, même sans compte | Compte du client pas fermé |
| Répondre une fois, signaler un avis reçu | Client | Sur un avis le concernant |
| Cacher un avis, modifier la liste des gros mots, effacer un nom dans un texte | Administrateur | — |

## Questions ouvertes
- (aucune)

## Références
- `GLOSSAIRE-METIER.md`, `RM-CLIENTS.md`, `RM-RECHERCHE.md`, `RM-RENDEZ-VOUS.md`

## Notation dans les deux sens : précisions prises au lot 8.5 (choix de Claude le 12/10/2026, en mode « sans question » ; à relire par Raphael)
Construit : noter un client, modifier et retirer son avis (serveur), page publique d'un client, « Mes avis reçus » (répondre une fois, signaler), décision de l'administrateur (serveur), la note à côté du nom, la carte « Rendez-vous passé » dans la conversation. Table à part : `avis_client` (elle n'entre jamais dans le classement de la recherche).
- **Texte d'un avis sur un client** : 10 à 500 caractères ; la réponse du client : 2 à 500.
- **Le client est prévenu par mail** quand il reçoit un avis (« Karim Benali vous a laissé un avis »), sans recopier l'avis.
- **Un avis signalé reste affiché** jusqu'à la décision ; **caché**, il ne compte plus dans la moyenne, le client le voit encore dans « Mes avis reçus » avec le motif, et le prestataire qui l'a écrit reçoit le motif par mail.
- **Un avis retiré par le prestataire** disparaît partout, y compris de « Mes avis reçus ».
- **Moyenne** : arrondie au dixième (« 4,8 ★ · 6 avis ») ; sans avis : « Aucun avis pour l'instant ».
- **Adresse de la page publique** : `/clients/12/avis` (et non `/clients/12`, déjà prise par la fiche « Mes clients » du prestataire).
- **Compte fermé** : la page publique répond « Cette personne n'est pas (ou plus) sur rafals. » ; on ne peut plus la noter.
- **La carte « noter »** apparaît pour chaque rendez-vous tenu des 30 derniers jours entre les deux personnes ; elle reste, grisée (« avis laissé »), jusqu'à la fin des 30 jours.
- **Pas encore fait** : écran d'administration des avis sur un client signalés ; modifier ou retirer son avis à l'écran ; ces avis dans « Télécharger mes données ».
