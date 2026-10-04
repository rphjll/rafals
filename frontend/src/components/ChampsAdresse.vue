<script setup lang="ts">
// Les champs d'une adresse : numéro et rue, ville, code postal. Le code postal vient de la ville choisie ; une liste
// apparaît seulement si la ville en a plusieurs (ex. Marseille). Utilisé par CarteAdresse (client, local) et par le
// dossier de création d'auto-entreprise (domicile, local). Emplacement libre entre la rue et la ville (ex. « Complément »).
import { computed, watch } from 'vue'
import type { CommuneVisible } from '../outils/prestataires'
import AppChoixCommune from './AppChoixCommune.vue'
import AppChamp from './ui/AppChamp.vue'
import AppSelection from './ui/AppSelection.vue'

const ligne = defineModel<string>('ligne', { default: '' })
const commune = defineModel<CommuneVisible | null>('commune', { default: null })
const codePostal = defineModel<string>('codePostal', { default: '' })

const codesPostaux = computed(() => commune.value?.codes_postaux ?? [])
// Ville changée : on garde le code postal s'il est à elle, sinon on prend son seul code, sinon on laisse choisir
watch(
  commune,
  (nouvelle) => {
    const codes = nouvelle?.codes_postaux ?? []
    if (!codes.includes(codePostal.value)) codePostal.value = codes.length === 1 ? (codes[0] ?? '') : ''
  },
  { immediate: true },
)
// La liste déroulante travaille avec des numéros : 0 = premier code postal de la ville
const rangCodePostal = computed({
  get: () => (codesPostaux.value.includes(codePostal.value) ? codesPostaux.value.indexOf(codePostal.value) : null),
  set: (rang) => (codePostal.value = rang === null ? '' : (codesPostaux.value[rang] ?? '')),
})
</script>

<template>
  <AppChamp v-model="ligne" etiquette="Numéro et rue" obligatoire autocomplete="address-line1" placeholder="ex. 8 allée des Pins" />
  <slot />
  <AppChoixCommune v-model="commune" obligatoire />
  <AppSelection
    v-if="codesPostaux.length > 1"
    v-model="rangCodePostal"
    etiquette="Code postal"
    obligatoire
    :options="codesPostaux.map((code, rang) => ({ valeur: rang, texte: code }))"
  />
</template>
