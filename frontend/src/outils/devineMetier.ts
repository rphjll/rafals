// Trouver le métier d'une demande à partir de ce que le client écrit (« Publier une demande », grande maquette ; niveau 12
// remplacera cette liste par une petite IA). Chaque métier a ses mots ; le métier qui en a le plus dans le texte gagne.
// Un mot trop général (« réparer », « installer »…) compte pour moitié.
// Ex. « Fuite sous l'évier de la cuisine » → plombier (fuite + evier) ; « Réparer mon PC » → depannage-informatique.
//
// Revu après l'audit du 14/11/2026 (« Faire mes courses » donnait Soutien scolaire, « Cours de boxe » Dépannage
// informatique) :
// - un mot doit être ENTIER dans le texte (au pluriel près) : « mac » ne trouve plus « machine », « cours » plus « courses » ;
// - un début de mot s'écrit avec une étoile : « electri* » trouve « électricité », « électrique » ;
// - deux métiers à égalité : on ne devine pas, le client choisit (mieux vaut « pas reconnu » qu'un mauvais métier).
// Les mots sont écrits sans accents.

const MOTS: [code: string, mots: string[]][] = [
  ['massage', ['masser', 'massage', 'dos bloque', 'detente', 'relaxation']],
  ['plombier', ['fuite', 'fuit', 'evier', 'robinet', 'wc', 'chasse d eau', 'tuyau', 'canalisation', 'douche', 'chauffe-eau', 'chauffe eau', 'lavabo', 'bouche', 'debouch*', 'plomb*', 'siphon']],
  ['electricien', ['prise electrique', 'changer une prise', 'installer une prise', 'electri*', 'lumiere', 'disjonct*', 'interrupteur', 'spot', 'lampe', 'courant', 'tableau electrique', 'ampoule']],
  ['jardinier', ['jardin', 'pelouse', 'tondre ma pelouse', 'tondre la pelouse', 'tondre le gazon', 'tondre mon jardin', 'tonte', 'herbe', 'potager', 'gazon', 'desherb*']],
  ['taille-haies', ['haie', 'thuya']],
  ['elagueur', ['abattre', 'abattage', 'elag*', 'dessouch*', 'couper un arbre', 'arbre']],
  ['menage', ['menage', 'aspirateur', 'poussiere', 'nettoyer ma maison', 'nettoyer mon appartement', 'nettoyer mes toilettes', 'nettoyer la salle de bain', 'femme de menage']],
  ['vitres', ['vitres', 'carreaux sales', 'laver les vitres', 'nettoyer les vitres']],
  ['repassage', ['repass*', 'linge']],
  ['peintre', ['peindre', 'peinture', 'repeindre', 'plafond', 'tapisserie', 'papier peint']],
  ['soutien-scolaire', ['cours de maths', 'cours de francais', 'cours de physique', 'cours particuliers', 'maths', 'soutien scolaire', 'reviser', 'bac', 'brevet']],
  ['aide-devoirs', ['devoirs', 'aide aux devoirs']],
  ['cours-langues', ['cours d anglais', 'cours d espagnol', 'cours d allemand', 'cours de langue', 'apprendre l anglais']],
  ['traducteur', ['traduire', 'traduction', 'traducteur']],
  ['cours-musique', ['piano', 'guitare', 'violon', 'chant', 'solfege', 'cours de batterie', 'cours de musique']],
  ['cours-informatique', ['cours d informatique', 'apprendre l informatique', 'apprendre a utiliser']],
  ['cours-cuisine', ['cours de cuisine', 'cours de patisserie', 'apprendre a cuisiner']],
  ['yoga', ['yoga', 'pilates']],
  ['natation', ['natation', 'nager', 'aquagym']],
  ['arts-martiaux', ['boxe', 'judo', 'karate', 'self defense', 'krav maga']],
  ['danse', ['danse', 'salsa']],
  ['coach-sportif', ['muscu*', 'courir', 'maigrir', 'perdre du poids', 'fitness', 'coach sportif', 'remise en forme']],
  ['serrurier', ['serrure', 'porte claquee', 'verrou', 'enferme dehors', 'cle cassee', 'perdu mes cles']],
  ['pet-sitter', ['garder mon chat', 'garder mon chien', 'garder mes chats', 'garde de chat', 'garder mon animal', 'garder mes animaux']],
  ['promeneur-chiens', ['promener mon chien', 'promener', 'promenade']],
  ['toiletteur', ['toilettage', 'toiletteur', 'tondre mon chien', 'laver mon chien']],
  ['montage-meubles', ['monter un meuble', 'monter une armoire', 'monter mon armoire', 'montage de meuble', 'meuble en kit', 'ikea', 'etagere']],
  ['multiservices', ['fixer', 'bricol*', 'accrocher', 'percer', 'tringle', 'cadre', 'petits travaux']],
  ['chauffagiste', ['chaudiere', 'chauffage', 'radiateur']],
  ['coiffure', ['coiff*', 'cheveux', 'brushing', 'tresse']],
  ['barbier', ['barbe']],
  ['depannage-informatique', ['pc', 'ordi', 'ordinateur', 'imprimante', 'wifi', 'box internet', 'ma box', 'virus', 'windows', 'macbook', 'logiciel', 'clavier', 'imprimer']],
  ['reparation-telephone', ['telephone', 'smartphone', 'iphone', 'ecran casse']],
  ['developpeur-web', ['site internet', 'site web', 'creer mon site']],
  ['demenageur', ['demenag*', 'cartons', 'camion']],
  ['debarras', ['debarras*', 'vider ma cave', 'vider mon grenier', 'vider la maison', 'encombrants']],
  ['garde-enfants', ['garder mon enfant', 'garder mes enfants', 'garder ma fille', 'garder mon fils', 'nounou', 'baby-sitting', 'baby sitting', 'babysitting', 'baby-sitter', 'sortie d ecole', 'bebe']],
  ['animateur-enfants', ['anniversaire de mon fils', 'anniversaire de ma fille', 'anniversaire de mon enfant', 'animer l anniversaire', 'animation enfants', 'clown']],
  ['magicien', ['magicien', 'magie']],
  ['aide-domicile', ['personne agee', 'grand-mere', 'grand-pere', 'aide a domicile', 'repas a domicile']],
  ['courses', ['faire mes courses', 'faire les courses', 'courses au supermarche']],
  ['infirmier', ['prise de sang', 'infirmier', 'infirmiere', 'pansement', 'piqure']],
  ['estheticienne', ['epil*', 'soin du visage', 'sourcil']],
  ['onglerie', ['ongle', 'manucure', 'vernis']],
  ['maquillage', ['maquill*']],
  ['mecanicien', ['moteur', 'pneu', 'vidange de ma voiture', 'frein', 'batterie de ma voiture', 'ma voiture ne demarre', 'reparer ma voiture', 'garagiste', 'embrayage']],
  ['lavage-auto', ['laver ma voiture', 'nettoyer ma voiture', 'nettoyer l interieur de ma voiture', 'lavage de voiture', 'lavage auto']],
  ['moto', ['scooter', 'moto']],
  ['velo', ['velo', 'crevaison', 'derailleur']],
  ['retouches', ['ourlet', 'recoudre', 'retouche', 'fermeture eclair']],
  ['photographe', ['photographe', 'shooting', 'photos de mariage', 'photos']],
  ['dj', ['dj', 'sono']],
  ['traiteur', ['traiteur', 'repas pour', 'buffet']],
  ['patissier-evenements', ['gateau', 'piece montee']],
  ['vitrier', ['vitre cassee', 'fenetre cassee', 'double vitrage', 'carreau casse']],
  ['couvreur', ['toit', 'toiture', 'tuile', 'gouttiere', 'ardoise']],
  ['macon', ['macon', 'beton', 'muret', 'dalle', 'parpaing', 'fissure']],
  ['carreleur', ['carrel*', 'faience']],
  ['menuisier', ['menuis*', 'placard sur mesure', 'porte qui ferme mal']],
  ['poseur-sols', ['parquet', 'lino', 'moquette']],
  ['cloture', ['portail', 'cloture', 'grillage']],
  ['climatisation', ['clim', 'climatis*', 'pompe a chaleur']],
  ['desinsectisation', ['fourmis', 'cafards', 'punaises de lit', 'rats', 'souris dans', 'guepes', 'frelons', 'nuisibles']],
  ['nettoyage-textiles', ['nettoyer mon canape', 'nettoyer mon tapis', 'nettoyage de canape', 'nettoyage de tapis', 'shampouin*']],
  ['reparation-electromenager', ['lave-linge', 'lave linge', 'machine a laver', 'lave-vaisselle', 'lave vaisselle', 'frigo', 'refrigerateur', 'four', 'seche-linge', 'seche linge']],
]
const MOTS_VAGUES = new Set(['fixer', 'photos', 'promener', 'promenade', 'bebe', 'arbre', 'four', 'bouche'])

const sansAccent = (t: string) => t.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9-]+/g, ' ')

/** Le mot est-il dans le texte ? Entier (au pluriel près), ou en début de mot s'il finit par une étoile. */
function contient(texte: string, mot: string): boolean {
  if (mot.endsWith('*')) return texte.includes(` ${mot.slice(0, -1)}`)
  return [` ${mot} `, ` ${mot}s `, ` ${mot}x `].some((forme) => texte.includes(forme))
}

/** Le code du métier deviné (ex. « plombier »), ou null si aucun mot n'est reconnu ou si deux métiers sont à égalité */
export function devinerMetier(texte: string): string | null {
  const t = ` ${sansAccent(texte).trim().replace(/\s+/g, ' ')} `
  let meilleur: string | null = null
  let score = 0
  let egalite = false
  for (const [code, mots] of MOTS) {
    const n = mots.filter((m) => contient(t, m)).reduce((total, m) => total + (MOTS_VAGUES.has(m) ? 0.5 : 1), 0)
    if (n > score) {
      score = n
      meilleur = code
      egalite = false
    } else if (n > 0 && n === score) {
      egalite = true
    }
  }
  return egalite ? null : meilleur
}
