// ============================================================
//  LES MÉTIERS = des textes d'exemple pour pré-remplir le site
//
//  Ils ne changent PAS le style du site (c'est le rôle des modèles,
//  dans modeles.js). Ils servent à remplir d'un coup le nom, l'accroche,
//  les tarifs, les horaires… avec un exemple adapté au métier.
//
//  Pour AJOUTER un métier : copie un bloc (ex. "fleuriste: { ... },"),
//  change son identifiant, sa catégorie et ses textes.
//  - libelles : (facultatif) pour dire "Carte" au lieu de "Tarifs", etc.
//  - defauts.services : une ligne par prestation -> "Nom | Prix"
//  - defauts.horaires : une ligne par jour      -> "Jour : heures"
// ============================================================

// ---------- Les catégories (ordre d'affichage) ----------
const CATEGORIES = [
  "Beauté & bien-être",
  "Restauration",
  "Commerces",
  "Maison & travaux",
  "Auto & transport",
  "Santé",
  "Sport & loisirs",
  "Événements",
  "Animaux",
  "Services"
];

// ---------- Les métiers ----------
const METIERS = {

  // ===================== BEAUTÉ & BIEN-ÊTRE =====================

  barbier: {
    nom: "Barbier / Coiffeur", icone: "✂️", categorie: "Beauté & bien-être",
    resume: "Sombre et élégant, idéal pour un barbershop ou un salon de coiffure.",
    defauts: {
      nom: "Le Barbier du Coin",
      slogan: "Coupes, dégradés et taille de barbe, sans rendez-vous.",
      description: "Installé au cœur du quartier, notre salon vous accueille dans une ambiance détendue. Dégradés, coupes classiques ou modernes, taille de barbe à l'ancienne : on prend le temps de faire les choses bien.",
      telephone: "05 00 00 00 00", email: "", adresse: "1 avenue Pasteur, 33600 Pessac",
      horaires: "Lundi : fermé\nMardi - Vendredi : 9h30 - 19h30\nSamedi : 9h - 18h\nDimanche : 10h - 13h",
      services: "Coupe homme | 20 €\nDégradé | 22 €\nTaille de barbe | 12 €\nCoupe + barbe | 30 €\nCoupe enfant (- 12 ans) | 15 €",
      couleur: "#c9a227"
    }
  },

  beaute: {
    nom: "Esthéticienne / Institut", icone: "💅", categorie: "Beauté & bien-être",
    resume: "Doux et lumineux, pour un institut de beauté ou une onglerie.",
    defauts: {
      nom: "Institut Belle Peau",
      slogan: "Soins du visage, épilations et beauté des mains.",
      description: "Un cocon de douceur où prendre soin de vous. Soins du visage, épilations, pose d'ongles et massages, réalisés avec des produits de qualité et beaucoup d'attention.",
      telephone: "06 00 00 00 00", email: "", adresse: "5 avenue de Magonty, 33600 Pessac",
      horaires: "Lundi - Vendredi : 9h - 19h\nSamedi : 9h - 14h\nDimanche : fermé",
      services: "Soin visage éclat | 45 €\nÉpilation sourcils | 10 €\nManucure + vernis | 25 €\nPose gel complète | 45 €\nMassage relaxant 45 min | 55 €",
      couleur: "#c07a8a"
    }
  },

  coiffure: {
    nom: "Salon de coiffure mixte", icone: "💇", categorie: "Beauté & bien-être",
    resume: "Chic et lumineux, pour un salon de coiffure femmes, hommes et enfants.",
    defauts: {
      nom: "L'Atelier Coiffure",
      slogan: "Coupe, couleur et coiffage pour toute la famille.",
      description: "Notre équipe vous accueille avec ou sans rendez-vous pour une coupe, une couleur ou un coiffage de fête. Conseils personnalisés et produits professionnels.",
      telephone: "05 00 00 00 00", email: "", adresse: "12 place de la Ve République, 33600 Pessac",
      horaires: "Lundi : fermé\nMardi - Vendredi : 9h - 19h\nSamedi : 8h30 - 17h\nDimanche : fermé",
      services: "Coupe femme + brushing | 42 €\nCoupe homme | 22 €\nCoupe enfant | 15 €\nCouleur | à partir de 45 €\nBalayage | à partir de 70 €\nChignon | 40 €",
      couleur: "#9a6b4f"
    }
  },

  tatouage: {
    nom: "Tatoueur / Piercing", icone: "🖋️", categorie: "Beauté & bien-être",
    resume: "Sombre et artistique, pour un salon de tatouage ou de piercing.",
    libelles: { menuServices: "Tarifs", titreServices: "Tarifs indicatifs" },
    defauts: {
      nom: "Encre Noire Tattoo",
      slogan: "Tatouages sur mesure et piercings, dans un studio propre et chaleureux.",
      description: "Chaque projet est dessiné sur mesure avec vous. Fine line, réalisme, old school ou lettering : venez en discuter autour d'un café. Matériel stérile et à usage unique.",
      telephone: "06 00 00 00 00", email: "", adresse: "30 avenue Jean Jaurès, 33600 Pessac",
      horaires: "Lundi : fermé\nMardi - Samedi : 11h - 19h (sur rendez-vous)\nDimanche : fermé",
      services: "Petit tatouage (flash) | à partir de 80 €\nTatouage sur mesure | sur devis\nSéance à la journée | 450 €\nPiercing oreille | 30 €\nPiercing nez / nombril | 40 €",
      couleur: "#e11d48"
    }
  },

  massage: {
    nom: "Massage / Spa / Sophrologie", icone: "🧘", categorie: "Beauté & bien-être",
    resume: "Apaisant et naturel, pour un praticien bien-être ou un spa.",
    libelles: { boutonAppel: "Réserver" },
    defauts: {
      nom: "Instant Zen",
      slogan: "Massages bien-être et relaxation, pour souffler vraiment.",
      description: "Dans un espace calme et chaleureux, offrez-vous une vraie pause. Massages aux huiles, pierres chaudes, réflexologie plantaire et séances de relaxation. Cartes cadeaux disponibles.",
      telephone: "06 00 00 00 00", email: "", adresse: "8 rue Pierre Cérésole, 33600 Pessac",
      horaires: "Lundi - Vendredi : 10h - 20h\nSamedi : 10h - 17h\nDimanche : fermé",
      services: "Massage relaxant 1h | 60 €\nMassage pierres chaudes 1h15 | 75 €\nRéflexologie plantaire 45 min | 50 €\nSéance de sophrologie | 50 €\nCarte cadeau | au choix",
      couleur: "#5f8d6e"
    }
  },

  // ===================== RESTAURATION =====================

  restaurant: {
    nom: "Restaurant", icone: "🍽️", categorie: "Restauration",
    resume: "Chaleureux et gourmand, pour un restaurant ou une brasserie.",
    libelles: { menuServices: "Carte", titreServices: "La carte", voirServices: "Voir la carte", boutonAppel: "Réserver" },
    defauts: {
      nom: "Le Petit Bistrot",
      slogan: "Cuisine maison, produits frais et de saison.",
      description: "Une cuisine de bistrot généreuse, préparée chaque jour avec des produits frais du marché. Terrasse ensoleillée, menu du midi et soirées en famille ou entre amis.",
      telephone: "05 00 00 00 00", email: "", adresse: "20 avenue Pasteur, 33600 Pessac",
      horaires: "Lundi : fermé\nMardi - Vendredi : 12h - 14h / 19h - 22h\nSamedi : 19h - 22h30\nDimanche : 12h - 14h30",
      services: "Menu du midi (entrée + plat + dessert) | 18 €\nEntrecôte frites maison | 22 €\nPoisson du jour | 19 €\nSalade de chèvre chaud | 14 €\nDessert du jour | 7 €\nMenu enfant | 10 €",
      couleur: "#b5452f"
    }
  },

  pizzeria: {
    nom: "Pizzeria", icone: "🍕", categorie: "Restauration",
    resume: "Gourmand et coloré, pour une pizzeria sur place ou à emporter.",
    libelles: { menuServices: "Carte", titreServices: "Nos pizzas", voirServices: "Voir les pizzas", boutonAppel: "Commander" },
    defauts: {
      nom: "Pizza Napoli",
      slogan: "Pizzas au feu de bois, sur place ou à emporter.",
      description: "Pâte maison reposée 48 h, tomates italiennes et mozzarella fraîche : nos pizzas sont cuites au feu de bois devant vous. Commandez par téléphone et passez la récupérer !",
      telephone: "05 00 00 00 00", email: "", adresse: "45 avenue Jean Jaurès, 33600 Pessac",
      horaires: "Lundi : fermé\nMardi - Dimanche : 11h30 - 14h / 18h - 22h30",
      services: "Margherita | 10 €\nReine | 12 €\n4 fromages | 13 €\nCalzone | 13 €\nVégétarienne | 12 €\nTiramisu maison | 5 €",
      couleur: "#c8102e"
    }
  },

  boulangerie: {
    nom: "Boulangerie / Pâtisserie", icone: "🥐", categorie: "Restauration",
    resume: "Doré et appétissant, pour une boulangerie ou une pâtisserie.",
    libelles: { menuServices: "Produits", titreServices: "Nos produits", voirServices: "Voir nos produits" },
    defauts: {
      nom: "Aux Délices du Fournil",
      slogan: "Pain au levain, viennoiseries et pâtisseries faites maison.",
      description: "Chaque matin, nos boulangers pétrissent et façonnent le pain sur place. Viennoiseries pur beurre, gâteaux de fête sur commande et sandwichs frais le midi.",
      telephone: "05 00 00 00 00", email: "", adresse: "3 place de la Ve République, 33600 Pessac",
      horaires: "Lundi : fermé\nMardi - Samedi : 6h30 - 19h30\nDimanche : 7h - 13h",
      services: "Baguette tradition | 1,30 €\nPain au levain (500 g) | 3,80 €\nCroissant pur beurre | 1,20 €\nFormule sandwich + boisson + dessert | 8,50 €\nGâteau de fête (6 parts) | à partir de 24 €",
      couleur: "#c68a3a"
    }
  },

  cafe: {
    nom: "Café / Bar / Salon de thé", icone: "☕", categorie: "Restauration",
    resume: "Cosy et convivial, pour un café, un bar ou un salon de thé.",
    libelles: { menuServices: "Carte", titreServices: "La carte", voirServices: "Voir la carte" },
    defauts: {
      nom: "Le Comptoir",
      slogan: "Cafés de spécialité, brunchs et bonne humeur.",
      description: "Un lieu chaleureux pour travailler, bruncher ou refaire le monde. Café torréfié artisanalement, pâtisseries maison et brunch le week-end.",
      telephone: "05 00 00 00 00", email: "", adresse: "7 avenue Pasteur, 33600 Pessac",
      horaires: "Lundi - Vendredi : 8h - 19h\nSamedi - Dimanche : 9h - 18h",
      services: "Expresso | 2 €\nCappuccino | 3,80 €\nThé maison | 3,50 €\nPart de gâteau | 4,50 €\nBrunch complet (week-end) | 22 €",
      couleur: "#7b5a3c"
    }
  },

  traiteur: {
    nom: "Traiteur / Chef à domicile", icone: "🥘", categorie: "Restauration",
    resume: "Raffiné, pour un traiteur, un chef à domicile ou des plats cuisinés.",
    libelles: { menuServices: "Formules", titreServices: "Nos formules", voirServices: "Voir les formules" },
    defauts: {
      nom: "Saveurs & Réceptions",
      slogan: "Buffets, cocktails et repas de fête, livrés chez vous.",
      description: "Mariages, anniversaires, repas d'entreprise : nous préparons des menus sur mesure à partir de produits frais et locaux. Livraison et service possibles.",
      telephone: "06 00 00 00 00", email: "", adresse: "Pessac et toute la Gironde",
      horaires: "Lundi - Samedi : 9h - 18h (sur rendez-vous)",
      services: "Plateau repas entreprise | 16 € / pers.\nBuffet froid | à partir de 22 € / pers.\nCocktail dînatoire | à partir de 25 € / pers.\nChef à domicile | sur devis",
      couleur: "#8a6d3b"
    }
  },

  foodtruck: {
    nom: "Food truck", icone: "🚚", categorie: "Restauration",
    resume: "Fun et percutant, pour un food truck ou de la street food.",
    libelles: { menuServices: "Menu", titreServices: "Le menu", voirServices: "Voir le menu", boutonAppel: "Commander" },
    defauts: {
      nom: "Burger Truck 33",
      slogan: "Burgers maison et frites fraîches, près de chez vous.",
      description: "Pain brioché, steak haché frais et sauces maison : on cuisine tout minute. Retrouvez le camion chaque semaine sur nos emplacements, et pour vos événements privés.",
      telephone: "06 00 00 00 00", email: "", adresse: "Pessac, Mérignac, Talence",
      horaires: "Mardi : marché de Pessac, 11h30 - 14h\nJeudi : parc d'activités, 11h30 - 14h\nVendredi : 18h30 - 22h",
      services: "Burger classique | 9 €\nBurger chèvre-miel | 10 €\nFrites maison | 3 €\nMenu burger + frites + boisson | 13 €\nPrivatisation pour événement | sur devis",
      couleur: "#f59e0b"
    }
  },

  // ===================== COMMERCES =====================

  fleuriste: {
    nom: "Fleuriste", icone: "💐", categorie: "Commerces",
    resume: "Frais et poétique, pour un fleuriste ou un atelier floral.",
    libelles: { menuServices: "Créations", titreServices: "Nos créations" },
    defauts: {
      nom: "Pétales & Cie",
      slogan: "Bouquets de saison, compositions et fleurs pour vos événements.",
      description: "Des fleurs fraîches, locales quand c'est possible, et des bouquets composés avec amour. Mariages, deuils, anniversaires : on vous conseille pour chaque occasion.",
      telephone: "05 00 00 00 00", email: "", adresse: "15 avenue Pasteur, 33600 Pessac",
      horaires: "Lundi : fermé\nMardi - Samedi : 9h - 19h\nDimanche : 9h - 13h",
      services: "Bouquet de saison | à partir de 25 €\nComposition en pot | à partir de 35 €\nPlante verte | à partir de 15 €\nFleurs de mariage | sur devis\nLivraison à Pessac | 8 €",
      couleur: "#d9678a"
    }
  },

  epicerie: {
    nom: "Épicerie fine / Vrac", icone: "🧺", categorie: "Commerces",
    resume: "Naturel et authentique, pour une épicerie, du vrac ou des produits locaux.",
    libelles: { menuServices: "Produits", titreServices: "Nos produits" },
    defauts: {
      nom: "Le Panier Local",
      slogan: "Produits locaux, bio et en vrac, à deux pas de chez vous.",
      description: "Fruits et légumes de producteurs girondins, épicerie en vrac, fromages et produits d'hygiène zéro déchet. Venez avec vos contenants !",
      telephone: "05 00 00 00 00", email: "", adresse: "9 avenue de Magonty, 33600 Pessac",
      horaires: "Lundi : 14h - 19h\nMardi - Samedi : 9h - 19h30\nDimanche : fermé",
      services: "Paniers de légumes de saison | 15 € / 25 €\nÉpicerie en vrac | au poids\nFromages et crèmerie | au poids\nProduits d'hygiène zéro déchet | à partir de 4 €",
      couleur: "#6b8e23"
    }
  },

  boucherie: {
    nom: "Boucherie / Charcuterie", icone: "🥩", categorie: "Commerces",
    resume: "Franc et traditionnel, pour une boucherie ou une charcuterie artisanale.",
    libelles: { menuServices: "Produits", titreServices: "Nos spécialités" },
    defauts: {
      nom: "Boucherie du Marché",
      slogan: "Viandes de qualité, origine France, et charcuterie maison.",
      description: "Viandes sélectionnées chez des éleveurs de la région, maturées et découpées devant vous. Charcuterie et plats cuisinés maison, commandes pour vos barbecues et fêtes.",
      telephone: "05 00 00 00 00", email: "", adresse: "22 place de la Ve République, 33600 Pessac",
      horaires: "Lundi : fermé\nMardi - Samedi : 8h - 13h / 15h30 - 19h30\nDimanche : 8h - 13h",
      services: "Entrecôte maturée | 34 € / kg\nSaucisses maison | 14 € / kg\nPoulet fermier | 11 € / kg\nPlat cuisiné du jour | 9 € / part\nColis barbecue | sur commande",
      couleur: "#9b1c1c"
    }
  },

  caviste: {
    nom: "Caviste / Cave à vin", icone: "🍷", categorie: "Commerces",
    resume: "Élégant, pour un caviste, une cave à bières ou un bar à vin.",
    libelles: { menuServices: "Sélection", titreServices: "Notre sélection" },
    defauts: {
      nom: "La Cave de Pessac",
      slogan: "Vins de Bordeaux et d'ailleurs, conseils et dégustations.",
      description: "Plus de 400 références sélectionnées chez des vignerons passionnés. Pessac-Léognan, vins naturels, bières artisanales et spiritueux. Dégustations chaque vendredi soir.",
      telephone: "05 00 00 00 00", email: "", adresse: "18 avenue Jean Jaurès, 33600 Pessac",
      horaires: "Lundi : fermé\nMardi - Samedi : 10h - 13h / 15h - 20h\nDimanche : 10h - 13h",
      services: "Vins du moment | à partir de 8 €\nPessac-Léognan | à partir de 18 €\nBières artisanales | à partir de 3,50 €\nCoffret cadeau | à partir de 30 €\nSoirée dégustation | 15 € / pers.",
      couleur: "#7b1e3a"
    }
  },

  // ===================== MAISON & TRAVAUX =====================

  artisan: {
    nom: "Plombier / Chauffagiste", icone: "🔧", categorie: "Maison & travaux",
    resume: "Clair et efficace, pour un plombier ou un chauffagiste.",
    defauts: {
      nom: "Dupont Plomberie",
      slogan: "Dépannage rapide, installation et rénovation.",
      description: "Artisan plombier à votre service pour tous vos travaux : fuites, débouchage, chauffe-eau, rénovation de salle de bain. Intervention rapide, travail soigné et devis gratuit.",
      telephone: "06 00 00 00 00", email: "", adresse: "Pessac et alentours (33)",
      horaires: "Lundi - Samedi : 8h - 19h\nUrgences : 7j/7",
      services: "Déplacement + diagnostic | 50 €\nRecherche de fuite | à partir de 90 €\nDébouchage | à partir de 80 €\nRemplacement chauffe-eau | sur devis\nRénovation salle de bain | sur devis",
      couleur: "#2563eb"
    }
  },

  electricien: {
    nom: "Électricien", icone: "⚡", categorie: "Maison & travaux",
    resume: "Net et rassurant, pour un électricien ou un domoticien.",
    defauts: {
      nom: "Martin Électricité",
      slogan: "Dépannage, mise aux normes et installation électrique.",
      description: "Électricien qualifié pour particuliers et professionnels : pannes, tableaux électriques, mise aux normes, éclairage, bornes de recharge. Devis gratuit, travail garanti.",
      telephone: "06 00 00 00 00", email: "", adresse: "Pessac et Bordeaux Métropole",
      horaires: "Lundi - Vendredi : 8h - 18h\nSamedi : sur rendez-vous",
      services: "Dépannage (déplacement inclus) | à partir de 70 €\nRemplacement tableau électrique | sur devis\nMise aux normes | sur devis\nInstallation borne de recharge | sur devis\nPose luminaire | à partir de 45 €",
      couleur: "#eab308"
    }
  },

  peintre: {
    nom: "Peintre en bâtiment / Rénovation", icone: "🎨", categorie: "Maison & travaux",
    resume: "Propre et lumineux, pour un peintre, un plaquiste ou une entreprise de rénovation.",
    defauts: {
      nom: "Couleurs & Finitions",
      slogan: "Peinture intérieure et extérieure, finitions soignées.",
      description: "Nous redonnons vie à vos murs, plafonds, boiseries et façades. Préparation soignée, protection de vos meubles et chantier laissé propre. Devis gratuit sous 48 h.",
      telephone: "06 00 00 00 00", email: "", adresse: "Pessac et alentours",
      horaires: "Lundi - Vendredi : 8h - 18h",
      services: "Peinture d'une pièce (12 m²) | à partir de 450 €\nPlafond | à partir de 18 € / m²\nRavalement de façade | sur devis\nPose de papier peint | à partir de 20 € / m²\nPetits travaux de plâtrerie | sur devis",
      couleur: "#0d9488"
    }
  },

  paysagiste: {
    nom: "Paysagiste / Jardinier", icone: "🌿", categorie: "Maison & travaux",
    resume: "Vert et naturel, pour un paysagiste ou l'entretien de jardins.",
    defauts: {
      nom: "Jardins de Gironde",
      slogan: "Création et entretien de jardins, toute l'année.",
      description: "Tonte, taille de haies, élagage, création de massifs et de terrasses : nous prenons soin de votre extérieur. Contrats d'entretien à l'année. 50 % déductibles des impôts pour les particuliers.",
      telephone: "06 00 00 00 00", email: "", adresse: "Pessac, Mérignac, Gradignan, Talence",
      horaires: "Lundi - Vendredi : 8h - 18h\nSamedi : 8h - 12h",
      services: "Tonte de pelouse | à partir de 35 €\nTaille de haies | à partir de 40 € / h\nÉlagage | sur devis\nCréation de massif | sur devis\nContrat d'entretien annuel | sur devis",
      couleur: "#3f7d3a"
    }
  },

  menage: {
    nom: "Ménage / Nettoyage", icone: "🧽", categorie: "Maison & travaux",
    resume: "Frais et rassurant, pour une entreprise de ménage ou de nettoyage.",
    defauts: {
      nom: "Net & Brillant",
      slogan: "Ménage à domicile et nettoyage de bureaux.",
      description: "Une équipe de confiance pour l'entretien de votre maison ou de vos locaux. Ménage régulier, grand nettoyage, vitres, fin de chantier. 50 % de crédit d'impôt pour les particuliers.",
      telephone: "06 00 00 00 00", email: "", adresse: "Pessac et Bordeaux Métropole",
      horaires: "Lundi - Vendredi : 7h - 19h\nSamedi : 8h - 13h",
      services: "Ménage à domicile | 25 € / h\nGrand nettoyage | sur devis\nNettoyage de vitres | à partir de 60 €\nNettoyage de bureaux | sur devis\nFin de bail / fin de chantier | sur devis",
      couleur: "#0891b2"
    }
  },

  serrurier: {
    nom: "Serrurier / Vitrier", icone: "🔑", categorie: "Maison & travaux",
    resume: "Direct et fiable, pour un serrurier ou un vitrier qui intervient en urgence.",
    libelles: { boutonAppel: "Urgence" },
    defauts: {
      nom: "Serrurerie Express 33",
      slogan: "Ouverture de porte et dépannage en moins de 30 minutes.",
      description: "Porte claquée, clé perdue, serrure cassée, vitre brisée : un serrurier local intervient rapidement, avec un prix annoncé avant de commencer. Pas de mauvaise surprise.",
      telephone: "06 00 00 00 00", email: "", adresse: "Pessac et alentours",
      horaires: "7j/7 : 24h/24",
      services: "Ouverture de porte claquée | à partir de 89 €\nChangement de cylindre | à partir de 120 €\nPose de serrure 3 points | sur devis\nRemplacement de vitre | sur devis\nMise en sécurité après effraction | sur devis",
      couleur: "#dc2626"
    }
  },

  demenagement: {
    nom: "Déménagement / Transport", icone: "📦", categorie: "Maison & travaux",
    resume: "Solide, pour un déménageur, un transporteur ou un service de débarras.",
    defauts: {
      nom: "Allo Déménage",
      slogan: "Déménagements, livraisons et débarras, sans stress.",
      description: "Petite équipe sérieuse équipée d'un camion de 20 m³. Déménagements locaux et longue distance, transport de meubles, débarras de caves et greniers. Devis gratuit.",
      telephone: "06 00 00 00 00", email: "", adresse: "Pessac (33) - partout en France",
      horaires: "Lundi - Samedi : 8h - 19h",
      services: "Déménagement studio | à partir de 290 €\nDéménagement maison | sur devis\nTransport d'un meuble | à partir de 60 €\nDébarras cave / grenier | sur devis\nFourniture de cartons | 2 € / carton",
      couleur: "#ea580c"
    }
  },

  // ===================== AUTO & TRANSPORT =====================

  garage: {
    nom: "Garage / Mécanique", icone: "🚗", categorie: "Auto & transport",
    resume: "Solide et rassurant, pour un garage ou un atelier de réparation.",
    defauts: {
      nom: "Garage Martin",
      slogan: "Entretien et réparation toutes marques, au juste prix.",
      description: "Garage indépendant depuis plus de 15 ans, nous entretenons et réparons votre véhicule avec sérieux. Devis gratuit et détaillé avant chaque intervention, sans mauvaise surprise.",
      telephone: "05 00 00 00 00", email: "", adresse: "10 avenue Jean Jaurès, 33600 Pessac",
      horaires: "Lundi - Vendredi : 8h - 12h / 14h - 18h\nSamedi - Dimanche : fermé",
      services: "Vidange + filtre | à partir de 79 €\nPlaquettes de frein | à partir de 99 €\nDiagnostic électronique | 49 €\nPré-contrôle technique | 29 €\nClimatisation (recharge) | 69 €",
      couleur: "#e4572e"
    }
  },

  autoecole: {
    nom: "Auto-école", icone: "🚦", categorie: "Auto & transport",
    resume: "Dynamique et clair, pour une auto-école ou une moto-école.",
    libelles: { menuServices: "Forfaits", titreServices: "Nos forfaits", voirServices: "Voir les forfaits" },
    defauts: {
      nom: "Auto-École du Centre",
      slogan: "Code et permis B, avec des moniteurs patients et motivés.",
      description: "Préparez votre code en salle ou en ligne et votre permis avec des moniteurs à l'écoute. Conduite accompagnée dès 15 ans, boîte manuelle ou automatique. Paiement en plusieurs fois possible.",
      telephone: "05 00 00 00 00", email: "", adresse: "4 avenue Pasteur, 33600 Pessac",
      horaires: "Lundi : 14h - 19h\nMardi - Vendredi : 10h - 12h / 14h - 19h\nSamedi : 9h - 13h",
      services: "Forfait code | 190 €\nPermis B (20 h) | 1 290 €\nPermis boîte automatique (13 h) | 990 €\nConduite accompagnée | 1 390 €\nHeure de conduite | 55 €",
      couleur: "#16a34a"
    }
  },

  taxi: {
    nom: "Taxi / VTC", icone: "🚕", categorie: "Auto & transport",
    resume: "Percutant, pour un taxi, un VTC ou un service de navettes.",
    libelles: { menuServices: "Tarifs", titreServices: "Trajets & tarifs", boutonAppel: "Réserver" },
    defauts: {
      nom: "Taxi Pessac",
      slogan: "Gare, aéroport et trajets longue distance, 7j/7.",
      description: "Chauffeur local, véhicule confortable et climatisé. Transferts aéroport de Mérignac et gare Saint-Jean, transport médical conventionné, trajets longue distance. Réservation à l'avance conseillée.",
      telephone: "06 00 00 00 00", email: "", adresse: "Pessac et Bordeaux Métropole",
      horaires: "7j/7 : 5h - 23h\nNuit : sur réservation",
      services: "Pessac → Aéroport de Mérignac | à partir de 25 €\nPessac → Gare Saint-Jean | à partir de 30 €\nMise à disposition | 45 € / h\nTransport médical | conventionné CPAM\nLongue distance | sur devis",
      couleur: "#facc15"
    }
  },

  // ===================== SANTÉ =====================

  kine: {
    nom: "Kinésithérapeute", icone: "🦴", categorie: "Santé",
    resume: "Calme et professionnel, pour un kiné ou un cabinet de rééducation.",
    libelles: { menuServices: "Soins", titreServices: "Soins proposés", voirServices: "Voir les soins", boutonAppel: "Prendre RDV" },
    defauts: {
      nom: "Cabinet de Kinésithérapie Pasteur",
      slogan: "Rééducation, sport et bien-être, sur rendez-vous.",
      description: "Notre cabinet vous accueille pour la rééducation après une blessure ou une opération, la kiné du sport, la rééducation respiratoire et les douleurs du dos. Accessible aux personnes à mobilité réduite.",
      telephone: "05 00 00 00 00", email: "", adresse: "25 avenue Pasteur, 33600 Pessac",
      horaires: "Lundi - Vendredi : 8h - 20h\nSamedi : 8h - 12h",
      services: "Séance sur prescription | tarif conventionné\nKiné du sport | tarif conventionné\nRééducation respiratoire | tarif conventionné\nDrainage lymphatique | tarif conventionné",
      couleur: "#0284c7"
    }
  },

  osteopathe: {
    nom: "Ostéopathe / Praticien", icone: "🩺", categorie: "Santé",
    resume: "Doux et apaisant, pour un ostéopathe, un naturopathe ou un diététicien.",
    libelles: { menuServices: "Consultations", titreServices: "Consultations", voirServices: "Voir les tarifs", boutonAppel: "Prendre RDV" },
    defauts: {
      nom: "Camille Durand, Ostéopathe",
      slogan: "Ostéopathie pour adultes, enfants, sportifs et femmes enceintes.",
      description: "Mal de dos, torticolis, tensions, troubles du sommeil : l'ostéopathie aide à soulager de nombreux maux. Consultations sur rendez-vous. Pensez à vérifier le remboursement par votre mutuelle.",
      telephone: "06 00 00 00 00", email: "", adresse: "11 rue Paul Painlevé, 33600 Pessac",
      horaires: "Lundi - Vendredi : 9h - 20h\nSamedi : 9h - 13h",
      services: "Consultation adulte | 60 €\nConsultation enfant / nourrisson | 50 €\nConsultation sportif | 60 €\nConsultation femme enceinte | 60 €",
      couleur: "#14b8a6"
    }
  },

  // ===================== SPORT & LOISIRS =====================

  coach: {
    nom: "Coach sportif", icone: "💪", categorie: "Sport & loisirs",
    resume: "Énergique et motivant, pour un coach sportif ou un préparateur physique.",
    libelles: { menuServices: "Offres", titreServices: "Mes offres", voirServices: "Voir les offres", boutonAppel: "Séance d'essai" },
    defauts: {
      nom: "Alex Coaching",
      slogan: "Perte de poids, prise de muscle, remise en forme : on y va ensemble.",
      description: "Coach sportif diplômé, je vous accompagne à domicile, en extérieur ou en salle avec un programme adapté à votre niveau et à vos objectifs. Première séance d'essai offerte.",
      telephone: "06 00 00 00 00", email: "", adresse: "Pessac, Talence, Mérignac",
      horaires: "Lundi - Vendredi : 6h30 - 21h\nSamedi : 8h - 13h",
      services: "Séance d'essai | offerte\nSéance individuelle 1h | 45 €\nCarnet de 10 séances | 400 €\nCoaching en duo | 30 € / pers.\nProgramme en ligne (1 mois) | 49 €",
      couleur: "#ef4444"
    }
  },

  salle: {
    nom: "Salle de sport / CrossFit / Boxe", icone: "🏋️", categorie: "Sport & loisirs",
    resume: "Puissant, pour une salle de sport, un club de boxe ou de CrossFit.",
    libelles: { menuServices: "Abonnements", titreServices: "Abonnements", voirServices: "Voir les abonnements", boutonAppel: "Essai gratuit" },
    defauts: {
      nom: "Iron Gym Pessac",
      slogan: "Musculation, cours collectifs et coachs sur place.",
      description: "Plus de 800 m² d'équipements, un espace cardio, des cours collectifs tous les jours et des coachs pour vous conseiller. Ambiance motivante, sans prise de tête.",
      telephone: "05 00 00 00 00", email: "", adresse: "Parc d'activités, 33600 Pessac",
      horaires: "Lundi - Vendredi : 6h - 23h\nSamedi - Dimanche : 8h - 20h",
      services: "Séance découverte | offerte\nAbonnement mensuel sans engagement | 34,90 €\nAbonnement annuel | 24,90 € / mois\nÉtudiants | 19,90 € / mois\nCours collectifs | inclus",
      couleur: "#22c55e"
    }
  },

  danse: {
    nom: "École de danse / Yoga / Club", icone: "💃", categorie: "Sport & loisirs",
    resume: "Artistique et vivant, pour une école de danse, un studio de yoga ou une association.",
    libelles: { menuServices: "Cours", titreServices: "Cours & tarifs", voirServices: "Voir les cours", boutonAppel: "Cours d'essai" },
    defauts: {
      nom: "Studio Mouvement",
      slogan: "Danse, yoga et pilates pour enfants, ados et adultes.",
      description: "Hip-hop, modern jazz, danse classique, yoga et pilates : trouvez le cours qui vous ressemble, quel que soit votre niveau. Gala de fin d'année et stages pendant les vacances.",
      telephone: "05 00 00 00 00", email: "", adresse: "2 rue Léon Morin, 33600 Pessac",
      horaires: "Lundi - Vendredi : 17h - 21h30\nMercredi : 10h - 21h30\nSamedi : 9h - 17h",
      services: "Cours d'essai | offert\nCours enfant (1h / semaine) | 220 € / an\nCours adulte (1h / semaine) | 280 € / an\nCarte 10 cours yoga | 120 €\nStage vacances (5 jours) | 90 €",
      couleur: "#a855f7"
    }
  },

  musique: {
    nom: "Cours de musique / Chant", icone: "🎸", categorie: "Sport & loisirs",
    resume: "Créatif, pour un professeur de musique, une école de musique ou un studio.",
    libelles: { menuServices: "Cours", titreServices: "Cours & tarifs", voirServices: "Voir les cours" },
    defauts: {
      nom: "Notes & Accords",
      slogan: "Guitare, piano et chant, pour tous les âges et tous les niveaux.",
      description: "Apprenez à jouer vos morceaux préférés avec un professeur passionné. Cours individuels ou en petit groupe, à domicile ou au studio. Débutants bienvenus !",
      telephone: "06 00 00 00 00", email: "", adresse: "Pessac et alentours",
      horaires: "Lundi - Vendredi : 14h - 21h\nSamedi : 9h - 18h",
      services: "Cours d'essai 30 min | offert\nCours individuel 45 min | 30 €\nForfait 10 cours | 270 €\nCours en groupe (3-5 élèves) | 15 € / pers.\nCours à domicile | + 5 €",
      couleur: "#f97316"
    }
  },

  // ===================== SERVICES =====================

  photographe: {
    nom: "Photographe / Vidéaste", icone: "📷", categorie: "Services",
    resume: "Sobre et artistique pour mettre les photos en avant. Idéal photographe ou vidéaste.",
    libelles: { menuServices: "Prestations", titreServices: "Prestations" },
    defauts: {
      nom: "Lumière Studio",
      slogan: "Mariages, portraits, familles et photos d'entreprise.",
      description: "Photographe basé à Pessac, je capture vos moments importants avec naturel et sensibilité. Séances en studio ou en extérieur, retouches incluses et galerie en ligne privée.",
      telephone: "06 00 00 00 00", email: "", adresse: "Pessac et toute la Gironde",
      horaires: "Lundi - Samedi : sur rendez-vous",
      services: "Séance portrait (1h) | 150 €\nSéance famille / grossesse | 190 €\nMariage (journée) | à partir de 1 200 €\nPhotos d'entreprise | sur devis\nVidéo événement | sur devis",
      couleur: "#d4a373"
    }
  },

  informatique: {
    nom: "Réparation téléphone / Informatique", icone: "📱", categorie: "Services",
    resume: "Moderne et clair, pour la réparation de téléphones, d'ordinateurs ou le dépannage informatique.",
    defauts: {
      nom: "Répar'Phone Pessac",
      slogan: "Écran cassé ? Batterie faible ? Réparé en moins d'une heure.",
      description: "Réparation de smartphones, tablettes, consoles et ordinateurs, toutes marques. Diagnostic gratuit, pièces de qualité garanties 6 mois. Vente de coques et accessoires.",
      telephone: "05 00 00 00 00", email: "", adresse: "33 avenue Jean Jaurès, 33600 Pessac",
      horaires: "Lundi - Samedi : 10h - 19h\nDimanche : fermé",
      services: "Diagnostic | gratuit\nÉcran iPhone | à partir de 69 €\nÉcran Samsung | à partir de 79 €\nChangement de batterie | à partir de 39 €\nRéparation manette / console | à partir de 30 €\nNettoyage PC + réinstallation | 49 €",
      couleur: "#6366f1"
    }
  },

  cours: {
    nom: "Soutien scolaire / Cours particuliers", icone: "📚", categorie: "Services",
    resume: "Clair et bienveillant, pour du soutien scolaire, des cours de langues ou de l'aide aux devoirs.",
    libelles: { menuServices: "Cours", titreServices: "Cours & tarifs", voirServices: "Voir les tarifs" },
    defauts: {
      nom: "Réussite Scolaire",
      slogan: "Cours particuliers du primaire au lycée, à domicile ou en ligne.",
      description: "Maths, français, anglais, physique : des cours adaptés au rythme de chaque élève pour reprendre confiance et progresser. Préparation au brevet et au bac. 50 % de crédit d'impôt.",
      telephone: "06 00 00 00 00", email: "", adresse: "Pessac, Talence, Gradignan",
      horaires: "Lundi - Vendredi : 16h - 20h\nMercredi : 13h - 20h\nSamedi : 9h - 17h",
      services: "Cours primaire (1h) | 25 €\nCours collège (1h) | 28 €\nCours lycée (1h) | 32 €\nStage de révision brevet / bac | 120 € / semaine\nCours en ligne | - 3 € / h",
      couleur: "#2563eb"
    }
  },

  couture: {
    nom: "Retouches / Couture / Pressing", icone: "🧵", categorie: "Services",
    resume: "Doux et soigné, pour une couturière, un atelier de retouches ou un pressing.",
    defauts: {
      nom: "L'Atelier du Fil",
      slogan: "Retouches, ourlets et créations sur mesure.",
      description: "Ourlets, fermetures éclair, ajustements, réparations : nous redonnons une seconde vie à vos vêtements. Retouches express en 24 h et créations sur mesure.",
      telephone: "05 00 00 00 00", email: "", adresse: "6 avenue de Magonty, 33600 Pessac",
      horaires: "Lundi : fermé\nMardi - Vendredi : 9h30 - 18h30\nSamedi : 9h30 - 13h",
      services: "Ourlet pantalon | 12 €\nChangement de fermeture éclair | à partir de 15 €\nAjustement robe | à partir de 20 €\nRetouche express (24 h) | + 5 €\nCréation sur mesure | sur devis",
      couleur: "#b46a78"
    }
  },

  immobilier: {
    nom: "Agence immobilière", icone: "🏠", categorie: "Services",
    resume: "Élégant et sérieux, pour une agence immobilière ou un mandataire.",
    libelles: { menuServices: "Services", titreServices: "Nos services", voirServices: "Nos services" },
    defauts: {
      nom: "Pessac Immobilier",
      slogan: "Vendre, acheter ou louer, avec une agence qui connaît le quartier.",
      description: "Agence indépendante installée à Pessac depuis 2008. Estimation gratuite de votre bien, accompagnement complet de la visite à la signature, gestion locative.",
      telephone: "05 00 00 00 00", email: "", adresse: "14 avenue Pasteur, 33600 Pessac",
      horaires: "Lundi - Vendredi : 9h - 12h30 / 14h - 19h\nSamedi : 9h - 12h30 / 14h - 17h",
      services: "Estimation de votre bien | gratuite\nVente | honoraires selon barème\nLocation | honoraires selon barème\nGestion locative | à partir de 6 % des loyers",
      couleur: "#1e3a5f"
    }
  },

  comptable: {
    nom: "Comptable / Avocat / Conseil", icone: "💼", categorie: "Services",
    resume: "Sobre et professionnel, pour un cabinet comptable, un avocat ou un consultant.",
    libelles: { menuServices: "Expertises", titreServices: "Nos expertises", voirServices: "Nos expertises", boutonAppel: "Prendre RDV" },
    defauts: {
      nom: "Cabinet Lefèvre & Associés",
      slogan: "Expertise comptable pour les artisans, commerçants et indépendants.",
      description: "Nous accompagnons les TPE, artisans et indépendants dans leur comptabilité, leurs déclarations et la création de leur entreprise. Un interlocuteur unique, disponible et réactif.",
      telephone: "05 00 00 00 00", email: "", adresse: "40 avenue Jean Cordier, 33600 Pessac",
      horaires: "Lundi - Vendredi : 9h - 12h30 / 14h - 18h",
      services: "Premier rendez-vous | offert\nTenue de comptabilité | à partir de 90 € / mois\nCréation d'entreprise | à partir de 450 €\nDéclarations fiscales | sur devis\nConseil et accompagnement | sur devis",
      couleur: "#334155"
    }
  },

  toilettage: {
    nom: "Toilettage / Garde d'animaux", icone: "🐶", categorie: "Services",
    resume: "Joyeux et doux, pour un toiletteur, un pet-sitter ou une pension pour animaux.",
    libelles: { boutonAppel: "Prendre RDV" },
    defauts: {
      nom: "Patte Douce",
      slogan: "Toilettage chiens et chats, dans le calme et la douceur.",
      description: "Bain, coupe, démêlage, griffes : votre compagnon est chouchouté par une toiletteuse diplômée, sans cage et sans stress. Garde et promenades à domicile également.",
      telephone: "06 00 00 00 00", email: "", adresse: "10 avenue de Magonty, 33600 Pessac",
      horaires: "Lundi : fermé\nMardi - Samedi : 9h - 18h (sur rendez-vous)",
      services: "Toilettage petit chien | à partir de 40 €\nToilettage grand chien | à partir de 65 €\nToilettage chat | à partir de 50 €\nCoupe des griffes | 10 €\nPromenade à domicile (30 min) | 15 €",
      couleur: "#d97706"
    }
  }
};

// ============================================================
//  ENCORE PLUS DE MÉTIERS
//  Écrits en version courte avec la fonction ajouter(...) :
//  ajouter(identifiant, nom du métier, icône, catégorie, {
//    nom, slogan, description, services, horaires, (adresse), (telephone)
//  }, (libelles), (mots-clés pour la recherche))
// ============================================================

function ajouter(id, nomMetier, icone, categorie, textes, libelles, mots) {
  METIERS[id] = {
    nom: nomMetier, icone, categorie, libelles, mots: mots || "",
    defauts: {
      telephone: "05 00 00 00 00", email: "", adresse: "Pessac et alentours (33)",
      ...textes
    }
  };
}

// "Autre" : pour ceux dont le métier n'est pas dans la liste (toujours en premier)
METIERS.autre = {
  nom: "Autre (mon métier n'est pas dans la liste)", icone: "✳️", categorie: "", mots: "autre divers aucun",
  defauts: {
    nom: "Mon entreprise",
    slogan: "Une phrase courte qui dit ce que vous faites de mieux.",
    description: "Présentez votre activité en quelques lignes : ce que vous proposez, depuis quand, et pourquoi vos clients vous font confiance.",
    telephone: "06 00 00 00 00", email: "", adresse: "Pessac (33)",
    horaires: "Lundi - Vendredi : 9h - 18h\nSamedi : 9h - 12h\nDimanche : fermé",
    services: "Prestation 1 | 00 €\nPrestation 2 | 00 €\nPrestation 3 | sur devis"
  }
};

METIERS.toilettage.categorie = "Animaux";

const RDV = { boutonAppel: "Prendre RDV" };
const CARTE = { menuServices: "Carte", titreServices: "La carte", voirServices: "Voir la carte" };
const PRODUITS = { menuServices: "Produits", titreServices: "Nos produits", voirServices: "Voir nos produits" };
const COMMANDER = { ...CARTE, boutonAppel: "Commander" };

// ---------- Beauté & bien-être ----------
ajouter("onglerie", "Onglerie / Prothésiste ongulaire", "💅", "Beauté & bien-être", {
  nom: "Nail Studio", slogan: "Pose gel, semi-permanent et nail art, sur rendez-vous.",
  description: "Des ongles impeccables qui tiennent : pose gel, capsules, semi-permanent et nail art personnalisé. Hygiène irréprochable et produits de qualité.",
  services: "Semi-permanent mains | 30 €\nPose gel complète | 50 €\nRemplissage gel | 40 €\nNail art (par ongle) | 2 €\nDépose | 15 €",
  horaires: "Mardi - Vendredi : 9h30 - 19h\nSamedi : 9h - 17h\nDimanche - Lundi : fermé", adresse: "7 avenue Pasteur, 33600 Pessac"
}, RDV, "ongles manucure nail");
ajouter("maquillage", "Maquilleuse", "💄", "Beauté & bien-être", {
  nom: "Julie Make-up", slogan: "Maquillage mariée, soirée et cours d'auto-maquillage.",
  description: "Maquilleuse professionnelle, je me déplace pour sublimer votre beauté le jour J. Essai inclus pour les mariées, cours individuels pour apprendre à vous maquiller.",
  services: "Maquillage soirée | 45 €\nMaquillage mariée (essai inclus) | 150 €\nCours d'auto-maquillage (1h30) | 60 €\nMaquillage enfant (événement) | sur devis",
  horaires: "Lundi - Samedi : sur rendez-vous\nDimanche : mariages uniquement", telephone: "06 00 00 00 00"
}, RDV, "make-up makeup mariage");
ajouter("cils", "Extensions de cils / Regard", "👁️", "Beauté & bien-être", {
  nom: "L'Atelier du Regard", slogan: "Extensions de cils, rehaussement et sourcils parfaits.",
  description: "Un regard intense et naturel : extensions cil à cil ou volume russe, rehaussement de cils et restructuration des sourcils, réalisés avec précision.",
  services: "Rehaussement de cils | 55 €\nExtensions cil à cil | 80 €\nVolume russe | 110 €\nRemplissage (3 semaines) | 45 €\nRestructuration sourcils | 20 €",
  horaires: "Mardi - Samedi : 9h - 19h\nDimanche - Lundi : fermé", adresse: "12 avenue de Magonty, 33600 Pessac"
}, RDV, "sourcils");
ajouter("coiffure-domicile", "Coiffeur / Coiffeuse à domicile", "🏡", "Beauté & bien-être", {
  nom: "Coiff'à Dom", slogan: "Votre coiffeuse se déplace chez vous, sans supplément.",
  description: "Coupe, couleur, brushing ou chignon : je viens chez vous avec tout mon matériel. Idéal pour les familles, les personnes âgées ou les emplois du temps chargés.",
  services: "Coupe femme + brushing | 35 €\nCoupe homme | 18 €\nCoupe enfant | 12 €\nCouleur | à partir de 40 €\nCoiffure de mariage | sur devis",
  horaires: "Lundi - Samedi : 8h30 - 19h (sur rendez-vous)", telephone: "06 00 00 00 00"
}, RDV, "coiffeur coiffeuse domicile");

// ---------- Restauration ----------
ajouter("burger", "Burger", "🍔", "Restauration", {
  nom: "Le Burger du Coin", slogan: "Burgers maison, frites fraîches et milkshakes.",
  description: "Steak haché frais, pain brioché artisanal et sauces maison : nos burgers sont préparés à la minute. Sur place, à emporter ou en livraison.",
  services: "Classic cheese | 11 €\nBacon BBQ | 13 €\nVeggie | 12 €\nFrites maison | 3,50 €\nMilkshake | 5 €\nMenu enfant | 8 €",
  horaires: "Lundi - Jeudi : 11h30 - 14h / 18h30 - 22h\nVendredi - Samedi : 11h30 - 14h30 / 18h30 - 23h\nDimanche : 18h30 - 22h", adresse: "30 avenue Jean Jaurès, 33600 Pessac"
}, COMMANDER, "hamburger fast food");
ajouter("sushi", "Sushi / Japonais", "🍣", "Restauration", {
  nom: "Sakura Sushi", slogan: "Sushis, makis et plats japonais préparés devant vous.",
  description: "Poisson frais livré chaque jour, riz vinaigré maison et recettes traditionnelles. Plateaux à partager, sur place ou à emporter.",
  services: "Plateau découverte (18 pièces) | 19 €\nCalifornia saumon avocat (8) | 7,50 €\nChirashi saumon | 15 €\nRamen | 13 €\nMochi (2) | 5 €",
  horaires: "Mardi - Dimanche : 11h30 - 14h30 / 18h30 - 22h30\nLundi : fermé", adresse: "4 place de la Ve République, 33600 Pessac"
}, COMMANDER, "japonais maki asiatique");
ajouter("kebab", "Kebab / Snack", "🥙", "Restauration", {
  nom: "Istanbul Grill", slogan: "Kebabs, tacos et assiettes grillées, jusqu'à tard.",
  description: "Viande marinée maison, pain cuit sur place et crudités fraîches. Ouvert tard le soir, sur place, à emporter ou en livraison.",
  services: "Kebab sandwich | 7 €\nTacos 2 viandes | 9 €\nAssiette kebab frites | 12 €\nMenu + boisson | + 2 €\nBaklava | 2 €",
  horaires: "Lundi - Dimanche : 11h - 15h / 18h - 1h", adresse: "50 avenue Jean Jaurès, 33600 Pessac"
}, COMMANDER, "snack tacos grill");
ajouter("creperie", "Crêperie", "🥞", "Restauration", {
  nom: "La Crêpe Dorée", slogan: "Galettes de sarrasin et crêpes à la bretonne.",
  description: "Galettes de blé noir et crêpes de froment préparées à la minute sur billig, avec des produits bretons. Cidre et bolée de lait ribot pour accompagner.",
  services: "Galette complète | 9,50 €\nGalette savoyarde | 12 €\nCrêpe beurre sucre | 4 €\nCrêpe caramel beurre salé | 6 €\nBolée de cidre | 3,50 €",
  horaires: "Mardi - Samedi : 12h - 14h / 19h - 22h\nDimanche : 12h - 15h", adresse: "9 rue Paul Doumer, 33600 Pessac"
}, CARTE, "crepe galette bretagne");
ajouter("glacier", "Glacier", "🍦", "Restauration", {
  nom: "Givrée", slogan: "Glaces et sorbets artisanaux, fabriqués ici.",
  description: "Nos glaces sont turbinées chaque matin avec du lait frais et des fruits de saison. Plus de 24 parfums, cornets maison et coupes gourmandes.",
  services: "1 boule | 2,80 €\n2 boules | 4,80 €\n3 boules | 6,50 €\nCoupe gourmande | 8 €\nPot 500 ml à emporter | 9 €",
  horaires: "Avril - Septembre : 13h - 23h tous les jours\nOctobre - Mars : week-end 14h - 19h", adresse: "2 place de la Ve République, 33600 Pessac"
}, PRODUITS, "glace sorbet");
ajouter("chocolatier", "Chocolatier / Confiseur", "🍫", "Restauration", {
  nom: "Maison Cacao", slogan: "Chocolats fins et confiseries artisanales.",
  description: "Bonbons de chocolat, tablettes, pâtes de fruits et créations de saison, fabriqués dans notre atelier. Coffrets cadeaux pour toutes les occasions.",
  services: "Ballotin 250 g | 20 €\nTablette origine | 6,50 €\nPâtes de fruits (200 g) | 9 €\nCoffret cadeau | à partir de 25 €\nCommande entreprise | sur devis",
  horaires: "Mardi - Samedi : 10h - 19h\nDimanche : 10h - 13h", adresse: "14 avenue Pasteur, 33600 Pessac"
}, PRODUITS, "chocolat confiserie bonbon");
ajouter("bar", "Bar / Bar à cocktails", "🍸", "Restauration", {
  nom: "Le Comptoir des Amis", slogan: "Cocktails, bières pression et planches à partager.",
  description: "Un bar convivial pour se retrouver après le travail : cocktails maison, bières locales, vins et planches de charcuterie et fromages. Soirées concerts le vendredi.",
  services: "Bière pression (25 cl) | 3,50 €\nCocktail signature | 9 €\nMocktail sans alcool | 6 €\nVerre de vin | 4,50 €\nPlanche mixte | 16 €",
  horaires: "Mardi - Jeudi : 17h - 0h\nVendredi - Samedi : 17h - 2h\nDimanche - Lundi : fermé", adresse: "22 avenue Jean Jaurès, 33600 Pessac"
}, CARTE, "cocktail pub biere");
ajouter("asiatique", "Restaurant asiatique", "🥢", "Restauration", {
  nom: "Le Jardin de Saigon", slogan: "Cuisine vietnamienne et thaï, faite maison.",
  description: "Bo bun, nems croustillants, pad thaï et currys parfumés : une cuisine familiale et généreuse, préparée avec des produits frais.",
  services: "Nems (4) | 6 €\nBo bun bœuf | 13 €\nPad thaï crevettes | 14 €\nCurry vert poulet | 13 €\nFormule midi | 14,50 €",
  horaires: "Mardi - Dimanche : 11h45 - 14h / 19h - 22h\nLundi : fermé", adresse: "18 avenue de Magonty, 33600 Pessac"
}, COMMANDER, "vietnamien thai chinois");

// ---------- Commerces ----------
ajouter("fromagerie", "Fromagerie / Crèmerie", "🧀", "Commerces", {
  nom: "La Fromagerie du Marché", slogan: "Fromages affinés, crèmerie et plateaux sur mesure.",
  description: "Plus de 150 fromages sélectionnés chez de petits producteurs et affinés dans nos caves. Plateaux pour vos repas et conseils d'accords mets-vins.",
  services: "Fromages à la coupe | au poids\nPlateau 4 personnes | 28 €\nRaclette (par personne) | 9 €\nBeurre de baratte | 4,50 €\nPanier garni cadeau | à partir de 35 €",
  horaires: "Mardi - Samedi : 8h30 - 13h / 15h30 - 19h30\nDimanche : 8h30 - 13h", adresse: "5 place de la Ve République, 33600 Pessac"
}, PRODUITS, "fromage cremerie");
ajouter("primeur", "Primeur / Fruits et légumes", "🥕", "Commerces", {
  nom: "Le Panier Frais", slogan: "Fruits et légumes de saison, direct des producteurs.",
  description: "Des fruits et légumes frais, locaux et de saison, arrivés le matin même. Paniers de la semaine et livraison à domicile possible.",
  services: "Panier de la semaine | 15 € / 25 €\nFruits et légumes | au poids\nJus de fruits pressés | 4 €\nLivraison à Pessac | 3 €",
  horaires: "Mardi - Samedi : 8h - 19h30\nDimanche : 8h - 13h", adresse: "16 avenue Pasteur, 33600 Pessac"
}, PRODUITS, "fruits legumes marche");
ajouter("poissonnerie", "Poissonnerie", "🐟", "Commerces", {
  nom: "La Marée d'Arcachon", slogan: "Poissons, coquillages et plateaux de fruits de mer.",
  description: "Arrivages quotidiens du bassin d'Arcachon et de la côte atlantique. Huîtres, poissons entiers ou en filets, plateaux de fruits de mer sur commande.",
  services: "Huîtres du bassin (douzaine) | 9 €\nFilets de dorade | 28 € / kg\nPlateau de fruits de mer (2 pers.) | 55 €\nSoupe de poisson maison | 7 €",
  horaires: "Mardi - Samedi : 8h - 13h / 16h - 19h\nDimanche : 8h - 13h", adresse: "3 place de la Ve République, 33600 Pessac"
}, PRODUITS, "poisson huitre fruits de mer");
ajouter("librairie", "Librairie / Papeterie", "📚", "Commerces", {
  nom: "La Page Blanche", slogan: "Librairie indépendante, conseils et rencontres d'auteurs.",
  description: "Romans, BD, jeunesse, livres pratiques et papeterie : notre équipe de passionnés vous conseille et commande tout livre en 48 h. Dédicaces régulières.",
  services: "Commande de livres | en 48 h\nCarte de fidélité | 5 % offerts\nFournitures scolaires | selon liste\nCarte cadeau | au choix",
  horaires: "Mardi - Samedi : 9h30 - 19h\nDimanche - Lundi : fermé", adresse: "8 avenue Pasteur, 33600 Pessac"
}, PRODUITS, "livre bd papeterie");
ajouter("opticien", "Opticien", "👓", "Commerces", {
  nom: "Optique Vision", slogan: "Lunettes, lentilles et examen de vue sur place.",
  description: "Large choix de montures, verres de qualité et examen de la vue réalisé par un opticien diplômé. Tiers payant avec la plupart des mutuelles.",
  services: "Examen de vue | offert\nLunettes unifocales | à partir de 89 €\nLunettes progressives | à partir de 199 €\nLentilles (mois) | à partir de 25 €\nAjustage et réparation | gratuit",
  horaires: "Lundi : 14h - 19h\nMardi - Samedi : 9h30 - 12h30 / 14h - 19h", adresse: "20 avenue Pasteur, 33600 Pessac"
}, RDV, "lunettes lentilles vue");
ajouter("bijouterie", "Bijouterie / Créatrice de bijoux", "💍", "Commerces", {
  nom: "Éclat d'Or", slogan: "Bijoux, montres et créations sur mesure.",
  description: "Bijoux en or, argent et pierres précieuses, montres et alliances. Atelier de réparation et créations uniques dessinées avec vous.",
  services: "Création sur mesure | sur devis\nAlliances | à partir de 250 €\nRéparation / mise à taille | à partir de 25 €\nChangement de pile | 10 €\nGravure | 15 €",
  horaires: "Mardi - Samedi : 10h - 12h30 / 14h - 19h", adresse: "10 avenue Jean Jaurès, 33600 Pessac"
}, PRODUITS, "bijoux montre or alliance");
ajouter("vetements", "Boutique de vêtements", "👗", "Commerces", {
  nom: "Maison Lila", slogan: "Mode femme et accessoires, des pièces choisies avec soin.",
  description: "Une boutique à taille humaine où l'on vient pour les coups de cœur : vêtements, sacs et bijoux de créateurs, renouvelés chaque semaine.",
  services: "Robes | à partir de 45 €\nHauts | à partir de 25 €\nAccessoires | à partir de 15 €\nCarte cadeau | au choix\nConseil personnalisé | offert",
  horaires: "Mardi - Samedi : 10h - 19h\nDimanche - Lundi : fermé", adresse: "6 avenue Pasteur, 33600 Pessac"
}, PRODUITS, "mode pret-a-porter habits");
ajouter("friperie", "Friperie / Seconde main", "♻️", "Commerces", {
  nom: "Deuxième Vie", slogan: "Vêtements vintage et seconde main, triés à la main.",
  description: "Des pièces vintage et de seconde main en très bon état, pour une mode plus responsable. Dépôt-vente et rachat de vos vêtements.",
  services: "T-shirts | à partir de 5 €\nVestes | à partir de 20 €\nPièces vintage | à partir de 15 €\nDépôt-vente | 50 % pour vous",
  horaires: "Mercredi - Samedi : 11h - 19h\nDimanche : 14h - 18h", adresse: "25 avenue Jean Jaurès, 33600 Pessac"
}, PRODUITS, "vintage occasion depot vente");
ajouter("velo", "Magasin / Réparation de vélos", "🚲", "Commerces", {
  nom: "Cycles Pessac", slogan: "Vélos, vélos électriques et atelier de réparation.",
  description: "Vente de vélos de ville, VTT et vélos électriques, et atelier de réparation toutes marques. Révision rapide, souvent le jour même.",
  services: "Révision complète | 55 €\nCrevaison (main d'œuvre) | 12 €\nRéglage freins | 15 €\nVélo électrique | à partir de 1 290 €\nLocation à la journée | 25 €",
  horaires: "Mardi - Samedi : 9h30 - 12h30 / 14h - 19h", adresse: "35 avenue Jean Cordier, 33600 Pessac"
}, null, "cycle vtt electrique");
ajouter("deco", "Décoration / Concept store", "🪴", "Commerces", {
  nom: "Le Petit Grenier", slogan: "Décoration, cadeaux et objets de créateurs.",
  description: "Un concept store plein d'idées : décoration, bougies, vaisselle, papeterie et cadeaux d'artisans. Emballage cadeau offert.",
  services: "Bougies artisanales | à partir de 18 €\nVaisselle | à partir de 8 €\nIdées cadeaux | à partir de 10 €\nEmballage cadeau | offert",
  horaires: "Mardi - Samedi : 10h - 19h\nDimanche : 10h - 13h", adresse: "11 avenue Pasteur, 33600 Pessac"
}, PRODUITS, "cadeau concept store maison");
ajouter("animalerie", "Animalerie", "🐾", "Animaux", {
  nom: "Mon Ami Animal", slogan: "Tout pour vos animaux : alimentation, accessoires, conseils.",
  description: "Croquettes, accessoires, jouets et produits d'hygiène pour chiens, chats, rongeurs et oiseaux. Conseils personnalisés et livraison à domicile.",
  services: "Croquettes premium (12 kg) | à partir de 45 €\nJouets | à partir de 4 €\nAquariophilie | sur place\nLivraison à domicile | 5 €",
  horaires: "Lundi - Samedi : 9h30 - 19h30", adresse: "Zone commerciale, 33600 Pessac"
}, PRODUITS, "animaux croquettes");
ajouter("jouets", "Magasin de jouets / Jeux", "🧸", "Commerces", {
  nom: "La Boîte à Jeux", slogan: "Jouets, jeux de société et idées cadeaux pour tous.",
  description: "Jeux de société, jouets en bois, puzzles et loisirs créatifs. Soirées jeux chaque mois et conseils pour trouver le cadeau parfait.",
  services: "Jeux de société | à partir de 15 €\nJouets en bois | à partir de 12 €\nPuzzles | à partir de 10 €\nSoirée jeux | 5 € / pers.",
  horaires: "Mardi - Samedi : 10h - 19h\nDimanche (décembre) : 10h - 18h", adresse: "9 avenue Pasteur, 33600 Pessac"
}, PRODUITS, "jeux de societe enfant");

// ---------- Maison & travaux ----------
ajouter("macon", "Maçon", "🧱", "Maison & travaux", {
  nom: "Bâti Gironde", slogan: "Maçonnerie, extension et rénovation, du sol au toit.",
  description: "Entreprise de maçonnerie générale : extensions, murs, dalles, ouvertures et rénovation. Travail soigné, délais respectés et garantie décennale.",
  services: "Dalle béton | à partir de 60 € / m²\nMur de clôture | sur devis\nOuverture de mur porteur | sur devis\nExtension de maison | sur devis\nDevis | gratuit",
  horaires: "Lundi - Vendredi : 8h - 18h", telephone: "06 00 00 00 00"
}, null, "maconnerie construction beton");
ajouter("menuisier", "Menuisier / Ébéniste", "🪚", "Maison & travaux", {
  nom: "L'Atelier du Bois", slogan: "Menuiserie sur mesure : placards, escaliers, fenêtres.",
  description: "Fabrication et pose de menuiseries sur mesure dans notre atelier : dressings, escaliers, portes, fenêtres et meubles. Bois massif et finitions soignées.",
  services: "Dressing sur mesure | sur devis\nPose de fenêtre | à partir de 350 €\nEscalier bois | sur devis\nPorte intérieure posée | à partir de 280 €\nDevis | gratuit",
  horaires: "Lundi - Vendredi : 8h - 12h / 13h30 - 17h30", telephone: "06 00 00 00 00"
}, null, "menuiserie bois ebeniste");
ajouter("couvreur", "Couvreur / Zingueur", "🏠", "Maison & travaux", {
  nom: "Toitures du Sud-Ouest", slogan: "Toiture, gouttières et démoussage.",
  description: "Réparation et rénovation de toitures, pose de gouttières, démoussage et traitement. Intervention rapide en cas de fuite.",
  services: "Démoussage + traitement | à partir de 15 € / m²\nRecherche de fuite | à partir de 150 €\nGouttières zinc | sur devis\nRéfection de toiture | sur devis\nUrgence fuite | 7j/7",
  horaires: "Lundi - Samedi : 8h - 19h", telephone: "06 00 00 00 00"
}, null, "toiture toit gouttiere zinc");
ajouter("carreleur", "Carreleur", "🔲", "Maison & travaux", {
  nom: "Carrelage Pro 33", slogan: "Pose de carrelage, faïence et salles de bain.",
  description: "Pose de carrelage intérieur et extérieur, faïence murale et création de douches à l'italienne. Travail précis et finitions impeccables.",
  services: "Pose de carrelage | à partir de 35 € / m²\nFaïence murale | à partir de 40 € / m²\nDouche à l'italienne | sur devis\nTerrasse carrelée | sur devis",
  horaires: "Lundi - Vendredi : 8h - 18h", telephone: "06 00 00 00 00"
}, null, "carrelage faience salle de bain");
ajouter("cuisiniste", "Cuisiniste / Salles de bain", "🍳", "Maison & travaux", {
  nom: "Cuisines & Bains Design", slogan: "Cuisines et salles de bain sur mesure, pose comprise.",
  description: "Conception 3D gratuite dans notre showroom, fabrication sur mesure et pose par nos équipes. Un seul interlocuteur du projet à la livraison.",
  services: "Conception 3D | gratuite\nCuisine équipée posée | à partir de 5 000 €\nSalle de bain clé en main | à partir de 6 500 €\nPlan de travail | sur devis",
  horaires: "Mardi - Samedi : 9h30 - 12h30 / 14h - 19h", adresse: "Avenue de Canéjan, 33600 Pessac"
}, RDV, "cuisine salle de bain amenagement");
ajouter("pisciniste", "Pisciniste / Entretien piscine", "🏊", "Maison & travaux", {
  nom: "Aqua Services", slogan: "Construction, entretien et réparation de piscines.",
  description: "Entretien hebdomadaire, mise en route, hivernage et réparation de piscines. Construction de piscines coques et béton sur devis.",
  services: "Mise en route saison | 150 €\nEntretien (par passage) | 45 €\nHivernage | 130 €\nRecherche de fuite | sur devis\nConstruction | sur devis",
  horaires: "Lundi - Samedi : 8h - 18h", telephone: "06 00 00 00 00"
}, null, "piscine spa");
ajouter("climatisation", "Climatisation / Pompe à chaleur", "❄️", "Maison & travaux", {
  nom: "Clim & Confort", slogan: "Climatisation, pompes à chaleur et entretien.",
  description: "Installation et entretien de climatisations réversibles et pompes à chaleur par un installateur certifié. Aides de l'État possibles, on vous accompagne.",
  services: "Climatisation monosplit posée | à partir de 1 590 €\nPompe à chaleur air-eau | sur devis\nEntretien annuel | 120 €\nDépannage | à partir de 90 €",
  horaires: "Lundi - Vendredi : 8h - 18h\nSamedi : sur rendez-vous", telephone: "06 00 00 00 00"
}, null, "clim pac chauffage");
ajouter("architecte", "Architecte / Architecte d'intérieur", "📐", "Maison & travaux", {
  nom: "Atelier Lignes", slogan: "Architecture et aménagement intérieur, de l'idée au chantier.",
  description: "Nous concevons vos projets de construction, d'extension et de rénovation, et suivons le chantier jusqu'à la remise des clés. Plans 3D et permis de construire.",
  services: "Premier rendez-vous | offert\nPlans + permis de construire | sur devis\nAménagement intérieur | sur devis\nSuivi de chantier | sur devis",
  horaires: "Lundi - Vendredi : 9h - 18h (sur rendez-vous)", adresse: "15 avenue Jean Cordier, 33600 Pessac"
}, { menuServices: "Services", titreServices: "Nos services", voirServices: "Nos services", boutonAppel: "Prendre RDV" }, "plans permis decoration interieur");
ajouter("ramoneur", "Ramoneur", "🔥", "Maison & travaux", {
  nom: "Ramonage Express", slogan: "Ramonage de cheminées, poêles et inserts, certificat fourni.",
  description: "Ramonage obligatoire avec certificat pour votre assurance, pour cheminées, poêles à bois, à granulés et chaudières. Travail propre, sans salissure.",
  services: "Ramonage cheminée | 60 €\nRamonage poêle à granulés | 70 €\nEntretien poêle à granulés | 120 €\nDébistrage | sur devis",
  horaires: "Lundi - Samedi : 8h - 19h", telephone: "06 00 00 00 00"
}, null, "cheminee poele");
ajouter("multiservice", "Homme toutes mains / Multiservices", "🧰", "Maison & travaux", {
  nom: "Allô Bricolage", slogan: "Petits travaux, montage de meubles et dépannages.",
  description: "Pas le temps ou pas les outils ? Je m'occupe de vos petits travaux : montage de meubles, fixations, petite plomberie, électricité et jardinage. 50 % de crédit d'impôt.",
  services: "Heure de main d'œuvre | 35 €\nMontage de meuble | à partir de 30 €\nPose d'étagères / tableaux | à partir de 25 €\nForfait petits travaux (3h) | 95 €",
  horaires: "Lundi - Samedi : 8h - 19h", telephone: "06 00 00 00 00"
}, null, "bricolage bricoleur petits travaux");

// ---------- Auto & transport ----------
ajouter("carrosserie", "Carrossier", "🚙", "Auto & transport", {
  nom: "Carrosserie Moderne", slogan: "Carrosserie, peinture et débosselage, toutes assurances.",
  description: "Réparation de carrosserie après accident, peinture, débosselage sans peinture et remplacement de pare-brise. Nous gérons les démarches avec votre assurance.",
  services: "Devis | gratuit\nDébosselage sans peinture | à partir de 80 €\nRetouche peinture | à partir de 150 €\nPare-brise | pris en charge\nVéhicule de prêt | sur demande",
  horaires: "Lundi - Vendredi : 8h - 12h / 14h - 18h", adresse: "Zone artisanale, 33600 Pessac"
}, null, "carrosserie peinture auto");
ajouter("lavage-auto", "Lavage / Nettoyage auto", "🧼", "Auto & transport", {
  nom: "Clean Car 33", slogan: "Nettoyage intérieur et extérieur, à domicile ou en station.",
  description: "Votre voiture comme neuve : lavage à la main, nettoyage des sièges, rénovation des phares et lustrage. Nous nous déplaçons aussi chez vous ou au bureau.",
  services: "Lavage extérieur main | 25 €\nNettoyage intérieur complet | 55 €\nFormule complète | 75 €\nRénovation des phares | 40 €\nDéplacement à domicile | + 10 €",
  horaires: "Lundi - Samedi : 9h - 19h", telephone: "06 00 00 00 00"
}, RDV, "nettoyage voiture detailing");
ajouter("garage-moto", "Garage moto / Scooter", "🏍️", "Auto & transport", {
  nom: "Moto Service 33", slogan: "Entretien et réparation motos et scooters toutes marques.",
  description: "Révision, pneus, freins et diagnostic pour motos et scooters toutes marques. Vente d'équipements et d'accessoires.",
  services: "Vidange scooter | à partir de 49 €\nRévision moto | à partir de 120 €\nChangement de pneu (pose) | 25 €\nDiagnostic | 39 €",
  horaires: "Mardi - Samedi : 9h - 12h / 14h - 19h", adresse: "Avenue de Canéjan, 33600 Pessac"
}, null, "moto scooter deux-roues");
ajouter("depannage", "Dépannage / Remorquage", "🛻", "Auto & transport", {
  nom: "Dépannage Rapide 33", slogan: "Dépannage et remorquage 24h/24, 7j/7.",
  description: "Panne, batterie à plat, accident ou crevaison : un dépanneur intervient rapidement sur toute la métropole bordelaise. Agréé par la plupart des assurances.",
  services: "Dépannage sur place | à partir de 80 €\nRemorquage (métropole) | à partir de 120 €\nBatterie à plat | 60 €\nIntervention de nuit | + 30 %",
  horaires: "7j/7 : 24h/24", telephone: "06 00 00 00 00"
}, { boutonAppel: "Urgence" }, "remorquage depanneuse panne");

// ---------- Santé ----------
ajouter("dentiste", "Dentiste", "🦷", "Santé", {
  nom: "Cabinet Dentaire des Écus", slogan: "Soins dentaires, implants et blanchiment.",
  description: "Notre cabinet vous accueille pour les soins courants, la prévention, les prothèses et l'esthétique dentaire. Urgences prises en charge dans la journée.",
  services: "Consultation | tarif conventionné\nDétartrage | tarif conventionné\nBlanchiment | sur devis\nImplant | sur devis\nUrgence dentaire | le jour même",
  horaires: "Lundi - Vendredi : 8h30 - 19h\nSamedi : 9h - 12h", adresse: "30 avenue Pasteur, 33600 Pessac"
}, { menuServices: "Soins", titreServices: "Soins proposés", voirServices: "Voir les soins", boutonAppel: "Prendre RDV" }, "dentaire dents");
ajouter("infirmier", "Infirmier / Infirmière", "💉", "Santé", {
  nom: "Cabinet Infirmier Pasteur", slogan: "Soins infirmiers à domicile et au cabinet, 7j/7.",
  description: "Prises de sang, pansements, injections, suivi de diabète et soins post-opératoires, au cabinet ou à domicile, tous les jours de l'année.",
  services: "Prise de sang | conventionné\nPansement | conventionné\nInjection | conventionné\nSoins à domicile | 7j/7",
  horaires: "Cabinet : lundi - samedi 7h - 8h30\nDomicile : 7j/7 sur rendez-vous", adresse: "18 avenue Pasteur, 33600 Pessac"
}, { menuServices: "Soins", titreServices: "Soins proposés", voirServices: "Voir les soins", boutonAppel: "Prendre RDV" }, "infirmiere soins domicile");
ajouter("psychologue", "Psychologue / Thérapeute", "🧠", "Santé", {
  nom: "Claire Martin, Psychologue", slogan: "Consultations pour adultes, adolescents et couples.",
  description: "Un espace d'écoute bienveillant pour traverser une période difficile : stress, anxiété, deuil, difficultés relationnelles. Consultations au cabinet ou en visio.",
  services: "Consultation individuelle | 60 €\nConsultation adolescent | 55 €\nThérapie de couple | 80 €\nConsultation en visio | 60 €",
  horaires: "Lundi - Vendredi : 9h - 20h (sur rendez-vous)\nSamedi : 9h - 13h", adresse: "11 rue Paul Painlevé, 33600 Pessac"
}, { menuServices: "Consultations", titreServices: "Consultations", voirServices: "Voir les tarifs", boutonAppel: "Prendre RDV" }, "therapie psy therapeute");
ajouter("orthophoniste", "Orthophoniste", "🗣️", "Santé", {
  nom: "Cabinet d'Orthophonie", slogan: "Bilans et rééducation du langage, enfants et adultes.",
  description: "Bilans et rééducation des troubles du langage oral et écrit, de la voix, de la déglutition et de la communication, sur prescription médicale.",
  services: "Bilan orthophonique | conventionné\nSéance de rééducation | conventionné\nPrise en charge | sécurité sociale",
  horaires: "Lundi - Vendredi : 8h30 - 19h (sur rendez-vous)", adresse: "7 rue Léon Morin, 33600 Pessac"
}, { menuServices: "Soins", titreServices: "Soins proposés", voirServices: "Voir les soins", boutonAppel: "Prendre RDV" }, "langage dyslexie");
ajouter("podologue", "Pédicure-podologue", "🦶", "Santé", {
  nom: "Cabinet de Podologie", slogan: "Soins des pieds et semelles orthopédiques.",
  description: "Soins de pédicurie, examen de la marche et fabrication de semelles orthopédiques sur mesure pour adultes, enfants et sportifs.",
  services: "Soin de pédicurie | 35 €\nBilan podologique | 40 €\nSemelles orthopédiques | à partir de 140 €\nSoin à domicile | 45 €",
  horaires: "Lundi - Vendredi : 9h - 19h\nSamedi : 9h - 12h", adresse: "22 avenue de Magonty, 33600 Pessac"
}, RDV, "pieds semelles pedicure");
ajouter("dieteticien", "Diététicien / Nutritionniste", "🥗", "Santé", {
  nom: "Léa Bernard, Diététicienne", slogan: "Rééquilibrage alimentaire et accompagnement personnalisé.",
  description: "Perte de poids, alimentation du sportif, troubles digestifs ou simple envie de mieux manger : un accompagnement bienveillant, sans régime frustrant.",
  services: "Première consultation (1h) | 55 €\nConsultation de suivi | 40 €\nForfait 5 séances | 190 €\nConsultation en visio | 40 €",
  horaires: "Lundi - Vendredi : 9h - 19h (sur rendez-vous)", adresse: "11 rue Paul Painlevé, 33600 Pessac"
}, { menuServices: "Consultations", titreServices: "Consultations", voirServices: "Voir les tarifs", boutonAppel: "Prendre RDV" }, "nutrition alimentation");
ajouter("sage-femme", "Sage-femme", "🤰", "Santé", {
  nom: "Sophie Dubois, Sage-femme", slogan: "Suivi de grossesse, préparation à la naissance et rééducation.",
  description: "Accompagnement de la grossesse, préparation à la naissance, suivi à domicile après l'accouchement, rééducation du périnée et suivi gynécologique.",
  services: "Consultation de grossesse | conventionné\nPréparation à la naissance | conventionné\nRééducation du périnée | conventionné\nVisite à domicile | conventionné",
  horaires: "Lundi - Vendredi : 9h - 19h (sur rendez-vous)", adresse: "5 rue Léon Morin, 33600 Pessac"
}, { menuServices: "Consultations", titreServices: "Consultations", voirServices: "Voir les consultations", boutonAppel: "Prendre RDV" }, "grossesse naissance");
ajouter("naturopathe", "Naturopathe / Médecines douces", "🌱", "Santé", {
  nom: "Émilie, Naturopathe", slogan: "Bien-être au naturel : alimentation, plantes, gestion du stress.",
  description: "Un accompagnement global pour retrouver de l'énergie, mieux dormir et gérer son stress, grâce à l'alimentation, aux plantes et à l'hygiène de vie.",
  services: "Bilan de vitalité (1h30) | 70 €\nConsultation de suivi | 50 €\nAtelier collectif | 25 €\nConsultation en visio | 50 €",
  horaires: "Mardi - Samedi : 9h - 19h (sur rendez-vous)", adresse: "Pessac (33)"
}, { menuServices: "Consultations", titreServices: "Consultations", voirServices: "Voir les tarifs", boutonAppel: "Prendre RDV" }, "reflexologie hypnose medecine douce");

// ---------- Sport & loisirs ----------
ajouter("arts-martiaux", "Arts martiaux / Boxe", "🥋", "Sport & loisirs", {
  nom: "Dojo Pessacais", slogan: "Judo, karaté et boxe pour enfants et adultes.",
  description: "Un club familial pour apprendre le respect, la confiance en soi et se dépenser. Cours adaptés à chaque âge et chaque niveau, encadrés par des professeurs diplômés.",
  services: "Cours d'essai | offert\nCotisation enfant (annuelle) | 180 €\nCotisation adulte (annuelle) | 240 €\nStage vacances (5 jours) | 90 €",
  horaires: "Lundi - Vendredi : 17h - 21h30\nMercredi : 14h - 21h30\nSamedi : 9h - 12h", adresse: "Salle omnisports, 33600 Pessac"
}, { menuServices: "Cours", titreServices: "Cours & tarifs", voirServices: "Voir les cours", boutonAppel: "Cours d'essai" }, "judo karate boxe mma");
ajouter("club-sport", "Club sportif / Association", "⚽", "Sport & loisirs", {
  nom: "AS Pessac Football", slogan: "Le club de foot de tous les Pessacais, des U6 aux vétérans.",
  description: "Un club convivial qui forme les jeunes et accueille tous les niveaux. Entraînements encadrés par des éducateurs diplômés, matchs chaque week-end.",
  services: "Licence école de foot | 120 €\nLicence jeunes | 150 €\nLicence seniors | 180 €\nStage vacances | 80 €",
  horaires: "Entraînements : lundi - vendredi 17h30 - 21h\nMatchs : samedi et dimanche", adresse: "Stade municipal, 33600 Pessac"
}, { menuServices: "Inscriptions", titreServices: "Inscriptions", voirServices: "S'inscrire", boutonAppel: "Nous appeler" }, "football foot rugby basket tennis association");
ajouter("escape-game", "Escape game / Loisirs", "🔐", "Sport & loisirs", {
  nom: "L'Énigme", slogan: "60 minutes pour vous échapper. Oserez-vous ?",
  description: "Trois salles immersives pour jouer en famille, entre amis ou entre collègues. Énigmes, décors et effets spéciaux : sensations garanties !",
  services: "2 joueurs | 30 € / pers.\n3-4 joueurs | 25 € / pers.\n5-6 joueurs | 22 € / pers.\nAnniversaire / entreprise | sur devis",
  horaires: "Lundi - Vendredi : 14h - 23h\nSamedi - Dimanche : 10h - 23h", adresse: "Zone commerciale, 33600 Pessac"
}, { menuServices: "Tarifs", titreServices: "Tarifs", voirServices: "Voir les tarifs", boutonAppel: "Réserver" }, "escape jeu enigme loisir");
ajouter("equitation", "Centre équestre", "🐴", "Sport & loisirs", {
  nom: "Les Écuries du Bourgailh", slogan: "Cours d'équitation, balades et pension pour chevaux.",
  description: "Cours de poney et d'équitation pour tous les âges, balades en forêt, stages pendant les vacances et pension pour chevaux dans un cadre verdoyant.",
  services: "Baptême poney | 15 €\nCours collectif (1h) | 25 €\nForfait annuel | 650 €\nBalade en forêt (1h) | 30 €\nPension cheval (mois) | à partir de 350 €",
  horaires: "Mardi - Dimanche : 9h - 19h\nLundi : fermé", adresse: "Forêt du Bourgailh, 33600 Pessac"
}, { menuServices: "Activités", titreServices: "Activités & tarifs", voirServices: "Voir les activités", boutonAppel: "Réserver" }, "cheval poney equitation");
ajouter("escalade", "Salle d'escalade / Trampoline", "🧗", "Sport & loisirs", {
  nom: "Bloc Session", slogan: "Escalade de bloc pour tous, dès 5 ans.",
  description: "Plus de 200 blocs renouvelés chaque semaine, un espace enfants, un coin café et une super ambiance. Location de chaussons sur place.",
  services: "Entrée adulte | 14 €\nEntrée enfant | 10 €\nCarte 10 entrées | 120 €\nAbonnement mensuel | 49 €\nLocation chaussons | 3 €",
  horaires: "Lundi - Vendredi : 12h - 23h\nSamedi - Dimanche : 9h - 20h", adresse: "Zone d'activités, 33600 Pessac"
}, { menuServices: "Tarifs", titreServices: "Tarifs", voirServices: "Voir les tarifs" }, "escalade bloc trampoline");
ajouter("surf", "École de surf / Sports nautiques", "🏄", "Sport & loisirs", {
  nom: "Océan Surf School", slogan: "Cours de surf et paddle sur la côte girondine.",
  description: "Apprenez à surfer en toute sécurité avec des moniteurs diplômés d'État. Cours pour débutants et confirmés, planches et combinaisons fournies.",
  services: "Cours découverte (2h) | 45 €\nStage 5 jours | 190 €\nCours particulier | 80 €\nLocation planche (demi-journée) | 20 €",
  horaires: "Avril - Octobre : tous les jours selon les marées", adresse: "Lacanau Océan (33)"
}, { menuServices: "Cours", titreServices: "Cours & tarifs", voirServices: "Voir les cours", boutonAppel: "Réserver" }, "surf paddle kitesurf plage");

// ---------- Événements ----------
ajouter("dj", "DJ / Animation musicale", "🎧", "Événements", {
  nom: "DJ Max Events", slogan: "Mariages, anniversaires et soirées d'entreprise.",
  description: "DJ professionnel, j'anime vos événements avec une musique adaptée à tous vos invités. Sono, éclairage et micro inclus, rendez-vous de préparation offert.",
  services: "Soirée anniversaire | à partir de 450 €\nMariage (formule complète) | à partir de 950 €\nSoirée d'entreprise | sur devis\nOption photobooth | 250 €",
  horaires: "Réponse sous 24 h, 7j/7", telephone: "06 00 00 00 00", adresse: "Toute la Gironde"
}, { menuServices: "Formules", titreServices: "Nos formules", voirServices: "Voir les formules" }, "dj musique soiree mariage sono");
ajouter("wedding-planner", "Organisatrice de mariage", "💒", "Événements", {
  nom: "Le Grand Jour", slogan: "Organisation et décoration de mariages sur mesure.",
  description: "De la recherche du lieu au jour J, je vous accompagne pour un mariage qui vous ressemble, sans stress. Coordination le jour même et décoration sur mesure.",
  services: "Coordination du jour J | à partir de 800 €\nOrganisation complète | sur devis\nDécoration de salle | sur devis\nPremier rendez-vous | offert",
  horaires: "Lundi - Samedi : sur rendez-vous", telephone: "06 00 00 00 00", adresse: "Bordeaux et Gironde"
}, { menuServices: "Formules", titreServices: "Nos formules", voirServices: "Voir les formules", boutonAppel: "Prendre RDV" }, "mariage wedding planner organisation evenement");
ajouter("location-salle", "Location de salle", "🏛️", "Événements", {
  nom: "Le Domaine des Pins", slogan: "Une salle de réception pour tous vos événements.",
  description: "Une grande salle lumineuse de 200 m² avec terrasse et parc, pour vos mariages, anniversaires, séminaires et repas de famille. Cuisine équipée et parking.",
  services: "Location demi-journée | 350 €\nLocation journée | 600 €\nWeek-end complet | 1 200 €\nMobilier et vaisselle | inclus\nVisite | gratuite",
  horaires: "Visites sur rendez-vous, 7j/7", adresse: "Chemin des Pins, 33600 Pessac"
}, { menuServices: "Tarifs", titreServices: "Tarifs", voirServices: "Voir les tarifs", boutonAppel: "Réserver" }, "salle reception fete seminaire");
ajouter("animateur", "Animateur / Anniversaires enfants", "🎈", "Événements", {
  nom: "Fête & Magie", slogan: "Anniversaires, magie et maquillage pour enfants.",
  description: "Des animations inoubliables pour les enfants : spectacles de magie, maquillage, sculpture de ballons et jeux. Je me déplace chez vous ou dans votre salle.",
  services: "Anniversaire 2h (jusqu'à 12 enfants) | 180 €\nSpectacle de magie (45 min) | 150 €\nMaquillage (par heure) | 60 €\nSculpture de ballons | 60 € / h",
  horaires: "Mercredi, samedi et dimanche : sur réservation", telephone: "06 00 00 00 00"
}, { menuServices: "Formules", titreServices: "Nos formules", voirServices: "Voir les formules", boutonAppel: "Réserver" }, "anniversaire magicien clown enfant");
ajouter("photobooth", "Location matériel de fête / Photobooth", "📸", "Événements", {
  nom: "Flash Box", slogan: "Photobooth, jeux et matériel pour vos fêtes.",
  description: "Louez notre borne photo avec impressions illimitées, accessoires et galerie en ligne, ainsi que tables, lumières et jeux géants pour réussir vos événements.",
  services: "Photobooth (soirée) | 290 €\nImpressions illimitées | incluses\nJeux géants en bois | 80 €\nGuirlandes lumineuses | 40 €\nLivraison et installation | selon distance",
  horaires: "Lundi - Samedi : 9h - 19h", telephone: "06 00 00 00 00"
}, { menuServices: "Locations", titreServices: "Nos locations", voirServices: "Voir les locations", boutonAppel: "Réserver" }, "location materiel borne photo fete");

// ---------- Animaux ----------
ajouter("veterinaire", "Vétérinaire", "🩺", "Animaux", {
  nom: "Clinique Vétérinaire des Pins", slogan: "Soins, vaccins et chirurgie pour vos compagnons.",
  description: "Une équipe de vétérinaires et d'assistantes à l'écoute pour chiens, chats et NAC : consultations, vaccins, chirurgie, radiologie et urgences.",
  services: "Consultation | 45 €\nVaccin chien / chat | à partir de 55 €\nStérilisation chat | à partir de 120 €\nDétartrage | sur devis\nUrgences | sur appel",
  horaires: "Lundi - Vendredi : 8h30 - 19h\nSamedi : 9h - 17h", adresse: "40 avenue de Magonty, 33600 Pessac"
}, { menuServices: "Soins", titreServices: "Soins & tarifs", voirServices: "Voir les soins", boutonAppel: "Prendre RDV" }, "veto clinique chien chat");
ajouter("educateur-canin", "Éducateur canin", "🐕", "Animaux", {
  nom: "Dog Coach 33", slogan: "Éducation canine positive, à domicile ou en groupe.",
  description: "Chiot turbulent, tirage en laisse, aboiements ? J'accompagne votre chien et vous avec des méthodes douces et efficaces, à domicile ou en cours collectifs.",
  services: "Bilan comportemental | 50 €\nSéance individuelle | 45 €\nForfait 5 séances | 200 €\nCours collectif (1h) | 15 €",
  horaires: "Lundi - Samedi : 9h - 19h (sur rendez-vous)", telephone: "06 00 00 00 00"
}, RDV, "chien dressage education");
ajouter("pension-animaux", "Pension / Garde d'animaux", "🏡", "Animaux", {
  nom: "La Pension des Copains", slogan: "Pension et garde de chiens et chats pendant vos absences.",
  description: "Pendant vos vacances, vos compagnons sont chouchoutés : grands parcs, promenades quotidiennes et photos envoyées chaque jour. Visites à domicile possibles.",
  services: "Pension chien (jour) | 20 €\nPension chat (jour) | 12 €\nVisite à domicile (30 min) | 15 €\nPromenade | 12 €",
  horaires: "Accueil : lundi - samedi 9h - 12h / 16h - 19h", telephone: "06 00 00 00 00"
}, { boutonAppel: "Réserver" }, "garde pet sitter chenil");

// ---------- Services ----------
ajouter("cordonnier", "Cordonnier / Clés", "👞", "Services", {
  nom: "Cordonnerie du Centre", slogan: "Réparation de chaussures, clés et plaques.",
  description: "Ressemelage, talons, réparation de sacs et de cuir, reproduction de clés et gravure de plaques, souvent pendant que vous attendez.",
  services: "Talons dame | 12 €\nRessemelage | à partir de 35 €\nDouble de clé | à partir de 5 €\nGravure de plaque | 15 €\nCirage | 5 €",
  horaires: "Mardi - Samedi : 9h - 12h30 / 14h30 - 19h", adresse: "13 avenue Jean Jaurès, 33600 Pessac"
}, null, "chaussures cles cuir");
ajouter("assistante-maternelle", "Assistante maternelle / Garde d'enfants", "👶", "Services", {
  nom: "Les P'tits Loups", slogan: "Assistante maternelle agréée, dans une maison chaleureuse.",
  description: "J'accueille vos enfants de 0 à 6 ans dans un cadre sécurisant et bienveillant, avec jardin et activités d'éveil. Agréée par le département, places disponibles.",
  services: "Accueil à la journée | selon contrat\nAccueil périscolaire | selon contrat\nAides CAF | possibles\nPremière rencontre | offerte",
  horaires: "Lundi - Vendredi : 7h30 - 18h30", telephone: "06 00 00 00 00"
}, { menuServices: "Accueil", titreServices: "Mon accueil", voirServices: "En savoir plus" }, "nounou creche baby-sitting enfant");
ajouter("aide-domicile", "Aide à domicile / Seniors", "🤝", "Services", {
  nom: "Présence Seniors", slogan: "Aide à domicile pour les personnes âgées et leurs familles.",
  description: "Courses, repas, ménage, aide à la toilette et compagnie : nos auxiliaires de vie accompagnent vos proches avec douceur. 50 % de crédit d'impôt.",
  services: "Aide à domicile | 26 € / h\nCourses accompagnées | 26 € / h\nGarde de nuit | sur devis\nÉvaluation à domicile | gratuite",
  horaires: "7j/7 : 7h - 21h", adresse: "Pessac et Bordeaux Métropole"
}, null, "senior personne agee auxiliaire de vie");
ajouter("graphiste", "Graphiste / Communication", "🎨", "Services", {
  nom: "Studio Pixel", slogan: "Logos, flyers et identité visuelle pour les entreprises.",
  description: "Je crée l'image de votre entreprise : logo, cartes de visite, flyers, affiches et visuels pour les réseaux sociaux. Un travail sur mesure, à l'écoute de vos idées.",
  services: "Création de logo | à partir de 250 €\nCartes de visite | à partir de 90 €\nFlyer / affiche | à partir de 120 €\nPack réseaux sociaux | sur devis",
  horaires: "Lundi - Vendredi : 9h - 18h", telephone: "06 00 00 00 00", adresse: "Pessac et à distance"
}, { menuServices: "Prestations", titreServices: "Prestations" }, "logo design communication");
ajouter("developpeur", "Développeur web / Création de sites", "💻", "Services", {
  nom: "Web Express", slogan: "Sites internet simples et efficaces pour les commerces.",
  description: "Je crée des sites vitrines modernes, rapides et adaptés aux téléphones, pour que vos clients vous trouvent sur Google. Paiement unique, sans abonnement.",
  services: "Site vitrine | à partir de 99 €\nNom de domaine (an) | environ 12 €\nModifications | sur devis\nFiche Google | offerte",
  horaires: "Lundi - Samedi : 9h - 19h", telephone: "06 00 00 00 00", adresse: "Pessac (33)"
}, { menuServices: "Offres", titreServices: "Mes offres", voirServices: "Voir les offres" }, "site internet web informatique");
ajouter("agence-voyage", "Agence de voyages", "✈️", "Services", {
  nom: "Horizons Voyages", slogan: "Voyages sur mesure, séjours et circuits.",
  description: "Nos conseillers organisent vos vacances, voyages de noces et séjours de groupe, avec un accompagnement avant, pendant et après le voyage.",
  services: "Devis personnalisé | gratuit\nSéjour tout compris | à partir de 590 €\nVoyage de noces | sur devis\nVoyage de groupe | sur devis",
  horaires: "Mardi - Samedi : 9h30 - 12h30 / 14h - 18h30", adresse: "17 avenue Pasteur, 33600 Pessac"
}, { menuServices: "Voyages", titreServices: "Nos voyages", voirServices: "Voir les voyages", boutonAppel: "Prendre RDV" }, "voyage vacances sejour");
ajouter("conciergerie", "Conciergerie / Location saisonnière", "🔑", "Services", {
  nom: "Clés en Main 33", slogan: "Gestion de votre location Airbnb de A à Z.",
  description: "Nous gérons votre logement en location courte durée : annonces, accueil des voyageurs, ménage, linge et petites réparations. Vous encaissez, on s'occupe du reste.",
  services: "Gestion complète | 20 % des revenus\nMénage entre voyageurs | à partir de 35 €\nLinge de maison | 15 € / séjour\nEstimation | gratuite",
  horaires: "7j/7 : 8h - 20h", adresse: "Bordeaux Métropole"
}, { menuServices: "Services", titreServices: "Nos services", voirServices: "Nos services" }, "airbnb location saisonniere gestion");
ajouter("avocat", "Avocat", "⚖️", "Services", {
  nom: "Maître Laurent, Avocate", slogan: "Droit de la famille, du travail et des contrats.",
  description: "Je vous conseille et vous défends avec rigueur et humanité : divorce, garde d'enfants, licenciement, litiges et contrats. Premier rendez-vous pour faire le point.",
  services: "Premier rendez-vous | 60 €\nDroit de la famille | sur devis\nDroit du travail | sur devis\nRédaction de contrats | sur devis",
  horaires: "Lundi - Vendredi : 9h - 19h (sur rendez-vous)", adresse: "28 avenue Jean Cordier, 33600 Pessac"
}, { menuServices: "Domaines", titreServices: "Domaines d'intervention", voirServices: "Voir les domaines", boutonAppel: "Prendre RDV" }, "juriste droit notaire");
ajouter("assurance", "Assurance / Courtier", "🛡️", "Services", {
  nom: "Cabinet Assur Plus", slogan: "Assurances auto, habitation, santé et professionnelles.",
  description: "Courtier indépendant, je compare pour vous les offres de nombreuses compagnies pour trouver la meilleure protection au meilleur prix.",
  services: "Étude personnalisée | gratuite\nAssurance auto | sur devis\nMultirisque habitation | sur devis\nMutuelle santé | sur devis\nAssurance pro | sur devis",
  horaires: "Lundi - Vendredi : 9h - 12h30 / 14h - 18h30", adresse: "24 avenue Pasteur, 33600 Pessac"
}, { menuServices: "Assurances", titreServices: "Nos assurances", voirServices: "Voir les assurances", boutonAppel: "Prendre RDV" }, "courtier mutuelle banque credit");
ajouter("coursier", "Coursier / Livraison", "📦", "Services", {
  nom: "Rapid'Course 33", slogan: "Livraison de colis et plis urgents dans la journée.",
  description: "Coursier indépendant pour les professionnels et les particuliers : plis urgents, colis, courses et livraisons programmées sur toute la métropole.",
  services: "Course express (métropole) | à partir de 15 €\nLivraison programmée | à partir de 10 €\nAbonnement entreprise | sur devis",
  horaires: "Lundi - Samedi : 7h - 20h", telephone: "06 00 00 00 00"
}, null, "livraison colis transport");
ajouter("formation", "Formateur / Consultant", "🎓", "Services", {
  nom: "Cap Compétences", slogan: "Formations et accompagnement pour les entreprises.",
  description: "Formations en management, bureautique et prise de parole, en présentiel ou à distance. Programmes adaptés à vos équipes, éligibles au financement.",
  services: "Formation d'une journée | à partir de 350 € / pers.\nFormation intra-entreprise | sur devis\nCoaching individuel | 90 € / h\nAudit | sur devis",
  horaires: "Lundi - Vendredi : 9h - 18h", adresse: "Pessac et à distance"
}, { menuServices: "Formations", titreServices: "Nos formations", voirServices: "Voir les formations", boutonAppel: "Nous contacter" }, "formation consultant coaching entreprise");
ajouter("pompes-funebres", "Pompes funèbres", "🕊️", "Services", {
  nom: "Pompes Funèbres de Pessac", slogan: "À vos côtés dans les moments difficiles, 24h/24.",
  description: "Organisation complète des obsèques, démarches administratives, contrats obsèques et marbrerie. Une équipe disponible et à l'écoute, jour et nuit.",
  services: "Organisation des obsèques | sur devis\nContrat obsèques | sur devis\nMarbrerie | sur devis\nPermanence | 24h/24",
  horaires: "Bureau : lundi - samedi 9h - 18h\nPermanence téléphonique : 24h/24", adresse: "Avenue du Cimetière, 33600 Pessac"
}, { menuServices: "Services", titreServices: "Nos services", voirServices: "Nos services" }, "obseques funeraire");

// Mots-clés en plus pour la recherche (on peut taper l'un de ces mots pour trouver le métier)
Object.entries({
  barbier: "coiffeur barber", beaute: "esthetique esthetitienne soins", coiffure: "coiffeur coiffeuse",
  tatouage: "tattoo piercing", massage: "spa sophrologie relaxation bien-etre", restaurant: "brasserie bistrot",
  pizzeria: "pizza italien", boulangerie: "patisserie pain", cafe: "salon de the coffee", traiteur: "chef cuisinier",
  foodtruck: "food truck street food", fleuriste: "fleurs", epicerie: "bio vrac", boucherie: "charcuterie viande",
  caviste: "vin cave biere", artisan: "plombier chauffagiste plomberie", electricien: "electricite",
  peintre: "peinture renovation platrier", paysagiste: "jardinier jardin espaces verts", menage: "nettoyage femme de menage",
  serrurier: "vitrier serrure", demenagement: "demenageur transport debarras", garage: "mecanicien mecanique voiture",
  autoecole: "permis conduite", taxi: "vtc chauffeur navette", kine: "kinesitherapeute kine reeducation",
  osteopathe: "osteo", coach: "sport fitness personal trainer", salle: "musculation gym fitness crossfit",
  danse: "yoga pilates", musique: "guitare piano chant", photographe: "photo video videaste",
  informatique: "telephone reparation smartphone ordinateur", cours: "prof professeur soutien scolaire",
  couture: "retouche pressing", immobilier: "agence immobiliere", comptable: "expert-comptable conseil",
  toilettage: "chien toiletteur"
}).forEach(([id, mots]) => { if (METIERS[id]) METIERS[id].mots = ((METIERS[id].mots || "") + " " + mots).trim(); });
