import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  server: {
    // Sous Windows, Docker ne voit pas toujours les fichiers modifiés : on les surveille en boucle.
    // Une fois par seconde (au lieu de 10 fois par seconde par défaut) : Vite prenait 40 % du processeur au repos.
    watch: { usePolling: true, interval: 1000, binaryInterval: 3000 },
    // Les adresses /api partent vers la boîte « backend »
    proxy: { '/api': 'http://backend:8000' },
  },
})
