<script setup lang="ts">
// Les chiffres du haut de « Mon activité » et de l'accueil (« Votre journée »), comme la grande maquette : 4 cases
// blanches, le chiffre en grand et en vert, un clic ouvre la page qui le détaille (RM-MON-ACTIVITE.md, lot 10.1).
import { computed } from 'vue'
import { type ActiviteChiffree, chiffresAffiches } from '../../outils/activite'
import { montant } from '../../outils/paiements'

const props = defineProps<{ chiffres: ActiviteChiffree }>()
const affiches = computed(() =>
  chiffresAffiches(props.chiffres, montant, new Date().toLocaleDateString('fr-FR', { month: 'long', timeZone: 'Europe/Paris' })),
)
</script>

<template>
  <div v-if="affiches.length" class="stats" :style="affiches.length === 3 ? 'grid-template-columns: repeat(auto-fit, minmax(160px, 1fr))' : undefined">
    <RouterLink v-for="c in affiches" :key="c.texte" class="stat" :to="c.vers">
      <b>{{ c.valeur }}</b><span>{{ c.texte }}</span>
    </RouterLink>
  </div>
</template>
