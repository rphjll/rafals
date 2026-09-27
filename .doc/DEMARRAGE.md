# Démarrage du projet — fichier de reprise

> Tenu à jour par Claude après CHAQUE réponse du développeur. C'est ce fichier qui permet de reprendre dans une nouvelle conversation.
> État général : **En cours** (devient « Démarrage terminé » à la fin de la phase 8)
> Dernière mise à jour : 27/09/2026 17:40

## Analyse du dossier (faite le 27/09/2026)
- Cas : **A — dossier vide** (seul `methode-projet.md` est présent)
- Git : non suivi au départ → `git init` + première sauvegarde locale faits le 27/09/2026. Pas encore relié à GitHub (phase 2).
- Identité git : déjà réglée sur le poste (nom « Raphael », adresse raphael.jallu@gmail.com).
- Documents trouvés : `methode-projet.md` (la méthode elle-même). Aucun cahier des charges.
- Code trouvé : aucun.
- Poste (Windows 10 Home, version 19045) :
  - git 2.55.0 : installé
  - VS Code + extension Claude Code : installés (la conversation tourne dedans)
  - Docker : **absent** (ni la commande, ni Docker Desktop)
  - WSL 2 : **absent**
  - Virtualisation du processeur : **désactivée dans le BIOS** → à activer avant Docker
  - Mémoire vive : 7,9 Go (suffisant, mais juste pour Docker)
  - Disque C : 19,3 Go libres (juste : Docker + WSL prennent 5 à 10 Go)

## Phases
- [ ] 1. Le poste
- [ ] 2. Le projet (git, GitHub, arborescence)
- [ ] 3. Présentation → `.doc/PRESENTATION.md`
- [ ] 4. Vocabulaire → `GLOSSAIRE-METIER.md`
- [ ] 5. Hébergeur et outils → `technique/HEBERGEMENT.md`, `CLAUDE.md`
- [ ] 6. Règles métier (liste des sujets + niveaux 1 et 2) → `SUIVI_REGLES_METIER.md`, `RM-*.md`
- [ ] 7. Charte et conventions d'écran → `CHARTE-VISUELLE.md`, `CONVENTIONS-IHM.md`
- [ ] 8. Plan → `PLAN-DEV.md`, `SUIVI-DEV.md`

## Phase en cours
1. Le poste

## Questions en attente (posées, pas encore répondues)
1. **Identifiant GitHub** — Quel est ton identifiant sur github.com (le nom affiché en haut à droite quand tu es connecté) ?
2. **Virtualisation** — As-tu pu activer « Virtualization Technology (VTx) » dans le BIOS de ton HP EliteBook 840 G2 ? Choix : A. Oui, c'est fait (Claude le vérifie par une commande) ; B. Je suis bloqué (dire à quel moment).

## Prochaine action
Guide en cours : activer la virtualisation dans le BIOS (le PC redémarre, la conversation s'arrête). À la reprise : vérifier par commande que la virtualisation est activée (`VirtualizationFirmwareEnabled`), puis guider l'installation de WSL 2 (`wsl --install`, avec accord), puis de Docker Desktop.

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
| 27/09 | 1 | Nom du projet ? | Garder « rafal » | CLAUDE.md, REGLES-PROJET.md |

## Décisions prises par Claude (« choisis pour moi »), à revoir si besoin
- (aucune pour l'instant)

## Points à revoir plus tard
- Espace disque (19,3 Go libres) : surveiller lors de l'installation de Docker.
