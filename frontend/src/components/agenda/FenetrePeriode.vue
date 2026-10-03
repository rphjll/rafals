<script setup lang="ts">
// Mon agenda › Calendrier : fenêtre « Fermeture exceptionnelle » ou « Ouverture exceptionnelle »
// (.doc/ihm/RM-AGENDA-IHM.md). Une seule forme : « Du [jour] à [heure] jusqu'au [jour] à [heure] ».
// Le même jour des deux côtés = seulement quelques heures ; de 0 h 00 à 24 h 00 = des jours entiers.
import { computed, ref, watch } from 'vue'
import { ErreurServeur, appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import {
  type AgendaVisible,
  type Blocage,
  QUARTS_D_HEURE,
  ajouterJours,
  minutesEnHeure,
  minutesLisibles,
  periodeLisible,
} from '../../outils/agenda'
import { aujourdhuiIso } from '../../outils/dates'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppChamp from '../ui/AppChamp.vue'
import AppFenetre from '../ui/AppFenetre.vue'
import AppSelection from '../ui/AppSelection.vue'

const props = defineProps<{
  ouverte: boolean
  type: 'fermeture' | 'ouverture'
  /** Jours choisis dans le calendrier, ex. « 2026-10-20 » et « 2026-10-24 » */
  du: string
  au: string
  agenda: AgendaVisible
}>()
const emit = defineEmits<{ maj: [agenda: AgendaVisible]; fermer: [] }>()
const { afficherMessage } = useMessage()

const fermeture = computed(() => props.type === 'fermeture')
const du = ref('')
const au = ref('')
const de = ref<number | null>(0) // en minutes : 0 = 0 h 00
const a = ref<number | null>(1440) // 1440 = 24 h 00 (fin de journée)
const motif = ref('')
const erreur = ref('')
// Des rendez-vous tombent pendant la fermeture (RM-AGENDA) : le serveur refuse (409) et liste ; le prestataire choisit
const conflit = ref('')
const envoiEnCours = ref(false)

watch(
  () => props.ouverte,
  (ouverte) => {
    if (!ouverte) return
    du.value = props.du
    au.value = props.au
    // Fermeture : des jours entiers au départ. Ouverture : 9 h 00 – 12 h 00 au départ.
    de.value = fermeture.value ? 0 : 540
    a.value = fermeture.value ? 1440 : 720
    motif.value = ''
    erreur.value = ''
    conflit.value = ''
  },
  { immediate: true },
)

// Sans fuseau : lu à l'heure de Paris par le serveur. « Jusqu'au 24/10 à 24 h 00 » = le 25/10 à 0 h 00.
const periode = computed(() => {
  if (!du.value || !au.value || de.value === null || a.value === null) return null
  return {
    debut: `${du.value}T${minutesEnHeure(de.value)}`,
    fin: a.value === 1440 ? `${ajouterJours(au.value, 1)}T00:00` : `${au.value}T${minutesEnHeure(a.value)}`,
  }
})
// Le bouton dit exactement ce qui va se passer : « Fermer : du 20/10/2026 au 24/10/2026 »
const resume = computed(() => {
  if (!periode.value) return ''
  const texte = periodeLisible({ id: 0, motif: null, ...periode.value })
  return `${texte.charAt(0).toLowerCase()}${texte.slice(1)}`
})

async function enregistrer(rendezVous: 'annuler' | 'garder' | null = null) {
  erreur.value = ''
  if (!periode.value) {
    erreur.value = 'Choisissez les jours et les heures.'
    return
  }
  if (periode.value.fin <= periode.value.debut) {
    erreur.value = 'La fin doit être après le début.'
    return
  }
  envoiEnCours.value = true
  try {
    const avant = (fermeture.value ? props.agenda.blocages : props.agenda.ouvertures).map((p) => p.id)
    const coupees = props.agenda.ouvertures.length
    const agenda = await appelerServeur<AgendaVisible>(
      fermeture.value ? '/api/moi/agenda/blocages' : '/api/moi/agenda/ouvertures',
      {
        metier_id: props.agenda.metier_id, ...periode.value, motif: motif.value,
        ...(fermeture.value ? { rendez_vous: rendezVous } : {}),
      },
    )
    emit('maj', agenda)
    emit('fermer')
    const nouvelles: Blocage[] = (fermeture.value ? agenda.blocages : agenda.ouvertures).filter((p) => !avant.includes(p.id))
    const coupe = fermeture.value ? agenda.ouvertures.length > coupees : nouvelles.length > 1
    afficherMessage(
      `${fermeture.value ? 'Fermeture' : 'Ouverture'} enregistrée : ${resume.value}.` +
        (rendezVous === 'annuler' ? ' Les rendez-vous de la période sont annulés.' : '') +
        (coupe ? ' Une ouverture a été coupée en deux autour de la fermeture.' : ''),
    )
  } catch (e) {
    if (e instanceof ErreurServeur && e.statut === 409) conflit.value = e.message
    else erreur.value = messageErreur(e)
  } finally {
    envoiEnCours.value = false
  }
}
</script>

<template>
  <AppFenetre
    :ouverte="ouverte"
    :titre="fermeture ? 'Fermeture exceptionnelle' : 'Ouverture exceptionnelle'"
    @fermer="emit('fermer')"
  >
    <form class="flex flex-col gap-3 text-texte" @submit.prevent="enregistrer()">
      <div class="grid grid-cols-[1fr_130px] gap-2.5">
        <AppChamp v-model="du" etiquette="Du" type="date" :min="aujourdhuiIso()" obligatoire />
        <AppSelection
          v-model="de"
          etiquette="à"
          obligatoire
          :options="QUARTS_D_HEURE.filter((m) => m < 1440).map((m) => ({ valeur: m, texte: minutesLisibles(m) }))"
        />
      </div>
      <div class="grid grid-cols-[1fr_130px] gap-2.5">
        <AppChamp v-model="au" etiquette="Jusqu'au" type="date" :min="du || aujourdhuiIso()" obligatoire />
        <AppSelection
          v-model="a"
          etiquette="à"
          obligatoire
          :options="QUARTS_D_HEURE.filter((m) => m > 0).map((m) => ({ valeur: m, texte: minutesLisibles(m) }))"
        />
      </div>
      <p v-if="du && du === au" class="text-[13px] text-texte-doux">Un seul jour : seules ces heures sont concernées.</p>
      <AppChamp
        v-model="motif"
        etiquette="Motif (pour vous seul)"
        maxlength="120"
        :placeholder="fermeture ? 'ex. Congés, dentiste…' : 'ex. Mariage, salon…'"
      />
      <p class="text-[13.5px] text-texte-doux">
        <template v-if="fermeture">
          Les clients ne verront plus d'horaires pendant cette période. Si des rendez-vous y tombent, vous choisirez de
          les annuler ou de les garder.
        </template>
        <template v-else>
          Les clients pourront réserver pendant ces heures, sans arrêt du début à la fin, même si votre semaine type est
          fermée. Une fermeture exceptionnelle passe avant.
        </template>
      </p>
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <AppAlerte v-if="conflit" etat="attente">
        {{ conflit }} Annuler : chaque client est prévenu par mail. Garder : tout le reste de la période est fermé.
      </AppAlerte>
    </form>
    <template #pied>
      <template v-if="conflit">
        <AppBouton variante="danger" @click="enregistrer('annuler')">Annuler ces rendez-vous et fermer</AppBouton>
        <AppBouton variante="secondaire" @click="enregistrer('garder')">Fermer autour</AppBouton>
      </template>
      <AppBouton v-else :occupe="envoiEnCours" @click="enregistrer()">
        {{ fermeture ? 'Fermer' : 'Ouvrir' }}{{ resume ? ` : ${resume}` : '' }}
      </AppBouton>
      <AppBouton variante="secondaire" @click="emit('fermer')">Annuler</AppBouton>
    </template>
  </AppFenetre>
</template>
