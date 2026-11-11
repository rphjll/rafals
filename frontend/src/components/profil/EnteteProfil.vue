<script setup lang="ts">
// Haut de « Mon profil », façon Instagram (21/10/2026) : la photo ronde (slot « photo »), les chiffres à côté
// (ex. « 8 photos · 4,8 ★ 23 avis · 12 abonnés · 4 abonnements »), puis le nom, la présentation (slot) et les boutons.
import type { ChiffreProfil } from '../../outils/profil'

defineProps<{ nom: string; chiffres: ChiffreProfil[] }>()
</script>

<template>
  <div class="ig-haut">
    <slot name="photo" />
    <dl class="ig-chiffres">
      <div v-for="c in chiffres" :key="c.texte" class="flex-col-reverse!">
        <dt><small>{{ c.texte }}</small></dt>
        <dd class="m-0"><b>{{ c.valeur }}</b></dd>
      </div>
    </dl>
  </div>
  <div class="ig-infos">
    <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap">
      <h1 class="ig-nom">{{ nom }}</h1>
      <slot name="badges" />
    </div>
    <slot />
  </div>
  <div v-if="$slots.boutons" class="ig-btns"><slot name="boutons" /></div>
</template>
