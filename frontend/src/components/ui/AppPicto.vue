<script setup lang="ts">
// Pictogramme au trait d'un dossier de métiers (tracés : outils/pictos.ts). Il prend la couleur du texte autour.
import { tracePicto } from '../../outils/pictos'

withDefaults(defineProps<{ code: string; taille?: number }>(), { taille: 28 })
</script>

<template>
  <svg
    :width="taille"
    :height="taille"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.9"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
    class="shrink-0"
  >
    <path :d="tracePicto(code)" />
  </svg>
</template>
