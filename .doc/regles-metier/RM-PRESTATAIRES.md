# Règle métier — Prestataires (sujet 02)

> Validé et formalisé le 28/09/2026 (phase 6 du démarrage).

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
- Exemple 1 : Karim, « Pessac, jusqu'à 15 km ». Mme Dupont à Talence (7,4 km) → elle le trouve.
- Exemple 2 : M. Petit à Libourne (38 km) → il ne trouve pas Karim.
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

## Contenu du profil (proposé par Claude, validé par Raphael le 28/09/2026)
- Obligatoire : nom affiché (ex. « Julie Martin — Ménage » ou « Net & Clair »), métier principal, ville + distance.
- Facultatif : photo ou logo, présentation (quelques lignes), métiers secondaires, SIRET.
- Le téléphone et l'adresse mail du prestataire ne sont **pas** affichés publiquement : le client les voit seulement après avoir réservé. **Pourquoi :** éviter que les clients contournent rafals (et la commission) dès la première recherche.

## Précisions prises au lot 2.3 (proposé par Claude le 28/09/2026 en mode « tout seul », validé par Raphael le 29/09/2026 point par point)
- **Distance** : de 1 à **100 km** (validé par Raphael le 29/09/2026). Distances réelles calculées sur la liste officielle des communes : Pessac → Talence 7,4 km, Pessac → Libourne 38 km.
- **Au plus 5 métiers secondaires** (validé par Raphael le 29/09/2026) ; le métier principal ne peut pas être aussi secondaire.
- **Nom affiché** : 2 à 80 caractères. **Présentation** : 1 000 caractères au plus (validé par Raphael le 29/09/2026).
- **SIRET** : on peut le taper avec des espaces ; rafals vérifie tout de suite qu'il a 14 chiffres **et la bonne clé de contrôle** (le dernier chiffre se calcule à partir des autres). Un SIRET nouveau ou changé passe « à vérifier » (vérification auprès de l'État au lot 2.4) ; le retirer = « absent ». ⚠️ L'exemple de Julie (912 345 678 00014) est inventé et ne passe pas la clé : il reste un exemple de lecture, pas un vrai numéro.
- **Photo** : JPG ou PNG, 5 Mo au plus (même vérification que l'accord des parents). Elle est visible de tous (elle sera montrée sur les annonces) (validé par Raphael le 29/09/2026).
- **Statuts** : pause ↔ reprise par le prestataire ; arrêt (définitif : plus aucune modification) ; blocage et déblocage par l'administrateur seulement. Un prestataire bloqué ne peut ni reprendre ni se mettre en pause ; seul l'administrateur le débloque, ce qui le remet « actif » (validé par Raphael le 29/09/2026 : pas de déblocage automatique). Un prestataire arrêté ne peut plus être bloqué ni débloqué.
- **Devenir prestataire** exige l'adresse vérifiée et, avant 18 ans, l'accord des parents accepté (règle de `RM-COMPTES.md`), sinon message clair.
- Toute création, modification, photo et changement de statut est écrit au journal des actions.

## Vérification du SIRET auprès de l'État : précisions du lot 2.4 (validé par Raphael le 29/09/2026)
- Service utilisé : **« Recherche d'entreprises »** de l'État (recherche-entreprises.api.gouv.fr), gratuit, sans inscription.
- **Vérifié** si le SIRET existe, que l'établissement est **ouvert**, et que le **nom de famille du compte** apparaît dans le nom officiel ou parmi les **dirigeants**.
  - Ex. Julie Martin, auto-entrepreneuse, nom officiel « JULIE MARTIN » → vérifié. Julie gérante de « NET ET CLAIR » (dirigeante) → vérifié.
- **Nom caché par l'État** (« non diffusible », fréquent chez les auto-entrepreneurs) : **accepté d'office** si le SIRET existe et est ouvert (décision de Raphael du 29/09/2026).
- **Refusé tout de suite, avec la raison** (le SIRET n'est pas enregistré) : introuvable ; établissement fermé ; SIRET d'une autre entreprise (« Ce SIRET appartient à « GOOGLE FRANCE » : il ne semble pas être le vôtre… »).
- **Service injoignable** : SIRET enregistré « à vérifier » (espèces seulement), nouvel essai automatique **toutes les 30 minutes**, écrit au journal.
- **Cas particulier** (ex. salarié qui n'est pas dirigeant) : l'administrateur peut **valider le SIRET à la main**, après avoir vu un justificatif.

## Qui peut faire quoi
| Action | Qui | Condition |
|---|---|---|
| Devenir prestataire | Titulaire d'un compte | Adresse mail vérifiée ; accord des parents vérifié avant 18 ans |
| Modifier son profil | Le prestataire lui-même | — |
| Ajouter ou changer son SIRET | Le prestataire lui-même | Vérifié automatiquement |
| Bloquer / débloquer un prestataire | Administrateur | — |

## Désactivation / clôture / suppression (proposé par Claude, validé par Raphael le 28/09/2026)
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
