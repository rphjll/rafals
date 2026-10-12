import { createApp } from 'vue'
import '@fontsource-variable/bricolage-grotesque'
import '@fontsource-variable/figtree'
import './style.css'
import App from './App.vue'
import { routeur } from './router'

createApp(App).use(routeur).mount('#app')

// Application à installer (RM-APPLICATION.md) : le petit programme qui montre « Pas de connexion » sans réseau
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => navigator.serviceWorker.register('/sw.js').catch(() => {}))
}
