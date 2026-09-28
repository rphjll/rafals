# rafals — Phrases à copier pour un lot

Un lot = une conversation. `/clear` entre deux lots sans rapport. Le plus simple reste d'écrire `continuer`.

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
« à vérifier » dans SUIVI-DEV.md, ajoute l'entrée du journal,
puis fais la sauvegarde git.
```
