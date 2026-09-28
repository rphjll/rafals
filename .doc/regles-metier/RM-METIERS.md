# Règle métier — Métiers et catégories (sujet 04)

> Validé et formalisé le 28/09/2026 (phase 6 du démarrage).

## Objectif
La grande liste des métiers de rafals, rangée dans des catégories (« dossiers »), et la façon dont clients et prestataires y trouvent un métier.

## Principes
- Chaque Annonce est rangée sous un Métier ; chaque prestataire a un métier principal et peut avoir des métiers secondaires (voir `RM-PRESTATAIRES.md`).
- Recherche d'un métier : en ouvrant une catégorie, ou en tapant les premières lettres (voir `GLOSSAIRE-METIER.md`).

## Source de la liste : triée (décidé le 28/09/2026)
Claude construit la liste à partir des 110 métiers et 10 catégories de vitrine-express (`vitrine-express/vitrine-express/js/metiers.js`), et la complète avec le répertoire officiel des métiers de France Travail, en ne gardant que les métiers qu'un **particulier** peut réserver. Raphael relit la liste avant qu'elle entre dans rafals.
- Exemple 1 : « Professeur de guitare » (absent de vitrine-express, présent dans la liste officielle, sert des particuliers) → ajouté, catégorie « Sport & loisirs ».
- Exemple 2 : « Contrôleur aérien » → écarté (ne sert pas des particuliers).
**Pourquoi :** Mme Dupont ne doit pas se perdre dans des milliers de métiers qui ne la concernent pas.

## Métier manquant : le prestataire le propose (décidé le 28/09/2026)
Un prestataire qui ne trouve pas son métier clique « Mon métier n'est pas dans la liste » et écrit son nom. La demande arrive dans l'écran « Administration » : l'administrateur l'accepte (et la range dans une catégorie), ou la remplace par un métier existant. En attendant, le prestataire utilise le métier « Autre ».
- Exemple 1 : Nadia propose « Cerf-voliste » le 02/11 → Raphael l'accepte le 03/11 dans « Sport & loisirs » → les annonces de Nadia passent de « Autre » à « Cerf-voliste ».
- Exemple 2 : Tom propose « Plombier chauffagiste » → Raphael répond « Plombier » (existe déjà) et ajoute « chauffagiste » aux mots-clés de « Plombier ».
**Pourquoi :** la liste s'enrichit avec les vrais besoins, sans laisser entrer des doublons ou des fautes.

## Mots-clés (proposé par Claude, validé par Raphael le 28/09/2026)
Chaque métier a des mots-clés, comme dans vitrine-express : la recherche les trouve, sans tenir compte des accents.
- Exemple 1 : taper « kine » trouve « Kinésithérapeute ».
- Exemple 2 : taper « electricien » (sans accent) trouve « Électricien ».

## Une seule catégorie par métier (proposé par Claude, validé par Raphael le 28/09/2026)
Chaque métier est rangé dans une seule catégorie ; les mots-clés servent à le retrouver par d'autres chemins.
- Exemple : « Photographe » est dans « Événements » ; taper « photo » le trouve aussi.

## Précisions prises au lot 2.1 (proposé par Claude, validé par Raphael le 28/09/2026 avec la liste)
- **Liste de départ : 14 dossiers, 128 métiers**, dans `backend/app/donnees/metiers.json` (chargée avec `charger-metiers.bat`, relançable sans doublon). Le 14e dossier « Autre » contient le seul métier « Autre ».
- **Écartés de vitrine-express** : restaurants et commerces (vente d'objets), lieux (salle d'escalade, location de salle…), quelques professions réglementées ou agences. Liste et raisons dans le fichier. Raphael peut les repêcher.
- **Recherche** : dès la 1re lettre, au début du nom, d'un mot du nom ou d'un mot-clé, sans accents. Ordre : nom qui commence par le texte, puis mot du nom, puis mot-clé ; ensuite alphabétique. 10 résultats au maximum.
  - Ex. « fuite » → Couvreur / Zingueur, Plombier (mots-clés) ; « eben » → Menuisier / Ébéniste.
- **Proposer un métier qui existe déjà** est refusé avec son nom (« Ce métier existe déjà dans la liste : « Plombier ». »).
- **Décision de l'administrateur** : accepter (choisir le dossier : le métier est créé), remplacer par un métier existant (le nom proposé devient un de ses mots-clés), ou refuser.
- Chaque proposition, décision, création ou modification de métier est écrite au journal des actions.

## Qui peut faire quoi
| Action | Qui | Condition |
|---|---|---|
| Proposer un métier | Prestataire | — |
| Accepter / refuser une proposition | Administrateur | — |
| Ajouter, renommer, désactiver un métier ou une catégorie | Administrateur | — |

## Désactivation / clôture / suppression
- Désactiver un métier (réversible) : il n'apparaît plus dans les choix pour les nouvelles annonces ; les annonces existantes le gardent.
- Supprimer un métier : interdit dès qu'une annonce l'a utilisé.

## Valeurs figées
Aucune.

## Questions ouvertes
- (aucune)

## Références
- `GLOSSAIRE-METIER.md`, `RM-PRESTATAIRES.md`, `PRESENTATION.md` (vitrine-express)
