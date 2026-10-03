<script setup lang="ts">
// Un devis lisible (.doc/ihm/RM-DEVIS-IHM.md) : lignes, totaux (HT, TVA, TTC, ou la mention 293 B), dates des travaux,
// arrhes et solde, validité. Le même pour le client et pour le prestataire.
import { type DevisVisible, jourDevis, quantite } from '../../outils/devis'
import { montant } from '../../outils/paiements'

defineProps<{ devis: DevisVisible; nomPrestataire: string }>()
</script>

<template>
  <div class="flex flex-col gap-3">
    <h3 class="text-[16px] font-bold">Devis {{ devis.numero }}</h3>
    <div class="overflow-x-auto">
      <table class="w-full min-w-[480px] border-collapse text-[14px]">
        <thead>
          <tr class="border-b border-bord text-left text-[13px] text-texte-doux">
            <th class="px-1.5 py-2 font-semibold">Désignation</th>
            <th class="px-1.5 py-2 text-right font-semibold">Quantité</th>
            <th class="px-1.5 py-2 text-right font-semibold">Prix unitaire{{ devis.facture_tva ? ' HT' : '' }}</th>
            <th v-if="devis.facture_tva" class="px-1.5 py-2 text-right font-semibold">TVA</th>
            <th class="px-1.5 py-2 text-right font-semibold">Montant{{ devis.facture_tva ? ' HT' : '' }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(ligne, rang) in devis.lignes" :key="rang" class="border-b border-bord">
            <td class="px-1.5 py-2">{{ ligne.libelle }}</td>
            <td class="px-1.5 py-2 text-right tabular-nums">{{ quantite(ligne.quantite_centiemes) }}</td>
            <td class="px-1.5 py-2 text-right tabular-nums">{{ montant(ligne.prix_unitaire_centimes) }}</td>
            <td v-if="devis.facture_tva" class="px-1.5 py-2 text-right tabular-nums">
              {{ ligne.tva_pour_mille ? `${(ligne.tva_pour_mille / 10).toString().replace('.', ',')} %` : '—' }}
            </td>
            <td class="px-1.5 py-2 text-right tabular-nums">{{ montant(ligne.montant_centimes) }}</td>
          </tr>
          <template v-if="devis.facture_tva">
            <tr>
              <td :colspan="4" class="px-1.5 pt-2 text-right text-texte-doux">Total HT</td>
              <td class="px-1.5 pt-2 text-right tabular-nums">{{ montant(devis.ht_centimes) }}</td>
            </tr>
            <tr>
              <td :colspan="4" class="px-1.5 text-right text-texte-doux">TVA</td>
              <td class="px-1.5 text-right tabular-nums">{{ montant(devis.tva_centimes) }}</td>
            </tr>
          </template>
          <tr>
            <td :colspan="devis.facture_tva ? 4 : 3" class="px-1.5 py-2 text-right">
              <b>Total{{ devis.facture_tva ? ' TTC' : '' }}</b>
              <span v-if="devis.mention_tva" class="block text-[13px] text-texte-doux">{{ devis.mention_tva }}</span>
            </td>
            <td class="px-1.5 py-2 text-right font-bold tabular-nums">{{ montant(devis.ttc_centimes) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <dl class="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 text-[14px]">
      <dt class="text-texte-doux">Travaux</dt>
      <dd>du {{ jourDevis(devis.travaux_debut) }} au {{ jourDevis(devis.travaux_fin) }}</dd>
      <template v-if="devis.arrhes_centimes">
        <dt class="text-texte-doux">Arrhes</dt>
        <dd>
          {{ montant(devis.arrhes_centimes) }} ({{ devis.arrhes_pourcent }} %) — payées en acceptant, gardées par
          {{ nomPrestataire }} si le client annule
        </dd>
      </template>
      <dt class="text-texte-doux">Solde</dt>
      <dd>{{ montant(devis.solde_centimes) }} — à payer après les travaux, une fois vérifiés</dd>
      <dt class="text-texte-doux">Valable</dt>
      <dd>jusqu'au {{ jourDevis(devis.valable_jusqu_au) }}</dd>
    </dl>
  </div>
</template>
