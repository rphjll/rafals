# Ma carte de visite — Règles métier

> Lot 10.4. Demande d'origine (07/10/2026, liste « faire ce que fait AlloVoisins ») : « Oui, carte de visite » (pas de prospectus). Règles écrites le 22/10/2026 avec Raphael, une question à la fois. Écran : `ihm/RM-CARTE-VISITE-IHM.md` (à écrire avec la maquette).

## À quoi elle sert
Karim, plombier à Pessac, donne sa carte à un client sur un chantier ou la laisse chez un commerçant. Le client scanne le carré avec son téléphone : il arrive sur la page publique de Karim sur rafals (ses avis, ses photos, [Écrire à Karim], [Demander un devis]).

## Ce qu'il y a sur la carte (un seul côté, 8,5 × 5,5 cm)
1. Le nom affiché, ex. « Karim Benali ».
2. Le métier principal, ex. « Plombier » ; un métier secondaire en plus s'il tient sur la ligne, ex. « Plombier · Chauffagiste ».
3. La ville, ex. « Pessac ».
4. La note : « 4,8/5 · 23 avis sur rafals ». Sans aucun avis : « Nouveau sur rafals ».
5. Le téléphone, **seulement si Karim coche** « Mettre mon téléphone sur la carte » (réponse de Raphael du 22/10/2026 : « oui si il veut »), ex. « 06 12 34 56 78 ». C'est le numéro de son compte (« Mes informations »). Sans numéro dans son compte : la case est verrouillée 🔒 « Ajoutez d'abord votre téléphone dans Mon profil › Mon compte › Mes informations. »
6. Le carré à scanner (un *QR code*) vers sa page publique, ex. `https://rafals.fr/prestataires/12`, avec dessous « Mes avis et mes photos ».
7. En petit, en bas : « rafals. ».

Le PDF n'est jamais enregistré : la carte est fabriquée au moment du téléchargement avec ce qui est dans son profil ce jour-là (comme le PDF d'une facture). Seules la couleur et la petite phrase sont gardées (voir plus bas).

## Couleur et petite phrase (ajoutées le 22/10/2026)
Demande de Raphael, mot pour mot : « ok mtn faut pouvoir choisir les couleurs et la modif un peu ». Réponses : « toute pretes », « ajouter un ptite phrase », gardées d'une visite à l'autre (« oui »). MLD validé : `.doc/mld/MLD-carte-visite.html` ; `db/schema_v33.sql` (rubriques `prestataire.carte_couleur` et `prestataire.carte_phrase`).
- **6 couleurs toutes prêtes** : Vert rafals `#2F6B4F` (au départ), Bleu nuit `#1D3A5F`, Orange `#C4561B`, Bordeaux `#7A1F2B`, Violet `#4B2E83`, Noir `#1D2620`. La couleur va sur le nom, sur une bande de 3 mm sur le côté gauche de la carte et sur le carré à scanner. Toutes assez foncées pour rester lisibles et se scanner. Une autre couleur est refusée : « Choisissez une des 6 couleurs proposées. »
- **Une petite phrase** facultative, 40 caractères au plus, imprimée sous la ville, ex. « Devis gratuit, intervention sous 48 h ». Même filtre que les avis et les messages (mots interdits, IA de modération). Trop longue : « La petite phrase doit faire entre 1 et 40 caractères. » Vide (ou seulement des espaces) : pas de phrase.
- [Enregistrer ma carte] garde la couleur et la phrase. Les PDF téléchargés prennent **ce qui est affiché** sur la page, même pas encore enregistré ; télécharger n'enregistre rien.
- Enregistrer est refusé dans les mêmes cas que télécharger (sans SIRET vérifié, profil pas actif).

## Deux PDF (réponse de Raphael du 22/10/2026 : « les 2 »)
- **[Télécharger la planche à découper]** : une page A4 avec **10 cartes identiques** (2 colonnes × 5 lignes), avec de petits repères de coupe dans les marges. Pour imprimer chez soi sur du papier épais.
- **[Télécharger pour un imprimeur]** : **une seule carte** au format exact (8,5 × 5,5 cm), pour un imprimeur en ligne ou en boutique.

## Qui peut la télécharger
- Seulement un prestataire **avec un SIRET vérifié** (réponse de Raphael du 22/10/2026, corrigée aussitôt : « non pardon ma reponse est plutot pas de carte sans siret »). Sans SIRET vérifié : les deux boutons sont verrouillés 🔒 « Les cartes de visite sont réservées aux prestataires avec un SIRET vérifié. » avec [Créer mon auto-entreprise] / [Ajouter mon SIRET] comme dans « Sans SIRET : vos limites ».
- Le profil doit être **actif** : en pause, bloqué ou arrêté, sa page publique est fermée et le carré mènerait à une page vide. Boutons verrouillés 🔒 « Votre profil est en pause : sa page publique est fermée, le carré à scanner ne mènerait nulle part. Reprenez votre activité d'abord. » (bloqué / arrêté : même idée).

## Comment le carré est fabriqué
Bibliothèque libre `segno` (choix de Raphael du 22/10/2026 : « bibliothèque »), ajoutée dans `backend/requirements.txt` ; conteneur `backend` reconstruit le 22/10/2026. Niveau de correction d'erreur « M » (lisible même un peu abîmé). L'adresse vient du réglage `ADRESSE_SITE` (`backend/app/config.py`) : sur le PC de Raphael c'est `http://localhost:5174`, qu'un téléphone ne peut pas ouvrir ; en ligne, ce sera l'adresse du vrai site.

## Décisions prises par Claude, à confirmer
- La note s'écrit « 4,8/5 » et non « 4,8 ★ » : les PDF de rafals utilisent les polices de base, qui n'ont pas l'étoile.
- Fond blanc, sans bord perdu : un imprimeur n'a pas besoin de marge de coupe en plus.
- Un seul métier secondaire au plus, pour que la carte reste lisible.
