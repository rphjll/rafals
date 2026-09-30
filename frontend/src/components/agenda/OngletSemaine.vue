<script setup lang="ts">
// Mon agenda › Semaine type (.doc/ihm/RM-AGENDA-IHM.md) : les 7 jours, plusieurs plages possibles par jour,
// enregistrés ensemble. Un jour sans plage est fermé.
import { ref, watch } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { type AgendaVisible, JOURS } from '../../outils/agenda'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppChamp from '../ui/AppChamp.vue'
import AppSection from '../ui/AppSection.vue'

const props = defineProps<{ agenda: AgendaVisible }>()
const emit = defineEmits<{ maj: [agenda: AgendaVisible] }>()
const { afficherMessage } = useMessage()

// Une liste de plages « 09:00 → 12:00 » par jour (index 0 = lundi)
const semaine = ref<{ debut: string; fin: string }[][]>([])
function remplir() {
  semaine.value = JOURS.map((_, rang) =>
    props.agenda.plages
      .filter((p) => p.jour_semaine === rang + 1)
      .map((p) => ({ debut: p.debut.slice(0, 5), fin: p.fin.slice(0, 5) })),
  )
}
watch(() => props.agenda, remplir, { immediate: true })

const erreur = ref('')
const envoiEnCours = ref(false)

function ajouter(rang: number) {
  const jour = semaine.value[rang]
  if (!jour) return
  const derniere = jour[jour.length - 1]
  // Après une plage du matin, on propose l'après-midi ; sinon une journée classique
  jour.push(derniere && derniere.fin < '14:00' ? { debut: '14:00', fin: '19:00' } : { debut: '09:00', fin: '12:00' })
}

async function enregistrer() {
  erreur.value = ''
  envoiEnCours.value = true
  try {
    const plages = semaine.value.flatMap((jour, rang) =>
      jour.map((p) => ({ jour_semaine: rang + 1, debut: p.debut, fin: p.fin })),
    )
    emit('maj', await appelerServeur<AgendaVisible>('/api/moi/agenda/semaine', { plages }))
    afficherMessage('Semaine type enregistrée.')
  } catch (e) {
    erreur.value = messageErreur(e)
  } finally {
    envoiEnCours.value = false
  }
}
</script>

<template>
  <AppSection titre="Semaine type">
    <p class="text-[13.5px] text-texte-doux">
      Vos horaires de chaque semaine, heure de Paris. Plusieurs plages possibles par jour (ex. une pause déjeuner). Un jour
      sans plage est fermé.
    </p>
    <div class="flex flex-col divide-y divide-bord">
      <div v-for="(jour, rang) in semaine" :key="rang" class="grid gap-2.5 py-3 sm:grid-cols-[100px_1fr]">
        <b class="capitalize sm:pt-2">{{ JOURS[rang] }}</b>
        <div class="flex flex-col gap-2">
          <p v-if="!jour.length" class="text-[13.5px] text-texte-doux sm:pt-2">Fermé</p>
          <div v-for="(plage, n) in jour" :key="n" class="flex flex-wrap items-end gap-2">
            <div class="w-[130px]"><AppChamp v-model="plage.debut" etiquette="De" type="time" obligatoire /></div>
            <div class="w-[130px]"><AppChamp v-model="plage.fin" etiquette="À" type="time" obligatoire /></div>
            <button
              type="button"
              class="mb-1.5 size-[34px] rounded-full bg-erreur-doux font-bold text-erreur"
              :aria-label="`Retirer la plage de ${plage.debut} à ${plage.fin} du ${JOURS[rang]}`"
              @click="jour.splice(n, 1)"
            >
              ×
            </button>
          </div>
          <div><AppBouton variante="secondaire" @click="ajouter(rang)">+ Ajouter une plage</AppBouton></div>
        </div>
      </div>
    </div>
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <div class="flex flex-wrap gap-2">
      <AppBouton :occupe="envoiEnCours" @click="enregistrer">Enregistrer la semaine</AppBouton>
      <AppBouton variante="secondaire" @click="remplir">Annuler</AppBouton>
    </div>
    <p class="text-[13px] text-texte-doux">
      Rendez-vous déjà pris hors des nouveaux horaires : vous pourrez choisir de les annuler ou de les garder (quand les
      rendez-vous existeront).
    </p>
  </AppSection>
</template>
