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
