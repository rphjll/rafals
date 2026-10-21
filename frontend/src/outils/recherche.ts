// Recherche : types de ce que renvoie le serveur, et textes des cartes (RM-RECHERCHE.md).

import type { CommuneVisible, LieuService } from './prestataires'

export interface CarteResultat {
  prestataire_id: number
  nom_affiche: string
  a_une_photo: boolean
  ville: string
  distance_km: number
  /** Le métier écrit sur la carte, ex. « Plombier » */
  metier: string
  principal: boolean
  siret_verifie: boolean
  /** Rangs des 2 premières photos de son travail, ex. [1, 2] → /api/prestataires/12/photos/1 */
  photos: number[]
  note: number | null
  nombre_avis: number
  nouveau: boolean
  vient_chez_vous: boolean
  carte_possible: boolean
  /** « 12 abonnés », visible par tous (abonnements, 21/10/2026) */
  abonnes: number
  /** La personne connectée le suit : bouton [Abonné ✓] */
  abonne: boolean
}

export interface PageResultats {
  metier: { id: number; nom: string }
  ville: CommuneVisible
  total: number
  page: number
  pages: number
  resultats: CarteResultat[]
  metiers_voisins: { id: number; nom: string }[]
}

/** Un dossier de métiers (ex. « Jardinage ») et ses prestataires pour une ville */
export interface Rubrique {
  dossier_id: number
  code: string
  nom: string
  total: number
  page: number
  pages: number
  resultats: CarteResultat[]
}

export interface PageRubriques {
  ville: CommuneVisible
  rubriques: Rubrique[]
}

export interface PrestatairePublic {
  id: number
  nom_affiche: string
  presentation: string | null
  a_une_photo: boolean
  ville: string
  distance_km: number
  lieu: LieuService
  metiers: { id: number; nom: string }[]
  siret_verifie: boolean
  note: number | null
  nombre_avis: number
  absences: number
  /** Rangs des photos de son travail (10 au plus) */
  photos: number[]
  abonnes: number
  abonne: boolean
}

/** 4.5 → « 4,5 » */
export function noteLisible(note: number): string {
  return note.toFixed(1).replace('.', ',')
}

/** 1 → « 1 avis » … 3 → « 3 photos » (mot qui prend un « s » au pluriel) */
export function pluriel(nombre: number, mot: string): string {
  return `${nombre} ${mot}${nombre > 1 ? 's' : ''}`
}

/** Adresse d'une photo du travail d'un prestataire : (12, 1) → « /api/prestataires/12/photos/1 » */
export function adressePhotoTravail(prestataireId: number, rang: number, version = 0): string {
  return `/api/prestataires/${prestataireId}/photos/${rang}${version ? `?v=${version}` : ''}`
}

// La ville du visiteur est retenue sur son appareil : « Trouver un prestataire » la redemande une seule fois.
const CLE_VILLE = 'rafals.ville'

export function villeRetenue(): CommuneVisible | null {
  try {
    const ville = JSON.parse(localStorage.getItem(CLE_VILLE) ?? 'null')
    return ville && typeof ville.id === 'number' && typeof ville.nom === 'string' ? ville : null
  } catch {
    return null // navigation privée, ou valeur abîmée : on redemande la ville
  }
}

export function retenirVille(ville: CommuneVisible) {
  try {
    localStorage.setItem(CLE_VILLE, JSON.stringify(ville))
  } catch {
    // navigation privée : la ville sera redemandée à la prochaine visite
  }
}
