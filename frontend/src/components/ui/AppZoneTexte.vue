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
  <div class="champ">
    <label :for="id">
      {{ etiquette }}<span v-if="obligatoire" class="text-erreur" aria-hidden="true"> *</span>
    </label>
    <textarea
      :id="id"
      v-model="valeur"
      rows="5"
    />
    <small class="flex justify-between gap-3">
      <span>{{ aide }}</span>
      <span :class="valeur.length > maximum ? 'font-semibold text-erreur' : ''">{{ valeur.length }} / {{ maximum }}</span>
    </small>
  </div>
</template>
