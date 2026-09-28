<script setup lang="ts">
// Structure commune : l'en-tête en haut, la page en dessous, le message court par-dessus.
import AppEntete from './components/AppEntete.vue'
import AppMessage from './components/ui/AppMessage.vue'
</script>

<template>
  <div class="min-h-screen bg-fond text-texte">
    <AppEntete />
    <main class="px-4 pt-7 pb-16">
      <div class="mx-auto max-w-[1080px]">
        <RouterView />
      </div>
    </main>
    <AppMessage />
  </div>
</template>
