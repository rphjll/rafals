// Paiement par carte : types et textes montrés, à un seul endroit (RM-PAIEMENTS.md ; lot 5.2).

import { euros } from './annonces'
import { jourCourt, aParis } from './agenda'
import type { BadgeEtat } from './prestataires'

export type StatutPaiement = 'a_payer' | 'paye' | 'verse' | 'rembourse' | 'abandonne'

export interface PaiementVisible {
  id: number
  rendez_vous_id: number
  titre: string
  debut: string
  /** Le prestataire (vu par le client) ou le client (vu par le prestataire) */
  avec: string
  statut: StatutPaiement
  montant_centimes: number
  paye_le: string | null
  rembourse_le: string | null
  rembourse_centimes: number | null
  /** Client : ce qu'il récupère s'il annule à temps (prix - frais de paiement) */
  rembourse_si_annule_centimes: number | null
  /** Prestataire seulement */
  commission_centimes: number | null
  frais_stripe_centimes: number | null
  net_centimes: number | null
  verse_le: string | null
  versement_prevu_le: string | null
}

/** Où en est le prestataire pour être payé par carte */
export interface EtatCarte {
  ouvert: boolean
  siret_verifie: boolean
  mandat_facturation_le: string | null
  compte_cree: boolean
  pret: boolean
}

/** « 46,50 € » : toujours avec les centimes dans les sommes d'argent payées */
export function montant(centimes: number): string {
  const signe = centimes < 0 ? '−' : ''
  const absolu = Math.abs(centimes)
  return `${signe}${Math.floor(absolu / 100)},${String(absolu % 100).padStart(2, '0')} €`
}

/** « 13/10 » */
function jourMois(iso: string): string {
  return jourCourt(aParis(iso).jour).slice(0, 5)
}

/** La ligne « Prix » d'un rendez-vous payé par carte, vue par le client.
 *  Ex. « 50 € · payé par carte le 02/10/2026 », « 120 € · par carte · remboursé 120,00 € le 05/10/2026 » */
export function prixPayeClient(prix: number | null, p: PaiementVisible): string {
  const debut = `${prix ? euros(prix) : '—'} · `
  if (p.statut === 'a_payer') return `${debut}paiement par carte en attente`
  if (p.statut === 'abandonne') return `${debut}paiement par carte non terminé (rien n'a été pris)`
  if (p.statut === 'rembourse' && p.rembourse_le)
    return `${debut}par carte · remboursé ${montant(p.rembourse_centimes ?? 0)} le ${jourCourt(aParis(p.rembourse_le).jour)}`
  return `${debut}payé par carte${p.paye_le ? ` le ${jourCourt(aParis(p.paye_le).jour)}` : ''}`
}

/** La même ligne, vue par le prestataire. Ex. « 50 € par carte · pour vous 46,50 €, versés le 15/10 » */
export function prixPayePrestataire(prix: number | null, p: PaiementVisible): string {
  const debut = `${prix ? euros(prix) : '—'} par carte · `
  if (p.statut === 'rembourse') return `${debut}remboursé au client`
  const net = montant(p.net_centimes ?? 0)
  if (p.statut === 'verse' && p.verse_le) return `${debut}${net} versés le ${jourMois(p.verse_le)}`
  if (p.versement_prevu_le) return `${debut}pour vous ${net}, versés le ${jourMois(p.versement_prevu_le)}`
  return `${debut}pour vous ${net}, versés après la décision sur l'absence`
}

/** L'état dans le tableau des paiements du prestataire */
export function badgePaiement(p: PaiementVisible): { etat: BadgeEtat; texte: string } {
  if (p.statut === 'verse') return { etat: 'ok', texte: 'versé' }
  if (p.statut === 'rembourse') return { etat: 'erreur', texte: 'remboursé au client' }
  if (p.versement_prevu_le) return { etat: 'attente', texte: `versé le ${jourMois(p.versement_prevu_le)}` }
  return { etat: 'attente', texte: 'en attente (absence)' }
}

/** Ce qui revient au prestataire dans le tableau : le net ; remboursé en entier (sa faute), il perd les frais de Stripe ;
 *  le client a annulé (remboursé moins les frais), il ne perd rien */
export function pourLePrestataire(p: PaiementVisible): number {
  if (p.statut !== 'rembourse') return p.net_centimes ?? 0
  return p.rembourse_centimes === p.montant_centimes ? -(p.frais_stripe_centimes ?? 0) : 0
}
