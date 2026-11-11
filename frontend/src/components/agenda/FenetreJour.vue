<script setup lang="ts">
// Mon agenda › Calendrier › clic sur un jour (toucher sur téléphone) : « Horaires du mardi 27 octobre »
// (.doc/ihm/RM-AGENDA-IHM.md ; RM-AGENDA.md § « Agenda simplifié »). Pour ce jour seul, une ligne par plage :
// - jour fermé en entier par une fermeture exceptionnelle → « Fermé de … à … » (le reste suit la semaine type) ;
// - sinon → « Ouvert de … à … ».
import { computed, ref, watch } from 'vue'
import { type Minutes, QUARTS_D_HEURE, jourCourt, jourLisible, minutesLisibles } from '../../outils/agenda'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppFenetre from '../ui/AppFenetre.vue'

const props = defineProps<{
  ouverte: boolean
  /** Le jour cliqué, ex. « 2026-10-27 » */
  jour: string
  /** Lignes proposées au départ (heures ouvertes du jour, ou heures habituelles pour un jour fermé) */
  depart: Minutes[]
  /** Le jour a déjà des « horaires du jour » : on peut remettre les horaires habituels */
  modifie: boolean
  /** Heures habituelles de ce jour (semaine type), pour l'explication */
  habituelles: string
  /** Le métier de ce calendrier (« Calendrier Électricien ») */
  metier?: string
}>()
// La page applique tout de suite les horaires, et les envoie au serveur derrière (OngletCalendrier.vue)
const emit = defineEmits<{ enregistrer: [plages: Minutes[]]; remettre: []; fermer: [] }>()

const plages = ref<Minutes[]>([])
const erreur = ref('')
watch(
  () => props.ouverte,
  (ouverte) => {
    if (!ouverte) return
    // Les heures ouvertes du jour ; un jour fermé n'a aucune ligne (« Fermé toute la journée »)
    plages.value = props.depart.map(([d, f]) => [d, f] as Minutes)
    erreur.value = ''
  },
  { immediate: true },
)

const triees = computed(() => [...plages.value].sort((x, y) => x[0] - y[0]))
const texte = (liste: Minutes[]) => liste.map(([d, f]) => `${minutesLisibles(d)} – ${minutesLisibles(f)}`).join(' · ')
const debuts = QUARTS_D_HEURE.slice(0, -1).map((m) => ({ valeur: m, texte: minutesLisibles(m) }))
const fins = QUARTS_D_HEURE.slice(1).map((m) => ({ valeur: m, texte: minutesLisibles(m) }))

function changer(rang: number, bout: 0 | 1, valeur: number | null) {
  const plage = plages.value[rang]
  if (plage && valeur !== null) plage[bout] = valeur
  erreur.value = ''
}
// La nouvelle plage commence 2 h après la dernière (ex. après 8 h – 12 h : 14 h – 18 h)
function ajouter() {
  const derniere = plages.value.length ? Math.max(...plages.value.map((p) => p[1])) : 420  // sans plage : 9 h – 13 h
  const debut = Math.min(derniere + 120, 1320)
  plages.value.push([debut, Math.min(debut + 240, 1440)])
}
function controler(): string {
  if (triees.value.some(([d, f]) => f <= d)) return 'Chaque plage doit finir après son début.'
  if (triees.value.some((p, i) => i > 0 && p[0] < (triees.value[i - 1]?.[1] ?? 0))) return 'Deux plages se chevauchent : changez leurs heures.'
  return ''
}

function enregistrer() {
  erreur.value = controler()
  if (!erreur.value) emit('enregistrer', triees.value)
}
</script>

<template>
  <AppFenetre :ouverte="ouverte" :titre="`Horaires du ${jourLisible(jour)}`" @fermer="emit('fermer')">
    <p v-if="metier" class="doux petit" style="margin-top: -6px">Calendrier {{ metier }}</p>
    <!-- Raphael, 17/10/2026 : on écrit les heures d'OUVERTURE (« OUVERT »), sur tous les jours -->
    <div class="bandeau b-vert">Indiquez vos heures d'OUVERTURE ce jour-là. En dehors, vous serez fermé.</div>
    <p class="doux">D'habitude : {{ habituelles }}.</p>
    <div v-for="(plage, rang) in plages" :key="rang" class="plage">
      <span>Ouvert de</span>
      <select :value="plage[0]" aria-label="Ouvert de" @change="changer(rang, 0, Number(($event.target as HTMLSelectElement).value))">
        <option v-for="h in debuts" :key="h.valeur" :value="h.valeur">{{ h.texte }}</option>
      </select>
      <span>à</span>
      <select :value="plage[1]" aria-label="Jusqu’à" @change="changer(rang, 1, Number(($event.target as HTMLSelectElement).value))">
        <option v-for="h in fins" :key="h.valeur" :value="h.valeur">{{ h.texte }}</option>
      </select>
      <button type="button" class="croix" :aria-label="`Retirer la plage ${rang + 1}`" @click="plages.splice(rang, 1)">×</button>
    </div>
    <div v-if="!plages.length" class="bandeau b-err">Fermé toute la journée.</div>
    <button type="button" class="lien-plus" @click="ajouter">+ Ajouter une plage</button>
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <template #pied>
      <AppBouton @click="enregistrer">
        Enregistrer : {{ jourCourt(jour) }}, {{ triees.length ? `ouvert ${texte(triees)}` : 'fermé toute la journée' }}
      </AppBouton>
      <AppBouton v-if="modifie" variante="secondaire" @click="emit('remettre')">Remettre les horaires habituels</AppBouton>
      <AppBouton variante="secondaire" @click="emit('fermer')">Annuler</AppBouton>
    </template>
  </AppFenetre>
</template>
