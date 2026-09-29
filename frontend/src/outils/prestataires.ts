// Libellés et couleurs des états du prestataire : un seul endroit pour « Mon activité » et l'Administration.

type Etat = 'ok' | 'attente' | 'erreur' | 'neutre'

export interface CommuneVisible {
  id: number
  nom: string
  codes_postaux: string[]
  departement: string
}

export interface ProfilPrestataire {
  id: number
  nom_affiche: string
  presentation: string | null
  metier_principal: { id: number; nom: string }
  metiers_secondaires: { id: number; nom: string }[]
  commune: CommuneVisible
  distance_km: number
  siret: string | null
  siret_statut: 'absent' | 'a_verifier' | 'verifie' | 'refuse'
  statut: 'actif' | 'en_pause' | 'bloque' | 'arrete'
  a_une_photo: boolean
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
