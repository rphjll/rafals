# Mon activité — Règles

> Écrit le 07/10/2026 pour le lot 10.1. Raphael a choisi « Oui, avec l'année » à la question « En haut de « Mon activité », est-ce que je mets des chiffres comme dans la maquette ? ». **Les définitions ci-dessous sont proposées par Claude : à valider par Raphael** (il a dit « commence par ce que tu veux en gros »). Écran : `ihm/RM-MON-ACTIVITE-IHM.md`.

## Principe
En haut de « Mon activité », quelques chiffres disent où on en est aujourd'hui. Ils se calculent tout seuls à partir de ce qui existe déjà dans rafals : **rien n'est enregistré en plus**. Chaque chiffre mène à la page qui le détaille.
- Exemple : Karim ouvre « Mon activité » un mercredi : il lit « 3 demandes près de chez vous » sans ouvrir aucune autre page.
- Exemple : Julie n'a rien en cours : elle lit « 0 demande en ligne », « 0 conversation à lire », « 0 rendez-vous à venir ».

## Qui voit quoi
- Un compte **avec** un profil de prestataire voit les chiffres du prestataire.
- Un compte **sans** profil de prestataire voit les chiffres du client.
- Personne n'est connecté : pas de chiffres.

## Chiffres du prestataire
| Chiffre | Ce qu'il compte exactement | Exemple | Un clic ouvre |
|---|---|---|---|
| Demandes près de chez vous | Les demandes de la page « Demandes près de chez moi » : ouvertes, d'un de ses métiers, dans son rayon | Karim, plombier à Pessac (15 km) : la fuite de Mme Dupont à Pessac compte ; la fuite à Libourne (40 km) ne compte pas | Demandes près de chez moi |
| Rendez-vous d'ici dimanche | Ses rendez-vous **confirmés** qui commencent entre maintenant et dimanche minuit (heure de Paris) | Mercredi 07/10 : le rendez-vous de vendredi 09/10 compte ; celui de mardi 06/10 (passé) et celui de lundi 12/10 ne comptent pas | Mon agenda |
| Devis en attente | Ses devis **envoyés** auxquels le client n'a pas encore répondu | Devis de 120 € envoyé à Julie, sans réponse : compte. Devis accepté ou refusé : ne compte plus | Devis |
| Encaissé ce mois-ci | Le « chiffre à déclarer » du mois en cours, tel que défini dans `RM-DEMARCHES.md` : factures de vente moins avoirs, à la date de la facture ; hors taxe s'il facture la TVA | Octobre : 50,00 € + 1 190,00 € + 60,00 € − 50,00 € (un avoir) = 1 250,00 € | Paiements |
| Encaissé cette année | La même somme, du 1er janvier à aujourd'hui | 5 320,00 € en 2026 | (pas de clic : c'est le bloc de la barre de la TVA) |

**Seulement ce qui passe par rafals** : ce que le prestataire encaisse ailleurs n'est pas compté (l'écran le dit).

## La barre de la TVA
- Elle n'existe que pour un prestataire qui **ne facture pas** la TVA (case « Je facture la TVA » non cochée, `RM-DEVIS.md` § « TVA »).
- Elle compare « Encaissé cette année » au **seuil de 37 500 €** au-delà duquel un auto-entrepreneur de services doit facturer la TVA.
  - Exemple : 5 320,00 € encaissés → « Il vous reste 32 180,00 € avant le seuil de TVA (37 500 €) », barre remplie à 14 %.
  - Exemple : 38 000,00 € encaissés → « Vous avez dépassé le seuil de TVA (37 500 €) : parlez-en à votre comptable ou à votre service des impôts. », barre pleine, en orange.
- **Deux notifications sur le téléphone** (demande de Raphael du 17/10/2026 : « une notif de la barre de TVA qnd elle est a 80% et quand elle est dépassée ») : au moment où une facture fait passer le total de l'année à 80 % du seuil, puis au-delà du seuil. Un clic ouvre « Mon activité ». Rien n'est enregistré : rafals compare le total avant et après la facture, donc chaque palier ne sonne qu'une fois.
  - Exemple 1 : Karim passe de 29 800 € à 30 050 € → « Vous approchez du seuil de TVA : Vous avez encaissé 30 050,00 € en 2026 : 80 % du seuil de TVA (37 500,00 €). Il vous reste 7 450,00 €. »
  - Exemple 2 : il passe de 37 400 € à 37 600 € → « Seuil de TVA dépassé : Vous avez encaissé 37 600,00 € en 2026, plus que le seuil de TVA (37 500,00 €) : parlez-en à votre comptable ou à votre service des impôts. »
  - **Un mail aussi**, avec le même texte (accord de Raphael du 17/10/2026 : « oui pour le mail »), pour celui qui n'a pas activé les notifications. Objet : « rafals : vous approchez du seuil de TVA » ou « rafals : seuil de TVA dépassé ».
  - Choix de Claude : une seule facture qui saute les deux paliers d'un coup donne seulement « Seuil de TVA dépassé » ; un avoir qui fait redescendre puis une nouvelle facture qui fait repasser le palier font sonner de nouveau.
- rafals **ne change rien tout seul** : il ne coche pas la case TVA à la place du prestataire.
- ⚠️ **À confirmer par un comptable avant la mise en ligne** : (1) le montant du seuil (37 500 € pour les services en 2026, 41 250 € pour le seuil dit « majoré », d'après des sites spécialisés lus le 07/10/2026 ; il change presque chaque année) ; (2) la vente de marchandises a un autre seuil, que rafals ne gère pas ; (3) le seuil se juge sur tout le chiffre d'affaires, y compris hors rafals.

## Chiffres du client
| Chiffre | Ce qu'il compte exactement | Exemple | Un clic ouvre |
|---|---|---|---|
| Demandes en ligne | Ses demandes publiées encore ouvertes | « Tondre ma pelouse », ouverte : compte. Une demande fermée ou expirée : ne compte pas | Mes demandes |
| Conversations à lire | Le même nombre que la pastille rouge de « Messages » : conversations avec du nouveau | Karim et Sofia ont écrit : 2 | Messages |
| Rendez-vous à venir | Ses rendez-vous **en attente ou confirmés** qui n'ont pas encore commencé | Rendez-vous de samedi 10/10 avec Karim : compte | Rendez-vous |

## Ce qui n'est pas fait
- Pas de comparaison avec le mois d'avant, pas de courbe.
- Pas de chiffres « client » pour un prestataire (il les retrouve dans « Mes demandes » et « Rendez-vous »).

---

# Mes clients (lot 10.2)

> Écrit le 07/10/2026. Raphael a choisi « Oui, clients de rafals » (pas de client saisi à la main), puis « Tout le résumé » pour ce que la liste montre. Les détails ci-dessous sont proposés par Claude : **à valider par Raphael**.

## Principe
Un prestataire voit la liste des personnes pour qui il a déjà travaillé, ou à qui il a envoyé un devis, **sur rafals**. Rien n'est enregistré en plus : la liste se calcule à partir de ses rendez-vous, de ses devis et de ses factures.
- Exemple : Julie a eu 2 rendez-vous avec Karim et lui a demandé 1 devis → elle est dans « Mes clients » de Karim.
- Exemple : Paul a seulement écrit un message à Karim, sans rendez-vous ni devis → il n'y est pas.

## Qui est dans la liste
Un compte y figure s'il a, avec ce prestataire, **au moins un rendez-vous confirmé** (passé ou à venir) **ou au moins un devis envoyé**.
- Un rendez-vous refusé, annulé ou encore en attente de confirmation ne suffit pas.
- Une demande de devis à laquelle le prestataire n'a pas répondu ne suffit pas.
- Chaque prestataire ne voit que ses propres clients, jamais ceux d'un autre.

## Ce qui est montré pour chaque client
| Rubrique | Ce que c'est | Exemple |
|---|---|---|
| Nom | Le nom complet tant que la règle des coordonnées le permet (voir plus bas), sinon le prénom et l'initiale | « Julie Martin », puis « Julie M. » |
| Rendez-vous | Le nombre de rendez-vous confirmés avec lui, passés et à venir | « 2 rendez-vous » |
| Devis | Le nombre de devis qu'il lui a envoyés, et combien attendent encore une réponse | « 1 devis », « 1 devis en attente » |
| Payé | Tout ce que ce client lui a payé par rafals : ses factures de vente moins ses avoirs (même calcul que le chiffre à déclarer, `RM-DEMARCHES.md`) | « 85,00 € payés » |
| Prochain ou dernier rendez-vous | Le prochain rendez-vous confirmé s'il y en a un, sinon le dernier, sinon « Pas encore de rendez-vous » | « Prochain rendez-vous : 10/10/2026 » |
| Téléphone | Seulement si la règle des coordonnées le permet | « 06 12 34 56 78 » |
| [Écrire à Julie] | Ouvre la conversation avec ce client (`RM-MESSAGERIE.md` : un prestataire peut écrire à un client qui a un rendez-vous ou un devis avec lui) | |

## Règle des coordonnées (déjà validée, `RM-CLIENTS.md`)
Le nom complet et le téléphone d'un client ne sont montrés que tant qu'il a un rendez-vous en cours avec ce prestataire, et jusqu'à **3 mois après le dernier**. « Mes clients » applique la même règle, sans exception.
- Exemple : dernier rendez-vous de Julie le 10/10/2026 → Karim voit « Julie Martin » et son téléphone jusqu'au 10/01/2027 ; ensuite « Julie M. », sans téléphone.
- Exemple : Nadia n'a qu'un devis, aucun rendez-vous → « Nadia B. », sans téléphone.
- L'adresse du client n'est **pas** dans la liste : elle reste sur chaque rendez-vous.

## Détail d'un client et profil (ajoutés le 07/10/2026)
Demande de Raphael, mot pour mot : « dans mes clients je veux que si je clic sur mon client y'ai un truc en dessous qui s'ouvre et y'a toute les info et un bouton voir le profil aussi », puis, pour le profil : « ca dois ouvrir le meem profil que les prestataires mais avec les infos que le client a mis du coup ».
- **Le détail** (sous la ligne du client) montre : son téléphone, l'adresse de son dernier rendez-vous chez lui, ce qu'il a payé, la liste de ses rendez-vous confirmés avec ce prestataire (jour, titre, prix, « à venir » ou « passé ») et la liste des devis que ce prestataire lui a envoyés (jour, numéro, total, état).
- **Le profil** est une page présentée comme la page publique d'un prestataire, mais **elle n'est pas publique** : seul un prestataire qui a ce client peut l'ouvrir (les autres, et les visiteurs, lisent « Cette personne ne fait pas partie de vos clients. »). Elle montre son nom, « Client · sur rafals depuis octobre 2026 », le même détail, et ses demandes encore en ligne (déjà visibles de tous sur l'accueil).
- Le téléphone, le nom complet et l'adresse suivent la règle des coordonnées ci-dessus : cachés 3 mois après le dernier rendez-vous, ou s'il n'y a qu'un devis.
  - Exemple : Julie, rendez-vous le 16/10/2026 → « Julie Martin », « 06 12 34 56 78 », « 8 allée des Pins, 33600 Pessac ».
  - Exemple : Hugo, dernier rendez-vous il y a 130 jours → « Hugo P. », téléphone et adresse cachés ; son rendez-vous reste dans la liste.
- Jamais montrés : son adresse mail, sa date de naissance, ses rendez-vous avec d'autres prestataires, ses absences.
- Un client n'a aujourd'hui ni photo ni texte de présentation : le profil montre ses initiales. En ajouter serait une évolution des données (MLD d'abord).

## Compte fermé
Un client qui a fermé son compte reste dans la liste sous le nom « Personne ayant quitté rafals », avec ses nombres et ce qu'il a payé (le prestataire en a besoin pour ses comptes), sans téléphone et sans bouton [Écrire].

## Ordre
Le client vu le plus récemment en premier : on regarde la date de son rendez-vous le plus récent (ou à venir) et celle de son dernier devis.

## Ce qui n'est pas fait
- Pas de client saisi à la main, pas d'import d'un fichier (choix de Raphael).
- Pas de note personnelle sur un client, pas d'export.
