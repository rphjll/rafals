// Libellés et couleurs des états du prestataire : un seul endroit pour « Mon activité » et l'Administration.

export type BadgeEtat = 'ok' | 'attente' | 'erreur' | 'neutre'
type Etat = BadgeEtat

export interface CommuneVisible {
  id: number
  nom: string
  codes_postaux: string[]
  departement: string
}

/** Un métier du profil ; fin_le = dernier jour prévu (« 2026-11-15 »), vide = pas de fin prévue. */
export interface MetierExerce {
  id: number
  nom: string
  fin_le: string | null
}

export interface ProfilPrestataire {
  id: number
  nom_affiche: string
  presentation: string | null
  metier_principal: MetierExerce
  /** Le métier secondaire qui deviendra principal après la date de fin du principal */
  metier_principal_suivant: { id: number; nom: string } | null
  metiers_secondaires: MetierExerce[]
  /** Métiers dont la date de fin est passée (ex. Chauffagiste, arrêté depuis le 31/08) : ils peuvent être repris */
  metiers_arretes: MetierExerce[]
  commune: CommuneVisible
  distance_km: number
  siret: string | null
  siret_statut: 'absent' | 'a_verifier' | 'verifie' | 'refuse'
  /** Case « Je facture la TVA » (lot 5.4) */
  facture_tva: boolean
  statut: 'actif' | 'en_pause' | 'bloque' | 'arrete'
  a_une_photo: boolean
  /** Rangs des photos de son travail, ex. [1, 2, 3] */
  photos: number[]
}

export function badgeSiret(statut: string): { etat: Etat; texte: string } {
  return (
    {
      verifie: { etat: 'ok' as Etat, texte: 'SIRET vérifié' },
      a_verifier: { etat: 'attente' as Etat, texte: 'À vérifier' },
      refuse: { etat: 'erreur' as Etat, texte: 'SIRET refusé' },
    }[statut] ?? { etat: 'attente', texte: 'Sans SIRET' }
  )
}

export function badgeStatut(statut: string): { etat: Etat; texte: string } {
  return (
    {
      actif: { etat: 'ok' as Etat, texte: 'actif' },
      en_pause: { etat: 'neutre' as Etat, texte: 'en pause' },
      bloque: { etat: 'erreur' as Etat, texte: 'bloqué' },
    }[statut] ?? { etat: 'neutre', texte: 'arrêté' }
  )
}

/** « 44306184100047 » → « 443 061 841 00047 » */
export function siretLisible(siret: string | null): string {
  return siret ? siret.replace(/^(\d{3})(\d{3})(\d{3})(\d{5})$/, '$1 $2 $3 $4') : ''
}
