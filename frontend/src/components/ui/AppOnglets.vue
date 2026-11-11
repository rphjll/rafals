<script setup lang="ts">
// Onglets d'une page (Administration, Mon agenda, Mon profil). L'onglet choisi est dans l'adresse (ex. ?onglet=semaine) :
// un lien ou le bouton « retour » ramène au bon onglet. Le 1er onglet n'a pas besoin de ?onglet.
// « egaux » (Mon profil, façon Instagram) : onglets de même largeur, trait en haut, petit dessin (« icone » : un tracé SVG).
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const props = defineProps<{
  onglets: readonly { id: string; texte: string; icone?: string }[]
  compteurs?: Record<string, number>
  egaux?: boolean
}>()
const route = useRoute()
const routeur = useRouter()
const actif = defineModel<string>({ required: true })

const premier = computed(() => props.onglets[0]?.id)
function choisir(id: string) {
  routeur.replace({ query: id === premier.value ? {} : { onglet: id } })
}
// L'adresse décide de l'onglet montré
watch(
  () => route.query.onglet,
  (onglet) => (actif.value = props.onglets.find((o) => o.id === onglet)?.id ?? premier.value ?? ''),
  { immediate: true },
)
</script>

<template>
  <!-- Onglets de la grande maquette : trait vert sous l'onglet choisi ; « egaux » : ceux du profil (trait en haut) -->
  <div :class="egaux ? 'ig-onglets' : 'onglets'" role="tablist">
    <button v-for="o in onglets" :key="o.id" type="button" role="tab" :aria-selected="actif === o.id" @click="choisir(o.id)">
      <svg v-if="o.icone" class="i" viewBox="0 0 24 24" aria-hidden="true"><path :d="o.icone" /></svg>
      <span>{{ o.texte }}</span>
      <span v-if="compteurs?.[o.id]" class="badge">{{ compteurs[o.id] }}</span>
    </button>
  </div>
</template>
