# Règle métier — Métiers et catégories (sujet 04)

> En cours d'écriture (phase 6 du démarrage). Chaque règle est validée par Raphael au fil des questions.

## Objectif
La grande liste des métiers de rafals, rangée dans des catégories (« dossiers »), et la façon dont clients et prestataires y trouvent un métier.

## Principes
- Chaque Annonce est rangée sous un Métier ; chaque prestataire a un métier principal et peut avoir des métiers secondaires (voir `RM-PRESTATAIRES.md`).
- Recherche d'un métier : en ouvrant une catégorie, ou en tapant les premières lettres (voir `GLOSSAIRE-METIER.md`).

## Source de la liste : triée (décidé le 28/09/2026)
Claude construit la liste à partir des 110 métiers et 10 catégories de vitrine-express (`vitrine-express/vitrine-express/js/metiers.js`), et la complète avec le répertoire officiel des métiers de France Travail, en ne gardant que les métiers qu'un **particulier** peut réserver. Raphael relit la liste avant qu'elle entre dans rafals.
- Exemple 1 : « Professeur de guitare » (absent de vitrine-express, présent dans la liste officielle, sert des particuliers) → ajouté, catégorie « Sport & loisirs ».
- Exemple 2 : « Contrôleur aérien » → écarté (ne sert pas des particuliers).
**Pourquoi :** Mme Dupont ne doit pas se perdre dans des milliers de métiers qui ne la concernent pas.

## Questions ouvertes
- Que se passe-t-il si un prestataire ne trouve pas son métier dans la liste ?

## Références
- `GLOSSAIRE-METIER.md`, `RM-PRESTATAIRES.md`, `PRESENTATION.md` (vitrine-express)
