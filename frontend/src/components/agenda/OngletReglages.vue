<script setup lang="ts">
// Mon agenda › Réglages (.doc/ihm/RM-AGENDA-IHM.md) : écart entre deux heures de début, pause, délais de réservation.
import { onMounted, ref, watch } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { type AgendaVisible, DELAIS_MAX, DELAIS_MIN, PAUSES, dureeLisible } from '../../outils/agenda'
import { DELAIS_ANNULATION, type ReglagesReservation } from '../../outils/rendez_vous'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppChoix from '../ui/AppChoix.vue'
import AppSection from '../ui/AppSection.vue'
import AppSelection from '../ui/AppSelection.vue'

const props = defineProps<{ agenda: AgendaVisible }>()
const emit = defineEmits<{ maj: [agenda: AgendaVisible] }>()
const { afficherMessage } = useMessage()

const pas = ref<'15' | '30' | '60'>('15')
const pause = ref<number | null>(0)
const delaiMin = ref<number | null>(120)
const delaiMax = ref<number | null>(2)
watch(
  () => props.agenda.reglages,
  (r) => {
    pas.value = String(r.pas_minutes) as '15' | '30' | '60'
    pause.value = r.pause_minutes
    delaiMin.value = r.delai_min_minutes
    delaiMax.value = r.delai_max_mois
  },
  { immediate: true },
)
const erreur = ref('')

// Réservations (RM-RENDEZ-VOUS) : confirmation automatique ou « j'accepte chaque demande », délai d'annulation
const confirmation = ref<'auto' | 'demande'>('auto')
const delaiAnnulation = ref<number | null>(24)
const erreurReservations = ref('')
onMounted(async () => {
  const r = await appelerServeur<ReglagesReservation>('/api/moi/prestataire/rendez-vous/reglages')
  confirmation.value = r.confirmation_automatique ? 'auto' : 'demande'
  delaiAnnulation.value = r.annulation_delai_heures
})
async function enregistrerReservations() {
  erreurReservations.value = ''
  try {
    await appelerServeur('/api/moi/prestataire/rendez-vous/reglages', {
      confirmation_automatique: confirmation.value === 'auto',
      annulation_delai_heures: delaiAnnulation.value,
    })
    afficherMessage('Réglages des réservations enregistrés.')
  } catch (e) {
    erreurReservations.value = messageErreur(e)
  }
}

async function enregistrer() {
  erreur.value = ''
  try {
    emit('maj', await appelerServeur<AgendaVisible>('/api/moi/agenda/reglages', {
      pas_minutes: Number(pas.value),
      pause_minutes: pause.value,
      delai_min_minutes: delaiMin.value,
      delai_max_mois: delaiMax.value,
    }))
    afficherMessage('Réglages enregistrés.')
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
</script>

<template>
  <AppSection titre="Réservations">
    <AppChoix
      v-model="confirmation"
      etiquette="Quand un client réserve"
      obligatoire
      :options="[
        { valeur: 'auto', texte: 'Confirmé aussitôt', detail: 'l\'horaire libre est pris' },
        { valeur: 'demande', texte: 'J\'accepte chaque demande', detail: '24 h pour répondre' },
      ]"
    />
    <AppSelection
      v-model="delaiAnnulation"
      etiquette="Annulation gratuite par le client jusqu'à"
      obligatoire
      :options="DELAIS_ANNULATION.map((h) => ({ valeur: h, texte: `${h} h avant` }))"
    />
    <AppAlerte v-if="erreurReservations">{{ erreurReservations }}</AppAlerte>
    <div><AppBouton @click="enregistrerReservations">Enregistrer</AppBouton></div>
  </AppSection>

  <AppSection titre="Horaires">
    <AppChoix
      v-model="pas"
      etiquette="Heures de début proposées aux clients"
      obligatoire
      :options="[
        { valeur: '15', texte: 'toutes les 15 min' },
        { valeur: '30', texte: 'toutes les 30 min' },
        { valeur: '60', texte: 'toutes les heures' },
      ]"
    />
    <p class="-mt-2 text-[13px] text-texte-doux">Ex. ouvert à 9 h, service de 45 min : 9 h 00, 9 h 15, 9 h 30…</p>
    <div class="grid gap-3 sm:grid-cols-2">
      <div class="flex flex-col gap-1">
        <AppSelection
          v-model="pause"
          etiquette="Pause après chaque rendez-vous"
          obligatoire
          :options="PAUSES.map((m) => ({ valeur: m, texte: dureeLisible(m) }))"
        />
        <p class="text-[13px] text-texte-doux">Pour le trajet ou le rangement.</p>
      </div>
      <AppSelection
        v-model="delaiMin"
        etiquette="Réservation au plus tôt"
        obligatoire
        :options="DELAIS_MIN.map((m) => ({ valeur: m, texte: m ? `${dureeLisible(m)} avant` : 'à tout moment' }))"
      />
    </div>
    <AppSelection
      v-model="delaiMax"
      etiquette="Réservation au plus tard"
      obligatoire
      :options="DELAIS_MAX.map((m) => ({ valeur: m, texte: `${m} mois à l'avance` }))"
    />
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <div><AppBouton @click="enregistrer">Enregistrer</AppBouton></div>
  </AppSection>
</template>
