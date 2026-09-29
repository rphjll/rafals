<script setup lang="ts">
// Case à cocher avec son texte (zone cliquable de 42 px de haut). Verrouillée : 🔒 et la raison dessous.
defineProps<{ texte: string; raisonVerrou?: string }>()
const cochee = defineModel<boolean>({ default: false })
</script>

<template>
  <div class="flex flex-col gap-1">
    <label
      class="flex min-h-[42px] items-center gap-2.5 text-[14.5px] font-medium"
      :class="raisonVerrou ? 'cursor-not-allowed text-texte-doux' : 'cursor-pointer'"
    >
      <input v-model="cochee" type="checkbox" :disabled="!!raisonVerrou" class="size-5 accent-primaire" />
      <span><span v-if="raisonVerrou" aria-hidden="true">🔒 </span>{{ texte }}</span>
    </label>
    <p v-if="raisonVerrou" class="text-[13px] text-texte-doux">{{ raisonVerrou }}</p>
  </div>
</template>
