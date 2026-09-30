# Règle métier — Recherche (sujet 07)

> Validé et formalisé le 30/09/2026 (lot 4.0).

## Objectif
Comment un client trouve un prestataire : un métier + une ville, et l'ordre des résultats.

## Déjà décidé (sujets 02, 04, 05)
- Le client cherche un **métier** (par les premières lettres ou par dossier, `RM-METIERS.md`) et une **ville**.
- Un prestataire apparaît si la ville du client est dans son **rayon** (distance à vol d'oiseau, `RM-PRESTATAIRES.md`), et seulement s'il a au moins une **annonce en ligne** de ce métier (`RM-ANNONCES.md`).
- Ceux dont c'est le **métier principal** passent avant ceux qui l'exercent en **métier secondaire** ; ensuite, les **mieux notés** d'abord.
- Téléphone, mail et rue du local : jamais dans les résultats (seulement après réservation).

## Prestataires sans avis : après les notés, avec un badge « Nouveau » (décidé le 30/09/2026)
- Exemple : « plombier + Talence » → 1) Sophie 4,8 ★ (12 avis) ; 2) Marc 4,2 ★ (30 avis) ; 3) Karim, badge « Nouveau sur rafals ».
**Pourquoi :** Karim reste visible sans passer devant ceux qui ont fait leurs preuves.

## La note ET le nombre d'avis comptent (décidé le 30/09/2026)
Réponse de Raphael, mot pour mot : « faudra faire plein de calcules pour savoir qui est premier mais ou c'est en fonction des 2 mais dans l'exemple c sophie qui est devant mais faudra faire des calcules ».
Calcul proposé par Claude et validé (« note pondérée ») : **note de classement = (somme des notes reçues + 5 avis fictifs à 4 ★) ÷ (nombre d'avis + 5)** ; le 5 et le 4 sont des réglages.
- Julie, 1 avis à 5 ★ : (5 + 20) ÷ 6 = 4,17.
- Sophie, 40 avis à 4,8 ★ : (192 + 20) ÷ 45 = 4,71 → Sophie passe devant Julie.
- Marc, 30 avis à 4,2 ★ : (126 + 20) ÷ 35 = 4,17.
Le client voit toujours la **vraie** note et le nombre d'avis (« 5 ★ · 1 avis »).
**Pourquoi :** un seul avis (peut-être d'un ami) ne suffit pas pour être premier.

## La distance est affichée, sans changer l'ordre (décidé le 30/09/2026)
Chaque résultat affiche sa distance (« à 25 km ») ; l'ordre reste celui de la note. Le client peut trier lui-même par distance (« Les plus proches »).
- Exemple : Mme Dupont (Talence) → 1) Sophie, 4,71, « à 25 km » (Bordeaux) ; 2) Marc, 4,17, « à 5 km » (Pessac). Avec « Les plus proches » : Marc puis Sophie.

## Une carte par prestataire (décidé le 30/09/2026)
Chaque résultat est un prestataire, avec ses annonces du métier cherché résumées ; un clic ouvre sa **page publique** (profil + annonces en ligne).
- Exemple : « Karim Benali · Plombier · 4,5 ★ (8 avis) · à 5 km · à partir de 40 € · 3 annonces ».
- « À partir de » : le plus petit prix des annonces du métier (prix fixe, ou prix de l'heure) ; « Sur devis » s'il n'a que des annonces sur devis.
**Pourquoi :** un prestataire avec 20 annonces ne remplit jamais la page.

## Quatre filtres (décidé le 30/09/2026)
Cases à cocher au-dessus des résultats ; chacune cache ceux qui ne conviennent pas (décocher les fait revenir) :
- **« Vient chez moi »** : cache ceux qui ne travaillent que chez eux (salon, atelier) pour ce métier.
- **« Paiement par carte »** : cache ceux qu'on ne peut payer qu'en espèces.
- **« Libre dans les 7 jours »** : cache ceux qui n'ont aucun horaire libre dans les 7 prochains jours.
- **« Prix maximum »** (ex. 60 €) : cache ceux dont le prix « à partir de » est plus cher ; ceux « sur devis » restent.
- Exemple : 12 plombiers pour Talence ; Mme Dupont coche « Paiement par carte » → il en reste 7.

## Précisions proposées par Claude (validées par Raphael le 30/09/2026)
- La recherche marche **sans compte** (comme la page d'une annonce).
- **Aucun résultat** : « Aucun plombier ne vient à Talence pour l'instant. » + les métiers du même dossier à essayer (ex. « Chauffagiste », « Dépannage »).
- Au-delà de 30 résultats : pages de 30 (CONVENTIONS-IHM).
- À note de classement égale : le plus proche d'abord, puis le plus ancien sur rafals.

## Qui peut faire quoi
| Action | Qui | Condition |
|---|---|---|
| Chercher un prestataire | Tout le monde, même sans compte | — |
| Apparaître dans les résultats | Un prestataire | Activité active ; au moins une annonce en ligne du métier cherché ; ville du client dans son rayon |

## Questions ouvertes
- (aucune)

## Références
- `RM-PRESTATAIRES.md`, `RM-METIERS.md`, `RM-ANNONCES.md`, `RM-AVIS.md` (à écrire)
