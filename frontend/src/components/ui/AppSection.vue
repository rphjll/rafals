<script setup lang="ts">
// Bloc d'une page : fond blanc, bord, titre ; bouton facultatif à droite du titre (slot « action »).
// « danger » : bord rouge, pour une action définitive (ex. Fermer mon compte).
// Posé dans une AppListeLignes (« Mon profil ») : devient une ligne « picto, titre, résumé, › » qui se déplie.
import { computed, inject } from 'vue'
import { CLE_LISTE_LIGNES, ligneDe } from '../../outils/profil'

const props = withDefaults(defineProps<{ titre?: string; danger?: boolean }>(), { titre: '', danger: false })
const liste = inject(CLE_LISTE_LIGNES, null)
const ligne = computed(() => ligneDe(props.titre))
const ouverte = computed(() => !!liste?.ouvertes.value.has(ligne.value.cle))
const resume = computed(() => liste?.resumes.value[ligne.value.cle] ?? '')
</script>

<template>
  <section v-if="liste">
    <div class="flex items-center gap-3 px-5 hover:bg-fond max-sm:px-4">
      <button
        type="button"
        class="grid min-h-[64px] flex-1 grid-cols-[42px_1fr_auto] items-center gap-3 py-2.5 text-left"
        :aria-expanded="ouverte"
        @click="liste.basculer(ligne.cle)"
      >
        <span class="grid size-[42px] place-items-center rounded-rafals text-[19px]" :class="ligne.teinte" aria-hidden="true">
          {{ ligne.picto }}
        </span>
        <span class="min-w-0">
          <span class="block font-extrabold" :class="danger ? 'text-erreur' : ''">{{ titre }}</span>
          <span v-if="resume" class="block truncate text-[13px] text-texte-doux">{{ resume }}</span>
        </span>
        <span class="text-xl text-texte-doux transition-transform" :class="ouverte ? 'rotate-90' : ''" aria-hidden="true">›</span>
      </button>
      <slot v-if="!ouverte" name="action" />
    </div>
    <div v-show="ouverte" class="flex flex-col gap-3.5 px-5 pb-5 sm:pl-[74px] max-sm:px-4">
      <div v-if="$slots.action" class="flex flex-wrap gap-2.5"><slot name="action" /></div>
      <slot />
    </div>
  </section>
  <section
    v-else
    class="carte flex flex-col gap-3.5 p-5"
    :class="danger ? 'border-erreur' : ''"
  >
    <div v-if="titre || $slots.action" class="flex flex-wrap items-center justify-between gap-2.5">
      <h2 class="text-xl font-bold">{{ titre }}</h2>
      <slot name="action" />
    </div>
    <slot />
  </section>
</template>
