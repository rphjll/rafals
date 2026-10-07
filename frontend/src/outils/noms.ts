// Les initiales montrées dans un rond quand il n'y a pas de photo.

/** « Karim Benali » → « KB », « Marie D. » → « MD » (le marqueur des données de test « ZZTEST » est ignoré) */
export function initialesDe(nom: string): string {
  return nom
    .replace(/^ZZTEST\s+/, '')
    .split(/\s+/)
    .slice(0, 2)
    .map((mot) => mot[0]?.toUpperCase() ?? '')
    .join('')
}
