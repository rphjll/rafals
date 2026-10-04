# rafals — API extérieures étudiées (pour les services du niveau 6)

> Recherches faites par Claude le 04/10/2026 à la demande de Raphael. Rien n'est construit. Les points marqués ❓ ne sont pas encore vérifiés.

## 1. Déclarer à l'URSSAF depuis rafals : « API Tierce Déclaration auto-entrepreneur »
Demande de Raphael, mot pour mot : « avoir une api qui se connecte a l'ursaf direct comme ca y'a pas besoin d'aller sur le site de l'ursaf pour declarer […] ils clicent sur un bonton et ca l'envoie a l'urasaf ».
- **Elle existe**, proposée par l'URSSAF aux plateformes où des auto-entrepreneurs vendent leurs services.
- Elle permet : enregistrer l'accord du prestataire (un « mandat »), estimer ses cotisations, déclarer son chiffre d'affaires à sa place. Le prestataire peut toujours corriger sur son compte URSSAF.
- Pour y accéder : présenter le projet et s'inscrire sur https://portailapi.urssaf.fr/fr/ (le portail ne répondait pas le 04/10/2026).
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
