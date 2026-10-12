// Avis : types de ce que renvoie le serveur, à un seul endroit (RM-AVIS.md).

/** Ce que voit tout le monde : « ★★★★★ Marie D., octobre 2026 : … » */
export interface AvisPublic {
  id: number
  note: number
  texte: string
  auteur: string
  mois: string
  reponse: string | null
}

/** Ce que voient son auteur et le prestataire concerné */
export interface AvisDetaille extends AvisPublic {
  rendez_vous_id: number
  modifiable_jusqu_au: string
  retire: boolean
  cache_motif: string | null
  signale: boolean
}

/** 4 → « ★★★★☆ » */
export function etoiles(note: number): string {
  const entiere = Math.round(note)
  return '★'.repeat(entiere) + '☆'.repeat(5 - entiere)
}

export const AVIS_TEXTE_MIN = 10
export const AVIS_TEXTE_MAX = 1000

// ---------- Avis d'un prestataire sur un client (RM-AVIS.md § « Notation dans les deux sens ») ----------

export const AVIS_CLIENT_TEXTE_MAX = 500

export interface AvisClientPublic {
  id: number
  note: number
  texte: string
  /** « Karim Benali » */
  auteur: string
  mois: string
  reponse: string | null
}

/** Un avis que j'ai reçu comme client (« Mes avis reçus ») */
export interface AvisClientRecu extends AvisClientPublic {
  rendez_vous_id: number
  titre: string
  modifiable_jusqu_au: string
  retire: boolean
  cache_motif: string | null
  signale: boolean
}

/** La page publique d'un client : « Marie D. », jamais le nom complet */
export interface ClientPublic {
  id: number
  nom: string
  membre_depuis: string
  note: number | null
  nombre_avis: number
  avis: AvisClientPublic[]
}

/** « 4,8 ★ · 6 avis » ; sans avis : « Aucun avis pour l'instant » */
export function texteNote(note: number | null, nombre: number): string {
  if (!nombre || note === null) return 'Aucun avis pour l’instant'
  return `${note.toFixed(1).replace('.', ',')} ★ · ${nombre} avis`
}
