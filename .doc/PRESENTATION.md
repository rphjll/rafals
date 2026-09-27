# rafals — Présentation

> Rempli pendant la phase 3 du démarrage, au fil des réponses de Raphael.

## À quoi sert l'application
Mettre en relation des clients particuliers et des prestataires de services, et offrir aux prestataires (auto-entrepreneurs ou sociétés) des services en ligne pour gérer leur activité.

Réponse de Raphael, mot pour mot (27/09/2026) : « creer un site pour des clients particuliers et/ou prestataires de services pour les mettre en relation et permettre aux prestataires de services qui sont des auto entrepreneur ou societe de beneficier de services en ligne, comme la facturation electronique, le paiement en ligne la gestion de leur agenda et des rdv, l'aide à la creation d'une auto entreprise, l'aide ou l'automatisation des taches administratives d'un autoentrpreneur (declaration...), la possibilité de creer un site web ( dans un sous domaine), qui sera le site vitrine d'un prestataire, et tous autres services possible »

Services cités pour les prestataires :
- facturation électronique ;
- paiement en ligne ;
- gestion de l'agenda et des rendez-vous ;
- aide à la création d'une auto-entreprise ;
- aide ou automatisation des tâches administratives d'un auto-entrepreneur (déclarations…) ;
- création d'un site vitrine sur un sous-domaine ;
- « tous autres services possibles » (à cadrer à la question 5 : ce que l'application ne fera pas).

## Qui l'utilise
| Type d'utilisateur | Ce qu'il vient faire |
|---|---|
| Client particulier | Cherche un prestataire (métier + ville), prend rendez-vous, paie en ligne si le prestataire le propose. Ex. Mme Dupont cherche une femme de ménage à Nantes. |
| Prestataire (auto-entrepreneur ou société) | Crée son profil et ses annonces, gère son agenda et ses rendez-vous, émet ses factures, choisit comment il se fait payer, crée son site vitrine, se fait aider pour ses démarches. Ex. Julie Martin, ménage à domicile. |
| Futur auto-entrepreneur (pas encore déclaré) | Vient se faire aider pour créer son auto-entreprise. Ex. Karim veut devenir plombier indépendant. |
| Administrateur de la plateforme (Raphael) | Gère la plateforme : valide les nouveaux prestataires, règle les litiges, suit les abonnements. |

## Les grands objets
Liste de départ (définis dans `regles-metier/GLOSSAIRE-METIER.md`) :
Prestataire, Client, Annonce (ex. « Ménage 2 h — 50 € »), Rendez-vous, Facture, Paiement, Site vitrine (ex. « julie-menage.rafals.fr »), Démarche administrative (ex. « déclaration URSSAF de septembre »).

Raphael (27/09/2026) : « ca n'est qu'une liste de depart, il devra y en avoir d'autre et tu m'aidera a trouver quoi et comment les developper ». → Claude propose des objets supplémentaires en phase 4 (vocabulaire) et au fil des règles métier (phase 6).

## Les actions principales
1. Le client cherche un prestataire (métier + ville).
2. Le client prend rendez-vous dans l'agenda du prestataire.
3. Le client paie en ligne — **pas obligatoire** : le prestataire choisit comment il se fait payer, et pour quelles annonces (ex. Julie accepte le paiement en ligne pour le ménage, mais seulement espèces ou chèque pour le repassage).
4. Le prestataire crée son profil et ses annonces.
5. Le prestataire gère son agenda.
6. Le prestataire émet une facture électronique.
7. Le prestataire crée son site vitrine (sous-domaine).
8. Le futur auto-entrepreneur est aidé pour créer son auto-entreprise.
9. Le prestataire est aidé pour ses déclarations.

## Ce que l'application ne fera PAS
- Pas de comptabilité complète : pas de bilan, ni de déclaration de TVA de société. Seulement les factures et les déclarations simples d'auto-entrepreneur.
- rafals ne garde jamais l'argent des clients : le paiement en ligne passe par un service de paiement spécialisé (ex. Stripe) et va directement au prestataire. Pas d'agrément Banque de France à obtenir.
- Pas de vente d'objets : rafals ne gère que des services (ménage, plomberie, coiffure…). Ex. un fleuriste ne peut pas vendre ses bouquets en ligne avec livraison.

Restent possibles (proposés comme exclusions le 27/09/2026, non retenus) : une application mobile à installer ; des clients professionnels (entreprises) ; le conseil personnalisé (juridique, fiscal) ; la gestion de salariés (paie).

## Contraintes connues
- Loi (relevé par Claude le 27/09/2026, **à vérifier** en phase 5 et dans les règles métier) :
  - **Données personnelles (RGPD)** : rafals enregistre des noms, adresses, téléphones, rendez-vous. Il faut dire à quoi elles servent, permettre de les consulter et de les effacer, et les héberger en Europe.
  - **Facture électronique** : depuis le 01/09/2026, toute entreprise doit pouvoir recevoir des factures électroniques ; les micro-entreprises devront en émettre à partir du 01/09/2027, en passant par une plateforme agréée par l'État. Entre un prestataire et un **particulier**, ce n'est pas une facture électronique mais une transmission des montants encaissés aux impôts (« e-reporting »).
  - **Plateforme de mise en relation** : obligation d'informer clairement les clients (qui est le prestataire, comment les résultats sont classés) et, sans doute, de déclarer chaque année aux impôts les revenus des prestataires (règle européenne « DAC7 »).
  - **Paiement en ligne** : passe par un service agréé (voir « ne fera pas »).
  - **Déclarations URSSAF automatiques** : nécessitent une habilitation (« tierce déclaration »).
- Pays / langues : France seulement (DOM compris), en français.
- Appareils : ordinateur et téléphone — un seul site qui s'adapte à l'écran.

## Outil existant
**vitrine-express** : un outil commencé par Raphael pour créer des sites vitrines de prestataires à partir de modèles.
Raphael (27/09/2026) : « ca ne doit etre utilisé que comme une base de travail pas un outil fini, loin de la ».
Emplacement : `vitrine-express/vitrine-express/` dans le dossier rafals.

Ce qu'il fait (lu par Claude le 27/09/2026, sans rien modifier) : site en HTML + JavaScript seuls (pas de serveur, pas de base de données), qui s'ouvre d'un double-clic.
- 10 modèles de mise en page × 5 styles chacun = 50 combinaisons (Classique, Élégance, Duo, Magazine, Cartes, Minimal, Impact, Galerie photo, Carte & menu, Pro).
- Textes d'exemple pour 110 métiers rangés en 10 catégories (`js/metiers.js`), avec recherche par les premières lettres.
- Un éditeur : textes, couleurs, disposition, déplacement des rubriques, aperçu ordinateur et téléphone.
- Le client clique « Je veux ce site » : son projet part en fichier `.json` (formulaire Netlify ou e-mail) ; l'administrateur l'ouvre avec un code, puis télécharge le `index.html` final à mettre en ligne sur Netlify.
- Aucun mot de passe ni clé secrète dans les fichiers (vérifié).

Ce qu'on garde / ce qu'on jette : <à décider en phase 5 (outils) et au lot « site vitrine »>. Pistes : les modèles, les styles et la liste des 110 métiers sont réutilisables comme idées et comme contenu ; le fonctionnement (fichier envoyé par e-mail, mise en ligne à la main sur Netlify) sera remplacé par les comptes prestataires et les sous-domaines de rafals.
