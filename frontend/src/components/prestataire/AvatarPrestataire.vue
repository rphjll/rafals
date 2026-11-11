<script setup lang="ts">
// Photo ronde d'un prestataire, ou ses initiales s'il n'en a pas (« Karim Benali » → « KB ») :
// Mon activité, résultats de recherche, page publique.
import { computed } from 'vue'
import AppInitiales from '../ui/AppInitiales.vue'

const props = withDefaults(
  defineProps<{ id: number; nom: string; aUnePhoto: boolean; taille?: 'mini' | 'petite' | 'moyenne' | 'grande'; version?: number }>(),
  { taille: 'petite', version: 0 },
)
// « mini » : 36 px, le rond de la grande maquette (cartes des prestataires) ; « moyenne » : anciennes cartes
const TAILLES = { mini: 'size-9 text-[15px]', petite: 'size-14 text-lg sm:size-16', moyenne: 'size-[92px] text-[28px]', grande: 'size-24 text-3xl' }
const classeTaille = computed(() => TAILLES[props.taille])
</script>

<template>
  <img
    v-if="aUnePhoto"
    :src="`/api/prestataires/${id}/photo${version ? `?v=${version}` : ''}`"
    :alt="`Photo de ${nom}`"
    class="shrink-0 rounded-full object-cover"
    :class="classeTaille"
  />
  <AppInitiales v-else :nom="nom" :taille="classeTaille" />
</template>
