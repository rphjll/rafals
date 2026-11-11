// La fenêtre « Un problème ? Une idée ? » (lot 13.1) : une seule, posée dans l'en-tête, ouverte depuis la liste du
// compte (ordinateur) ou depuis la page « Moi » (téléphone).
import { ref } from 'vue'

const retourOuvert = ref(false)

export function useRetour() {
  return { retourOuvert }
}
