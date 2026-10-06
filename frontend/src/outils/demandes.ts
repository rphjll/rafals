// Demandes publiées par les clients (RM-DEMANDES.md) : ce que le serveur renvoie, et les mots montrés à l'écran.

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
