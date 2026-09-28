import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    // Sous Windows, Docker ne voit pas toujours les fichiers modifiés : on les surveille en boucle
    watch: { usePolling: true },
    // Les adresses /api partent vers la boîte « backend »
    proxy: { '/api': 'http://backend:8000' },
  },
})
