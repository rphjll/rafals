<script setup lang="ts">
// Carte centrée pour les formulaires courts (inscription, connexion…) : titre, texte d'intro, contenu.
defineProps<{ titre: string; intro?: string }>()
</script>

<template>
  <section class="mx-auto flex w-full max-w-[460px] flex-col gap-4 rounded-rafals border border-bord bg-surface p-6">
    <h1 class="text-[26px] font-bold">{{ titre }}</h1>
    <p v-if="intro" class="-mt-2 text-texte-doux">{{ intro }}</p>
    <slot />
  </section>
</template>
