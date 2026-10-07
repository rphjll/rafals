# Mon activité — Interface

> Fichiers : `frontend/src/pages/MonActivitePage.vue`, `frontend/src/outils/activite.ts` (la liste des fonctions), `frontend/src/composables/useMenu.ts`. Construit le 07/10/2026 (hors lot), d'après la maquette `maquette-mon-activite.html` (https://claude.ai/artifact/DURJoPoweoC7WLU7RUh4wu).
> Demande de Raphael du 07/10/2026, mot pour mot : « tu vois l'onglet abonnement de allo voisin avec beacoup de trucs dedans et bah tout ces trucs qui y'a dans mon compte bah je veux le mettre aussi dans 1 seul onglet qui s'appelera mon activité et l'onglet actuel mon activité il vas s'appeler mon profil », puis « y'en a quelques uns qui ne doivent pas etre dans mon activité par exemple messages c'est un onglet a pars », puis, sur la liste des 12 fonctions : « la cb la liste que tu m'a donné est bonne ».

## Où
- Entrée « Mon activité » du menu → `/mon-activite`. Elle remplace « Mes réservations » (choix de Raphael le 07/10/2026 : « Elle disparaît »).
- L'ancienne entrée « Mon activité » (la fiche du prestataire, `/proposer`) s'appelle **« Mon profil »** ; pour un compte sans profil de prestataire, elle s'appelle toujours « Proposer mes services ».
- « Messages » et « Mon profil » ne sont pas dans la page : ce sont des onglets à part.

## La page
De haut en bas :
1. Titre « Mon activité » et la phrase « Tout ce que vous faites sur rafals, au même endroit. »
2. Personne n'est connecté : bandeau gris « Connectez-vous pour voir votre activité. » et [Se connecter] (qui ramène ici après la connexion).
2 bis. **Les chiffres** (lot 10.1, construit le 07/10/2026 ; règles : `RM-MON-ACTIVITE.md`), lus sur `/api/moi/activite` à chaque ouverture de la page. Une petite carte par chiffre, le nombre en très gros et le texte en gris dessous ; 2 par ligne sur téléphone, 4 sur ordinateur ; un clic ouvre la page du détail. Si le serveur ne répond pas, la page s'affiche sans les chiffres.
   - Prestataire : « 3 » demandes près de chez vous → Demandes près de chez moi ; « 2 » rendez-vous d'ici dimanche → Mon agenda, onglet Rendez-vous ; « 1 » devis en attente de réponse → Devis ; « 640,00 € » encaissés en octobre → Mon agenda, onglet Paiements. Le texte s'accorde (« 1 demande près de chez vous »).
   - Dessous, pour un prestataire, une carte « Encaissé en 2026 » avec la somme à droite (« 5 320,00 € ») ; s'il ne facture pas la TVA, une barre verte remplie à la part du seuil atteinte et « Il vous reste 32 180,00 € avant le seuil de TVA (37 500,00 €). » ; seuil dépassé : barre pleine orange et « Vous avez dépassé le seuil de TVA (37 500,00 €) : parlez-en à votre comptable ou à votre service des impôts. » ; toujours la ligne « Seulement ce qui est passé par rafals : ajoutez vous-même ce que vous avez encaissé ailleurs. »
   - Client : « 1 » demande en ligne → Mes demandes ; « 2 » conversations à lire → Messages ; « 1 » rendez-vous à venir → Rendez-vous.
3. Des groupes de tuiles. Une tuile = un rond de couleur avec un pictogramme, le nom en gras, une ligne grise. Un clic ouvre la page. Survol : anneau vert.

| Groupe | Tuile | Ligne grise | Ouvre | Qui la voit |
|---|---|---|---|---|
| Trouver des clients | Demandes près de chez moi | Les clients qui cherchent mon métier | `/demandes-pres-de-chez-moi` | prestataire |
| | Alertes | Un mail à chaque nouvelle demande | *bientôt* (lot 8.6) | prestataire |
| | Être mis en avant | Apparaître en premier dans les résultats | *bientôt* (à construire) | prestataire |
| Gérer mon activité (pour un client : « Mes services ») | Mes demandes | Ce que j'ai publié, et les réponses | `/mes-demandes` | tous |
| | Mon agenda | Mes horaires et mes jours fermés | `/mon-agenda` | prestataire |
| | Rendez-vous | À venir et passés | `/rendez-vous` | tous |
| | Devis | Demandes de devis et devis envoyés | `/devis` | tous |
| | Factures | Toutes mes factures en PDF | `/factures` | tous |
| | Paiements | Ce que j'ai encaissé, par carte et en espèces | `/mon-agenda?onglet=paiements` | prestataire |
| | Paiements | Ce que j'ai payé par carte | `/compte` | client |
| | Mes clients | Les personnes pour qui j'ai déjà travaillé | *bientôt* (à construire) | prestataire |
| | Mes avis | À donner après un rendez-vous passé | `/rendez-vous?onglet=passes` | client |
| Me faire connaître | Mes avis | Ce que mes clients disent de moi | sa page publique `/prestataires/12` | prestataire |
| | Ma carte de visite | À imprimer, avec un carré à scanner | *bientôt* (à construire) | prestataire |
| | Mon site | Une page à mon nom, visible sur Google | *bientôt* (lots 6.5 et 6.6) | prestataire |
| Mes démarches | Déclarer à l'URSSAF | Mes déclarations et leurs rappels | `/demarches` | prestataire |
| | Mon auto-entreprise | La créer et suivre mon dossier | `/creer-mon-auto-entreprise` | prestataire |

4. **Tuile « bientôt »** (fonction pas encore construite) : contour en pointillés, badge orange « bientôt ». Un clic affiche le message court « « Alertes » n'est pas encore disponible : bientôt. » (un clic produit toujours quelque chose de visible).
5. Pour un compte sans profil de prestataire, en bas : bandeau gris « Vous proposez vos services ? Créez votre profil : les demandes des clients, l'agenda et les démarches s'ajoutent ici. » et [Proposer mes services].

Exemples : Julie (cliente) voit un seul groupe « Mes services » avec 6 tuiles (Mes demandes, Rendez-vous, Devis, Factures, Paiements, Mes avis). Karim (prestataire) voit 4 groupes et 15 tuiles, dont 5 « bientôt ».

## Sous-menu
Sur une page de « Mon activité » (Rendez-vous, Devis, Mon agenda…), le sous-menu sous l'en-tête montre : « ‹ Mon activité » (retour à la page d'ensemble), puis Mes demandes, Rendez-vous, Devis, Factures, et pour un prestataire Demandes près de chez moi, Mon agenda, Déclarer à l'URSSAF. Pas de sous-menu sur la page d'ensemble.

## Pas encore fait (décidé par Raphael le 07/10/2026, une question par fonction)
- **Mes clients** (« Oui, clients de rafals ») : les personnes avec qui le prestataire a eu un rendez-vous ou un devis sur rafals ; pas de client saisi à la main.
- **Relance d'un devis sans réponse** (« Prévenir Julie tout seul ») : un seul mail au client au bout de 3 jours.
- **Ma carte de visite** (« Oui, carte de visite ») : un PDF à imprimer avec le nom, le métier, la ville, la note et un carré à scanner vers la page publique ; pas de prospectus.
- **Être mis en avant** (« Oui, maintenant ») : payer pour apparaître en premier ; règles (prix, durée, étiquette), MLD et paiement à écrire d'abord.
