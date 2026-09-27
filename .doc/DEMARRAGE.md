# Démarrage du projet — fichier de reprise

> Tenu à jour par Claude après CHAQUE réponse du développeur. C'est ce fichier qui permet de reprendre dans une nouvelle conversation.
> État général : **En cours** (devient « Démarrage terminé » à la fin de la phase 8)
> Dernière mise à jour : 27/09/2026 20:00

## Analyse du dossier (faite le 27/09/2026)
- Cas : **A — dossier vide** (seul `methode-projet.md` est présent)
- Git : non suivi au départ → `git init` + première sauvegarde locale faits le 27/09/2026. Relié le 27/09/2026 au dépôt privé https://github.com/rphjll/rafals (branche `main`, anciennement `master`).
- Identité git : déjà réglée sur le poste (nom « Raphael », adresse raphael.jallu@gmail.com).
- Documents trouvés : `methode-projet.md` (la méthode elle-même). Aucun cahier des charges.
- Code trouvé : aucun.
- Poste (Windows 10 Home, version 19045) :
  - git 2.55.0 : installé
  - VS Code + extension Claude Code : installés (la conversation tourne dedans)
  - Docker : **fonctionne** (vérifié le 27/09/2026 : Docker 29.8.0, `docker run hello-world` affiche « Hello from Docker! »)
  - WSL 2 : **installé le 27/09/2026** (`wsl --install --no-distribution --web-download` ; la version Microsoft Store avait échoué avec « Défaillance irrémédiable ») → PC redémarré, vérifié par `wsl --status` (version par défaut 2, WSL 2.7.14)
  - Virtualisation du processeur : **activée** (vérifié le 27/09/2026 par commande : `VirtualizationFirmwareEnabled = True`)
  - Mémoire vive : 7,9 Go (suffisant, mais juste pour Docker)
  - Disque C : 19,3 Go libres au départ, **16,4 Go** après WSL (Docker Desktop prendra environ 3 à 4 Go, puis 2 à 3 Go pour les conteneurs du projet)
  - Docker Desktop 4.91.0 : **installé le 27/09/2026** par winget. Disque C : **12,9 Go** libres après installation.
  - Comptes Windows : Raphael travaille sous `rapha` (compte **standard**, pas administrateur). Les administrateurs sont `Administrateur` et `lione`. L'installation de Docker a donc été validée avec `lione`, et c'est `lione` qui a été mis dans le groupe `docker-users` : `rapha` n'y est pas → → `rapha` **ajouté à `docker-users`** le 27/09/2026 (vérifié : le groupe contient `lione` et `rapha`).
  - Disque C après redémarrage : **44,3 Go** libres (Windows a libéré de la place au redémarrage, sans doute les fichiers temporaires des installations)
  - Outil `gh` (GitHub en ligne de commande) : absent, pas nécessaire (le dépôt se crée sur le site)
  - winget 1.29 (installateur de logiciels de Windows) : présent

## Phases
- [x] 1. Le poste (terminée le 27/09/2026)
- [x] 2. Le projet (git, GitHub, arborescence) (terminée le 27/09/2026)
- [x] 3. Présentation → `.doc/PRESENTATION.md` (terminée le 27/09/2026)
- [x] 4. Vocabulaire → `GLOSSAIRE-METIER.md` (terminée le 27/09/2026)
- [x] 5. Hébergeur et outils → `technique/HEBERGEMENT.md`, `CLAUDE.md` (terminée le 27/09/2026)
- [ ] 6. Règles métier (liste des sujets + niveaux 1 et 2) → `SUIVI_REGLES_METIER.md`, `RM-*.md`
- [ ] 7. Charte et conventions d'écran → `CHARTE-VISUELLE.md`, `CONVENTIONS-IHM.md`
- [ ] 8. Plan → `PLAN-DEV.md`, `SUIVI-DEV.md`

## Phase en cours
6. Règles métier (liste des sujets + niveaux 1 et 2) → `SUIVI_REGLES_METIER.md`, `RM-*.md`

## Questions en attente (posées, pas encore répondues)
1. **Sujet 02, Q5 — Visible tout de suite ?** A. visible tout de suite, l'administrateur peut bloquer ensuite (recommandé) ; B. visible seulement après validation de l'administrateur ; C. choisis pour moi.

## Prochaine action
Phase 6 : lire l'étape 5 et le § 7.1 de la méthode (niveaux), les modèles D et E. Liste des 16 sujets validée. Sujet 01 validé. Sujet 02 « Prestataires » en cours (questions prévues, une par une : plusieurs métiers, zone d'intervention, vérification du SIRET, validation par l'administrateur avant d'être visible). Ensuite : écrire les règles des niveaux 1 et 2, une question à la fois.

## Arborescence créée (phase 2)
`.doc/regles-metier/`, `.doc/ihm/`, `.doc/technique/` (vides, avec un fichier `.gitkeep` pour que git les garde). Les fichiers `.md` de chaque dossier sont créés dans leur phase.

## Guide donné pour le BIOS (HP EliteBook 840 G2, BIOS M71 01.18, processeur Intel i5-5300U)
1. Sauvegarder son travail et redémarrer le PC.
2. Dès l'allumage, appuyer plusieurs fois sur **Échap**, puis **F10** (« Computer Setup »).
3. Onglet **Advanced** → **Device Configurations** (ou **System Options**) → cocher **Virtualization Technology (VTx)**.
4. **Main** → **Save Changes and Exit** → confirmer.
5. Si le BIOS demande un mot de passe administrateur : s'arrêter et le dire à Claude.

## Réponses obtenues
| Date | Phase | Question | Réponse | Écrite dans |
|---|---|---|---|---|
| 27/09 | 1 | As-tu un compte GitHub ? | Oui (identifiant à donner) | DEMARRAGE.md |
| 27/09 | 1 | Quand activer la virtualisation et installer Docker ? | Maintenant | DEMARRAGE.md |
| 27/09 | 1 | Nom du projet ? | Garder « rafal » (remplacé ensuite par « rafals ») | CLAUDE.md, REGLES-PROJET.md |
| 27/09 | 1 | Virtualisation activée dans le BIOS ? | Oui, vérifié par commande (`True`) | DEMARRAGE.md |
| 27/09 | 1 | Identifiant GitHub | `rphjll` | DEMARRAGE.md |
| 27/09 | 1 | Installer WSL 2 : qui lance la commande ? | Claude, en fenêtre administrateur, sans Ubuntu | DEMARRAGE.md |
| 27/09 | 1 | Installer Docker Desktop : comment ? | Claude, avec winget | DEMARRAGE.md |
| 27/09 | 1 | Ajouter `rapha` au groupe `docker-users` ? | Oui, fait par Claude | DEMARRAGE.md |
| 27/09 | 2 | Visibilité du dépôt GitHub | Privé | DEMARRAGE.md |
| 27/09 | 3 | À quoi sert rafals ? | Mise en relation clients particuliers / prestataires + services en ligne pour les prestataires (facturation électronique, paiement, agenda, création d'auto-entreprise, déclarations, site vitrine) | PRESENTATION.md |
| 27/09 | 3 | Qui utilise rafals ? | Client particulier, Prestataire, Futur auto-entrepreneur, Administrateur | PRESENTATION.md |
| 27/09 | 3 | Grands objets | Liste de départ acceptée ; d'autres viendront, Claude aide à les trouver | PRESENTATION.md |
| 27/09 | 3 | Actions principales | Acceptées ; le paiement en ligne n'est pas obligatoire, le prestataire choisit son mode de paiement par prestation | PRESENTATION.md |
| 27/09 | 3 | Ce que rafals ne fera pas | Pas de comptabilité complète ; rafals ne garde jamais l'argent. (Appli mobile et clients pros restent possibles) | PRESENTATION.md |
| 27/09 | 3 | Pays et langue | France (DOM compris), français | PRESENTATION.md |
| 27/09 | 3 | Appareils | Ordinateur et téléphone | PRESENTATION.md |
| 27/09 | 3 | Outil existant | vitrine-express (création de sites vitrines à partir de modèles), base de travail seulement, loin d'être fini | PRESENTATION.md |
| 27/09 | 3 | Garder vitrine-express suivi par git ? | Oui | DEMARRAGE.md |
| 27/09 | 3 | 3e limite (ne fera pas) | Pas de vente d'objets (conseil personnalisé et salariés restent possibles) | PRESENTATION.md |
| 27/09 | 3 | Fiche de présentation validée ? | Oui | PRESENTATION.md |
| 27/09 | 4 | Client et prestataire : un seul compte ? | Oui, un seul compte | GLOSSAIRE-METIER.md |
| 27/09 | 4 | Société avec plusieurs salariés : combien d'agendas ? | Un seul agenda par prestataire (pour commencer) | GLOSSAIRE-METIER.md |
| 27/09 | 4 | Futur auto-entrepreneur qui reçoit son SIRET | Il garde le même compte | GLOSSAIRE-METIER.md |
| 27/09 | 4 | Prestataire sans SIRET visible ? | Il peut publier, paiement en espèces seulement ; rafals lui conseille le SIRET. Avec SIRET : carte sur le site ou espèces, au choix par publication. ⚠️ à vérifier juridiquement | GLOSSAIRE-METIER.md |
| 27/09 | 4 | « Publication », c'est quoi ? | Une annonce de service (= Prestation) | GLOSSAIRE-METIER.md |
| 27/09 | 4 | Mot pour une annonce de service | « Annonce » (remplace « Prestation » et « Publication ») | GLOSSAIRE-METIER.md, PRESENTATION.md |
| 27/09 | 4 | Comment le client cherche ? | Grande liste de tous les métiers, rangés dans des catégories (« dossiers », ex. Commerces), + recherche par les premières lettres | GLOSSAIRE-METIER.md |
| 27/09 | 4 | Avis des clients ? | Oui, seulement après un vrai rendez-vous | GLOSSAIRE-METIER.md |
| 27/09 | 4 | Devis sur rafals ? | Oui, accepté en un clic, transformé en facture | GLOSSAIRE-METIER.md |
| 27/09 | 4 | Comment rafals gagne de l'argent ? | Commission sur les paiements par carte (sûr) ; site vitrine : abonnement ou prix unique « à vie », à décider ensemble | GLOSSAIRE-METIER.md |
| 27/09 | 4 | Glossaire validé ? | Oui (14 mots) | GLOSSAIRE-METIER.md |
| 27/09 | 5 | Hébergeur | OVHcloud « pour l'instant », avec possibilité de changer (portabilité : Docker, PostgreSQL, S3) | HEBERGEMENT.md |
| 27/09 | 5 | Réserver rafals.fr | Plus tard, avant la mise en ligne | HEBERGEMENT.md |
| 27/09 | 5 | Outils | Ceux de la méthode : Python + FastAPI, Vue 3 + TypeScript + Tailwind, PostgreSQL, MinIO/S3, Docker. Ports 8001 / 5174 / 5433 gardés (choix par défaut de Claude) | CLAUDE.md, REGLES-PROJET.md |
| 27/09 | 6 | Liste des 16 sujets de règles | Validée | SUIVI_REGLES_METIER.md |
| 27/09 | 6 | Sujet 01 : comment s'inscrire ? | Mail + mot de passe, lien de vérification | RM-COMPTES.md |
| 27/09 | 6 | Sujet 01 : client ou prestataire à l'inscription ? | Pareil pour tous, puis « Proposer mes services » | RM-COMPTES.md |
| 27/09 | 6 | Sujet 01 : âge minimum | 16 ans, accord des parents avant 18 ans | RM-COMPTES.md |
| 27/09 | 6 | Sujet 01 : qui est administrateur ? | Raphael seul au début, peut en nommer d'autres (« quelques potes », pas sûr) | RM-COMPTES.md |
| 27/09 | 6 | Sujet 01 Comptes : relecture | Validé (y compris les règles de sécurité proposées) | RM-COMPTES.md |
| 27/09 | 6 | Sujet 02 : plusieurs métiers ? | Oui : un métier principal + des secondaires ; en métier secondaire, affiché après les spécialistes ; classement par note | RM-PRESTATAIRES.md |
| 27/09 | 6 | Sujet 02 : zone d'intervention | Ville + distance en km (vol d'oiseau, choix de Claude pour le cas limite) | RM-PRESTATAIRES.md |
| 27/09 | 6 | Sujet 02 : vérifier le SIRET ? | Oui, automatiquement (répertoire de l'État) | RM-PRESTATAIRES.md |
| 27/09 | 6 | Sujet 02 : lieu du service | Au choix par annonce : chez le client, chez moi, les deux | RM-PRESTATAIRES.md |
| 27/09 | 1 | Nom du projet (changement) | « rafals » (le dossier s'appelle toujours « rafal ») | CLAUDE.md, REGLES-PROJET.md |

## Décisions prises par Claude (« choisis pour moi »), à revoir si besoin
- Ports côté PC : serveur 8001, écrans 5174, base 5433 (ceux du modèle ; aucun autre projet sur ce PC ne les utilise pour l'instant).
- Distance de la zone d'intervention mesurée à vol d'oiseau entre les centres des villes (sujet 02).
- Mots de passe des bases : fixés au lot 0.1 (fichier `.env`, jamais envoyé sur GitHub).

## Points à revoir plus tard
- Réserver `rafals.fr` avant la mise en ligne (libre au 27/09/2026) ; revérifier qu'il est toujours libre.
- À décider ensemble : pourcentage de la commission ; prix du site vitrine (abonnement ou prix unique à vie).
- Liste de « tous les métiers qui existent » : choisir la source (ex. répertoire officiel des métiers de France Travail, le « ROME », en ne gardant que les métiers qui servent des particuliers ; ou compléter les 110 de vitrine-express). À décider au lot qui construit la recherche.
- ⚠️ **Juridique, avant mise en ligne** : prestataires sans SIRET payés en espèces via rafals → risque de travail non déclaré et de responsabilité de la plateforme. Faire vérifier par un avocat ou un expert-comptable.
- Idée à proposer plus tard : les particuliers peuvent employer quelqu'un sans SIRET pour le ménage, le jardinage ou le petit bricolage, en le payant avec le CESU (chèque emploi service universel) ; rafals pourrait un jour proposer cette formule.
- Façon de poser les questions : 3 questions sur 4 non comprises le 27/09/2026 → une seule question à la fois, phrases courtes, notion expliquée juste avant.
- Raphael a refusé que Claude liste le contenu de `C:\Projets\` (27/09/2026) : ne pas parcourir ses dossiers sans qu'il donne le chemin.
- Objets supplémentaires à proposer à Raphael (phase 4) : ex. Avis, Abonnement, Devis, Métier (catégorie), Zone d'intervention, Disponibilité, Mode de paiement.
- Facturation électronique (France) : réception obligatoire pour toutes les entreprises depuis le 01/09/2026, émission obligatoire pour les micro-entreprises au 01/09/2027. Les factures doivent passer par une plateforme agréée par l'État : rafals devra probablement s'y connecter plutôt que l'être. À aborder en question 6 (contraintes) et en phase 5.
- Déclarations URSSAF automatiques : nécessitent une habilitation (« tierce déclaration »). À aborder en question 6.
- Espace disque (19,3 Go libres) : surveiller lors de l'installation de Docker.
