// Le menu (.doc/ihm/RM-ENTETE-IHM.md) : l'en-tête et la barre du bas lisent la même liste.
// Depuis le 10/11/2026 (Raphael : « exactement pareil que la maquette ») : les 5 entrées de la grande maquette,
// Accueil, Trouver, Demandes, Messages (une fois connecté) et Mon activité ; la barre du bas ajoute « Moi ».
// Plus de sous-menu sous l'en-tête : chaque page de « Mon activité » a son lien « ‹ Mon activité » en haut.
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import type { NomIcone } from '../outils/icones'
import { useCompte } from './useCompte'
import { useNonLus } from './useNonLus'

/** Une entrée principale : « court » sert à la barre du bas sur téléphone */
export interface EntreeMenu {
  vers: string
  texte: string
  court: string
  icone: NomIcone
  actif: boolean
  compteur?: number
}

export const PAGE_ACTIVITE = '/mon-activite'

const estDans = (chemin: string, vers: string) => chemin === vers || chemin.startsWith(`${vers}/`)
// Les pages rangées dans « Mon activité » : l'entrée « Mon activité » reste allumée sur elles
const PAGES_DE_L_ACTIVITE = [
  PAGE_ACTIVITE, '/mon-agenda', '/devis', '/factures', '/mes-clients', '/clients', '/mes-avis-recus', '/ma-carte-de-visite',
  '/demarches', '/creer-mon-auto-entreprise',
]
// Les pages du compte : « Moi » (barre du bas) reste allumé sur elles
const PAGES_DU_COMPTE = ['/moi', '/profil', '/mes-abonnements', '/parametres', '/administration']

export function useMenu() {
  const route = useRoute()
  const { compte } = useCompte()
  const estPrestataire = computed(() => !!compte.value?.prestataire_id)
  const estSur = (vers: string) => estDans(route.path, vers)

  const { nonLus } = useNonLus()
  const entrees = computed<EntreeMenu[]>(() => [
    { vers: '/', texte: 'Accueil', court: 'Accueil', icone: 'accueil', actif: route.path === '/' },
    { vers: '/trouver', texte: 'Trouver', court: 'Trouver', icone: 'trouver', actif: estSur('/trouver') || estSur('/prestataires') },
    { vers: '/demandes', texte: 'Demandes', court: 'Demandes', icone: 'demandes', actif: estSur('/demandes') },
    // Le compteur orange : nombre de conversations avec du nouveau
    ...(compte.value
      ? [
          { vers: '/messages', texte: 'Messages', court: 'Messages', icone: 'messages' as const, actif: estSur('/messages'), compteur: nonLus.value },
          { vers: PAGE_ACTIVITE, texte: 'Mon activité', court: 'Activité', icone: 'activite' as const, actif: PAGES_DE_L_ACTIVITE.some(estSur) },
        ]
      : []),
  ])
  // Téléphone : les mêmes entrées + « Moi » (la page du compte) ; sans compte, elles mènent à « Se connecter »
  const entreesBas = computed<EntreeMenu[]>(() => {
    const connecte = !!compte.value
    const toutes: EntreeMenu[] = connecte
      ? entrees.value
      : [
          ...entrees.value,
          { vers: '/connexion', texte: 'Messages', court: 'Messages', icone: 'messages', actif: false },
          { vers: '/connexion', texte: 'Mon activité', court: 'Activité', icone: 'activite', actif: false },
        ]
    return [...toutes, { vers: connecte ? '/moi' : '/connexion', texte: 'Moi', court: 'Moi', icone: 'moi', actif: PAGES_DU_COMPTE.some(estSur) || estSur('/connexion') }]
  })

  return { estPrestataire, estSur, entrees, entreesBas }
}
