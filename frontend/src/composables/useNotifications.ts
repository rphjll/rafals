// Notifications sur ce téléphone ou cet ordinateur (RM-ALERTES.md, RM-APPLICATION.md ; lot 8.7).
// Chaque appareil donne son accord séparément : le navigateur fabrique une adresse d'envoi, rafals la garde
// (table APPAREIL) et y envoie « Nouvelle demande : Fuite sous l'évier, Talence (5 km) ».
// États possibles du bouton :
//   'impossible'  : ce navigateur ne sait pas recevoir de notifications (ex. iPhone sans rafals installé)
//   'pas-branche' : rafals n'a pas encore ses clés (.env) : bouton verrouillé
//   'refuse'      : la personne a cliqué « Bloquer » dans le navigateur : seul le navigateur peut le défaire
//   'inactif' / 'actif'
import { ref } from 'vue'
import { appelerServeur } from '../api'

export type EtatNotifications = 'chargement' | 'impossible' | 'pas-branche' | 'refuse' | 'inactif' | 'actif'

const possible = 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window

/** La clé publique de rafals (texte en base64 « url ») en octets, comme le navigateur la demande */
function enOctets(cle: string): Uint8Array<ArrayBuffer> {
  const base64 = (cle + '='.repeat((4 - (cle.length % 4)) % 4)).replace(/-/g, '+').replace(/_/g, '/')
  return Uint8Array.from(atob(base64), (c) => c.charCodeAt(0))
}

async function abonnementActuel(): Promise<PushSubscription | null> {
  if (!possible) return null
  const enregistrement = await navigator.serviceWorker.ready
  return enregistrement.pushManager.getSubscription()
}

/** Avant la déconnexion : cet appareil ne reçoit plus rien pour ce compte (RM-APPLICATION.md) */
export async function couperAvantDeconnexion(): Promise<void> {
  try {
    const abonnement = await abonnementActuel()
    if (!abonnement) return
    await appelerServeur('/api/moi/appareils/couper', { adresse: abonnement.endpoint })
    await abonnement.unsubscribe()
  } catch {
    // pas de réseau : la déconnexion se fait quand même
  }
}

export function useNotifications() {
  const etat = ref<EtatNotifications>('chargement')

  async function charger() {
    if (!possible) {
      etat.value = 'impossible'
      return
    }
    const { cle } = await appelerServeur<{ cle: string | null }>('/api/notifications/cle')
    if (!cle) etat.value = 'pas-branche'
    else if (Notification.permission === 'denied') etat.value = 'refuse'
    else {
      const abonnement = await abonnementActuel()
      const actif = abonnement
        ? (await appelerServeur<{ active: boolean }>('/api/moi/appareils/etat', { adresse: abonnement.endpoint })).active
        : false
      etat.value = actif ? 'actif' : 'inactif'
    }
  }

  /** Le navigateur demande « Autoriser / Bloquer » ; rend le message à afficher */
  async function activer(): Promise<string> {
    const { cle } = await appelerServeur<{ cle: string | null }>('/api/notifications/cle')
    if (!cle) throw new Error('Les notifications ne sont pas encore branchées sur rafals.')
    if ((await Notification.requestPermission()) !== 'granted') {
      etat.value = 'refuse'
      throw new Error('Vous avez refusé les notifications dans le navigateur : rien n’est activé.')
    }
    const enregistrement = await navigator.serviceWorker.ready
    const abonnement =
      (await enregistrement.pushManager.getSubscription()) ??
      (await enregistrement.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: enOctets(cle) }))
    const cles = abonnement.toJSON().keys ?? {}
    const { message } = await appelerServeur<{ message: string }>('/api/moi/appareils', {
      adresse: abonnement.endpoint,
      cle_publique: cles.p256dh ?? '',
      cle_secrete: cles.auth ?? '',
    })
    etat.value = 'actif'
    return message
  }

  async function couper(): Promise<string> {
    const abonnement = await abonnementActuel()
    let message = 'Notifications coupées sur cet appareil.'
    if (abonnement) {
      message = (await appelerServeur<{ message: string }>('/api/moi/appareils/couper', { adresse: abonnement.endpoint })).message
      await abonnement.unsubscribe()
    }
    etat.value = 'inactif'
    return message
  }

  return { etat, charger, activer, couper }
}
