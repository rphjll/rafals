# Règle métier — Demandes publiées par les clients (sujet 17)

> Rédigé par Claude le 04/10/2026 sur le modèle d'AlloVoisins, corrigé avec Raphael sur la maquette `maquette-niveau-8-demandes.html` (8 versions), **validé par Raphael le 04/10/2026** (« oui »). Les lignes « (choix de Claude) » sont donc validées avec le reste.

## Objectif
Le client écrit son besoin ; les prestataires du coin y répondent. C'est l'inverse de la recherche (`RM-RECHERCHE.md`), où le client cherche lui-même.
- Exemple 1 : Mme Dupont publie « Tondre ma pelouse samedi à Pessac, budget 40 € ». Tom et Karim lui répondent dans la journée.
- Exemple 2 : M. Petit publie « Fuite sous l'évier, dès que possible, Talence ». Karim, plombier à Pessac (rayon 15 km), reçoit une alerte.

## Déjà décidé par Raphael
- On copie AlloVoisins pour les demandes, les alertes, la messagerie, la notation dans les deux sens et l'application ; **pas la location de matériel** (04/10/2026 : « je veux faire le 1,2,3,5,6 mais pas la 4 »).
- **Répondre à une demande : comme sur AlloVoisins** (« comme sur allo voisin »). Le bouton [Répondre] ouvre une conversation privée avec le client ; ils se mettent d'accord ; puis le prestataire fait une proposition (un prix), que le client est libre d'accepter. Source : page d'aide « Comment répondre aux demandes ? » d'AlloVoisins, lue le 04/10/2026.

## Publier une demande (choix de Claude)
Il faut un compte (adresse mail vérifiée). Publier est gratuit. La demande contient :
- un **métier** de la liste (`RM-METIERS.md`) : c'est lui qui dit quels prestataires sont prévenus ;
- un **titre** (5 à 80 caractères) et une **description** (20 à 1000 caractères) ;
- la **ville** (une commune de la liste) ; **jamais la rue** : elle n'est donnée qu'au prestataire choisi ;
- **quand** : « dès que possible », « dans les 7 jours », « un jour précis » (date), ou « pas pressé » ;
- **où** : « chez moi » ou « chez le prestataire » ;
- un **budget** facultatif (en euros) ;
- jusqu'à **5 photos** facultatives.
- Exemple 1 : métier Jardinier · « Tondre ma pelouse » · « 200 m², terrain plat, j'ai une prise dehors » · Pessac · samedi 10/10 · chez moi · 40 €.
- Exemple 2 : métier Plombier · « Fuite sous l'évier » · « Le siphon goutte depuis hier soir » · Talence · dès que possible · chez moi · pas de budget · 1 photo.
**Pourquoi un métier obligatoire :** sans lui, on ne sait pas qui prévenir (sujet 18).

## Qui voit une demande (choix de Claude)
Seulement les prestataires **en activité** qui exercent ce métier (principal ou secondaire, pas arrêté) et dont le **rayon** couvre la ville de la demande (même calcul que la recherche). Pas besoin d'avoir une annonce en ligne : un débutant peut répondre. (Annonces retirées le 04/10/2026 : les demandes et [Écrire à Karim] deviennent les seuls chemins vers un rendez-vous, voir `RM-PRESTATAIRES.md` § « Sans annonces ».)
**Le rayon se mesure depuis l'adresse de son compte** (« Mon adresse » dans « Mon profil » ; décision de Raphael du 15/10/2026 : « ca doit etre pres de chez l'adresse qu'il a tapé dans mon compte »), pas depuis la ville de départ du profil. **Sans adresse, il ne voit aucune demande** : « Demandes près de chez moi » affiche « Vous n'avez pas encore d'adresse… » et un bouton **[Ajouter votre adresse]** (→ « Mon profil ») ; sur l'accueil, [Répondre] est verrouillé 🔒 : « Ajoutez votre adresse dans « Mon profil » : les demandes près de chez vous se calculent depuis elle. »
- Exemple 0 : Karim, profil « part de Pessac », adresse 3 rue Gambetta à Libourne, rayon 15 km → ne voit pas la fuite de Pessac (40 km de Libourne).
- Exemple 1 : Karim, plombier, adresse à Pessac, rayon 15 km → voit la fuite de Talence (5 km).
- Exemple 2 : Sophie, plombière à Arcachon, rayon 20 km → ne la voit pas (55 km).
Ils voient : le titre, la description, les photos, la ville, le « quand », le budget, et le client sous la forme « Marie D. » avec sa note de client (sujet 20). **Jamais** le nom complet, le téléphone, le mail ni la rue.
**Pourquoi pas tout le monde :** une demande parle de la vie privée d'une personne (son jardin, sa fuite) ; seuls ceux qui peuvent y répondre la lisent (données personnelles, `RM-CLIENTS.md`).

## L'accueil montre toutes les demandes (décision de Raphael du 05/10/2026)
Réponse de Raphael, mot pour mot : « sur la page d'acceuille je veux que y'ai ecrit bonjour avec le prénom de la personne puis une barre de recherche ou y'a ecrit de quoi avez vous besoin ? et en dessous toute les demandes faites par des clients ».
- **Cela change « Qui voit une demande »** ci-dessus : les demandes ouvertes sont listées sur l'accueil, pour tout le monde, la plus récente en haut. Pas encore construit (lot 8.4).
  - Exemple 1 : Julie, femme de ménage à Nantes, ouvre l'accueil et voit « Tondre ma pelouse · Jardinier · Pessac · samedi 10/10 · 40 € · Marie D. ».
  - Exemple 2 : M. Petit, simple client, voit la même liste.
- **Ce qui ne change pas** (choix de Claude) : la liste ne montre jamais le nom complet, le téléphone, le mail ni la rue ; **seuls les prestataires du métier et du rayon peuvent répondre** et reçoivent l'alerte (`RM-ALERTES.md`).
  - Exemple : Julie voit la pelouse de Pessac mais n'a pas de bouton [Répondre] : elle n'est pas jardinière et Pessac est hors de son rayon.
- ⚠️ À faire vérifier avant la mise en ligne (données personnelles) : une demande décrit la vie privée d'une personne (« le siphon goutte depuis hier ») et devient lisible par tous. Le formulaire devra le dire au client avant qu'il publie.
- **La barre « De quoi avez-vous besoin ? »** de l'accueil **filtre la liste** (choix « b » de Raphael le 05/10/2026) : ne restent que les demandes dont le titre ou la description contient le texte tapé. Ex. « pelouse » → « Tondre ma pelouse » reste ; « chien » → « Promener mon chien le midi » reste. On publie par la carte « Publier une demande », à droite de la liste (demande de Raphael du 05/10/2026 : « sur le coté a droite comme sur allo voisin il faut que je puisse mettre mon texte pour publier ma demande ») : le client y écrit son besoin, clique [Publier ma demande], puis complète le métier, la ville et le « quand » (choix de Claude : ces rubriques restent obligatoires, sinon on ne sait pas quels prestataires prévenir).

## L'adresse est demandée dès la publication, avec un plan (décision de Raphael du 05/10/2026)
Réponse de Raphael, mot pour mot : « faut que on pussie metre l'adresse et que y'ai une carte google maps qui aparaise et on puisse mettre des photos ». Pas encore construit côté serveur (lot 8.3).
- **Cela change « Publier une demande »** : le client écrit son adresse complète en publiant (avant : seulement la ville, et la rue au moment d'accepter une proposition). Un plan avec un repère lui confirme l'endroit.
  - Exemple 1 : Mme Dupont tape « 8 allée des Pins, Pessac », choisit « 8 Allée des Pins 33600 Pessac » : le plan s'affiche avec un repère sur sa rue.
  - Exemple 2 : M. Petit se trompe de ville, le voit sur le plan, clique [Changer] et corrige.
- **Ce qui ne change pas** (choix de Claude) : **la rue n'est montrée qu'au prestataire choisi**, après acceptation d'une proposition. Sur l'accueil et pour les prestataires qui répondent, on ne voit que la ville (« Pessac »). La ville de la demande est celle de l'adresse.
- **Photos** : inchangé, 5 au plus, JPG ou PNG, 5 Mo chacune ; elles se choisissent dans la même carte.
- **Plan OpenStreetMap et non Google Maps** (choix de Claude, à confirmer par Raphael) : Google Maps demande un compte Google avec une carte bancaire et une clé, et envoie l'adresse des visiteurs à Google ; OpenStreetMap marche tout de suite, sans compte. Détail : `.doc/technique/API-EXTERNES.md` § 3.

## Précisions prises au lot 8.3, première partie (choix de Claude le 06/10/2026, en mode « sans question » ; à relire par Raphael)
Construit : publier, lister sur l'accueil, « mes demandes », modifier, fermer, prolonger, expirer, photos. (Répondre, propositions et rendez-vous : seconde partie, plus haut.)
- **Qui peut publier** : compte connecté, adresse mail vérifiée (et accord des parents avant 18 ans), comme pour réserver. Sinon : « Vérifiez votre adresse mail (et, avant 18 ans, l'accord de vos parents) pour publier une demande. »
- **La liste de l'accueil se lit sans compte** ; elle montre 100 demandes au plus, la plus récente en haut. Une demande cachée, fermée, expirée, ou d'un compte fermé n'y est plus.
- **Les photos demandent d'être connecté** (elles montrent souvent l'intérieur d'un logement). Sans compte, on lit seulement « 2 photos (connectez-vous pour les voir) ».
- **Adresse** : choisie dans les propositions du service d'adresses de l'État. « Chez moi » : la rue est obligatoire. « Chez le prestataire » : la ville suffit.
  - Exemple 1 : Mme Dupont, chez elle, « 8 Allée des Pins 33600 Pessac » → acceptée ; l'accueil affiche « Pessac ».
  - Exemple 2 : M. Petit cherche un coiffeur « chez le prestataire » et choisit seulement « Talence » → acceptée, sans rue.
- **La ville est retrouvée** par son code officiel ; s'il est inconnu de rafals (ex. un arrondissement de Paris), par le code postal.
- **Un jour précis** ne peut pas être passé ; la demande se ferme à la fin de ce jour (minuit, heure de Paris). Ex. publiée le 06/10 pour le 10/10 → expire le 11/10 à 0 h 00.
- **Pas de rappel « se ferme dans 3 jours »** pour une demande qui dure moins de 3 jours (ex. publiée jeudi pour samedi).
- **Prolonger** : 30 jours de plus pour une demande ouverte ; une demande expirée redevient ouverte, s'il reste de la place parmi les 5. Un jour précis déjà passé ne se prolonge pas.
- **Modifier** : tant que la demande est ouverte (la condition « tant que personne n'a répondu » viendra avec les réponses). Les photos ne se changent pas : fermer et republier.
- **Budget** : en euros dans l'écran (« 40 » ou « 40,50 »), gardé en centimes.
- Publier, modifier, fermer et prolonger sont écrits au journal des actions.
- **Table des photos** : `photo_demande_publiee` (le nom `photo_demande` est déjà pris par les demandes de devis).

## Précisions prises au lot 8.3, seconde partie (choix de Claude le 07/10/2026, en mode « sans question » ; à relire par Raphael)
Construit : qui peut répondre, répondre, propositions, négociation du prix, rendez-vous, demande pourvue, rouvrir ; les limites des prestataires sans SIRET, signaler une demande et la cacher (12/10/2026). **Pas encore construit** : un devis en réponse à une demande.
- **[Répondre]** : un 2e clic rouvre la même conversation, sans compter une 2e réponse. Une demande complète (10 réponses) reste ouverte à ceux qui ont déjà répondu.
- **Le lieu d'une proposition vient de la demande** : « chez moi » → le prestataire vient chez le client ; « chez le prestataire » → le client va chez lui (son local doit être rempli dans « Ma fiche »).
- **Durée proposée** : de 15 minutes à 12 heures. **L'heure** doit être à venir.
- **Une nouvelle proposition remplace celle qui attendait** pour la même demande (l'ancienne passe « remplacée »). Une proposition refusée, retirée ou expirée n'est pas remplacée : la nouvelle est indépendante.
  - Exemple : Karim propose 50 €, puis 45 € avant que Mme Dupont réponde → la carte à 50 € est « remplacée », seule celle à 45 € peut être acceptée.
- **Carte bancaire** : la case n'est acceptée que si le prestataire a un SIRET vérifié et le paiement par carte activé. Si la carte n'est plus possible au moment d'accepter, le client paie en espèces (même règle que les annonces).
- **Adresse du rendez-vous** : celle écrite dans la demande. Sans demande (le client a écrit en premier) : l'adresse de « Mon compte » ; s'il n'en a pas : « Indiquez d'abord votre adresse dans « Mon compte »… ».
- **Titre du rendez-vous** : le titre de la demande ; sans demande, le nom du métier (ex. « Plombier »).
- **Deux clients, la même heure** : le premier qui accepte a le rendez-vous ; l'autre lit « … a déjà un rendez-vous à cette heure-là ».
- **Un rendez-vous venu d'une proposition ne se déplace pas tout seul** : le bouton [Déplacer] est verrouillé 🔒 (« demandez un autre horaire au prestataire dans vos messages »). Il s'annule comme les autres.
- **Rouvrir** : seulement une demande pourvue dont le rendez-vous a été annulé (par le client ou le prestataire) ; elle repart pour 30 jours, s'il reste de la place parmi les 5.
- **Paiement par carte jamais terminé** (30 minutes) : le rendez-vous est annulé comme une réservation ; la demande reste « pourvue » et le client peut la rouvrir.
- **Une demande ne se modifie plus dès qu'un prestataire a répondu** : « Un prestataire a déjà répondu : fermez cette demande et publiez-en une autre pour la changer. »
- **Dans le fil**, rafals écrit une ligne à chaque étape (a répondu, propose, a refusé, prix proposé, garde son prix, a accepté, a retiré, a choisi un autre prestataire).
- **Le rendez-vous porte son métier** (table `rendez_vous`, rubrique `metier_id`) : c'est lui qui dit dans quel calendrier il tombe ; avant, on le lisait dans l'annonce.

## Prestataire sans SIRET : des limites pour répondre et proposer (validé par Raphael le 09/10/2026, construit le 12/10/2026)
La règle complète est dans `RM-PRESTATAIRES.md` § « Limites d'un prestataire sans SIRET ». Ce qu'elle change ici :
- **Répondre** : bouton [Répondre] verrouillé 🔒, avec la raison, sur une demande d'un métier interdit sans SIRET ; avant sa première réponse, son adresse doit être remplie et la case « Mon activité est occasionnelle et je déclare mes revenus aux impôts » cochée.
- **Proposer** : 100 € au plus ; espèces seulement (déjà en place).
- **Accepter** : refusé si le prestataire a déjà 2 rendez-vous confirmés dans le mois du rendez-vous, ou s'il a atteint 1 000 € de rendez-vous qui ont eu lieu sur les 12 derniers mois (ses propositions en attente sont alors retirées et il est prévenu) ; le client lit l'avertissement « Pas de facture, pas de garantie, pas d'assurance professionnelle. » avant de confirmer.
  - Exemple 1 : Emma, sans SIRET, propose 40 € pour une pelouse → acceptée par Mme Dupont après l'avertissement.
  - Exemple 2 : Emma a déjà 2 rendez-vous en octobre → Mme Dupont ne peut pas accepter sa proposition pour le 28/10.

## Répondre : une conversation, puis une proposition
- [Répondre] ouvre la conversation entre ce prestataire et ce client (`RM-MESSAGERIE.md`), avec la demande rappelée en haut.
- Dans la conversation, le prestataire envoie une **proposition** : prix, jour, heure de début, durée, lieu, et les moyens de paiement qu'il accepte (espèces ; carte seulement s'il a un SIRET vérifié et le paiement par carte activé, `RM-PAIEMENTS.md`).
- Exemple 1 : Tom (sans SIRET) propose « 35 € · samedi 10/10 à 10 h 00 · 1 h · chez vous · espèces ».
- Exemple 2 : Karim propose « 60 € · lundi 12/10 à 8 h 30 · 1 h · chez vous · carte ou espèces ».
- **Le client peut refuser une proposition** (Raphael, 04/10/2026, mot pour mot : « quand un client recoit une proposition il faut qu'il ai la posibilité de refuser comme sur vinted »). Sous la proposition : [Accepter 35 € · samedi à 10 h 00] et [Refuser]. Refuser ne demande pas de raison ; la proposition passe à « refusée », le prestataire est prévenu (« Marie D. a refusé votre proposition de 35 € »), la conversation reste ouverte et il peut en faire une autre.
  - Exemple 1 : Karim propose 60 €, Mme Dupont clique [Refuser], Karim propose 50 €, elle accepte.
  - Exemple 2 : Tom propose samedi à 10 h, Mme Dupont refuse et écrit « plutôt l'après-midi ? », Tom propose samedi à 15 h.
- **Le client peut négocier le prix** (Raphael, 04/10/2026, mot pour mot : « faut que y'ai un bouton negocier le prix aussi entre accepter et refuser »). Les trois boutons, dans cet ordre : [Accepter 60 € · lundi à 8 h 30] · [Négocier le prix] · [Refuser].
  - [Négocier le prix] ouvre une fenêtre « Votre prix (€) » ; le prix doit être plus bas que celui de la proposition. Le jour, l'heure, la durée et le lieu ne changent pas. La proposition passe à « prix en négociation ».
  - Le prestataire voit « Prix proposé par Marie D. : 50 € au lieu de 60 € » avec [Accepter 50 €] et [Refuser ce prix].
  - **Il accepte** : sa proposition est remplacée par la même à 50 € ; le client n'a plus qu'à cliquer [Accepter 50 € · lundi à 8 h 30] (c'est là qu'il donne son adresse et choisit le paiement).
  - **Il refuse** : sa proposition de départ à 60 € redevient « en attente » ; le client peut encore l'accepter, la refuser, ou proposer un autre prix.
  - Exemple 1 : Karim propose 60 €, Mme Dupont propose 50 €, Karim accepte, elle confirme : rendez-vous à 50 €.
  - Exemple 2 : Tom propose 35 €, Mme Dupont propose 20 €, Tom refuse (« Tom L. garde son prix de 35 € »), elle accepte 35 €.
  - Une seule négociation à la fois par proposition (choix de Claude) : tant que le prestataire n'a pas répondu, le client ne peut pas proposer un deuxième prix.
- Le prestataire peut retirer ou remplacer sa proposition tant qu'elle n'est pas acceptée. Une proposition non acceptée expire au début de l'heure proposée.

## Accepter une proposition crée un rendez-vous (choix de Claude)
Quand le client clique [Accepter 35 € · samedi à 10 h 00] :
- un **rendez-vous confirmé** est créé, comme ceux de `RM-RENDEZ-VOUS.md` (annulation, absence, rappel, facture, avis : tout pareil) ; payé par carte, il suit `RM-PAIEMENTS.md` (5 % pour rafals, versement 48 h après) ;
- s'il est « chez moi », le client donne son adresse à ce moment-là, et seul ce prestataire la voit ;
- la demande passe à **« pourvue »** : elle n'est plus proposée aux autres ; ceux qui avaient répondu lisent « Mme D. a choisi un autre prestataire » ;
- le rendez-vous prend sa place dans l'agenda du prestataire, **même hors de sa semaine type** (c'est lui qui a proposé l'heure) ; une proposition est refusée si elle tombe sur un autre de ses rendez-vous.
**Pourquoi un rendez-vous :** rafals sait que le travail a eu lieu → avis vérifiés, paiement par carte, facture. Sur AlloVoisins, la proposition n'est qu'une demande de paiement ; ici elle porte aussi le jour et l'heure, parce que rafals a un agenda.

## Limites (choix de Claude ; réglages modifiables sans toucher au code)
- **10 réponses au plus** par demande : ensuite elle est « complète » pour les autres. *Pourquoi :* Mme Dupont ne doit pas recevoir 40 conversations pour une pelouse.
- **5 demandes ouvertes au plus** par client.
- Une demande reste ouverte **30 jours**, ou jusqu'au jour précis demandé s'il arrive avant. 3 jours avant la fin, un mail : « Votre demande “Tondre ma pelouse” se ferme dans 3 jours : prolongez-la de 30 jours si vous cherchez encore. »
- Un prestataire répond **une fois** par demande (ensuite il continue dans la conversation).
- On ne répond pas à sa propre demande.

## Vie d'une demande
| État | Ce que ça veut dire | Comment on y arrive |
|---|---|---|
| ouverte | Les prestataires concernés la voient et peuvent répondre | À la publication |
| pourvue | Une proposition a été acceptée | [Accepter] |
| fermée | Le client n'en a plus besoin | [Fermer ma demande] |
| expirée | Personne n'a été choisi à temps | Après 30 jours ou le jour demandé |
- Le client peut **modifier** une demande ouverte tant que personne n'a répondu ; ensuite il la ferme et en publie une autre.
- Rendez-vous annulé avant d'avoir lieu : le client peut **rouvrir** sa demande (elle repart pour 30 jours).
- Jamais d'effacement : une demande fermée reste dans « Mes demandes ».

## Textes surveillés (choix de Claude)
- Même filtre que les avis (liste de mots interdits + IA, `RM-AVIS.md`) sur le titre et la description.
- **Pas de coordonnées dans une demande** : un numéro de téléphone ou une adresse mail dans le texte est refusé (« Ne mettez pas vos coordonnées ici : le prestataire que vous choisirez les recevra. »).
- Un prestataire peut **signaler** une demande (fausse, hors sujet, illégale) : l'administrateur la laisse ou la cache (`RM-ADMINISTRATION.md`).

## Qui peut faire quoi
| Action | Qui | Condition |
|---|---|---|
| Publier, modifier, fermer, prolonger, rouvrir une demande | Le client | Compte vérifié ; 5 demandes ouvertes au plus |
| Voir une demande | Prestataire en activité | Métier exercé, adresse dans son compte, ville dans son rayon autour de cette adresse |
| Répondre | Le même | Demande ouverte, moins de 10 réponses, pas la sienne |
| Faire une proposition | Le prestataire, dans la conversation | Demande ouverte ; heure libre de rendez-vous |
| Accepter, refuser une proposition, ou négocier son prix | Le client | Proposition en attente |
| Accepter ou refuser le prix proposé par le client | Le prestataire | Négociation en attente |
| Cacher une demande | Administrateur | — |

## Valeurs par défaut (réglages)
Réponses par demande : 10 · demandes ouvertes par client : 5 · durée : 30 jours · rappel avant la fin : 3 jours · photos : 5.

## Questions ouvertes
- (aucune)

## Références
- `RM-MESSAGERIE.md`, `RM-ALERTES.md`, `RM-RENDEZ-VOUS.md`, `RM-PAIEMENTS.md`, `RM-AVIS.md`, `RM-CLIENTS.md`, `RM-RECHERCHE.md`
- AlloVoisins : https://support.allovoisins.com/hc/fr/articles/360013305880 (répondre aux demandes), https://support.allovoisins.com/hc/fr/articles/4411371579410 (payer et se faire payer)
