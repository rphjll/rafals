# Installer rafals sur ton PC (Windows)

rafals tourne entièrement sur ton PC, dans Docker. Rien n'est envoyé sur Internet : les mails restent dans une page de test, les paiements par carte sont coupés.

## Ce qu'il te faut

1. **Git** : https://git-scm.com/download/win (installe avec les choix proposés).
2. **Docker Desktop** : https://www.docker.com/products/docker-desktop/ (redémarre le PC si on te le demande).
3. Environ **10 Go** de place libre (l'IA qui relit les avis pèse à elle seule 2 Go).

## Installation (une seule fois)

1. Lance **Docker Desktop** et attends que la baleine, en bas à droite de l'écran, ne bouge plus.
2. Ouvre le menu Démarrer, tape `cmd`, puis Entrée, et copie ces deux lignes :
   ```
   cd C:\
   git clone https://github.com/rphjll/rafals.git
   ```
   Le projet est maintenant dans `C:\rafals`.
3. Ouvre le dossier `C:\rafals` et **double-clique sur `installer.bat`**.

`installer.bat` fait tout, dans l'ordre :
1. il vérifie que Docker est lancé ;
2. il crée ton fichier de réglages `.env`, avec des mots de passe tirés au hasard rien que pour toi ;
3. il construit et démarre les boîtes Docker (la première fois : 10 à 20 minutes) ;
4. il attend que la base de données soit prête ;
5. il crée toutes les tables (les fichiers `db\schema_v1.sql`, `schema_v2.sql`… dans l'ordre) ;
6. il prépare le placard à fichiers (photos, factures) ;
7. il charge les listes de départ : les communes de France, les métiers, les mots interdits dans les avis.

À la fin, le site s'ouvre tout seul : **http://localhost:5174**.

Si une étape échoue, lis le message, corrige (par exemple : lance Docker Desktop), puis relance `installer.bat`. Ce qui est déjà fait est gardé, rien n'est effacé.

## Ensuite

- **Créer ton compte** sur le site. Le mail de vérification arrive dans la page des mails de test : **http://localhost:8025**.
- **Devenir administrateur** : double-clique sur `nommer-premier-administrateur.bat` et tape l'adresse mail de ton compte.
- **Les fois suivantes** : `demarrer.bat` pour lancer rafals, `arreter.bat` pour l'arrêter.
- **Recevoir les nouveautés** : dans `cmd`, tape `cd C:\rafals` puis `git pull`, puis double-clique sur `demarrer.bat`. Si une nouveauté ajoute un fichier `db\schema_vXX.sql`, il faut l'exécuter une fois (la commande est écrite en haut du fichier).

## Les services extérieurs (facultatif)

Sans rien faire, tout marche en mode essai. Ces trois services demandent **ton propre compte** ; ne demande jamais les clés de quelqu'un d'autre, ce sont des secrets :

| Service | Sans compte | Avec ton compte |
|---|---|---|
| Stripe (paiement par carte) | seulement les espèces | ajoute `STRIPE_CLE_SECRETE` et `STRIPE_SECRET_WEBHOOK` (mode test) dans `.env` |
| INPI (créer une auto-entreprise) | mode démonstration | ajoute `INPI_IDENTIFIANT` et `INPI_MOT_DE_PASSE` |
| URSSAF (déclarer le chiffre d'affaires) | bouton verrouillé | ajoute `URSSAF_IDENTIFIANT` et `URSSAF_SECRET` |

Après une modification de `.env`, relance `demarrer.bat`.

La vérification des SIRET, les adresses et les cartes (OpenStreetMap) marchent sans compte.

## À ne jamais faire

- Envoyer ton fichier `.env` à quelqu'un, ou le mettre sur GitHub : il contient tes mots de passe.
- Supprimer les « volumes » de Docker : tu perdrais ta base de données.
