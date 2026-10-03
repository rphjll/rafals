<script setup lang="ts" generic="V extends string | number">
// Cases collées pour basculer entre deux ou trois vues (ex. « 1 mois | 2 mois », « Coiffeuse | Maquilleuse »).
// À la différence d'AppChoix (réponse d'un formulaire), le clic change tout de suite ce qui est affiché.
defineProps<{ etiquette: string; options: { valeur: V; texte: string }[] }>()
const valeur = defineModel<V>({ required: true })
</script>

<template>
  <div class="inline-flex flex-wrap overflow-hidden rounded-rafals border border-primaire" role="group" :aria-label="etiquette">
    <button
      v-for="option in options"
      :key="option.valeur"
      type="button"
      :aria-pressed="valeur === option.valeur"
      class="min-h-[42px] px-3.5 py-2 font-semibold outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-inset"
      :class="valeur === option.valeur ? 'bg-primaire text-primaire-texte' : 'bg-surface text-primaire hover:bg-primaire-doux'"
      @click="valeur = option.valeur"
    >
      {{ option.texte }}
    </button>
  </div>
</template>
