// Messagerie et propositions (RM-MESSAGERIE.md, RM-DEMANDES.md) : ce que le serveur renvoie, et les mots de l'écran.
import { formaterDateHeure } from './dates'
import { montant } from './paiements'
import type { BadgeEtat } from './prestataires'

export interface ConversationResumee {
  id: number
  cote: 'client' | 'prestataire'
  /** « Karim Benali » pour le client, « Marie D. » pour le prestataire */
  avec: string
  prestataire_id: number
  client_id: number
  dernier_message_le: string
  apercu: string
  non_lus: number
  bloquee: boolean
}

export interface MessageVisible {
  id: number
  de_moi: boolean
  /** « information » : une ligne écrite par rafals (ex. « Marie D. a refusé la proposition de 35,00 € ») */
  genre: 'texte' | 'information'
  texte: string
  cree_le: string
  lu: boolean
  nombre_photos: number
}

export interface ConversationVisible extends ConversationResumee {
  bloquee_par_moi: boolean
  coordonnees_masquees: boolean
  messages: MessageVisible[]
}

export interface PropositionVisible {
  id: number
  conversation_id: number
  demande_id: number | null
  demande_titre: string | null
  metier: string
  prix_centimes: number
  debut: string
  fin: string
  lieu: 'chez_client' | 'chez_moi'
  paiement_carte: boolean
  paiement_especes: boolean
  /** Ce que le client peut vraiment choisir en acceptant */
  modes_de_paiement: ('carte' | 'especes')[]
  statut: 'en_attente' | 'acceptee' | 'refusee' | 'retiree' | 'remplacee' | 'non_retenue' | 'expiree'
  remplace_id: number | null
  cree_le: string
  /** Le prix proposé par le client, s'il attend la réponse du prestataire */
  negociation: { id: number; prix_centimes: number; statut: string } | null
  rendez_vous_id: number | null
}

export const DUREES = [30, 45, 60, 90, 120, 180, 240].map((minutes) => ({ valeur: minutes, texte: duree(minutes) }))

/** 60 → « 1 h » ; 45 → « 45 min » ; 90 → « 1 h 30 » */
export function duree(minutes: number): string {
  const heures = Math.floor(minutes / 60)
  const reste = minutes % 60
  if (!heures) return `${reste} min`
  return reste ? `${heures} h ${String(reste).padStart(2, '0')}` : `${heures} h`
}

export function dureeDe(p: Pick<PropositionVisible, 'debut' | 'fin'>): string {
  return duree(Math.round((new Date(p.fin).getTime() - new Date(p.debut).getTime()) / 60000))
}

/** « 12/10/2026 à 8 h 30 · 1 h · chez vous » (vu par le client) ou « … · chez le client » (vu par le prestataire) */
export function quandEtOu(p: PropositionVisible, cote: 'client' | 'prestataire'): string {
  const chezLeClient = cote === 'client' ? 'chez vous' : 'chez le client'
  const chezLePrestataire = cote === 'client' ? 'chez le prestataire' : 'chez vous'
  return `${formaterDateHeure(p.debut)} · ${dureeDe(p)} · ${p.lieu === 'chez_client' ? chezLeClient : chezLePrestataire}`
}

export function textePaiement(p: Pick<PropositionVisible, 'paiement_carte' | 'paiement_especes'>): string {
  return [p.paiement_carte ? 'carte' : '', p.paiement_especes ? 'espèces' : ''].filter(Boolean).join(' ou ')
}

export function prix(centimes: number): string {
  return montant(centimes)
}

export function badgeProposition(p: PropositionVisible): { etat: BadgeEtat; texte: string } {
  if (p.statut === 'en_attente' && p.negociation) return { etat: 'attente', texte: 'prix en négociation' }
  return {
    en_attente: { etat: 'attente' as BadgeEtat, texte: 'en attente' },
    acceptee: { etat: 'ok' as BadgeEtat, texte: 'acceptée' },
    refusee: { etat: 'erreur' as BadgeEtat, texte: 'refusée' },
    retiree: { etat: 'neutre' as BadgeEtat, texte: 'retirée' },
    remplacee: { etat: 'neutre' as BadgeEtat, texte: 'remplacée' },
    non_retenue: { etat: 'neutre' as BadgeEtat, texte: 'non retenue' },
    expiree: { etat: 'neutre' as BadgeEtat, texte: 'expirée' },
  }[p.statut]
}

/** Lignes de rafals déjà montrées par une carte de proposition : on ne les répète pas dans le fil */
export function repeteUneCarte(texte: string): boolean {
  return / propose : | accepte \d|^Prix proposé par /.test(texte)
}
