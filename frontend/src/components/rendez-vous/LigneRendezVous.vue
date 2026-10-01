<script setup lang="ts">
// Un rendez-vous dans une liste (.doc/ihm/RM-RENDEZ-VOUS-IHM.md) : titre, état, plage horaire, l'autre personne
// (et son téléphone quand c'est permis), lieu, prix ; les boutons viennent de la page (slot « actions »).
import { euros } from '../../outils/annonces'
import { type RendezVousVisible, badgeRendezVous, plage } from '../../outils/rendez_vous'
import AppBadge from '../ui/AppBadge.vue'

defineProps<{ rdv: RendezVousVisible; libelleAutre: 'Avec' | 'Client' }>()
</script>

<template>
  <div class="flex flex-col gap-1.5 py-3.5">
    <div class="flex flex-wrap items-center justify-between gap-2">
      <h3 class="text-[17px] font-bold">
        {{ rdv.titre }}<template v-if="rdv.heures"> · {{ rdv.heures }} h</template>
      </h3>
      <AppBadge :etat="badgeRendezVous(rdv).etat">{{ badgeRendezVous(rdv).texte }}</AppBadge>
    </div>
    <p class="font-semibold">{{ plage(rdv) }}</p>
    <dl class="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 text-[14.5px]">
      <dt class="text-texte-doux">{{ libelleAutre }}</dt>
      <dd class="font-medium">
        <RouterLink
          v-if="rdv.autre.prestataire_id"
          :to="`/prestataires/${rdv.autre.prestataire_id}`"
          class="underline hover:text-primaire"
        >
          {{ rdv.autre.nom }}
        </RouterLink>
        <template v-else>{{ rdv.autre.nom }}</template>
        <template v-if="rdv.autre.telephone"> · {{ rdv.autre.telephone }}</template>
      </dd>
      <template v-if="rdv.adresse">
        <dt class="text-texte-doux">Où</dt>
        <dd class="font-medium">{{ rdv.lieu === 'chez_client' && libelleAutre === 'Avec' ? 'Chez vous : ' : '' }}{{ rdv.adresse }}</dd>
      </template>
      <dt class="text-texte-doux">Prix</dt>
      <dd class="font-medium">
        {{ rdv.prix_centimes ? euros(rdv.prix_centimes) : '—' }} · {{ rdv.mode_paiement === 'carte' ? 'carte' : 'espèces' }}
      </dd>
      <template v-if="rdv.motif">
        <dt class="text-texte-doux">Motif</dt>
        <dd class="font-medium">« {{ rdv.motif }} »</dd>
      </template>
    </dl>
    <div class="flex flex-wrap items-center gap-2 pt-1 empty:hidden">
      <slot name="actions" />
    </div>
  </div>
</template>
