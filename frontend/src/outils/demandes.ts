// Demandes publiées par les clients (RM-DEMANDES.md) : ce que le serveur renvoie, et les mots montrés à l'écran.
import type { BadgeEtat } from './prestataires'

/** Une demande sur l'accueil : jamais le nom complet ni la rue */
export interface DemandeVisible {
  id: number
  titre: string
  description: string
  metier_id: number
  metier: string
  ville: string
  quand: Quand
  jour: string | null
  lieu: 'chez_moi' | 'chez_prestataire'
  budget_centimes: number | null
  client: string
  cree_le: string
  nombre_photos: number
  a_moi: boolean
  nombre_reponses: number
  /** 10 prestataires ont déjà répondu */
  complete: boolean
  /** Pour un prestataire connecté : son métier, son rayon, pas complète (ou il a déjà répondu) */
  peut_repondre: boolean
  /** Pour un prestataire qui a déjà répondu : sa conversation avec le client */
  conversation_id: number | null
  /** Prestataire sans SIRET : pourquoi [Répondre] est verrouillé (métier, adresse, case, plafond) */
  raison_verrou: string | null
}

/** Une de mes demandes, dans « Mes demandes » : avec son état et mon adresse */
export interface MaDemande extends DemandeVisible {
  statut: 'ouverte' | 'pourvue' | 'fermee' | 'expiree'
  expire_le: string
  adresse_ligne: string | null
  adresse_complement: string | null
  code_postal: string | null
  latitude: number | null
  longitude: number | null
  cachee: boolean
}

export const REPONSES_MAX = 10

export function badgeDemande(demande: MaDemande): { etat: BadgeEtat; texte: string } {
  if (demande.cachee) return { etat: 'erreur', texte: 'cachée par l’administrateur' }
  return {
    ouverte: { etat: 'ok' as BadgeEtat, texte: 'ouverte' },
    pourvue: { etat: 'ok' as BadgeEtat, texte: 'pourvue : prestataire choisi' },
    fermee: { etat: 'neutre' as BadgeEtat, texte: 'fermée' },
    expiree: { etat: 'attente' as BadgeEtat, texte: 'expirée' },
  }[demande.statut]
}

export type Quand = 'des_que_possible' | 'sept_jours' | 'jour_precis' | 'pas_presse'

export const QUAND: { valeur: Quand; texte: string }[] = [
  { valeur: 'des_que_possible', texte: 'Dès que possible' },
  { valeur: 'sept_jours', texte: 'Dans les 7 jours' },
  { valeur: 'jour_precis', texte: 'Un jour précis' },
  { valeur: 'pas_presse', texte: 'Pas pressé' },
]

const jourLong = new Intl.DateTimeFormat('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' })

/** « Dès que possible », ou « samedi 10 octobre » pour un jour précis */
export function texteQuand(demande: Pick<DemandeVisible, 'quand' | 'jour'>): string {
  if (demande.quand === 'jour_precis' && demande.jour) return jourLong.format(new Date(`${demande.jour}T12:00:00`))
  return QUAND.find((q) => q.valeur === demande.quand)?.texte ?? ''
}

/** 4000 → « 40 € » ; 4050 → « 40,50 € » */
export function texteBudget(centimes: number): string {
  return `${(centimes / 100).toLocaleString('fr-FR', { minimumFractionDigits: centimes % 100 ? 2 : 0 })} €`
}
