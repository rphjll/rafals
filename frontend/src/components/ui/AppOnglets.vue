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
  <div
    class="border-bord"
    :class="egaux ? 'grid auto-cols-fr grid-flow-col border-t' : 'flex flex-wrap gap-1.5 border-b'"
    role="tablist"
  >
    <button
      v-for="o in onglets"
      :key="o.id"
      type="button"
      role="tab"
      :aria-selected="actif === o.id"
      :class="[
        egaux
          ? '-mt-px flex min-h-12 items-center justify-center gap-2 border-t-2 px-2 text-[14px] font-extrabold'
          : '-mb-px min-h-[42px] border-b-[3px] px-3 py-2.5 font-semibold',
        actif === o.id ? (egaux ? 'border-texte text-texte' : 'border-primaire text-primaire') : 'border-transparent text-texte-doux',
      ]"
      @click="choisir(o.id)"
    >
      <svg
        v-if="o.icone"
        class="size-[18px] shrink-0"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <path :d="o.icone" />
      </svg>
      {{ o.texte }}
      <span v-if="compteurs?.[o.id]" class="ml-1 rounded-full bg-accent px-[7px] py-px text-xs text-sur-etat">
        {{ compteurs[o.id] }}
      </span>
    </button>
  </div>
</template>
