// Annonces : types et textes montrés (prix, durée, lieu, paiement), à un seul endroit (RM-ANNONCES.md).

import type { BadgeEtat } from './prestataires'

export type FormePrix = 'fixe' | 'heure' | 'devis'
export type Lieu = 'chez_client' | 'chez_moi' | 'les_deux'
export type StatutAnnonce = 'en_ligne' | 'en_pause' | 'retiree'

/** Ce que remplit le prestataire */
export interface DonneesAnnonce {
  metier_id: number
  titre: string
  description: string | null
  forme_prix: FormePrix
  prix_centimes: number | null
  duree_minutes: number | null
  heures_min: number | null
  heures_max: number | null
  lieu: Lieu
  paiement_carte: boolean
  paiement_especes: boolean
}

/** Une annonce dans « Mes annonces » */
export interface AnnonceVisible extends Omit<DonneesAnnonce, 'metier_id'> {
  id: number
  metier: { id: number; nom: string }
  modes_de_paiement: ('carte' | 'especes')[]
  statut: StatutAnnonce
  /** Pourquoi les clients ne la voient pas ; vide = visible de tous */
  raison_cachee: string | null
  /** Retirée par l'administrateur (après un signalement) : le prestataire ne peut pas la remettre en ligne */
  retiree_par_administrateur: boolean
  /** Son métier a passé sa date de fin : republier est refusé tant qu'il n'est pas repris */
  metier_arrete: boolean
  nombre_photos: number
}

/** Une annonce vue par un client : la ville, jamais la rue du local */
export interface AnnoncePublique
  extends Omit<AnnonceVisible, 'statut' | 'raison_cachee' | 'metier_arrete' | 'paiement_carte' | 'paiement_especes'> {
  prestataire: { id: number; nom_affiche: string; a_une_photo: boolean }
  ville: string
}

/** 5000 → « 50 € » ; 4550 → « 45,50 € » */
export function euros(centimes: number): string {
  const valeur = centimes / 100
  return `${Number.isInteger(valeur) ? valeur : valeur.toFixed(2).replace('.', ',')} €`
}

/** « 45,50 » ou « 45.5 » → 4550 ; texte vide ou illisible → null */
export function versCentimes(texte: string): number | null {
  const nombre = Number(texte.replace(',', '.').replace(/\s|€/g, ''))
  return texte.trim() && Number.isFinite(nombre) ? Math.round(nombre * 100) : null
}

/** 120 → « 2 h » ; 45 → « 45 min » ; 90 → « 1 h 30 » */
export function duree(minutes: number): string {
  const heures = Math.floor(minutes / 60)
  const reste = minutes % 60
  if (!heures) return `${reste} min`
  return reste ? `${heures} h ${String(reste).padStart(2, '0')}` : `${heures} h`
}

/** « 50 € · 2 h » ; « 40 €/h · de 1 h à 3 h » ; « Sur devis » */
export function prixCourt(a: Pick<DonneesAnnonce, 'forme_prix' | 'prix_centimes' | 'duree_minutes' | 'heures_min' | 'heures_max'>): string {
  if (a.forme_prix === 'devis' || a.prix_centimes === null) return 'Sur devis'
  if (a.forme_prix === 'heure') {
    const plage = a.heures_min === a.heures_max ? `${a.heures_min} h` : `de ${a.heures_min} h à ${a.heures_max} h`
    return `${euros(a.prix_centimes)}/h · ${plage}`
  }
  return `${euros(a.prix_centimes)} · ${duree(a.duree_minutes ?? 0)}`
}

export const LIEUX: Record<Lieu, string> = {
  chez_client: 'Chez le client',
  chez_moi: 'Chez moi',
  les_deux: 'Chez le client ou chez moi',
}

/** Pour le client : « Chez vous (Karim vient de Pessac) » ; « Au local, à Mérignac » */
export function lieuPourLeClient(a: AnnoncePublique): string {
  const chezVous = `Chez vous (${a.prestataire.nom_affiche} vient de ${a.ville})`
  if (a.lieu === 'chez_client') return chezVous
  if (a.lieu === 'chez_moi') return `Chez ${a.prestataire.nom_affiche}, à ${a.ville} (adresse donnée après réservation)`
  return `Chez vous, ou chez ${a.prestataire.nom_affiche} à ${a.ville}`
}

/** [« carte », « especes »] → « Carte bancaire ou espèces » */
export function paiement(modes: ('carte' | 'especes')[]): string {
  const textes = modes.map((m) => (m === 'carte' ? 'carte bancaire' : 'espèces'))
  const phrase = textes.join(' ou ')
  return phrase.charAt(0).toUpperCase() + phrase.slice(1)
}

export function badgeAnnonce(statut: StatutAnnonce): { etat: BadgeEtat; texte: string } {
  return {
    en_ligne: { etat: 'ok' as BadgeEtat, texte: 'en ligne' },
    en_pause: { etat: 'neutre' as BadgeEtat, texte: 'en pause' },
    retiree: { etat: 'neutre' as BadgeEtat, texte: 'retirée' },
  }[statut]
}

/** Durées proposées pour un prix fixe (la durée bloque l'agenda) */
export const DUREES_PROPOSEES = [15, 30, 45, 60, 90, 120, 150, 180, 240, 300, 360, 480]
