// Créer une auto-entreprise depuis rafals (lot 7.2) : ce que le serveur renvoie, et les libellés communs aux étapes.
import { appelerServeur } from '../api'
import type { BadgeEtat, CommuneVisible } from './prestataires'

export const CHEMIN = '/api/moi/creation-entreprise'
export const SITE_DE_L_ETAT = 'https://formalites.entreprises.gouv.fr'

export interface PieceVisible {
  sorte: string
  /** « la pièce d'identité » */
  nom: string
  /** Le pouvoir et l'attestation sont écrits par rafals */
  deposee_par_rafals: boolean
  depose_le: string | null
  a_refaire: boolean
  /** Effacé à la fin du dossier */
  efface: boolean
}

export type StatutDossier = 'brouillon' | 'envoye' | 'en_examen' | 'a_corriger' | 'accepte' | 'refuse' | 'ferme'

export interface DossierCreation {
  id: number
  statut: StatutDossier
  /** Rien n'est envoyé à l'État (pas encore de compte INPI) */
  demonstration: boolean
  civilite: 'monsieur' | 'madame' | null
  nom_naissance: string | null
  nom_usage: string | null
  prenoms: string | null
  naissance_le: string | null
  naissance_commune: CommuneVisible | null
  naissance_pays: string | null
  nationalite: 'francaise' | 'union_europeenne' | 'autre' | null
  situation_famille: string | null
  numero_secu: string | null
  adresse_rue: string | null
  commune: CommuneVisible | null
  code_postal: string | null
  mail: string | null
  telephone: string | null
  pere_nom: string | null
  mere_nom: string | null
  metier_id: number | null
  metier: string | null
  metier_reglemente: boolean
  description: string | null
  debut_le: string | null
  lieu_travail: 'chez_clients' | 'chez_moi' | 'local' | null
  local_adresse: string | null
  local_commune: CommuneVisible | null
  local_code_postal: string | null
  nom_commercial: string | null
  activite_en_meme_temps: 'aucune' | 'salarie' | 'retraite' | null
  ancien_siren: string | null
  periodicite: 'mois' | 'trimestre' | null
  impot_avec_cotisations: boolean | null
  acre_demandee: boolean | null
  adresse_non_publique: boolean | null
  pieces: PieceVisible[]
  /** Par étape (vous, activite, choix, papiers) : ce qu'il reste à faire avant d'envoyer */
  manque: Record<string, string[]>
  envoye_le: string | null
  guichet_numero: string | null
  motif: string | null
  corriger_avant_le: string | null
  siret_recu: string | null
  statut_change_le: string
}

export interface Situation {
  peut_commencer: boolean
  /** « Vous avez déjà une entreprise (SIRET …) : il n'y a rien à créer. » */
  raison: string | null
  a_un_profil: boolean
  dossier: DossierCreation | null
}

export interface ReglesMetiers {
  reglementes: number[]
  renvoyes: number[]
  debut_max: string
}

export const NOMS_ETAPES = ['Vous', 'Votre activité', 'Vos choix', 'Vos papiers', 'Vérifier et envoyer']
/** Les étapes dans l'ordre, avec la clé de `manque` qui dit si l'étape est finie */
export const CLES_ETAPES = ['vous', 'activite', 'choix', 'papiers'] as const

export const SITUATIONS = [
  { valeur: 1, cle: 'celibataire', texte: 'Célibataire' },
  { valeur: 2, cle: 'concubinage', texte: 'En concubinage' },
  { valeur: 3, cle: 'pacse', texte: 'Pacsé(e)' },
  { valeur: 4, cle: 'marie', texte: 'Marié(e)' },
  { valeur: 5, cle: 'divorce', texte: 'Divorcé(e)' },
  { valeur: 6, cle: 'veuf', texte: 'Veuf / veuve' },
]

export function badgeDossier(statut: StatutDossier): { etat: BadgeEtat; texte: string } {
  return {
    brouillon: { etat: 'neutre' as BadgeEtat, texte: 'pas encore envoyé' },
    envoye: { etat: 'attente' as BadgeEtat, texte: 'envoyé' },
    en_examen: { etat: 'attente' as BadgeEtat, texte: "en cours d'examen" },
    a_corriger: { etat: 'erreur' as BadgeEtat, texte: 'une correction à faire' },
    accepte: { etat: 'ok' as BadgeEtat, texte: 'accepté' },
    refuse: { etat: 'erreur' as BadgeEtat, texte: 'refusé' },
    ferme: { etat: 'neutre' as BadgeEtat, texte: 'fermé' },
  }[statut]
}

/** « 198033306312352 » → « 1 98 03 33 063 123 52 » */
export function numeroSecuLisible(numero: string): string {
  const n = numero.replace(/\s/g, '')
  return [n.slice(0, 1), n.slice(1, 3), n.slice(3, 5), n.slice(5, 7), n.slice(7, 10), n.slice(10, 13), n.slice(13)]
    .filter(Boolean)
    .join(' ')
}

/** Enregistre une étape (ou fait un geste : envoi, correction…) et renvoie la nouvelle situation */
export const envoyerEtape = (chemin: string, donnees: unknown = {}) => appelerServeur<Situation>(`${CHEMIN}${chemin}`, donnees)
