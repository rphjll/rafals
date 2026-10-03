# Proposer mes services / Mon activité — Interface

> Fichiers : `frontend/src/pages/ProposerPage.vue`, `frontend/src/components/prestataire/FormulaireProfil.vue`, `FicheActivite.vue`, `CarteMesAnnonces.vue`, `CarteMetiers.vue`, `frontend/src/components/CarteAdresse.vue` (local), `frontend/src/components/AppChoixCommune.vue`, `frontend/src/outils/prestataires.ts`. Construit au lot 2.5 (29/09/2026), complété au lot 3.2 (29/09/2026). Règles : `RM-PRESTATAIRES.md`, `RM-ANNONCES.md`. Maquettes : `maquette-lot-2.5-prestataire.html`, `maquette-lot-3.2-annonces.html`.

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
4. (absentes si arrêté, lot 3.2) Carte « Mes annonces » : « 3 en ligne sur 20 » à droite du titre ; « Vous apparaissez dans les recherches grâce à vos annonces en ligne. » (ou, sans annonce en ligne, « Aucune annonce en ligne : écrivez-en une pour que les clients vous trouvent. ») ; [Voir mes annonces] (s'il en a) → `/mes-annonces`, [Écrire une annonce] → `/mes-annonces/nouvelle`.
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
