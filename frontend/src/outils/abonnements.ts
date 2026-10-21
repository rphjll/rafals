// Abonnements à un prestataire (.doc/regles-metier/RM-ABONNEMENTS.md ; demande de Raphael du 21/10/2026) :
// types et textes communs à [S'abonner], aux cartes et à « Mes abonnements ».

/** Réponse du serveur après [S'abonner] / [Se désabonner], ex. { abonne: true, abonnes: 13 } */
export interface EtatAbonnement {
  abonne: boolean
  abonnes: number
}

/** Les 3 cases de la cloche, pour un seul prestataire */
export interface NotificationsAbonnement {
  creneau: boolean
  nouveaute: boolean
  retour: boolean
}

/** Une petite carte de « Mes abonnements » */
export interface AbonnementVisible {
  prestataire_id: number
  nom_affiche: string
  a_une_photo: boolean
  ville: string
  metier: string
  note: number | null
  nombre_avis: number
  abonnes: number
  /** false : en pause, bloqué ou arrêté → « Profil en pause », pas de lien */
  visible: boolean
  notifications: NotificationsAbonnement
  abonne_le: string
}

/** Les 3 cases, avec un exemple (Karim → le nom du prestataire) */
export const CASES_NOTIFICATIONS: { cle: keyof NotificationsAbonnement; titre: string; exemple: string }[] = [
  { cle: 'creneau', titre: 'Créneau libre', exemple: '« {nom} est libre jeudi 23/10/2026 à 14 h 00 »' },
  { cle: 'nouveaute', titre: 'Nouveau métier', exemple: '« {nom} propose maintenant : Chauffagiste »' },
  { cle: 'retour', titre: 'Retour après une absence', exemple: '« {nom} reprend son activité ce lundi 03/11/2026 »' },
]

/** 0 → « » (rien d'écrit), 1 → « 1 abonné », 12 → « 12 abonnés » */
export function texteAbonnes(nombre: number): string {
  if (nombre === 0) return ''
  return nombre === 1 ? '1 abonné' : `${nombre} abonnés`
}

/** [S'abonner] ou [Se désabonner] : rend le nouvel état */
export function cheminAbonnement(prestataireId: number, abonne: boolean): string {
  return `/api/prestataires/${prestataireId}/abonnement${abonne ? '/retirer' : ''}`
}
