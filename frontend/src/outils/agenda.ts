// Agenda : types et calculs d'affichage (heures, jours, périodes bloquées), à un seul endroit (RM-AGENDA.md).
// Toutes les dates sont lues à l'heure de Paris.

export interface Plage {
  jour_semaine: number // 1 = lundi … 7 = dimanche
  debut: string // « 09:00:00 »
  fin: string
}

export interface Blocage {
  id: number
  debut: string // moment exact (UTC), ex. « 2026-10-19T22:00:00Z »
  fin: string
  motif: string | null
}

export interface ReglagesAgenda {
  pas_minutes: number
  pause_minutes: number
  delai_min_minutes: number
  delai_max_mois: number
}

export interface AgendaVisible {
  plages: Plage[]
  blocages: Blocage[]
  reglages: ReglagesAgenda
}

export const JOURS = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
export const MOIS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']

/** « 09:00:00 » ou « 09:00 » → « 9 h 00 » */
export function heure(texte: string): string {
  const [h, m] = texte.split(':')
  return `${Number(h)} h ${m}`
}

/** « 09:00:00 » → « 9 » ; « 09:30:00 » → « 9 h 30 » (pour les cases du calendrier) */
export function heureCourte(texte: string): string {
  const [h, m] = texte.split(':')
  return m === '00' ? String(Number(h)) : `${Number(h)} h ${m}`
}

/** Un moment exact → sa date et son heure à Paris : { jour: « 2026-10-20 », heure: « 00:00 » } */
export function aParis(iso: string): { jour: string; heure: string } {
  const [jour, h] = new Date(iso).toLocaleString('sv-SE', { timeZone: 'Europe/Paris' }).split(' ')
  return { jour: jour ?? '', heure: (h ?? '').slice(0, 5) }
}

/** « 2026-10-20 » + 4 jours → « 2026-10-24 » */
export function ajouterJours(jour: string, nombre: number): string {
  const [a, m, j] = jour.split('-').map(Number)
  const date = new Date(Date.UTC(a ?? 0, (m ?? 1) - 1, (j ?? 1) + nombre))
  return date.toISOString().slice(0, 10)
}

/** 1 = lundi … 7 = dimanche, pour « 2026-10-13 » */
export function jourSemaine(jour: string): number {
  const [a, m, j] = jour.split('-').map(Number)
  return ((new Date(Date.UTC(a ?? 0, (m ?? 1) - 1, j ?? 1)).getUTCDay() + 6) % 7) + 1
}

/** « 2026-10-13 » → « mardi 13 octobre » */
export function jourLisible(jour: string): string {
  const [, m, j] = jour.split('-').map(Number)
  return `${JOURS[jourSemaine(jour) - 1]} ${j} ${MOIS[(m ?? 1) - 1]}`
}

/** « 2026-10-20 » → « 20/10/2026 » */
export function jourCourt(jour: string): string {
  const [a, m, j] = jour.split('-')
  return `${j}/${m}/${a}`
}

/** Le blocage couvre-t-il au moins une partie de ce jour (heure de Paris) ? */
export function bloqueCeJour(blocage: Blocage, jour: string): boolean {
  const debut = aParis(blocage.debut)
  const fin = aParis(blocage.fin)
  return `${debut.jour} ${debut.heure}` < `${ajouterJours(jour, 1)} 00:00` && `${fin.jour} ${fin.heure}` > `${jour} 00:00`
}

/** « Du 20/10/2026 au 24/10/2026 » (jours entiers) ; « 03/11/2026, de 14 h 00 à 16 h 00 » ; sinon les deux moments */
export function periodeLisible(blocage: Blocage): string {
  const d = aParis(blocage.debut)
  const f = aParis(blocage.fin)
  if (d.heure === '00:00' && f.heure === '00:00') {
    const dernier = ajouterJours(f.jour, -1)
    return dernier === d.jour ? `Le ${jourCourt(d.jour)}` : `Du ${jourCourt(d.jour)} au ${jourCourt(dernier)}`
  }
  if (d.jour === f.jour) return `${jourCourt(d.jour)}, de ${heure(d.heure)} à ${heure(f.heure)}`
  return `Du ${jourCourt(d.jour)} à ${heure(d.heure)} au ${jourCourt(f.jour)} à ${heure(f.heure)}`
}

/** 90 → « 1 h 30 » ; 0 → « aucune » ; 2880 → « 2 jours » */
export function dureeLisible(minutes: number): string {
  if (minutes === 0) return 'aucune'
  if (minutes % 1440 === 0) return minutes === 1440 ? '24 h' : `${minutes / 1440} jours`
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  if (!h) return `${m} min`
  return m ? `${h} h ${String(m).padStart(2, '0')}` : `${h} h`
}

// Choix proposés dans les réglages (bornes : backend/app/reglages.py)
export const PAUSES = [0, 15, 30, 45, 60, 90, 120, 180]
export const DELAIS_MIN = [0, 30, 60, 120, 240, 1440, 2880, 10080]
export const DELAIS_MAX = [1, 2, 3, 6, 12]
