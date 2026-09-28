# rafals — Charte visuelle

> Choisie par Raphael le 28/09/2026 en regardant la maquette cliquable `.doc/ihm/maquette-charte.html` (https://claude.ai/artifact/K2WSEd51fSMiCsQ2S3s3R7) : ambiance **B. Vert sauge**, boutons **arrondis**.
> Ces valeurs sont recopiées telles quelles dans les réglages de Tailwind au lot des écrans ; on ne tape jamais une couleur à la main dans un écran.

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

## Polices (Google Fonts, gratuites)
- **Titres** : Bricolage Grotesque, graisse 600 à 700 (ex. « Électricien à Pessac », le logo).
- **Texte** : Figtree, graisse 400 à 700 (tout le reste).
- Chiffres alignés (`tabular-nums`) pour les prix, les notes et les heures.

## Formes
- Coins arrondis : **10 px** pour les boutons, les champs, les cartes et les fenêtres.
- Badges (étiquettes d'état) : bouts complètement ronds.
- Pas d'ombre portée : les cartes sont séparées par leur bordure.

## Boutons (un seul composant `AppBouton`, 4 variantes)
| Variante | Aspect | Exemple |
|---|---|---|
| Principal | Fond vert, texte blanc | « Réserver mardi 14/10 à 10 h 00 », « Rechercher » |
| Secondaire | Fond blanc, bordure et texte verts | « Demander un devis » |
| Danger | Fond blanc, bordure et texte rouges | « Annuler », « Supprimer » |
| Verrouillé | Fond gris, texte gris, 🔒, bulle d'explication au clic | « 🔒 Payer par carte » chez Karim sans SIRET |
Hauteur minimale 42 px (confortable au doigt).

## Mode sombre
rafals suit le réglage clair / sombre de l'appareil. Chaque couleur a sa valeur sombre (tableau ci-dessus).
