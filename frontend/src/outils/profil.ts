import type { NomIcone } from './icones'
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
  /** Icône de la grande maquette (outils/icones.ts) */
  icone: NomIcone
  /** Couleur du rond : vert, orange, rouge ou gris (comme la maquette) */
  couleur: 'vert' | 'orange' | 'rouge' | 'gris'
  /** Même ligne sous un autre titre (ex. « Modifier mes informations ») : elle reste ouverte en changeant de titre */
  cle?: string
}
const LIGNES: Record<string, Ligne> = {
  'Sans SIRET : vos limites': { icone: 'bouclier', couleur: 'orange' },
  'Paiement par carte': { icone: 'carte', couleur: 'vert' },
  'Mes métiers': { icone: 'fusee', couleur: 'orange' },
  Visibilité: { icone: 'site', couleur: 'vert' },
  TVA: { icone: 'euro', couleur: 'vert' },
  'Mes informations': { icone: 'messages', couleur: 'vert' },
  'Modifier mes informations': { icone: 'messages', couleur: 'vert', cle: 'Mes informations' },
  'Accord de tes parents': { icone: 'devis', couleur: 'orange' },
  'Mon adresse': { icone: 'lieu', couleur: 'orange' },
  Absences: { icone: 'agenda', couleur: 'orange' },
  'Notifications sur cet appareil': { icone: 'cloche', couleur: 'vert' },
  'Mes paiements par carte': { icone: 'euro', couleur: 'vert' },
  'Mes données': { icone: 'telecharger', couleur: 'gris' },
  'Fermer mon compte': { icone: 'sortir', couleur: 'rouge' },
}
export function ligneDe(titre: string): Ligne & { cle: string } {
  const l = LIGNES[titre] ?? { icone: 'suite', couleur: 'vert' }
  return { ...l, cle: l.cle ?? titre }
}
/** Fond et couleur du rond d'une ligne (ex. vert pâle et vert) */
export const COULEURS_LIGNE = {
  vert: { background: 'var(--primaire-doux)', color: 'var(--primaire)' },
  orange: { background: 'var(--accent-doux)', color: 'var(--accent)' },
  rouge: { background: 'var(--erreur-doux)', color: 'var(--erreur)' },
  gris: { background: 'var(--surface2)', color: 'var(--texte-doux)' },
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
