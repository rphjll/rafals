# Créer mon auto-entreprise — Interface

> Fichiers : `frontend/src/pages/CreerAutoEntreprisePage.vue`. Construit au lot 6.2 (03/10/2026, pendant l'absence de Raphael : maquette `maquette-lot-6.2-services.html` **à valider**). Règles : `RM-CREATION-AUTO-ENTREPRISE.md`.

## Page « Créer mon auto-entreprise » (`/creer-mon-auto-entreprise`, ouverte à tous, même sans compte)
On y arrive par : « Proposer mes services » (sous le formulaire : « Pas encore d'entreprise ? [Créer mon auto-entreprise : le guide] »), « Mon activité › Paiement par carte » sans SIRET ([Pas de SIRET ? Créer mon auto-entreprise : le guide]), et « Mes démarches » sans SIRET.
1. Titre « Créer mon auto-entreprise » ; « rafals vous guide en 5 étapes ; la déclaration se fait sur le site officiel de l'État, gratuitement. »
2. Bandeau vert dès qu'une étape est cochée : « 2 étapes sur 5 faites. » ; à 5 : « Les 5 étapes sont faites : bravo ! »
3. Une carte par étape, avec la case « C'est fait » à droite du titre :
   - « 1. Est-ce pour moi ? » — 18 ans (16-17 ans : accord des parents, sous conditions) ; métiers qui demandent un diplôme ou 3 ans d'expérience, et une assurance.
   - « 2. Je prépare mes papiers » — pièce d'identité, justificatif de domicile, diplôme ou preuve d'expérience.
   - « 3. Je déclare mon activité » — guichet unique, « micro-entrepreneur », gratuit, 30 minutes ; [Ouvrir le guichet unique] (nouvel onglet : formalites.entreprises.gouv.fr).
   - « 4. J'attends mon SIRET » — 1 à 4 semaines ; on peut déjà travailler sur rafals en espèces.
   - « 5. Je termine sur rafals » — ajouter le SIRET, créer son espace URSSAF, activer la carte ; [Proposer mes services] → `/proposer`.
4. « L'avancement est gardé sur cet appareil seulement. Besoin d'un conseil sur le statut ? Voyez la CCI ou la chambre des métiers (gratuit). Ces explications sont une aide, pas un conseil juridique. »
L'avancement est gardé dans le navigateur (rien n'est enregistré sur rafals) ; si le navigateur le refuse, le guide marche quand même.
