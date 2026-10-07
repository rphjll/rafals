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
