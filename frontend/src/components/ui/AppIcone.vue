<script setup lang="ts">
// Icône au trait de la grande maquette (.doc/ihm/maquette-site-complet.html, « Icônes ») : 22 px, couleur du texte.
// La taille se change par une classe (ex. class="size-4"). Tracés : outils/icones.ts.
import { computed } from 'vue'
import { ICONES, type NomIcone } from '../../outils/icones'

const props = defineProps<{ nom: NomIcone }>()
const trace = computed(() => ICONES[props.nom])
</script>

<template>
  <!-- eslint-disable-next-line vue/no-v-html -- tracés fixes écrits dans outils/icones.ts, jamais venus d'un utilisateur -->
  <svg class="i" viewBox="0 0 24 24" aria-hidden="true" v-html="trace" />
</template>
