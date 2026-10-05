# Règle métier — Alertes et notifications (sujet 18)

> Rédigé par Claude le 04/10/2026 sur le modèle d'AlloVoisins, corrigé avec Raphael sur la maquette `maquette-niveau-8-demandes.html` (8 versions), **validé par Raphael le 04/10/2026** (« oui »). Les lignes « (choix de Claude) » sont donc validées avec le reste.

## Objectif
Prévenir tout de suite la bonne personne : un prestataire quand une demande de son métier est publiée près de chez lui ; chacun quand on lui écrit ou qu'on accepte sa proposition.
- Exemple 1 : M. Petit publie « Fuite sous l'évier » à Talence à 8 h 02 → à 8 h 02, le téléphone de Karim affiche « Nouvelle demande : Fuite sous l'évier, Talence (5 km) ».
- Exemple 2 : Mme Dupont accepte la proposition de Tom → Tom reçoit « Mme D. a accepté : samedi 10/10 à 10 h 00 ».

## Ce qu'AlloVoisins fait
Le prestataire règle ses catégories et son rayon, puis reçoit une notification à chaque demande publiée dans sa zone (page d'aide « Comment ça marche AlloVoisins ? », lue le 04/10/2026). rafals connaît déjà les métiers et le rayon du prestataire (`RM-PRESTATAIRES.md`) : rien de plus à remplir.

## Qui reçoit l'alerte d'une nouvelle demande
Exactement ceux qui peuvent la voir (`RM-DEMANDES.md`) : prestataires en activité, métier exercé, ville dans leur rayon. Pas d'alerte pour un prestataire en pause, bloqué ou arrêté, ni pour l'auteur de la demande.

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
