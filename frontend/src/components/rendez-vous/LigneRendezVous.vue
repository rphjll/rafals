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
// « 14 h », « 9 h 30 »
const heureDebut = computed(() => {
  const [h, m] = aParis(props.rdv.debut).heure.split(':')
  return `${Number(h)} h${m === '00' ? '' : ` ${m}`}`
})

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
  <!-- La ligne de la grande maquette : l'heure en grand à gauche, ce qu'on fait et chez qui, l'état et les boutons à droite -->
  <div class="ligne ligne-rdv">
    <span class="heure">{{ heureDebut }}</span>
    <div class="txt">
      <b>{{ rdv.titre }}<template v-if="rdv.heures"> · {{ rdv.heures }} h</template></b>
      <span class="whitespace-normal!">
        {{ plage(rdv) }} ·
        <RouterLink v-if="rdv.autre.prestataire_id" :to="`/prestataires/${rdv.autre.prestataire_id}`" class="lien">{{ rdv.autre.nom }}</RouterLink>
        <template v-else>{{ libelleAutre === 'Client' ? '' : 'avec ' }}{{ rdv.autre.nom }}</template><template v-if="rdv.autre.telephone"> · {{ rdv.autre.telephone }}</template>
        <template v-if="rdv.adresse"> · {{ rdv.lieu === 'chez_client' && libelleAutre === 'Avec' ? 'chez vous : ' : '' }}{{ rdv.adresse }}</template>
        · {{ prix }}<template v-if="rdv.motif"> · motif « {{ rdv.motif }} »</template>
      </span>
      <span v-if="rdv.autre.absences" class="puce p-err mt-1 self-start">{{ rdv.autre.absences }} absence{{ rdv.autre.absences > 1 ? 's' : '' }} en 6 mois</span>
    </div>
    <span class="fin flex-wrap">
      <AppBadge :etat="badgeRendezVous(rdv).etat">{{ badgeRendezVous(rdv).texte }}</AppBadge>
      <slot name="actions" />
    </span>
    <AppAlerte v-if="absence" class="w-full" :etat="absence.visee ? 'attente' : 'ok'">{{ absence.texte }}</AppAlerte>
  </div>
</template>
