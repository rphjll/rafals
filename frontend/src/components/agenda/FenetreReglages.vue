<script setup lang="ts">
// Mon agenda › Calendrier › [Réglages] (.doc/ihm/RM-AGENDA-IHM.md) : les mêmes réglages pour tous les métiers.
// Réservations (confirmation, annulation), heures de début, pause, délais ; avec plusieurs métiers :
// « un rendez-vous dans un métier bloque mes autres calendriers ».
import { ref, watch } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { type AgendaVisible, DELAIS_MAX, DELAIS_MIN, PAUSES, dureeLisible } from '../../outils/agenda'
import { DELAIS_ANNULATION, type ReglagesReservation } from '../../outils/rendez_vous'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppChoix from '../ui/AppChoix.vue'
import AppFenetre from '../ui/AppFenetre.vue'
import AppSelection from '../ui/AppSelection.vue'

const props = defineProps<{ ouverte: boolean; agenda: AgendaVisible; plusieursMetiers: boolean }>()
const emit = defineEmits<{ maj: [agenda: AgendaVisible]; fermer: [] }>()
const { afficherMessage } = useMessage()

const pas = ref<'15' | '30' | '60'>('15')
const pause = ref<number | null>(0)
const delaiMin = ref<number | null>(120)
const delaiMax = ref<number | null>(2)
const bloqueAutres = ref<'oui' | 'non'>('oui')
// Réservations (RM-RENDEZ-VOUS) : confirmation automatique ou « j'accepte chaque demande », délai d'annulation
const confirmation = ref<'auto' | 'demande'>('auto')
const delaiAnnulation = ref<number | null>(24)
const erreur = ref('')
const envoiEnCours = ref(false)

// À chaque ouverture : les réglages enregistrés
watch(
  () => props.ouverte,
  async (ouverte) => {
    if (!ouverte) return
    erreur.value = ''
    const r = props.agenda.reglages
    pas.value = String(r.pas_minutes) as '15' | '30' | '60'
    pause.value = r.pause_minutes
    delaiMin.value = r.delai_min_minutes
    delaiMax.value = r.delai_max_mois
    bloqueAutres.value = r.rendez_vous_bloque_autres_metiers ? 'oui' : 'non'
    try {
      const reservations = await appelerServeur<ReglagesReservation>('/api/moi/prestataire/rendez-vous/reglages')
      confirmation.value = reservations.confirmation_automatique ? 'auto' : 'demande'
      delaiAnnulation.value = reservations.annulation_delai_heures
    } catch (e) {
      erreur.value = messageErreur(e)
    }
  },
  { immediate: true },
)

async function enregistrer() {
  erreur.value = ''
  envoiEnCours.value = true
  try {
    await appelerServeur('/api/moi/prestataire/rendez-vous/reglages', {
      confirmation_automatique: confirmation.value === 'auto',
      annulation_delai_heures: delaiAnnulation.value,
    })
    emit('maj', await appelerServeur<AgendaVisible>('/api/moi/agenda/reglages', {
      pas_minutes: Number(pas.value),
      pause_minutes: pause.value,
      delai_min_minutes: delaiMin.value,
      delai_max_mois: delaiMax.value,
      rendez_vous_bloque_autres_metiers: bloqueAutres.value === 'oui',
    }))
    emit('fermer')
    afficherMessage('Réglages enregistrés.')
  } catch (e) {
    erreur.value = messageErreur(e)
  } finally {
    envoiEnCours.value = false
  }
}
</script>

<template>
  <AppFenetre :ouverte="ouverte" titre="Réglages" large @fermer="emit('fermer')">
    <div class="flex flex-col gap-3.5 text-texte">
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
      <template v-if="plusieursMetiers">
        <AppChoix
          v-model="bloqueAutres"
          etiquette="Un rendez-vous dans un métier bloque mes autres calendriers"
          obligatoire
          :options="[
            { valeur: 'oui', texte: 'Oui', detail: 'jamais deux rendez-vous en même temps' },
            { valeur: 'non', texte: 'Non', detail: 'chaque calendrier est indépendant' },
          ]"
        />
        <p class="-mt-2 text-[13px] text-texte-doux">
          Ex. un rendez-vous samedi de 15 h à 16 h dans un métier. Oui : personne ne peut réserver votre autre métier à
          15 h. Non : il reste réservable à 15 h.
        </p>
      </template>
      <p class="text-[13px] text-texte-doux">Ces réglages valent pour tous vos métiers.</p>
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    </div>
    <template #pied>
      <AppBouton :occupe="envoiEnCours" @click="enregistrer">Enregistrer les réglages</AppBouton>
      <AppBouton variante="secondaire" @click="emit('fermer')">Annuler</AppBouton>
    </template>
  </AppFenetre>
</template>
