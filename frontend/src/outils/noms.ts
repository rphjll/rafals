// Les initiales et la couleur du rond d'une personne sans photo.

/** « Karim Benali » → « KB », « Marie D. » → « MD » (le marqueur des données de test « ZZTEST » est ignoré) */
export function initialesDe(nom: string): string {
  return nom
    .replace(/^ZZTEST\s+/, '')
    .split(/\s+/)
    .slice(0, 2)
    .map((mot) => mot[0]?.toUpperCase() ?? '')
    .join('')
}

/** Couleur pleine du rond d'une personne (grande maquette) : une des 10 couleurs --av1 à --av10 de style.css,
 * toujours la même pour un même nom (ex. « Julie M. » : toujours la même couleur, partout) */
export function couleurDe(nom: string): string {
  let somme = 0
  for (const lettre of nom.replace(/^ZZTEST\s+/, '')) somme = (somme * 31 + lettre.charCodeAt(0)) % 997
  return `var(--av${(somme % 10) + 1})`
}
