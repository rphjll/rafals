# rafals — API extérieures étudiées (pour les services du niveau 6)

> Recherches faites par Claude le 04/10/2026 à la demande de Raphael. Rien n'est construit. Les points marqués ❓ ne sont pas encore vérifiés.

## 1. Déclarer à l'URSSAF depuis rafals : « API Tierce Déclaration auto-entrepreneur »
Demande de Raphael, mot pour mot : « avoir une api qui se connecte a l'ursaf direct comme ca y'a pas besoin d'aller sur le site de l'ursaf pour declarer […] ils clicent sur un bonton et ca l'envoie a l'urasaf ».
- **Elle existe**, proposée par l'URSSAF aux plateformes où des auto-entrepreneurs vendent leurs services.
- Elle permet : enregistrer l'accord du prestataire (un « mandat »), estimer ses cotisations, déclarer son chiffre d'affaires à sa place. Le prestataire peut toujours corriger sur son compte URSSAF.
- Pour y accéder : présenter le projet et s'inscrire sur https://portailapi.urssaf.fr/fr/ (le portail ne répondait pas le 04/10/2026).
- **04/10/2026, second essai** : le portail de l'URSSAF (portailapi.urssaf.fr) et la page d'information ne répondent toujours pas ; la documentation technique n'est pas publique (« API REST gratuite, à accès restreint », contact : contact-api@urssaf.fr). Ce que la fiche officielle (data.gouv.fr) confirme : notifier le mandat, savoir si la personne peut être déclarée par un tiers et connaître sa périodicité, annuler le mandat, estimer les cotisations, déclarer le chiffre d'affaires (l'URSSAF renvoie les montants dus), lancer un paiement par prélèvement SEPA. **Les noms exacts des appels et des champs ne sont pas connus** : rafals se construit avec un faux URSSAF et un seul fichier à adapter (`services/urssaf.py`) le jour où la documentation est obtenue.
- ❓ À vérifier : faut-il que rafals soit une entreprise (très probable) ; délais ; espace d'essai ; le paiement des cotisations passe-t-il par l'API.
- Sources : https://www.data.gouv.fr/dataservices/api-tierce-declaration-auto-entrepreneur · https://www.autoentrepreneur.urssaf.fr/portail/accueil/informations-tierce-declaration.html

## 2. Créer une auto-entreprise depuis rafals : « API mandataire de dépôt » du guichet unique (INPI)
Demande de Raphael, mot pour mot : « dans mon site y'ai la possiblilité de créé une auto entreprise direct dedans avec une api si possible ».
- **Elle existe.** Contrat technique lu en entier : « Contrat d'interface — Spécifications de l'API mandataire de dépôt de formalités sur le guichet unique » (INPI, juin 2026, 52 pages), https://www.inpi.fr/inpi-block/download-document?id=1927 ; page d'accès : https://www.inpi.fr/ressources/formalites-dentreprises/acces-aux-api-guichet-unique
- **Accès** : il suffit d'un compte sur le portail e-procedures de l'INPI, et d'accepter une fois ses conditions d'utilisation sur le site. Aucun agrément n'est demandé dans le contrat.
- **Un espace d'essai existe** (« démonstration »), avec ses propres comptes : https://procedures-demo.inpi.fr et https://guichet-unique-demo.inpi.fr/api — on peut tout tester sans créer de vraie entreprise.
- **Ce que l'API fait** : déposer une création (`POST /api/formalities`), la corriger avant signature, joindre les pièces (fichiers envoyés dans la demande), signer, payer s'il y a des frais, suivre l'état du dossier, répondre aux demandes de régularisation (« il manque une pièce »).
- **Signature** : pour une **création**, une signature simple par l'API suffit (`POST /api/signatures`) ; pas de certificat. (Modification et cessation demandent un certificat qualifié : hors sujet.)
- **Contenu du dossier** : l'identité de la personne, l'adresse de l'entreprise, les options fiscales, l'établissement ; pièces justificatives (ex. la pièce d'identité). La liste exacte des rubriques est dans le « dictionnaire de données » de l'INPI (pas encore lu).
- **Paiement** : s'il y a des frais, ils se paient par un « compte client INPI » alimenté d'avance par le mandataire.
- ❓ À vérifier avant de construire : (1) le mandat que la personne doit donner à rafals et sous quelle forme (le contrat technique n'en parle pas) ; (2) si rafals doit être une entreprise pour déposer pour d'autres ; (3) les frais selon le métier (commerçant, artisan, libéral) ; (4) les rubriques exactes (dictionnaire de données) ; (5) la protection des données sensibles (pièce d'identité, numéro de sécurité sociale).
- **Conséquence sur les règles** : `RM-CREATION-AUTO-ENTREPRISE.md` dit aujourd'hui « rafals guide, il ne fait pas la démarche » et « ne demande jamais la pièce d'identité ». Si on construit ceci, ces deux règles changent.

### Dictionnaire de données de l'INPI, lu le 04/10/2026 (85 classes, 1 646 rubriques)
Ce qu'un dossier de création d'auto-entreprise doit contenir (noms exacts de l'API entre parenthèses) :
- **Enveloppe** (`Formality`) : `typeFormalite` « C » (création), `typePersonne` « P » (personne physique), `diffusionINSEE` et `diffusionCommerciale` (« O » / « N »), `referenceMandataire` (notre numéro de dossier), `content`.
- **Nature** (`BlocNatureCreation`) : `dateCreation`, `microEntreprise` = vrai, `etablieEnFrance`.
- **La personne** (`PPEntrepreneur` › `descriptionEntrepreneur`) : `genre` (1 M, 2 F), `nom`, `nomUsage`, `prenoms` (liste), `dateDeNaissance`, `codeInseeGeographique` (commune ou pays de naissance), `codeNationalite`, `situationMatrimoniale` (1 célibataire, 2 divorcé, 3 veuf, 4 marié, 5 pacsé, 6 concubinage), `numeroSecu`, `formeSociale` = 2 ; `adresseDomicile` ; `contact` (mail, téléphone) ; `roleConjoint` si marié ou pacsé.
- **Social** : `regimeMicroSocial` (`optionMicroSocial` = vrai, `periodiciteVersement` « M » ou « T ») ; `voletSocial` (`activiteSimultanee` et son statut : salarié, retraité… ; `indicateurActiviteAnterieure` et `ancienNumeroSiren` ; `demandeAcre` ; `organismeAssuranceMaladieActuelle`).
- **Fiscal** (`BlocOptionFiscale`) : `regimeImpositionBenefices` (116 « Micro BIC » ou 110 « Régime spécial BNC »), `regimeImpositionTVA` = 310 « Franchise en base TVA », `optionVersementLiberatoire` (oui / non).
- **Adresse de l'entreprise** : `indicateurDomicileEntrepreneur`, `ambulant`, `domiciliataire`.
- **Établissement principal** : adresse, `effectifSalarie`, `nomCommercial`, et l'activité (`BlocDescriptionActivite`) : `formeExercice` (COMMERCIALE, ARTISANALE, ARTISANALE_REGLEMENTEE, INDEPENDANTE…), `categorisationActivite1` à `4` (liste fournie par `/api/data_dictionary/category_activities`), `descriptionDetaillee`, `dateDebut`, `exerciceActivite` (« P » permanente), `indicateurNonSedentaire`, `origine` (`typeOrigine` 1 = création), et pour un métier artisanal réglementé la qualification (`optionJQPA`).
- **Pièces jointes** (`BlocPieceJointe`, **PDF uniquement**, envoyées en base64) : `PJ_11` carte d'identité ou `PJ_12` passeport (avec la mention manuscrite « conforme à l'original », datée et signée) ; `PJ_14` / `PJ_15` titre de séjour ; `PJ_17` / `PJ_63` attestation sur l'honneur de non-condamnation (avec les noms des parents) ; `PJ_31` diplôme d'un métier réglementé ; `PJ_226` autorisation du mineur ; **`PJ_51` « Eventuel pouvoir si mandataire » : obligatoire pour nous** (« si vous êtes un mandataire, vous devez obligatoirement attacher un justificatif (procuration) »).
- **États du dossier** (`status`) : RECEIVED, SIGNATURE_PENDING, SIGNED, PAYMENT_PENDING, PAID, VALIDATION_PENDING, **AMENDMENT_PENDING** (correction demandée), **VALIDATED**, **REJECTED**, EXPIRED, ERROR. Les motifs de refus de l'URSSAF, des greffes et des chambres de métiers sont listés dans le dictionnaire.

Réponses aux questions restées ouvertes :
1. **Le mandat** : un pouvoir signé par la personne, joint au dossier en `PJ_51`. rafals l'écrit tout seul avec les réponses de la personne.
2. **rafals doit-il être une entreprise ?** Le déclarant mandataire se décrit par `Declarant.entrepriseMandataire` (une entreprise, avec son SIREN). ⚠️ Donc oui pour la vraie mise en service ; pour l'espace d'essai de l'INPI, un simple compte suffit. Rien à faire avant la mise en ligne.
3. **Les frais** : ⚠️ à confirmer avec un professionnel ; la création d'une micro-entreprise est en principe gratuite (sauf agent commercial).
4. **Données sensibles** : numéro de sécurité sociale et pièce d'identité. Proposition : gardés seulement le temps du dossier, effacés dès qu'il est accepté ou fermé (à valider avec le MLD).

## 3. Adresses et plan de la carte « Publier une demande » (ajouté le 05/10/2026)
Utilisés par `frontend/src/components/demandes/CartePublierDemande.vue`, directement depuis le navigateur du visiteur (rien ne passe par le serveur de rafals).
- **Propositions d'adresses : service de géocodage de l'État** (Géoplateforme de l'IGN), `https://data.geopf.fr/geocodage/search?q=…&limit=5`. Gratuit, sans clé, sans inscription. Essayé le 05/10/2026 : « 12 rue de lille merignac » → « 12 Rue de Lille 33700 Mérignac », avec sa position (44.824022, -0.615012).
- **Plan : OpenStreetMap**, affiché dans un cadre (`https://www.openstreetmap.org/export/embed.html?bbox=…&marker=…`). Gratuit, sans clé. Pas de bibliothèque ajoutée au projet.
- **Pourquoi pas Google Maps** (demandé par Raphael) : il faut un compte Google Cloud avec une carte bancaire et une clé à garder secrète ; l'adresse et l'adresse IP des visiteurs partent chez Google, ce qui demande un bandeau d'accord (RGPD), alors que le projet garde tout en France ou en Europe (polices installées chez nous, hébergement OVH). Si Raphael veut quand même Google Maps : créer la clé, la mettre dans `.env`, et changer la seule fonction `adressePlan` du composant.
- **À savoir** : en affichant le plan, le navigateur du visiteur parle à OpenStreetMap (adresse IP et zone regardée). À mentionner dans la page « Données personnelles » avant la mise en ligne.
- **À faire au lot 8.3** : décider si les propositions d'adresses passent par le serveur de rafals, comme la vérification du SIRET.
