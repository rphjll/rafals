<script setup lang="ts">
// Mon compte › Mes paiements par carte (.doc/ihm/RM-COMPTE-IHM.md ; RM-PAIEMENTS.md, lot 5.2) : ce que le client a payé
// par carte, et ses remboursements. Sans paiement par carte : la carte ne s'affiche pas.
import { onMounted, ref } from 'vue'
import { appelerServeur } from '../../api'
import { aParis, jourCourt } from '../../outils/agenda'
import { type PaiementVisible, montant } from '../../outils/paiements'
import AppBadge from '../ui/AppBadge.vue'
import AppSection from '../ui/AppSection.vue'

const paiements = ref<PaiementVisible[]>([])
onMounted(async () => {
  // Une page de paiement fermée sans payer n'a rien coûté : elle n'est pas listée
  paiements.value = (await appelerServeur<PaiementVisible[]>('/api/moi/paiements')).filter((p) => p.paye_le)
})
const date = (iso: string) => jourCourt(aParis(iso).jour)
</script>

<template>
  <AppSection v-if="paiements.length" titre="Mes paiements par carte">
    <div class="overflow-x-auto">
      <table class="w-full min-w-[480px] border-collapse text-[14px]">
        <thead>
          <tr class="border-b border-bord text-left text-[13px] text-texte-doux">
            <th class="px-1.5 py-2 font-semibold">Rendez-vous</th>
            <th class="px-1.5 py-2 font-semibold">Payé le</th>
            <th class="px-1.5 py-2 text-right font-semibold">Montant</th>
            <th class="px-1.5 py-2 font-semibold">Remboursement</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in paiements" :key="p.id" class="border-b border-bord">
            <td class="px-1.5 py-2">
              {{ p.titre }} · {{ p.avec }}<br />
              <span class="text-[13px] text-texte-doux">{{ date(p.debut) }}</span>
            </td>
            <td class="px-1.5 py-2">{{ p.paye_le ? date(p.paye_le) : '—' }}</td>
            <td class="px-1.5 py-2 text-right tabular-nums">{{ montant(p.montant_centimes) }}</td>
            <td class="px-1.5 py-2">
              <AppBadge v-if="p.rembourse_le" etat="ok">{{ montant(p.rembourse_centimes ?? 0) }} le {{ date(p.rembourse_le).slice(0, 5) }}</AppBadge>
              <template v-else>—</template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="text-[13.5px] text-texte-doux">Les factures arriveront bientôt.</p>
  </AppSection>
</template>
