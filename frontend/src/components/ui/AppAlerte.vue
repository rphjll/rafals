<script setup lang="ts">
// Bandeau d'information posé là où l'utilisateur regarde (ex. l'erreur du serveur juste au-dessus du bouton) :
// le « bandeau » de la grande maquette. « neutre » : une simple explication (ex. paiement par carte, lot 5.2).
withDefaults(defineProps<{ etat?: 'ok' | 'attente' | 'erreur' | 'neutre' }>(), { etat: 'erreur' })
const classesEtat: Record<string, string> = { ok: 'b-ok', attente: 'b-att', erreur: 'b-err', neutre: 'b-neutre' }
</script>

<template>
  <div :role="etat === 'erreur' ? 'alert' : 'status'" class="bandeau flex-row! flex flex-wrap items-center gap-3" :class="classesEtat[etat]">
    <slot />
  </div>
</template>
