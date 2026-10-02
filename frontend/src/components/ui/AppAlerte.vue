<script setup lang="ts">
// Bandeau d'information posé là où l'utilisateur regarde (ex. l'erreur du serveur juste au-dessus du bouton).
// « neutre » : une simple explication (ex. ce qui se passe si l'on paie par carte, lot 5.2).
withDefaults(defineProps<{ etat?: 'ok' | 'attente' | 'erreur' | 'neutre' }>(), { etat: 'erreur' })

const classesEtat: Record<string, string> = {
  ok: 'bg-ok-doux text-ok',
  attente: 'bg-attente-doux text-attente',
  erreur: 'bg-erreur-doux text-erreur',
  neutre: 'bg-neutre-doux text-texte',
}
</script>

<template>
  <div
    :role="etat === 'erreur' ? 'alert' : 'status'"
    class="flex flex-wrap items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium"
    :class="classesEtat[etat]"
  >
    <slot />
  </div>
</template>
