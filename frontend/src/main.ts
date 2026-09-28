import { createApp } from 'vue'
import '@fontsource-variable/bricolage-grotesque'
import '@fontsource-variable/figtree'
import './style.css'
import App from './App.vue'
import { routeur } from './router'

createApp(App).use(routeur).mount('#app')
