<script setup lang="ts">
// Bloc d'une page : titre au-dessus, carte blanche dessous (grande maquette) ; bouton facultatif à droite du titre (slot « action »).
// « danger » : bord rouge, pour une action définitive (ex. Fermer mon compte).
// Posé dans une AppListeLignes (« Mon profil ») : devient une ligne « picto, titre, résumé, › » qui se déplie.
import { computed, inject } from 'vue'
import { CLE_LISTE_LIGNES, COULEURS_LIGNE, ligneDe } from '../../outils/profil'
import AppIcone from './AppIcone.vue'

const props = withDefaults(defineProps<{ titre?: string; danger?: boolean }>(), { titre: '', danger: false })
const liste = inject(CLE_LISTE_LIGNES, null)
const ligne = computed(() => ligneDe(props.titre))
const ouverte = computed(() => !!liste?.ouvertes.value.has(ligne.value.cle))
const resume = computed(() => liste?.resumes.value[ligne.value.cle] ?? '')
</script>

<template>
  <!-- Dans « Mon profil » : la ligne qui se déplie de la grande maquette (rond coloré, titre, résumé, ›) -->
  <div v-if="liste" class="dep" :class="{ ouvert: ouverte }">
    <div class="flex items-center">
      <button type="button" class="dep-tete" :aria-expanded="ouverte" @click="liste.basculer(ligne.cle)">
        <span class="ico-rond" :style="COULEURS_LIGNE[ligne.couleur]"><AppIcone :nom="ligne.icone" /></span>
        <span class="txt">
          <b :style="danger ? 'color: var(--erreur)' : undefined">{{ titre }}</b>
          <span v-if="resume">{{ resume }}</span>
        </span>
        <span class="chev" aria-hidden="true">›</span>
      </button>
      <span v-if="!ouverte && $slots.action" class="pr-4"><slot name="action" /></span>
    </div>
    <div v-show="ouverte" class="dep-corps">
      <div v-if="$slots.action" class="btns"><slot name="action" /></div>
      <slot />
    </div>
  </div>
  <!-- Grande maquette : le titre au-dessus, le contenu dans une carte blanche dessous -->
  <section v-else class="section">
    <div v-if="titre || $slots.action" class="section-titre flex-wrap" style="align-items: center">
      <h2>{{ titre }}</h2>
      <slot name="action" />
    </div>
    <div class="carte flex flex-col gap-3.5 p-[18px]" :class="danger ? 'border-erreur!' : ''"><slot /></div>
  </section>
</template>
