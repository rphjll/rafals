// ============================================================
//  LES 10 MODÈLES
//
//  Chaque modèle a sa propre MISE EN PAGE (en-tête, grand bandeau,
//  façon d'afficher les rubriques…). La mise en page elle-même est
//  dessinée dans generateur.js.
//
//  Chaque modèle a 5 STYLES (sous-modèles) : des couleurs et une
//  écriture pensées pour aller avec lui.
//
//  Un style :
//    couleur : la couleur principale (boutons, prix, décorations)
//    fond    : la couleur du fond de page
//    surface : la 2e couleur de fond (cartes, rubriques une sur deux)
//    encre   : la couleur du texte
//    doux    : la couleur des petits textes
//    ecriture: le style d'écriture (voir ECRITURES dans generateur.js)
//
//  exemple : le métier dont on prend les textes pour l'aperçu
// ============================================================

const MODELES = {

  classique: {
    nom: "Classique", icone: "🏠", exemple: "garage",
    description: "Simple et efficace : un grand bandeau coloré puis les rubriques les unes sous les autres.",
    variantes: [
      { id: "atelier", nom: "Atelier", couleur: "#e4572e", fond: "#f4f5f7", surface: "#ffffff", encre: "#15191f", doux: "#5b6270", ecriture: "solide" },
      { id: "ocean",   nom: "Océan",   couleur: "#0e7490", fond: "#f0f7f9", surface: "#ffffff", encre: "#0c2a33", doux: "#4f6b74", ecriture: "douce" },
      { id: "foret",   nom: "Forêt",   couleur: "#2f6b3a", fond: "#f5f7f2", surface: "#ffffff", encre: "#1c2a1e", doux: "#5c6b5a", ecriture: "editorial" },
      { id: "nuit",    nom: "Nuit",    couleur: "#f59e0b", fond: "#111318", surface: "#1a1d24", encre: "#f3f4f6", doux: "#a4a9b3", ecriture: "grotesk" },
      { id: "rubis",   nom: "Rubis",   couleur: "#be123c", fond: "#ffffff", surface: "#fbf2f4", encre: "#1f1115", doux: "#6b5a5f", ecriture: "serif" }
    ]
  },

  elegance: {
    nom: "Élégance", icone: "✨", exemple: "beaute",
    description: "Raffiné et centré, avec de fines décorations. Parfait pour la beauté, le bien-être, le luxe.",
    variantes: [
      { id: "ivoire",   nom: "Ivoire",      couleur: "#b08d57", fond: "#fbf8f3", surface: "#ffffff", encre: "#2e2a25", doux: "#857b6f", ecriture: "luxe" },
      { id: "poudre",   nom: "Rose poudré", couleur: "#c07a8a", fond: "#fbf5f5", surface: "#ffffff", encre: "#3a2e2e", doux: "#86767a", ecriture: "luxe" },
      { id: "noiror",   nom: "Noir & or",   couleur: "#c9a227", fond: "#0f0f0f", surface: "#181818", encre: "#f2efe8", doux: "#a8a298", ecriture: "luxe" },
      { id: "sauge",    nom: "Sauge",       couleur: "#6f8f70", fond: "#f6f8f4", surface: "#ffffff", encre: "#2a332a", doux: "#6b776b", ecriture: "elegant" },
      { id: "bordeaux", nom: "Bordeaux",    couleur: "#7b1e3a", fond: "#faf6f3", surface: "#ffffff", encre: "#2b1b20", doux: "#7a6a6e", ecriture: "serif" }
    ]
  },

  duo: {
    nom: "Duo", icone: "🌓", exemple: "coach",
    description: "Écran partagé en deux : le texte d'un côté, un grand visuel de l'autre. Moderne et dynamique.",
    variantes: [
      { id: "energie",    nom: "Énergie",    couleur: "#ef4444", fond: "#ffffff", surface: "#f5f5f5", encre: "#111111", doux: "#555555", ecriture: "condense" },
      { id: "electrique", nom: "Électrique", couleur: "#6366f1", fond: "#f7f7fb", surface: "#ffffff", encre: "#14142b", doux: "#5b5b76", ecriture: "grotesk" },
      { id: "menthe",     nom: "Menthe",     couleur: "#0f9f73", fond: "#f3faf7", surface: "#ffffff", encre: "#0f2a22", doux: "#52706a", ecriture: "douce" },
      { id: "charbon",    nom: "Charbon",    couleur: "#facc15", fond: "#141414", surface: "#1e1e1e", encre: "#f5f5f5", doux: "#a3a3a3", ecriture: "condense" },
      { id: "terracotta", nom: "Terracotta", couleur: "#c2410c", fond: "#fbf6f1", surface: "#ffffff", encre: "#2a1a12", doux: "#7a6556", ecriture: "editorial" }
    ]
  },

  magazine: {
    nom: "Magazine", icone: "📰", exemple: "photographe",
    description: "Comme un magazine : très grands titres, rubriques numérotées, beaucoup de caractère.",
    variantes: [
      { id: "papier", nom: "Papier", couleur: "#d4402b", fond: "#f6f1ea", surface: "#fffdf9", encre: "#1a1714", doux: "#6d655c", ecriture: "editorial" },
      { id: "encre",  nom: "Encre",  couleur: "#111111", fond: "#ffffff", surface: "#f4f4f4", encre: "#111111", doux: "#666666", ecriture: "serif" },
      { id: "nuit",   nom: "Nuit",   couleur: "#e8c07d", fond: "#121212", surface: "#1b1b1b", encre: "#f1ede6", doux: "#9e978d", ecriture: "editorial" },
      { id: "olive",  nom: "Olive",  couleur: "#6b7a2a", fond: "#f4f3ea", surface: "#ffffff", encre: "#22241a", doux: "#6a6b5c", ecriture: "classique" },
      { id: "cobalt", nom: "Cobalt", couleur: "#1d4ed8", fond: "#f5f7fb", surface: "#ffffff", encre: "#0b1530", doux: "#56607a", ecriture: "geometrique" }
    ]
  },

  cartes: {
    nom: "Cartes", icone: "🧁", exemple: "boulangerie",
    description: "Doux et chaleureux : chaque rubrique est posée comme une carte arrondie. Très convivial.",
    variantes: [
      { id: "dore",      nom: "Pain doré", couleur: "#c68a3a", fond: "#f3eadc", surface: "#fffaf2", encre: "#2b1d14", doux: "#7a6556", ecriture: "arrondi" },
      { id: "lavande",   nom: "Lavande",   couleur: "#7c6fd6", fond: "#edecfa", surface: "#ffffff", encre: "#1f1b3a", doux: "#625e80", ecriture: "arrondi" },
      { id: "pistache",  nom: "Pistache",  couleur: "#5f9e4a", fond: "#e9f2e4", surface: "#ffffff", encre: "#1c2a18", doux: "#5c6b56", ecriture: "douce" },
      { id: "corail",    nom: "Corail",    couleur: "#f0634f", fond: "#fbeae6", surface: "#ffffff", encre: "#2d1612", doux: "#7c5f58", ecriture: "arrondi" },
      { id: "ardoise",   nom: "Ardoise",   couleur: "#38bdf8", fond: "#161d28", surface: "#212b3a", encre: "#eef2f7", doux: "#9fb0c4", ecriture: "douce" }
    ]
  },

  minimal: {
    nom: "Minimal", icone: "◻️", exemple: "comptable",
    description: "Épuré au maximum : beaucoup d'espace, de fines lignes, zéro superflu. Chic et sérieux.",
    variantes: [
      { id: "blanc",     nom: "Blanc pur",  couleur: "#111111", fond: "#ffffff", surface: "#fafafa", encre: "#111111", doux: "#6b6b6b", ecriture: "moderne" },
      { id: "sable",     nom: "Sable",      couleur: "#9a7b4f", fond: "#f7f4ef", surface: "#ffffff", encre: "#1f1b16", doux: "#77706a", ecriture: "moderne" },
      { id: "bleunuit",  nom: "Bleu nuit",  couleur: "#1e3a5f", fond: "#ffffff", surface: "#f6f8fb", encre: "#0f1a2a", doux: "#5d6a7c", ecriture: "grotesk" },
      { id: "graphite",  nom: "Graphite",   couleur: "#e5e5e5", fond: "#161616", surface: "#1f1f1f", encre: "#ededed", doux: "#9a9a9a", ecriture: "moderne" },
      { id: "sapin",     nom: "Vert sapin", couleur: "#14532d", fond: "#fbfbf8", surface: "#ffffff", encre: "#13201a", doux: "#66706a", ecriture: "editorial" }
    ]
  },

  impact: {
    nom: "Impact", icone: "⚡", exemple: "salle",
    description: "Puissant et percutant : énormes titres, grands blocs de couleur. Idéal sport, fête, street food.",
    variantes: [
      { id: "rouge",   nom: "Rouge vif",   couleur: "#ef233c", fond: "#0b0b0d", surface: "#16161a", encre: "#ffffff", doux: "#b3b3b8", ecriture: "impact" },
      { id: "jaune",   nom: "Jaune choc",  couleur: "#ffd60a", fond: "#111111", surface: "#1c1c1c", encre: "#ffffff", doux: "#b0b0b0", ecriture: "impact" },
      { id: "bleu",    nom: "Électrique",  couleur: "#3a86ff", fond: "#0a0f1f", surface: "#111a33", encre: "#ffffff", doux: "#aab4cc", ecriture: "condense" },
      { id: "neon",    nom: "Néon",        couleur: "#22c55e", fond: "#0b0f0c", surface: "#141a16", encre: "#f2fff6", doux: "#a6b5aa", ecriture: "impact" },
      { id: "orange",  nom: "Orange soleil", couleur: "#ff6b1a", fond: "#fff7f0", surface: "#ffffff", encre: "#1a0f08", doux: "#6b574a", ecriture: "impact" }
    ]
  },

  galerie: {
    nom: "Galerie photo", icone: "🖼️", exemple: "fleuriste",
    description: "Les photos d'abord : une mosaïque en haut de page et une grande galerie. Pour montrer son travail.",
    variantes: [
      { id: "petale",  nom: "Pétale",      couleur: "#d9678a", fond: "#ffffff", surface: "#fbf3f6", encre: "#2d1d24", doux: "#7c6670", ecriture: "luxe" },
      { id: "studio",  nom: "Studio noir", couleur: "#e7e5e4", fond: "#0c0c0c", surface: "#161616", encre: "#f5f5f5", doux: "#a3a3a3", ecriture: "geometrique" },
      { id: "nature",  nom: "Nature",      couleur: "#3f7d3a", fond: "#f5f8f2", surface: "#ffffff", encre: "#1f2d1f", doux: "#5c6b5a", ecriture: "editorial" },
      { id: "sable",   nom: "Sable chaud", couleur: "#b4793f", fond: "#faf5ee", surface: "#ffffff", encre: "#2a1f16", doux: "#7a6a5a", ecriture: "serif" },
      { id: "azur",    nom: "Azur",        couleur: "#0284c7", fond: "#f5fafd", surface: "#ffffff", encre: "#0b2233", doux: "#557082", ecriture: "douce" }
    ]
  },

  menu: {
    nom: "Carte & menu", icone: "🍽️", exemple: "restaurant",
    description: "Comme une belle carte de restaurant : titres décorés, prix alignés avec des pointillés.",
    variantes: [
      { id: "bistrot",    nom: "Bistrot",    couleur: "#b5452f", fond: "#fdf8f1", surface: "#fffdf9", encre: "#2b1d14", doux: "#7a6556", ecriture: "elegant" },
      { id: "ardoise",    nom: "Ardoise",    couleur: "#d4a373", fond: "#1f2421", surface: "#283029", encre: "#f4efe6", doux: "#b5ad9f", ecriture: "elegant" },
      { id: "trattoria",  nom: "Trattoria",  couleur: "#2e7d32", fond: "#fbf7ee", surface: "#fffdf8", encre: "#2a2116", doux: "#756a5a", ecriture: "classique" },
      { id: "brasserie",  nom: "Brasserie",  couleur: "#c9a227", fond: "#14213d", surface: "#1b2a4a", encre: "#f5efe0", doux: "#b7b2a3", ecriture: "luxe" },
      { id: "guinguette", nom: "Guinguette", couleur: "#e76f51", fond: "#fff8ec", surface: "#fffdf8", encre: "#2d2016", doux: "#7c6a58", ecriture: "manuscrit" }
    ]
  },

  pro: {
    nom: "Pro", icone: "💼", exemple: "artisan",
    description: "Sérieux et rassurant : bandeau d'infos en haut, carte de contact visible tout de suite. Pour artisans et pros.",
    variantes: [
      { id: "confiance", nom: "Confiance", couleur: "#2563eb", fond: "#ffffff", surface: "#f3f6fb", encre: "#0f172a", doux: "#526075", ecriture: "douce" },
      { id: "chantier",  nom: "Chantier",  couleur: "#f59e0b", fond: "#ffffff", surface: "#f6f5f2", encre: "#1c1917", doux: "#57534e", ecriture: "solide" },
      { id: "sante",     nom: "Santé",     couleur: "#0d9488", fond: "#f7fbfb", surface: "#ffffff", encre: "#0f2d2b", doux: "#537370", ecriture: "douce" },
      { id: "marine",    nom: "Marine",    couleur: "#1e3a5f", fond: "#f6f8fb", surface: "#ffffff", encre: "#0f1a2a", doux: "#56637a", ecriture: "grotesk" },
      { id: "rouge",     nom: "Rouge",     couleur: "#dc2626", fond: "#ffffff", surface: "#f7f4f4", encre: "#1a1010", doux: "#5e5252", ecriture: "solide" }
    ]
  }
};
