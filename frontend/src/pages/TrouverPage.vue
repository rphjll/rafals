<script setup lang="ts">
// Trouver un prestataire (.doc/ihm/RM-TROUVER-IHM.md) : pour l'instant, le choix du métier.
// La ville et les résultats arrivent avec la recherche (niveau 4).
import { ref } from 'vue'
import AppChoixMetier from '../components/AppChoixMetier.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import type { MetierVisible } from '../composables/useMetiers'

const metier = ref<MetierVisible | null>(null)
</script>

<template>
  <div class="flex flex-col gap-5">
    <h1 class="text-[28px] font-bold">Trouver un prestataire</h1>
    <section class="flex flex-col gap-3.5 rounded-rafals border border-bord bg-surface p-5">
      <h2 class="text-xl font-bold">Quel métier ?</h2>
      <AppChoixMetier v-model="metier" />
      <AppAlerte v-if="metier" etat="attente">
        La suite (votre ville, puis les prestataires près de chez vous) arrive bientôt.
      </AppAlerte>
    </section>
  </div>
</template>
