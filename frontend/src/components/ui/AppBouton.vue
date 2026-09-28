<script setup lang="ts">
// Le SEUL bouton de rafals (CONVENTIONS-IHM : un seul composant par élément répété).
// Variante « verrouille » : reste visible, grisé, avec 🔒 ; un clic affiche la raison dans une bulle.
import { computed, ref } from 'vue'

const props = withDefaults(
  defineProps<{
    variante?: 'principal' | 'secondaire' | 'danger' | 'verrouille'
    raisonVerrou?: string
    type?: 'button' | 'submit'
    pleineLargeur?: boolean
  }>(),
  { variante: 'principal', raisonVerrou: '', type: 'button', pleineLargeur: false },
)
const emit = defineEmits<{ click: [evenement: MouseEvent] }>()

const bulleVisible = ref(false)
const verrouille = computed(() => props.variante === 'verrouille')

const classesVariante: Record<string, string> = {
  principal: 'bg-primaire text-primaire-texte border-primaire hover:brightness-110',
  secondaire: 'bg-surface text-primaire border-primaire hover:bg-primaire-doux',
  danger: 'bg-surface text-erreur border-erreur hover:bg-erreur-doux',
  verrouille: 'bg-neutre-doux text-neutre border-neutre-doux cursor-not-allowed',
}

function clic(evenement: MouseEvent) {
  if (verrouille.value) {
    bulleVisible.value = !bulleVisible.value
    return
  }
  emit('click', evenement)
}
</script>

<template>
  <span class="relative" :class="pleineLargeur ? 'flex w-full' : 'inline-flex'">
    <button
      :type="verrouille ? 'button' : type"
      :aria-disabled="verrouille || undefined"
      class="inline-flex min-h-[42px] items-center justify-center gap-2 rounded-rafals border px-[18px] py-2.5 font-semibold transition"
      :class="[classesVariante[variante], pleineLargeur ? 'w-full' : '']"
      @click="clic"
      @blur="bulleVisible = false"
    >
      <span v-if="verrouille" aria-hidden="true">🔒</span>
      <slot />
    </button>
    <span
      v-if="verrouille && bulleVisible && raisonVerrou"
      role="status"
      class="absolute bottom-[calc(100%+8px)] left-0 z-10 w-64 rounded-lg bg-texte px-3 py-2.5 text-left text-[13px] leading-snug font-medium text-surface"
    >
      {{ raisonVerrou }}
    </span>
  </span>
</template>
