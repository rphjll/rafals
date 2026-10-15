# Règle métier — Prestataires (sujet 02)

> Validé et formalisé le 28/09/2026 (phase 6 du démarrage).

## Objectif
Ce qu'un prestataire renseigne sur rafals (métiers, zone, SIRET) et quand les clients peuvent le trouver.

## Principes
- On devient prestataire depuis son compte, par « Proposer mes services » (voir `RM-COMPTES.md`).
- Un calendrier par métier du prestataire, jamais un par salarié, même pour une société (voir `GLOSSAIRE-METIER.md` ; « un calendrier par métier » décidé le 03/10/2026, `RM-AGENDA.md`).
- Sans SIRET : payé en espèces seulement ; rafals lui conseille de se déclarer (voir `GLOSSAIRE-METIER.md`, ⚠️ à vérifier juridiquement).

## Sans annonces : le prestataire se présente (décision de Raphael du 04/10/2026)
Réponse de Raphael, mot pour mot : « je vais enlever le sistème d'annonce car c trop dur je vais plutot faire en sorte que ca soit les comptes qui se présentent et les clients qui postes des demandes et les prestataires qui acceptent ou non ou ne font rien ». Puis choix « b » : enlever vraiment les annonces. MLD validé par Raphael le 04/10/2026 (« oui ») : `.doc/mld/MLD-retrait-annonces.html`. Les lignes « (choix de Claude) » ont été proposées avec le MLD.

⚠️ **Construit en partie le 07/10/2026** (demande de Raphael pour « Trouver un prestataire ») : les **photos de son travail** (table `photo_prestataire`, `db/schema_v24.sql`) et « **visible dès que le profil est rempli** » (la recherche ne demande plus d'annonce). **Le lieu dans le profil est construit depuis le 08/10/2026** (lot 9.1, `db/schema_v25.sql`). **Le code des annonces est retiré depuis le 09/10/2026** (lots 9.2 et 9.3) : plus de page « Mes annonces », plus de réservation directe, devis demandé depuis le profil. Les tables des annonces restent dans la base jusqu'au lot 9.4. Un métier se retire maintenant du profil sans condition (avant : refusé s'il avait des annonces).

**Lieu des services, précisions du 08/10/2026** (choix de Claude, lot 9.1) :
- Les profils existants et les nouveaux partent sur « chez le client ».
- « Chez moi » ou « les deux » demande que « Mon adresse » soit remplie (depuis le 07/10/2026, c'est aussi l'adresse du local), sinon : « Vos clients viennent chez vous : indiquez d'abord votre adresse dans « Mon adresse ». »
  - Exemple 1 : Léa, coiffeuse, choisit « chez moi » sans adresse → refusé ; elle enregistre « 12 rue des Lilas, Talence », puis choisit « chez moi » → accepté.
  - Exemple 2 : Karim, plombier, laisse « chez le client » → aucune adresse demandée.
- Tant que le lieu n'est pas « chez le client », l'adresse ne s'efface pas : « Vos clients viennent chez vous : changez d'abord le lieu de vos services dans votre profil. »
- Le filtre « Vient chez moi » de la recherche lit le lieu du profil (« chez le client » ou « les deux ») ; un prestataire qui a encore des annonces en ligne reste jugé sur elles jusqu'au lot 9.4.
- La page publique dit le lieu : « Part de Pessac, se déplace jusqu'à 15 km », « Vous reçoit à Pessac (adresse donnée après un rendez-vous) », ou les deux.

**Photos de son travail, précisions du 07/10/2026** (choix de Claude) : une photo ajoutée prend le rang suivant ; en retirer une fait remonter les suivantes d'un rang (on retire la n° 2 : la n° 3 devient la n° 2) ; les 2 premières sont sur sa carte dans « Trouver un prestataire », toutes sont sur sa page publique ; visibles par tous, sauf si l'activité est en pause, arrêtée ou bloquée ; une activité arrêtée ne peut plus en ajouter ni en retirer ; le fichier d'une photo retirée reste rangé (comme une ancienne photo de profil).
- Exemple 1 : Karim ajoute « cuisine.jpg » puis « bain.jpg » → photos n° 1 et n° 2 ; il retire la n° 1 → « bain.jpg » devient la n° 1.
- Exemple 2 : Julie a déjà 10 photos → « Au plus 10 photos sur votre profil : retirez-en une d'abord. »

**Le principe.** Il n'y a plus d'annonce. Le profil dit **qui** est le prestataire ; le **prix, le jour et l'heure** sont dans la proposition qu'il fait à un client précis (`RM-DEMANDES.md`).
- Exemple 1 : avant, Julie publiait « Ménage 2 h — 50 € ». Après, son profil dit « Julie Martin — Ménage, Nantes, jusqu'à 10 km », avec 3 photos ; quand Mme Dupont publie « Ménage de printemps, 3 pièces », Julie lui propose « 50 € · mardi 14/10 à 9 h · 2 h ».
- Exemple 2 : avant, Karim publiait « Dépannage fuite — 40 € de l'heure ». Après, il répond à la demande « Fuite sous l'évier » de M. Petit par « 60 € · lundi 12/10 à 8 h 30 · 1 h ».

**Trois façons d'arriver à un rendez-vous ou à un devis** (choix de Claude) :
1. Le client **publie une demande** ; les prestataires du métier et du coin répondent, ou ne font rien (`RM-DEMANDES.md`).
2. Le client trouve un prestataire par la recherche et clique **[Écrire à Karim]** sur son profil ; Karim lui fait une proposition dans la conversation, sans demande publiée (`RM-MESSAGERIE.md`).
3. Le client clique **[Demander un devis]** sur le profil d'un prestataire avec SIRET vérifié, en choisissant un de ses métiers (`RM-DEVIS.md`).

**Visible dès que le profil est rempli** (choix de Claude ; remplace « visible dès la première annonce ») : nom affiché, métier principal, ville et distance renseignés, activité ni en pause, ni arrêtée, ni bloquée.
- Exemple 1 : Julie remplit son profil le 01/10 à 10 h → elle apparaît dans la recherche « Ménage + Nantes » à 10 h.
- Exemple 2 : Karim, « en création », veut seulement être aidé à se déclarer → il met son activité **en pause** : aucun client ne le voit, et il la reprend quand il a son SIRET.

**Ce que le profil reçoit à la place des annonces** (choix de Claude) :
- jusqu'à **10 photos** de son travail (JPG ou PNG, 5 Mo chacune, même vérification que la photo du profil) ;
- le **lieu** : « chez le client », « chez moi / dans mon local » ou « les deux » ; pour « chez moi » ou « les deux », l'adresse du local est obligatoire, et la rue n'est montrée au client qu'après un rendez-vous ;
- **pas de prix** : il peut écrire ses tarifs habituels dans sa présentation (1 000 caractères).

**Ce qui disparaît** : la réservation directe d'un horaire par le client, les prix affichés, la limite de 20 annonces, le réglage « confirmation automatique ».

**Les moyens de paiement** se choisissent dans chaque proposition : espèces ; carte seulement avec un SIRET vérifié et le paiement par carte activé (`RM-PAIEMENTS.md`).

## Limites d'un prestataire sans SIRET (validé par Raphael le 09/10/2026, règle par règle)
Demande de Raphael du 04/10/2026, mot pour mot : « je veux que les prestataires ai une tres gros limite car sinon je pourrais avoir des problemes juridiques ». Proposition de Claude du 04/10/2026, reprise le 08/10/2026 (« c un peut strict sur certaines regles et d'autre pas assez »), puis tranchée une règle à la fois le 09/10/2026 ; écriture demandée par Raphael (« oui »).

**Construit le 12/10/2026** (lots 11.1 et 11.2 : `services/particuliers.py`, `schema_v26.sql`, `tests/test_particuliers.py`). ⚠️ **À montrer à un avocat avant la mise en ligne** : aucun de ces chiffres ne vient de la loi, et il n'existe pas de montant en dessous duquel on a le droit de travailler sans se déclarer.

Ces limites valent pour tout prestataire dont le SIRET n'est pas « vérifié » (absent, à vérifier ou refusé). **Dès que le SIRET est vérifié, elles tombent toutes.**

| # | Règle | Décision de Raphael |
|---|---|---|
| 1 | Métiers interdits sans SIRET | Plomberie, électricité, gaz, bâtiment, coiffure, esthétique, réparation auto, santé, garde d'enfants de moins de 3 ans, transport de personnes, alimentation (« A » : la liste proposée) |
| 2 | Prix d'une proposition | 100 € au plus (« A ») |
| 3 | Rendez-vous par mois | 2 au plus (« C 2 par mois » ; la proposition était 4) |
| 4 | Total des rendez-vous par an | 1 000 € au plus (« A ») |
| 5 | Durée sans SIRET | Pas de limite (« b pas de durés » ; la proposition était 6 mois) |
| 6 | Affichage | Étiquette « Particulier, non professionnel » sur le profil et sur chaque proposition ; avertissement au client avant d'accepter : « Pas de facture, pas de garantie, pas d'assurance professionnelle. » (« A ») |
| 7 | À fournir avant la première réponse | Vrai nom, vraie adresse (cachés du public, gardés par rafals), et la case « Mon activité est occasionnelle et je déclare mes revenus aux impôts », avec sa date (« bien comme ca ») |

**Exemples.**
- Emma, 19 ans, sans SIRET, fait 2 promenades de chien à 15 € en octobre. Un 3e client veut accepter sa proposition pour le 28/10 : refusé, « Emma a atteint sa limite du mois ». Elle peut de nouveau en avoir à partir du 1er novembre, et continuer ainsi des années tant qu'elle reste sous 1 000 € par an.
- Karim, plombier sans SIRET : il ne voit pas de bouton [Répondre] sur « Fuite sous l'évier » (« La plomberie demande un SIRET »). Il se fait aider par rafals pour créer son auto-entreprise ; SIRET vérifié, il répond à tout, sans limite.
- Emma propose « Débarrasser un garage, 250 € » : refusé, « Sans SIRET, une proposition ne peut pas dépasser 100 € ».
- Emma a déjà fait 980 € cette année : une proposition de 40 € ne peut pas être acceptée ; elle lit « Vous avez atteint la limite des particuliers : créez votre auto-entreprise ».

**Ce qui ne change pas** (règles déjà en place) : espèces seulement, pas de devis, pas de facture, pas de commission pour rafals.

**Précisions données par Raphael le 09/10/2026** (réponses mot pour mot entre guillemets) :
1. **Les métiers interdits sont rangés automatiquement, sans écran d'administration** (« non je ne veux pas m'ochuper de ca dans l'amin commande faut que ca soit automatique »). Claude range une fois pour toutes chaque métier de la liste en « SIRET obligatoire » ou « autorisé sans SIRET » ; un métier ajouté plus tard est « SIRET obligatoire » d'office (choix de Claude, par prudence).
   - SIRET obligatoire, par exemple : Plombier, Électricien, Maçon, Coiffeur / Coiffeuse, Esthéticienne, Mécanicien, Infirmier / Infirmière, Assistante maternelle, Chauffeur privé / VTC, Traiteur.
   - Autorisé sans SIRET, par exemple : Promeneur de chiens, Repassage, Montage de meubles, Soutien scolaire, Jardinier, Femme / Homme de ménage.
   - La liste complète (129 métiers au 09/10/2026) sera écrite au moment de construire, et montrée à l'avocat avec le reste.
2. **Les 1 000 € comptent seulement les rendez-vous qui ont eu lieu** (« ceux qui ont lieux ») : confirmés, dont l'heure est passée, ni annulés ni marqués « absent ». Un rendez-vous à venir ou annulé ne compte pas.
3. **L'année, ce sont les 12 derniers mois** (« les 12 derrniers mois »). Ex. le 09/10/2026, on additionne les rendez-vous d'Emma qui ont eu lieu du 09/10/2025 au 09/10/2026.
4. **2 rendez-vous par mois, pas 2 propositions** (choix « B ») : il peut envoyer autant de propositions qu'il veut ; il est bloqué quand 2 de ses propositions ont été acceptées pour ce mois-là.
   - Exemple 1 : en octobre, Mme Dupont et M. Petit refusent les propositions d'Emma ; elle peut en envoyer une troisième à Mme Martin.
   - Exemple 2 : Emma a déjà 2 rendez-vous confirmés en octobre (le 12 et le 20) ; Mme Martin ne peut pas accepter sa proposition pour le 28/10, mais elle peut accepter celle pour le 03/11.
   - Précisé par Claude (à relire) : le mois est celui du calendrier, et c'est le jour du rendez-vous qui compte ; les rendez-vous confirmés à venir comptent dans les 2, un rendez-vous annulé ne compte plus.
5. **Quand les 1 000 € sont atteints** (« si le plafond est atteit de plus de 1000 euro par ans a ce mement la oui elles sont retirés mais le resataire est prévenue ») : ses propositions encore en attente sont retirées, il est prévenu par mail, et il ne peut plus en envoyer tant qu'il est au-dessus (ou sans SIRET vérifié).
   - Exemple : le rendez-vous du 20/10 porte Emma à 1 010 € sur 12 mois ; ses 2 propositions en attente passent à « retirée » et elle reçoit « Vous avez atteint la limite des particuliers : créez votre auto-entreprise ».
   - Précisé par Claude (à relire) : un rendez-vous déjà confirmé n'est jamais annulé par rafals pour cette raison ; le total peut donc dépasser un peu 1 000 € (au plus de 2 rendez-vous de 100 €).

**Précisions prises en construisant, le 12/10/2026 (choix de Claude, en mode « sans question » ; à relire par Raphael) :**
- **« A eu lieu »** : rendez-vous confirmé, dont l'heure de fin est passée, sans absence signalée (ni du client ni du prestataire). Ex. Mme Dupont n'était pas là, Emma clique [Client absent] : ces 15 € ne comptent pas.
- **Les 12 derniers mois** : 365 jours, comptés à partir de la fin de chaque rendez-vous.
- **Au plafond de 1 000 €** : il ne peut plus répondre ni proposer, et aucun client ne peut plus accepter une proposition déjà envoyée ; une tâche de fond (toutes les 15 minutes) retire ses propositions en attente, écrit une ligne dans chaque conversation et lui envoie un seul mail.
- **Bouton [Répondre] verrouillé 🔒 avec la raison**, au lieu d'un bouton absent, quand la demande est dans ses métiers et son rayon mais qu'une limite l'arrête : « « Plombier » demande un SIRET… », « Ajoutez votre adresse dans « Mon profil »… » (sans adresse, depuis le 15/10/2026, pour tous les prestataires), « Sans SIRET, avant de répondre : … cochez… », « Vous avez atteint la limite des particuliers… ». Ex. Karim, sans SIRET, voit « Fuite sous l'évier » dans « Demandes près de chez moi » avec le bouton verrouillé.
- **La case se coche dans « Mon profil »**, carte « Sans SIRET : vos limites », qui montre aussi où il en est (« 1 sur 2 rendez-vous ce mois-ci », « 230,00 € sur 1 000,00 € »).
- **L'étiquette** est écrite en entier sur la page publique et sur chaque proposition ; sur les petites cartes de « Trouver un prestataire », le coin dit seulement « Particulier » (la place manque).
- **Les 4 plafonds sont des réglages** (`backend/app/reglages.py`) : 100 €, 2 par mois, 1 000 €, 365 jours.
- **Dans les tests automatiques**, les prestataires d'essai n'ont pas de SIRET ; pour ne pas tous les bloquer, les limites sont coupées partout sauf dans `tests/test_particuliers.py`, qui les vérifie une par une.

**Pourquoi la règle 5 est à signaler à l'avocat** : sans limite de durée, un particulier peut rester sans SIRET indéfiniment ; la règle des 6 mois était celle qui poussait à se déclarer (remarque de Claude du 09/10/2026, Raphael a maintenu son choix).

## Une seule adresse : l'adresse du prestataire est aussi son local (décision de Raphael du 07/10/2026)
Réponse de Raphael, mot pour mot : « mon local et mon adress c la meme chose donc compress les pour que ca fasse que 1 fin juste pour le titre met mon adresse ».
- Un prestataire n'a plus qu'une adresse à remplir, « Mon adresse ». L'enregistrer l'écrit aussi comme adresse de son local ; l'effacer efface aussi le local.
  - Exemple 1 : Karim enregistre « 3 rue du Moulin, 33600 Pessac » dans « Mon adresse » → c'est son adresse de client **et** celle de son local.
  - Exemple 2 : Léa, coiffeuse avec une annonce en ligne « au salon », veut effacer son adresse → refusé : « Des annonces en ligne ont lieu chez vous : mettez-les en pause ou changez leur lieu d'abord. »
- L'adresse d'un simple client ne crée aucun local.
- La base ne change pas : les tables `adresse` et `local` restent ; c'est le serveur qui recopie (`services/clients.py`). Choix de Claude, pour ne toucher à aucune table sans MLD.
- ⚠️ Conséquence à connaître : un prestataire dont le salon n'est pas à son domicile ne peut plus donner deux adresses différentes.
- Profil arrêté ou bloqué : l'adresse du compte se modifie toujours, le local ne bouge plus (choix de Claude).

## Un métier principal et des métiers secondaires (décidé le 27/09/2026)
Un prestataire choisit **un métier principal** et peut ajouter **des métiers secondaires**. Il apparaît dans les recherches de tous ses métiers, mais pour un métier secondaire, il apparaît **après** les prestataires dont c'est le métier principal. Dans chaque groupe, les mieux notés d'abord.
Réponse de Raphael, mot pour mot : « oui mais plus loin que les plombiers il doit aparaitre plus bas que les plombier et ca sera un clasement des mieux notés ».
- Exemple : Mme Dupont cherche « Électricien + Pessac ». Résultats : 1) Sophie, électricienne (métier principal), 4,8 ★ ; 2) Marc, électricien (métier principal), 4,2 ★ ; 3) Karim, plombier (électricien en métier secondaire), 4,9 ★ — Karim est 3e malgré sa meilleure note.
- Exemple : Mme Dupont cherche « Plombier + Pessac » → Karim est dans le 1er groupe, classé selon sa note parmi les plombiers.
**Pourquoi :** le client voit d'abord les spécialistes du métier qu'il cherche.
Le détail du classement (prestataires sans avis, distance…) sera traité dans le sujet 07 « Recherche ».

## Zone d'intervention : une ville et une distance (décidé le 27/09/2026)
Le prestataire indique sa ville de départ et la distance maximale, en kilomètres, jusqu'à laquelle il se déplace. Il apparaît dans les recherches des clients situés dans ce rayon. **Pour les demandes des clients**, le même rayon se mesure depuis l'adresse de son compte (décision du 15/10/2026, `RM-DEMANDES.md`).
- Exemple 1 : Karim, « Pessac, jusqu'à 15 km ». Mme Dupont à Talence (7,4 km) → elle le trouve.
- Exemple 2 : M. Petit à Libourne (38 km) → il ne trouve pas Karim.
**Cas limite tranché :** la distance est mesurée à vol d'oiseau, entre le centre des deux villes (plus simple et suffisant pour choisir un prestataire).

## Vérification automatique du SIRET (décidé le 27/09/2026)
Quand un prestataire écrit son SIRET, rafals le cherche aussitôt dans le répertoire public des entreprises de l'État (INSEE, gratuit). Le SIRET est refusé si le numéro n'existe pas, si l'établissement est fermé, ou si le nom de l'entreprise ne correspond pas au nom du prestataire.
- Exemple 1 : Julie Martin écrit 912 345 678 00014 → trouvé, ouvert, au nom de « Julie Martin » → accepté ; le paiement par carte devient possible sur ses annonces.
- Exemple 2 : un inconnu écrit 123 456 789 00012 → numéro inexistant → refusé ; il reste « sans SIRET » (espèces seulement).
- Exemple 3 : Karim écrit le SIRET de son oncle « Plomberie Benali » → le nom ne correspond pas → refusé.
**Pourquoi :** empêcher un faux SIRET d'ouvrir le paiement par carte.
**Cas limite tranché :** si le répertoire de l'État ne répond pas (panne), le SIRET est mis « en attente » et revérifié automatiquement plus tard ; en attendant, espèces seulement.

## Lieu du service : au choix, pour chaque annonce (décidé le 27/09/2026 ; remplacé le 04/10/2026 par un seul lieu dans le profil, voir « Sans annonces »)
Pour chaque annonce, le prestataire indique où a lieu le service : « chez le client », « chez moi / dans mon local » (adresse du local écrite une fois dans le profil, voir `RM-ANNONCES.md`), ou « les deux ».
- Exemple 1 : Karim, « Plomberie, dépannage fuite » → chez le client (la zone d'intervention s'applique).
- Exemple 2 : Léa, coiffeuse à Mérignac : « Coupe femme — au salon, 12 rue des Lilas » et « Coupe à domicile — chez le client, +10 € ».
**Cas limite tranché :** pour un service « chez moi », la zone d'intervention sert seulement à la recherche (les clients dans le rayon voient l'annonce) ; le client se déplace.

## Visible tout de suite (décidé le 27/09/2026 ; « dès sa première annonce » remplacé le 04/10/2026 par « dès que le profil est rempli », voir « Sans annonces »)
Un prestataire est visible des clients dès qu'il publie sa première annonce, sans attendre l'administrateur. L'administrateur voit chaque nouveau prestataire dans son écran « Administration » et peut le bloquer à tout moment.
- Exemple 1 : Julie remplit son profil le 01/10 à 10 h, publie « Ménage 2 h — 50 € » à 10 h 05 → visible à 10 h 05.
- Exemple 2 : le 02/10, Raphael voit un profil « Plombier pas cher » avec des photos volées → il le bloque ; ses annonces disparaissent aussitôt.
**Pourquoi :** pas d'attente pour les prestataires, pas de travail quotidien obligatoire pour Raphael.
Un prestataire sans annonce publiée n'apparaît dans aucune recherche (ex. Karim « en création », qui se fait seulement aider à se déclarer).

## Contenu du profil (proposé par Claude, validé par Raphael le 28/09/2026)
- Obligatoire : nom affiché (ex. « Julie Martin — Ménage » ou « Net & Clair »), métier principal, ville + distance.
- Facultatif : photo ou logo, présentation (quelques lignes), métiers secondaires, SIRET.
- Le téléphone et l'adresse mail du prestataire ne sont **pas** affichés publiquement : le client les voit seulement après avoir réservé. **Pourquoi :** éviter que les clients contournent rafals (et la commission) dès la première recherche.

## Précisions prises au lot 2.3 (proposé par Claude le 28/09/2026 en mode « tout seul », validé par Raphael le 29/09/2026 point par point)
- **Distance** : de 1 à **100 km** (validé par Raphael le 29/09/2026). Distances réelles calculées sur la liste officielle des communes : Pessac → Talence 7,4 km, Pessac → Libourne 38 km.
- **Au plus 5 métiers secondaires** (validé par Raphael le 29/09/2026) ; le métier principal ne peut pas être aussi secondaire.
- **Nom affiché** : 2 à 80 caractères. **Présentation** : 1 000 caractères au plus (validé par Raphael le 29/09/2026).
- **SIRET** : on peut le taper avec des espaces ; rafals vérifie tout de suite qu'il a 14 chiffres **et la bonne clé de contrôle** (le dernier chiffre se calcule à partir des autres). Un SIRET nouveau ou changé passe « à vérifier » (vérification auprès de l'État au lot 2.4) ; le retirer = « absent ». ⚠️ L'exemple de Julie (912 345 678 00014) est inventé et ne passe pas la clé : il reste un exemple de lecture, pas un vrai numéro.
- **Photo** : JPG ou PNG, 5 Mo au plus (même vérification que l'accord des parents). Elle est visible de tous (elle sera montrée sur les annonces) (validé par Raphael le 29/09/2026).
- **Statuts** : pause ↔ reprise par le prestataire ; arrêt (définitif : plus aucune modification) ; blocage et déblocage par l'administrateur seulement. Un prestataire bloqué ne peut ni reprendre ni se mettre en pause ; seul l'administrateur le débloque, ce qui le remet « actif » (validé par Raphael le 29/09/2026 : pas de déblocage automatique). Un prestataire arrêté ne peut plus être bloqué ni débloqué.
- **Devenir prestataire** exige l'adresse vérifiée et, avant 18 ans, l'accord des parents accepté (règle de `RM-COMPTES.md`), sinon message clair.
- Toute création, modification, photo et changement de statut est écrit au journal des actions.

## Vérification du SIRET auprès de l'État : précisions du lot 2.4 (validé par Raphael le 29/09/2026)
- Service utilisé : **« Recherche d'entreprises »** de l'État (recherche-entreprises.api.gouv.fr), gratuit, sans inscription.
- **Vérifié** si le SIRET existe, que l'établissement est **ouvert**, et que le **nom de famille du compte** apparaît dans le nom officiel ou parmi les **dirigeants**.
  - Ex. Julie Martin, auto-entrepreneuse, nom officiel « JULIE MARTIN » → vérifié. Julie gérante de « NET ET CLAIR » (dirigeante) → vérifié.
- **Nom caché par l'État** (« non diffusible », fréquent chez les auto-entrepreneurs) : **accepté d'office** si le SIRET existe et est ouvert (décision de Raphael du 29/09/2026).
- **Refusé tout de suite, avec la raison** (le SIRET n'est pas enregistré) : introuvable ; établissement fermé ; SIRET d'une autre entreprise (« Ce SIRET appartient à « GOOGLE FRANCE » : il ne semble pas être le vôtre… »).
- **Service injoignable** : SIRET enregistré « à vérifier » (espèces seulement), nouvel essai automatique **toutes les 30 minutes**, écrit au journal.
- **Cas particulier** (ex. salarié qui n'est pas dirigeant) : l'administrateur peut **valider le SIRET à la main**, après avoir vu un justificatif.

## Qui peut faire quoi
| Action | Qui | Condition |
|---|---|---|
| Devenir prestataire | Titulaire d'un compte | Adresse mail vérifiée ; accord des parents vérifié avant 18 ans |
| Modifier son profil | Le prestataire lui-même | — |
| Ajouter ou changer son SIRET | Le prestataire lui-même | Vérifié automatiquement |
| Bloquer / débloquer un prestataire | Administrateur | — |

## Désactivation / clôture / suppression (proposé par Claude, validé par Raphael le 28/09/2026)
- **Mettre en pause** (réversible) : le prestataire se rend invisible (ex. Julie pendant ses congés d'août) ; ses rendez-vous déjà pris restent.
- **Bloquer** (réversible, par l'administrateur) : invisible, ne peut plus publier ; ses rendez-vous à venir sont annulés et les clients prévenus.
- **Arrêter son activité** (définitif) : le profil prestataire est clôturé ; ses factures restent consultables (la loi oblige à les garder 10 ans).
- **Supprimer** : interdit dès que le prestataire a eu un rendez-vous ou émis une facture.

## Valeurs figées
Le nom, l'adresse et le SIRET du prestataire sont recopiés sur chaque devis et chaque facture au moment où ils sont émis. Ex. Julie change de nom commercial en 2027 → ses factures de 2026 gardent l'ancien nom.

## Questions ouvertes
- ⚠️ Prestataires sans SIRET payés en espèces : à faire vérifier juridiquement, avec les limites du § « Limites d'un prestataire sans SIRET » (09/10/2026).

## Références
- `GLOSSAIRE-METIER.md`, `RM-COMPTES.md`

## Sans SIRET : tout reste visible, avec un cadenas (décision de Raphael du 15/10/2026)

Raphael : « c pareil qu'une auto entreprise sauf que les boutons qui ne peut pas utiliser y'a un cadenas dessus ». Un prestataire sans SIRET vérifié voit les mêmes écrans qu'un auto-entrepreneur ; ce qu'il ne peut pas faire reste à sa place, grisé avec 🔒, et un clic donne la raison. Il **peut** répondre aux demandes et faire des propositions pour les 50 métiers autorisés sans SIRET, dans ses limites (paragraphe « Limites d'un prestataire sans SIRET »).

| Endroit | Ce qui est verrouillé 🔒 | Raison affichée |
|---|---|---|
| Accueil, Demandes près de chez moi | [Répondre] (métier qui demande un SIRET, case pas cochée, limite atteinte) | la raison de la limite |
| Fenêtre « Faire une proposition » | case « Carte sur rafals » | « Le paiement par carte demande un SIRET vérifié… » |
| Mon agenda › Rendez-vous passés | [Payé…] (qui fait la facture) | « Une facture demande un SIRET vérifié… » |
| Mes démarches | [Déclarer à l'URSSAF], [Rappels par mail] | « Déclarer à l'URSSAF concerne les auto-entrepreneurs… » |
| Mon profil › Paiement par carte | [Activer le paiement par carte] | (déjà en place) |
| Sa page publique, vue par un client | [Demander un devis] | « Ce prestataire n'a pas de SIRET vérifié : il ne fait pas de devis… » |

- Exemple 1 : Emma, 19 ans, promène des chiens sans SIRET → elle répond à « Promener mon chien » ; dans sa proposition, la case « 🔒 Carte sur rafals » est grisée, seule « Espèces » est possible.
- Exemple 2 : Marie ouvre la page d'Emma → [🔒 Demander un devis] ; un clic : « Ce prestataire n'a pas de SIRET vérifié : il ne fait pas de devis. Écrivez-lui pour vous mettre d'accord. »
