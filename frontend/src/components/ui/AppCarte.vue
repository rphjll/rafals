<script setup lang="ts">
// Carte centrée pour les formulaires courts (inscription, connexion…) : titre, texte d'intro, contenu (grande maquette).
defineProps<{ titre: string; intro?: string }>()
</script>

<template>
  <!-- Comme « Se connecter » dans la grande maquette : titre centré, puis le formulaire dans une carte de 420 px -->
  <div class="connexion page">
    <div class="tete" style="text-align: center">
      <h1>{{ titre }}</h1>
      <p v-if="intro">{{ intro }}</p>
    </div>
    <section class="carte form p-[18px]"><slot /></section>
  </div>
</template>
