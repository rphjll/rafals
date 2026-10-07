<script setup lang="ts">
// Photo ronde d'un prestataire, ou ses initiales s'il n'en a pas (« Karim Benali » → « KB ») :
// Mon activité, résultats de recherche, page publique.
import { computed } from 'vue'
import { initialesDe } from '../../outils/noms'

const props = withDefaults(
  defineProps<{ id: number; nom: string; aUnePhoto: boolean; taille?: 'petite' | 'moyenne' | 'grande'; version?: number }>(),
  { taille: 'petite', version: 0 },
)
const initiales = computed(() => initialesDe(props.nom))
// « moyenne » : les petites cartes des résultats de recherche
const TAILLES = { petite: 'size-14 text-lg sm:size-16', moyenne: 'size-[92px] text-[28px]', grande: 'size-24 text-3xl' }
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
  <div
    v-else
    class="grid shrink-0 place-items-center rounded-full bg-primaire-doux font-bold text-primaire"
    :class="classeTaille"
    aria-hidden="true"
  >
    {{ initiales }}
  </div>
</template>
