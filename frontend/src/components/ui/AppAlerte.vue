<script setup lang="ts">
// Bandeau d'information posé là où l'utilisateur regarde (ex. l'erreur du serveur juste au-dessus du bouton).
withDefaults(defineProps<{ etat?: 'ok' | 'attente' | 'erreur' }>(), { etat: 'erreur' })

const classesEtat: Record<string, string> = {
  ok: 'bg-ok-doux text-ok',
  attente: 'bg-attente-doux text-attente',
  erreur: 'bg-erreur-doux text-erreur',
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
