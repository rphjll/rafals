<script setup lang="ts">
// Une liste de factures (.doc/ihm/RM-FACTURES-IHM.md) : numéro (et « avoir »), date, objet, l'autre personne et le
// moyen de paiement, total, bouton [PDF]. `autre` : qui montrer sous l'objet (le vendeur pour un client…).
import { formaterDate } from '../../outils/dates'
import { type FactureVisible, moyenLisible, ouvrirPdf } from '../../outils/factures'
import { montant } from '../../outils/paiements'
import AppBadge from '../ui/AppBadge.vue'
import AppIcone from '../ui/AppIcone.vue'

defineProps<{ factures: FactureVisible[]; autre: 'vendeur' | 'acheteur' }>()
</script>

<template>
  <!-- Une ligne par facture, comme la grande maquette -->
  <div class="liste">
    <div v-for="f in factures" :key="f.id" class="ligne">
      <span class="ico-rond"><AppIcone nom="devis" /></span>
      <div class="txt">
        <b>{{ f.numero }} · {{ f[autre] }}<AppBadge v-if="f.sorte === 'avoir'" etat="attente" class="ml-2">avoir</AppBadge></b>
        <span>{{ formaterDate(f.emise_le) }} · {{ f.objet }} · {{ moyenLisible(f) }}</span>
      </div>
      <span class="fin">
        <b style="color: var(--texte)" class="tabular-nums">{{ montant(f.ttc_centimes) }}</b>
        <button type="button" class="btn btn-2 btn-petit" :aria-label="`Télécharger ${f.numero}`" @click="ouvrirPdf(f.id)"><AppIcone nom="telecharger" />PDF</button>
      </span>
    </div>
  </div>
</template>
