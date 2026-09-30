<script setup lang="ts">
// Onglets d'une page (Administration, Mon agenda). L'onglet choisi est dans l'adresse (ex. ?onglet=semaine) :
// un lien ou le bouton « retour » ramène au bon onglet. Le 1er onglet n'a pas besoin de ?onglet.
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const props = defineProps<{ onglets: readonly { id: string; texte: string }[]; compteurs?: Record<string, number> }>()
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
  <div class="flex flex-wrap gap-1.5 border-b border-bord" role="tablist">
    <button
      v-for="o in onglets"
      :key="o.id"
      type="button"
      role="tab"
      :aria-selected="actif === o.id"
      class="-mb-px min-h-[42px] border-b-[3px] px-3 py-2.5 font-semibold"
      :class="actif === o.id ? 'border-primaire text-primaire' : 'border-transparent text-texte-doux'"
      @click="choisir(o.id)"
    >
      {{ o.texte }}
      <span v-if="compteurs?.[o.id]" class="ml-1 rounded-full bg-accent px-[7px] py-px text-xs text-sur-etat">
        {{ compteurs[o.id] }}
      </span>
    </button>
  </div>
</template>
