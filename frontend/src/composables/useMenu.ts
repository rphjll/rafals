// Les deux groupes du menu (.doc/ihm/RM-ENTETE-IHM.md) : l'en-tête et le sous-menu lisent la même liste.
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useCompte } from './useCompte'
import { useNonLus } from './useNonLus'

export interface LienMenu {
  vers: string
  texte: string
}
/** Une entrée principale : « court » et « picto » servent à la barre du bas sur téléphone */
export interface EntreeMenu extends LienMenu {
  court: string
  picto: string
  actif: boolean
  compteur?: number
}
type Groupe = 'reservations' | 'activite'

const RESERVATIONS: LienMenu[] = [
  { vers: '/mes-demandes', texte: 'Mes demandes' },
  { vers: '/rendez-vous', texte: 'Rendez-vous' },
  { vers: '/devis', texte: 'Devis' },
  { vers: '/factures', texte: 'Factures' },
]
// Visible seulement des prestataires
const ACTIVITE: LienMenu[] = [
  { vers: '/proposer', texte: 'Ma fiche' },
  { vers: '/demandes-pres-de-chez-moi', texte: 'Demandes près de chez moi' },
  { vers: '/mon-agenda', texte: 'Mon agenda' },
  { vers: '/devis', texte: 'Devis' },
  { vers: '/factures', texte: 'Factures' },
  { vers: '/demarches', texte: 'Mes démarches' },
]

// « Devis » et « Factures » sont dans les deux groupes : on reste dans le groupe d'où l'on vient.
const dernierGroupe = ref<Groupe>('reservations')

const estDans = (chemin: string, vers: string) => chemin === vers || chemin.startsWith(`${vers}/`)
const contient = (liens: LienMenu[], chemin: string) => liens.some((lien) => estDans(chemin, lien.vers))

export function useMenu() {
  const route = useRoute()
  const { compte } = useCompte()
  const estPrestataire = computed(() => !!compte.value?.prestataire_id)

  const groupe = computed<Groupe | null>(() => {
    const reservations = contient(RESERVATIONS, route.path)
    const activite = contient(ACTIVITE, route.path)
    if (reservations && activite) return estPrestataire.value ? dernierGroupe.value : 'reservations'
    if (activite) return 'activite'
    return reservations ? 'reservations' : null
  })
  watch(groupe, (g) => g && (dernierGroupe.value = g), { immediate: true })

  const sousMenu = computed<LienMenu[]>(() => {
    if (groupe.value === 'reservations') return RESERVATIONS
    return groupe.value === 'activite' && estPrestataire.value ? ACTIVITE : []
  })
  const estSur = (vers: string) => estDans(route.path, vers)

  // Les entrées principales : l'en-tête (ordinateur) et la barre du bas (téléphone) lisent la même liste.
  // Les pages de chaque groupe sont dans le sous-menu (AppSousMenu), sous l'en-tête.
  const { nonLus } = useNonLus()
  const entrees = computed<EntreeMenu[]>(() => [
    { vers: '/', texte: 'Accueil', court: 'Accueil', picto: 'menu-accueil', actif: route.path === '/' },
    { vers: '/trouver', texte: 'Trouver un prestataire', court: 'Trouver', picto: 'menu-trouver', actif: estSur('/trouver') },
    { vers: '/rendez-vous', texte: 'Mes réservations', court: 'Réservations', picto: 'menu-reservations', actif: groupe.value === 'reservations' },
    // Le compteur rouge : nombre de conversations avec du nouveau
    ...(compte.value
      ? [{ vers: '/messages', texte: 'Messages', court: 'Messages', picto: 'menu-messages', actif: estSur('/messages'), compteur: nonLus.value }]
      : []),
    {
      vers: '/proposer',
      texte: estPrestataire.value ? 'Mon activité' : 'Proposer mes services',
      court: estPrestataire.value ? 'Activité' : 'Proposer',
      picto: 'menu-activite',
      actif: groupe.value === 'activite',
    },
  ])

  return { groupe, sousMenu, estPrestataire, estSur, entrees }
}
