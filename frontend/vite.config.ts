import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  server: {
    // Sous Windows, Docker ne voit pas toujours les fichiers modifiés : on les surveille en boucle
    watch: { usePolling: true },
    // Les adresses /api partent vers la boîte « backend »
    proxy: { '/api': 'http://backend:8000' },
  },
})
