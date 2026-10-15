// La personne connectée, partagée par toutes les pages (null = personne n'est connecté).
import { ref } from 'vue'
import { appelerServeur } from '../api'
import { couperAvantDeconnexion } from './useNotifications'

export interface CompteVisible {
  id: number
  email: string
  prenom: string
  nom: string
  telephone: string | null
  date_naissance: string | null
  email_verifie: boolean
  est_administrateur: boolean
  accord_parental_necessaire: boolean
  peut_reserver_ou_publier: boolean
  prestataire_id: number | null
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
    await couperAvantDeconnexion() // cet appareil ne reçoit plus rien pour ce compte (RM-APPLICATION.md)
    await appelerServeur('/api/deconnexion', {})
    compte.value = null
  }

  /** Renvoie le lien de vérification d'adresse ; renvoie le message du serveur à afficher. */
  async function renvoyerLienVerification(email: string): Promise<string> {
    return (await appelerServeur<{ message: string }>('/api/comptes/verification/renvoi', { email })).message
  }

  return { compte, chargementFait, chargerCompte, seConnecter, seDeconnecter, renvoyerLienVerification }
}
