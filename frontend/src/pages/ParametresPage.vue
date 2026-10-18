<script setup lang="ts">
// « Paramètres » (.doc/ihm/RM-PARAMETRES-IHM.md), ouverte depuis la liste sous le prénom (demande de Raphael du 17/10/2026).
// Pour l'instant une seule carte, « Apparence » : thème Automatique, Clair ou Sombre, gardé dans l'appareil.
import AppChoix from '../components/ui/AppChoix.vue'
import AppSection from '../components/ui/AppSection.vue'
import { useMessage } from '../composables/useMessage'
import { useTheme, type ChoixTheme } from '../composables/useTheme'

const { choix, choisirTheme } = useTheme()
const { afficherMessage } = useMessage()

const options: { valeur: ChoixTheme; texte: string; detail: string; apercus: string[] }[] = [
  { valeur: 'auto', texte: 'Automatique', detail: 'Comme votre téléphone ou votre ordinateur', apercus: ['apercu-clair', 'apercu-sombre'] },
  { valeur: 'clair', texte: 'Clair', detail: 'Fond blanc, toujours', apercus: ['apercu-clair'] },
  { valeur: 'sombre', texte: 'Sombre', detail: 'Fond noir, plus doux le soir', apercus: ['apercu-sombre'] },
]
const messages: Record<ChoixTheme, string> = {
  auto: 'Thème automatique : comme votre appareil.',
  clair: 'Thème clair activé.',
  sombre: 'Thème sombre activé.',
}

// Effet immédiat, sans bouton « Enregistrer »
function changer(nouveau: ChoixTheme) {
  choisirTheme(nouveau)
  afficherMessage(messages[nouveau])
}
</script>

<template>
  <div class="mx-auto flex w-full max-w-[720px] flex-col gap-4">
    <div>
      <h1 class="text-[clamp(28px,4.5vw,40px)] font-black">Paramètres</h1>
      <p class="text-texte-doux">Réglez rafals comme vous le préférez.</p>
    </div>
    <AppSection titre="Apparence">
      <AppChoix :model-value="choix" etiquette="Thème" :options="options" @update:model-value="changer">
        <template #avant="{ option }">
          <span class="mb-2 flex h-[46px] overflow-hidden rounded-[10px] border border-bord" aria-hidden="true">
            <span v-for="apercu in options.find((o) => o.valeur === option.valeur)?.apercus" :key="apercu" class="flex-1 p-[9px]" :class="apercu">
              <span class="block h-2 rounded bg-current" />
            </span>
          </span>
        </template>
      </AppChoix>
      <p class="text-[13px] text-texte-doux">
        Le choix est gardé sur cet appareil. Sur un autre téléphone ou ordinateur, vous le refaites une fois.
      </p>
    </AppSection>
  </div>
</template>
