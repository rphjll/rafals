<script setup lang="ts">
// Étiquette d'état : couleurs d'état de la charte (OK, en attente, erreur, neutre).
withDefaults(defineProps<{ etat?: 'ok' | 'attente' | 'erreur' | 'neutre' }>(), { etat: 'neutre' })

const classesEtat: Record<string, string> = {
  ok: 'bg-ok-doux text-ok',
  attente: 'bg-attente-doux text-attente',
  erreur: 'bg-erreur-doux text-erreur',
  neutre: 'bg-neutre-doux text-texte-doux',
}
</script>

<template>
  <span class="inline-block rounded-full px-2 py-[3px] text-xs font-semibold" :class="classesEtat[etat]">
    <slot />
  </span>
</template>
