// [Écrire à Julie], côté prestataire (« Mes clients », profil d'un client) : ouvre la conversation avec ce client,
// ou la retrouve si elle existe déjà. Le serveur refuse si ce n'est pas un de ses clients ou si elle est bloquée.
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'

export function useEcrireAuClient() {
  const routeur = useRouter()
  // Le client auquel on est en train d'écrire (son bouton ne réagit plus) et l'erreur à montrer sous sa ligne
  const enCours = ref<number | null>(null)
  const erreurEcrire = ref<{ clientId: number; texte: string } | null>(null)

  async function ecrire(clientId: number) {
    erreurEcrire.value = null
    enCours.value = clientId
    try {
      const conversation = await appelerServeur<{ id: number }>('/api/conversations', { client_id: clientId })
      routeur.push(`/messages/${conversation.id}`)
    } catch (e) {
      erreurEcrire.value = { clientId, texte: messageErreur(e) }
    } finally {
      enCours.value = null
    }
  }

  return { enCours, erreurEcrire, ecrire }
}
