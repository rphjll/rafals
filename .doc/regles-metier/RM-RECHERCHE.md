# Règle métier — Recherche (sujet 07)

> Validé et formalisé le 30/09/2026 (lot 4.0).

## Une rubrique par dossier de métiers (demande de Raphael du 07/10/2026, construit le même jour)
Demande, mot pour mot : « quand je suis dans l'onglet y'a la recherche en haut et en dessous y'a plein de rubriques et bah je veux que tu m'enelve toute ces bulles et que a la place tu me mette tout les prestataires mais dans une rubrique […] fait comme sur allo voisin », avec une capture d'écran d'AlloVoisins. Maquette validée (« oui c'est parfait la ») : `.doc/ihm/maquette-trouver-par-service.html`.
- **La ville d'abord** (choix de Raphael : « Demander la ville d'abord ») : tant que le site ne connaît pas la ville du visiteur, aucun prestataire n'est montré. La ville est retenue sur son appareil, pas dans son compte.
  - Exemple 1 : Julie ouvre « Trouver un prestataire » pour la première fois → « Indiquez votre ville pour voir les prestataires près de chez vous. »
  - Exemple 2 : elle tape « Pessac » et [Rechercher] → les rubriques de Pessac ; le lendemain, elles s'affichent sans rien redemander.
- **Une rubrique par dossier** (« Bricolage », « Jardinage »…), dans l'ordre des dossiers. Y sont les prestataires **actifs**, qui exercent un métier du dossier, et dont le **rayon** couvre la ville. Un dossier sans prestataire n'apparaît pas.
  - Exemple 1 : à Pessac, « Bricolage · 14 prestataires près de Pessac », « Jardinage · 9 prestataires près de Pessac » ; pas de rubrique « Coiffure » si aucun coiffeur ne vient à Pessac.
  - Exemple 2 : Luc, plombier à Libourne, jusqu'à 10 km → absent des rubriques de Pessac (47 km).
- **Une seule carte par prestataire dans une rubrique** (choix de Claude) : avec son métier principal s'il est dans ce dossier, sinon son premier métier secondaire du dossier (« aussi plombier »). Il peut être dans deux rubriques.
  - Exemple 1 : Karim, électricien (principal) et plombier (secondaire), deux métiers du même dossier → une carte « Électricien ».
  - Exemple 2 : Karim, plombier (principal) et coiffeur (secondaire) → une carte « Plombier » dans un dossier, une carte « aussi coiffeur » dans l'autre.
- **Ordre dans une rubrique** : le même que la recherche (métier principal d'abord, puis les mieux notés, puis les nouveaux, puis le plus proche).
- **10 cartes par rubrique** (réglage `RECHERCHE_CARTES_PAR_RUBRIQUE`, choix de Claude), puis [Voir tout] : tout le dossier, 30 par page.
- **Carte** : photo de profil ou initiales, nom, métier, « Pessac · à 2 km », « SIRET vérifié » ou « Particulier » (sans SIRET vérifié), les **2 premières photos de son travail** (choix de Raphael : « Oui, tout de suite » ; réglage `RECHERCHE_PHOTOS_SUR_CARTE`), la note et le nombre d'avis ou « Nouveau sur rafals ». Pas de prix. Pas repris d'AlloVoisins : « Profil boosté », « En ligne à 15:36 ».
- ⚠️ À faire vérifier : le mot « Particulier » pour un prestataire dont le SIRET est absent, à vérifier ou refusé (choix de Claude, repris de la capture).

## Sans annonces (décision de Raphael du 04/10/2026 ; construit le 07/10/2026 et le 09/10/2026, lot 9.2)
> **Construit le 07/10/2026**, en avance sur le lot 9.1, pour que les rubriques ne soient pas vides : la condition « au moins une annonce en ligne » a disparu de la recherche. Tant que les annonces existent, celles d'un prestataire donnent encore son prix et servent aux filtres : avec « Vient chez moi », « Paiement par carte » ou « Libre dans les 7 jours », un prestataire sans annonce n'est pas montré (choix de Claude, jusqu'au lot 9.2).

Les annonces sont retirées (`RM-PRESTATAIRES.md` § « Sans annonces »). Après les lots 8.3 et 8.4, ce fichier se lira ainsi (choix de Claude, proposés avec le MLD `MLD-retrait-annonces.html`) :
- **Qui apparaît** : un prestataire dont l'activité est active, qui exerce le métier cherché (principal ou secondaire, pas arrêté) et dont le rayon couvre la ville du client. La condition « au moins une annonce en ligne » disparaît.
- **Carte d'un résultat** : nom, photo, ville, distance, « Nouveau » ou la note et le nombre d'avis, « vient chez vous » et « carte bancaire acceptée ». Plus de « à partir de 40 € » ni de nombre d'annonces.
  - Exemple 1 : « Karim Benali · Plombier · 4,5 ★ (8 avis) · à 5 km · vient chez vous ».
  - Exemple 2 : « Julie Martin · Ménage · Nouveau · à 2 km · carte bancaire acceptée ».
- **Page publique** : profil, photos de son travail, avis, et les boutons [Écrire à Karim] et [Demander un devis] (SIRET vérifié seulement). Plus de liste d'annonces.
- L'ordre des résultats ne change pas (métier principal d'abord, puis les mieux notés).

**Construit le 09/10/2026 (lot 9.2)** : la carte d'un résultat n'a plus de prix ni de nombre d'annonces ; la page publique n'a plus de liste d'annonces.
- **Filtres (choix de Claude)** : il reste « Vient chez moi » (lieu du profil : « chez le client » ou « les deux ») et « Paiement par carte » (SIRET vérifié et paiement par carte activé). « Prix maximum » et « Libre dans les 7 jours » sont retirés : il n'y a plus de prix affiché, et le client ne voit plus les horaires libres.
  - Exemple 1 : Léa reçoit au salon (lieu « chez moi ») → elle disparaît avec le filtre « Vient chez moi ».
  - Exemple 2 : Julie a un SIRET vérifié et a activé la carte → elle reste avec le filtre « Paiement par carte » ; Paul, sans SIRET, disparaît.

## Objectif
Comment un client trouve un prestataire : un métier + une ville, et l'ordre des résultats.

## Déjà décidé (sujets 02, 04, 05)
- Le client cherche un **métier** (par les premières lettres ou par dossier, `RM-METIERS.md`) et une **ville**.
- Un prestataire apparaît si la ville du client est dans son **rayon** (distance à vol d'oiseau, `RM-PRESTATAIRES.md`). ~~Et seulement s'il a au moins une annonce en ligne de ce métier~~ : condition enlevée le 07/10/2026 (voir « Sans annonces »).
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

## Précisions prises au lot 4.1 (proposées par Claude, validées par Raphael le 30/09/2026)
- **Page publique d'un prestataire** (`/prestataires/12`) : nom, photo, présentation, ville et rayon, métiers exercés, badge « SIRET vérifié », annonces en ligne (comme la page d'une annonce : jamais la rue ni le téléphone). Visible seulement si l'activité est active ; son auteur la voit toujours (aperçu).
- **Carte d'un résultat** : nom, photo, ville de départ, distance arrondie au km, « Nouveau » ou la note et le nombre d'avis, « à partir de 40 €/h » ou « à partir de 50 € » (ou « Sur devis »), nombre d'annonces, « vient chez vous » et « carte bancaire acceptée » si c'est le cas.
- **« Libre dans les 7 jours »** : aujourd'hui et les 6 jours suivants, en tenant compte des délais « au plus tôt / au plus tard » du prestataire.
- **Prix maximum** : saisi en euros (« 60 »).
- **Métiers voisins** : 5 au plus, ceux du même dossier, par ordre alphabétique.

## Qui peut faire quoi
| Action | Qui | Condition |
|---|---|---|
| Chercher un prestataire | Tout le monde, même sans compte | — |
| Apparaître dans les résultats | Un prestataire | Activité active ; au moins une annonce en ligne du métier cherché ; ville du client dans son rayon |

## Questions ouvertes
- (aucune)

## Références
- `RM-PRESTATAIRES.md`, `RM-METIERS.md`, `RM-ANNONCES.md`, `RM-AVIS.md` (à écrire)
