# Démarrage du projet — fichier de reprise

> Tenu à jour par Claude après CHAQUE réponse du développeur. C'est ce fichier qui permet de reprendre dans une nouvelle conversation.
> État général : **En cours** (devient « Démarrage terminé » à la fin de la phase 8)
> Dernière mise à jour : 27/09/2026 19:45

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
- [ ] 3. Présentation → `.doc/PRESENTATION.md`
- [ ] 4. Vocabulaire → `GLOSSAIRE-METIER.md`
- [ ] 5. Hébergeur et outils → `technique/HEBERGEMENT.md`, `CLAUDE.md`
- [ ] 6. Règles métier (liste des sujets + niveaux 1 et 2) → `SUIVI_REGLES_METIER.md`, `RM-*.md`
- [ ] 7. Charte et conventions d'écran → `CHARTE-VISUELLE.md`, `CONVENTIONS-IHM.md`
- [ ] 8. Plan → `PLAN-DEV.md`, `SUIVI-DEV.md`

## Phase en cours
3. Présentation → `.doc/PRESENTATION.md`

## Questions en attente (posées, pas encore répondues)
1. **3e exclusion** (Raphael n'a pas compris la première formulation : réexpliquée le 27/09/2026) (la méthode en demande au moins 3) : pas de conseil juridique ou fiscal personnalisé ; pas de gestion de salariés (paie) ; pas de vente de produits (seulement des services).

## Prochaine action
Phase 3 : `.doc/PRESENTATION.md` créé vide (modèle B). Questions 1 à 7 répondues (Raphael a relu les réponses 5 à 7). Reste : réponses aux 2 questions en attente ; compléter les contraintes légales ; une 3e exclusion (la méthode en demande au moins 3). Ensuite : relire la fiche complète avec Raphael, cocher la phase 3, passer à la phase 4 (vocabulaire) en proposant des objets supplémentaires.

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
| 27/09 | 1 | Nom du projet (changement) | « rafals » (le dossier s'appelle toujours « rafal ») | CLAUDE.md, REGLES-PROJET.md |

## Décisions prises par Claude (« choisis pour moi »), à revoir si besoin
- (aucune pour l'instant)

## Points à revoir plus tard
- Raphael a refusé que Claude liste le contenu de `C:\Projets\` (27/09/2026) : ne pas parcourir ses dossiers sans qu'il donne le chemin.
- Objets supplémentaires à proposer à Raphael (phase 4) : ex. Avis, Abonnement, Devis, Métier (catégorie), Zone d'intervention, Disponibilité, Mode de paiement.
- Facturation électronique (France) : réception obligatoire pour toutes les entreprises depuis le 01/09/2026, émission obligatoire pour les micro-entreprises au 01/09/2027. Les factures doivent passer par une plateforme agréée par l'État : rafals devra probablement s'y connecter plutôt que l'être. À aborder en question 6 (contraintes) et en phase 5.
- Déclarations URSSAF automatiques : nécessitent une habilitation (« tierce déclaration »). À aborder en question 6.
- Espace disque (19,3 Go libres) : surveiller lors de l'installation de Docker.
