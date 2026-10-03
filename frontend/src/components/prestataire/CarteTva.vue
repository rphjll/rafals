<script setup lang="ts">
// Mon activité › TVA (.doc/ihm/RM-PROPOSER-IHM.md ; RM-DEVIS.md, lot 5.4) : la case « Je facture la TVA », pour les
// prochains devis (et factures).
import { ref, watch } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import AppCase from '../ui/AppCase.vue'
import AppSection from '../ui/AppSection.vue'

const props = defineProps<{ factureTva: boolean }>()
const emit = defineEmits<{ maj: [factureTva: boolean] }>()
const { afficherMessage } = useMessage()
const coche = ref(props.factureTva)
watch(() => props.factureTva, (v) => (coche.value = v))

watch(coche, async (valeur) => {
  if (valeur === props.factureTva) return
  try {
    await appelerServeur('/api/moi/prestataire/tva', { facture_tva: valeur })
    afficherMessage(valeur ? 'Vos prochains devis indiqueront la TVA.' : 'Vos prochains devis seront sans TVA (mention 293 B).')
    emit('maj', valeur)
  } catch (e) {
    coche.value = props.factureTva
    afficherMessage(messageErreur(e), 'erreur')
  }
})
</script>

<template>
  <AppSection titre="TVA">
    <AppCase v-model="coche" texte="Je facture la TVA" />
    <p class="text-[13.5px] text-texte-doux">
      Non coché : vos devis et factures portent « TVA non applicable, art. 293 B du CGI » (auto-entrepreneur en franchise).
      Coché : un taux par ligne (5,5 %, 10 % ou 20 %) et les totaux HT, TVA, TTC. Vaut pour vos prochains devis.
    </p>
  </AppSection>
</template>
