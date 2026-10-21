// « Mon profil » façon Instagram (.doc/ihm/RM-PROFIL-IHM.md, 21/10/2026) : dessin et couleur de chaque ligne
// des onglets « Mon activité » et « Mon compte », et les chiffres du haut de la page.
import type { InjectionKey, Ref } from 'vue'
import { appelerServeur } from '../api'
import { noteLisible } from './recherche'

/** Une carte (AppSection) posée dans une AppListeLignes devient une ligne qui se déplie */
export interface ListeLignes {
  ouvertes: Ref<Set<string>>
  resumes: Ref<Record<string, string>>
  basculer: (cle: string) => void
}
export const CLE_LISTE_LIGNES: InjectionKey<ListeLignes> = Symbol('liste-lignes')

interface Ligne {
  picto: string
  teinte: string
  /** Même ligne sous un autre titre (ex. « Modifier mes informations ») : elle reste ouverte en changeant de titre */
  cle?: string
}
const BLEU = 'bg-teinte-bleu'
const VERT = 'bg-teinte-vert'
const JAUNE = 'bg-teinte-jaune'
const ORANGE = 'bg-teinte-orange'
const ROSE = 'bg-teinte-rose'
const VIOLET = 'bg-teinte-violet'
const LIGNES: Record<string, Ligne> = {
  'Sans SIRET : vos limites': { picto: '⚠️', teinte: JAUNE },
  'Paiement par carte': { picto: '💳', teinte: BLEU },
  'Mes métiers': { picto: '🛠️', teinte: VERT },
  Visibilité: { picto: '👁️', teinte: JAUNE },
  TVA: { picto: '🧮', teinte: VIOLET },
  'Mes informations': { picto: '👤', teinte: VERT },
  'Modifier mes informations': { picto: '👤', teinte: VERT, cle: 'Mes informations' },
  'Accord de tes parents': { picto: '✍️', teinte: VIOLET },
  'Mon adresse': { picto: '🏠', teinte: ORANGE },
  Absences: { picto: '⏰', teinte: ROSE },
  'Notifications sur cet appareil': { picto: '🔔', teinte: VIOLET },
  'Mes paiements par carte': { picto: '🧾', teinte: BLEU },
  'Mes données': { picto: '📦', teinte: JAUNE },
  'Fermer mon compte': { picto: '🚪', teinte: ROSE },
}
export function ligneDe(titre: string): Ligne & { cle: string } {
  const l = LIGNES[titre] ?? { picto: '•', teinte: VERT }
  return { ...l, cle: l.cle ?? titre }
}

/** Un chiffre du haut : « 12 » + « abonnés » */
export interface ChiffreProfil {
  valeur: string
  texte: string
}
/** « 4,8 ★ » / « 23 avis » ; « — » / « 0 avis » tant que personne n'a noté */
export function chiffreNote(note: number | null, nombre: number): ChiffreProfil {
  return { valeur: note === null ? '—' : `${noteLisible(note)} ★`, texte: `${nombre} avis` }
}
/** « 1 photo », « 8 photos », « 0 abonnement » */
export function chiffre(nombre: number, mot: string): ChiffreProfil {
  return { valeur: String(nombre), texte: nombre > 1 ? `${mot}s` : mot }
}

/** Combien de prestataires je suis (« 4 abonnements ») ; null si la liste n'a pas pu être lue */
export async function compterAbonnements(): Promise<number | null> {
  try {
    return (await appelerServeur<unknown[]>('/api/moi/abonnements')).length
  } catch {
    return null
  }
}
/** « 4 abonnements », ou « — » tant que le nombre n'est pas connu */
export function chiffreOuTiret(nombre: number | null, mot: string): ChiffreProfil {
  return nombre === null ? { valeur: '—', texte: `${mot}s` } : chiffre(nombre, mot)
}
