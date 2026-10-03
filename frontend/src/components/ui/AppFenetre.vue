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
      class="fixed inset-0 z-20 grid place-items-center bg-voile p-4"
      @click.self="emit('fermer')"
    >
      <div
        ref="cadre"
        role="dialog"
        aria-modal="true"
        :aria-label="titre"
        class="max-h-[calc(100dvh-32px)] w-full overflow-y-auto rounded-rafals border border-bord bg-surface p-[22px] text-texte"
        :class="large ? 'max-w-[640px]' : 'max-w-[440px]'"
      >
        <h3 class="mb-2 text-xl font-bold">{{ titre }}</h3>
        <div class="mb-[18px] leading-relaxed text-texte-doux"><slot /></div>
        <div class="flex min-h-[42px] flex-wrap justify-between gap-2.5">
          <slot name="pied" />
        </div>
      </div>
    </div>
  </Teleport>
</template>
