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
  <div class="champ">
    <label :for="id">
      {{ etiquette }}<span v-if="obligatoire" class="text-erreur" aria-hidden="true"> *</span>
    </label>
    <select
      :id="id"
      v-model="valeur"
      :required="obligatoire"
    >
      <option :value="null" disabled>{{ vide }}</option>
      <option v-for="option in options" :key="option.valeur" :value="option.valeur">{{ option.texte }}</option>
    </select>
  </div>
</template>
