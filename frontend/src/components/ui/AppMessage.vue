<script setup lang="ts">
// Affiche le message court de useMessage(), comme le « toast » de la grande maquette : foncé avec ✓ en bas de
// l'écran (rouge pour une erreur). Placé une seule fois, dans App.vue.
import { useMessage } from '../../composables/useMessage'
import AppIcone from './AppIcone.vue'

const { texte, etat } = useMessage()
</script>

<template>
  <div v-if="texte" role="status" class="toast vu" :style="etat === 'ok' ? undefined : { background: 'var(--erreur)', color: '#fff' }">
    <AppIcone v-if="etat === 'ok'" nom="ok" />{{ texte }}
  </div>
</template>
