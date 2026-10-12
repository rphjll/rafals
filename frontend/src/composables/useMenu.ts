// Le menu (.doc/ihm/RM-ENTETE-IHM.md) : l'en-tête, la barre du bas et le sous-menu lisent la même liste.
// Depuis le 07/10/2026 (demande de Raphael) : tout est rangé dans « Mon activité » ; l'ancienne entrée
// « Mon activité » (la fiche du prestataire) s'appelle « Mon profil » ; « Mes réservations » n'existe plus.
// Le même jour, « Mon profil » et « Mon compte » ont fusionné : la page /profil s'ouvre par le rond des initiales.
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { adresseDe, fonctionsPour } from '../outils/activite'
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

export const PAGE_ACTIVITE = '/mon-activite'

const estDans = (chemin: string, vers: string) => chemin === vers || chemin.startsWith(`${vers}/`)

export function useMenu() {
  const route = useRoute()
  const { compte } = useCompte()
  const estPrestataire = computed(() => !!compte.value?.prestataire_id)
  const estSur = (vers: string) => estDans(route.path, vers)

  // Les pages de « Mon activité » qui ont leur ligne dans le sous-menu (un prestataire en voit plus qu'un client)
  const pagesActivite = computed<LienMenu[]>(() => {
    const prestataireId = compte.value?.prestataire_id ?? null
    return fonctionsPour(prestataireId)
      .filter((f) => f.sousMenu)
      .map((f) => ({ vers: adresseDe(f, prestataireId) ?? PAGE_ACTIVITE, texte: f.texte }))
  })
  // Le profil d'un client (/clients/12) s'ouvre depuis « Mes clients » : il fait partie de « Mon activité »
  const dansActivite = computed(() => estSur(PAGE_ACTIVITE) || estSur('/clients') || pagesActivite.value.some((page) => estSur(page.vers)))

  // Sous l'en-tête, sur une page de « Mon activité » (pas sur la page d'ensemble, qui montre déjà tout en tuiles)
  const sousMenu = computed<LienMenu[]>(() =>
    dansActivite.value && !estSur(PAGE_ACTIVITE) ? [{ vers: PAGE_ACTIVITE, texte: '‹ Mon activité' }, ...pagesActivite.value] : [],
  )

  // Les entrées principales : l'en-tête (ordinateur) et la barre du bas (téléphone) lisent la même liste.
  const { nonLus } = useNonLus()
  const entrees = computed<EntreeMenu[]>(() => [
    { vers: '/', texte: 'Accueil', court: 'Accueil', picto: 'menu-accueil', actif: route.path === '/' },
    { vers: '/trouver', texte: 'Trouver un prestataire', court: 'Trouver', picto: 'menu-trouver', actif: estSur('/trouver') },
    // Le compteur rouge : nombre de conversations avec du nouveau
    ...(compte.value
      ? [{ vers: '/messages', texte: 'Messages', court: 'Messages', picto: 'menu-messages', actif: estSur('/messages'), compteur: nonLus.value }]
      : []),
    { vers: PAGE_ACTIVITE, texte: 'Mon activité', court: 'Activité', picto: 'menu-activite', actif: dansActivite.value },
    // « Mon profil » s'ouvre par le rond des initiales (AppEntete) ; ici il ne reste que l'invitation à devenir prestataire
    ...(estPrestataire.value
      ? []
      : [{ vers: '/profil?proposer=1', texte: 'Proposer mes services', court: 'Proposer', picto: 'services-personne', actif: estSur('/profil') }]),
  ])

  return { sousMenu, estPrestataire, estSur, entrees }
}
