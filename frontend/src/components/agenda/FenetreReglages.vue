<script setup lang="ts">
// Mon agenda › Calendrier › [Réglages] (.doc/ihm/RM-AGENDA-IHM.md) : les mêmes réglages pour tous les métiers.
// Audit du 14/11/2026 (accord de Raphael le 15/11) : depuis que le prestataire propose lui-même l'heure, seul le délai
// d'annulation gratuite sert encore. Les 5 autres réglages (confirmation, heures de début, pause, au plus tôt, au plus
// tard) et « chaque calendrier est indépendant » ne sont plus montrés ; leurs valeurs en base sont renvoyées telles quelles.
import { ref, watch } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { type AgendaVisible } from '../../outils/agenda'
import { DELAIS_ANNULATION, type ReglagesReservation } from '../../outils/rendez_vous'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppFenetre from '../ui/AppFenetre.vue'
import AppSelection from '../ui/AppSelection.vue'

const props = defineProps<{ ouverte: boolean; agenda: AgendaVisible; plusieursMetiers: boolean }>()
const emit = defineEmits<{ maj: [agenda: AgendaVisible]; fermer: [] }>()
const { afficherMessage } = useMessage()

const confirmationAutomatique = ref(true) // gardée telle quelle : elle n'a plus d'effet
const delaiAnnulation = ref<number | null>(24)
const erreur = ref('')
const envoiEnCours = ref(false)

// À chaque ouverture : le délai enregistré
watch(
  () => props.ouverte,
  async (ouverte) => {
    if (!ouverte) return
    erreur.value = ''
    try {
      const reservations = await appelerServeur<ReglagesReservation>('/api/moi/prestataire/rendez-vous/reglages')
      confirmationAutomatique.value = reservations.confirmation_automatique
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
      confirmation_automatique: confirmationAutomatique.value,
      annulation_delai_heures: delaiAnnulation.value,
    })
    emit('maj', props.agenda)
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
      <AppSelection
        v-model="delaiAnnulation"
        etiquette="Annulation gratuite par le client jusqu'à"
        obligatoire
        :options="DELAIS_ANNULATION.map((h) => ({ valeur: h, texte: `${h} h avant` }))"
      />
      <p class="-mt-2 text-[13px] text-texte-doux">
        Ex. 24 h avant : un rendez-vous samedi à 15 h s'annule sans frais jusqu'à vendredi 15 h.
      </p>
      <p class="text-[13px] text-texte-doux">
        Ce réglage vaut pour tous vos métiers. Vous choisissez vous-même le jour et l'heure de chaque rendez-vous quand
        vous faites une proposition, et deux rendez-vous ne tombent jamais en même temps.
      </p>
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    </div>
    <template #pied>
      <AppBouton :occupe="envoiEnCours" @click="enregistrer">Enregistrer les réglages</AppBouton>
      <AppBouton variante="secondaire" @click="emit('fermer')">Annuler</AppBouton>
    </template>
  </AppFenetre>
</template>
