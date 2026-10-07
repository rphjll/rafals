// Le compteur rouge de l'entrée « Messages » : nombre de conversations avec du nouveau (RM-MESSAGERIE.md).
// Relu toutes les minutes, et dès qu'on ouvre une conversation.
import { ref } from 'vue'
import { appelerServeur } from '../api'
import { useCompte } from './useCompte'

const nonLus = ref(0)
let minuteur: ReturnType<typeof setInterval> | undefined

async function actualiserNonLus() {
  const { compte } = useCompte()
  if (!compte.value) {
    nonLus.value = 0
    return
  }
  try {
    nonLus.value = (await appelerServeur<{ nombre: number }>('/api/moi/conversations/non-lues')).nombre
  } catch {
    // serveur injoignable : on garde le dernier nombre connu
  }
}

export function useNonLus() {
  if (minuteur === undefined) minuteur = setInterval(() => document.visibilityState === 'visible' && actualiserNonLus(), 60000)
  return { nonLus, actualiserNonLus }
}
