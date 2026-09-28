<script setup lang="ts">
// Liste déroulante : étiquette au-dessus, astérisque si obligatoire (CONVENTIONS-IHM).
import { useId } from 'vue'

withDefaults(
  defineProps<{ etiquette: string; options: { valeur: number; texte: string }[]; obligatoire?: boolean; vide?: string }>(),
  { obligatoire: false, vide: 'Choisir…' },
)
const valeur = defineModel<number | null>({ default: null })
const id = useId()
</script>

<template>
  <div class="flex flex-col gap-1.5">
    <label :for="id" class="text-[13px] font-semibold">
      {{ etiquette }}<span v-if="obligatoire" class="text-erreur" aria-hidden="true"> *</span>
    </label>
    <select
      :id="id"
      v-model="valeur"
      :required="obligatoire"
      class="min-h-[42px] rounded-rafals border border-bord bg-fond px-3 py-2.5 text-texte outline-none focus:border-primaire focus:ring-2 focus:ring-primaire"
    >
      <option :value="null" disabled>{{ vide }}</option>
      <option v-for="option in options" :key="option.valeur" :value="option.valeur">{{ option.texte }}</option>
    </select>
  </div>
</template>
