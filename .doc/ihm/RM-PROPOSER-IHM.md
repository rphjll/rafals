# Proposer mes services / Mon profil — Interface

> **Changé le 09/10/2026** (lot 9.3, retrait des annonces) : dans la carte « Mes métiers », les phrases ne parlent plus d'annonces (« Vous n'apparaissez plus dans les recherches de ce métier. », « Coiffeur repris : vous apparaissez de nouveau dans ses recherches. ») ; carte « Paiement par carte » : « Vous pouvez accepter la carte dans vos propositions. »

> **Renommé le 07/10/2026** (demande de Raphael : « l'onglet actuel mon activité il vas s'appeler mon profil ») : partout où ce document écrit « Mon activité » pour cette page, lire **« Mon profil »** (entrée du menu, titre de la page, fils d'Ariane, messages « page « Mon profil » »). « Mon activité » désigne maintenant la page d'ensemble `/mon-activite` (`RM-MON-ACTIVITE-IHM.md`). Le contenu de la page ne change pas.

> Fichiers : `frontend/src/pages/ProposerPage.vue`, `frontend/src/components/prestataire/FormulaireProfil.vue`, `FicheActivite.vue`, `CarteMesAnnonces.vue`, `CarteMetiers.vue`, `frontend/src/components/CarteAdresse.vue` (local), `frontend/src/components/AppChoixCommune.vue`, `frontend/src/outils/prestataires.ts`. Construit au lot 2.5 (29/09/2026), complété au lot 3.2 (29/09/2026). Règles : `RM-PRESTATAIRES.md`, `RM-ANNONCES.md`. Maquettes : `maquette-lot-2.5-prestataire.html`, `maquette-lot-3.2-annonces.html`.

> ⚠️ **Depuis le 07/10/2026, « Mon profil » et « Mon compte » sont une seule page** (`/profil`, `frontend/src/pages/ProfilPage.vue`), ouverte par le rond des initiales : voir `RM-PROFIL-IHM.md`. `ProposerPage.vue` n'existe plus ; `/proposer` mène à `/profil` ; pour un client, « Proposer mes services » est une carte de cette page, dont le bouton déplie le formulaire. Les cartes décrites ci-dessous n'ont pas changé.

> **07/10/2026 : la carte « Mon local » n'existe plus** ; l'adresse du local est la carte « Mon adresse » (`RM-PROFIL-IHM.md` § « Une seule adresse »).

## Page `/proposer`
Entrée de menu « Proposer mes services », qui devient « Mon activité » quand le compte a un profil de prestataire. Contenu centré (720 px au maximum).

**(pas connecté)** carte « Proposer mes services » — « Connectez-vous pour proposer vos services. » — [Se connecter] puis [Créer mon compte] (secondaire).

## Sans profil : « Proposer mes services »
1. Titre « Proposer mes services ».
2. (adresse non vérifiée) bandeau orange « Vérifiez d'abord votre adresse mail (lien reçu par mail), puis revenez proposer vos services. » — pas de formulaire.
3. (16-17 ans sans accord accepté) bandeau orange « Il faut d'abord que l'accord de tes parents soit accepté. » + [Mon compte] — pas de formulaire.
4. Sinon : « Créez votre profil de prestataire : les clients vous trouveront dès que vous publierez votre première annonce. » puis le formulaire.

## Formulaire du profil (création et modification)
**Carte « Votre activité »**
1. Nom affiché * — aide « Ce que les clients verront, ex. « Julie Martin — Ménage » ou « Net & Clair ». »
2. Métier principal * — recherche de métier (sans les dossiers) ; une fois choisi, bandeau vert « ✓ Plombier » + [Changer].
3. Métiers secondaires (5 au plus) — pastilles « Électricien × » (× retire) puis recherche « Ajouter un métier : tapez les premières lettres… » (les métiers déjà choisis ne sont plus proposés) ; aide « Vous apparaîtrez aussi dans ces recherches, après les spécialistes. » ; à 5 : « 5 métiers secondaires : c'est le maximum. »

**Carte « Où intervenez-vous ? »** (2 colonnes sur ordinateur)
4. Ville de départ * — recherche par nom ou code postal (« ex. Pessac ou 33600 ») ; choisie : « ✓ Pessac (33600) » + [Changer].
5. Jusqu'à (km) * — nombre, 15 par défaut ; aide « De 1 à 100 km, à vol d'oiseau. »
5 bis. (lot 9.1, 08/10/2026) Où ont lieu vos services ? * — 3 cases côte à côte (`AppChoix`) : « Chez le client — Je me déplace » (choisie au départ), « Chez moi — Le client vient à mon adresse », « Les deux — Au choix, à chaque proposition ». Avec « Chez moi » ou « Les deux », une ligne dessous : « Il faut que « Mon adresse » soit remplie. Votre rue n'est montrée à un client qu'après un rendez-vous. » Erreur du serveur si l'adresse manque : « Vos clients viennent chez vous : indiquez d'abord votre adresse dans « Mon adresse ». »

**Carte « Présentation et SIRET »**
6. Présentation — zone de texte avec compteur « 57 / 1000 » (rouge au-delà).
7. SIRET (facultatif) — « 14 chiffres, ex. 443 061 841 00047 » ; aide « Sans SIRET, vos clients ne pourront vous payer qu'en espèces. Avec un SIRET vérifié par l'État, la carte bancaire devient possible. »
8. (erreur) bandeau rouge au-dessus du bouton : message du serveur (ex. « Ce SIRET appartient à « GOOGLE FRANCE » : il ne semble pas être le vôtre… »), ou « Choisissez votre métier principal. » / « Choisissez votre ville de départ. » vérifiés par l'écran.
9. Boutons : création [Proposer mes services] → message vert « Votre profil de prestataire est créé. », le menu passe à « Mon activité » ; modification [Enregistrer] + [Annuler] (secondaire) → « Profil enregistré. »

## Avec un profil : « Mon activité »
1. Titre « Mon activité ».
2. Bandeau selon le statut : bloqué (rouge) « Votre profil est bloqué par l'administrateur de rafals : contactez-le. » ; en pause (orange) « Votre profil est en pause : vous n'apparaissez plus dans les recherches. Vos rendez-vous déjà pris restent. » ; arrêté (orange) « Votre activité est arrêtée : ce profil n'est plus visible ni modifiable. »
3. Carte du profil : photo ronde (ou initiales « KB »), nom affiché + badge d'état (actif vert, en pause gris, bloqué rouge, arrêté gris) ; puis :
   - Métier : « Plombier · aussi Électricien, Chauffagiste »
   - Zone : « Pessac (33600), jusqu'à 15 km »
   - SIRET : badge (« SIRET vérifié » vert, « À vérifier » orange, « SIRET refusé » rouge, « Sans SIRET » orange), le numéro lisible « 443 061 841 00047 », et si non vérifié « espèces seulement » (+ « (nouvel essai automatique auprès de l'État) » si à vérifier)
   - Présentation (si remplie)
   - Boutons [Modifier mon profil] → le formulaire prérempli ; [Changer ma photo] → choix d'un fichier JPG ou PNG → « Photo enregistrée. » (absents si arrêté)
   - **Carte « Photos de mon travail »** (ajoutée le 07/10/2026, `frontend/src/components/prestataire/CartePhotosTravail.vue`, juste sous la carte du profil ; absente si arrêté) : phrase « Montrez ce que vous savez faire : une cuisine posée, une haie taillée… 10 photos au plus (JPG ou PNG, 5 Mo chacune). Les 2 premières sont sur votre carte dans « Trouver un prestataire ». » ; les photos en vignettes (4/3), chacune avec [Retirer] (rouge clair) → « Photo retirée. » ; « Aucune photo pour l'instant. » s'il n'y en a pas ; [Ajouter une photo] → choix d'un fichier → « Photo ajoutée. » ; à 10 photos, le bouton laisse la place à « 10 photos : retirez-en une pour en ajouter une autre. »
   - Carte « Visibilité » : la phrase est maintenant « Vous apparaissez dans les recherches tant que votre activité est active. » (plus besoin d'annonce, 07/10/2026).
4. **Carte « Mes annonces » : cachée depuis le 05/10/2026** (annonces retirées, `RM-PRESTATAIRES.md` § « Sans annonces » ; le fichier `CarteMesAnnonces.vue` existe encore, il sera supprimé au lot 9.3). Elle affichait : « 3 en ligne sur 20 » à droite du titre ; « Vous apparaissez dans les recherches grâce à vos annonces en ligne. » (ou, sans annonce en ligne, « Aucune annonce en ligne : écrivez-en une pour que les clients vous trouvent. ») ; [Voir mes annonces] (s'il en a) → `/mes-annonces`, [Écrire une annonce] → `/mes-annonces/nouvelle`.
5. Carte « Mes métiers » (RM-ANNONCES : pas de bouton « supprimer ») : une ligne par métier, séparées par un trait. **Depuis le 03/10/2026, la date d'arrêt se règle dans « Mon agenda › Calendrier », bouton [Date d'arrêt]** (`RM-AGENDA-IHM.md`) : ici elle est seulement affichée.
   - Principal : « Plombier » + badge vert « principal » ; si date d'arrêt : « Arrêt prévu après le 15/11/2026 : ensuite, Électricien deviendra votre métier principal. » (ou « c'est votre seul métier ; votre profil restera affiché, sans annonce. »).
   - Secondaires : « Électricien » (+ « Arrêt prévu après le 31/12/2026. »).
   - Arrêtés : « Chauffagiste » + badge gris « arrêté depuis le 31/08/2026 », « Ses annonces sont en pause : reprenez le métier, puis republiez-les. » ; [Reprendre ce métier] (principal) → « Chauffagiste repris : republiez ses annonces dans « Mes annonces ». »
   - Note : « Ajouter un métier : [Modifier mon profil]. Arrêter un métier : dans Mon agenda › Calendrier (lien), bouton « Date d'arrêt ». Après cette date, les annonces du métier sont mises en pause (gardées), et les rendez-vous de ce métier pris après cette date sont annulés (clients prévenus). »
6. Carte « Mon local » (carte commune des adresses) : vide « Pas de local : ajoutez son adresse si des clients viennent chez vous (salon, atelier…). » + [Ajouter l'adresse de mon local] ; enregistrée : l'adresse sur 2 ou 3 lignes, « Pour vos annonces « chez moi ». Les clients voient seulement la ville ; la rue, après avoir réservé. », [Modifier], [Effacer l'adresse] (danger) — refus affiché dans la carte : « Des annonces en ligne ont lieu chez vous : mettez-les en pause ou changez leur lieu d'abord. » ; formulaire comme « Mon adresse » (RM-COMPTE-IHM).
7. Carte « Visibilité » (absente si arrêté) : « Vous apparaissez dans les recherches tant que votre activité est active et qu'une annonce est en ligne. » ; boutons [Mettre en pause] (secondaire) ou [Reprendre mon activité] (principal), et [Arrêter mon activité…] (danger) → fenêtre « Arrêter votre activité ? » (« C'est définitif… Pour une absence, choisissez plutôt « Mettre en pause ». ») : [Arrêter définitivement] / [Annuler]. Bloqué : les deux boutons sont verrouillés 🔒 avec la raison dans la bulle.

## Carte « Paiement par carte » (lot 5.2, 02/10/2026 ; maquette `maquette-lot-5.2-paiements.html`)
Fichier : `frontend/src/components/prestataire/CartePaiementCarte.vue`, placée après « Mes annonces » (absente si arrêté). Règles : `RM-PAIEMENTS.md`. Badge à droite du titre selon l'état :
- **Carte pas encore ouverte sur rafals** (pas de clés Stripe) : « Le paiement par carte arrivera bientôt sur rafals. » (pas de badge).
- **Sans SIRET vérifié** (badge gris « espèces seulement ») : « Payé par carte, l'argent arrive sur votre compte en banque 48 h après chaque rendez-vous. » + 🔒 [Activer le paiement par carte] : « Il faut d'abord un SIRET vérifié par l'État : ajoutez-le avec [Modifier mon profil]. »
- **À activer** (badge gris « pas activé ») : explication (paiement en réservant sur la page de Stripe, argent bloqué jusqu'au rendez-vous, versé 48 h après) ; « Exemple : Coupe à 50 € : rafals garde 2,50 € (5 %), Stripe 1,00 € de frais, vous recevez **46,50 €**. » ; « Remboursements : si vous refusez, annulez ou êtes absent… les frais de Stripe restent à votre charge. » ; case « J'accepte que rafals fasse mes factures à ma place, à mon nom (mandat de facturation). * » (seulement la première fois) ; erreur du serveur au-dessus du bouton (ex. « Cochez la case : vous acceptez que rafals fasse vos factures à votre place. ») ; [Activer le paiement par carte] → la page de Stripe (identité, RIB).
- **En vérification** (badge orange « vérification par Stripe ») : bandeau orange « Stripe vérifie vos informations : cela prend de quelques minutes à 2 jours. Vos annonces proposent les espèces en attendant. » ; [Continuer chez Stripe] [Actualiser] → « Paiement par carte activé. » ou « Toujours en cours de vérification par Stripe. »
- **Activé** (badge vert « activé ») : « Vos annonces qui acceptent la carte la proposent aux clients. » + « Mandat de facturation accepté le 02/10/2026. Vos paiements : « Mon agenda › Paiements ». »
- Retour de la page de Stripe (`?stripe=retour`) : « Merci : Stripe vérifie vos informations. » (si pas encore activé), puis l'adresse redevient `/proposer`.

## Carte « TVA » (lot 5.4, 03/10/2026 ; maquette `maquette-lot-5.4-devis.html`)
Fichier : `frontend/src/components/prestataire/CarteTva.vue`, après « Paiement par carte ». Case « Je facture la TVA » (enregistrée au clic) → « Vos prochains devis indiqueront la TVA. » / « Vos prochains devis seront sans TVA (mention 293 B). » ; « Non coché : … « TVA non applicable, art. 293 B du CGI » (auto-entrepreneur en franchise). Coché : un taux par ligne (5,5 %, 10 % ou 20 %) et les totaux HT, TVA, TTC. Vaut pour vos prochains devis. »

## Liens vers le guide « Créer mon auto-entreprise » (lot 6.2, 03/10/2026)
Sans profil, sous le formulaire : « Pas encore d'entreprise ? [Créer mon auto-entreprise] ». Dans « Mon activité », carte « Paiement par carte » sans SIRET vérifié : [Pas de SIRET ? Créer mon auto-entreprise : le guide]. Voir `RM-CREATION-AUTO-ENTREPRISE-IHM.md`.

## SIRET déjà rempli (lot 7.2, 04/10/2026)
Quand on arrive de « Créer mon auto-entreprise » (carte « Vous avez déjà une entreprise ? » sans profil, ou dossier accepté sans profil), le champ « SIRET (facultatif) » est déjà rempli (adresse `/proposer?siret=91234567800017`). Les boutons vers la création d'entreprise s'appellent maintenant [Créer mon auto-entreprise] (plus « : le guide »), car rafals fait la démarche.
