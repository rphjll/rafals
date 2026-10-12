# En-tête commun et sous-menu — Interface

> Fichiers : `frontend/src/components/AppEntete.vue`, `frontend/src/components/AppSousMenu.vue`, `frontend/src/composables/useMenu.ts`, `frontend/src/App.vue`, `frontend/src/composables/useCompte.ts`. Construit au lot 0.4, zone du compte au lot 1.2 (28/09/2026).
> **Refait le 04/10/2026** (nouvelle présentation, maquette https://claude.ai/artifact/8GvhAaZ5x1m7Kyv1dLMQb3) : le menu passe de 10 entrées à 3, les autres pages sont rangées dans un sous-menu ou derrière le prénom.

## En-tête
Bandeau blanc (`surface`) collé en haut de toutes les pages, bordure fine en bas, hauteur 60 px. Contenu centré sur 1080 px au maximum, marges de 16 px sur les côtés.

**Ordre des éléments, de gauche à droite :**
1. Logo « rafals. » (police des titres, vert `primaire`, point orange `accent`) → lien vers l'accueil `/`.
2. Menu principal, collé à droite, 4 entrées (5 une fois connecté) :
   1. « Accueil » → `/`, où le client publie une demande (ajoutée le 05/10/2026 ; demande de Raphael : « crée un nouvel onglet acceuille et de laisser trouver un prestataire »)
   2. « Trouver un prestataire » → `/trouver`, où se fait la recherche
   3. « Mes réservations » → `/rendez-vous` (groupe « réservations »)
   4. « Messages » → `/messages` — **seulement connecté** ; à droite du mot, une pastille rouge avec le nombre de conversations qui ont du nouveau, relue toutes les minutes (ajoutée le 07/10/2026, `RM-MESSAGES-IHM.md`)
   5. « Proposer mes services » → `/proposer` — devient « Mon activité » quand le compte a un profil de prestataire (groupe « activité »)
3. Zone du compte, au bout du menu (affichée seulement une fois qu'on sait si quelqu'un est connecté, pour éviter un clignotement) :
   - personne n'est connecté : bouton principal [Se connecter] → `/connexion` ;
   - connecté : une pastille ronde avec les initiales (ex. « JM »), le prénom (ex. « Julie ») et « ▾ ». Un clic ouvre une petite liste sous la pastille :
     1. « Mon compte » → `/compte`
     2. « Administration » → `/administration` — **seulement pour un administrateur**
     3. bouton secondaire [Se déconnecter] → accueil + message vert « Vous êtes déconnecté. »
   - La liste se referme : par un 2ᵉ clic sur la pastille, un clic ailleurs, la touche Échap, ou un changement de page.

L'entrée du groupe affiché est surlignée (fond `primaire-doux`, texte `primaire`). Survol : même effet. Depuis le 07/10/2026 (style « chaleureux ») les entrées sont en forme de pastille (`rounded-bouton`) et en gras ; le logo utilise `font-marque`. Sur « Mon compte » ou « Administration », c'est le contour de la pastille qui passe au vert.

## Sous-menu (sous l'en-tête, au-dessus de la page)
Bandeau blanc avec une ligne d'onglets ; la page affichée est soulignée en vert. Il n'apparaît que sur les pages d'un groupe. **Les pages elles-mêmes ne changent pas** (en particulier « Mon agenda »).

| Groupe | Pour qui | Onglets, dans l'ordre |
|---|---|---|
| Mes réservations | tout le monde | Mes demandes `/mes-demandes` (ajouté le 07/10/2026) · Rendez-vous `/rendez-vous` · Devis `/devis` · Factures `/factures` |
| Mon activité | prestataire seulement | Ma fiche `/proposer` · Demandes près de chez moi `/demandes-pres-de-chez-moi` (ajouté le 07/10/2026) · Mon agenda `/mon-agenda` · Devis `/devis` · Factures `/factures` · Mes démarches `/demarches` |

- « Devis » et « Factures » sont dans les deux groupes (ce sont les mêmes pages) : on reste dans le groupe d'où l'on vient. Ex. Julie clique « Mon activité » puis « Devis » : le sous-menu « Mon activité » reste affiché. Arrivée directe par un lien : groupe « Mes réservations ».
- Sur « Proposer mes services » sans profil de prestataire : pas de sous-menu.
- Sur un petit écran, la ligne d'onglets défile sur le côté.

## Menu depuis le 07/10/2026 (demande de Raphael, détail : `RM-MON-ACTIVITE-IHM.md`)
**Ce paragraphe remplace la liste des entrées et des deux groupes décrite plus haut.**
- Entrées : « Accueil » `/` · « Trouver un prestataire » `/trouver` · « Messages » `/messages` (seulement connecté) · **« Mon activité » `/mon-activite`** · **« Mon profil » `/proposer`** (compte sans profil de prestataire : « Proposer mes services »).
- « Mes réservations » n'existe plus : ses pages sont dans « Mon activité ».
- « Mon activité » est surlignée sur sa page et sur toutes les pages qu'elle range (Mes demandes, Rendez-vous, Devis, Factures, Demandes près de chez moi, Mon agenda, Déclarer à l'URSSAF) ; « Mon profil » sur `/proposer`.
- Sous-menu : seulement sur ces pages rangées, avec « ‹ Mon activité » en premier. Plus de « Ma fiche » dans le sous-menu (c'est « Mon profil »).
- Barre du bas sur téléphone : « Accueil », « Trouver », « Messages », « Activité », « Profil » (ou « Proposer »).

## Menu depuis la fusion de « Mon profil » et « Mon compte » (07/10/2026, demande de Raphael, détail : `RM-PROFIL-IHM.md`)
- **Prestataire** : 4 entrées, Accueil · Trouver un prestataire · Messages · Mon activité. « Mon profil » n'est plus une entrée principale.
- **Client ou visiteur** : les mêmes, plus « Proposer mes services » (→ `/profil?proposer=1`), qui disparaît dès que le profil de prestataire est créé.
- **Rond des initiales** (☰ sur téléphone) : « Mon profil » (→ `/profil`) à la place de « Mon compte », puis « Administration » (administrateurs), puis « Se déconnecter ».
- La barre du bas sur téléphone lit la même liste : 4 boutons pour un prestataire, 5 pour un client.

## Barre du bas sur téléphone (ajoutée le 07/10/2026, `frontend/src/components/AppBarreBas.vue`)
Sous 768 px, les entrées principales quittent le menu ☰ et vont dans une barre blanche arrondie fixée en bas de l'écran, sur toutes les pages : un pictogramme et un mot court par entrée — « Accueil », « Trouver », « Réservations », « Messages » (seulement connecté, avec la pastille rouge des non lus), « Proposer » (ou « Activité » pour un prestataire). L'entrée de la page affichée est en vert sur fond vert clair. L'en-tête et la barre lisent la même liste (`useMenu`, `entrees`). Le menu ☰ ne garde que le compte : « Mon compte », « Administration », [Se déconnecter], ou [Se connecter]. Le message court de 3 secondes s'affiche au-dessus de la barre. **Ce paragraphe remplace la 2ᵉ ligne ci-dessous** (« les 4 entrées, puis un trait… »).

## Sous 768 px de large (téléphone, petite tablette)
- Le menu disparaît ; un bouton ☰ apparaît à droite (libellé lu à voix haute : « Ouvrir le menu » / « Fermer le menu »).
- Un clic sur ☰ déroule le menu sous l'en-tête, une entrée par ligne : les 4 entrées, puis un trait, le prénom en petit, « Mon compte », « Administration » (administrateur), [Se déconnecter] — sans pastille à ouvrir.
- Le menu se referme tout seul quand on change de page.

## Particularités
- La liste des groupes est écrite une seule fois, dans `useMenu.ts` ; l'en-tête et le sous-menu la lisent tous les deux.
- Pas encore fait (prévu dans la maquette) : la barre de 5 boutons en bas de l'écran sur téléphone, et le tableau de bord de « Mon activité ».
