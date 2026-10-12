# Alertes — Interface

> Fichier : `frontend/src/pages/AlertesPage.vue`. Construit le 12/10/2026 (lot 8.6), d'après la maquette validée `maquette-niveau-8-demandes.html` (onglet « Alertes », réécrit en questions complètes à la demande de Raphael le 04/10/2026). Règles : `RM-ALERTES.md`.

## Où
« Mon activité » → « Alertes » (`/alertes`), réservée aux prestataires (même gardien que « Mon agenda »). Contenu centré, 720 px au plus.

## Ce qu'on voit, de haut en bas
1. Titre « Alertes : être prévenu des nouvelles demandes ».
2. Cadre **« Pour quels métiers voulez-vous être prévenu ? »** : pour chaque métier exercé,
   - la phrase « Un client cherche « Plombier » près de chez vous : » ;
   - deux cases collées [Me prévenir] | [Ne pas me prévenir] (la réponse en cours est en vert) ;
   - dessous, la conséquence : « Vous êtes prévenu de chaque demande « Plombier » dans votre rayon de 15 km autour de Pessac. » ou « Vous ne recevez rien pour « Jardinier ». Les demandes restent visibles dans « Demandes près de chez moi ». »
3. Cadre **« Comment voulez-vous être prévenu ? »** : « Par mail », trois cases côte à côte : [Un mail à chaque demande] (au départ), [Un seul mail le soir à 18 h — avec toutes les demandes du jour], [Aucun mail]. Dessous, la conséquence de la réponse en cours, par exemple « Vous recevez un seul mail à 18 h, avec toutes les demandes du jour. Ex. 15 demandes dans la journée : 1 mail au lieu de 15. », puis « Les mails qui concernent vos conversations, vos propositions et vos rendez-vous ne se coupent pas. »

**Chaque clic est enregistré tout de suite** : message vert « Alertes enregistrées. » ; un refus de la règle s'affiche en message rouge et la réponse revient à l'ancienne.

## Compteur rouge
Dans « Mon activité », la tuile « Demandes près de chez moi » porte une pastille rouge avec le nombre de demandes arrivées depuis la dernière visite de cette page ; l'ouvrir la remet à zéro. (Pas de pastille dans le sous-menu.)

## Pas encore fait
- « Sur ce téléphone (une notification, même quand rafals est fermé) » [Oui] / [Non] : lot 8.7.
