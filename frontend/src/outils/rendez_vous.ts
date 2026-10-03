// Rendez-vous : types et textes montrés (états, plages horaires), à un seul endroit (RM-RENDEZ-VOUS.md).

import { aParis, heure, jourCourt, jourLisible } from './agenda'
import type { AvisDetaille } from './avis'
import type { PaiementVisible } from './paiements'
import type { BadgeEtat } from './prestataires'

export type StatutRendezVous =
  | 'en_attente'
  | 'confirme'
  | 'refuse'
  | 'expire'
  | 'annule_client'
  | 'annule_prestataire'
  | 'deplace'

export interface RendezVousVisible {
  id: number
  annonce_id: number
  remplace_id: number | null
  debut: string
  fin: string
  titre: string
  prix_centimes: number | null
  heures: number | null
  lieu: 'chez_client' | 'chez_moi'
  adresse: string | null
  mode_paiement: 'especes' | 'carte'
  statut: StatutRendezVous
  motif: string | null
  reponse_avant: string | null
  annulable_jusqu_au: string | null
  absence: Absence | null
  /** L'avis laissé sur ce rendez-vous (lot 4.8) */
  avis: AvisDetaille | null
  /** Client : rendez-vous tenu, dans les 30 jours, pas encore d'avis */
  peut_noter: boolean
  /** Le prestataire (vu par le client) ou le client (vu par le prestataire) ; téléphone seulement quand c'est permis ;
   *  « absences » : celles du client en 6 mois, montrées au prestataire */
  autre: { nom: string; telephone: string | null; prestataire_id?: number; client_id?: number; absences?: number }
  /** Payé par carte (lot 5.1) */
  paiement: PaiementVisible | null
  /** Juste après une réservation par carte : la page de paiement de Stripe */
  paiement_adresse?: string | null
  /** [Payé] : argent reçu hors de rafals (lot 5.5) */
  paye_direct_le: string | null
  paye_direct_moyen: 'especes' | 'cheque' | 'virement' | null
  /** La facture de ce rendez-vous, s'il en a une */
  facture_id: number | null
  facture_numero: string | null
}

/** Absence sur un rendez-vous (lot 4.5) */
export interface Absence {
  absent: 'client' | 'prestataire'
  signalee_le: string
  contestable_jusqu_au: string
  contestation: string | null
  contestee_le: string | null
  decision: 'compte' | 'ne_compte_pas' | null
  compte: boolean
}

/** On peut signaler une absence après le début, et jusqu'à 7 jours après la fin (RM-RENDEZ-VOUS) ; le client d'un
 *  rendez-vous payé par carte, 48 h seulement : l'argent part ensuite vers le prestataire (RM-PAIEMENTS) */
export function absenceSignalable(r: RendezVousVisible, moi: 'client' | 'prestataire', maintenant = new Date()): boolean {
  const heure = 3600 * 1000
  const paye = r.paiement && (r.paiement.statut === 'paye' || r.paiement.statut === 'verse')
  const delai = moi === 'client' && paye ? 48 * heure : 7 * 24 * heure
  return r.statut === 'confirme' && !r.absence && new Date(r.debut) <= maintenant && maintenant.getTime() <= new Date(r.fin).getTime() + delai
}

/** [Payé…] : rendez-vous en espèces confirmé, dont l'heure est passée, pas encore noté payé, sans absence (RM-FACTURES).
 *  (Le SIRET vérifié du prestataire est contrôlé par l'écran et par le serveur.) */
export function encaissable(r: RendezVousVisible, maintenant = new Date()): boolean {
  return r.statut === 'confirme' && r.mode_paiement === 'especes' && !r.paye_direct_le && !r.absence && !!r.prix_centimes && new Date(r.debut) <= maintenant
}

/** La personne marquée absente peut contester dans les 7 jours, une seule fois */
export function contestable(a: Absence | null, moi: 'client' | 'prestataire', maintenant = new Date()): boolean {
  return !!a && a.absent === moi && !a.contestee_le && maintenant < new Date(a.contestable_jusqu_au)
}

export interface ReglagesReservation {
  confirmation_automatique: boolean
  annulation_delai_heures: number
}

export const DELAIS_ANNULATION = [2, 12, 24, 48]

/** Rendez-vous encore « vivant » : demande en attente, ou confirmé pas encore terminé */
export function aVenir(r: RendezVousVisible, maintenant = new Date()): boolean {
  return (r.statut === 'en_attente' || r.statut === 'confirme') && new Date(r.fin) > maintenant
}

export function badgeRendezVous(r: RendezVousVisible): { etat: BadgeEtat; texte: string } {
  if (r.absence) return { etat: 'erreur', texte: r.absence.absent === 'client' ? 'client absent' : 'prestataire absent' }
  if (r.statut === 'confirme') return new Date(r.fin) > new Date() ? { etat: 'ok', texte: 'confirmé' } : { etat: 'neutre', texte: 'passé' }
  return (
    {
      en_attente: { etat: 'attente' as BadgeEtat, texte: 'en attente' },
      refuse: { etat: 'erreur' as BadgeEtat, texte: 'refusé' },
      expire: { etat: 'neutre' as BadgeEtat, texte: 'sans réponse' },
      annule_client: { etat: 'neutre' as BadgeEtat, texte: 'annulé par le client' },
      annule_prestataire: { etat: 'erreur' as BadgeEtat, texte: 'annulé par le prestataire' },
      deplace: { etat: 'neutre' as BadgeEtat, texte: 'déplacé' },
    }[r.statut] ?? { etat: 'neutre', texte: r.statut }
  )
}

/** « Mardi 13/10/2026, 10 h 00 – 10 h 45 » */
export function plage(r: Pick<RendezVousVisible, 'debut' | 'fin'>): string {
  const d = aParis(r.debut)
  const f = aParis(r.fin)
  const jour = jourLisible(d.jour).split(' ')[0] ?? ''
  return `${jour.charAt(0).toUpperCase()}${jour.slice(1)} ${jourCourt(d.jour)}, ${heure(d.heure)} – ${heure(f.heure)}`
}

/** « lundi 12/10 à 10 h 00 » (pour les délais) */
export function momentCourt(iso: string): string {
  const m = aParis(iso)
  return `${jourLisible(m.jour).split(' ')[0]} ${jourCourt(m.jour).slice(0, 5)} à ${heure(m.heure)}`
}
