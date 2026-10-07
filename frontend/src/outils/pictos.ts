// Pictogrammes au trait : dossiers de métiers (bulles de l'accueil, tuiles de « Trouver un prestataire »), entrées du
// menu, photo et envoi dans les messages. Un tracé par code, dessiné dans une case de 24 x 24. Code inconnu : la grille.

const GRILLE = 'M4 4h6.5v6.5H4zM13.5 4H20v6.5h-6.5zM4 13.5h6.5V20H4zM13.5 13.5H20V20h-6.5z'

const TRACES: Record<string, string> = {
  'maison-travaux': 'M15 4a5 5 0 00-5 7l-7 7 3 3 7-7a5 5 0 007-5l-3 3-3-3z',
  'menage-entretien': 'M12 3l2 6 6 2-6 2-2 6-2-6-6-2 6-2z',
  'jardin-exterieur': 'M5 19c0-9 5-14 15-14 0 10-5 15-14 15zM5 19l8-8',
  'beaute-bien-etre': 'M8.5 8L20 18M8.5 16L20 6M9 6a3 3 0 11-6 0 3 3 0 016 0zM9 18a3 3 0 11-6 0 3 3 0 016 0z',
  sante: 'M12 20s-7-4.5-7-10a4 4 0 017-2.5A4 4 0 0119 10c0 5.5-7 10-7 10z',
  'enfants-famille': 'M12 21a9 9 0 100-18 9 9 0 000 18zM8.5 14.5c1 1.5 2.2 2 3.5 2s2.5-.5 3.5-2M9 10h.01M15 10h.01',
  'cours-formation': 'M4 5.5c3-1 5.5-.5 8 1 2.5-1.5 5-2 8-1V19c-3-1-5.5-.5-8 1-2.5-1.5-5-2-8-1zM12 6.5V20',
  'sport-loisirs': 'M12 21a9 9 0 100-18 9 9 0 000 18zM3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18',
  evenements: 'M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z',
  animaux:
    'M12 20c-3 0-5-1.5-5-3.5S9.5 12 12 12s5 2.5 5 4.5S15 20 12 20zM6 10.5a1.5 2 0 100-4 1.5 2 0 000 4zM18 10.5a1.5 2 0 100-4 1.5 2 0 000 4zM9.5 7.5a1.5 2 0 100-4 1.5 2 0 000 4zM14.5 7.5a1.5 2 0 100-4 1.5 2 0 000 4z',
  'auto-transport': 'M4 16v-4l2-5h12l2 5v4zM4 12h16M7 16v2M17 16v2M7.5 14h.01M16.5 14h.01',
  'numerique-bureau': 'M4 5h16v11H4zM9 20h6M12 16v4',
  'services-personne': 'M12 11a4 4 0 100-8 4 4 0 000 8zM4 21c0-4 4-6 8-6s8 2 8 6',
  // Entrées du menu (barre du bas sur téléphone)
  'menu-accueil': 'M3 11l9-8 9 8M5 10v10h14V10',
  'menu-trouver': 'M11 18a7 7 0 100-14 7 7 0 000 14zM20 20l-3.5-3.5',
  'menu-reservations': 'M5 5h14a2 2 0 012 2v12a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2zM3 10h18M8 3v4M16 3v4',
  'menu-messages': 'M4 5h16v11H9l-5 4z',
  'menu-activite': 'M5 7h14a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9a2 2 0 012-2zM9 7V4h6v3',
  appareil: 'M5 7h14a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9a2 2 0 012-2zM12 17a3.5 3.5 0 100-7 3.5 3.5 0 000 7zM8 7l1.5-3h5L16 7',
  envoyer: 'M4 12l16-8-6 16-3-6z',
}

// Une couleur par dossier, dans l'ordre, puis on recommence (noms écrits en entier pour Tailwind)
const TEINTES = [
  'bg-teinte-orange text-teinte-orange-texte',
  'bg-teinte-vert text-teinte-vert-texte',
  'bg-teinte-jaune text-teinte-jaune-texte',
  'bg-teinte-bleu text-teinte-bleu-texte',
  'bg-teinte-rose text-teinte-rose-texte',
  'bg-teinte-violet text-teinte-violet-texte',
] as const

/** Le tracé du dossier « jardin-exterieur » ; code inconnu (ou « tout ») : la grille de 4 carrés */
export function tracePicto(code: string): string {
  return TRACES[code] ?? GRILLE
}

export function teinte(rang: number): string {
  return TEINTES[rang % TEINTES.length] ?? TEINTES[0]
}
