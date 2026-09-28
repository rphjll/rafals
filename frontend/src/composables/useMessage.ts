// Message court après une action (« Rendez-vous confirmé »), visible 3 secondes en bas de l'écran.
// Un seul message à la fois pour toute l'application, affiché par AppMessage (placé dans App.vue).
import { ref } from 'vue'

type EtatMessage = 'ok' | 'erreur'

const texte = ref('')
const etat = ref<EtatMessage>('ok')
let minuteur: ReturnType<typeof setTimeout> | undefined

export function useMessage() {
  function afficherMessage(nouveauTexte: string, nouvelEtat: EtatMessage = 'ok') {
    texte.value = nouveauTexte
    etat.value = nouvelEtat
    clearTimeout(minuteur)
    minuteur = setTimeout(() => (texte.value = ''), 3000)
  }
  return { texte, etat, afficherMessage }
}
