<script setup lang="ts">
// Affiche le message court de useMessage(). Placé une seule fois, dans App.vue.
import { useMessage } from '../../composables/useMessage'

const { texte, etat } = useMessage()
</script>

<template>
  <div
    v-if="texte"
    role="status"
    class="fixed bottom-[calc(20px+env(safe-area-inset-bottom,0px))] left-1/2 z-30 -translate-x-1/2 rounded-rafals px-[18px] py-3 font-semibold text-sur-etat"
    :class="etat === 'ok' ? 'bg-ok' : 'bg-erreur'"
  >
    {{ texte }}
  </div>
</template>
