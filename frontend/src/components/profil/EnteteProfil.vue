<script setup lang="ts">
// Haut de « Mon profil », façon Instagram (21/10/2026) : la photo ronde (slot « photo »), les chiffres à côté
// (ex. « 8 photos · 4,8 ★ 23 avis · 12 abonnés · 4 abonnements »), puis le nom, la présentation (slot) et les boutons.
import type { ChiffreProfil } from '../../outils/profil'

defineProps<{ nom: string; chiffres: ChiffreProfil[] }>()
</script>

<template>
  <div class="flex flex-col gap-3 px-5 pt-6 max-sm:px-4 max-sm:pt-5">
    <div class="grid grid-cols-[auto_1fr] items-center gap-5 max-sm:gap-3.5">
      <slot name="photo" />
      <dl class="grid grid-cols-[repeat(auto-fit,minmax(64px,1fr))] gap-1 text-center">
        <div v-for="c in chiffres" :key="c.texte" class="flex flex-col-reverse">
          <dt class="text-[13px] text-texte-doux max-sm:text-[12px]">{{ c.texte }}</dt>
          <dd class="text-xl font-black tabular-nums max-sm:text-[17px]">{{ c.valeur }}</dd>
        </div>
      </dl>
    </div>
    <div class="flex flex-col gap-1">
      <div class="flex flex-wrap items-center gap-2">
        <h1 class="text-[19px] font-black">{{ nom }}</h1>
        <slot name="badges" />
      </div>
      <slot />
    </div>
    <div class="grid grid-cols-2 gap-2 sm:flex sm:flex-wrap [&>*:last-child:nth-child(odd)]:max-sm:col-span-2">
      <slot name="boutons" />
    </div>
  </div>
</template>
