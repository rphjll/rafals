# Règle métier — Annonces (sujet 05)

> ⚠️ **Plus appliqué depuis le 09/10/2026** (lots 9.2 et 9.3) : le code des annonces est retiré du serveur et des écrans. Ce fichier sera rangé aux archives au lot 9.4. Restent valables et repris ailleurs : la date de fin d'un métier (`RM-PRESTATAIRES.md`) et l'adresse où le prestataire reçoit (`RM-PRESTATAIRES.md` § « Une seule adresse »).

> Validé et formalisé le 29/09/2026 (lot 3.0).
>
> ⚠️ **Annonces retirées : décision de Raphael du 04/10/2026** (« je vais enlever le sistème d'annonce car c trop dur », puis choix « b » : les enlever vraiment). La règle qui les remplace est dans `RM-PRESTATAIRES.md` § « Sans annonces ». MLD validé : `.doc/mld/MLD-retrait-annonces.html`.
> **Pas encore construit** : le retrait se fait après les lots 8.3 et 8.4. D'ici là, le code suit encore ce fichier.
> Après le retrait, il restera valable seulement : « Arrêter un métier » (la date d'arrêt dans le calendrier, sans la partie sur les annonces cachées) et « Adresse du lieu “chez moi” » (la rue du local montrée seulement après un rendez-vous). Ces deux parties seront alors recopiées dans `RM-AGENDA.md` et `RM-PRESTATAIRES.md`, et ce fichier sera rangé dans les archives.

## Objectif
Ce qu'un prestataire met en ligne pour être trouvé et réservé : nom du service, prix, lieu, modes de paiement.

## Déjà décidé (sujets 02 et glossaire, 27-28/09/2026)
- On dit **annonce** partout, jamais « publication » ni « prestation ».
- **Lieu**, pour chaque annonce : « chez le client », « chez moi / dans mon local » (adresse du local prise dans le profil, voir plus bas), ou « les deux » (voir `RM-PRESTATAIRES.md`).
- **Paiement**, pour chaque annonce : un prestataire avec SIRET vérifié choisit « carte sur le site » et/ou « espèces » ; sans SIRET : espèces seulement (⚠️ à vérifier juridiquement).
- Le prestataire devient visible des clients dès sa **première annonce publiée**.

## Contenu d'une annonce (décidé le 29/09/2026)
Titre, métier, prix, durée (sauf « sur devis »), lieu, modes de paiement, plus :
- une **description** de 1000 caractères au plus (comme la présentation du profil) ;
- jusqu'à **5 photos** JPG ou PNG, 5 Mo chacune (même vérification que la photo du profil).
- Exemple : Julie, « Ménage 2 h — 50 € », description « Produits fournis, repassage non compris », 1 photo d'une cuisine qu'elle a nettoyée.
**Pourquoi :** le client se fait une idée avant de réserver.

## Adresse du lieu « chez moi » : la ville pour tous, la rue après réservation (décidé le 29/09/2026)
- Tout le monde voit la ville (ex. « Mérignac ») ; le client voit la rue (« 12 rue des Lilas ») seulement après avoir réservé, comme le téléphone du prestataire.
- Exemple : Léa, « Coupe femme — au salon ». Avant de réserver, Mme Dupont voit « Mérignac » ; après, « 12 rue des Lilas, 33700 Mérignac ».
**Pourquoi :** protège un prestataire qui reçoit chez lui, et évite qu'on contourne rafals.
- **Une seule adresse de local, dans le profil** (décidé le 29/09/2026) : Léa écrit « 12 rue des Lilas » une fois dans « Mon activité » ; ses 4 annonces « au salon » l'utilisent ; si elle déménage, elle la change une fois. Une annonce « chez moi » est refusée tant que le profil n'a pas d'adresse de local. (Précise `RM-PRESTATAIRES.md`, qui disait « avec l'adresse » pour chaque annonce.)

## Forme du prix (décidé le 29/09/2026)
Au choix, pour chaque annonce :
- **prix fixe** : ex. Julie, « Ménage 2 h — 50 € » ;
- **prix à l'heure** : ex. Karim, « Dépannage fuite — 40 € de l'heure » ;
- **sur devis** : ex. un maçon, « Muret de jardin — prix sur devis » (il vient d'abord voir ; les devis arrivent au niveau 5). Réservé aux prestataires avec un SIRET (décidé le 02/10/2026, `RM-DEVIS.md`).
**Pourquoi :** certains métiers ne peuvent pas connaître le prix à l'avance.

## Durée obligatoire (décidé le 29/09/2026)
Chaque annonce à prix fixe ou à l'heure a une durée (ex. 30 min, 2 h), qui bloque l'agenda du prestataire (pas de durée pour « sur devis », voir plus bas).
- Exemple : Julie, « Ménage — 2 h ». Mme Dupont réserve mardi à 9 h : Julie est occupée de 9 h à 11 h, et le client suivant ne peut réserver qu'à partir de 11 h.
**Pourquoi :** rafals ne propose que des horaires vraiment libres, donc jamais deux clients en même temps.

## Prix à l'heure : le client choisit le nombre d'heures, dans des limites (décidé le 29/09/2026)
Pour une annonce à l'heure, le prestataire fixe un nombre d'heures minimum et maximum ; le client choisit en réservant, voit le prix total avant de confirmer, et l'agenda est bloqué pour ce temps.
- Exemple 1 : Sonia, « Ménage — 25 €/h, de 2 h à 4 h ». Mme Dupont choisit 3 h → elle voit « 75 € » ; Sonia est occupée 3 h.
- Exemple 2 : Karim fixe « de 1 h à 1 h » → le client ne choisit rien (1 h, 40 €).
**Pourquoi :** le client connaît le montant avant de réserver.

## Sur devis : le client envoie une demande écrite (décidé le 29/09/2026)
Pour une annonce « sur devis », il n'y a pas de rendez-vous : le client décrit son besoin (et peut ajouter des photos), puis le prestataire répond par un devis.
- Exemple : Mme Dupont écrit à Paul, maçon : « Muret de 5 mètres au fond du jardin », avec 2 photos. Paul répond par un devis (niveau 5).
**Conséquence :** une annonce « sur devis » n'a **pas de durée** (l'agenda n'est pas utilisé) ; la durée reste obligatoire pour les prix fixes et à l'heure. La demande écrite et le devis seront précisés avec le sujet 10 (Devis).

## Valeurs figées (invariant du projet)
Le titre, le prix et la durée sont recopiés sur le rendez-vous au moment de la réservation.
- Exemple : Mme Dupont réserve « Ménage 2 h — 50 € » le 01/10 pour le 14/10 ; le 05/10, Julie passe l'annonce à 55 € → Mme Dupont paie toujours 50 € ; les réservations suivantes, 55 €.

## Chaque annonce est rangée dans un des métiers du prestataire (décidé le 29/09/2026)
Le prestataire choisit, pour chaque annonce, un métier parmi ceux de son profil (principal ou secondaires).
- Exemple 1 : Karim (Plombier + Chauffagiste) range « Dépannage fuite » dans Plombier et « Entretien chaudière » dans Chauffagiste. Un client qui cherche « chauffagiste » voit directement « Entretien chaudière ».
- Exemple 2 : Karim ne peut pas publier dans « Coiffeur » sans ajouter d'abord ce métier à son profil.
**Pourquoi :** le profil correspond toujours à ce que le prestataire propose, et la recherche montre la bonne annonce.

## Pause et retrait, jamais d'effacement (décidé le 29/09/2026)
- **[Mettre en pause]** : l'annonce est cachée des clients et reste dans « Mes annonces » ; **[Republier]** la remet en ligne. Ex. Julie met « Repassage — 20 € » en pause pendant août.
- **[Retirer]** : Julie ne veut plus la proposer ; l'annonce est rangée dans « Annonces retirées », hors de sa liste principale ; elle peut la **republier** depuis là telle quelle (confirmé le 29/09/2026 ; ex. retirée en juin, republiée en décembre).
- Une annonce n'est **jamais effacée**, pour garder l'historique des rendez-vous et des factures.
- Les rendez-vous déjà pris restent dans les deux cas.

## Arrêter un métier : une date de fin dans le calendrier, pas un bouton « supprimer » (décidé le 29/09/2026)
Réponse de Raphael, mot pour mot : « au lieux d'un bouton suprimer ce metier je veux que dans le calendrier il puisse choisir une date de cloturations donc si il dis demain par exemple toute les reservations apres seront annulés et il n'execrcera plus ce metier mais si il veut reprendre faut quand meme faire en sorte qu'il puisse ».
- Le prestataire choisit dans son calendrier une **date de fin** pour un de ses métiers. (Depuis le 03/10/2026 : bouton [Date d'arrêt] du calendrier de ce métier, un seul jour ; tous les jours d'après y sont fermés. Le bouton de « Mon activité » est retiré. Voir `RM-AGENDA.md`.)
- Les réservations de ce métier **après** cette date sont annulées ; après cette date, il n'exerce plus ce métier.
- Il peut **reprendre** ce métier plus tard.
- Précision de Raphael, mot pour mot : « quans il cloture a partir d'une date apres c bloqué pour tout lesreste de sa vie il peut plus faire d'annonces sur ce metier ou quoi sauf si il re met ce metier dans se compétences » → après la date de fin, le métier sort de son profil ; pour reprendre, il le remet dans ses métiers.
- Exemple : le 01/11, Karim met la date de fin « 15/11 » sur Chauffagiste. Le rendez-vous « Entretien chaudière » de Mme Dupont le 10/11 reste ; celui de M. Petit le 20/11 est annulé.
- **Ses annonces de ce métier sont cachées, pas effacées** (décidé le 29/09/2026) : du 16/11 à mars, aucun client ne voit « Entretien chaudière » ; en mars, Karim remet Chauffagiste dans ses métiers, retrouve l'annonce dans « Mes annonces » et clique [Republier], sans rien réécrire.
- **Métier principal arrêté : un métier secondaire devient principal automatiquement** (décidé le 29/09/2026 au lot 3.1). Réponse de Raphael, mot pour mot : « il arret la plomberie et un message vas dire chauffagise vas passer en metier principal automatiquement donc je veux que ca soit automatique pas que ca soit lui qui doive le changer ». Ex. Karim (principal Plombier, secondaire Chauffagiste) met la date de fin « 15/11 » sur Plombier → message « Après le 15/11, Chauffagiste deviendra votre métier principal » ; le 16/11, c'est fait sans rien à changer. **S'il a plusieurs métiers secondaires**, le message lui demande lequel deviendra principal, le 1er ajouté à son profil étant choisi d'avance (ex. Julie arrête « Femme de ménage » ; elle a « Repassage » puis « Garde d'enfants » → « Repassage » proposé, elle peut choisir « Garde d'enfants »).
- **Seul métier arrêté : le profil reste affiché, sans annonce** (décidé le 29/09/2026). Réponse de Raphael, mot pour mot : « non il n'est pas caché juste il n'y a pas d'annoce donc il faut que pour les autres ca soit affiché aucune annonce ». Ex. Léa n'a que Coiffeur et met la date de fin « 15/11 » : le 16/11, son profil est toujours visible et affiche « Aucune annonce » ; son activité n'est ni en pause ni arrêtée. En mars, elle remet Coiffeur (elle enlève la date de fin) et republie ses annonces. Comme tout prestataire sans annonce en ligne, elle n'apparaît dans aucune recherche (`RM-PRESTATAIRES.md`).
- ⚠️ Change l'écran actuel « Mon activité » (lot 2.5), qui permet de retirer directement un métier secondaire : à reprendre au niveau 3.

## 20 annonces en ligne au plus (décidé le 29/09/2026)
Un prestataire a au plus **20 annonces en ligne** en même temps (réglage modifiable sans toucher au code) ; les annonces en pause ou retirées ne comptent pas.
- Exemple 1 : Julie en a 3 → aucun souci.
- Exemple 2 : un tricheur essaie d'en publier une 21e → « Vous avez déjà 20 annonces en ligne : mettez-en une en pause pour publier celle-ci. »
**Pourquoi :** empêcher qu'un seul compte remplisse les recherches.

## Précisions prises au lot 3.1 (proposées par Claude, validées par Raphael le 29/09/2026)
- **Pas de brouillon** : une annonce écrite est aussitôt en ligne. Titre de 3 à 80 caractères.
- **Carte** : cochée seulement si le SIRET est vérifié au moment d'écrire l'annonce (« Le paiement par carte demande un SIRET vérifié : sans lui, espèces seulement. »). Si le SIRET est perdu plus tard, l'annonce passe seule en espèces et revient à la carte quand il est de nouveau vérifié.
- **Ville montrée** : pour « chez moi », la ville du local ; sinon, la ville du prestataire.
- **Local** : impossible à effacer tant qu'une annonce « chez moi » ou « les deux » est en ligne ; effacé quand le compte est fermé (ce peut être le domicile).
- **Retirer un métier depuis le formulaire du profil** : accepté seulement s'il n'a jamais eu d'annonce (ex. ajouté par erreur) ; sinon « mettez-lui une date de fin dans votre calendrier ».
- **À la date de fin** : une tâche automatique (toutes les heures) met « en pause » les annonces en ligne du métier arrêté ; c'est pour cela que Karim, en mars, clique [Republier]. Republier est refusé tant que le métier n'est pas repris.
- **Métier principal remplacé** : si le métier choisi pour le remplacer est lui-même arrêté entre-temps, c'est le 1er métier secondaire encore exercé qui le remplace. L'ancien principal reste dans le profil comme « métier arrêté ».
- « Télécharger mes données » contient maintenant les annonces et le local.

## Qui peut faire quoi
| Action | Qui | Condition |
|---|---|---|
| Publier une annonce | Le prestataire | Peut réserver ou publier (adresse vérifiée, accord des parents avant 18 ans — `RM-COMPTES.md`) ; activité ni en pause, ni arrêtée, ni bloquée ; métier de son profil ; moins de 20 annonces en ligne |
| Modifier, mettre en pause, retirer, republier | Le prestataire | Ses propres annonces seulement |
| Voir une annonce en ligne | Tout le monde, même sans compte | La rue du local seulement après réservation |
| Cacher une annonce | L'administrateur | Bloquer le prestataire cache toutes ses annonces (`RM-PRESTATAIRES.md`) ; modération fine : sujet 16 |

## Désactivation / clôture / suppression
- Pause (réversible) et retrait : voir plus haut.
- Prestataire en pause, arrêté ou bloqué : toutes ses annonces sont cachées, sans être modifiées.
- Suppression : jamais.

## Questions ouvertes
- (aucune pour l'instant ; ⚠️ espèces sans SIRET toujours à faire vérifier juridiquement)

## Références
- `GLOSSAIRE-METIER.md`, `RM-PRESTATAIRES.md`, `RM-METIERS.md`
