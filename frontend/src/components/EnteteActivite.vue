<script setup lang="ts">
// Haut d'une page rangée dans « Mon activité » (Devis, Factures, Mes clients…), comme la grande maquette : le lien
// « ‹ Mon activité », le titre, puis une phrase qui dit à quoi sert la page. Un bouton peut se poser à droite (slot).
import AppIcone from './ui/AppIcone.vue'

defineProps<{ titre: string; texte?: string }>()
</script>

<template>
  <RouterLink class="retour" to="/mon-activite"><AppIcone nom="retour" />Mon activité</RouterLink>
  <div class="section-titre" style="align-items: center; flex-wrap: wrap">
    <div class="tete">
      <h1>{{ titre }}</h1>
      <p v-if="texte">{{ texte }}</p>
    </div>
    <slot />
  </div>
</template>
