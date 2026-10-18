// Thème clair ou sombre (RM-PARAMETRES-IHM.md), choisi dans « Paramètres ».
// Le choix est gardé dans l'appareil (navigateur), jamais dans la base : décision de Raphael du 17/10/2026.
// - 'auto' : comme le téléphone ou l'ordinateur (rien de gardé ; c'est le choix de départ)
// - 'clair' / 'sombre' : toujours ce thème sur cet appareil
// Le premier affichage est fait par index.html (même clé, même règle) ; ce fichier prend le relais ensuite.
import { ref } from 'vue'

export type ChoixTheme = 'auto' | 'clair' | 'sombre'

const CLE = 'rafals-theme'
const appareilSombre = window.matchMedia('(prefers-color-scheme: dark)')

function lireChoix(): ChoixTheme {
  try {
    const garde = localStorage.getItem(CLE)
    return garde === 'clair' || garde === 'sombre' ? garde : 'auto'
  } catch {
    return 'auto' // stockage refusé (navigation privée) : on suit l'appareil
  }
}

const choix = ref<ChoixTheme>(lireChoix())

function appliquer() {
  const sombre = choix.value === 'sombre' || (choix.value === 'auto' && appareilSombre.matches)
  document.documentElement.classList.toggle('sombre', sombre)
}
// En « Automatique », l'appareil qui passe en sombre le soir fait passer rafals en sombre aussitôt
appareilSombre.addEventListener('change', appliquer)

export function useTheme() {
  function choisirTheme(nouveau: ChoixTheme) {
    choix.value = nouveau
    try {
      if (nouveau === 'auto') localStorage.removeItem(CLE)
      else localStorage.setItem(CLE, nouveau)
    } catch {
      // stockage refusé : le thème change quand même, jusqu'à la fermeture de la page
    }
    appliquer()
  }
  return { choix, choisirTheme }
}
