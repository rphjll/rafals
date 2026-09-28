<script setup lang="ts">
// Page d'attente pour les entrées du menu pas encore construites (.doc/ihm/RM-ACCUEIL-IHM.md).
import { useRouter } from 'vue-router'
import AppBouton from '../components/ui/AppBouton.vue'

defineProps<{ titre: string; arrivee: string }>()
const routeur = useRouter()
</script>

<template>
  <section class="flex flex-col items-start gap-4 py-6">
    <h1 class="text-[28px] font-bold">{{ titre }}</h1>
    <p v-if="arrivee" class="text-texte-doux">Cette page arrive {{ arrivee }}.</p>
    <p v-else class="text-texte-doux">Cette adresse ne correspond à aucune page de rafals.</p>
    <AppBouton @click="routeur.push('/')">Retour à l'accueil</AppBouton>
  </section>
</template>
