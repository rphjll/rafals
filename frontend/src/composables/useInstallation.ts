// Installer rafals sur l'appareil (RM-APPLICATION.md) : le bouton [Installer rafals] du menu du compte.
// - Android, ordinateur (Chrome, Edge) : le navigateur prévient qu'il sait installer ; le bouton ouvre sa fenêtre.
// - iPhone, iPad : le navigateur ne sait pas le faire tout seul ; le bouton explique les deux gestes à faire.
// - Déjà installée (ouverte comme une application) : pas de bouton.
import { computed, ref } from 'vue'

// L'événement du navigateur « je peux installer ce site » (il n'est pas décrit dans les types de TypeScript)
interface InvitationInstallation extends Event {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

const invitation = ref<InvitationInstallation | null>(null)
const installee = ref(
  window.matchMedia('(display-mode: standalone)').matches || (navigator as Navigator & { standalone?: boolean }).standalone === true,
)
const surApple = /iphone|ipad|ipod/i.test(navigator.userAgent)

window.addEventListener('beforeinstallprompt', (evenement) => {
  evenement.preventDefault() // on garde l'invitation pour notre bouton, au lieu de la bannière du navigateur
  invitation.value = evenement as InvitationInstallation
})
window.addEventListener('appinstalled', () => {
  installee.value = true
  invitation.value = null
})

export function useInstallation() {
  /** 'navigateur' : un clic installe ; 'apple' : il faut montrer les gestes ; null : pas de bouton */
  const facon = computed<'navigateur' | 'apple' | null>(() => {
    if (installee.value) return null
    if (invitation.value) return 'navigateur'
    return surApple ? 'apple' : null
  })

  /** Ouvre la fenêtre d'installation du navigateur ; rend vrai si la personne a accepté */
  async function installer(): Promise<boolean> {
    const demande = invitation.value
    if (!demande) return false
    await demande.prompt()
    const { outcome } = await demande.userChoice
    invitation.value = null
    return outcome === 'accepted'
  }

  return { facon, installer }
}
