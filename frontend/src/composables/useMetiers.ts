// Les dossiers de métiers, chargés une seule fois et partagés par tous les écrans.
import { ref } from 'vue'
import { appelerServeur } from '../api'

export interface MetierVisible {
  id: number
  code: string
  nom: string
  categorie: string
}

export interface Dossier {
  id: number
  code: string
  nom: string
  metiers: MetierVisible[]
}

const dossiers = ref<Dossier[]>([])
let chargement: Promise<void> | null = null

export function useMetiers() {
  function chargerDossiers(forcer = false): Promise<void> {
    if (!chargement || forcer) {
      chargement = appelerServeur<Dossier[]>('/api/metiers/dossiers').then((liste) => {
        dossiers.value = liste
      })
    }
    return chargement
  }

  function rechercher(texte: string): Promise<MetierVisible[]> {
    return appelerServeur<MetierVisible[]>(`/api/metiers/recherche?q=${encodeURIComponent(texte)}`)
  }

  return { dossiers, chargerDossiers, rechercher }
}
