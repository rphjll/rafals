<script setup lang="ts">
// Structure commune, comme la grande maquette : l'en-tête en haut, la page dans une colonne centrée de 880 px
// (1100 px pour « Mon agenda », 680 px pour un profil ou une page publique), la barre du bas sur téléphone.
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppBarreBas from './components/AppBarreBas.vue'
import AppEntete from './components/AppEntete.vue'
import AppMessage from './components/ui/AppMessage.vue'
import { useCompte } from './composables/useCompte'

const { chargerCompte } = useCompte()
onMounted(chargerCompte)

const route = useRoute()
const largeur = computed(() => {
  if (route.name === 'mon-agenda' || route.name === 'administration') return 'large'
  if (route.name === 'profil' || route.name === 'prestataire' || route.name === 'connexion') return 'etroit'
  return ''
})
</script>

<template>
  <!-- Formes douces qui flottent derrière les pages (style dans style.css) -->
  <div class="deco" aria-hidden="true"><span class="d1" /><span class="d2" /><span class="d3" /><span class="d4" /></div>
  <AppEntete />
  <main class="colonne" :class="largeur">
    <!-- Chaque page pose elle-même la classe « page » (colonne de 22 px d'écart, petite entrée animée) -->
    <RouterView :key="route.path" />
  </main>
  <AppBarreBas />
  <AppMessage />
</template>
