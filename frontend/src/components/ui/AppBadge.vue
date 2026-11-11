<script setup lang="ts">
// Étiquette d'état : la « puce » de la grande maquette (vert, orange, rouge, gris ; « accent » : orange pâle).
withDefaults(defineProps<{ etat?: 'ok' | 'attente' | 'erreur' | 'neutre' | 'accent' }>(), { etat: 'neutre' })

const classesEtat: Record<string, string> = { ok: 'p-ok', attente: 'p-att', erreur: 'p-err', neutre: 'p-neutre', accent: 'p-accent' }
</script>

<template>
  <span class="puce" :class="classesEtat[etat]"><slot /></span>
</template>
