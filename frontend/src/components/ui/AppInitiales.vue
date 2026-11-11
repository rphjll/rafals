<script setup lang="ts">
// Rond d'une personne sans photo (grande maquette, classe « av ») : couleur pleine propre à son nom, première lettre
// en blanc. La même partout (accueil, messages, mes clients, recherche, en-tête). Ex. « Marie D. » → « M » sur rose.
// « taille » : classes de taille et de texte (par défaut 36 px, comme la maquette).
import { computed } from 'vue'
import { couleurDe } from '../../outils/noms'

const props = withDefaults(defineProps<{ nom: string; taille?: string }>(), { taille: '' })
const lettre = computed(() => props.nom.replace(/^ZZTEST\s+/, '').trim()[0]?.toUpperCase() ?? '?')
</script>

<template>
  <span class="av" :class="taille" :style="{ background: couleurDe(nom) }" aria-hidden="true">{{ lettre }}</span>
</template>
