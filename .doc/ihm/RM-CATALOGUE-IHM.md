# Catalogue des composants — Interface

> Fichiers : `frontend/src/pages/CataloguePage.vue` et les composants de `frontend/src/components/ui/`. Construit au lot 0.4 (28/09/2026).
> Page de vérification : on y voit tous les composants communs d'un coup, sur les 4 formats d'écran. Elle sera retirée (ou réservée aux administrateurs) avant la mise en ligne.

## Page Catalogue (`/catalogue`)
**Ordre des éléments :**
1. Titre « Catalogue des composants », puis « Les briques communes de tous les écrans de rafals. Tout est cliquable. »
2. Carte « Boutons », de gauche à droite :
   - [Réserver mardi 14/10 à 10 h 00] (principal) → message vert « Bouton principal cliqué ».
   - [Demander un devis] (secondaire) → message vert « Bouton secondaire cliqué ».
   - [Annuler] (danger) → message rouge « Annulation refusée : exemple de message d'erreur ».
   - [🔒 Payer par carte] (verrouillé) → bulle au-dessus du bouton : « Karim n'a pas encore de SIRET : il ne peut être payé qu'en espèces, le jour du rendez-vous. Réservez, puis payez-le sur place. » Un 2e clic ou un clic ailleurs la ferme.
3. Carte « Champs » (2 colonnes sur ordinateur, 1 sur téléphone) :
   - « Adresse mail * » prérempli `julie.martin@example.com`, aide « Exemple de donnée d'essai : @example.com ».
   - « Mot de passe * » prérempli `soleil` → erreur rouge « Au moins 10 caractères (ex. MaisonBleue44). » tant qu'il fait moins de 10 caractères.
4. Carte « Badges » : « SIRET vérifié » (OK), « Sans SIRET » (en attente), « Rendez-vous annulé » (erreur), « Espèces seulement » (neutre).
5. Carte « Fenêtre et message » : [Ouvrir la fenêtre de confirmation] → fenêtre « Confirmer le rendez-vous ? » avec [Confirmer] à gauche et [Annuler] (danger) à droite. Confirmer → fenêtre fermée + message vert « Rendez-vous confirmé · mardi 14/10 à 10 h 00 » pendant 3 secondes. Échap ou clic sur le fond sombre → fenêtre fermée.

## Composants communs (`frontend/src/components/ui/`)
| Composant | Rôle | Options |
|---|---|---|
| `AppBouton` | Tous les boutons | `variante` : principal, secondaire, danger, verrouille ; `raison-verrou` (texte de la bulle) ; `type` ; `pleine-largeur` ; `occupe` (envoi en cours : inactif, lot 1.2) |
| `AppChamp` | Tous les champs de saisie | `etiquette`, `obligatoire` (astérisque), `erreur`, `aide`, `type`, `v-model` |
| `AppFenetre` | Toutes les fenêtres de confirmation | `ouverte`, `titre`, contenu, emplacement `pied` pour les boutons ; ferme sur Échap ou clic sur le fond |
| `AppBadge` | Étiquettes d'état | `etat` : ok, attente, erreur, neutre |
| `AppCarte` | Carte centrée des formulaires courts (lot 1.2) | `titre`, `intro`, contenu |
| `AppAlerte` | Bandeau posé là où l'on regarde : erreur du serveur au-dessus du bouton, information (lot 1.2) | `etat` : erreur, attente, ok |
| `AppSeparateur` | Trait avec un petit texte au milieu, ex. « déjà inscrit ? » (lot 1.2) | contenu |
| `AppChampFichier` | Zone « Choisir un fichier » (lot 1.4) | `etiquette`, `aide`, `accepte` (formats), `v-model` (le fichier) |
| `AppSelection` | Liste déroulante (lot 2.2) | `etiquette`, `options` (valeur, texte), `obligatoire`, `v-model` |
| `AppRecherche` | Champ de recherche avec propositions : pause de frappe, ↑ ↓ Entrée (lot 2.5 ; sert aux métiers et aux communes) | `etiquette`, `chercher`, `libelle`, `detail`, `cle`, `placeholder`, `aide`, emplacement `aucun-resultat`, évènement `choisir` |
| `AppElementChoisi` | Bandeau vert « ✓ Pessac (33600) [Changer] » (lot 2.5) | `texte`, `detail`, évènement `changer` |
| `AppZoneTexte` | Texte sur plusieurs lignes avec compteur « 57 / 1000 » (lot 2.5) | `etiquette`, `maximum`, `aide`, `v-model` |
| `AppMessage` + `useMessage()` | Message court après une action, 3 secondes | `afficherMessage(texte, 'ok' \| 'erreur')` ; placé une seule fois dans `App.vue` |
