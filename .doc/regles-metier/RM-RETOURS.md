# « Un problème ? Une idée ? » — Règles métier

> Lot 13.1 (niveau 13, « Tri et corrections de la nuit »). Demande de Raphael du 09/11/2026 : les utilisateurs signalent les bugs et proposent des idées ; chaque soir, une routine les trie, corrige les bugs et prépare les idées (lots 13.2 et 13.3). Règles écrites avec Raphael, une question à la fois. **Écrit le 09/11/2026 (6 réponses de Raphael) et validé par Raphael le 09/11/2026 (« oui »), décisions de Claude comprises.**

## À quoi il sert
Julie M., cliente à Rezé, appuie sur [Publier ma demande] et rien ne se passe. Elle ouvre « Un problème ? Une idée ? », écrit « le bouton Publier ne répond pas sur mon téléphone » et envoie. Karim, électricien, y écrit « ce serait bien de pouvoir mettre une vidéo de mon travail ». La routine du soir lit ces messages : le premier est un bug, le second une idée.

## Qui peut envoyer (réponse 1, 09/11/2026 : « Comptes connectés »)
1. Seules les personnes **connectées à leur compte** (client ou prestataire) voient le bouton et peuvent envoyer.
2. Pourquoi : on sait qui a écrit (on peut le prévenir quand c'est corrigé) et un compte qui envoie des faux bugs piégés peut être bloqué.
3. Un visiteur sans compte ne voit pas le bouton.

## Où est le bouton (réponse 2, 09/11/2026 : « Menu du compte »)
4. Sur ordinateur : dans le menu du compte (clic sur le prénom en haut à droite), après « Paramètres » (et « Administration » pour un administrateur), avant « Se déconnecter ».
5. Sur téléphone : dans la liste du compte du menu ☰, même place. (Précisé le 09/11/2026 : « l'onglet Moi » n'existe que dans la grande maquette ; le vrai site range le compte dans ☰.)
6. Aucun bouton fixé sur les pages : rien ne cache le contenu.

## Problème ou idée (réponse 3, 09/11/2026 : « il le dis lui meme mais tu fais quand meme la verification au cas ou il ne se soit pas trompé »)
7. En haut de la fenêtre, l'utilisateur choisit [Un problème] ou [Une idée]. La phrase d'exemple suit son choix : « Ex. Le bouton Publier ne répond pas » / « Ex. Pouvoir mettre une vidéo de mon travail ».
8. La routine du soir vérifie ce choix et le corrige si l'utilisateur s'est trompé. Ex. « Idée : le bouton Publier ne marche pas » → traité comme un problème ; « Problème : il manque un mode sombre » → traité comme une idée. Le choix d'origine est gardé, la correction est notée à côté.

## Capture d'écran (réponse 4, 09/11/2026 : « Oui, 1 image facultative »)
9. Sous le texte : [+ Ajouter une capture d'écran], facultatif, **une seule image**, JPG ou PNG, 5 Mo au plus (comme les photos des demandes). Ex. Julie joint la photo de son écran où le bouton Publier est coupé.
10. L'image est rangée dans le « placard » à fichiers (Garage en local, S3 d'OVH en ligne) et **effacée quand le problème est réglé** ou l'idée refusée.

## L'utilisateur est prévenu (réponse 5, 09/11/2026 : « Oui, une notification »)
11. Au moment de l'envoi : « Merci, c'est envoyé. Nous regardons chaque soir. »
12. Ensuite, une **notification rafals** (pas de mail) quand son message est traité :
    - problème corrigé : « Merci Julie ! Le problème que vous avez signalé le 09/11 (bouton Publier) est corrigé. » ;
    - idée acceptée et ajoutée : « Votre idée (vidéo de votre travail) a été ajoutée à rafals. » ;
    - idée refusée : « Merci pour votre idée, elle n'est pas prévue pour l'instant. »

## Limite contre les abus (réponse 6, 09/11/2026 : « 5 par jour »)
13. Au plus **5 messages par compte et par jour** (de minuit à minuit, heure de Paris). Au 6ᵉ : « Vous avez déjà envoyé 5 messages aujourd'hui, merci ! Vous pourrez en envoyer d'autres demain. »
14. Pourquoi : un compte malveillant ne peut pas remplir la file de la nuit ni consommer tous les jetons Claude.

## Décisions de Claude, confirmées par Raphael le 09/11/2026
15. Texte de **10 à 2 000 caractères** (comme les signalements). Ex. « bug » seul est refusé : « Décrivez un peu plus (10 caractères au moins). »
16. Joint **automatiquement**, sans rien demander : la page où était l'utilisateur (ex. `/demandes/nouvelle`), ordinateur ou téléphone, et le navigateur (ex. Chrome sur Android). Rien d'autre : ni position, ni adresse. Pourquoi : la routine retrouve plus vite le bug.
17. Les gros mots passent par le même filtre que les avis (liste + IA de modération) : un message injurieux est gardé pour l'administrateur et n'est pas lu par la routine.

## Suite
Lots 13.2 (routine du soir) et 13.3 (page « Corrections et idées ») : règles à écrire dans ce fichier, à leur tour.
