# Règle métier — Prestataires (sujet 02)

> En cours d'écriture (phase 6 du démarrage). Chaque règle est validée par Raphael au fil des questions.

## Objectif
Ce qu'un prestataire renseigne sur rafals (métiers, zone, SIRET) et quand les clients peuvent le trouver.

## Principes
- On devient prestataire depuis son compte, par « Proposer mes services » (voir `RM-COMPTES.md`).
- Un seul agenda par prestataire, même pour une société (voir `GLOSSAIRE-METIER.md`).
- Sans SIRET : annonces payables en espèces seulement ; rafals lui conseille de se déclarer (voir `GLOSSAIRE-METIER.md`, ⚠️ à vérifier juridiquement).

## Un métier principal et des métiers secondaires (décidé le 27/09/2026)
Un prestataire choisit **un métier principal** et peut ajouter **des métiers secondaires**. Il apparaît dans les recherches de tous ses métiers, mais pour un métier secondaire, il apparaît **après** les prestataires dont c'est le métier principal. Dans chaque groupe, les mieux notés d'abord.
Réponse de Raphael, mot pour mot : « oui mais plus loin que les plombiers il doit aparaitre plus bas que les plombier et ca sera un clasement des mieux notés ».
- Exemple : Mme Dupont cherche « Électricien + Pessac ». Résultats : 1) Sophie, électricienne (métier principal), 4,8 ★ ; 2) Marc, électricien (métier principal), 4,2 ★ ; 3) Karim, plombier (électricien en métier secondaire), 4,9 ★ — Karim est 3e malgré sa meilleure note.
- Exemple : Mme Dupont cherche « Plombier + Pessac » → Karim est dans le 1er groupe, classé selon sa note parmi les plombiers.
**Pourquoi :** le client voit d'abord les spécialistes du métier qu'il cherche.
Le détail du classement (prestataires sans avis, distance…) sera traité dans le sujet 07 « Recherche ».

## Zone d'intervention : une ville et une distance (décidé le 27/09/2026)
Le prestataire indique sa ville de départ et la distance maximale, en kilomètres, jusqu'à laquelle il se déplace. Il apparaît dans les recherches des clients situés dans ce rayon.
- Exemple 1 : Karim, « Pessac, jusqu'à 15 km ». Mme Dupont à Talence (6 km) → elle le trouve.
- Exemple 2 : M. Petit à Libourne (40 km) → il ne trouve pas Karim.
**Cas limite tranché :** la distance est mesurée à vol d'oiseau, entre le centre des deux villes (plus simple et suffisant pour choisir un prestataire).

## Vérification automatique du SIRET (décidé le 27/09/2026)
Quand un prestataire écrit son SIRET, rafals le cherche aussitôt dans le répertoire public des entreprises de l'État (INSEE, gratuit). Le SIRET est refusé si le numéro n'existe pas, si l'établissement est fermé, ou si le nom de l'entreprise ne correspond pas au nom du prestataire.
- Exemple 1 : Julie Martin écrit 912 345 678 00014 → trouvé, ouvert, au nom de « Julie Martin » → accepté ; le paiement par carte devient possible sur ses annonces.
- Exemple 2 : un inconnu écrit 123 456 789 00012 → numéro inexistant → refusé ; il reste « sans SIRET » (espèces seulement).
- Exemple 3 : Karim écrit le SIRET de son oncle « Plomberie Benali » → le nom ne correspond pas → refusé.
**Pourquoi :** empêcher un faux SIRET d'ouvrir le paiement par carte.
**Cas limite tranché :** si le répertoire de l'État ne répond pas (panne), le SIRET est mis « en attente » et revérifié automatiquement plus tard ; en attendant, espèces seulement.

## Lieu du service : au choix, pour chaque annonce (décidé le 27/09/2026)
Pour chaque annonce, le prestataire indique où a lieu le service : « chez le client », « chez moi / dans mon local » (avec l'adresse), ou « les deux ».
- Exemple 1 : Karim, « Plomberie, dépannage fuite » → chez le client (la zone d'intervention s'applique).
- Exemple 2 : Léa, coiffeuse à Mérignac : « Coupe femme — au salon, 12 rue des Lilas » et « Coupe à domicile — chez le client, +10 € ».
**Cas limite tranché :** pour un service « chez moi », la zone d'intervention sert seulement à la recherche (les clients dans le rayon voient l'annonce) ; le client se déplace.

## Visible tout de suite (décidé le 27/09/2026)
Un prestataire est visible des clients dès qu'il publie sa première annonce, sans attendre l'administrateur. L'administrateur voit chaque nouveau prestataire dans son écran « Administration » et peut le bloquer à tout moment.
- Exemple 1 : Julie remplit son profil le 01/10 à 10 h, publie « Ménage 2 h — 50 € » à 10 h 05 → visible à 10 h 05.
- Exemple 2 : le 02/10, Raphael voit un profil « Plombier pas cher » avec des photos volées → il le bloque ; ses annonces disparaissent aussitôt.
**Pourquoi :** pas d'attente pour les prestataires, pas de travail quotidien obligatoire pour Raphael.
Un prestataire sans annonce publiée n'apparaît dans aucune recherche (ex. Karim « en création », qui se fait seulement aider à se déclarer).

## Contenu du profil (proposé par Claude, à valider à la relecture)
- Obligatoire : nom affiché (ex. « Julie Martin — Ménage » ou « Net & Clair »), métier principal, ville + distance.
- Facultatif : photo ou logo, présentation (quelques lignes), métiers secondaires, SIRET.
- Le téléphone et l'adresse mail du prestataire ne sont **pas** affichés publiquement : le client les voit seulement après avoir réservé. **Pourquoi :** éviter que les clients contournent rafals (et la commission) dès la première recherche.

## Qui peut faire quoi
| Action | Qui | Condition |
|---|---|---|
| Devenir prestataire | Titulaire d'un compte | Adresse mail vérifiée ; accord des parents vérifié avant 18 ans |
| Modifier son profil | Le prestataire lui-même | — |
| Ajouter ou changer son SIRET | Le prestataire lui-même | Vérifié automatiquement |
| Bloquer / débloquer un prestataire | Administrateur | — |

## Désactivation / clôture / suppression (proposé par Claude, à valider à la relecture)
- **Mettre en pause** (réversible) : le prestataire se rend invisible (ex. Julie pendant ses congés d'août) ; ses rendez-vous déjà pris restent.
- **Bloquer** (réversible, par l'administrateur) : invisible, ne peut plus publier ; ses rendez-vous à venir sont annulés et les clients prévenus.
- **Arrêter son activité** (définitif) : le profil prestataire est clôturé ; ses factures restent consultables (la loi oblige à les garder 10 ans).
- **Supprimer** : interdit dès que le prestataire a eu un rendez-vous ou émis une facture.

## Valeurs figées
Le nom, l'adresse et le SIRET du prestataire sont recopiés sur chaque devis et chaque facture au moment où ils sont émis. Ex. Julie change de nom commercial en 2027 → ses factures de 2026 gardent l'ancien nom.

## Questions ouvertes
- ⚠️ Prestataires sans SIRET payés en espèces : à faire vérifier juridiquement.

## Références
- `GLOSSAIRE-METIER.md`, `RM-COMPTES.md`
