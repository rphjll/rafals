# Vitrine Express

Ton site où les clients choisissent un modèle et le personnalisent eux-mêmes, avec un aperçu en direct.

## Ce qu'il y a dans le dossier

```
vitrine-express/
├── index.html        → la page d'accueil (présentation + liste des modèles)
├── editeur.html      → l'éditeur (formulaire à gauche, aperçu à droite)
├── css/style.css     → le style de ton site
└── js/
    ├── config.js     → TES infos (nom, e-mail, prix, ville)  ← à modifier en premier
    ├── modeles.js    → les 10 modèles et leurs 5 styles chacun
    ├── metiers.js    → les textes d'exemple de 110 métiers (boulangerie, garage…) + « Autre »
    ├── generateur.js → dessine les 10 mises en page et fabrique le site (pas besoin d'y toucher)
    └── editeur.js    → ce qui fait marcher l'éditeur
```

## Pour l'essayer

Double-clique sur `index.html` : il s'ouvre dans ton navigateur. Pas besoin d'installer quoi que ce soit.

## À faire avant de le montrer

1. Ouvre `js/config.js` et mets **ton e-mail**, ton prix, et **change le `codeAdmin`** (choisis un mot que toi seul connais).
2. Teste chaque modèle dans l'éditeur, sur ordinateur et en vue téléphone.

## Les 3 niveaux

1. **Le modèle** (10 au choix) : la mise en page. Classique, Élégance, Duo, Magazine, Cartes, Minimal, Impact, Galerie photo, Carte & menu, Pro. Chacun a une structure vraiment différente.
2. **Le style** (5 par modèle, donc 50 en tout) : les couleurs et l'écriture pensées pour ce modèle. Pastilles sur l'accueil, et petites cartes sous « Modèle » dans l'éditeur.
3. **La personnalisation** : tout ce qui suit (textes, couleurs, disposition…).

Changer de modèle ou de style **garde tous les textes et les photos** du client.

Le champ **« Votre métier »** (onglet Textes) remplit tous les textes avec un exemple adapté, et ça marche avec n'importe quel modèle :
- **110 métiers** rangés en 10 catégories, et **« Autre »** tout en haut (textes neutres à compléter).
- On **tape les premières lettres** : la liste ne garde que les métiers qui commencent par ces lettres. Les accents ne comptent pas (« electricien » trouve « Électricien ») et des mots-clés aident (« kine », « vtc », « fitness »…).
- Si on tape **le mot entier** d'un métier (ex. « fromagerie »), il est choisi tout seul.
- Flèches ↑ ↓ et Entrée au clavier, ou un clic / un toucher sur un métier.
- Si le client a déjà écrit ses propres textes, on lui demande confirmation avant de les remplacer.

## Ce que le client peut personnaliser

L'éditeur est rangé en 3 onglets :
- **✏️ Textes** : nom, accroche, présentation, contact, horaires, tarifs, photos
- **🎨 Style** : ambiances prêtes en un clic, couleur principale, couleur du fond, style de l'en-tête, style d'écriture, taille du texte, forme des boutons
- **↕️ Disposition** : textes à gauche ou au centre, hauteur de l'en-tête, et le mode **✋ Déplacer / agrandir**

### Noms des rubriques

Dans l'onglet **✏️ Textes**, la partie **« Noms des rubriques »** permet de renommer chaque rubrique (À propos, Tarifs, Photos, Horaires & contact, Plan d'accès). Le nouveau nom change le titre sur le site **et** l'onglet du menu en haut.

### Le mode « Déplacer / agrandir »

1. Bouton **✋ Déplacer / agrandir** au-dessus de l'aperçu.
2. **Ordre des rubriques** : une liste de toutes les rubriques (y compris le plan). On en **fait glisser** une vers le haut ou le bas, à la souris ou au doigt, et le site prend cet ordre.
3. On **touche sur le site** un élément (un titre, un texte, les photos, le plan…) : un cadre bleu apparaît, et un panneau dit **« Vous modifiez : … »** avec de gros boutons :
   **Plus petit / Plus grand**, des **flèches** pour déplacer, **Cacher cette rubrique**, **Changer ce titre** et **Remettre comme avant**.
4. Les rubriques cachées se réaffichent avec le bouton **👁 Réafficher** dans le même panneau.
5. **✅ J'ai fini** pour quitter. **↶ Annuler** revient en arrière.

Sur téléphone, le panneau se place en bas de l'écran. Les outils n'apparaissent jamais dans le site final.

## Comment ça marche pour un client

1. Il choisit un modèle et le personnalise (textes, tarifs, photos, couleur).
2. Il clique sur **« Je veux ce site »** et laisse son nom et son téléphone.
3. **Son projet complet t'est envoyé** (un fichier `projet-nom-du-commerce.json` avec tout dedans, photos comprises) :
   - **Si ton site est en ligne sur Netlify** : c'est automatique. La demande arrive dans ton tableau de bord Netlify, rubrique **Forms**, avec le fichier du projet en pièce jointe.
   - **Sinon** (site ouvert sur un ordi, ou photos trop lourdes) : le client télécharge son projet et te l'envoie par e-mail en pièce jointe.

## Ce que TU fais quand tu reçois une demande

1. Ouvre `editeur.html?admin=TON_CODE` (le code de `config.js`). Une barre jaune **Mode admin** apparaît.
2. Clique sur **« Ouvrir un projet client »** et choisis le fichier `.json` reçu : tout se remplit tout seul, et une fenêtre te rappelle le nom et le téléphone du client.
3. Rappelle le client, corrige ce qu'il faut, vois le paiement avec tes parents.
4. Clique sur **« Télécharger le site final »** : tu obtiens son `index.html`.
5. Mets-le en ligne sur Netlify (voir plus bas).

Astuce : **« Sauvegarder le projet »** te permet de garder une copie de chaque client pour faire des modifications plus tard.

⚠️ Le mode admin empêche un client normal de télécharger son site sans payer, mais ce n'est pas une vraie sécurité : quelqu'un qui s'y connaît pourrait lire le code. Pour des petits commerces, c'est largement suffisant.

## Recevoir les demandes automatiquement (Netlify Forms)

1. Mets ton dossier `vitrine-express` en ligne sur Netlify (voir juste en dessous).
2. Dans Netlify, va dans ton site → **Forms** → active la détection des formulaires (**Enable form detection**), puis remets le dossier en ligne une fois.
3. Le formulaire **demande-site** apparaît. Dans **Form notifications**, ajoute ton e-mail pour être prévenu à chaque nouvelle demande.
4. Le plan gratuit de Netlify accepte un nombre limité de demandes par mois : largement assez pour commencer.

## Mettre un site en ligne gratuitement (Netlify)

1. Crée un compte sur https://app.netlify.com (avec l'accord de tes parents, ou sur leur compte).
2. Va dans **Sites → Add new site → Deploy manually**.
3. Glisse-dépose un **dossier** qui contient le `index.html` du client.
4. C'est en ligne ! Netlify te donne une adresse du type `nom-au-hasard.netlify.app`.
5. Pour une vraie adresse (ex. `barber-pessac.fr`), le client achète le nom de domaine (~12 €/an, chez OVH ou Gandi par exemple) et tu le relies dans **Domain settings**.

Tu peux aussi mettre **ton site Vitrine Express lui-même** en ligne de la même façon : glisse-dépose tout le dossier `vitrine-express`.

## Ajouter un style ou un métier

- **Un nouveau style** : dans `js/modeles.js`, copie une ligne de `variantes` d'un modèle et change son `id`, son `nom` et ses couleurs.
- **Un nouveau métier** : dans `js/metiers.js`, copie une ligne `ajouter("...", ...)` en bas du fichier et change l'identifiant, le nom, l'icône, la catégorie, les textes et les mots-clés. Il apparaît tout seul dans la recherche « Votre métier ».
- **Un nouveau modèle** (nouvelle mise en page) : c'est plus technique, il faut le dessiner dans `js/generateur.js` (`MISES_EN_PAGE` et `cssModele`). Demande de l'aide si tu veux en ajouter un.

Les anciens projets clients (avec l'ancien système de modèles par métier) s'ouvrent toujours dans le mode admin : ils arrivent dans le modèle Classique, avec le bon métier.

## Idées pour la suite

- Ajouter une section « Avis clients »
- Plus tard : comptes clients et paiement en ligne (demande d'être majeur ou de passer par tes parents)
