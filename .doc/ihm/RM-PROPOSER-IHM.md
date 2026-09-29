# Proposer mes services / Mon activité — Interface

> Fichiers : `frontend/src/pages/ProposerPage.vue`, `frontend/src/components/prestataire/FormulaireProfil.vue`, `FicheActivite.vue`, `frontend/src/components/AppChoixCommune.vue`, `frontend/src/outils/prestataires.ts`. Construit au lot 2.5 (29/09/2026). Règles : `RM-PRESTATAIRES.md`. Maquette : `maquette-lot-2.5-prestataire.html`.

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
4. Carte « Visibilité » (absente si arrêté) : « Vous apparaîtrez dans les recherches dès que vous publierez une annonce (bientôt disponible). » ; boutons [Mettre en pause] (secondaire) ou [Reprendre mon activité] (principal), et [Arrêter mon activité…] (danger) → fenêtre « Arrêter votre activité ? » (« C'est définitif… Pour une absence, choisissez plutôt « Mettre en pause ». ») : [Arrêter définitivement] / [Annuler]. Bloqué : les deux boutons sont verrouillés 🔒 avec la raison dans la bulle.
