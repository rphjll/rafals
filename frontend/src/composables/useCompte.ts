// La personne connectée, partagée par toutes les pages (null = personne n'est connecté).
import { ref } from 'vue'
import { appelerServeur } from '../api'

export interface CompteVisible {
  id: number
  email: string
  prenom: string
  nom: string
  email_verifie: boolean
}

const compte = ref<CompteVisible | null>(null)
const chargementFait = ref(false)

export function useCompte() {
  async function chargerCompte() {
    try {
      compte.value = await appelerServeur<CompteVisible>('/api/moi')
    } catch {
      compte.value = null
    } finally {
      chargementFait.value = true
    }
  }

  async function seConnecter(email: string, motDePasse: string) {
    compte.value = await appelerServeur<CompteVisible>('/api/connexion', { email, mot_de_passe: motDePasse })
  }

  async function seDeconnecter() {
    await appelerServeur('/api/deconnexion', {})
    compte.value = null
  }

  return { compte, chargementFait, chargerCompte, seConnecter, seDeconnecter }
}
