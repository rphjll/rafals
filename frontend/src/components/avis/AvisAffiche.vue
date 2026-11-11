<script setup lang="ts">
// Un avis affiché (.doc/ihm/RM-AVIS-IHM.md) : étoiles, auteur et mois (ou « Votre avis »), texte, réponse du
// prestataire en retrait ; pour son auteur ou le prestataire : avis caché, retiré, signalé. Boutons : slot « actions ».
import { type AvisDetaille, type AvisPublic, etoiles } from '../../outils/avis'
import AppAlerte from '../ui/AppAlerte.vue'
import AppInitiales from '../ui/AppInitiales.vue'

defineProps<{ avis: AvisPublic | AvisDetaille; titre?: string; nomPrestataire?: string }>()
const detaille = (a: AvisPublic | AvisDetaille): a is AvisDetaille => 'retire' in a
</script>

<template>
  <!-- Comme un avis de la grande maquette : rond, nom et étoiles sur une ligne, le texte, puis le mois -->
  <div class="flex flex-col gap-1">
    <span class="pp-qui">
      <AppInitiales v-if="!titre" :nom="avis.auteur" />
      <b>{{ titre ?? avis.auteur }}</b>
      <span class="etoile" :aria-label="`${avis.note} étoile${avis.note > 1 ? 's' : ''} sur 5`">{{ etoiles(avis.note) }}</span>
    </span>
    <p class="whitespace-pre-line">{{ avis.texte }}</p>
    <span v-if="!titre" class="doux petit">{{ avis.mois }}</span>
    <p v-if="avis.reponse" class="ml-4 border-l-[3px] border-primaire-doux py-0.5 pl-2.5 text-[14px]">
      <b>Réponse{{ nomPrestataire ? ` de ${nomPrestataire}` : '' }} :</b> {{ avis.reponse }}
    </p>
    <template v-if="detaille(avis)">
      <AppAlerte v-if="avis.cache_motif">Avis caché par rafals : « {{ avis.cache_motif }} ».</AppAlerte>
      <p v-else-if="avis.retire" class="doux petit">Avis retiré : il n'est plus affiché.</p>
      <AppAlerte v-else-if="avis.signale" etat="attente">Signalé : l'administrateur va le regarder.</AppAlerte>
    </template>
    <div class="btns pt-1 empty:hidden"><slot name="actions" /></div>
  </div>
</template>
