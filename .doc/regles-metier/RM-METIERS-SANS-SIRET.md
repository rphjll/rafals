# Règle métier — Métiers autorisés ou non sans SIRET

> Écrit par Claude le 09/10/2026, à la demande de Raphael (« non je ne veux pas m'ochuper de ca dans l'amin commande faut que ca soit automatique »). Complète `RM-PRESTATAIRES.md` § « Limites d'un prestataire sans SIRET », règle 1.
> **Construit le 12/10/2026** : rubrique `metier.siret_obligatoire` (`schema_v26.sql`), remplie d'après la liste `sans_siret` de `backend/app/donnees/metiers.json` (les 50 métiers autorisés, par leur code). ⚠️ **À montrer à un avocat avant la mise en ligne** : ce classement est fait par prudence, il ne vaut pas un avis juridique.

## Objectif
Dire, pour chacun des 129 métiers de rafals, si un prestataire **sans SIRET vérifié** peut répondre aux demandes de ce métier. Le site l'applique tout seul : aucun écran d'administration.
- Exemple 1 : Emma, sans SIRET, voit [Répondre] sur « Promener mon chien le midi » (Promeneur de chiens : autorisé).
- Exemple 2 : Karim, sans SIRET, ne voit pas [Répondre] sur « Fuite sous l'évier » (Plombier : SIRET obligatoire). Avec un SIRET vérifié, il répond à tout.

## Les trois groupes
| Groupe | Nombre | Ce que ça veut dire |
|---|---|---|
| **SIRET obligatoire, par la règle** | 56 | Le métier relève d'un des 11 mots validés par Raphael le 09/10/2026 (plomberie, électricité, gaz, bâtiment, coiffure, esthétique, réparation auto, santé, garde d'enfants de moins de 3 ans, transport de personnes, alimentation). |
| **SIRET obligatoire, ajouté par prudence** | 23 | Le métier n'est dans aucun des 11 mots, mais la loi y exige un diplôme, un certificat ou une inscription. Proposé par Claude, **gardé par Raphael le 09/10/2026 (« A »)**. |
| **Autorisé sans SIRET** | 50 | Petits services : dans les limites de prix, de nombre et de total par an. |

Un métier ajouté plus tard à la liste est « SIRET obligatoire » d'office, tant que ce fichier ne dit pas le contraire.

## Le classement, dossier par dossier

### Maison & travaux
- **SIRET obligatoire, par la règle** : Antenniste / Parabole (bâtiment) ; Carreleur (bâtiment) ; Chauffagiste (gaz) ; Climatisation / Pompe à chaleur (bâtiment) ; cordiste (bâtiment) ; Couvreur / Zingueur (bâtiment) ; Cuisiniste / Salles de bain (bâtiment) ; Domotique / Alarmes (électricité) ; Électricien (électricité) ; Façadier / Ravalement (bâtiment) ; Maçon (bâtiment) ; Menuisier / Ébéniste (bâtiment) ; Peintre en bâtiment (bâtiment) ; Pisciniste / Entretien piscine (bâtiment) ; Plaquiste (bâtiment) ; Plombier (plomberie) ; Poseur de sols / Parquet (bâtiment) ; Ramoneur (bâtiment) ; Serrurier (bâtiment) ; Stores / Volets (bâtiment) ; Vitrier (bâtiment).
- **SIRET obligatoire, par prudence** : Architecte d'intérieur / Décorateur (travaux dans un logement, assurance exigée dès qu'il dirige un chantier) ; Diagnostiqueur immobilier (certification obligatoire).
- **Autorisé sans SIRET** : Homme toutes mains / Multiservices, Montage de meubles.

### Ménage & entretien
- **SIRET obligatoire, par prudence** : Désinsectisation / Dératisation (produits dangereux, certificat obligatoire).
- **Autorisé sans SIRET** : Débarras / Vide-maison, Femme / Homme de ménage, Grand nettoyage / Fin de chantier, Nettoyage de canapés et tapis, Nettoyage de vitres, Repassage.

### Jardin & extérieur
- **SIRET obligatoire, par la règle** : Clôtures / Portails (bâtiment) ; Paysagiste (bâtiment) ; Terrassier (bâtiment).
- **SIRET obligatoire, par prudence** : Élagueur / Abattage (travail en hauteur, dangereux).
- **Autorisé sans SIRET** : Jardinier, Taille de haies.

### Beauté & bien-être
- **SIRET obligatoire, par la règle** : Barbier (coiffure) ; Coiffeur / Coiffeuse (coiffure ; « à domicile » fusionné dedans le 15/11/2026) ; Esthéticienne (esthétique) ; Extensions de cils / Regard (esthétique) ; Maquilleur / Maquilleuse (esthétique) ; Masseur / Masseuse bien-être (esthétique) ; Onglerie / Prothésiste ongulaire (esthétique) ; Sophrologue (santé).
- **SIRET obligatoire, par prudence** : Tatoueur / Pierceur (déclaration et formation à l'hygiène obligatoires).
- **Autorisé sans SIRET** : Conseil en image / Relooking.

### Santé
- **SIRET obligatoire, par la règle** : Diététicien / Nutritionniste (santé) ; Ergothérapeute (santé) ; Infirmier / Infirmière (santé) ; Kinésithérapeute (santé) ; Naturopathe / Médecines douces (santé) ; Orthophoniste (santé) ; Ostéopathe (santé) ; Pédicure-podologue (santé) ; Psychologue / Thérapeute (santé) ; Psychomotricien (santé) ; Sage-femme (santé).

### Enfants & famille
- **SIRET obligatoire, par la règle** : Assistante maternelle (garde d'enfants de moins de 3 ans).
- **Autorisé sans SIRET** : Aide aux devoirs, Animateur / Anniversaires enfants, Garde d'enfants / Baby-sitting.

### Cours & formation
- **SIRET obligatoire, par prudence** : Moniteur de conduite (autorisation d'enseigner obligatoire).
- **Autorisé sans SIRET** : Cours de couture, Cours de cuisine / Pâtisserie, Cours de dessin / Peinture, Cours de langues, Cours de musique, Cours d'informatique, Formateur / Consultant, Soutien scolaire.

### Sport & loisirs
- **SIRET obligatoire, par prudence** : Arts martiaux / Boxe (enseigner un sport contre de l'argent demande un diplôme) ; Coach sportif (enseigner un sport contre de l'argent demande un diplôme) ; Guide / Accompagnateur randonnée (enseigner un sport contre de l'argent demande un diplôme) ; Maître-nageur / Cours de natation (enseigner un sport contre de l'argent demande un diplôme) ; Moniteur d'équitation (enseigner un sport contre de l'argent demande un diplôme) ; Moniteur de surf / Sports nautiques (enseigner un sport contre de l'argent demande un diplôme) ; Professeur de danse (enseigner un sport contre de l'argent demande un diplôme) ; Professeur de tennis / Padel (enseigner un sport contre de l'argent demande un diplôme) ; Professeur de yoga / Pilates (le Pilates est un sport encadré ; le yoga seul ne l'est pas, rangé ici par prudence).

### Événements
- **SIRET obligatoire, par la règle** : Chef à domicile (alimentation) ; Pâtissier pour événements (alimentation) ; Traiteur (alimentation).
- **Autorisé sans SIRET** : Décorateur d'événements, DJ / Animation musicale, Fleuriste pour événements, Location matériel de fête / Photobooth, Magicien, Musicien / Chanteur, Organisateur de mariage / d'événements, Photographe, Vidéaste.

### Animaux
- **SIRET obligatoire, par la règle** : Vétérinaire (santé).
- **SIRET obligatoire, par prudence** : Éducateur canin (certificat obligatoire pour travailler avec des animaux) ; Maréchal-ferrant (métier d'artisan réglementé).
- **Autorisé sans SIRET** : Pet-sitter / Garde d'animaux, Promeneur de chiens, Toiletteur.

### Auto & transport
- **SIRET obligatoire, par la règle** : Carrossier (réparation auto) ; Chauffeur privé / VTC (transport de personnes) ; Contrôle technique (réparation auto) ; Dépannage / Remorquage (réparation auto) ; Mécanicien (réparation auto) ; Mécanicien à domicile (réparation auto) ; Mécanicien moto / Scooter (réparation auto).
- **SIRET obligatoire, par prudence** : Coursier / Livraison (transport de marchandises, inscription obligatoire avec un véhicule à moteur) ; Déménageur (transport de marchandises, inscription obligatoire) ; Réparation de vélos (réparation de véhicules, métier d'artisan).
- **Autorisé sans SIRET** : Lavage / Nettoyage auto.

### Numérique & bureau
- **SIRET obligatoire, par prudence** : Comptable / Aide à la gestion (tenir une comptabilité est réservé aux experts-comptables).
- **Autorisé sans SIRET** : Community manager, Création de sites web, Dépannage informatique, Graphiste, Rédacteur / Correcteur, Réparation de téléphones, Secrétariat / Assistance administrative, Traducteur.

### Services à la personne
- **SIRET obligatoire, par prudence** : Aide à domicile / Seniors (personnes fragiles, autorisation obligatoire).
- **Autorisé sans SIRET** : Conciergerie / Location saisonnière, Cordonnier / Clés, Courses et accompagnement, Couturière / Retouches, Écrivain public, Horloger, Réparation d'électroménager.

### Autre
- **SIRET obligatoire, par prudence** : Autre (métier inconnu : SIRET obligatoire d'office).

## Cas tranchés par Claude (à relire)
- **Garde d'enfants / Baby-sitting : autorisé.** La règle interdit la garde des moins de 3 ans, mais le métier ne dit pas l'âge de l'enfant ; c'est le petit service le plus courant. La carte de la demande et l'avertissement au client diront « enfants de 3 ans et plus seulement, sans SIRET ». L'âge n'est pas contrôlé par le site.
- **Homme toutes mains / Multiservices et Montage de meubles : autorisés**, bien qu'ils soient dans le dossier « Maison & travaux » : petits bricolages sans gros œuvre. Ex. poser une tringle, monter une armoire.
- **Jardinier et Taille de haies : autorisés** ; **Paysagiste, Terrassier, Clôtures / Portails : SIRET obligatoire** (ce sont des travaux).
- **Courses et accompagnement : autorisé** ; conduire une personne contre de l'argent reste interdit sans SIRET (transport de personnes).
- **Photographe, DJ, Musicien, Magicien, cours particuliers, dépannage informatique : autorisés.**

## Qui peut faire quoi
| Action | Qui | Condition |
|---|---|---|
| Répondre à une demande d'un métier « SIRET obligatoire » | Prestataire | SIRET vérifié |
| Répondre à une demande d'un métier « autorisé sans SIRET » | Prestataire | Les limites de `RM-PRESTATAIRES.md` s'il n'a pas de SIRET vérifié |
| Changer le groupe d'un métier | Claude, dans ce fichier et dans la liste des métiers, sur décision de Raphael | Pas d'écran d'administration |

## Le métier à prendre à la place, sans SIRET (demande de Raphael du 25/11/2026)
Demande mot pour mot : « pour les métiers interdit je veux un équivalent faisable pour les presataires genre pour plombier ca serai bricoleur ». Choix de Raphael (« A ») : l'équivalent est **proposé à la place**. Le prestataire sans SIRET **ne voit jamais** les demandes du métier interdit.
- Exemple 1 : Karim, sans SIRET, choisit « Plombier » dans « Ajouter un métier ». Bandeau orange : « « Plombier » demande un SIRET : sans SIRET, vous ne pourrez pas répondre à ses demandes. Choisissez plutôt « Homme toutes mains / Multiservices » (petits services, sans SIRET). » avec [Prendre « Homme toutes mains / Multiservices »] et [Créer mon auto-entreprise]. Un clic sur le premier bouton remplace le choix.
- Exemple 2 : Karim garde « Plombier » quand même. Sur « Fuite sous l'évier », [Répondre] reste verrouillé : « « Plombier » demande un SIRET. Sans SIRET, choisissez plutôt « Homme toutes mains / Multiservices » dans « Mon profil », ou créez votre auto-entreprise… ».
- Un métier sans équivalent (santé, conduite, coiffure…) : « Ce métier n'a pas d'équivalent sans SIRET : créez votre auto-entreprise pour l'exercer. »
- Le bandeau apparaît dans « Ajouter un métier » et dans le formulaire du profil (métier principal et chaque métier secondaire). Avec un SIRET vérifié, il n'apparaît jamais.

**La liste (choisie par Claude, à relire par Raphael et par l'avocat)**. Elle est rangée dans le code (`EQUIVALENTS_SANS_SIRET`, `services/particuliers.py`), pas dans la base.

| Métier interdit sans SIRET | À prendre à la place |
|---|---|
| Plombier, Électricien, Peintre en bâtiment, Plaquiste, Carreleur, Poseur de sols / Parquet, Stores / Volets, Clôtures / Portails | Homme toutes mains / Multiservices |
| Menuisier / Ébéniste, Cuisiniste / Salles de bain | Montage de meubles |
| Paysagiste | Jardinier |
| Élagueur / Abattage | Taille de haies |
| Déménageur | Débarras / Vide-maison |
| Coursier / Livraison, Aide à domicile / Seniors | Courses et accompagnement |
| Assistante maternelle | Garde d'enfants / Baby-sitting |
| Éducateur canin | Promeneur de chiens |
| Chef à domicile, Traiteur, Pâtissier pour événements | Cours de cuisine / Pâtisserie |
| Maquilleur / Maquilleuse | Conseil en image / Relooking |
| Comptable / Aide à la gestion | Secrétariat / Assistance administrative |

Les autres métiers interdits n'ont pas d'équivalent : il faudrait un diplôme, une assurance obligatoire ou une carte pro (santé, gaz et chauffage, toiture, VTC, mécanique, coiffure, esthétique, sport…).

Un test vérifie que chaque métier de cette liste existe, que celui de gauche demande un SIRET et que celui de droite est actif et autorisé sans SIRET (`tests/test_particuliers.py`).

## Questions ouvertes
- Liste des équivalents du 25/11/2026 : à relire par Raphael, puis par l'avocat (un « Homme toutes mains » ne doit faire que de petits travaux, pas de plomberie ni d'électricité).

## Références
- `RM-PRESTATAIRES.md` (§ « Limites d'un prestataire sans SIRET »), `RM-DEMANDES.md`, `RM-METIERS.md`
