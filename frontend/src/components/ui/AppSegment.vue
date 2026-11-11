<script setup lang="ts" generic="V extends string | number">
// Cases collées pour basculer entre deux ou trois vues (ex. « 1 mois | 2 mois », « Clair | Sombre ») : le « seg » de
// la grande maquette (fond gris clair, case choisie blanche). « enLigne » : cases à la largeur de leur texte.
// À la différence d'AppChoix (réponse d'un formulaire), le clic change tout de suite ce qui est affiché.
withDefaults(defineProps<{ etiquette: string; options: { valeur: V; texte: string }[]; enLigne?: boolean }>(), { enLigne: false })
const valeur = defineModel<V>({ required: true })
</script>

<template>
  <div class="seg" :class="{ 'seg-inline': enLigne }" role="group" :aria-label="etiquette">
    <button v-for="option in options" :key="option.valeur" type="button" :aria-pressed="valeur === option.valeur" @click="valeur = option.valeur">
      {{ option.texte }}
    </button>
  </div>
</template>
