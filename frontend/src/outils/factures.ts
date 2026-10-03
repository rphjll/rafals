// Factures : types et textes montrés, à un seul endroit (RM-FACTURES.md ; lot 5.6).

import { MOYENS_DIRECTS } from './devis'

export interface FactureVisible {
  id: number
  /** « F-2026-0001 » (prestataire), « R-2026-0001 » (commission de rafals) */
  numero: string
  sorte: 'vente' | 'avoir' | 'commission'
  emise_le: string
  objet: string
  vendeur: string
  acheteur: string
  /** Négatif pour un avoir */
  ttc_centimes: number
  moyen_paiement: 'carte' | 'especes' | 'cheque' | 'virement' | null
  avoir_de: string | null
}

export type MoyenDirect = keyof typeof MOYENS_DIRECTS

/** « carte », « espèces », « chèque », « virement » ; la commission est « déjà prélevée » */
export function moyenLisible(f: FactureVisible): string {
  if (f.sorte === 'commission') return 'déjà prélevée'
  if (f.moyen_paiement === 'carte') return 'carte'
  return f.moyen_paiement ? MOYENS_DIRECTS[f.moyen_paiement] : ''
}

/** Ouvre le PDF d'une facture dans un nouvel onglet (on peut l'enregistrer ou l'imprimer) */
export function ouvrirPdf(factureId: number): void {
  window.open(`/api/factures/${factureId}/pdf`, '_blank', 'noopener')
}
