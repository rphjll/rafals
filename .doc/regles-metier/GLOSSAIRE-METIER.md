# rafals — Glossaire métier

Un mot = une définition = un seul sens dans tout le projet. Ce fichier ne décrit pas les tables : un objet peut s'étendre sur plusieurs tables.

> Phase 4 du démarrage : définitions proposées par Claude et tranchées une à une par Raphael le 27/09/2026. Relu et validé par Raphael le 27/09/2026.

## Les grands objets
Prestataire, Client, Annonce, Rendez-vous, Facture, Paiement, Site vitrine, Démarche administrative, Métier, Catégorie de métier, Avis, Devis, Commission.
Liste de départ : d'autres objets seront ajoutés (voir `PRESENTATION.md`).

## Prestataire
Personne ou société qui propose des services aux clients via rafals : un auto-entrepreneur (ex. Julie Martin, ménage à domicile) ou une société (ex. « Plomberie Martin SARL »). Il a des Annonces, un agenda de Rendez-vous, émet des Factures, peut avoir un Site vitrine et suivre des Démarches administratives.
Exemple : Julie Martin, auto-entrepreneuse à Nantes, propose « Ménage 2 h — 50 € » et « Repassage 1 h — 20 € ».
À ne pas confondre avec : **Client** (celui qui achète le service). Une même personne peut être les deux avec **un seul compte** (validé par Raphael le 27/09/2026) : ex. Julie Martin, prestataire de ménage, cherche aussi un plombier pour chez elle, avec la même adresse mail et le même mot de passe.
Un Prestataire a **un calendrier par métier** (décidé par Raphael le 03/10/2026, `RM-AGENDA.md`), jamais un par salarié : une société avec plusieurs salariés n'a qu'un calendrier pour un métier (validé par Raphael le 27/09/2026) : ex. Mme Dupont réserve « Net & Clair, mardi 9 h » ; c'est Net & Clair qui décide si Sonia, Léa ou Maria y va. Le choix de la personne pourra venir plus tard.
Un futur auto-entrepreneur (pas encore de SIRET) a déjà un compte Prestataire, qu'il **garde** quand il reçoit son SIRET : rien à ressaisir (validé par Raphael le 27/09/2026). Ex. Karim s'inscrit pour se faire aider à déclarer son activité de plombier, puis écrit son SIRET dans le même compte.
Prestataire **sans SIRET** (réponse de Raphael le 27/09/2026, mot pour mot : « non en faite dans le site faura lui conseiller d'avoir un siret mais si il n'en a pas juste il peut faire des publications mais il peut que payer en liquide directement quand il rend le service ») :
- rafals lui conseille de se déclarer pour obtenir un SIRET ;
- il peut quand même faire des « publications », c'est-à-dire des **Annonces** (précisé par Raphael le 27/09/2026) ;
- le client ne peut le payer qu'**en espèces**, directement chez lui, le jour du service ; pas de paiement par carte sur le site.
⚠️ **À faire vérifier par un professionnel du droit avant la mise en ligne** : aider des personnes non déclarées à se faire payer régulièrement en espèces peut être considéré comme du travail non déclaré, et engager la responsabilité de rafals (alerte donnée par Claude le 27/09/2026).
Prestataire **avec SIRET** : pour chaque annonce, il choisit le mode de paiement : **par carte sur le site**, ou **en espèces chez le client**.

## Client
Particulier qui cherche un prestataire, prend rendez-vous et paie le service. Il a des Rendez-vous, reçoit des Factures, fait des Paiements.
Exemple : Mme Dupont, Nantes, prend rendez-vous avec Julie Martin le mardi 14/10 à 9 h.
À ne pas confondre avec : **Prestataire**.

## Annonce
⚠️ **Mot retiré : décision de Raphael du 04/10/2026.** Il n'y a plus d'annonce : le Prestataire se présente par son profil, le Client publie une **Demande**, et le prix, le jour et l'heure sont dans la **Proposition** du prestataire (`RM-PRESTATAIRES.md` § « Sans annonces », `RM-DEMANDES.md`). Pas encore construit (après les lots 8.3 et 8.4) : la définition ci-dessous décrit le code actuel.
Exemple 1 : Mme Dupont publie la demande « Tondre ma pelouse samedi à Pessac, 40 € » ; Tom propose « 35 € · samedi 10/10 à 10 h ».
Exemple 2 : M. Petit écrit à Karim depuis son profil ; Karim propose « 60 € · lundi 12/10 à 8 h 30 ».

Un service qu'un Prestataire met en ligne pour être trouvé et réservé, avec un nom, une durée ou un tarif, une ville, et les modes de paiement qu'il accepte pour ce service. Appartient à un seul Prestataire. Mot choisi par Raphael le 27/09/2026 : on dit **annonce** partout (écrans, code, documents), jamais « publication » ni « prestation ».
Exemple 1 : « Ménage 2 h — 50 € — Nantes — carte sur le site ou espèces » (Julie Martin, avec SIRET).
Exemple 2 : « Plomberie, dépannage fuite — 40 €/h — Pessac — espèces seulement » (Karim, sans SIRET).
À ne pas confondre avec : **Rendez-vous** (le service réalisé pour un client à une date donnée).

## Rendez-vous
Un créneau dans l'agenda d'un Prestataire, réservé par un Client pour une Annonce.
Exemple : « Mme Dupont — Ménage 2 h — mardi 14/10/2026 de 9 h à 11 h — chez Julie Martin ».
À ne pas confondre avec : **Annonce** (le service proposé, sans date ni client).

## Facture
Document émis par un Prestataire à un Client pour un ou plusieurs Rendez-vous réalisés, avec un numéro qui se suit sans trou.
Exemple : « F-2026-0012 — Julie Martin → Mme Dupont — Ménage 2 h du 14/10/2026 — 50 € ».
À ne pas confondre avec : **Paiement** (l'argent reçu ; une facture peut être payée en plusieurs fois, ou pas encore payée).

## Paiement
Somme versée par un Client à un Prestataire pour une Facture ou un Rendez-vous, avec son mode (en ligne, espèces, chèque, virement…). En ligne, l'argent passe par un service de paiement agréé et va directement au Prestataire : rafals ne le garde jamais.
Exemple : « 50 € — carte bancaire en ligne — 14/10/2026 — facture F-2026-0012 ».
À ne pas confondre avec : **Facture**.

## Site vitrine
Site internet d'un Prestataire, créé à partir d'un modèle (repris de vitrine-express) et publié sur un sous-domaine de rafals.
Exemple : « julie-menage.rafals.fr », modèle « Classique », style bleu.
Prix du site vitrine pour le prestataire : **pas encore décidé** — soit un abonnement, soit un prix payé une fois pour avoir le site à vie (Raphael, 27/09/2026 : « je sais pas encore faudra voire ca ensemble »).
À ne pas confondre avec : la **page profil** du prestataire dans les résultats de recherche de rafals.

## Démarche administrative
Une tâche administrative qu'un Prestataire (ou futur auto-entrepreneur) doit faire, que rafals l'aide à préparer ou fait à sa place quand c'est autorisé.
Exemple 1 : « Déclaration URSSAF du chiffre d'affaires de septembre 2026 — à faire avant le 31/10/2026 ».
Exemple 2 : « Création de l'auto-entreprise de Karim — étape 2 sur 5 : choix de l'activité ».

## Métier
Une activité professionnelle, choisie dans une grande liste qui doit contenir **tous les métiers qui existent** (demande de Raphael le 27/09/2026). Chaque Annonce est rangée sous un Métier ; c'est ce qui permet au client de la trouver. Chaque Métier appartient à une Catégorie de métier. Le client le trouve de deux façons : en ouvrant une catégorie, ou en tapant les premières lettres du nom (« plom » → Plombier), comme dans vitrine-express.
Exemple 1 : « Plombier », catégorie « Maison & travaux ».
Exemple 2 : « Fleuriste », catégorie « Commerces ».
À ne pas confondre avec : **Annonce** (un service précis d'un prestataire précis ; ex. « Plomberie, dépannage fuite, Pessac, 40 €/h » de Karim est une annonce du métier « Plombier »).

## Catégorie de métier
Un « dossier » qui regroupe des Métiers voisins, pour que le client s'y retrouve dans la grande liste (mot de Raphael : une « rubrique »). Point de départ : les 10 catégories de vitrine-express (Beauté & bien-être, Restauration, Commerces, Maison & travaux, Auto & transport, Santé, Sport & loisirs, Événements, Animaux, Services).
Exemple : la catégorie « Commerces » contient Fleuriste, Boulanger, Fromager…
À ne pas confondre avec : **Métier**.

## Avis
Une note (de 1 à 5 étoiles) et un petit texte laissés par un Client après un Rendez-vous, visibles par les autres clients sur les Annonces du Prestataire. Seul un client qui a eu un vrai rendez-vous peut en laisser un, ce qui évite les faux avis (validé par Raphael le 27/09/2026).
Exemple : « ★★★★★ Mme Dupont, 16/10/2026 : ponctuel et soigneux » sur l'annonce « Plomberie, dépannage fuite » de Karim.
À ne pas confondre avec : une réclamation ou un litige (un problème à régler par l'administrateur).

## Devis
Un prix proposé par un Prestataire à un Client **avant** de faire le travail, que le client accepte ou refuse sur rafals. Une fois le travail fait, la Facture est fabriquée à partir du devis accepté, sans tout ressaisir (validé par Raphael le 27/09/2026). Sert quand le prix dépend du travail (bâtiment, déménagement, événement…).
Exemple : « D-2026-003 — Karim → Mme Dupont — salle de bain complète — 1 800 € — accepté le 20/10/2026 ».
À ne pas confondre avec : **Facture** (émise après le travail ; c'est elle qui compte pour les impôts) ; **Annonce** (prix public affiché pour tous, pas pour un client précis).

## Commission
Le petit pourcentage que rafals garde sur chaque Paiement par carte fait sur le site ; le reste va directement au Prestataire (décidé par Raphael le 27/09/2026 : « la comission ca c sur »). Pourcentage à fixer. Rien sur les paiements en espèces, puisque l'argent ne passe pas par rafals.
Exemple (avec 5 %) : Mme Dupont paie 50 € par carte → Julie reçoit 47,50 €, rafals 2,50 €.
À ne pas confondre avec : le prix du **Site vitrine** (payé par le prestataire à rafals, pas pris sur les paiements des clients).

## SIRET
Le numéro d'identité d'une entreprise (14 chiffres), donné par l'État quand une personne ou une société déclare son activité. Il doit figurer sur les factures. Un auto-entrepreneur en a un dès qu'il est déclaré.
Exemple : Julie Martin, auto-entrepreneuse de ménage depuis 2024 : SIRET 912 345 678 00014. Karim, pas encore déclaré : pas de SIRET.

## Cycle de vie (valable pour tous les objets)
- **Désactiver** : réversible (ex. Julie met en pause son annonce « Repassage » pendant l'été).
- **Clôturer** : définitif (ex. un rendez-vous passé et payé).
- **Supprimer** : interdit dès que l'objet a servi (ex. une annonce qui a déjà eu un rendez-vous ne se supprime pas, elle se désactive).
