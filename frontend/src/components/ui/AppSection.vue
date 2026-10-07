<script setup lang="ts">
// Bloc d'une page : fond blanc, bord, titre ; bouton facultatif à droite du titre (slot « action »).
// « danger » : bord rouge, pour une action définitive (ex. Fermer mon compte).
withDefaults(defineProps<{ titre?: string; danger?: boolean }>(), { titre: '', danger: false })
</script>

<template>
  <section
    class="carte flex flex-col gap-3.5 p-5"
    :class="danger ? 'border-erreur' : ''"
  >
    <div v-if="titre || $slots.action" class="flex flex-wrap items-center justify-between gap-2.5">
      <h2 class="text-xl font-bold">{{ titre }}</h2>
      <slot name="action" />
    </div>
    <slot />
  </section>
</template>
