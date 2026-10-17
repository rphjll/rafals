# Règle métier — Alertes et notifications (sujet 18)

> Rédigé par Claude le 04/10/2026 sur le modèle d'AlloVoisins, corrigé avec Raphael sur la maquette `maquette-niveau-8-demandes.html` (8 versions), **validé par Raphael le 04/10/2026** (« oui »). Les lignes « (choix de Claude) » sont donc validées avec le reste.

## Objectif
Prévenir tout de suite la bonne personne : un prestataire quand une demande de son métier est publiée près de chez lui ; chacun quand on lui écrit ou qu'on accepte sa proposition.
- Exemple 1 : M. Petit publie « Fuite sous l'évier » à Talence à 8 h 02 → à 8 h 02, le téléphone de Karim affiche « Nouvelle demande : Fuite sous l'évier, Talence (5 km) ».
- Exemple 2 : Mme Dupont accepte la proposition de Tom → Tom reçoit « Mme D. a accepté : samedi 10/10 à 10 h 00 ».

## Ce qu'AlloVoisins fait
Le prestataire règle ses catégories et son rayon, puis reçoit une notification à chaque demande publiée dans sa zone (page d'aide « Comment ça marche AlloVoisins ? », lue le 04/10/2026). rafals connaît déjà les métiers et le rayon du prestataire (`RM-PRESTATAIRES.md`) : rien de plus à remplir.

## Qui reçoit l'alerte d'une nouvelle demande
Exactement ceux qui peuvent la voir (`RM-DEMANDES.md`) : prestataires en activité, métier exercé, adresse dans leur compte, ville dans leur rayon autour de cette adresse (depuis le 15/10/2026). Sans adresse : aucune alerte. Pas d'alerte pour un prestataire en pause, bloqué ou arrêté, ni pour l'auteur de la demande.

## Trois façons de prévenir (choix de Claude, corrigé par Raphael le 04/10/2026)
Raphael, mot pour mot : « enleve l'onglet notification ». Il n'y a donc **pas de liste de notifications** sur le site.
1. **Un compteur rouge sur l'onglet concerné** : « Demandes près de chez moi » (nouvelles demandes), « Messages » (conversations non lues), « Mes avis reçus » (nouvel avis). Le compteur revient à zéro quand on ouvre l'onglet.
2. **La notification sur le téléphone ou l'ordinateur**, si l'application est installée ou les notifications acceptées dans le navigateur (`RM-APPLICATION.md`).
3. **Le mail**.
- Exemple 1 : Karim a tout laissé activé → pour la fuite de Talence, il a « Demandes près de chez moi (1) », une notification sur son téléphone et un mail.
- Exemple 2 : Mme Dupont reçoit une proposition → « Messages (1) » en rouge, une notification, un mail.

## Ce qui déclenche une notification (choix de Claude)
| Événement | Qui est prévenu | Compteur rouge sur l'onglet | Téléphone | Mail |
|---|---|---|---|---|
| Nouvelle demande dans mon métier et mon rayon | Prestataire | oui | oui | oui (réglable) |
| Un prestataire a répondu à ma demande | Client | oui | oui | oui |
| Nouveau message | L'autre personne | oui | oui | après 15 min sans lecture |
| Nouvelle proposition | Client | oui | oui | oui |
| Proposition acceptée | Prestataire | oui | oui | oui |
| Proposition refusée | Prestataire | oui | oui | non |
| Le client propose un autre prix | Prestataire | oui | oui | oui |
| Le prestataire accepte ou refuse ce prix | Client | oui | oui | oui |
| La demande a été pourvue par un autre | Prestataires qui avaient répondu | oui | non | non |
| Ma demande se ferme dans 3 jours | Client | oui | non | oui |
| La barre de la TVA passe 80 %, puis le seuil (17/10/2026, `RM-MON-ACTIVITE.md`) | Prestataire qui ne facture pas la TVA | non | oui | oui |
Les mails qui existent déjà (rendez-vous confirmé, annulé, rappel, avis…) ne changent pas.

## Réglages du prestataire : onglet « Alertes » (choix de Claude, réécrit le 04/10/2026)
L'onglet garde son nom « Alertes » (Raphael, 04/10/2026 : « je voulais pas que tu enleve l'onglet alerte ») ; seul son contenu est réécrit. Titre de l'écran : « Alertes : être prévenu des nouvelles demandes ».
Raphael, mot pour mot : « l'onglet alerte n'est pas claire meme moi je ne comprend pas ce que c'est demande de plombier oui ou non ». L'écran est donc écrit en questions complètes, chacune avec ses réponses en toutes lettres et un exemple :
1. **« Pour quels métiers voulez-vous être prévenu ? »** — pour chaque métier : « Un client cherche un plombier près de chez vous : » [Me prévenir] / [Ne pas me prévenir], avec dessous la conséquence (« Vous êtes prévenu de chaque demande de plombier dans votre rayon de 15 km. » ou « Vous ne recevez rien pour plombier. Les demandes restent visibles dans « Demandes près de chez moi ». »).
   - Exemple : Karim garde « Me prévenir » pour Plombier et choisit « Ne pas me prévenir » pour Jardinier.
2. **« Comment voulez-vous être prévenu ? »** — « Sur ce téléphone (une notification, même quand rafals est fermé) » [Oui] / [Non] ; « Par mail » : [Un mail à chaque demande] (au départ), [Un seul mail le soir à 18 h, avec toutes les demandes du jour], [Aucun mail].
   - Exemple : Julie, ménage à Nantes, reçoit 15 demandes par jour → « un seul mail le soir » : 1 mail à 18 h au lieu de 15.
**Pourquoi un résumé :** dans une grande ville, un mail par demande finit dans les indésirables.
- Garde-fou : au-delà de **20 mails de demandes dans la journée**, les suivants sont regroupés dans le mail de 18 h (réglage).

## Réglages du client (choix de Claude)
Dans « Mon compte » : « Recevoir les notifications sur ce téléphone » oui / non. Les mails qui concernent ses propres demandes et rendez-vous ne se coupent pas (il doit savoir qu'on lui a répondu).

## Données personnelles
- Une notification ne contient jamais le nom complet, le téléphone ni l'adresse : « Nouvelle demande : Fuite sous l'évier, Talence (5 km) ».
- Une notification de message ne recopie pas le message : « Karim vous a écrit ».

## Précisions prises au lot 8.5 (choix de Claude le 12/10/2026, en mode « sans question » ; à relire par Raphael)
Construit : le mail à chaque nouvelle demande, les réglages par métier, le résumé de 18 h, le plafond de 20, le compteur de « Demandes près de chez moi » (côté serveur), les mails des étapes d'une proposition. Notifications sur le téléphone : construites le 15/10/2026 (lot 8.7, § « Précisions prises au lot 8.7 »). **Pas encore construit** : la pastille rouge à l'écran.
- **Le mail d'une nouvelle demande** a pour objet « rafals : nouvelle demande, Fuite sous l'évier, Talence (5 km) » ; il ne contient ni nom, ni téléphone, ni adresse. La distance est celle entre le centre de la ville de son adresse et celui de la ville de la demande, arrondie au kilomètre.
- **Un prestataire sans SIRET n'est pas prévenu** d'une demande d'un métier qui demande un SIRET : il ne pourrait pas y répondre (`RM-PRESTATAIRES.md`, limites sans SIRET).
- **Le résumé de 18 h** part une fois par jour, à partir de 18 h (heure de Paris), seulement s'il y a au moins une demande. Il liste les demandes du jour encore ouvertes. Pour celui qui a choisi « un mail à chaque demande » et dépassé 20 mails, il ne liste que les demandes en trop.
  - Exemple 1 : Julie a choisi le résumé ; 15 demandes dans la journée → 1 mail à 18 h avec les 15.
  - Exemple 2 : Karim reçoit un mail par demande ; 23 demandes → 20 mails, puis à 18 h un mail avec les 3 dernières.
- **Le résumé ne compte pas les demandes publiées avant l'inscription du prestataire.**
- **Mails ajoutés aux étapes d'une proposition** (tableau « Ce qui déclenche une notification ») : « Karim Benali a répondu à votre demande », « Karim Benali vous fait une proposition », « Marie D. vous propose un autre prix », « Karim Benali accepte votre prix », « Karim Benali garde son prix ». Ils disent seulement ce qui s'est passé et renvoient à « Messages ». La proposition acceptée garde le mail « rendez-vous confirmé » qui existait.
- **Le compteur rouge** compte les demandes de ses métiers et de son rayon arrivées depuis sa dernière visite de « Demandes près de chez moi », même pour un métier où il a choisi « Ne pas me prévenir ».

## Précisions prises au lot 8.7 (choix de Claude le 15/10/2026 ; à relire par Raphael)
- **La notification d'une nouvelle demande ne suit pas le réglage du mail** : « Aucun mail » ou « résumé de 18 h » ne coupe pas le téléphone ; seul « Ne pas me prévenir » pour un métier, ou [Couper les notifications], l'arrête. Pas de plafond de 20 pour le téléphone.
  - Exemple : Julie a choisi « Un seul mail le soir » ; une demande de ménage arrive à 10 h → son téléphone sonne à 10 h, et la demande est aussi dans le mail de 18 h.
- **Un message** : notification tout de suite (« Karim Benali vous a écrit »), le mail reste au bout de 15 minutes sans lecture. **Proposition acceptée ou refusée** : notification au prestataire (« Marie D. a accepté votre proposition : rendez-vous mardi 20/10 à 10 h »).
- **Pour les étapes d'une proposition**, la notification reprend l'objet du mail (« Karim Benali vous fait une proposition »).
- **À l'activation**, une notification d'essai « Les notifications sont activées sur cet appareil. » pour voir tout de suite que ça marche.
- **Un appareil qui n'existe plus** (téléphone changé, rafals désinstallé) est effacé dès que le navigateur répond qu'il n'existe plus.
- **Le client** règle ses notifications dans « Mon profil », carte « Notifications sur cet appareil ».

## Qui peut faire quoi
| Action | Qui | Condition |
|---|---|---|
| Recevoir les alertes de demandes | Prestataire en activité | Métier exercé, ville dans le rayon, alerte du métier activée |
| Régler ses alertes | Chacun | Les siennes seulement |

## Valeurs par défaut (réglages)
Alertes de demandes : activées pour tous les métiers · mail : à chaque demande · résumé : 18 h · plafond : 20 mails de demandes par jour.

## Questions ouvertes
- (aucune)

## Références
- `RM-DEMANDES.md`, `RM-MESSAGERIE.md`, `RM-APPLICATION.md`, `RM-PRESTATAIRES.md`
- AlloVoisins : https://support-pro.allovoisins.com/hc/fr/articles/22062882967826
