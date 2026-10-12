// Petit programme de l'application installée (un « service worker », RM-APPLICATION.md).
// Il ne fait qu'une chose : quand une page ne peut pas être chargée faute de réseau, montrer « Pas de connexion ».
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
