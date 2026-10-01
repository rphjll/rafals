// Recherche : types de ce que renvoie le serveur, et textes des cartes (RM-RECHERCHE.md).

import type { AnnoncePublique } from './annonces'
import { euros } from './annonces'
import type { CommuneVisible } from './prestataires'

export interface CarteResultat {
  prestataire_id: number
  nom_affiche: string
  a_une_photo: boolean
  ville: string
  distance_km: number
  principal: boolean
  note: number | null
  nombre_avis: number
  nouveau: boolean
  a_partir_de_centimes: number | null
  a_partir_de_par_heure: boolean
  nombre_annonces: number
  vient_chez_vous: boolean
  carte_possible: boolean
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

export interface PrestatairePublic {
  id: number
  nom_affiche: string
  presentation: string | null
  a_une_photo: boolean
  ville: string
  distance_km: number
  metiers: { id: number; nom: string }[]
  siret_verifie: boolean
  note: number | null
  nombre_avis: number
  absences: number
  annonces: AnnoncePublique[]
}

/** 4.5 → « 4,5 » */
export function noteLisible(note: number): string {
  return note.toFixed(1).replace('.', ',')
}

/** « à partir de 40 €/h » ; « à partir de 45 € » ; « Sur devis » */
export function aPartirDe(r: Pick<CarteResultat, 'a_partir_de_centimes' | 'a_partir_de_par_heure'>): string {
  if (r.a_partir_de_centimes === null) return 'Sur devis'
  return `à partir de ${euros(r.a_partir_de_centimes)}${r.a_partir_de_par_heure ? '/h' : ''}`
}

/** 1 → « 1 annonce » ; 3 → « 3 annonces » (mot qui prend un « s » au pluriel) */
export function pluriel(nombre: number, mot: string): string {
  return `${nombre} ${mot}${nombre > 1 ? 's' : ''}`
}
