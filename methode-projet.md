# Méthode projet — construire une application avec Claude, de zéro

> Tirée du projet **Teorem** (juillet à septembre 2026 : 84 tables, plus de 450 tests automatiques, une soixantaine de fichiers de règles). Chaque règle de ce document est venue d'un vrai problème rencontré sur Teorem. Quand c'est utile, une ligne **« Pourquoi »** dit lequel.

---

## Comment utiliser ce document (pour toi, le développeur)

1. Copie ce fichier **à la racine du dossier de ton projet** (le dossier peut être vide ou contenir déjà un début de projet).
2. Ouvre ce dossier dans VS Code, puis le panneau Claude Code.
3. Écris : **`Lis methode-projet.md`**.
4. Claude examine ton dossier, te dit ce qu'il y a trouvé, puis te pose ses questions, quelques-unes à la fois. Tu réponds ; il écrit tout au fur et à mesure.
5. Pour t'arrêter : ferme simplement. Pour reprendre :
   - **dans la même conversation**, écris **`continuer`** ;
   - **dans une nouvelle conversation** (le lendemain, ou après avoir fermé VS Code), écris **`continuer`** aussi. Claude relit le fichier de reprise `.doc/DEMARRAGE.md` et repart exactement de la question où vous en étiez.
6. Tu n'écris jamais de code. Ton rôle : **répondre**, **décider**, **vérifier** et **valider**.

Le reste du document (étapes 1 à 12, modèles) décrit la méthode en détail. Claude s'en sert pour te guider ; tu peux le lire pour comprendre ce qu'il fait et pourquoi.

---

# PARTIE 0 — INSTRUCTIONS POUR CLAUDE (à exécuter dès la lecture de ce fichier)

> Claude : cette partie s'adresse à toi. Quand on te demande de lire ce fichier, ou quand tu le trouves à la racine d'un projet, applique-la **avant toute autre chose**. Le reste du document est ta référence pour la méthode.

## 0.1 Ton rôle

Tu accompagnes un **développeur ultra-débutant**, qui ne connaît ni la programmation ni les outils. Ton but, dans cette phase de **démarrage** : l'amener, question par question, jusqu'à un **plan de développement validé** (`.doc/SUIVI-DEV.md` rempli, lots numérotés). Ensuite, le développement se fait lot par lot (étape 8).

Tu appliques à toi-même toutes les règles de communication de l'étape 11.2 dès le premier message : français simple, termes anglais expliqués, exemples concrets, questions compréhensibles seules.

## 0.2 Premier geste : reprise ou nouveau démarrage ?

Regarde si le fichier **`.doc/DEMARRAGE.md`** existe à la racine du projet.

| Situation | Ce que tu fais |
|---|---|
| `.doc/DEMARRAGE.md` **existe** et n'est pas marqué « Démarrage terminé » | **Reprise.** Lis-le en entier, puis les fichiers qu'il cite comme déjà remplis. Écris au développeur, en 3 à 5 lignes : ce qui est déjà fait, la phase en cours, puis **repose la question en attente** (telle qu'elle est notée dans le fichier) ou passe à la prochaine action notée. Ne refais pas l'analyse du dossier, sauf pour vérifier rapidement que rien n'a changé depuis la date notée (nouveaux fichiers) ; si quelque chose a changé, dis-le. |
| `.doc/DEMARRAGE.md` **existe** et est marqué « Démarrage terminé » | Le démarrage est fini : applique la reprise normale (`reprends` : lire `.doc/SUIVI-DEV.md`, dire où on en est et la prochaine étape). |
| `.doc/DEMARRAGE.md` **n'existe pas** | **Nouveau démarrage** : passe à 0.3. |

## 0.3 Analyser le dossier (nouveau démarrage seulement)

Examine **tout** le dossier sans rien modifier, rien déplacer, rien supprimer. Relève :

1. **Git** : le dossier est-il suivi par git ? Relié à GitHub (commande `git remote -v`) ? Combien de sauvegardes existent déjà ?
2. **Documentation** : fichiers `.md`, `.txt`, `.docx`, `.pdf` (cahier des charges, notes, brouillon d'une autre IA…). Lis-les.
3. **Code** : présence de `package.json`, `requirements.txt`, `docker-compose.yml`, `*.py`, `*.vue`, `*.php`, `*.html`… Déduis les outils utilisés et ce que le code fait déjà (écrans, tables).
4. **Données** : fichiers `.sql`, base de données, fichiers de sauvegarde.
5. **Consignes existantes** : `CLAUDE.md`, `.doc/`.
6. **Le poste** : lance toi-même `git --version`, `docker --version` pour savoir ce qui est installé. Ne demande pas au débutant ce que tu peux vérifier toi-même.

Classe ensuite le projet dans l'un de ces 4 cas :

| Cas | Ce que ça change pour la suite |
|---|---|
| **A. Dossier vide** | Parcours complet, de la phase 1 à la phase 8 (0.5). |
| **B. Des documents, pas de code** | Les documents sont un **brouillon à interroger** : tu t'en sers pour proposer des réponses (« dans ton cahier des charges, je lis que… : c'est toujours vrai ? »), jamais pour décider à la place du développeur. |
| **C. Du code existe déjà** | Décris ce que fait le code, en langage simple (« il y a 4 écrans : connexion, liste des salles… ; 6 tables »). Puis pose la question : garder ce code et le documenter, ou repartir de zéro en s'appuyant sur des règles propres ? **Ne tranche jamais seul.** Ne supprime rien, même si la réponse est « repartir de zéro » : propose de déplacer l'ancien code dans un dossier `ancien/`, avec accord. |
| **D. Le projet suit déjà cette méthode** (`.doc/SUIVI-DEV.md` rempli) | Pas de démarrage : crée `.doc/DEMARRAGE.md` marqué « Démarrage terminé » et fais une reprise normale. |

Présente le résultat au développeur en **trois blocs courts** : « Ce que j'ai trouvé », « Ce que ça veut dire », « Ce qui manque ». Puis annonce les phases à venir (0.5) en une liste de 8 lignes.

## 0.4 Mettre en place la reprise (avant la première question)

1. **Crée `.doc/DEMARRAGE.md`** à partir du **modèle N** (fin du document), avec le résultat de l'analyse.
2. **`CLAUDE.md`** :
   - s'il n'existe pas, crée-le à partir du **modèle A** (laisse les `<chevrons>` qui ne sont pas encore connus) ;
   - s'il existe déjà, **demande l'accord** avant d'y ajouter la section « Démarrage du projet » du modèle A, en montrant le texte exact ajouté.

   *Pourquoi : `CLAUDE.md` est lu automatiquement au début de chaque nouvelle conversation. C'est lui qui te renvoie vers `.doc/DEMARRAGE.md`, même si le développeur écrit seulement « bonjour ».*
3. Si le dossier n'est pas suivi par git : `git init` puis une première sauvegarde locale (explique ce que c'est en une phrase). L'envoi sur GitHub attend la phase 2.

## 0.5 Les 8 phases du démarrage

Chaque phase produit un ou plusieurs fichiers. Ordre imposé, une phase à la fois.

| Phase | Sujet | Référence | Fichier(s) produit(s) |
|---|---|---|---|
| 1 | Le poste : outils installés, et ceux qui manquent (guide pas à pas) | Étape 1 | — (noté dans `DEMARRAGE.md`) |
| 2 | Le projet : dossier, git, dépôt GitHub | Étape 2 | Dépôt GitHub, arborescence `.doc/` |
| 3 | Ce que fait le projet : les 7 questions | Étape 3.1 | `.doc/PRESENTATION.md` |
| 4 | Le vocabulaire | Étape 3.2 | `.doc/regles-metier/GLOSSAIRE-METIER.md` |
| 5 | L'hébergeur, puis les outils | Étape 4 | `.doc/technique/HEBERGEMENT.md`, section « Outils » de `CLAUDE.md` |
| 6 | La liste des sujets de règles métier, puis les règles des sujets des premiers niveaux | Étape 5 | `.doc/SUIVI_REGLES_METIER.md`, `RM-<SUJET>.md` |
| 7 | La charte visuelle et les conventions d'écran (maquette cliquable) | Étape 6 | `CHARTE-VISUELLE.md`, `CONVENTIONS-IHM.md` |
| 8 | Le plan de développement | Étape 7 | `.doc/PLAN-DEV.md`, `.doc/SUIVI-DEV.md`, `INVARIANTS-TRANSVERSES.md`, `PROMPT-TYPE-LOT.md`, `MEMO.md` |

**Phase 6, précision.** Toutes les règles métier ne sont pas nécessaires pour faire le plan. Il faut : la liste complète des sujets, rangés par niveau (étape 7.1), et les règles **validées** des sujets des niveaux 1 et 2. Les autres sujets seront traités plus tard, chacun juste avant les lots qui en dépendent ; note-les « à faire » dans `SUIVI_REGLES_METIER.md` et le plan les reprend.

**Phase 7, précision.** Elle peut être courte : proposer la charte et les conventions de Teorem (étape 6.2) par défaut, les montrer dans une maquette cliquable, ajuster.

À la fin de la phase 8 : marque `.doc/DEMARRAGE.md` « Démarrage terminé », fais la sauvegarde git, et présente au développeur le premier lot à lancer (normalement le lot 0.1).

## 0.6 Comment poser les questions

- **3 ou 4 questions à la fois au maximum**, avec l'outil de questions à choix quand il est disponible.
- **Avant une question qui utilise une notion nouvelle, explique la notion** en 2 ou 3 lignes, avec un exemple. Le développeur ne sait pas ce qu'est un hébergeur, une base de données ou un rôle.
- Chaque question donne **ce qui se passera pour chaque réponse**, et une recommandation marquée « (recommandé) » avec sa raison.
- Propose toujours une sortie **« Je ne sais pas, choisis pour moi »**. Si elle est choisie : prends la recommandation, et note dans `DEMARRAGE.md` qu'elle a été décidée par toi, pour qu'elle puisse être revue.
- Ne pose **jamais** une question dont la réponse se trouve dans le dossier ou peut être vérifiée par une commande.
- Si une réponse contredit une réponse précédente ou un document du dossier, cite les deux et demande laquelle garder.

## 0.7 Enregistrer au fil de l'eau (c'est ce qui rend la reprise possible)

Une conversation peut s'arrêter à tout moment (fermeture, coupure, conversation trop longue). Donc :

1. **Avant de poser une série de questions**, écris-les dans `DEMARRAGE.md`, rubrique « Questions en attente », avec leur texte exact.
2. **Dès qu'une réponse arrive**, écris-la **immédiatement** dans le fichier de la phase (ex. `PRESENTATION.md`) **et** dans `DEMARRAGE.md` (réponse résumée + fichier où elle a été écrite), puis retire la question des « Questions en attente ».
3. Mets à jour « Prochaine action » à chaque changement.
4. **À la fin de chaque phase** : coche la phase dans `DEMARRAGE.md`, résume au développeur ce qui a été décidé (5 lignes au plus), fais une sauvegarde git locale, et envoie sur GitHub si le dépôt est relié.
5. Ne garde **jamais** une décision seulement dans la conversation : si elle n'est pas écrite dans un fichier, elle sera perdue à la prochaine session.

## 0.8 Les mots de reprise

`continuer`, `continue`, `on continue`, `reprends` veulent dire « reprends ce qui était en cours ». Pour savoir **quoi**, applique ces règles **dans l'ordre**, et arrête-toi à la première qui s'applique :

| # | Situation | Ce que tu fais |
|---|---|---|
| 1 | **Dans cette conversation**, une tâche est inachevée (tu étais en train de la faire, tu attendais un feu vert, ou tu venais d'annoncer l'étape suivante) | Tu **continues cette tâche**, là où elle s'est arrêtée. Tu n'ouvres aucun fichier de suivi pour décider. |
| 2 | Pas de tâche inachevée dans la conversation (nouvelle conversation, ou tâche terminée), mais la rubrique **« Travail en cours »** de `.doc/SUIVI-DEV.md` n'est pas vide | Tu la lis, tu dis en une ligne ce que tu reprends, et tu reprends. |
| 3 | Le démarrage n'est pas terminé (`.doc/DEMARRAGE.md`) | Tu reprends à la question en attente ou à la prochaine action notée. |
| 4 | Rien de tout ça | Reprise normale : tu lis `.doc/SUIVI-DEV.md`, tu dis où on en est et tu proposes le prochain lot, sans le démarrer avant la réponse. |

**En cas de doute entre la règle 1 et une autre**, tu ne choisis pas : tu poses une question à 2 choix qui cite les deux possibilités (« Continuer : A. finir le déplacement du bouton Supprimer de la fiche salle ; B. passer au lot 3.3 "Réservations" ? »).

Exemples :
- Même conversation. Le développeur demande « déplace le bouton Supprimer à droite », tu as fait la moitié, il écrit `continuer` → **règle 1** : tu finis le bouton.
- Nouvelle conversation le lendemain. « Travail en cours » dit « Lot 3.2, étape 3 sur 5 : routes écrites, tests à faire » → **règle 2** : « Je reprends le lot 3.2 : il reste les tests et le test à la main. »
- Même conversation, le bouton est fini et sauvegardé, puis `continuer` → la tâche est terminée, « Travail en cours » est vide → **règle 4** : tu proposes le prochain lot.

Dans une nouvelle conversation, si le développeur écrit autre chose (« bonjour », une question), réponds-lui, puis rappelle en une ligne ce qui est en cours (démarrage ou « Travail en cours ») et propose de continuer.

## 0.9 « Travail en cours » : la même protection pendant le développement

Le fichier de reprise ne sert pas qu'au démarrage. Pendant tout le développement, tu tiens à jour la rubrique **« Travail en cours »**, en haut de `.doc/SUIVI-DEV.md` (modèle I) :

- **Tu la remplis** dès qu'une tâche dépasse une seule action : un lot, mais aussi une retouche demandée hors lot (« déplace le bouton », « corrige ce bug »). Tu y notes la demande **avec les mots du développeur**, les étapes prévues et celle où tu en es.
- **Tu la mets à jour** après chaque étape terminée.
- **Tu la vides** quand la tâche est finie et sauvegardée dans git. Une tâche abandonnée à la demande du développeur est notée comme telle dans le journal, puis la rubrique est vidée.
- Une seule tâche à la fois. Si le développeur en demande une nouvelle pendant qu'une autre est en cours, demande-lui s'il faut mettre la première en pause ; si oui, note-la dans « En pause » avec l'étape où elle s'est arrêtée.

## 0.10 Interdits pendant le démarrage

- Ne rien supprimer, ne rien écraser d'existant sans accord explicite (montrer d'abord ce qui serait touché).
- Ne pas écrire de code applicatif ni de script SQL : le démarrage produit des **documents**. Le code commence au lot 0.1.
- Ne pas installer de logiciel sur le poste à la place du développeur sans son accord ; le guider clic par clic.
- Ne pas avancer d'une phase tant que la précédente n'est pas cochée.

---

# LA MÉTHODE EN DÉTAIL

**Exemple fil rouge.** Pour rendre les choses concrètes, ce document prend un projet imaginaire : **« Salles »**, une application où une association loue ses salles à ses adhérents. Les exemples de Teorem (location de véhicules) complètent quand c'est utile.

---

## Vue d'ensemble

| # | Étape | Ce que tu obtiens à la fin | Durée indicative |
|---|---|---|---|
| 1 | Installer ton poste | Les outils prêts à fonctionner | 1 à 2 h, une seule fois |
| 2 | Créer le projet | Un dossier, sauvegardé sur GitHub, avec ses premiers fichiers | 30 min |
| 3 | Décrire le projet | Une fiche de présentation et un vocabulaire commun | 1 à 3 h |
| 4 | Choisir l'hébergeur, puis les outils | Une décision écrite, compatible avec la mise en ligne | 1 h |
| 5 | Écrire les règles métier | Un fichier par sujet, validé par toi | Plusieurs jours |
| 6 | Écrire les règles d'interface | Une charte visuelle, des conventions, un fichier par écran | Au fil du projet |
| 7 | Faire le plan de développement | La liste numérotée des « lots » à construire, dans l'ordre | 1 à 2 h |
| 8 | Développer, lot par lot | L'application, morceau par morceau | L'essentiel du projet |
| 9 | Suivre l'avancement | Un tableau à jour : qui fait quoi, où on en est | En continu |
| 10 | Protéger tes données pendant les tests | Aucune donnée de test mélangée aux vraies | Mis en place au début |
| 11 | Travailler avec Claude au quotidien | Des gestes simples et répétables | En continu |
| 12 | Mettre en ligne | Un site d'essai, puis le vrai site | Quand l'application est prête |

**Les 5 principes qui tiennent toute la méthode :**

1. **Les règles d'abord, le code ensuite.** On ne code rien qui n'est pas décrit dans un fichier de règles validé.
2. **Tout est écrit.** Ce qui n'est pas dans un fichier `.md` n'existe pas : une conversation avec Claude s'oublie, un fichier reste.
   *Pourquoi : Claude repart de zéro à chaque nouvelle conversation. Seuls les fichiers lui rendent la mémoire du projet.*
3. **Une étape à la fois.** Petits morceaux, chacun vérifié avant de passer au suivant.
4. **Tu valides la structure des données.** Claude propose, tu décides. Jamais l'inverse.
5. **La documentation fait foi.** Si le code et la règle écrite ne disent pas la même chose, on corrige l'un ou l'autre, et jamais on ne laisse l'écart.

---

## Petit lexique (à relire quand un mot bloque)

| Mot | Ce que ça veut dire |
|---|---|
| **Dépôt** (*repository*, *repo*) | Le dossier de ton projet, suivi par git |
| **git** | Le logiciel qui garde l'historique de chaque modification de tes fichiers |
| **Sauvegarde git** (*commit*) | Une photo de ton projet à un instant donné, avec une phrase qui dit ce qui a changé |
| **Envoyer sur GitHub** (*push*) | Copier tes sauvegardes git sur le site GitHub, à l'abri si ton PC tombe en panne |
| **Récupérer** (*pull*) | Faire l'inverse : ramener sur ton PC la dernière version qui est sur GitHub |
| **Serveur** (*backend*) | La partie invisible de l'application : elle calcule, vérifie, lit et écrit dans la base |
| **Écrans** (*frontend*) | La partie visible : les pages et les boutons, dans le navigateur |
| **Base de données** | L'endroit où les données sont rangées, en tableaux (des « tables ») |
| **Table** | Un tableau de la base. Exemple : la table `salle`, une ligne par salle |
| **MLD** (modèle logique de données) | Le dessin des tables et des liens entre elles, **avant** de les créer |
| **Script SQL** | Le fichier qui crée ou modifie réellement les tables |
| **Conteneur** (*Docker*) | Une petite machine virtuelle prête à l'emploi : un conteneur pour la base, un pour le serveur, un pour les écrans. Rien d'autre à installer sur ton PC |
| **Lot** | Un morceau de développement assez petit pour être fini, testé et sauvegardé en une séance |
| **Test automatique** | Un petit programme qui vérifie tout seul qu'une règle est bien respectée, en quelques secondes |
| **Hébergeur** | L'entreprise qui loue l'ordinateur sur lequel ton site tournera en ligne |
| **VPS** (serveur privé virtuel) | Un ordinateur distant loué chez un hébergeur, qui t'est réservé |
| **Artifact** | Une page web que Claude publie pour te montrer un schéma ou une maquette cliquable |

---

## Étape 1 — Installer ton poste

À faire **une seule fois** par ordinateur. Tout est gratuit, sauf l'abonnement Claude.

### 1.1 Les outils à installer (Windows)

| Outil | À quoi il sert | Où le trouver | Point d'attention |
|---|---|---|---|
| **VS Code** | L'éditeur dans lequel tu travailles avec Claude | code.visualstudio.com | Installation par défaut |
| **Git pour Windows** | Garde l'historique de tes fichiers | git-scm.com | Garder toutes les options par défaut |
| **Docker Desktop** | Fait tourner base, serveur et écrans sans rien installer d'autre | docker.com/products/docker-desktop | Demande d'activer **WSL 2** (une fonction de Windows) : accepter, puis redémarrer le PC |
| **Extension Claude Code** | Claude directement dans VS Code | Dans VS Code : icône « Extensions » (carrés à gauche), chercher « Claude Code », Installer | Il faut un abonnement Claude (Pro ou Max) |
| **Compte GitHub** | La copie de secours de ton projet, en ligne | github.com, bouton « Sign up » | Noter ton identifiant et ton adresse |
| **Extension « VsCode Action Buttons »** (facultatif) | Des boutons cliquables en bas de VS Code : ▶ Démarrer, 💾 Sauver… | Même recherche que pour Claude Code | Voir l'étape 11 |
| **Notion** (facultatif) | Un tableau de suivi plus joli que le fichier texte | notion.so | Voir l'étape 9 |

### 1.2 Vérifier que tout marche

Dans VS Code, ouvre un terminal (menu **Terminal → Nouveau terminal**) et tape ces trois lignes, une par une :

```
git --version
docker --version
claude --version
```

Chacune doit afficher un numéro de version. Si l'une affiche « n'est pas reconnu », l'outil n'est pas installé ou VS Code doit être redémarré.

### 1.3 Donner ton identité à git (une seule fois)

```
git config --global user.name "<Ton Nom>"
git config --global user.email "<ton-adresse@exemple.fr>"
```

*Pourquoi : sans ça, la première sauvegarde git échoue avec un message incompréhensible.*

**Astuce.** Sur Teorem, un script `INSTALLATION-POSTE.ps1` installe ou met à jour tous ces outils d'un coup sur un nouveau PC. Demande à Claude d'en faire un pour ton projet dès que tu as un deuxième ordinateur.

---

## Étape 2 — Créer le projet

### 2.1 Le dossier et la sauvegarde GitHub

1. Crée un dossier, par exemple `T:\Projets\Salles`.
2. Dans VS Code : **Fichier → Ouvrir le dossier** → choisis-le.
3. Sur github.com : bouton **New** (nouveau dépôt) → nom `salles` → coche **Private** (privé) → **Create repository**.
4. Dans le panneau Claude Code, écris : *« Relie ce dossier au dépôt GitHub `<adresse du dépôt>` et fais une première sauvegarde. »*

### 2.2 L'arborescence de la documentation

Demande à Claude de créer cette arborescence **vide**, puis remplis-la au fil des étapes :

```
<projet>/
├── CLAUDE.md                     ← les consignes que Claude lit à CHAQUE conversation
├── MEMO.md                       ← tes 4 seuls gestes (étape 11)
└── .doc/
    ├── REGLES-PROJET.md          ← copie de CLAUDE.md (voir plus bas)
    ├── PRESENTATION.md           ← ce que fait le projet (étape 3)
    ├── SUIVI_REGLES_METIER.md    ← où en est l'écriture des règles (étape 5)
    ├── PLAN-DEV.md               ← l'ordre de construction (étape 7)
    ├── SUIVI-DEV.md              ← le tableau des lots + le journal (étape 9)
    ├── INVARIANTS-TRANSVERSES.md ← la liste à vérifier à la fin de chaque lot (étape 8)
    ├── PROMPT-TYPE-LOT.md        ← les phrases à copier pour lancer un lot (étape 8)
    ├── regles-metier/
    │   ├── GLOSSAIRE-METIER.md   ← le vocabulaire (étape 3)
    │   └── RM-<SUJET>.md         ← une règle métier par sujet (étape 5)
    ├── ihm/
    │   └── RM-<ECRAN>-IHM.md     ← un fichier par écran (étape 6)
    └── technique/
        ├── CHARTE-VISUELLE.md    ← couleurs, boutons (étape 6)
        ├── CONVENTIONS-IHM.md    ← règles valables pour tous les écrans (étape 6)
        └── <SUJET>.md            ← hébergement, sécurité, stockage… (étape 4)
```

**Pourquoi un double de `CLAUDE.md` dans `.doc/` :** si un jour il faut tout reconstruire, le dossier `.doc/` seul doit suffire. Règle : **toute modification de `CLAUDE.md` est recopiée dans `.doc/REGLES-PROJET.md` dans la même sauvegarde git.**

### 2.3 Le fichier `CLAUDE.md`

C'est le fichier le plus important du projet. Claude Code le lit automatiquement au début de **chaque** conversation. Tout ce que tu veux qu'il respecte toujours va dedans.

Copie le **modèle A** (partie « Modèles ») et remplis-le. Il contient déjà toutes les règles de travail de cette méthode.

**Règle d'or.** Chaque fois que tu corriges Claude sur sa façon de travailler (« tu n'es pas précis », « demande-moi avant de supprimer »…), dis-lui : **« écris cette règle dans CLAUDE.md »**. Sinon, la prochaine conversation refera la même erreur.

---

## Étape 3 — Décrire le projet

But : que toi, Claude et toute personne qui arrive sur le projet parlent de la même chose avec les mêmes mots.

### 3.1 La fiche de présentation (`.doc/PRESENTATION.md`, modèle B)

Réponds à ces 7 questions, en phrases simples :

1. **À quoi sert l'application ?** (une phrase)
2. **Qui l'utilise ?** Chaque type d'utilisateur, avec ce qu'il vient y faire.
3. **Quels sont les grands objets manipulés ?** (salle, réservation, adhérent…)
4. **Quelles actions principales ?** (réserver, annuler, payer…)
5. **Ce que l'application ne fera PAS** (au moins 3 points).
6. **Contraintes connues** : lois (données personnelles, factures), pays, langues, téléphone ou ordinateur.
7. **Existe-t-il déjà un outil** (tableur, ancien logiciel) ? Que garder, que jeter ?

Exemple « Salles » :
- *Qui l'utilise ?* « Le **gestionnaire** de l'association crée les salles et fixe les prix. L'**adhérent** réserve une salle et paie en ligne. »
- *Ce qu'elle ne fera pas* : « pas de gestion de la comptabilité de l'association ; pas d'application à installer, seulement un site ; pas de location à des non-adhérents. »

**Astuce.** Tu peux faire ce premier jet en discutant avec n'importe quelle IA. Mais considère ce résultat comme un **brouillon à interroger**, jamais comme une décision (voir l'étape 5).

### 3.2 Le glossaire (`.doc/regles-metier/GLOSSAIRE-METIER.md`, modèle C)

Un mot = une définition = un seul sens dans tout le projet.

- Exemple Teorem : « **Client** = celui qui paie la location. **Conducteur** = celui qui conduit. Un conducteur est toujours un client de type personne, mais un client n'est pas toujours conducteur (une entreprise paie, son salarié conduit). »
- Exemple « Salles » : « **Réservation** = une salle bloquée pour un créneau. **Location** = une réservation payée. » Si tu ne tranches pas, Claude utilisera les deux mots au hasard.

*Pourquoi : un même mot employé pour deux choses différentes finit en deux tables mélangées, et c'est très coûteux à défaire.*

---

## Étape 4 — Choisir l'hébergeur, puis les outils

**Dans cet ordre.** Les outils que tu choisis doivent pouvoir tourner chez ton futur hébergeur. Si tu choisis d'abord les outils, tu risques de découvrir au moment de la mise en ligne que ton hébergeur ne les accepte pas.

### 4.1 Quel type de projet ?

| Ton projet | Il te faut | Hébergeurs possibles |
|---|---|---|
| **Site vitrine** (pages d'information, pas de compte, pas de données saisies) | Seulement des écrans | Cloudflare Pages, Netlify, GitHub Pages (souvent gratuits) |
| **Application** (comptes, données enregistrées, règles de calcul) | Écrans + serveur + base de données | Un **VPS** (OVH, Scaleway, Hetzner…) ou une plateforme qui accepte Docker et PostgreSQL |

« Salles » et Teorem sont des **applications** : il faut un serveur qui tourne en permanence et une base qui garde ses données.

### 4.2 Les questions à poser à un hébergeur

Avant de choisir, vérifie ces 5 points sur son site (ou demande à Claude de les vérifier **à la date du jour**, les offres changent vite) :

1. Accepte-t-il les **conteneurs Docker**, sans restriction ?
2. Peut-il faire tourner une base **PostgreSQL** qui **garde ses données** après un redémarrage ?
3. Où sont ses serveurs ? (La France ou l'Union européenne simplifient la loi sur les données personnelles.)
4. Propose-t-il un **stockage de fichiers** (photos, documents) compatible « S3 » ?
5. Combien ça coûte par mois, pour un petit site ?

**Exemple : Cloudflare.** Il héberge très bien la partie écrans, qui n'est qu'un ensemble de fichiers. Mais il n'offre pas de base PostgreSQL permanente, et ses conteneurs sont effacés à chaque redémarrage. Il ne convient donc pas pour une application complète comme Teorem. Il peut en revanche se placer **devant** ton VPS pour accélérer l'affichage dans les pays lointains (c'est un « CDN »).

**Exemple : un VPS OVH ou Scaleway.** C'est un ordinateur complet qui t'est réservé : Docker s'y installe sans restriction. C'est le choix de Teorem : un serveur d'essai et un serveur de production chez OVH, environ 16 € HT par mois au total, nom de domaine compris.

**Règle de portabilité.** Utilise uniquement des briques standards (Docker, PostgreSQL, stockage S3). Tu pourras alors changer d'hébergeur en copiant tes données, sans réécrire le code.

### 4.3 Les outils proposés (ceux de Teorem)

Ils ne sont pas imposés. Ce sont les outils éprouvés sur Teorem, compatibles avec n'importe quel VPS :

| Rôle | Outil proposé | Pourquoi |
|---|---|---|
| Serveur | **Python + FastAPI** | Python est lisible pour un débutant ; FastAPI génère tout seul la liste de ce que le serveur sait faire |
| Écrans | **Vue 3 + TypeScript + Vite** | Un écran = un fichier ; TypeScript signale les fautes avant même de lancer |
| Style des écrans | **Tailwind CSS**, composants faits main | Aucune licence ni compte à renouveler. *Pourquoi : PrimeVue, essayé sur Teorem, demandait une licence annuelle.* |
| Base de données | **PostgreSQL** | Gratuit, solide, accepté partout |
| Lien serveur ↔ base | **SQLAlchemy 2** + pilote **psycopg (version 3)** | *Pourquoi pas `psycopg2` : il ne s'installe plus avec les versions récentes de Python.* |
| Fichiers (photos, PDF) | **MinIO** en local, stockage S3 de l'hébergeur en ligne | Le même code partout, seule la configuration change |
| Tout faire tourner | **Docker** (un conteneur par brique) | Rien à installer sur ton PC à part Docker ; identique en local et en ligne |
| Tests automatiques | **pytest** | L'outil standard de Python |
| Vérification dans le navigateur | **Playwright** | Un script qui clique dans l'application à ta place et prend des captures |

**Si tu choisis d'autres outils**, écris ta décision dans `.doc/technique/<SUJET>.md` avec le « pourquoi », et reporte-la dans la partie « Outils » de `CLAUDE.md`.

### 4.4 Deux pièges à éviter dès le premier jour

- **Les ports.** Chaque projet local utilise des « portes d'entrée » numérotées (5432 pour la base, 8000 pour le serveur, 5173 pour les écrans). Si deux projets tournent en même temps, ils se battent pour la même porte. Donne à chaque projet ses propres numéros (Teorem : 5433, 8001, 5174) et écris-les dans `CLAUDE.md`.
- **Les fichiers `.bat` (Windows) s'écrivent sans aucun accent.** *Pourquoi : un seul « é » dans un commentaire a fait afficher neuf messages d'erreur incompréhensibles sur Teorem.*

---

## Étape 5 — Écrire les règles métier

Une **règle métier** dit ce que l'application doit faire, en langage courant, sans code. Exemple : « une salle ne peut pas être réservée deux fois sur le même créneau ».

### 5.1 La démarche

1. **Découpe le projet en sujets.** « Salles » : adhérents, salles, créneaux et fermetures, réservations, paiements, annulations. Liste-les dans `SUIVI_REGLES_METIER.md` (modèle D), avec le statut « à faire ».
2. **Un sujet à la fois.** Dis à Claude : *« On traite le sujet Réservations. Interroge-moi. »*
3. **Claude pose ses questions**, par petits groupes de 3 ou 4, sous forme de choix (A / B / autre) avec les conséquences de chaque réponse.
4. **Tu réponds.** Tu as le droit de dire « je ne sais pas, propose-moi » : Claude donne alors sa recommandation et pourquoi.
5. **Claude écrit le fichier `RM-<SUJET>.md`** (modèle E). Tu le relis.
6. **Tu valides** → statut « validé et formalisé » dans `SUIVI_REGLES_METIER.md`.

### 5.2 Ce que doit contenir une bonne règle

- **La règle** elle-même, sans ambiguïté.
- **Au moins 2 exemples concrets**, avec de vraies valeurs.
- **Le « pourquoi »** en une ligne quand il n'est pas évident.
- **Les cas limites**, tranchés.
- **Les questions encore ouvertes**, listées clairement.

Exemple « Salles », règle d'annulation :
> **Annulation par l'adhérent.** Remboursement intégral jusqu'à 48 h avant le début, rien ensuite.
> - Réservation du samedi 14/03 à 10 h, annulée le jeudi 12/03 à 9 h (49 h avant) → remboursée en totalité.
> - Même réservation, annulée le jeudi 12/03 à 11 h (47 h avant) → aucun remboursement.
> **Pourquoi :** en dessous de 48 h, la salle ne peut plus être relouée.
> **Cas limite tranché :** l'heure qui compte est celle de la réception de l'annulation par le serveur, pas celle affichée sur le téléphone de l'adhérent.

### 5.3 Règles d'écriture

- **Les vocabulaires distincts restent distincts.** Exemple Teorem : *désactiver* (réversible), *clôturer* (définitif), *supprimer* (interdit dès que l'objet a servi). Décide ces trois cas pour chaque objet.
- **Les valeurs qui deviennent contractuelles sont figées.** Un prix, un taux de TVA, une caution : on les recopie au moment où ils engagent quelqu'un, on ne les recalcule jamais plus tard à partir du tarif du moment.
  *Pourquoi : si l'association augmente ses prix en juin, une réservation payée en mai ne doit pas changer de prix.*
- **Rien de « en dur » qui varie selon le pays, le client ou le temps** (taux de TVA, délais légaux…) : ce sont des réglages.
- **Un brouillon d'une autre IA n'est jamais une règle.** C'est un point de départ à interroger, sujet par sujet.
- **La règle fait foi, pas le code.** Pour modifier l'application, on modifie d'abord la règle, puis le code. On ne déduit jamais une règle en lisant le code.
- **Datation.** Chaque décision importante porte sa date (« décidé le 12/03/2027 »). Elle sert à savoir laquelle de deux consignes contradictoires est la plus récente.

---

## Étape 6 — Écrire les règles d'interface

Trois niveaux de fichiers, du plus général au plus précis.

### 6.1 La charte visuelle (`.doc/technique/CHARTE-VISUELLE.md`)

Couleurs, polices, formes des boutons, couleurs des statuts. **On la décide en regardant, pas en lisant** : demande à Claude une **maquette cliquable** (un *Artifact*) et corrige-la jusqu'à ce qu'elle te plaise. Une fois validée, Claude la recopie dans le fichier.

### 6.2 Les conventions d'interface (`.doc/technique/CONVENTIONS-IHM.md`, modèle F)

Les règles valables pour **tous** les écrans. Voici celles de Teorem, à reprendre telles quelles, car elles sont nées de vrais problèmes :

| Règle | Pourquoi |
|---|---|
| **Un clic produit toujours quelque chose de visible, à l'endroit du clic** : l'action, ou un message qui dit pourquoi elle est refusée | Sur Teorem, une confirmation s'affichait tout en bas de la page, hors de l'écran ; Lionel a cru pendant 2 jours qu'il n'avait pas le droit de supprimer |
| **Un bouton interdit reste visible, grisé, avec un cadenas et une bulle qui explique pourquoi et quoi faire** | Un bouton qui disparaît n'explique rien |
| **Jamais de fenêtre du navigateur** (`alert`, `confirm`, grise avec l'adresse du site) : toujours une fenêtre propre à l'application | Aspect peu professionnel, et impossible à mettre en forme |
| **Chaque écran marche sur 4 formats** : ordinateur, tablette, téléphone debout, téléphone couché. Menu en « burger » (☰) sous 768 pixels de large | Sur Teorem, une page parfaite sur ordinateur était écrasée sur téléphone |
| **Un seul composant par élément répété** (bouton, champ, tableau, fenêtre) | Pour changer le style du bouton « Enregistrer » à un seul endroit, et non dans 40 écrans |
| **Une action = un bouton**, jamais un lien souligné | Un lien se confond avec du texte |
| **Rubrique obligatoire = astérisque**, et c'est la base de données qui décide ce qui est obligatoire, pas l'écran | Sinon l'écran et la base se contredisent |
| **Un pied de fenêtre avec des boutons « Suivant » ne bouge jamais en hauteur** d'une étape à l'autre | Sinon le doigt rate le bouton au 3ᵉ « Suivant » |
| **Le curseur se place tout seul dans le premier champ** d'une ligne qu'on vient d'ajouter | Un clic de moins, à chaque fois |

### 6.3 Un fichier par écran (`.doc/ihm/RM-<ECRAN>-IHM.md`, modèle G)

**Obligatoire pour tout écran**, écrit dès sa première version. Il décrit :
- la disposition générale ;
- l'**ordre exact des champs** et des colonnes ;
- le **libellé et la place de chaque bouton** ;
- les états : chargement, vide, erreur, lecture, modification ;
- ce qui est propre à cet écran (tri par défaut, filtres, comportements).

**Règle : toute retouche visible par l'utilisateur met à jour ce fichier dans la même sauvegarde git.** Un libellé changé, un champ déplacé, un message d'erreur reformulé : tout compte.
*Pourquoi : sur Teorem, plusieurs écrans avaient été retouchés sans mise à jour du fichier, et leur description ne correspondait plus à rien.*

### 6.4 Construire l'interface en même temps que le serveur

Dès que la structure de données d'un écran est prête, on construit l'écran. On n'attend pas que tout le serveur soit fini.
*Pourquoi : l'interface compte autant que les fonctions. La découvrir à la fin, c'est découvrir trop tard qu'elle ne convient pas.*

### 6.5 Avant toute nouvelle maquette

Claude **relit d'abord les composants déjà construits** et la charte. Il ne réinvente jamais un bouton ou un style déjà validé.
*Pourquoi : sur Teorem, une maquette entière a été refaite parce que ses boutons ne ressemblaient pas à ceux de l'application.*

---

## Étape 7 — Faire le plan de développement

### 7.1 Construire dans l'ordre des dépendances, pas dans l'ordre des écrans

On commence par ce dont tout le reste dépend. On range les sujets en **niveaux** :

| Niveau | Contenu type | Exemple « Salles » |
|---|---|---|
| 0 — Amorçage | Conteneurs, connexion à la base, squelette de tests | — |
| 1 — Fondations | Connexion des utilisateurs, rôles, journal des actions | Comptes, rôles gestionnaire/adhérent |
| 2 — Objets communs | Ce que tous les modules utilisent | Adhérents, documents |
| 3 — Cœur | L'objet principal du projet | Salles, créneaux, tarifs |
| 4 — L'action principale | Ce pour quoi l'application existe | Réservations |
| 5 — Argent | Paiements, factures | Paiement en ligne, reçus |
| 6+ — Le reste | Statistiques, services avancés | Statistiques d'occupation |

**Les erreurs qui obligent à tout réécrire :** construire les écrans avant les règles ; la base avant le MLD validé ; les factures (PDF) avant les objets qu'elles décrivent ; la partie publique avant le moteur métier.

### 7.2 Découper en lots

Chaque niveau est découpé en **lots numérotés** (`1.1`, `1.2`…). Un lot :
- est de type **Serveur** (*Backend* : tables + calculs + tests) ou **Écrans** (*Frontend* : pages et fenêtres) ;
- tient en **une séance** et **une sauvegarde git** ;
- cite le fichier de règles dont il vient ;
- indique de quels lots il dépend : **on ne démarre un lot que si ses dépendances sont terminées.**

Exemples « Salles » :
- **Lot 3.1 — Serveur — Salles** : table `salle` (nom, capacité, prix de l'heure), ajout/modification/suppression, tests. Source : `RM-SALLES.md`. Dépend de : 1.3.
- **Lot 3.2 — Écrans — Liste des salles et fiche salle**. Source : `RM-SALLES.md`. Dépend de : 3.1.

Claude écrit le plan dans `PLAN-DEV.md` (modèle H) et le tableau des lots dans `SUIVI-DEV.md` (modèle I). Tu relis l'ordre et tu valides.

---

## Étape 8 — Développer, lot par lot

### 8.1 Lancer un lot

Copie la phrase de démarrage du modèle J (`PROMPT-TYPE-LOT.md`) dans Claude Code, en remplaçant le numéro du lot. Un lot = une conversation. Entre deux lots sans rapport, tape `/clear` pour repartir d'une conversation vide.

### 8.2 L'ordre imposé pour toute modification de données

1. **Claude propose un MLD**, jamais de script SQL à ce stade. Tu le valides (voir 8.3).
2. **Claude écrit le script SQL** (`schema_v<N>.sql`) : traduction exacte du MLD validé.
3. **Le script est exécuté à la main**, par toi ou par Claude avec ton accord. Jamais par le code tout seul.
4. **Claude met à jour les « modèles »** : un simple miroir des colonnes dans le code, aucun calcul dedans.
5. **Claude écrit les calculs** dans des fichiers séparés (dossier `services/`).
6. **Claude écrit les routes** : les adresses que les écrans appellent.
7. **Claude écrit les tests** à partir des règles métier.

**Les scripts `schema_v*.sql` sont numérotés et jamais modifiés une fois exécutés.** Pour corriger, on écrit le suivant (`schema_v12.sql` corrige `schema_v11.sql`).
*Pourquoi : on peut toujours savoir dans quel ordre la base a été construite, et la reconstruire.*

### 8.3 Le format du MLD (ce que tu dois recevoir)

- Un **schéma graphique** publié en *Artifact* : une boîte par table, des flèches entre les tables. Pas une liste de texte.
- Dans chaque boîte : le **nom de la table en MAJUSCULES**, puis uniquement `id (PK)` et les liens `xxx_id (FK)`. PK = l'identifiant unique de la ligne ; FK = le numéro d'une ligne d'une autre table.
- Les autres rubriques (nom, prix…) sont listées **à côté** du schéma. Si tu veux tout voir dans les boîtes, demande le « MLD complet ».
- Sur chaque flèche, les **cardinalités** : `(1,1)` un et un seul · `(0,1)` zéro ou un · `(0,n)` zéro ou plusieurs · `(1,n)` au moins un.
- Fond blanc uni, et une légende.
- **Au moins 2 exemples de vraies lignes**, chacun traduit en français.

Exemple « Salles » :
> `SALLE (id)` ← `(0,n)` — `(1,1)` → `RESERVATION (id, salle_id, adherent_id)`
> - Ligne 1 : réservation n° 12 → salle n° 3 (« Salle des fêtes »), adhérent n° 45 (Julie Martin). **Traduction :** Julie a réservé la salle des fêtes.
> - Ligne 2 : réservation n° 13 → salle n° 3, adhérent n° 45. **Traduction :** Julie a réservé la même salle une deuxième fois, à une autre date. Une salle peut donc avoir plusieurs réservations, mais une réservation porte sur une seule salle.

### 8.4 Quand le lot est-il terminé ?

**Lot Serveur — 7 cases :**
1. SQL écrit et **validé par toi**
2. Modèles à jour (miroir des colonnes)
3. Routes écrites
4. Tests automatiques qui passent
5. **Test de fiche** si le lot crée ou modifie une fiche (voir 8.5)
6. Test à la main dans l'application
7. Sauvegarde git

**Lot Écrans — 4 cases :**
1. Écran construit selon `CONVENTIONS-IHM.md` et la charte
2. Branché sur les vraies routes (jamais de fausses données)
3. Test à la main, sur les 4 formats d'écran
4. Sauvegarde git, avec le fichier `RM-<ECRAN>-IHM.md` à jour

**Et pour tous les lots :** Claude repasse la liste `INVARIANTS-TRANSVERSES.md` (modèle K), point par point, et dit pour chacun s'il est respecté ou pourquoi il ne s'applique pas.

### 8.5 Le test de fiche

Chaque fiche (adhérent, salle, réservation…) a un test qui refait son cycle complet, dans cet ordre :
1. **Ajout**, toutes les rubriques remplies, puis relecture.
2. **Modification** de toutes les rubriques, puis relecture et comparaison une à une.
3. Pour chaque **fiche liée** (ex. une pièce jointe) : ajout, modification, **tentative de suppression de la fiche principale, qui doit être refusée**, puis suppression de la fiche liée.
4. **Suppression de la fiche principale**, désormais possible.

**La liste des rubriques n'est jamais écrite à la main dans le test** : elle est lue automatiquement dans le code. Une rubrique ajoutée entre donc toute seule dans le test.
*Pourquoi : une liste écrite à la main vieillit sans que personne ne s'en aperçoive.*

### 8.6 Réutiliser au lieu de recopier

Dès qu'un même calcul, style ou comportement apparaît **une deuxième fois**, Claude le regroupe tout de suite à un seul endroit. On n'attend pas « un grand ménage plus tard ».
Exception : deux fonctions au même nom mais qui ne font pas la même chose ne se fusionnent pas.

---

## Étape 9 — Suivre l'avancement

### 9.1 Les 4 états d'un lot

| État | Symbole | Qui le met | Quand |
|---|---|---|---|
| À faire | ⬜ | — | Au départ |
| En cours | 🟡 | Claude | Au démarrage du lot |
| À vérifier | 🔎 | Claude | Quand toutes les cases de 8.4 sont cochées |
| Fait | ✅ | **Toi seul** | Après avoir testé toi-même et dit « je valide » |

**Claude ne met jamais « Fait » tout seul.** Si tu ne dis pas clairement que tu valides, il te pose la question.
*Pourquoi : « Claude a fini » et « j'ai vérifié » sont deux choses différentes. Sur Teorem, des lots marqués « Fait » n'avaient jamais été relus.*

### 9.2 Où se trouve le suivi

- **`.doc/SUIVI-DEV.md`** (la référence) : le tableau des lots par niveau, puis le **journal**.
- **Le journal** : une entrée par séance, qui donne la date, le lot, ce qui a été fait, les **décisions prises et pourquoi**, et les problèmes rencontrés. Une entrée datée n'est jamais réécrite après coup.
- **Notion** (facultatif) : une base avec une ligne par lot et une colonne « Statut » (À faire / En cours / À vérifier / Fait). Claude la met à jour **en même temps** que le fichier. Si Notion n'est pas accessible, le fichier suffit, et Claude te le signale.
- **`.doc/SUIVI_REGLES_METIER.md`** : même principe, mais pour l'écriture des règles (étape 5).

### 9.3 Le journal ne remplace jamais le fichier de règles

Une décision prise en cours de lot va **dans son fichier de règles** (`RM-*.md` ou `RM-*-IHM.md`). Le journal n'en garde que l'histoire : la date et le pourquoi.
*Pourquoi : le journal de Teorem dépasse 7 000 lignes. Personne ne peut y retrouver comment un écran doit être aujourd'hui.*

---

## Étape 10 — Protéger tes données pendant les tests

À mettre en place **dès le premier lot**, pas après le premier accident.
*Pourquoi : sur Teorem, des données de test se sont mélangées aux vraies à trois reprises (161 établissements de test en une seule fois). Une consigne ne suffit pas : il faut que le code refuse.*

### 10.1 Une base de test séparée

- Deux bases dans le même conteneur : **`<projet>_db`** (tes données) et **`<projet>_test_db`** (vide, même structure).
- Un seul fichier pour lancer les tests : **`lancer-tests.bat`**. Il vérifie que la base de test a la même structure que la vraie, la recrée si besoin, puis lance les tests dessus.
- **Garde-fou dans le code** : les tests refusent de démarrer s'ils visent une autre base que la base de test.
- La base de test est **vidée au début** de chaque série de tests, pas à la fin : une série interrompue ne laisse ainsi jamais de désordre, et les données du dernier échec restent consultables.

### 10.2 Deux comptes pour la base

| Compte | Utilisé par | Droits |
|---|---|---|
| `<projet>_user` (administrateur) | Toi et Claude, pour créer les tables et inspecter | Tous |
| `<projet>_app` (application) | Le serveur et les tests | Lire et écrire les données, **jamais** créer ou supprimer une table |

*Pourquoi : si le serveur a un défaut, il ne peut pas détruire la structure de la base. Et les tests sont toujours lancés avec le compte application, sinon ils ne vérifient pas les vraies protections.*

### 10.3 Ce qui est saisi à la main dans l'application

Quand Claude (ou toi) essaie un écran, les données vont forcément dans la vraie base. On les **marque dès la création** :

| Donnée | Marque | Exemple |
|---|---|---|
| Personne, adresse e-mail | domaine **`@example.com`** (réservé, jamais une vraie adresse) | `adherent.test@example.com` |
| Nom d'organisation, de lieu | préfixe **`ZZTEST `** (se range en fin de liste) | `ZZTEST Salle du fond` |
| Code, numéro | préfixe **`ZZ-`** | `ZZ-001` |

Puis un fichier **`nettoyer-donnees-test.bat`** qui fait d'abord une sauvegarde, puis classe chaque ligne en trois groupes :
- **Protégée** (liste de tes vraies données, tenue à jour) : jamais touchée ;
- **Marquée test** : supprimée après ta confirmation ;
- **Inconnue** : seulement signalée, **jamais supprimée**.

### 10.4 Règles absolues pour Claude

- **Ne jamais supprimer une donnée existante sans ton accord explicite**, même si elle a l'air d'un test.
  *Pourquoi : sur Teorem, un vrai client a disparu, effacé par une session qui préparait des données de test.*
- Un script qui clique dans l'application (Playwright) **ne touche que les lignes qu'il a lui-même créées et marquées**.
- À la fin d'une tâche, **vérifier par un comptage** qu'il ne reste aucune donnée de test, au lieu d'écrire « c'est nettoyé » sans l'avoir vérifié.
- Mot de passe de tous les comptes de test : **`123`**.

### 10.5 Les sauvegardes

- **`sauver.bat`** : exporte la base et les fichiers dans un dossier dédié, puis fait une sauvegarde git et l'envoie sur GitHub.
- **`restaurer_base.bat`** : remplace la base locale par la dernière sauvegarde (utile pour passer d'un PC à l'autre).
- La base de test n'est jamais sauvegardée : elle se reconstruit toute seule.

---

## Étape 11 — Travailler avec Claude au quotidien

### 11.1 Tes gestes (à recopier dans `MEMO.md`, modèle L)

| Tu veux… | Tu fais |
|---|---|
| Reprendre là où tu t'étais arrêté | Tu écris **`continuer`** (ou `reprends`). Dans la même conversation, Claude finit ce qu'il était en train de faire. Dans une nouvelle, il relit « Travail en cours » puis le suivi, et repart de là. S'il hésite entre deux choses, il te demande laquelle |
| Lancer l'application | Bouton **▶ Démarrer** (ou double-clic sur `demarrer.bat`) |
| Sauvegarder | Bouton **💾 Sauver** (ou `sauver.bat`) |
| Laisser Claude avancer seul sur plusieurs lots | **« Fais les lots 3.1 à 3.4, tout seul »** : aucune question en cours de route, il décide selon les règles, note chaque décision dans le journal et te remet un **bilan** à la fin avec les questions restantes |
| Finir la journée proprement | **`dodo`** : Claude relit le code, vérifie que les règles écrites correspondent au code, lance tous les tests, met le suivi à jour, sauvegarde et envoie sur GitHub |

Les boutons en bas de VS Code s'obtiennent avec l'extension « VsCode Action Buttons » : demande à Claude de les configurer.

### 11.2 Ce que tu peux exiger de Claude (déjà écrit dans le modèle A)

- **Tout en français simple.** Un mot anglais inévitable est suivi de son explication entre parenthèses.
- **Des questions compréhensibles seules** : la situation concrète (vrais noms, vrais numéros), ce qui se passe pour chaque réponse, une seule décision par question, sous forme de choix.
- **Au moins 2 exemples concrets** pour toute notion un peu abstraite.
- **Du détail fichier par fichier** pour tout changement de configuration : la ligne avant, la ligne après, et les fichiers qui ne changent pas.
- **Pendant le travail, 1 ou 2 lignes d'information seulement.** Le détail vient à la fin, dans le résultat.
- **Toutes tes questions ont une réponse** avant qu'il t'en pose une nouvelle.
- **Diagnostiquer avant de conclure** : quand tu dis « ça ne marche pas », il vérifie quel compte est connecté et si ta demande est bien arrivée au serveur, avant de proposer une cause.
- **Pour un outil que tu nommes** (« Claude Design », « Notion »…), il vérifie ce que fait vraiment cet outil, et il ne le remplace pas par un autre sans te le dire.

### 11.3 La mémoire de Claude

En plus de `CLAUDE.md`, Claude Code tient une **mémoire personnelle** sur ton PC, hors du projet. Quand tu lui dis « retiens que… », il y écrit une fiche. Règle simple :
- ce qui concerne **le projet** (règles, conventions) → `CLAUDE.md` ou un fichier `.doc/`, **sauvegardé sur GitHub** ;
- ce qui concerne **ta façon de travailler** (préférences, habitudes) → la mémoire.

*Pourquoi : la mémoire reste sur un seul PC. Ce qui est dans le dépôt suit le projet partout.*

---

## Étape 12 — Mettre en ligne

À faire quand l'application tourne correctement en local. Demande à Claude un plan écrit dans `.doc/technique/DEPLOIEMENT.md`, sur ce modèle (celui de Teorem) :

| Partie | Qui | Contenu |
|---|---|---|
| A. Comptes et achats | **Toi** | Compte chez l'hébergeur, nom de domaine, commande du serveur, service d'envoi d'e-mails. Chaque clic est décrit |
| B. Préparer le code | Claude | Versions « production » des conteneurs, fichiers de réglages du serveur |
| C. Les adresses | **Toi** | Faire pointer ton nom de domaine vers le serveur (10 minutes) |
| D. Installer | Claude | D'abord un **serveur d'essai** (`staging.<domaine>`), jamais directement le vrai |
| E. Essayer | Toi et Claude | Tests automatiques sur le serveur, puis tes essais à la main |
| F. Production | Claude, avec tes contrôles | Le vrai site, avec des **sauvegardes automatiques** testées (une sauvegarde qu'on n'a jamais restaurée n'est pas une sauvegarde) |
| G. La vie courante | Toi et Claude | Comment publier une modification, que faire si ça casse, quoi surveiller, combien ça coûte |

Chaque étape indique clairement **« toi »** ou **« moi (Claude) »**.

---

## Récapitulatif : la journée type

1. Ouvrir VS Code sur le projet, cliquer **▶ Démarrer**.
2. Écrire **`continuer`**.
3. Claude annonce le lot suivant et en propose le plan (et le MLD si des tables changent).
4. Tu valides, ou tu corriges.
5. Claude construit, teste et met le lot à « 🔎 À vérifier ».
6. Tu essaies dans l'application. Si ça te va : « je valide », et le lot passe à ✅.
7. En fin de journée : **`dodo`**.

---
---

# MODÈLES À COPIER

Remplace tout ce qui est entre `<chevrons>`. Supprime les lignes qui ne concernent pas ton projet.

---

## Modèle A — `CLAUDE.md`

````markdown
# <NOM DU PROJET> — Consignes pour Claude Code

> Ce fichier est dupliqué dans `.doc/REGLES-PROJET.md`. Toute modification ici est recopiée là-bas dans la même sauvegarde git.

## Démarrage du projet (à lire en premier, à chaque conversation)

Si `.doc/DEMARRAGE.md` existe et n'est pas marqué « Démarrage terminé » : le projet est en phase de démarrage. Lis `methode-projet.md` (partie 0) puis `.doc/DEMARRAGE.md`, et reprends à la question en attente ou à la prochaine action notée, quel que soit le premier message du développeur. Après chaque réponse, écris-la aussitôt dans le fichier concerné et dans `.doc/DEMARRAGE.md`.

## Langue et clarté (RÈGLE STRICTE)

- Réponds toujours en français simple, y compris dans les questions à choix, les titres et les messages de sauvegarde git.
- Un terme technique incontournable s'écrit d'abord en français, puis en anglais entre parenthèses avec une courte explication la première fois (ex. « enregistrer une sauvegarde dans git (un *commit*) »).
- Au moins 2 exemples concrets, avec de vraies valeurs, pour toute notion un peu abstraite.
- Changement d'infrastructure (Docker, base, configuration) : détail fichier par fichier, ligne avant / ligne après, et dire quels fichiers ne changent pas.
- Pendant le travail : 1 ou 2 lignes d'information au maximum. Le détail complet vient à la fin.
- Réponds à toutes mes questions avant de m'en poser une nouvelle.

## Questions (RÈGLE STRICTE)

- Une question se comprend sans relire le reste du message : situation concrète, vrais noms et vrais numéros.
- Sous forme de choix, avec pour chaque réponse ce qui se passera concrètement.
- Une seule décision par question.
- Si tu n'as pas compris une de mes phrases, cite-la mot pour mot et dis ce que tu n'y trouves pas.

## Qui utilise ce projet

<Prénom>, débutant en programmation. Explique le « pourquoi » de chaque choix technique. Il garde la main sur la structure de la base et sur tout ce qui touche à ses données ou à son ordinateur.

## Outils

- Serveur : <Python + FastAPI>
- Écrans : <Vue 3 + TypeScript + Vite + Tailwind CSS>, composants faits main
- Base : <PostgreSQL>, pilote <psycopg version 3>, <SQLAlchemy 2>
- Fichiers : <MinIO en local, stockage S3 en ligne>
- Tout tourne dans Docker : conteneurs <db>, <backend>, <frontend>, <minio>
- Ports côté PC : serveur <8001>, écrans <5174>, base <5433>
- Hébergement prévu : <hébergeur, pays>
- Les fichiers `.bat` s'écrivent sans aucun accent ni tiret long.

## Base de données

- Base principale : `<projet>_db` ; base des tests : `<projet>_test_db` (même conteneur)
- Compte administrateur : `<projet>_user` / `<mot de passe>` (création des tables, inspection)
- Compte application : `<projet>_app` / `<mot de passe>` (serveur et tests ; aucun droit de créer une table)

## Ordre imposé à chaque évolution de données

1. Proposer un MLD (jamais de SQL à ce stade) et attendre ma validation.
2. Écrire `schema_v<N>.sql` (jamais modifié une fois exécuté ; une correction = le numéro suivant).
3. Mettre à jour les modèles : miroir pur des colonnes, aucun calcul.
4. Calculs dans `services/`, puis schémas et routes, puis tests.
Jamais de création automatique des tables par le code.

## Format du MLD (RÈGLE STRICTE)

Artifact HTML avec un schéma Mermaid `flowchart` sur fond blanc uni. Nom de table en MAJUSCULES ; dans les boîtes, seulement `id (PK)` et `xxx_id (FK)` ; autres rubriques listées à côté. Flèches avec cardinalités Merise `(1,1)` `(0,1)` `(0,n)` `(1,n)`. Une légende. Au moins 2 exemples de vraies lignes traduits en français. Si je demande le « MLD complet », toutes les rubriques dans les boîtes.

## Données de test (RÈGLE STRICTE)

- Tests lancés uniquement par `lancer-tests.bat`, sur `<projet>_test_db`, avec le compte `<projet>_app`. Les tests refusent de démarrer sur une autre base.
- Données saisies à la main dans l'application : marquées dès la création (`@example.com`, `ZZTEST `, `ZZ-`), nettoyées par `nettoyer-donnees-test.bat`.
- Un script Playwright ne touche que les lignes qu'il a créées et marquées.
- Jamais de suppression d'une donnée existante ou ambiguë sans mon accord explicite.
- Fin de tâche : vérifier par un comptage qu'il ne reste aucune donnée de test.
- Mot de passe des comptes de test : `123`.

## Tests de fiche

Chaque fiche a son test dans `backend/tests/fiches/test_fiche_<nom>.py` : ajout → modification → fiches liées (suppression de la fiche principale refusée tant qu'un lien existe) → suppression. Rubriques lues automatiquement, jamais listées à la main.

## Interface

Lire `.doc/technique/CONVENTIONS-IHM.md` et `CHARTE-VISUELLE.md` avant tout écran. Chaque écran a son `.doc/ihm/RM-<ECRAN>-IHM.md`, mis à jour dans la même sauvegarde que toute retouche visible. Maquettes en Artifact cliquable, après relecture des composants existants.

## Réutilisation

Dès la 2ᵉ apparition d'une même logique ou d'un même style, la regrouper à un seul endroit.

## Suivi

- `.doc/SUIVI-DEV.md` (et Notion : base `<identifiant>`) : états ⬜ à faire / 🟡 en cours / 🔎 à vérifier / ✅ fait.
- Claude met « à vérifier », jamais « fait ». Seul <Prénom> passe un lot à « fait ». S'il ne le dit pas, lui demander.
- Fin de chaque lot : repasser `.doc/INVARIANTS-TRANSVERSES.md`.
- Règles métier : lire `.doc/SUIVI_REGLES_METIER.md` avant de répondre sur une règle.

## Mots-clés

- **« continuer » / « reprends »** : dans l'ordre, et s'arrêter à la première qui s'applique : 1) une tâche inachevée dans cette conversation → la finir ; 2) la rubrique « Travail en cours » de `.doc/SUIVI-DEV.md` n'est pas vide → la reprendre ; 3) démarrage non terminé → reprendre `.doc/DEMARRAGE.md` ; 4) sinon, dire où on en est et proposer le prochain lot. En cas de doute entre deux possibilités, me demander avec 2 choix (détail : `methode-projet.md` § 0.8).
- **« Travail en cours »** (en haut de `.doc/SUIVI-DEV.md`) : rempli dès qu'une tâche dépasse une action (lot ou retouche hors lot), mis à jour à chaque étape, vidé une fois la tâche finie et sauvegardée.
- **« tout seul »** : pour la tâche demandée, aucune question en cours de route. Décider selon les règles, noter chaque décision dans le journal de `SUIVI-DEV.md`, aller jusqu'au bout (lot à « à vérifier »), puis faire un bilan avec les questions restantes. Exception : ne jamais supprimer une donnée ambiguë.
- **« dodo »** : relire le code, vérifier que les règles écrites correspondent au code et corriger les écarts, lancer tous les tests, mettre à jour le suivi, sauvegarder dans git et envoyer sur GitHub, sans poser de question.

## Façon de travailler

Étape par étape, une action à la fois. Expliquer le pourquoi. Diagnostiquer avant de conclure (quel compte est connecté, la demande est-elle arrivée au serveur).
````

---

## Modèle B — `.doc/PRESENTATION.md`

```markdown
# <NOM DU PROJET> — Présentation

## À quoi sert l'application
<Une phrase.>

## Qui l'utilise
| Type d'utilisateur | Ce qu'il vient faire |
|---|---|
| <Gestionnaire> | <Crée les salles, fixe les prix, voit les réservations> |
| <Adhérent> | <Réserve une salle, paie, annule> |

## Les grands objets
<Salle, Créneau, Réservation, Paiement…> (définis dans GLOSSAIRE-METIER.md)

## Les actions principales
1. <…>

## Ce que l'application ne fera PAS
- <…>
- <…>
- <…>

## Contraintes connues
- Loi : <données personnelles, factures…>
- Pays / langues : <…>
- Appareils : <ordinateur, téléphone…>

## Outil existant
<Aucun / tableur / ancien logiciel : ce qu'on garde, ce qu'on jette.>
```

---

## Modèle C — `.doc/regles-metier/GLOSSAIRE-METIER.md`

```markdown
# Glossaire métier

Un mot = une définition = un seul sens dans tout le projet. Ce fichier ne décrit pas les tables : un objet peut s'étendre sur plusieurs tables.

## Les grands objets
<Liste.>

## <Objet 1>
<Définition en 2 à 4 phrases, puis ses liens avec les autres objets.>
Exemple : <cas concret.>
À ne pas confondre avec : <mot voisin, et la différence.>

## Cycle de vie (valable pour tous les objets)
- **Désactiver** : réversible.
- **Clôturer** : définitif.
- **Supprimer** : interdit dès que l'objet a servi.
```

---

## Modèle D — `.doc/SUIVI_REGLES_METIER.md`

```markdown
# Suivi de l'écriture des règles métier

À lire en premier avant toute discussion sur une règle.

## Méthode
1. Un sujet à la fois, par questions / réponses.
2. Sujet validé → écrit dans `regles-metier/RM-<SUJET>.md` (et `ihm/RM-<SUJET>-IHM.md` si besoin).
3. Tout brouillon venu d'une autre IA est un point de départ à interroger, jamais une décision.

## Statuts
à faire · à vérifier ou compléter · validé et formalisé

## Avancement
| # | Sujet | Statut | Fichier produit |
|---|---|---|---|
| 01 | <Utilisateurs et rôles> | à faire | — |
| 02 | <Salles> | à faire | — |

## Décisions en attente
- <Question ouverte, sujet concerné, date.>
```

---

## Modèle E — `.doc/regles-metier/RM-<SUJET>.md`

```markdown
# Règle métier — <Sujet>

## Objectif
<Ce que couvre ce fichier, en 2 lignes.>

## Principes
<Les règles générales.>

## <Règle 1> (décidé le <JJ/MM/AAAA>)
<La règle, sans ambiguïté.>
- Exemple 1 : <vraies valeurs> → <résultat>.
- Exemple 2 : <vraies valeurs> → <résultat>.
**Pourquoi :** <une ligne.>
**Cas limite tranché :** <…>

## Qui peut faire quoi
| Action | Qui | Condition |
|---|---|---|

## Désactivation / clôture / suppression
<Ce qui s'applique à cet objet.>

## Valeurs figées
<Ce qui est recopié au moment où ça engage quelqu'un.>

## Questions ouvertes
- <…>

## Références
- `GLOSSAIRE-METIER.md`, `RM-<autre>.md`
```

---

## Modèle F — `.doc/technique/CONVENTIONS-IHM.md`

```markdown
# Conventions d'interface — valables pour tous les écrans

Chaque écran a en plus son propre `ihm/RM-<ECRAN>-IHM.md` (obligatoire).

## RÈGLE ABSOLUE — un clic produit toujours quelque chose de visible, à l'endroit du clic
1. Le clic fait l'action, ou son étape intermédiaire s'affiche sans avoir à faire défiler.
2. S'il échoue, le message s'affiche là où l'utilisateur regarde.
3. S'il est interdit, le bouton reste visible, grisé, avec un cadenas et une bulle qui dit pourquoi et quoi faire.

## Structure des pages
<Menu à gauche, contenu à droite / autre.>

## Formats d'écran
Ordinateur, tablette, téléphone debout, téléphone couché. Sous 768 px : menu burger (☰). Un tableau trop large défile sur le côté au lieu d'écraser ses colonnes.

## Listes et tableaux
<Tri par défaut, filtres au-delà de 30 lignes, clic sur une ligne = ouvre la fiche.>

## Fenêtres
Jamais de fenêtre du navigateur (alert/confirm) : toujours la fenêtre de confirmation de l'application.
Un pied de fenêtre à boutons de navigation garde la même hauteur à chaque étape.

## Champs
Étiquette au-dessus. Obligatoire = astérisque, décidé par la base de données. Le curseur se place dans le premier champ d'une ligne ajoutée.

## Boutons
Une action = un bouton, jamais un lien souligné. Actions fréquentes à gauche, rares (supprimer) à droite.

## Composants communs
Un seul composant par élément répété (dossier `components/ui/`). Liste :
- `AppBouton` — <…>
```

---

## Modèle G — `.doc/ihm/RM-<ECRAN>-IHM.md`

```markdown
# <Écran> — Interface

> Fichiers : `<NomView.vue>`, `<NomPopup.vue>`. Construit au lot <X.Y>.

## Page <Nom>
**Ordre des éléments :**
1. En-tête : titre « <…> » à gauche, bouton [<+ Nouveau…>] à droite.
2. (chargement) « Chargement… »
3. (erreur) bandeau rouge avec le message du serveur
4. (vide) « <Aucun… pour l'instant.> »
5. Tableau

**Colonnes, dans cet ordre :** <…>
**Tri par défaut :** <…>
**Clic sur une ligne :** <…>

## Fenêtre « <Fiche…> »
**Rubriques, dans cet ordre :** <…> (* = obligatoire)
**Boutons :** <[Enregistrer] à gauche, [Supprimer] à droite…>
**États :** lecture / modification / erreur
**Particularités :** <… ou « applique strictement CONVENTIONS-IHM, rien de spécifique ».>
```

---

## Modèle H — `.doc/PLAN-DEV.md`

```markdown
# Plan de développement

## Principe
Ordre des dépendances, jamais ordre des écrans : du plus fondamental au plus spécifique. Serveur et écrans avancent ensemble : dès qu'une structure est prête, ses écrans se construisent.

## Pour chaque module
Règles validées → MLD validé → SQL → modèles → calculs (services) → routes → tests → écrans.

## Erreurs à ne jamais commettre
Écrans avant les règles ; base avant le MLD validé ; factures avant les objets qu'elles décrivent ; partie publique avant le moteur métier.

## Niveaux
**Niveau 0 — Amorçage** : conteneurs, connexion à la base, squelette de tests, base de test séparée.
**Niveau 1 — Fondations** : <connexion, rôles, journal des actions>. → `RM-<…>`
**Niveau 2 — Objets communs** : <…>
**Niveau 3 — Cœur** : <…>
**Niveau 4 — Action principale** : <…>
**Niveau 5 — Argent** : <…>
**Niveau 6 — Le reste** : <…>

## Transverses (tout au long du projet)
Sécurité, journal des actions, tests écrits à partir des règles.
```

---

## Modèle I — `.doc/SUIVI-DEV.md`

```markdown
# Suivi du développement — <NOM DU PROJET>

On avance lot par lot, dans l'ordre de `PLAN-DEV.md`. Un lot ne démarre que si ses dépendances sont ✅.

## Travail en cours (tenu à jour par Claude à chaque étape, vidé quand la tâche est finie)

- **Demande** : <mots du développeur, ex. « déplace le bouton Supprimer à droite sur la fiche salle »> — ou Lot <X.Y>
- **Commencé le** : <JJ/MM/AAAA>
- **Étapes** :
  - [x] <étape 1>
  - [ ] <étape 2>  ← on en est là
  - [ ] <étape 3>
- **Question en attente** : <texte exact, ou « aucune »>
- **En pause** : <autre tâche interrompue et l'étape où elle s'est arrêtée, ou « aucune »>

## Définition de « terminé »

**Lot Serveur (7 cases)** : 1. SQL validé par <Prénom> · 2. Modèles · 3. Routes · 4. Tests automatiques OK · 5. Test de fiche (si fiche) · 6. Test à la main · 7. Sauvegarde git
**Lot Écrans (4 cases)** : 1. Écran selon CONVENTIONS-IHM · 2. Branché sur les vraies routes · 3. Test à la main sur 4 formats · 4. Sauvegarde git + `RM-<ECRAN>-IHM.md` à jour
**Tous les lots** : `INVARIANTS-TRANSVERSES.md` repassé.

Toutes les cases cochées → 🔎 à vérifier (jamais ✅ directement). ✅ seulement quand <Prénom> a vérifié et validé.

États : ⬜ à faire · 🟡 en cours · 🔎 à vérifier · ✅ fait

## Règle : une retouche compte aussi
Toute modification visible par l'utilisateur met à jour le `RM-<ECRAN>-IHM.md` dans la même sauvegarde git.

## Niveau 0 — Amorçage
| Lot | Type | Description | Règle source | Dépend de | État |
|---|---|---|---|---|---|
| 0.1 | Serveur | Conteneurs Docker, demarrer.bat / arreter.bat | CLAUDE.md | — | ⬜ |
| 0.2 | Serveur | Connexion à la base, adresse de contrôle `/health` | CLAUDE.md | 0.1 | ⬜ |
| 0.3 | Serveur | Squelette de tests + base de test séparée + lancer-tests.bat | CLAUDE.md | 0.2 | ⬜ |

## Niveau 1 — Fondations
| Lot | Type | Description | Règle source | Dépend de | État |
|---|---|---|---|---|---|
| 1.1 | Serveur | <Connexion + sessions> | RM-UTILISATEURS | 0.3 | ⬜ |
| 1.2 | Écrans | <Page de connexion> | RM-UTILISATEURS | 1.1 | ⬜ |

## Journal
- **<JJ/MM/AAAA>** — Lot <X.Y> — <ce qui a été fait>. Décisions : <…, et pourquoi>. Problèmes : <…>.
```

---

## Modèle J — `.doc/PROMPT-TYPE-LOT.md`

````markdown
# Phrases à copier pour un lot

Un lot = une conversation. `/clear` entre deux lots sans rapport.

## 1. Démarrer
```
Lis CLAUDE.md, .doc/PLAN-DEV.md, .doc/INVARIANTS-TRANSVERSES.md,
.doc/SUIVI-DEV.md et .doc/regles-metier/RM-<SUJET>.md.
On travaille sur le LOT <X.Y> : « <titre> ». Passe-le à « en cours ».
Sans rien coder, propose-moi :
1. le découpage du lot en petites étapes ;
2. le MLD si des tables changent (format de CLAUDE.md) ;
3. les points des invariants qui concernent ce lot ;
4. les dépendances vers d'autres lots.
Attends ma validation.
```

## 2. Construire
```
C'est validé. Construis le lot <X.Y> une étape à la fois,
et arrête-toi après chacune pour que je vérifie.
```

## 3. Clôturer
```
Clôture le lot <X.Y> : lance lancer-tests.bat et montre le résultat,
repasse INVARIANTS-TRANSVERSES.md point par point, mets le lot à
« à vérifier » dans SUIVI-DEV.md (et Notion), ajoute l'entrée du journal,
puis fais la sauvegarde git.
```
````

---

## Modèle K — `.doc/INVARIANTS-TRANSVERSES.md`

```markdown
# Invariants transverses — à vérifier à la fin de CHAQUE lot

Pour chaque point : respecté, ou pourquoi il ne s'applique pas.

## 1. Architecture
- [ ] SQL écrit dans un `schema_v*.sql` validé avant tout code ; jamais de création automatique des tables.
- [ ] Modèles = miroir des colonnes ; calculs dans `services/`.
- [ ] Ordre respecté : MLD → SQL → modèles → routes → tests.

## 2. Sécurité
- [ ] Chaque route vérifie qui est connecté.
- [ ] Chaque action sensible vérifie le rôle.
- [ ] Chaque modification importante est inscrite au journal des actions (qui, quoi, quand, avant/après).
- [ ] <Si plusieurs clients partagent l'application : chaque donnée porte l'identifiant de son propriétaire et la base empêche d'en voir un autre.>

## 3. Données
- [ ] Les valeurs contractuelles (prix, taux) sont figées au moment où elles engagent.
- [ ] Aucun taux, délai ou texte légal écrit en dur.
- [ ] Dates enregistrées en temps universel (UTC), affichées à l'heure locale.

## 4. Tests
- [ ] Tests écrits à partir des règles `RM-*` et au vert.
- [ ] Test de fiche à jour si une fiche est touchée.
- [ ] Aucune donnée de test restante dans la vraie base (vérifié par comptage).

## 5. Interface
- [ ] Chaque clic produit un résultat visible, à l'endroit du clic.
- [ ] Vérifié sur 4 formats d'écran.
- [ ] `RM-<ECRAN>-IHM.md` à jour.

## 6. Réutilisation
- [ ] Aucune logique ni aucun style recopié : ce qui apparaît 2 fois est regroupé.

## 7. Documentation
- [ ] Les règles écrites correspondent à ce que fait le code.
- [ ] `CLAUDE.md` et `.doc/REGLES-PROJET.md` identiques.
```

---

## Modèle L — `MEMO.md`

```markdown
# Mémo <NOM DU PROJET> — mes gestes

1. **Reprendre** : écrire `continuer` dans Claude Code (même dans une nouvelle conversation).
2. **Lancer** : bouton ▶ Démarrer.
3. **Sauvegarder** : bouton 💾 Sauver, puis une petite phrase.
4. **Laisser Claude avancer seul** : « fais les lots X à Y, tout seul ».
5. **Finir la journée** : `dodo`.
6. **Voir l'avancement** : `.doc/SUIVI-DEV.md` (ou le tableau Notion : <lien>).
```

---

## Modèle M — les fichiers `.bat` de base (sans accent, volontairement)

`demarrer.bat`
```bat
@echo off
cd /d %~dp0
docker compose up -d --build
start http://localhost:<PORT_ECRANS>
```

`arreter.bat`
```bat
@echo off
cd /d %~dp0
docker compose down
```

`sauver.bat`
```bat
@echo off
cd /d %~dp0
if not exist db-sync mkdir db-sync
docker compose exec -T db pg_dump -U <projet>_user -d <projet>_db --no-owner > db-sync\donnees.sql
set /p msg="Decris en quelques mots ce que tu as fait : "
if "%msg%"=="" set msg=Sauvegarde du %date%
git add -A
git commit -m "%msg%"
git push
pause
```

`lancer-tests.bat`, `preparer-base-test.bat`, `nettoyer-donnees-test.bat` et `restaurer_base.bat` dépendent de ton projet : demande à Claude de les écrire au **lot 0.3**, en suivant l'étape 10.

---

## Modèle N — `.doc/DEMARRAGE.md` (le fichier de reprise du démarrage)

```markdown
# Démarrage du projet — fichier de reprise

> Tenu à jour par Claude après CHAQUE réponse du développeur. C'est ce fichier qui permet de reprendre dans une nouvelle conversation.
> État général : **En cours** (devient « Démarrage terminé » à la fin de la phase 8)
> Dernière mise à jour : <JJ/MM/AAAA HH:MM>

## Analyse du dossier (faite le <JJ/MM/AAAA>)
- Cas : <A dossier vide / B documents seuls / C code existant / D méthode déjà suivie>
- Git : <non / oui, local seulement / oui, relié à GitHub : adresse>
- Documents trouvés : <liste, avec une ligne sur chacun>
- Code trouvé : <aucun / outils + ce qu'il fait>
- Poste : git <version ou absent>, Docker <version ou absent>

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
<Numéro et nom.>

## Questions en attente (posées, pas encore répondues)
1. <Texte exact de la question, avec ses choix.>

## Prochaine action
<Ce que Claude fait dès la reprise, en une phrase.>

## Réponses obtenues
| Date | Phase | Question | Réponse | Écrite dans |
|---|---|---|---|---|
| <JJ/MM> | 3 | Qui utilise l'application ? | Gestionnaire + adhérent | PRESENTATION.md |

## Décisions prises par Claude (« choisis pour moi »), à revoir si besoin
- <JJ/MM> — <décision> — Pourquoi : <…>

## Points à revoir plus tard
- <…>
```
