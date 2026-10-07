// Les deux groupes du menu (.doc/ihm/RM-ENTETE-IHM.md) : l'en-tête et le sous-menu lisent la même liste.
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useCompte } from './useCompte'

export interface LienMenu {
  vers: string
  texte: string
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

  return { groupe, sousMenu, estPrestataire, estSur }
}
