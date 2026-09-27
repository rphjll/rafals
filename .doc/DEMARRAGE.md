# Démarrage du projet — fichier de reprise

> Tenu à jour par Claude après CHAQUE réponse du développeur. C'est ce fichier qui permet de reprendre dans une nouvelle conversation.
> État général : **En cours** (devient « Démarrage terminé » à la fin de la phase 8)
> Dernière mise à jour : 27/09/2026 17:32

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
1. **Compte GitHub** — As-tu déjà un compte sur github.com ? Choix : A. Oui (donner l'identifiant) ; B. Non, guide-moi pour le créer (recommandé si pas de compte) ; C. Je ne sais pas.
2. **Virtualisation et Docker** — Docker a besoin que la « virtualisation » soit activée dans le BIOS, ce qui n'est pas le cas sur ce PC. Choix : A. Guide-moi maintenant pas à pas (recommandé : sans Docker, le code ne pourra pas tourner à partir du lot 0.1) ; B. Plus tard, on avance d'abord sur les phases 2 à 8 qui ne produisent que des documents ; C. Je ne sais pas, choisis pour moi.
3. **Nom du projet** — Le dossier s'appelle « rafal ». Choix : A. Garder « rafal » comme nom du projet ; B. Un autre nom (le donner) ; C. Je ne sais pas encore, on verra en phase 3.

## Prochaine action
Attendre les réponses aux 3 questions ci-dessus, puis guider l'installation (compte GitHub, virtualisation, WSL 2, Docker Desktop) selon les réponses.

## Réponses obtenues
| Date | Phase | Question | Réponse | Écrite dans |
|---|---|---|---|---|

## Décisions prises par Claude (« choisis pour moi »), à revoir si besoin
- (aucune pour l'instant)

## Points à revoir plus tard
- Espace disque (19,3 Go libres) : surveiller lors de l'installation de Docker.
