// Devis : types et textes montrés (états, quantités, dates), à un seul endroit (RM-DEVIS.md ; lot 5.4).

import { aParis, jourCourt, jourLisible } from './agenda'
import { versCentimes } from './prix'
import type { BadgeEtat } from './prestataires'

export type StatutDemande = 'envoyee' | 'devis_recu' | 'declinee' | 'annulee'
export type StatutDevis =
  | 'envoye'
  | 'autre_date'
  | 'accepte'
  | 'termine'
  | 'paye'
  | 'refuse'
  | 'expire'
  | 'annule_client'
  | 'annule_prestataire'

export interface LigneVisible {
  libelle: string
  quantite_centiemes: number
  prix_unitaire_centimes: number
  tva_pour_mille: number | null
  montant_centimes: number
}

export interface DevisVisible {
  id: number
  numero: string
  statut: StatutDevis
  facture_tva: boolean
  mention_tva: string | null
  lignes: LigneVisible[]
  ht_centimes: number
  tva_centimes: number
  ttc_centimes: number
  arrhes_pourcent: number
  arrhes_centimes: number
  solde_centimes: number
  travaux_debut: string
  travaux_fin: string
  valable_jusqu_au: string
  mode_paiement: 'carte' | 'direct' | null
  modes_possibles: ('carte' | 'direct')[]
  envoye_le: string
  accepte_le: string | null
  termine_le: string | null
  paye_le: string | null
  message: string | null
  probleme: string | null
  probleme_le: string | null
  moyen_direct: 'especes' | 'cheque' | 'virement' | null
  arrhes_paiement: string | null
  solde_paiement: string | null
}

export interface DemandeVisible {
  id: number
  titre: string
  texte: string
  nombre_photos: number
  lieu: string | null
  statut: StatutDemande
  motif: string | null
  cree_le: string
  autre: { nom: string; telephone: string | null; prestataire_id?: number; client_id?: number }
  devis: DevisVisible | null
}

/** Réponse des actions sur un devis : la demande à jour, et la page de paiement de Stripe s'il faut payer */
export interface AvecPaiement {
  demande: DemandeVisible
  paiement_adresse: string | null
}

/** 4000 → « 40 » ; 250 → « 2,5 » */
export function quantite(centiemes: number): string {
  return (centiemes / 100).toString().replace('.', ',')
}

/** « 40 » ou « 2,5 » → 4000 ou 250 ; vide ou illisible → null (même calcul que les euros en centimes) */
export const versCentiemes = versCentimes

/** « lundi 19/10/2026 » (une date seule, sans heure) */
export function jourDevis(iso: string): string {
  return `${jourLisible(iso).split(' ')[0]} ${jourCourt(iso)}`
}

/** « 19/10 » */
export function jourMois(iso: string): string {
  return jourCourt(iso.length > 10 ? aParis(iso).jour : iso).slice(0, 5)
}

export const TAUX_TVA = [
  { valeur: 55, texte: '5,5 %' },
  { valeur: 100, texte: '10 %' },
  { valeur: 200, texte: '20 %' },
]

/** L'état d'une demande et de son devis, vu par le client ou par le prestataire */
export function badgeDemande(d: DemandeVisible, cote: 'client' | 'prestataire'): { etat: BadgeEtat; texte: string } {
  if (d.statut === 'envoyee') return cote === 'client' ? { etat: 'neutre', texte: 'demande envoyée' } : { etat: 'attente', texte: 'à répondre' }
  if (d.statut === 'declinee') return { etat: 'erreur', texte: 'déclinée' }
  if (d.statut === 'annulee' || !d.devis) return { etat: 'neutre', texte: 'annulée' }
  const textes: Record<StatutDevis, { etat: BadgeEtat; texte: string }> = {
    envoye: cote === 'client' ? { etat: 'attente', texte: 'devis à étudier' } : { etat: 'neutre', texte: 'devis envoyé' },
    autre_date: cote === 'client' ? { etat: 'neutre', texte: 'autre date demandée' } : { etat: 'attente', texte: 'autre date demandée' },
    accepte: { etat: 'ok', texte: 'accepté' },
    termine: { etat: cote === 'client' ? 'attente' : 'ok', texte: 'travaux terminés' },
    paye: { etat: 'ok', texte: 'payé' },
    refuse: { etat: 'erreur', texte: 'refusé' },
    expire: { etat: 'neutre', texte: 'expiré' },
    annule_client: { etat: 'neutre', texte: 'annulé par le client' },
    annule_prestataire: { etat: 'erreur', texte: 'annulé par le prestataire' },
  }
  return textes[d.devis.statut]
}

/** Demandes et devis qui attendent une action de cette personne (compteur orange de l'onglet) */
export function aFaire(d: DemandeVisible, cote: 'client' | 'prestataire'): boolean {
  const s = d.devis?.statut
  if (cote === 'client') return s === 'envoye' || (s === 'termine' && d.devis?.mode_paiement === 'carte')
  return d.statut === 'envoyee' || s === 'autre_date' || s === 'accepte'
}

export const MOYENS_DIRECTS = { especes: 'espèces', cheque: 'chèque', virement: 'virement' } as const

/** Les arrhes ont-elles vraiment été payées par carte (pas une page de paiement fermée) ? */
export function arrhesPayees(d: DevisVisible): boolean {
  return ['paye', 'verse', 'rembourse'].includes(d.arrhes_paiement ?? '')
}
