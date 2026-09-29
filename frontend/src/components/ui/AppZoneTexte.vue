<script setup lang="ts">
// Zone de texte sur plusieurs lignes, avec compteur de caractères (ex. présentation du prestataire).
import { useId } from 'vue'

withDefaults(defineProps<{ etiquette: string; maximum: number; aide?: string; obligatoire?: boolean }>(), {
  aide: '',
  obligatoire: false,
})
const valeur = defineModel<string>({ default: '' })
const id = useId()
</script>

<template>
  <div class="flex flex-col gap-1.5">
    <label :for="id" class="text-[13px] font-semibold">
      {{ etiquette }}<span v-if="obligatoire" class="text-erreur" aria-hidden="true"> *</span>
    </label>
    <textarea
      :id="id"
      v-model="valeur"
      rows="5"
      class="min-h-[110px] resize-y rounded-rafals border border-bord bg-fond px-3 py-2.5 text-texte outline-none focus:border-primaire focus:ring-2 focus:ring-primaire"
    />
    <p class="flex justify-between gap-3 text-[13px] text-texte-doux">
      <span>{{ aide }}</span>
      <span :class="valeur.length > maximum ? 'font-semibold text-erreur' : ''">{{ valeur.length }} / {{ maximum }}</span>
    </p>
  </div>
</template>
