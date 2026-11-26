<script setup lang="ts">
// Onglet « Factures » de « Devis et factures » (.doc/ihm/RM-FACTURES-IHM.md ; RM-FACTURES.md). Depuis le 25/11/2026,
// l'ancienne page « Mes factures » est rangée ici (demande de Raphael : « Devis » et « Factures » réunis).
// Client : ses factures reçues. Prestataire : 3 vues, « Émises » (faites par rafals à son nom), « Reçues » et
// « Commission de rafals ».
import { computed, onMounted, ref } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import type { FactureVisible } from '../../outils/factures'
import AppAlerte from '../ui/AppAlerte.vue'
import AppSection from '../ui/AppSection.vue'
import AppSegment from '../ui/AppSegment.vue'
import TableauFactures from './TableauFactures.vue'

const props = defineProps<{ prestataire: boolean }>()
const vue = ref<'emises' | 'recues' | 'commission'>(props.prestataire ? 'emises' : 'recues')
const recues = ref<FactureVisible[] | null>(null)
const duPrestataire = ref<FactureVisible[]>([])
const erreur = ref('')

onMounted(async () => {
  try {
    recues.value = await appelerServeur<FactureVisible[]>('/api/moi/factures')
    if (props.prestataire) duPrestataire.value = await appelerServeur<FactureVisible[]>('/api/moi/prestataire/factures')
  } catch (e) {
    erreur.value = messageErreur(e)
  }
})

const vues = [
  { valeur: 'emises' as const, texte: 'Émises' },
  { valeur: 'recues' as const, texte: 'Reçues' },
  { valeur: 'commission' as const, texte: 'Commission de rafals' },
]
const emises = computed(() => duPrestataire.value.filter((f) => f.sorte !== 'commission'))
const commissions = computed(() => duPrestataire.value.filter((f) => f.sorte === 'commission'))
</script>

<template>
  <AppSegment v-if="prestataire" v-model="vue" etiquette="Quelles factures" :options="vues" en-ligne />
  <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>

  <AppSection v-if="recues && vue === 'emises' && prestataire">
    <TableauFactures v-if="emises.length" :factures="emises" autre="acheteur" />
    <p v-else class="text-texte-doux">Aucune facture pour l'instant : elles se créent toutes seules à chaque paiement.</p>
    <p class="text-[13.5px] text-texte-doux">
      rafals fait ces factures à votre place, à votre nom (mandat de facturation). Un avoir est une facture « en moins »,
      après un remboursement.
    </p>
  </AppSection>
  <AppSection v-else-if="recues && vue === 'commission' && prestataire">
    <TableauFactures v-if="commissions.length" :factures="commissions" autre="vendeur" />
    <p v-else class="text-texte-doux">
      Pas encore de facture de commission : rafals vous en envoie une le 1er de chaque mois si vous avez été payé par carte.
    </p>
  </AppSection>
  <AppSection v-else-if="recues">
    <TableauFactures v-if="recues.length" :factures="recues" autre="vendeur" />
    <p v-else class="text-texte-doux">Aucune facture pour l'instant.</p>
    <p class="text-[13.5px] text-texte-doux">
      Les numéros sont ceux de chaque prestataire. Un avoir est une facture « en moins », après un remboursement.
    </p>
  </AppSection>
</template>
