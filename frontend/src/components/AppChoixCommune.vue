<script setup lang="ts">
// Choix d'une commune dans la liste officielle (.doc/ihm/RM-PROPOSER-IHM.md) : par le nom ou le code postal.
import { appelerServeur } from '../api'
import type { CommuneVisible } from '../outils/prestataires'
import AppElementChoisi from './ui/AppElementChoisi.vue'
import AppRecherche from './ui/AppRecherche.vue'

withDefaults(defineProps<{ etiquette?: string; obligatoire?: boolean }>(), { etiquette: 'Ville', obligatoire: false })
const choisie = defineModel<CommuneVisible | null>({ default: null })

const codePostal = (c: CommuneVisible) => c.codes_postaux[0] ?? c.departement
const chercher = (texte: string) => appelerServeur<CommuneVisible[]>(`/api/communes/recherche?q=${encodeURIComponent(texte)}`)
</script>

<template>
  <AppElementChoisi v-if="choisie" :texte="`${choisie.nom} (${codePostal(choisie)})`" @changer="choisie = null" />
  <AppRecherche
    v-else
    :etiquette="etiquette"
    :obligatoire="obligatoire"
    :chercher="chercher"
    :libelle="(c: CommuneVisible) => c.nom"
    :detail="(c: CommuneVisible) => c.codes_postaux.slice(0, 2).join(', ')"
    :cle="(c: CommuneVisible) => c.id"
    placeholder="ex. Pessac ou 33600"
    @choisir="(c: CommuneVisible) => (choisie = c)"
  >
    <template #aucun-resultat>
      <p class="text-[13px] text-texte-doux">Aucune commune ne correspond. Essayez le code postal.</p>
    </template>
  </AppRecherche>
</template>
