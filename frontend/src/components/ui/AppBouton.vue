<script setup lang="ts">
// Le SEUL bouton de rafals (CONVENTIONS-IHM : un seul composant par élément répété).
// Variante « verrouille » : reste visible, grisé, avec 🔒 ; un clic affiche la raison dans une bulle.
import { computed, ref } from 'vue'

const props = withDefaults(
  defineProps<{
    // « accent » : orange, pour l'action principale posée sur le bandeau foncé de l'accueil
    variante?: 'principal' | 'secondaire' | 'danger' | 'verrouille' | 'accent'
    raisonVerrou?: string
    type?: 'button' | 'submit'
    pleineLargeur?: boolean
    // Petit bouton (38 px de haut) : dans une ligne, une liste, un pied de carte
    petit?: boolean
    // Demande en cours d'envoi : le bouton ne réagit plus, pour ne pas envoyer deux fois
    occupe?: boolean
  }>(),
  { variante: 'principal', raisonVerrou: '', type: 'button', pleineLargeur: false, petit: false, occupe: false },
)
const emit = defineEmits<{ click: [evenement: MouseEvent] }>()

const bulleVisible = ref(false)
const verrouille = computed(() => props.variante === 'verrouille')

// Classes de la grande maquette (style.css) : btn-1 vert plein, btn-2 blanc bordé, btn-danger-2 bordé de rouge,
// btn-verrou grisé en pointillés, btn-accent orange (10/11/2026)
const classesVariante: Record<string, string> = {
  principal: 'btn-1',
  secondaire: 'btn-2',
  danger: 'btn-danger-2',
  verrouille: 'btn-verrou',
  accent: 'btn-accent',
}

function clic(evenement: MouseEvent) {
  if (props.occupe) {
    evenement.preventDefault()
    return
  }
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
      :aria-busy="occupe || undefined"
      class="btn"
      :class="[classesVariante[variante], petit ? 'btn-petit' : '', pleineLargeur ? 'w-full' : '', occupe ? 'cursor-wait opacity-70' : '']"
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
