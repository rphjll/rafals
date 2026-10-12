<script setup lang="ts">
// Un rendez-vous dans une liste (.doc/ihm/RM-RENDEZ-VOUS-IHM.md) : titre, état, plage horaire, l'autre personne
// (et son téléphone quand c'est permis), lieu, prix ; les boutons viennent de la page (slot « actions »).
import { computed } from 'vue'
import { euros } from '../../outils/prix'
import { jourCourt, aParis } from '../../outils/agenda'
import { MOYENS_DIRECTS } from '../../outils/devis'
import { prixPayeClient, prixPayePrestataire } from '../../outils/paiements'
import { type RendezVousVisible, badgeRendezVous, momentCourt, plage } from '../../outils/rendez_vous'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBadge from '../ui/AppBadge.vue'

const props = defineProps<{ rdv: RendezVousVisible; libelleAutre: 'Avec' | 'Client' }>()

// L'absence vue par chacun (RM-RENDEZ-VOUS) : « moi » = celui qui regarde
const moi = computed(() => (props.libelleAutre === 'Avec' ? 'client' : 'prestataire'))

// « 50 € · espèces », ou l'état du paiement par carte (lot 5.2)
const prix = computed(() => {
  const r = props.rdv
  if (r.paiement) return (moi.value === 'client' ? prixPayeClient : prixPayePrestataire)(r.prix_centimes, r.paiement)
  const prix = r.prix_centimes ? euros(r.prix_centimes) : '—'
  if (r.paye_direct_le && r.paye_direct_moyen) {
    const facture = r.facture_numero ? ` · facture ${r.facture_numero}` : ''
    const moyen = r.paye_direct_moyen === 'especes' ? 'en espèces' : `par ${MOYENS_DIRECTS[r.paye_direct_moyen]}`
    return `${prix} · payé ${moyen} le ${jourCourt(aParis(r.paye_direct_le).jour)}${facture}`
  }
  return `${prix} · ${r.mode_paiement === 'carte' ? 'carte' : 'espèces'}`
})
const absence = computed(() => {
  const a = props.rdv.absence
  if (!a) return null
  const visee = a.absent === moi.value
  const signalement = visee
    ? `${props.libelleAutre === 'Avec' ? props.rdv.autre.nom : 'Le client'} indique que vous n'êtes pas venu.`
    : `Vous avez signalé : ${props.rdv.autre.nom} n'est pas venu.`
  let suite = ''
  if (a.decision) suite = a.decision === 'compte' ? "Décision de rafals : l'absence compte." : "Décision de rafals : l'absence ne compte pas."
  else if (a.contestee_le) suite = `Contestée : « ${a.contestation} ». rafals va trancher.`
  else if (visee) suite = `Si c'est faux, contestez avant le ${momentCourt(a.contestable_jusqu_au)}.`
  else suite = `Elle comptera le ${momentCourt(a.contestable_jusqu_au)}, sauf contestation.`
  return { visee, texte: `${signalement} ${suite}` }
})
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
        <AppBadge v-if="rdv.autre.absences" etat="erreur" class="ml-1.5">
          {{ rdv.autre.absences }} absence{{ rdv.autre.absences > 1 ? 's' : '' }} en 6 mois
        </AppBadge>
      </dd>
      <template v-if="rdv.adresse">
        <dt class="text-texte-doux">Où</dt>
        <dd class="font-medium">{{ rdv.lieu === 'chez_client' && libelleAutre === 'Avec' ? 'Chez vous : ' : '' }}{{ rdv.adresse }}</dd>
      </template>
      <dt class="text-texte-doux">Prix</dt>
      <dd class="font-medium">{{ prix }}</dd>
      <template v-if="rdv.motif">
        <dt class="text-texte-doux">Motif</dt>
        <dd class="font-medium">« {{ rdv.motif }} »</dd>
      </template>
    </dl>
    <AppAlerte v-if="absence" :etat="absence.visee ? 'attente' : 'ok'">{{ absence.texte }}</AppAlerte>
    <div class="flex flex-wrap items-center gap-2 pt-1 empty:hidden">
      <slot name="actions" />
    </div>
  </div>
</template>
