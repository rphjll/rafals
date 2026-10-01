<script setup lang="ts">
// Administration › Absences contestées (.doc/ihm/RM-ADMINISTRATION-IHM.md ; RM-RENDEZ-VOUS.md) : les deux versions
// côte à côte, puis la décision ; plus bas, les annulations de dernière minute des prestataires (6 mois).
import { onMounted, ref } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { formaterDateHeure } from '../../outils/dates'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBadge from '../ui/AppBadge.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppSection from '../ui/AppSection.vue'

interface Contestation {
  rendez_vous_id: number
  titre: string
  debut: string
  absent: 'client' | 'prestataire'
  client: string
  prestataire: string
  contestation: string
  contestee_le: string
}
interface Tardives {
  prestataire_id: number
  nom: string
  nombre: number
}

const emit = defineEmits<{ maj: [] }>()
const { afficherMessage } = useMessage()
const contestations = ref<Contestation[]>([])
const tardives = ref<Tardives[]>([])
const erreur = ref('')

async function charger() {
  try {
    const [c, t] = await Promise.all([
      appelerServeur<Contestation[]>('/api/admin/contestations'),
      appelerServeur<Tardives[]>('/api/admin/annulations-tardives'),
    ])
    contestations.value = c
    tardives.value = t
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
onMounted(charger)

// Celui qui a signalé, et celui qui conteste (la personne marquée absente)
const signaleur = (c: Contestation) => (c.absent === 'prestataire' ? `${c.client} (client)` : `${c.prestataire} (prestataire)`)
const conteste = (c: Contestation) => (c.absent === 'prestataire' ? `${c.prestataire} (prestataire)` : `${c.client} (client)`)

async function trancher(c: Contestation, compte: boolean) {
  try {
    await appelerServeur(`/api/admin/contestations/${c.rendez_vous_id}`, { compte })
    afficherMessage(`Décision enregistrée : l'absence ${compte ? 'compte' : 'ne compte pas'}. Les deux sont prévenus.`)
    await charger()
    emit('maj')
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}
</script>

<template>
  <div class="flex flex-col gap-4">
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <AppSection v-if="!contestations.length">
      <p class="text-texte-doux">Aucune absence contestée.</p>
    </AppSection>
    <AppSection v-for="c in contestations" :key="c.rendez_vous_id" :titre="`${c.titre} · ${formaterDateHeure(c.debut)}`">
      <template #action><AppBadge etat="attente">à trancher</AppBadge></template>
      <div class="grid gap-2.5 sm:grid-cols-2">
        <div class="rounded-rafals border border-bord p-3 text-[14px]">
          <b>{{ signaleur(c) }}</b><br />
          a signalé : « {{ c.absent === 'prestataire' ? c.prestataire : c.client }} n'est pas venu ».
        </div>
        <div class="rounded-rafals border border-bord p-3 text-[14px]">
          <b>{{ conteste(c) }}</b><br />
          a contesté le {{ formaterDateHeure(c.contestee_le) }} : « {{ c.contestation }} »
        </div>
      </div>
      <div class="flex flex-wrap gap-2">
        <AppBouton variante="danger" @click="trancher(c, true)">L'absence compte</AppBouton>
        <AppBouton variante="secondaire" @click="trancher(c, false)">Elle ne compte pas</AppBouton>
      </div>
    </AppSection>

    <AppSection titre="Annulations de dernière minute (6 mois)">
      <p class="text-[13.5px] text-texte-doux">Rendez-vous annulés par le prestataire moins de 24 h avant.</p>
      <p v-if="!tardives.length" class="text-texte-doux">Aucune.</p>
      <ul v-else class="flex flex-col gap-1 text-[14.5px]">
        <li v-for="t in tardives" :key="t.prestataire_id">
          <RouterLink :to="`/prestataires/${t.prestataire_id}`" class="underline hover:text-primaire">{{ t.nom }}</RouterLink>
          · {{ t.nombre }}
        </li>
      </ul>
    </AppSection>
  </div>
</template>
