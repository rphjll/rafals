<script setup lang="ts">
// L'éditeur de la semaine type d'un métier (.doc/ihm/RM-AGENDA-IHM.md), comme la grande maquette : une ligne par jour,
// « De [9 h 00] à [12 h 00] × » pour chaque plage, « + Ajouter une plage ». Un jour sans plage est fermé.
// Sert à l'onglet « Semaine type » ([Changer les horaires]) et au premier passage dans l'agenda (semaine déjà remplie
// avec des horaires courants : « depart »).
import { ref, watch } from 'vue'
import { ErreurServeur, appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { type AgendaVisible, JOURS } from '../../outils/agenda'
import AppAlerte from '../ui/AppAlerte.vue'

type Plage = { debut: string; fin: string }
const props = defineProps<{ agenda: AgendaVisible; bouton: string; depart?: Plage[][]; annulable?: boolean }>()
const emit = defineEmits<{ maj: [agenda: AgendaVisible]; annuler: [] }>()
const { afficherMessage } = useMessage()

const semaine = ref<Plage[][]>([])
const erreur = ref('')
const conflit = ref('') // des rendez-vous tombent hors des nouveaux horaires : annuler ou garder (RM-AGENDA)
const envoiEnCours = ref(false)
watch(
  () => [props.agenda, props.depart],
  () => {
    erreur.value = conflit.value = ''
    semaine.value = props.depart
      ? props.depart.map((j) => j.map((p) => ({ ...p })))
      : JOURS.map((_, rang) => props.agenda.plages.filter((p) => p.jour_semaine === rang + 1).map((p) => ({ debut: p.debut.slice(0, 5), fin: p.fin.slice(0, 5) })))
  },
  { immediate: true },
)

// Les heures proposées, de quart d'heure en quart d'heure : « 09:15 » affiché « 9 h 15 »
const quarts = (depuis: number, jusqua: number) =>
  Array.from({ length: (jusqua - depuis) / 15 + 1 }, (_, n) => {
    const m = depuis + n * 15
    return { valeur: `${String(Math.floor(m / 60)).padStart(2, '0')}:${String(m % 60).padStart(2, '0')}`, texte: `${Math.floor(m / 60)} h ${String(m % 60).padStart(2, '0')}` }
  })
const DEBUTS = quarts(0, 1425)
const FINS = quarts(15, 1425) // le serveur n'accepte pas 24 h 00 : la dernière fin est 23 h 45

function ajouter(rang: number) {
  const jour = semaine.value[rang]
  if (!jour) return
  const derniere = jour[jour.length - 1]
  // Après une plage du matin, on propose l'après-midi ; sinon une matinée classique
  jour.push(derniere && derniere.fin <= '12:00' ? { debut: '14:00', fin: '19:00' } : derniere ? { debut: derniere.fin, fin: derniere.fin < '21:00' ? '22:00' : '23:45' } : { debut: '09:00', fin: '12:00' })
  conflit.value = erreur.value = ''
}

async function enregistrer(rendezVous: 'annuler' | 'garder' | null = null) {
  erreur.value = conflit.value = ''
  envoiEnCours.value = true
  try {
    const plages = semaine.value.flatMap((jour, rang) => jour.map((p) => ({ jour_semaine: rang + 1, debut: p.debut, fin: p.fin })))
    emit('maj', await appelerServeur<AgendaVisible>('/api/moi/agenda/semaine', { metier_id: props.agenda.metier_id, plages, rendez_vous: rendezVous }))
    afficherMessage('Semaine type enregistrée.')
  } catch (e) {
    if (e instanceof ErreurServeur && e.statut === 409) conflit.value = e.message
    else erreur.value = messageErreur(e)
  } finally {
    envoiEnCours.value = false
  }
}
</script>

<template>
  <div class="semaine">
    <div v-for="(jour, rang) in semaine" :key="rang" class="sem-jour">
      <b class="sem-nom capitalize">{{ JOURS[rang] }}</b>
      <div class="sem-plages">
        <div v-for="(plage, n) in jour" :key="n" class="plage">
          <span>De</span>
          <select v-model="plage.debut" :aria-label="`${JOURS[rang]} : début`">
            <option v-for="h in DEBUTS" :key="h.valeur" :value="h.valeur">{{ h.texte }}</option>
          </select>
          <span>à</span>
          <select v-model="plage.fin" :aria-label="`${JOURS[rang]} : fin`">
            <option v-for="h in FINS" :key="h.valeur" :value="h.valeur">{{ h.texte }}</option>
          </select>
          <button type="button" class="croix" :aria-label="`Retirer cette plage du ${JOURS[rang]}`" @click="jour.splice(n, 1)">×</button>
        </div>
        <span v-if="!jour.length" class="puce p-neutre">Fermé</span>
        <button type="button" class="lien-plus" @click="ajouter(rang)">+ Ajouter une plage</button>
      </div>
    </div>
  </div>
  <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
  <div v-if="conflit" class="bandeau b-att">
    <b>{{ conflit }}</b>
    <span>Annuler : chaque client est prévenu par mail. Garder : les rendez-vous restent.</span>
    <div class="btns">
      <button type="button" class="btn btn-danger btn-petit" @click="enregistrer('annuler')">Annuler ces rendez-vous et enregistrer</button>
      <button type="button" class="btn btn-2 btn-petit" @click="enregistrer('garder')">Les garder et enregistrer</button>
    </div>
  </div>
  <div v-else class="btns">
    <button type="button" class="btn btn-1" :aria-busy="envoiEnCours || undefined" @click="enregistrer()">{{ bouton }}</button>
    <button v-if="annulable" type="button" class="btn btn-2" @click="emit('annuler')">Annuler</button>
  </div>
</template>
