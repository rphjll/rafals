# Mon profil — Interface

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
2. Sa fiche de prestataire et ses cartes, comme avant (`RM-PROPOSER-IHM.md`) : fiche (photo, métier, zone, SIRET, présentation), « Photos de mon travail », « Paiement par carte », « TVA », « Mes métiers », « Visibilité » (la carte « Mon local » a disparu, voir plus bas). [Modifier mon profil] remplace la fiche par le formulaire.
3. Les cartes du compte, comme avant (`RM-COMPTE-IHM.md`) : « Mes informations », « Accord de tes parents » (16-17 ans), « Mon adresse », les absences (s'il y en a), **« Notifications sur cet appareil »** (lot 8.7 ; même carte que dans « Alertes », voir `RM-ALERTES-IHM.md` § « Sur ce téléphone » ; exemple « Une notification quand on vous écrit ou qu'on vous fait une proposition, ex. « Karim vous a écrit ». »), « Mes paiements par carte » (s'il y en a), « Mes données », « Fermer mon compte » tout en bas.

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
