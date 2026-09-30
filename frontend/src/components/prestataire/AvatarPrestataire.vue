<script setup lang="ts">
// Photo ronde d'un prestataire, ou ses initiales s'il n'en a pas (« Karim Benali » → « KB ») :
// Mon activité, résultats de recherche, page publique.
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{ id: number; nom: string; aUnePhoto: boolean; taille?: 'petite' | 'grande'; version?: number }>(),
  { taille: 'petite', version: 0 },
)
const initiales = computed(() =>
  props.nom
    .replace(/^ZZTEST\s+/, '')
    .split(/\s+/)
    .slice(0, 2)
    .map((mot) => mot[0]?.toUpperCase() ?? '')
    .join(''),
)
const classeTaille = computed(() => (props.taille === 'grande' ? 'size-24 text-3xl' : 'size-14 text-lg sm:size-16'))
</script>

<template>
  <img
    v-if="aUnePhoto"
    :src="`/api/prestataires/${id}/photo${version ? `?v=${version}` : ''}`"
    :alt="`Photo de ${nom}`"
    class="shrink-0 rounded-full object-cover"
    :class="classeTaille"
  />
  <div
    v-else
    class="grid shrink-0 place-items-center rounded-full bg-primaire-doux font-bold text-primaire"
    :class="classeTaille"
    aria-hidden="true"
  >
    {{ initiales }}
  </div>
</template>
