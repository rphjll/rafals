// Petit programme de l'application installée (un « service worker », RM-APPLICATION.md).
// 1) Quand une page ne peut pas être chargée faute de réseau, montrer « Pas de connexion ». 2) Afficher les notifications.
// Rien d'autre n'est gardé sur l'appareil : ni messages, ni adresses, ni pages du site.
const CACHE = 'rafals-hors-ligne-1'
const PAGE = '/hors-ligne.html'

self.addEventListener('install', (evenement) => {
  evenement.waitUntil(caches.open(CACHE).then((cache) => cache.add(PAGE)).then(() => self.skipWaiting()))
})

self.addEventListener('activate', (evenement) => {
  // Les anciennes versions de la page « Pas de connexion » sont effacées
  evenement.waitUntil(
    caches.keys().then((noms) => Promise.all(noms.filter((nom) => nom !== CACHE).map((nom) => caches.delete(nom)))).then(() => self.clients.claim()),
  )
})

self.addEventListener('fetch', (evenement) => {
  // Seulement l'ouverture d'une page : les appels au serveur (/api) et les fichiers passent sans y toucher
  if (evenement.request.mode !== 'navigate') return
  evenement.respondWith(fetch(evenement.request).catch(() => caches.match(PAGE)))
})

// Notifications (lot 8.7, RM-ALERTES.md) : rafals envoie { titre, texte, lien } ; un clic ouvre le bon écran
self.addEventListener('push', (evenement) => {
  let donnees = { titre: 'rafals', texte: 'Du nouveau sur rafals', lien: '/' }
  try {
    donnees = { ...donnees, ...evenement.data.json() }
  } catch {
    // message vide ou illisible : le texte par défaut
  }
  evenement.waitUntil(
    self.registration.showNotification(donnees.titre, { body: donnees.texte, icon: '/icone-192.png', badge: '/icone-192.png', data: { lien: donnees.lien } }),
  )
})

self.addEventListener('notificationclick', (evenement) => {
  evenement.notification.close()
  const lien = new URL(evenement.notification.data?.lien ?? '/', self.location.origin).href
  evenement.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((fenetres) => {
      // rafals déjà ouvert : on y va ; sinon une nouvelle fenêtre
      const ouverte = fenetres.find((f) => new URL(f.url).origin === self.location.origin)
      return ouverte ? ouverte.focus().then(() => ouverte.navigate(lien)) : self.clients.openWindow(lien)
    }),
  )
})
