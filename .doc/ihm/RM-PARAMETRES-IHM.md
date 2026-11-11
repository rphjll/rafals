# Paramètres — Interface

## Depuis le 10/11/2026 : identique à la grande maquette (lots 14.5 et 14.6)

Demande de Raphael, mot pour mot : « je veux que ca soit exactement pareil que la maquette et tu fais l'agenda pareil que la maquette ». Maquette : `.doc/ihm/maquette-site-complet.html`. Les styles de la maquette sont recopiés dans `frontend/src/style.css` ; les sections plus bas décrivent le fonctionnement, qui ne change pas sauf mention ici.

- « Apparence » : une carte, « Thème » en 3 cases collées **[Automatique | Clair | Sombre]** et l'explication du choix dessous (les petits aperçus de couleurs sont retirés).
- « Mes abonnements : ce qui vous est envoyé » : 3 lignes avec un **interrupteur** (`components/ui/AppInterrupteur.vue`) et un exemple.
- « Nouvelles demandes » (prestataire) : une ligne par métier avec son interrupteur, « Par mail » en 3 cases collées [À chaque demande | Un mail le soir à 18 h | Aucun mail] et l'explication, puis « Sur ce téléphone » avec son interrupteur.
- « Mon agenda » passe en sombre comme le reste (plus d'ancien style à part).


> Fichiers : `frontend/src/pages/ParametresPage.vue`, `frontend/src/composables/useTheme.ts`, `frontend/index.html` (premier affichage), `frontend/src/style.css` (couleurs sombres, aperçus `apercu-clair` / `apercu-sombre`).
> Demande de Raphael du 17/10/2026 : « je veux un theme sombre a mon site ou je pourrais le changer dans un nouvel onglet qui vas s'appeler parmettre qui sera quand je clic sur le nom de mon compte en haut a droite ». Maquette validée le même jour (« ok vsy ») : https://claude.ai/artifact/Qki4gKVhQiBKKdLggDGkJd (`.doc/ihm/maquette-parametres.html`).

## Où la trouver
- Adresse : `/parametres`.
- Dans la liste qui s'ouvre sous le prénom, en haut à droite : « Mon profil », **« Paramètres »**, « Administration » (administrateurs), [Se déconnecter]. Sur téléphone, la même ligne est dans le menu ☰.
- La page s'ouvre aussi sans être connecté (le réglage ne dépend pas du compte), mais le lien n'est que dans la liste du compte.

## Contenu
1. Titre « Paramètres », phrase « Réglez rafals comme vous le préférez. »
2. Carte « Apparence », choix « Thème » en 3 cases côte à côte (l'une sous l'autre sur téléphone), chacune avec un petit aperçu de couleurs au-dessus du texte :
   | Case | Petit texte | Effet |
   |---|---|---|
   | Automatique (choix de départ) | Comme votre téléphone ou votre ordinateur | Clair le jour, sombre si l'appareil est réglé en sombre ; change tout seul si l'appareil change |
   | Clair | Fond blanc, toujours | Toujours clair sur cet appareil |
   | Sombre | Fond noir, plus doux le soir | Toujours sombre sur cet appareil |
3. Phrase sous les cases : « Le choix est gardé sur cet appareil. Sur un autre téléphone ou ordinateur, vous le refaites une fois. »
4. **Carte « Mes abonnements : ce qui vous est envoyé »** (21/10/2026, tout compte connecté ; ancre `#abonnements`) : phrase « Pour tous les prestataires que vous suivez, sur votre téléphone. », puis 3 cases cochées au départ, chacune avec un exemple : « Créneau libre » (Ex. « Karim est libre jeudi 23/10/2026 à 14 h 00 »), « Nouveau métier » (Ex. « Karim propose maintenant : Chauffagiste »), « Retour après une absence » (Ex. « Karim reprend son activité ce lundi 03/11/2026 »). Chaque clic est enregistré tout de suite (« Enregistré ») ; en cas d'échec, la case revient. En bas : « Pour ne plus rien recevoir d'un prestataire en particulier : [🔕 Rendre muet] dans **Mes abonnements** » (lien). Règles : `RM-ABONNEMENTS.md`.
5. **Partie « Notifications : être prévenu des nouvelles demandes »** (21/10/2026, venue de « Mon activité › Alertes ») : seulement pour un prestataire. Pour quels métiers, « Sur ce téléphone », comment par mail. Détail : `RM-ALERTES-IHM.md`. Ex. Karim (Électricien) la voit ; Julie, cliente, ne voit que « Apparence ».

## Comportement
- Un clic sur une case change les couleurs de tout le site tout de suite, sans bouton « Enregistrer ». Message court de 3 secondes : « Thème sombre activé. », « Thème clair activé. » ou « Thème automatique : comme votre appareil. ».
- Le choix est gardé dans le navigateur de l'appareil (clé `rafals-theme` : `clair` ou `sombre` ; rien = Automatique). **Aucune donnée dans la base** (décision de Raphael du 17/10/2026). Exemples : Karim choisit « Sombre » sur son PC → son PC reste sombre, même après déconnexion ; son téléphone reste en « Automatique » tant qu'il n'y change rien.
- Navigation privée ou stockage refusé : le thème change quand même, mais revient à « Automatique » à la prochaine ouverture.
- Le thème est posé avant l'affichage de la page (petit script dans `index.html`), pour éviter un éclair blanc au chargement en sombre.
- « Mon agenda » passe aussi en sombre.
- La page « Pas de connexion » (`public/hors-ligne.html`) suit toujours seulement le réglage de l'appareil.
