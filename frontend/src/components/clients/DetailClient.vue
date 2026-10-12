<script setup lang="ts">
// Ce qu'un prestataire voit d'un de ses clients (.doc/ihm/RM-MON-ACTIVITE-IHM.md) : coordonnées tant qu'elles sont
// visibles, ses rendez-vous et ses devis avec lui. Le même bloc sous une ligne de « Mes clients » et sur son profil.
import { type FicheClient, etatDevis } from '../../outils/activite'
import { formaterDate } from '../../outils/dates'
import { montant } from '../../outils/paiements'
import AppBadge from '../ui/AppBadge.vue'

defineProps<{ fiche: FicheClient }>()
</script>

<template>
  <div class="flex flex-col gap-4">
    <dl class="grid gap-x-6 gap-y-1 sm:grid-cols-[auto_1fr]">
      <dt class="text-[13.5px] text-texte-doux">Téléphone</dt>
      <dd>{{ fiche.telephone ?? 'caché (plus de 3 mois après le dernier rendez-vous, ou pas encore de rendez-vous)' }}</dd>
      <dt class="text-[13.5px] text-texte-doux">Adresse</dt>
      <dd>{{ fiche.adresse ?? (fiche.telephone ? 'pas de rendez-vous chez ce client' : 'cachée') }}</dd>
      <dt class="text-[13.5px] text-texte-doux">Payé par rafals</dt>
      <dd class="tabular-nums">{{ montant(fiche.paye_centimes) }}</dd>
    </dl>

    <div class="flex flex-col gap-1.5">
      <h3 class="text-[16px] font-bold">Vos rendez-vous ensemble</h3>
      <p v-if="!fiche.les_rendez_vous.length" class="text-texte-doux">Pas encore de rendez-vous.</p>
      <ul v-else class="flex flex-col divide-y divide-bord">
        <li v-for="r in fiche.les_rendez_vous" :key="r.id" class="flex flex-wrap items-center gap-x-4 gap-y-1 py-2">
          <span class="w-[92px] tabular-nums">{{ formaterDate(r.debut) }}</span>
          <span class="min-w-0 flex-1">{{ r.titre }}</span>
          <b v-if="r.prix_centimes" class="tabular-nums">{{ montant(r.prix_centimes) }}</b>
          <AppBadge :etat="r.a_venir ? 'ok' : 'neutre'">{{ r.a_venir ? 'à venir' : 'passé' }}</AppBadge>
        </li>
      </ul>
    </div>

    <div v-if="fiche.les_devis.length" class="flex flex-col gap-1.5">
      <h3 class="text-[16px] font-bold">Vos devis pour {{ fiche.nom.split(' ')[0] }}</h3>
      <ul class="flex flex-col divide-y divide-bord">
        <li v-for="d in fiche.les_devis" :key="d.numero" class="flex flex-wrap items-center gap-x-4 gap-y-1 py-2">
          <span class="w-[92px] tabular-nums">{{ formaterDate(d.envoye_le) }}</span>
          <span class="min-w-0 flex-1">Devis {{ d.numero }}</span>
          <b class="tabular-nums">{{ montant(d.total_centimes) }}</b>
          <AppBadge :etat="d.statut === 'envoye' ? 'attente' : 'neutre'">{{ etatDevis(d.statut) }}</AppBadge>
        </li>
      </ul>
    </div>
  </div>
</template>
