<script setup lang="ts">
// Bandeau vert d'un élément choisi dans une recherche : « ✓ Plombier (Maison & travaux) [Changer] ».
import AppBouton from './AppBouton.vue'

defineProps<{ texte: string; detail?: string }>()
const emit = defineEmits<{ changer: [] }>()
</script>

<template>
  <div class="flex flex-wrap items-center gap-2.5 rounded-rafals bg-ok-doux px-3 py-2.5 font-semibold text-ok">
    ✓ {{ texte }} <span v-if="detail" class="text-[13px] font-medium">({{ detail }})</span>
    <span class="ml-auto"><AppBouton variante="secondaire" @click="emit('changer')">Changer</AppBouton></span>
  </div>
</template>
