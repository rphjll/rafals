<script setup lang="ts">
// Une liste de factures (.doc/ihm/RM-FACTURES-IHM.md) : numéro (et « avoir »), date, objet, l'autre personne et le
// moyen de paiement, total, bouton [PDF]. `autre` : qui montrer sous l'objet (le vendeur pour un client…).
import { formaterDate } from '../../outils/dates'
import { type FactureVisible, moyenLisible, ouvrirPdf } from '../../outils/factures'
import { montant } from '../../outils/paiements'
import AppBadge from '../ui/AppBadge.vue'
import AppBouton from '../ui/AppBouton.vue'

defineProps<{ factures: FactureVisible[]; autre: 'vendeur' | 'acheteur' }>()
</script>

<template>
  <div class="overflow-x-auto">
    <table class="w-full min-w-[560px] border-collapse text-[14px]">
      <thead>
        <tr class="border-b border-bord text-left text-[13px] text-texte-doux">
          <th class="px-1.5 py-2 font-semibold">Numéro</th>
          <th class="px-1.5 py-2 font-semibold">Date</th>
          <th class="px-1.5 py-2 font-semibold">Objet</th>
          <th class="px-1.5 py-2 text-right font-semibold">Total</th>
          <th class="px-1.5 py-2"><span class="sr-only">Télécharger</span></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="f in factures" :key="f.id" class="border-b border-bord">
          <td class="px-1.5 py-2 font-bold whitespace-nowrap">
            {{ f.numero }}
            <AppBadge v-if="f.sorte === 'avoir'" etat="attente" class="mt-1 block w-fit font-semibold">avoir</AppBadge>
          </td>
          <td class="px-1.5 py-2 whitespace-nowrap">{{ formaterDate(f.emise_le) }}</td>
          <td class="px-1.5 py-2">
            {{ f.objet }}<br />
            <span class="text-[13px] text-texte-doux">{{ f[autre] }} · {{ moyenLisible(f) }}</span>
          </td>
          <td class="px-1.5 py-2 text-right font-bold whitespace-nowrap tabular-nums">{{ montant(f.ttc_centimes) }}</td>
          <td class="px-1.5 py-2 text-right">
            <AppBouton variante="secondaire" :aria-label="`Ouvrir le PDF de ${f.numero}`" @click="ouvrirPdf(f.id)">PDF</AppBouton>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
