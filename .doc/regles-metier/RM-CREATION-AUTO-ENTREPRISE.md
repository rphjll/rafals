# Aide à la création d'auto-entreprise — Règles métier (sujet 14)

> Rédigé au lot 6.0 le 03/10/2026, **pendant l'absence de Raphael**. Tout ce qui est marqué 🟡 est un choix **proposé par Claude, à valider**. ⚠️ Les informations sur les démarches officielles sont à faire relire par un professionnel avant la mise en ligne.

## À quoi ça sert
Karim veut devenir plombier indépendant mais n'a pas encore d'entreprise. rafals lui explique, étape par étape et avec des mots simples, comment créer son auto-entreprise (le nom officiel est « micro-entreprise »), jusqu'à recevoir son SIRET.
- Exemple : Karim suit les 5 étapes, reçoit son SIRET 2 semaines plus tard, et l'ajoute à son profil : la carte bancaire et les devis deviennent possibles.
- Exemple : Julie, déjà sur rafals sans SIRET (espèces seulement), ouvre le guide depuis « Mon activité ».

## rafals guide, il ne fait pas la démarche 🟡 (REMPLACÉ le 04/10/2026 : voir « rafals fait la démarche » en bas ; le guide reste comme second choix)
rafals **n'envoie rien à l'administration** à la place de la personne : la déclaration se fait sur le site officiel de l'État (le « guichet unique »), gratuit. rafals donne les explications, la liste des papiers, et les liens. Pourquoi : faire la démarche à sa place demanderait un mandat et engagerait la responsabilité de rafals.
- Exemple : à l'étape 3, un bouton ouvre le site officiel dans un nouvel onglet.
- Exemple : rafals ne demande jamais le numéro de sécurité sociale ni la pièce d'identité.

## Qui voit le guide 🟡
Tout le monde, même sans compte (cela fait connaître rafals aux futurs prestataires). Adresse : `/creer-mon-auto-entreprise`. Un lien y mène depuis « Proposer mes services » et, pour un prestataire sans SIRET, depuis « Mon activité ».

## Les 5 étapes 🟡
1. **Est-ce pour moi ?** — avoir 18 ans (ou être mineur émancipé ; à 16-17 ans, c'est possible seulement avec l'accord des parents et sous conditions) ; certains métiers demandent un diplôme ou une assurance (ex. coiffeur, électricien, maçon).
2. **Je prépare mes papiers** — pièce d'identité, justificatif de domicile, et selon le métier : diplôme ou preuve de 3 ans d'expérience.
3. **Je déclare mon activité** — sur le guichet unique de l'État (formalites.entreprises.gouv.fr), gratuit, environ 30 minutes ; choisir « micro-entrepreneur ».
4. **J'attends mon SIRET** — l'INSEE l'envoie par courrier ou par mail, en 1 à 4 semaines ; pendant ce temps, on peut déjà travailler sur rafals en espèces.
5. **Je termine sur rafals** — ajouter le SIRET dans « Mon activité » (vérifié tout seul), créer son espace sur le site de l'URSSAF pour déclarer son chiffre d'affaires, puis activer le paiement par carte.
- Exemple : Karim, plombier, voit à l'étape 1 : « Plombier est un métier réglementé : il faut un diplôme (CAP…) ou 3 ans d'expérience. »
- Exemple : Julie, ménage à domicile : aucun diplôme demandé.

## Où j'en suis 🟡
Chaque étape a une case « C'est fait ». L'avancement est gardé **dans le navigateur de la personne** (rien n'est enregistré sur rafals : aucune donnée personnelle en plus, et le guide marche sans compte).
- Exemple : Karim coche les étapes 1 et 2 lundi ; mardi, sur le même ordinateur, il retrouve « 2 étapes sur 5 ».
- Exemple : sur un autre téléphone, il repart de zéro.

## Ce que rafals ne fait pas
- Pas de conseil sur le choix du statut (micro-entreprise, société…) : le guide le dit et renvoie vers les organismes gratuits (CCI, chambre des métiers).
- Pas de création de société (SARL, SAS).

## Questions pour Raphael
1. L'avancement gardé dans le navigateur te convient-il, ou veux-tu qu'il soit enregistré dans le compte (il faudra alors une rubrique de plus dans la base) ?
2. Le guide ouvert à tous, même sans compte : d'accord ?

## rafals fait la démarche (04/10/2026 ; demande de Raphael : « dans mon site y'ai la possiblilité de créé une auto entreprise direct dedans avec une api » ; maquette `maquette-lot-7.2-creation-auto-entreprise.html` validée : « oui je valide »)
rafals remplit et envoie le dossier de création au guichet officiel de l'État (API de l'INPI, détail dans `technique/API-EXTERNES.md`). La personne ne quitte pas rafals.
- Exemple : Karim répond aux 5 étapes le 04/10, clique [Envoyer mon dossier] ; le 20/10 il reçoit « Votre auto-entreprise est créée », son SIRET est ajouté à son profil.
- Exemple : Julie préfère le faire seule → [Je préfère le faire moi-même] ouvre le guide en 5 étapes, inchangé.

### Déjà une entreprise : on n'en recrée pas (demande de Raphael, mot pour mot : « une option si la personne a deja une entreprise ou mini entreprise pour pas en recréé une si il en a deja une il peut la mettre direct »)
- La page de départ propose deux chemins : [Commencer] (créer) et « Vous avez déjà une entreprise ? » avec la saisie du SIRET (même vérification que dans « Mon activité », lot 2.4).
  - Exemple : Paul a déjà son auto-entreprise → il écrit « 912 345 678 00012 », rafals le vérifie et l'ajoute à son profil ; aucun dossier n'est créé.
  - Exemple : Léa a une société (SARL) → même chose, le SIRET de la société.
- Un compte dont le profil a déjà un SIRET ne peut pas commencer de dossier : « Vous avez déjà une entreprise (SIRET …) : il n'y a rien à créer. » Le serveur refuse aussi.
- À l'étape 2, « Avez-vous déjà été à votre compte ? Oui » demande l'ancien SIREN ; si cette entreprise existe encore (répertoire des SIRET), le dossier s'arrête : « Ne la recréez pas : ajoutez son SIRET à votre profil. »

### Qui peut commencer
Il faut être connecté (le dossier est gardé dans le compte). Un seul dossier ouvert par compte. Moins de 18 ans : l'autorisation des parents est demandée en plus.

### Les 5 étapes
1. **Vous** : civilité, nom de naissance, nom d'usage, prénoms, date et lieu de naissance, nationalité, situation de famille, numéro de sécurité sociale, adresse, mail, téléphone.
2. **Votre activité** : métier (liste de rafals), description (10 à 250 caractères), date de début (d'aujourd'hui à dans 1 mois), lieu de travail, nom commercial, activité en même temps, déjà été à son compte.
3. **Vos choix** : URSSAF chaque trimestre (conseillé) ou chaque mois ; impôt payé avec les cotisations ou non ; ACRE ; adresse non publique. TVA et régime « micro » sont imposés.
4. **Vos papiers** : pièce d'identité avec la mention manuscrite ; diplôme pour un métier réglementé ; attestation sur l'honneur écrite par rafals (avec les noms des parents) ; titre de séjour, autorisation des parents ou bail selon le cas.
5. **Vérifier et envoyer** : deux cases (« je certifie », « je donne pouvoir à rafals ») puis [Envoyer mon dossier]. Après l'envoi, plus rien ne se modifie sauf demande de l'administration.

### Cas renvoyés vers le site de l'État
Le conjoint qui travaille dans l'entreprise ; l'agriculture ; les professions libérales réglementées (avocat, médecin…).

### Suivi
États : brouillon → envoyé → en cours d'examen → (à corriger) → accepté / refusé / fermé. rafals interroge le guichet toutes les heures. Un mail à chaque changement.
- Exemple : « La pièce d'identité est illisible », à corriger avant le 19/10/2026 → Karim dépose une nouvelle copie ; rappel 3 jours avant la limite.
- Exemple : accepté → le SIRET reçu est ajouté au profil (ou gardé dans le dossier si le profil n'existe pas encore).

### Données sensibles
Le numéro de sécurité sociale et les papiers sont effacés dès que le dossier est accepté, refusé ou fermé, et un brouillon abandonné depuis 30 jours est effacé aussi. Le reste du dossier (dates, état, SIRET) est gardé. ⚠️ À faire relire avant la mise en ligne (RGPD).

### Avant la mise en ligne (à la charge de Raphael, rien avant)
Compte INPI au nom de l'entreprise rafals ; vérification des frais et des textes par un professionnel.
