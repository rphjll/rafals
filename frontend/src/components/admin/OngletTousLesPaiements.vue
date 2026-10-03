<script setup lang="ts">
// Administration › Paiements (.doc/ihm/RM-ADMINISTRATION-IHM.md ; RM-ADMINISTRATION.md, lot 6.2) : tous les paiements
// par carte, le plus récent d'abord, 30 par page. Lecture seule : remboursements et versements sont automatiques.
import { computed, onMounted, ref } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { formaterDate } from '../../outils/dates'
import { montant } from '../../outils/paiements'
import type { BadgeEtat } from '../../outils/prestataires'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBadge from '../ui/AppBadge.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppSection from '../ui/AppSection.vue'

interface PaiementAdministre {
  id: number
  titre: string
  quand: string
  prestataire: string
  client: string
  montant_centimes: number
  commission_centimes: number
  statut: 'a_payer' | 'paye' | 'verse' | 'rembourse' | 'abandonne'
  paye_le: string | null
  rembourse_centimes: number | null
}
interface PagePaiements {
  paiements: PaiementAdministre[]
  total: number
  par_page: number
}

const page = ref(1)
const contenu = ref<PagePaiements | null>(null)
const erreur = ref('')
async function charger() {
  try {
    contenu.value = await appelerServeur<PagePaiements>(`/api/admin/paiements?page=${page.value}`)
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
onMounted(charger)
const pages = computed(() => Math.max(1, Math.ceil((contenu.value?.total ?? 0) / (contenu.value?.par_page ?? 30))))
function aller(numero: number) {
  page.value = numero
  charger()
}

function badge(p: PaiementAdministre): { etat: BadgeEtat; texte: string } {
  return {
    a_payer: { etat: 'neutre' as BadgeEtat, texte: 'page de paiement ouverte' },
    abandonne: { etat: 'neutre' as BadgeEtat, texte: 'jamais payé' },
    paye: { etat: 'attente' as BadgeEtat, texte: 'payé (bloqué)' },
    verse: { etat: 'ok' as BadgeEtat, texte: 'versé' },
    rembourse: { etat: 'erreur' as BadgeEtat, texte: `remboursé ${montant(p.rembourse_centimes ?? 0)}` },
  }[p.statut]
}
</script>

<template>
  <AppSection>
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <template v-if="contenu">
      <p v-if="!contenu.total" class="text-texte-doux">Aucun paiement par carte pour l'instant.</p>
      <template v-else>
        <div class="overflow-x-auto">
          <table class="w-full min-w-[620px] border-collapse text-[14px]">
            <thead>
              <tr class="border-b border-bord text-left text-[13px] text-texte-doux">
                <th class="px-1.5 py-2 font-semibold">Payé le</th>
                <th class="px-1.5 py-2 font-semibold">Quoi</th>
                <th class="px-1.5 py-2 text-right font-semibold">Montant</th>
                <th class="px-1.5 py-2 text-right font-semibold">Commission</th>
                <th class="px-1.5 py-2 font-semibold">État</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in contenu.paiements" :key="p.id" class="border-b border-bord">
                <td class="px-1.5 py-2 whitespace-nowrap">{{ p.paye_le ? formaterDate(p.paye_le) : '—' }}</td>
                <td class="px-1.5 py-2">
                  {{ p.titre }} — {{ p.quand }}<br />
                  <span class="text-[13px] text-texte-doux">{{ p.prestataire }} · {{ p.client }}</span>
                </td>
                <td class="px-1.5 py-2 text-right whitespace-nowrap tabular-nums">{{ montant(p.montant_centimes) }}</td>
                <td class="px-1.5 py-2 text-right whitespace-nowrap tabular-nums">
                  {{ p.statut === 'paye' || p.statut === 'verse' ? montant(p.commission_centimes) : '—' }}
                </td>
                <td class="px-1.5 py-2"><AppBadge :etat="badge(p).etat">{{ badge(p).texte }}</AppBadge></td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="flex flex-wrap items-center gap-2">
          <AppBouton v-if="page > 1" variante="secondaire" @click="aller(page - 1)">← Plus récents</AppBouton>
          <span class="text-[13.5px] text-texte-doux">Page {{ page }} sur {{ pages }} · {{ contenu.total }} paiement{{ contenu.total > 1 ? 's' : '' }}</span>
          <AppBouton v-if="page < pages" variante="secondaire" @click="aller(page + 1)">Plus anciens →</AppBouton>
        </div>
        <p class="text-[13.5px] text-texte-doux">Lecture seule : les remboursements et les versements sont automatiques.</p>
      </template>
    </template>
  </AppSection>
</template>
