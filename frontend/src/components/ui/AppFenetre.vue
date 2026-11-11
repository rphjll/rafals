<script setup lang="ts">
// Fenêtre propre à rafals : jamais la fenêtre grise du navigateur (CONVENTIONS-IHM).
// Échap ou clic sur le fond la ferme ; le pied (boutons) ne change pas de hauteur ; un contenu trop haut défile.
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'

// « large » : pour un contenu à plusieurs colonnes (ex. la semaine type, les réglages de l'agenda)
const props = defineProps<{ ouverte: boolean; titre: string; large?: boolean }>()
const emit = defineEmits<{ fermer: [] }>()
const cadre = ref<HTMLElement | null>(null)

function surTouche(evenement: KeyboardEvent) {
  if (evenement.key === 'Escape') emit('fermer')
}

watch(
  () => props.ouverte,
  async (ouverte) => {
    if (ouverte) {
      document.addEventListener('keydown', surTouche)
      await nextTick()
      cadre.value?.querySelector<HTMLElement>('input, button')?.focus()
    } else {
      document.removeEventListener('keydown', surTouche)
    }
  },
)
onBeforeUnmount(() => document.removeEventListener('keydown', surTouche))
</script>

<template>
  <Teleport to="body">
    <div
      v-if="ouverte"
      class="voile"
      @click.self="emit('fermer')"
    >
      <div
        ref="cadre"
        role="dialog"
        aria-modal="true"
        :aria-label="titre"
        class="fenetre text-texte"
      >
        <h2>{{ titre }}</h2>
        <div class="flex flex-col gap-3 leading-relaxed"><slot /></div>
        <div class="btns f-btns">
          <slot name="pied" />
        </div>
      </div>
    </div>
  </Teleport>
</template>
