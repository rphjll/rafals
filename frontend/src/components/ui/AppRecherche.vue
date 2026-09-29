<script setup lang="ts" generic="T">
// Champ de recherche avec propositions (métiers, communes…) : propositions dès la 1re lettre après une courte
// pause de frappe, ↑ ↓ pour se déplacer, Entrée ou clic pour choisir. Un seul composant pour toutes les recherches.
import { ref, shallowRef, useId, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    etiquette: string
    chercher: (texte: string) => Promise<T[]>
    libelle: (element: T) => string
    detail?: (element: T) => string
    cle: (element: T) => number
    placeholder?: string
    obligatoire?: boolean
    aide?: string
  }>(),
  { detail: () => '', placeholder: '', obligatoire: false, aide: '' },
)
const emit = defineEmits<{ choisir: [element: T]; aucunResultat: [texte: string] }>()

const id = useId()
const texte = defineModel<string>('texte', { default: '' })
const resultats = shallowRef<T[]>([])
const actif = ref(0)
const rechercheFaite = ref(false)
let minuteur: ReturnType<typeof setTimeout> | undefined

watch(texte, (valeur) => {
  clearTimeout(minuteur)
  rechercheFaite.value = false
  minuteur = setTimeout(async () => {
    resultats.value = valeur.trim() ? await props.chercher(valeur) : []
    actif.value = 0
    rechercheFaite.value = valeur.trim() !== ''
  }, 150)
})

function choisir(element: T) {
  emit('choisir', element)
  texte.value = ''
  resultats.value = []
}

function clavier(evenement: KeyboardEvent) {
  if (!resultats.value.length) return
  if (evenement.key === 'ArrowDown') actif.value = Math.min(resultats.value.length - 1, actif.value + 1)
  else if (evenement.key === 'ArrowUp') actif.value = Math.max(0, actif.value - 1)
  else if (evenement.key === 'Enter') choisir(resultats.value[actif.value])
  else return
  evenement.preventDefault()
}
</script>

<template>
  <div class="flex flex-col gap-1.5">
    <label :for="id" class="text-[13px] font-semibold">
      {{ etiquette }}<span v-if="obligatoire" class="text-erreur" aria-hidden="true"> *</span>
    </label>
    <input
      :id="id"
      v-model="texte"
      autocomplete="off"
      :placeholder="placeholder"
      role="combobox"
      :aria-expanded="resultats.length > 0"
      class="min-h-[42px] rounded-rafals border border-bord bg-fond px-3 py-2.5 text-texte outline-none focus:border-primaire focus:ring-2 focus:ring-primaire"
      @keydown="clavier"
    />
    <div v-if="resultats.length" class="overflow-hidden rounded-rafals border border-bord bg-surface" role="listbox">
      <button
        v-for="(element, i) in resultats"
        :key="cle(element)"
        type="button"
        role="option"
        :aria-selected="i === actif"
        class="flex w-full justify-between gap-2.5 border-t border-bord px-3 py-2.5 text-left first:border-t-0 hover:bg-primaire-doux"
        :class="i === actif ? 'bg-primaire-doux' : ''"
        @click="choisir(element)"
      >
        {{ libelle(element) }} <small class="text-texte-doux">{{ detail(element) }}</small>
      </button>
    </div>
    <slot v-else-if="rechercheFaite" name="aucun-resultat" :texte="texte" />
    <p v-if="aide" class="text-[13px] text-texte-doux">{{ aide }}</p>
  </div>
</template>
