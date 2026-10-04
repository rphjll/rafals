<script setup lang="ts">
// Le fil des 5 étapes du dossier de création (.doc/ihm/RM-CREATION-AUTO-ENTREPRISE-IHM.md) : l'étape en cours en vert,
// les étapes finies avec ✓. Un clic sur une étape y mène.
import { NOMS_ETAPES } from '../../outils/creation'

defineProps<{ etape: number; faites: boolean[] }>()
const emit = defineEmits<{ aller: [etape: number] }>()
</script>

<template>
  <ol class="flex flex-wrap gap-1.5 text-[13px]">
    <li v-for="(nom, rang) in NOMS_ETAPES" :key="nom">
      <button
        type="button"
        class="flex min-h-[36px] items-center gap-1.5 rounded-full border bg-surface py-1 pr-3 pl-1"
        :class="rang + 1 === etape ? 'border-primaire font-bold text-primaire' : 'border-bord text-texte-doux hover:border-primaire'"
        :aria-current="rang + 1 === etape ? 'step' : undefined"
        @click="emit('aller', rang + 1)"
      >
        <b
          class="grid h-6 w-6 place-items-center rounded-full text-[12px]"
          :class="rang + 1 === etape ? 'bg-primaire text-primaire-texte' : faites[rang] ? 'bg-ok-doux text-ok' : 'bg-neutre-doux text-neutre'"
        >
          {{ faites[rang] && rang + 1 !== etape ? '✓' : rang + 1 }}
        </b>
        {{ nom }}
      </button>
    </li>
  </ol>
</template>
