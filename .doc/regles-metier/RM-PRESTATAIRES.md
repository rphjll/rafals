# Règle métier — Prestataires (sujet 02)

> En cours d'écriture (phase 6 du démarrage). Chaque règle est validée par Raphael au fil des questions.

## Objectif
Ce qu'un prestataire renseigne sur rafals (métiers, zone, SIRET) et quand les clients peuvent le trouver.

## Principes
- On devient prestataire depuis son compte, par « Proposer mes services » (voir `RM-COMPTES.md`).
- Un seul agenda par prestataire, même pour une société (voir `GLOSSAIRE-METIER.md`).
- Sans SIRET : annonces payables en espèces seulement ; rafals lui conseille de se déclarer (voir `GLOSSAIRE-METIER.md`, ⚠️ à vérifier juridiquement).

## Un métier principal et des métiers secondaires (décidé le 27/09/2026)
Un prestataire choisit **un métier principal** et peut ajouter **des métiers secondaires**. Il apparaît dans les recherches de tous ses métiers, mais pour un métier secondaire, il apparaît **après** les prestataires dont c'est le métier principal. Dans chaque groupe, les mieux notés d'abord.
Réponse de Raphael, mot pour mot : « oui mais plus loin que les plombiers il doit aparaitre plus bas que les plombier et ca sera un clasement des mieux notés ».
- Exemple : Mme Dupont cherche « Électricien + Pessac ». Résultats : 1) Sophie, électricienne (métier principal), 4,8 ★ ; 2) Marc, électricien (métier principal), 4,2 ★ ; 3) Karim, plombier (électricien en métier secondaire), 4,9 ★ — Karim est 3e malgré sa meilleure note.
- Exemple : Mme Dupont cherche « Plombier + Pessac » → Karim est dans le 1er groupe, classé selon sa note parmi les plombiers.
**Pourquoi :** le client voit d'abord les spécialistes du métier qu'il cherche.
Le détail du classement (prestataires sans avis, distance…) sera traité dans le sujet 07 « Recherche ».

## Zone d'intervention : une ville et une distance (décidé le 27/09/2026)
Le prestataire indique sa ville de départ et la distance maximale, en kilomètres, jusqu'à laquelle il se déplace. Il apparaît dans les recherches des clients situés dans ce rayon.
- Exemple 1 : Karim, « Pessac, jusqu'à 15 km ». Mme Dupont à Talence (6 km) → elle le trouve.
- Exemple 2 : M. Petit à Libourne (40 km) → il ne trouve pas Karim.
**Cas limite tranché :** la distance est mesurée à vol d'oiseau, entre le centre des deux villes (plus simple et suffisant pour choisir un prestataire).

## Questions ouvertes
- Le client vient-il chez le prestataire (salon de coiffure) ou le prestataire se déplace-t-il ?
- Vérification du SIRET.
- Validation par l'administrateur avant d'être visible.

## Références
- `GLOSSAIRE-METIER.md`, `RM-COMPTES.md`
