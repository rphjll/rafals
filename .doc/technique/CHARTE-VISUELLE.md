# rafals — Charte visuelle

> Choisie par Raphael le 28/09/2026 en regardant la maquette cliquable `.doc/ihm/maquette-charte.html` (https://claude.ai/artifact/K2WSEd51fSMiCsQ2S3s3R7) : ambiance **B. Vert sauge**, boutons **arrondis**.
> Ces valeurs sont recopiées telles quelles dans les réglages de Tailwind au lot des écrans ; on ne tape jamais une couleur à la main dans un écran.

> **Style « chaleureux » depuis le 07/10/2026** (choisi par Raphael, « A », sur la maquette `.doc/ihm/maquette-trois-styles.html`, puis `.doc/ihm/maquette-style-chaleureux.html`, https://claude.ai/artifact/3GejTyBQFa9dZXbrmmChQc) : les couleurs ne changent pas ; les polices et les formes changent (voir « Polices » et « Formes »). **Exception : l'écran « Mon agenda » garde les formes d'avant** (Raphael, 04/10/2026 : « l'agenda ne dois pas changer »).

## Couleurs

| Rôle | Nom technique | Mode clair | Mode sombre | Sert à |
|---|---|---|---|---|
| Fond de page | `fond` | `#F3F6F2` | `#121713` | Derrière tout |
| Surface | `surface` | `#FFFFFF` | `#1A211C` | Cartes, fenêtres, en-tête |
| Texte | `texte` | `#1D2620` | `#E7ECF2` | Texte principal |
| Texte secondaire | `texte-doux` | `#58665C` | `#A3AEBD` | Villes, dates, aides |
| Bordure | `bord` | `#D8E1DA` | `#2C3730` | Contours des cartes et des champs |
| **Couleur principale** | `primaire` | `#2F6B4F` (vert sauge) | `#79C49C` | Logo, bouton principal, prix, liens d'action |
| Texte sur couleur principale | `primaire-texte` | `#FFFFFF` | `#0F1A13` | Texte des boutons principaux |
| Principale très claire | `primaire-doux` | `#E2EEE7` | `#1C3024` | Survol, avatar, ligne sélectionnée |
| **Touche** | `accent` | `#D9793A` (orange) | `#F0955A` | Étoiles des avis, point du logo « rafals. », contour de focus clavier |

## Couleurs d'état (identiques quelle que soit l'ambiance)

| État | Texte clair / fond clair | Texte sombre / fond sombre | Exemples |
|---|---|---|---|
| OK | `#2E7D4F` / `#E3F2E8` | `#6CC592` / `#17301F` | « SIRET vérifié », « Rendez-vous confirmé » |
| En attente | `#B26A00` / `#FCF0DC` | `#F0B35A` / `#33260F` | « Sans SIRET », « Devis en attente » |
| Erreur / annulé | `#B3261E` / `#FBE4E2` | `#F08A82` / `#3A1A18` | « Rendez-vous annulé », message d'erreur |
| Neutre / interdit | `#8A94A3` sur `#E8ECF1` | `#6D7888` sur `#262E39` | Bouton verrouillé 🔒, « Espèces seulement » |

## Couleurs techniques (ajoutées au lot 0.4, 28/09/2026)
| Nom technique | Mode clair | Mode sombre | Sert à |
|---|---|---|---|
| `sur-etat` | `#FFFFFF` | `#0F1A13` | Texte posé sur une couleur d'état pleine (message court vert ou rouge) |
| `voile` | noir bleuté à 55 % | idem | Fond assombri derrière une fenêtre |

## Couleur du calendrier (ajoutée le 03/10/2026, demandée par Raphael : « un vert vif »)
| Nom technique | Mode clair | Mode sombre | Sert à |
|---|---|---|---|
| `ouvert` | `#5FD38A` | `#1F8A4A` | Fond d'un jour ouvert dans le calendrier de « Mon agenda » |
| `ouvert-texte` | `#0F2A1A` | `#F2FFF6` | Texte posé sur ce vert ; bord en pointillés d'une ouverture exceptionnelle |

## Couleurs de la nouvelle présentation (ajoutées le 04/10/2026, demandées par Raphael : « plus de couleurs »)
Le vert sauge et l'orange restent les deux couleurs de rafals ; ils sont seulement utilisés en plus grandes surfaces.
| Nom technique | Mode clair | Mode sombre | Sert à |
|---|---|---|---|
| `fonce` | `#1F4D38` | `#1C3024` | Fond du grand bandeau de l'accueil |
| `sur-fonce` / `sur-fonce-doux` | `#FFFFFF` / `#D5E6DC` | `#E7ECF2` / `#A3AEBD` | Titre / texte posés sur `fonce` |
| `fonce-vif` | `#5FD38A` | `#79C49C` | Mots mis en avant sur `fonce` (« près de chez vous. ») |
| `accent-vif` / `accent-vif-texte` | `#E8863F` / `#1D2620` | `#F0955A` / `#1D2620` | Bouton orange [Rechercher], bandeau « Vous proposez vos services ? » |
| `teinte-orange` (+ `-texte`) | `#FBE7D8` / `#7A3A0E` | `#3A2616` / `#F4B48A` | Tuiles des dossiers de métiers |
| `teinte-vert` (+ `-texte`) | `#D8ECDF` / `#1F4D38` | `#1C3024` / `#8FD5AE` | idem |
| `teinte-jaune` (+ `-texte`) | `#FBEBC6` / `#6E4300` | `#33290F` / `#EFCB73` | idem |
| `teinte-bleu` (+ `-texte`) | `#DCEAF7` / `#1D4A72` | `#17293A` / `#93C2EC` | idem |
| `teinte-rose` (+ `-texte`) | `#F8DFE4` / `#7F2238` | `#3A1B24` / `#F0A3B4` | idem |
| `teinte-violet` (+ `-texte`) | `#E8E1F6` / `#49317F` | `#271F3D` / `#C2ADF0` | idem |

Toutes les couleurs sont écrites à un seul endroit : `frontend/src/style.css`.

## Polices (gratuites, installées dans rafals)
Installées avec l'application (paquets `@fontsource-variable`), jamais chargées depuis Google : charger une police chez Google envoie l'adresse du visiteur à Google sans son accord (RGPD).
- **Logo « rafals. »** : Bricolage Grotesque (classe `font-marque`), inchangé.
- **Titres et texte** (depuis le 07/10/2026) : **Nunito**, graisse 500 pour le texte, 700 à 900 pour les titres (ex. « Bonjour Julie ! » en 900). Les deux fichiers de la police sont rangés dans `frontend/src/assets/polices/` (avec sa licence libre OFL) et déclarés en haut de `style.css` : le paquet n'a pas pu être installé par npm le 07/10/2026 (erreur de certificat dans le conteneur).
- Avant le 07/10/2026, et encore sur « Mon agenda » : titres en Bricolage Grotesque, texte en Figtree.
- Chiffres alignés (`tabular-nums`) pour les prix, les notes et les heures.

## Formes (style « chaleureux », 07/10/2026)
| Élément | Classe à écrire | Valeur | Avant (et encore sur « Mon agenda ») |
|---|---|---|---|
| Champs, petits cadres | `rounded-rafals` | 16 px | 10 px |
| Cartes, fenêtres | `carte` (coins, fond, ombre d'un coup) ou `rounded-carte` | 26 px, ombre douce, pas de bordure | 10 px, bordure grise, pas d'ombre |
| Boutons, liens du menu | `rounded-bouton` | complètement ronds | 10 px |
| Badges (étiquettes d'état) | — | bouts complètement ronds | pareil |

- **Une carte s'écrit `carte`**, jamais « `rounded-… border border-bord bg-surface` » à la main. Ex. `<article class="carte p-5">`. Les écrans pas encore repassés gardent leur bordure avec des coins de 16 px : à convertir au fur et à mesure.
- Ombre des cartes : `0 8px 28px` vert foncé à 10 % en clair, noir à 35 % en sombre (`--ombre-carte`).
- **Comment « Mon agenda » garde l'ancien style** : toutes ces valeurs sont des réglages de `style.css` (`--coin`, `--coin-carte`, `--coin-bouton`, `--ombre-carte`, `--bord-carte`, polices, fonds des boutons secondaire et danger). `App.vue` pose la classe `style-classique` sur la page tant qu'on est sur `/mon-agenda` ; elle remet les valeurs d'avant. Rien n'est écrit dans les fichiers de l'agenda.
- Pictogrammes des dossiers de métiers : `AppPicto` (tracés et teintes dans `frontend/src/outils/pictos.ts`). Dessin de la rue aux trois maisons : `frontend/src/assets/quartier.svg` (une image : ses couleurs sont dans le fichier).

## Boutons (un seul composant `AppBouton`, 5 variantes)
| Variante | Aspect | Exemple |
|---|---|---|
| Principal | Fond vert, texte blanc | « Réserver mardi 14/10 à 10 h 00 », « Rechercher » |
| Secondaire | Fond vert très clair (`primaire-doux`), texte vert, sans bordure (avant le 07/10/2026 : fond blanc, bordure verte) | « Demander un devis » |
| Danger | Fond rouge très clair (`erreur-doux`), texte rouge, sans bordure (avant : fond blanc, bordure rouge) | « Annuler », « Supprimer » |
| Verrouillé | Fond gris, texte gris, 🔒, bulle d'explication au clic | « 🔒 Payer par carte » chez Karim sans SIRET |
| Accent (04/10/2026) | Fond orange `accent-vif`, texte foncé | « Rechercher » sur le bandeau vert foncé de l'accueil |
Hauteur minimale 42 px (confortable au doigt).

## Mode sombre
rafals suit le réglage clair / sombre de l'appareil. Chaque couleur a sa valeur sombre (tableau ci-dessus).
