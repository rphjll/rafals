<script setup lang="ts" generic="V extends string">
// Choix d'une seule réponse parmi quelques-unes, en cases côte à côte (ex. « Prix fixe · À l'heure · Sur devis »).
// Une case verrouillée reste visible avec 🔒 ; un clic affiche la raison dessous (CONVENTIONS-IHM).
// Le slot « avant » ajoute un petit dessin au-dessus du texte de chaque case.
import { ref, useId } from 'vue'

defineProps<{
  etiquette: string
  options: { valeur: V; texte: string; detail?: string; raisonVerrou?: string }[]
  obligatoire?: boolean
}>()
const valeur = defineModel<V>({ required: true })
const raison = ref('')
const id = useId()

function choisir(option: { valeur: V; raisonVerrou?: string }) {
  raison.value = option.raisonVerrou ?? ''
  if (!option.raisonVerrou) valeur.value = option.valeur
}
</script>

<template>
  <div class="flex flex-col gap-1.5" role="radiogroup" :aria-labelledby="id">
    <span :id="id" class="text-[13px] font-semibold">
      {{ etiquette }}<span v-if="obligatoire" class="text-erreur" aria-hidden="true"> *</span>
    </span>
    <div class="grid gap-2 sm:grid-cols-3">
      <button
        v-for="option in options"
        :key="option.valeur"
        type="button"
        role="radio"
        :aria-checked="valeur === option.valeur"
        :aria-disabled="option.raisonVerrou ? true : undefined"
        class="min-h-[42px] rounded-rafals border px-3 py-2.5 text-left outline-none focus-visible:ring-2 focus-visible:ring-primaire"
        :class="
          option.raisonVerrou
            ? 'cursor-not-allowed border-neutre-doux bg-neutre-doux text-texte-doux'
            : valeur === option.valeur
              ? 'border-primaire bg-primaire-doux font-semibold text-primaire'
              : 'border-bord bg-fond text-texte'
        "
        @click="choisir(option)"
      >
        <!-- Slot facultatif « avant » : un petit dessin au-dessus du texte (ex. aperçu d'un thème dans « Paramètres ») -->
        <slot name="avant" :option="option" />
        <span v-if="option.raisonVerrou" aria-hidden="true">🔒 </span>{{ option.texte }}
        <small v-if="option.detail" class="block text-[12.5px] font-normal text-texte-doux">{{ option.detail }}</small>
      </button>
    </div>
    <p v-if="raison" role="status" class="text-[13px] font-medium text-texte-doux">{{ raison }}</p>
  </div>
</template>
