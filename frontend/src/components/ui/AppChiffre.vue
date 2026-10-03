<script setup lang="ts">
// Un chiffre mis en avant : petit titre, grande valeur, détail facultatif dessous (ex. « Versé en octobre »,
// « 46,50 € », « 1 rendez-vous »). Utilisé par Mon agenda › Paiements et par le tableau de bord de l'administration.
defineProps<{ titre: string; valeur: string; detail?: string }>()
</script>

<template>
  <div class="rounded-rafals bg-fond px-3 py-2.5">
    <span class="text-[13.5px] text-texte-doux">{{ titre }}</span>
    <b class="block text-[22px] tabular-nums">{{ valeur }}</b>
    <span v-if="detail" class="text-[13.5px] text-texte-doux">{{ detail }}</span>
  </div>
</template>
