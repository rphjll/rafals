<script setup lang="ts">
// Numéros de page sous une longue liste : [‹ Précédente] [1] [2] [3] [Suivante ›], la page en cours en bouton principal.
// Rien n'est affiché s'il n'y a qu'une page.
import AppBouton from './AppBouton.vue'

defineProps<{ page: number; pages: number; etiquette: string }>()
const emit = defineEmits<{ aller: [numero: number] }>()
</script>

<template>
  <nav v-if="pages > 1" class="flex flex-wrap justify-center gap-1.5" :aria-label="etiquette">
    <AppBouton v-if="page > 1" variante="secondaire" @click="emit('aller', page - 1)">‹ Précédente</AppBouton>
    <AppBouton v-for="n in pages" :key="n" :variante="n === page ? 'principal' : 'secondaire'" @click="emit('aller', n)">
      {{ n }}
    </AppBouton>
    <AppBouton v-if="page < pages" variante="secondaire" @click="emit('aller', page + 1)">Suivante ›</AppBouton>
  </nav>
</template>
