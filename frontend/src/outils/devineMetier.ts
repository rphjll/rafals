// Trouver le métier d'une demande à partir de ce que le client écrit (« Publier une demande », grande maquette ; niveau 12
// remplacera cette liste par une petite IA). Chaque métier a ses mots ; le métier qui en a le plus dans le texte gagne.
// Un mot trop général (« réparer », « installer »…) compte pour moitié.
// Ex. « Fuite sous l'évier de la cuisine » → plombier (fuite + evier) ; « Réparer mon PC » → depannage-informatique.
// Les mots sont écrits sans accents ; « electri » trouve aussi « électricité », « électrique ».

const MOTS: [code: string, mots: string[]][] = [
  ['massage', ['masser', 'massage', 'masse', 'dos bloque', 'detente', 'relaxation']],
  ['plombier', ['fuite', 'evier', 'robinet', 'wc', 'toilette', 'chasse d eau', 'tuyau', 'canalisation', 'douche', 'chauffe-eau', 'chauffe eau', 'lavabo', 'bouche', 'plomb']],
  ['electricien', ['prise', 'electri', 'lumiere', 'disjonct', 'interrupteur', 'spot', 'lampe', 'courant', 'tableau electrique', 'ampoule']],
  ['jardinier', ['jardin', 'pelouse', 'tondre', 'tonte', 'herbe', 'potager', 'arbre']],
  ['taille-haies', ['haie', 'tailler', 'thuya']],
  ['menage', ['menage', 'nettoy', 'aspirat', 'poussiere', 'laver']],
  ['vitres', ['vitres', 'carreaux sales']],
  ['repassage', ['repass', 'linge']],
  ['peintre', ['peindre', 'peinture', 'repeindre', 'mur', 'plafond', 'tapisserie']],
  ['soutien-scolaire', ['cours', 'maths', 'devoirs', 'soutien scolaire', 'reviser', 'francais', 'physique']],
  ['cours-langues', ['anglais', 'espagnol', 'allemand', 'langue']],
  ['serrurier', ['serrure', 'cle', 'clef', 'porte claquee', 'verrou', 'enferme']],
  ['pet-sitter', ['chat', 'animal', 'animaux', 'garder mon chien']],
  ['promeneur-chiens', ['promener', 'promenade', 'chien']],
  ['montage-meubles', ['monter', 'meuble', 'etagere', 'armoire', 'ikea']],
  ['multiservices', ['fixer', 'bricol', 'accrocher', 'repar', 'installer', 'percer', 'tringle', 'cadre']],
  ['chauffagiste', ['chaudiere', 'chauffage', 'radiateur']],
  ['coiffure', ['coiff', 'cheveux', 'coupe de cheveux', 'brushing', 'tresse']],
  ['barbier', ['barbe']],
  ['depannage-informatique', ['pc', 'ordi', 'ordinateur', 'informatique', 'imprimante', 'wifi', 'box', 'internet', 'virus', 'windows', 'mac', 'portable', 'tablette', 'logiciel', 'mot de passe', 'ecran', 'souris', 'clavier', 'imprimer']],
  ['reparation-telephone', ['telephone', 'smartphone', 'iphone', 'ecran casse']],
  ['demenageur', ['demenag', 'carton', 'camion', 'porter', 'transporter']],
  ['garde-enfants', ['enfant', 'bebe', 'nounou', 'baby', 'sortie d ecole', 'garder ma fille', 'garder mon fils']],
  ['aide-domicile', ['personne agee', 'grand-mere', 'grand-pere', 'aide a domicile', 'repas a domicile']],
  ['courses', ['courses']],
  ['estheticienne', ['epil', 'soin du visage', 'sourcil']],
  ['onglerie', ['ongle', 'manucure', 'vernis']],
  ['maquillage', ['maquill']],
  ['mecanicien', ['voiture', 'auto', 'moteur', 'pneu', 'vidange', 'frein', 'batterie', 'garage']],
  ['moto', ['scooter', 'moto']],
  ['velo', ['velo', 'crevaison', 'chaine de velo', 'derailleur']],
  ['retouches', ['couture', 'ourlet', 'recoudre', 'retouche', 'fermeture eclair', 'pantalon', 'robe']],
  ['photographe', ['photo', 'photographe', 'shooting']],
  ['traiteur', ['traiteur', 'repas pour', 'buffet']],
  ['patissier-evenements', ['gateau', 'anniversaire']],
  ['vitrier', ['vitre cassee', 'carreau', 'fenetre cassee', 'double vitrage']],
  ['couvreur', ['toit', 'toiture', 'tuile', 'gouttiere', 'ardoise']],
  ['macon', ['macon', 'beton', 'muret', 'dalle', 'parpaing', 'fissure']],
  ['carreleur', ['carrel', 'faience']],
  ['menuisier', ['menuis', 'placard', 'porte qui ferme mal', 'bois']],
  ['poseur-sols', ['parquet', 'sol', 'lino', 'moquette']],
  ['climatisation', ['clim', 'climatis', 'pompe a chaleur']],
  ['coach-sportif', ['sport', 'muscu', 'courir', 'maigrir', 'perdre du poids', 'fitness', 'coach']],
  ['cours-musique', ['piano', 'guitare', 'violon', 'chant', 'solfege']],
  ['nettoyage-textiles', ['canape', 'tapis']],
  ['reparation-electromenager', ['lave-linge', 'lave linge', 'lave-vaisselle', 'frigo', 'refrigerateur', 'four', 'seche-linge']],
]
const MOTS_VAGUES = new Set(['repar', 'cours', 'installer', 'monter', 'fixer', 'porter', 'laver', 'courses', 'chien'])

const sansAccent = (t: string) => t.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9-]+/g, ' ')

/** Le code du métier deviné (ex. « plombier »), ou null si aucun mot n'est reconnu */
export function devinerMetier(texte: string): string | null {
  const t = ` ${sansAccent(texte)} `
  let meilleur: string | null = null
  let score = 0
  for (const [code, mots] of MOTS) {
    const n = mots.filter((m) => t.includes(` ${m}`)).reduce((total, m) => total + (MOTS_VAGUES.has(m) ? 0.5 : 1), 0)
    if (n > score) {
      score = n
      meilleur = code
    }
  }
  return meilleur
}
