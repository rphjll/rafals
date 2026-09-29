// Affichage des dates à la française, à l'heure de Paris (le serveur envoie de l'UTC).

const fuseau = 'Europe/Paris'

/** Ex. « 28/09/2026 » */
export function formaterDate(iso: string): string {
  // Une date seule (« 2010-05-04 ») n'a pas d'heure : on la lit telle quelle, sans fuseau
  if (/^\d{4}-\d{2}-\d{2}$/.test(iso)) {
    const [annee, mois, jour] = iso.split('-')
    return `${jour}/${mois}/${annee}`
  }
  return new Date(iso).toLocaleDateString('fr-FR', { timeZone: fuseau })
}

/** Ex. « 28/09/2026 à 18 h 40 » */
export function formaterDateHeure(iso: string): string {
  const moment = new Date(iso)
  const [heure, minute] = moment
    .toLocaleTimeString('fr-FR', { timeZone: fuseau, hour: '2-digit', minute: '2-digit' })
    .split(':')
  return `${formaterDate(iso)} à ${Number(heure)} h ${minute}`
}

/** Âge aujourd'hui pour une date de naissance « 2010-05-04 ». */
export function age(dateNaissance: string): number {
  const [annee, mois, jour] = dateNaissance.split('-').map(Number)
  const aujourdhui = new Date()
  const anniversairePasse =
    aujourdhui.getMonth() + 1 > mois || (aujourdhui.getMonth() + 1 === mois && aujourdhui.getDate() >= jour)
  return aujourdhui.getFullYear() - annee - (anniversairePasse ? 0 : 1)
}

/** Le jour d'aujourd'hui à Paris, au format d'un champ date : « 2026-09-29 ». */
export function aujourdhuiIso(): string {
  return new Date().toLocaleDateString('fr-CA', { timeZone: fuseau })
}
