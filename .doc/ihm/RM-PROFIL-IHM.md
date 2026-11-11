# Mon profil — Interface

## Depuis le 10/11/2026 : identique à la grande maquette (lots 14.5 et 14.6)

Demande de Raphael, mot pour mot : « je veux que ca soit exactement pareil que la maquette et tu fais l'agenda pareil que la maquette ». Maquette : `.doc/ihm/maquette-site-complet.html`. Les styles de la maquette sont recopiés dans `frontend/src/style.css` ; les sections plus bas décrivent le fonctionnement, qui ne change pas sauf mention ici.

- Carte « insta » de la maquette : photo de 96 px (ou les initiales), 4 chiffres à côté, nom + pastilles (actif, SIRET vérifié), métier en gras « · aussi … », présentation, lieu, SIRET ; [Modifier mon profil] [Changer ma photo] [Mon activité] ; les métiers en bulles rondes (le principal entouré de vert) + [+ Ajouter] ; onglets Photos · Mon activité · Mon compte (trait noir en haut).
- Les lignes qui se déplient sont des cartes séparées (rond coloré avec l'icône de la maquette, titre, résumé, ›) ; « Notifications sur cet appareil » a un interrupteur.
- Sous la carte : « Voir ma page publique › ».
- **« Mes métiers »** (11/11/2026, prix de l'heure) : une ligne par métier, « Électricien [principal] · 45 € de l'heure » (ou « Pas de prix de l'heure »), [Prix…] et [Arrêter ce métier…] ; [Prix…] ouvre « Prix de l'heure — Électricien » : « Votre prix de l'heure (€) », [Enregistrer], [Effacer le prix], [Annuler]. La fenêtre « Ajouter un métier » demande aussi « Votre prix de l'heure (€), facultatif ».


> **Changé le 21/10/2026 : présentation façon Instagram.** Demande de Raphael, mot pour mot : « la rubrique mon profil est moche essaye de faire un truc du style instagrame ». Maquette validée (« comme la maquette ») : https://claude.ai/artifact/VvWuWo8jwdMoCyTfsJhUr7 (`.doc/ihm/maquette-profil-instagram.html`). **Les onglets remplacent la règle du 07/10/2026 « l'un sous l'autre (pas d'onglets) »** (choix de Raphael du 21/10/2026). Rien n'a disparu : chaque carte est rangée dans un onglet. Largeur 640 px au plus. Fichiers : `ProfilPage.vue`, `prestataire/FicheActivite.vue`, `prestataire/CartePhotosTravail.vue`, `profil/EnteteProfil.vue`, `profil/LignesCompte.vue`, `ui/AppListeLignes.vue`, `ui/AppSection.vue`, `ui/AppOnglets.vue` (variante `egaux`), `outils/profil.ts`.
>
> **Prestataire** (ex. Karim Benali), une seule grande carte, de haut en bas :
> 1. Sa photo ronde (ou « KB »), **sans anneau coloré ni « + »** (Raphael : « enleve les 2 »). À côté, 4 chiffres : « 8 photos », « 4,8 ★ / 23 avis », « 12 abonnés » (ceux qui le suivent), « 4 abonnements » (les prestataires qu'il suit lui-même, demande de Raphael : « le nombre de personnes a qui il s'est lui meme abonné »). Un chiffre pas lisible (ex. profil en pause : sa page publique est fermée) s'écrit « — ».
> 2. Le nom, les badges « actif » et « SIRET vérifié », « **Plombier** · aussi Chauffagiste », la présentation, « 📍 Pessac (33600) · jusqu'à 20 km », le numéro de SIRET.
> 3. [Modifier mon profil] (principal, ouvre le formulaire), [Changer ma photo], [Mon activité] (→ `/mon-activite`).
> 4. Les métiers en **bulles rondes** (initiale du métier ; le principal entouré de vert, « principal » dessous) Un clic sur un métier ouvre l'onglet « Mon activité » sur la ligne « Mes métiers ». La bulle « + Ajouter » ouvre la fenêtre **« Ajouter un métier »** (demande de Raphael du 21/10/2026 : « quand je clic sur ajouter un metier ca m'enmène en bas alors que je veux que ca fasse comme si j'ajoute un métier ») : champ « Métier à ajouter » (propositions dès la 1re lettre, sans le principal ni les secondaires déjà là), puis [Ajouter Chauffagiste] / [Annuler] → message « Chauffagiste ajouté à vos métiers. ». Avec 5 métiers secondaires : « Vous avez déjà 5 métiers secondaires : c'est le maximum. Arrêtez-en un d'abord (ligne « Mes métiers »). » Fichier : `prestataire/FenetreAjoutMetier.vue`.
> 5. 3 onglets à dessins, de même largeur : **Photos** · **Mon activité** · **Mon compte** (adresse `?onglet=activite`, `?onglet=compte`). Activité arrêtée : seulement « Mon compte ».
> 6. **Photos** : grille carrée de 3 colonnes ; les 2 premières portent « Sur ma carte » ; dernière case « + Ajouter une photo » (tant qu'il y en a moins de 10). Un clic sur une photo l'ouvre en grand : [Retirer cette photo] / [Fermer]. Dessous : « 8 photos sur 10 (JPG ou PNG, 5 Mo chacune). Les 2 premières sont sur votre carte dans « Trouver un prestataire ». »
> 7. **Mon activité** : « Sans SIRET : vos limites » (seulement sans SIRET vérifié), « Paiement par carte », « Mes métiers », « Visibilité ».
> 8. **Mon compte** : « Mes informations », « Accord de tes parents » (16-17 ans), « Mon adresse », « Absences » (s'il y en a), « Notifications sur cet appareil », « Mes paiements par carte » (s'il y en a), « Mes données », « Fermer mon compte » (titre en rouge).
>
> **Chaque carte est une ligne** : picto sur une pastille de couleur, titre, petit résumé (ex. « karim@example.com · 06 12 34 56 78 », « Plombier (principal) · Chauffagiste », « Actif : vous apparaissez dans les recherches »), « › ». Un clic la déplie sur place avec exactement le contenu et les boutons d'avant ; un 2ᵉ clic la replie. Le badge d'une carte (ex. « Activé » de « Paiement par carte ») reste visible à droite de la ligne fermée.
>
> **Client** (ex. Julie Martin) : ses initiales « JM », 3 chiffres « 5 rendez-vous » (confirmés, passés ou à venir), « 3 avis donnés », « 4 abonnements » ; son nom, son adresse mail ; [Modifier mes informations] (ouvre la ligne « Mes informations ») ; le bloc « Proposer mes services » sur fond dégradé orange-vert (mêmes textes et mêmes bandeaux qu'avant) ; le titre « MON COMPTE » puis les mêmes lignes que l'onglet « Mon compte ».
>
> Décisions prises seul, à confirmer : pas de [Changer ma photo] pour un client (un client n'a pas de photo dans rafals aujourd'hui : ce serait une fonction nouvelle) ; les bulles montrent l'initiale du métier (un métier n'a pas de dessin à lui) ; « Mon profil » n'est plus écrit en titre (c'est le nom, comme sur Instagram).

> **Changé le 17/10/2026** (agenda simplifié) : dans la carte « **Mes métiers** », chaque métier exercé a un bouton danger **[Arrêter ce métier…]** ; il ouvre la fenêtre « Date d'arrêt — Coiffeuse » (avant : dans « Mon agenda ») avec un champ « Dernier jour de travail * » (aujourd'hui au départ), le texte « À partir du …, tous les jours du calendrier « Coiffeuse » sont fermés. Les rendez-vous de ce métier pris après cette date sont annulés : chaque client est prévenu par mail. », le choix du métier qui deviendra principal, puis [Arrêter Coiffeuse après le 31/10/2026] (danger) / [Annuler]. Un métier qui a déjà une date d'arrêt montre **[Retirer la date d'arrêt]** → « Date d'arrêt retirée : Coiffeuse continue. ». Phrase du bas : « Arrêter un métier : [Arrêter ce métier…], puis choisir son dernier jour. »

> Fichier : `frontend/src/pages/ProfilPage.vue`. Créé le 07/10/2026. Le détail de chaque carte reste dans `RM-PROPOSER-IHM.md` (cartes du prestataire) et `RM-COMPTE-IHM.md` (cartes du compte).

## D'où vient cette page
Demande de Raphael du 07/10/2026, mot pour mot : « on vas fusioner mon compte et mon profil pour que y'ai plus mon compte mais que du coup il reste mon profil mais qu'il soit a l'emplacement actuel de mon compte », puis « tout d'un coup mais ce ne sera pas un nouvel onglet c'est juste mon profil qui existe deja et mon compte qui existe deja qui vont fusionner et faire 1 qui s'appel mon profil qui sera au meme endroit que mon compte ».

- La page « Mon compte » n'existe plus. La page « Mon profil » contient tout, **sur une seule page, l'un sous l'autre** (pas d'onglets).
- Elle s'ouvre par **le rond avec les initiales**, en haut à droite, là où était « Mon compte » ; sur téléphone, par ☰. « Mon profil » n'est plus dans le menu principal.
- Adresse : `/profil`. Les anciennes adresses `/compte` et `/proposer` y mènent, avec leurs réglages (ex. `/proposer?siret=91234567800017`, retour de Stripe `?stripe=…`).

## Ce qu'on voit, de haut en bas (largeur 720 px au plus)

**Pas connecté** : carte « Mon profil », « Connectez-vous pour voir votre profil ou proposer vos services. », [Se connecter], [Créer mon compte].

**Prestataire** (ex. Karim Benali, plombier) :
1. Titre « Mon profil ».
2. Sa fiche de prestataire et ses cartes, comme avant (`RM-PROPOSER-IHM.md`) : fiche (photo, métier, zone, SIRET, présentation), « Photos de mon travail », « Paiement par carte », « Mes métiers », « Visibilité » (la carte « Mon local » a disparu, voir plus bas ; la carte « TVA » aussi, le 17/10/2026 : la TVA s'active toute seule par la barre de « Mon activité »). [Modifier mon profil] remplace la fiche par le formulaire.
3. Les cartes du compte, comme avant (`RM-COMPTE-IHM.md`) : « Mes informations », « Accord de tes parents » (16-17 ans), « Mon adresse », les absences (s'il y en a), **« Notifications sur cet appareil »** (lot 8.7 ; même carte que dans « Paramètres › Notifications », voir `RM-ALERTES-IHM.md` § « Sur ce téléphone » ; exemple « Une notification quand on vous écrit ou qu'on vous fait une proposition, ex. « Karim vous a écrit ». »), « Mes paiements par carte » (s'il y en a), « Mes données », « Fermer mon compte » tout en bas.

**Client qui n'est pas prestataire** (ex. Julie Martin) :
1. Titre « Mon profil ».
2. Carte « Proposer mes services » : la phrase « Vous faites du ménage, du jardinage, de la plomberie… ? Créez votre profil de prestataire. » et le bouton [Proposer mes services], qui déplie le formulaire sur place. Le formulaire est déjà déplié quand on arrive par l'entrée « Proposer mes services » du menu (`/profil?proposer=1`) ou de « Créer mon auto-entreprise » (`/profil?siret=…`). Adresse mail pas vérifiée, ou accord des parents manquant : un bandeau orange à la place du bouton.
3. Les cartes du compte (les mêmes que ci-dessus).

## Carte « Sans SIRET : vos limites » (ajoutée le 12/10/2026, lot 11.2)
Fichier : `frontend/src/components/prestataire/CarteParticulier.vue`, placée dans la fiche de l'activité juste avant « Photos de mon travail ». **Affichée seulement si le SIRET n'est pas vérifié** ; elle disparaît dès qu'il l'est. Règles : `RM-PRESTATAIRES.md` § « Limites d'un prestataire sans SIRET ».
De haut en bas :
1. Badge orange « Particulier, non professionnel ».
2. « Sans SIRET vérifié, vous rendez de petits services, payés en espèces. Vos clients lisent cette étiquette sur votre profil et sur vos propositions, avec l'avertissement « Pas de facture, pas de garantie, pas d'assurance professionnelle. » »
3. Quatre lignes : « Seulement les métiers autorisés sans SIRET (ex. promener un chien, repasser, tondre une pelouse). » · « **100,00 €** au plus par proposition. » · « **1 sur 2** rendez-vous ce mois-ci. » · « **230,00 € sur 1 000,00 €** de rendez-vous sur les 12 derniers mois. »
4. Plafond atteint : bandeau rouge « Vous avez atteint la limite des particuliers : vous ne pouvez plus répondre aux demandes tant que vous n'avez pas de SIRET. »
5. La case « Mon activité est occasionnelle et je déclare mes revenus aux impôts. » et le bouton [Enregistrer ma déclaration] (verrouillé 🔒 tant que la case n'est pas cochée : « Cochez d'abord la case… ») → message « C'est noté : vous pouvez répondre aux demandes. » Une fois faite : « ✓ « Mon activité est occasionnelle… » : déclaré le 12/10/2026. », sans case ni bouton.
6. Sans adresse : bandeau orange « Indiquez aussi votre adresse, plus bas : elle n'est pas montrée au public, mais rafals doit la connaître. »
7. « Avec un SIRET vérifié, aucune de ces limites : tous les métiers, tous les prix, la carte bancaire et les devis. » et le bouton secondaire [Créer mon auto-entreprise] → `/creer-mon-auto-entreprise`.

## Une seule adresse : « Mon adresse » (07/10/2026)
Demande de Raphael, mot pour mot : « mon local et mon adress c la meme chose donc compress les pour que ca fasse que 1 fin juste pour le titre met mon adresse ».
- La carte « Mon local » n'existe plus. Il reste une seule carte **« Mon adresse »**, à sa place habituelle parmi les cartes du compte.
- Pour un prestataire, sous l'adresse enregistrée : « C'est aussi l'adresse de votre local. Les clients voient seulement la ville ; la rue, après avoir réservé. » ; sans adresse : « Aucune adresse enregistrée : ajoutez-la si des clients viennent chez vous (salon, atelier…) ou pour réserver un service à domicile. »
- [Effacer mon adresse] est refusé à un prestataire tant qu'une annonce en ligne a lieu chez lui : « Des annonces en ligne ont lieu chez vous : mettez-les en pause ou changez leur lieu d'abord. »
- Règle : `RM-PRESTATAIRES.md` § « Une seule adresse ».

## Décisions prises par Claude, à confirmer
- Ordre pour un prestataire : la fiche d'abord, le compte ensuite (c'est l'ordre décrit dans la question à laquelle Raphael a répondu « tout d'un coup »).
- Pour qui n'est pas prestataire, l'entrée « Proposer mes services » reste dans le menu principal (sinon plus rien n'invite à devenir prestataire) ; elle disparaît dès que le profil est créé.
- Pas de titre « Mon compte » au milieu de la page : la carte « Mes informations » ouvre la partie compte.
