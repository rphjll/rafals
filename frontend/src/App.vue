<script setup lang="ts">
// Structure commune : l'en-tête en haut, la page en dessous, le message court par-dessus.
import { onMounted, watchEffect } from 'vue'
import { useRoute } from 'vue-router'
import AppEntete from './components/AppEntete.vue'
import AppSousMenu from './components/AppSousMenu.vue'
import AppMessage from './components/ui/AppMessage.vue'
import { useCompte } from './composables/useCompte'

const { chargerCompte } = useCompte()
onMounted(chargerCompte)

// « Mon agenda » garde les formes d'avant (coins de 10 px, bordures, Figtree) : voir style.css, « style-classique »
const route = useRoute()
watchEffect(() => document.documentElement.classList.toggle('style-classique', route.name === 'mon-agenda'))
</script>

<template>
  <div class="min-h-screen bg-fond text-texte">
    <AppEntete />
    <AppSousMenu />
    <main class="px-4 pt-7 pb-16">
      <div class="mx-auto max-w-[1080px]">
        <RouterView />
      </div>
    </main>
    <AppMessage />
  </div>
</template>
