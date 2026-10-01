<script setup lang="ts">
// Mon agenda (.doc/ihm/RM-AGENDA-IHM.md) : 5 onglets, un fichier chacun dans components/agenda/.
import { computed, onMounted, ref, watch } from 'vue'
import { appelerServeur, messageErreur } from '../api'
import OngletCalendrier from '../components/agenda/OngletCalendrier.vue'
import OngletHoraires from '../components/agenda/OngletHoraires.vue'
import OngletReglages from '../components/agenda/OngletReglages.vue'
import OngletRendezVous from '../components/agenda/OngletRendezVous.vue'
import OngletSemaine from '../components/agenda/OngletSemaine.vue'
import GardePrestataire from '../components/prestataire/GardePrestataire.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppOnglets from '../components/ui/AppOnglets.vue'
import { useCompte } from '../composables/useCompte'
import type { AgendaVisible } from '../outils/agenda'
import type { AnnonceVisible } from '../outils/annonces'
import type { ProfilPrestataire } from '../outils/prestataires'
import type { RendezVousVisible } from '../outils/rendez_vous'

const onglets = [
  { id: 'calendrier', texte: 'Calendrier' },
  { id: 'rendez-vous', texte: 'Rendez-vous' },
  { id: 'semaine', texte: 'Semaine type' },
  { id: 'reglages', texte: 'Réglages' },
  { id: 'horaires', texte: 'Horaires libres' },
] as const

const { compte } = useCompte()
const ongletActif = ref('calendrier')
const agenda = ref<AgendaVisible | null>(null)
const profil = ref<ProfilPrestataire | null>(null)
const annonces = ref<AnnonceVisible[]>([])
const rendezVous = ref<RendezVousVisible[]>([])
// Compteur orange : les demandes qui attendent une réponse
const compteurs = computed(() => ({
  'rendez-vous': rendezVous.value.filter((r) => r.statut === 'en_attente' && new Date(r.fin) > new Date()).length,
}))
const erreur = ref('')

async function charger() {
  if (!compte.value?.prestataire_id) return
  try {
    const [a, p, liste, rdv] = await Promise.all([
      appelerServeur<AgendaVisible>('/api/moi/agenda'),
      appelerServeur<ProfilPrestataire>('/api/moi/prestataire'),
      appelerServeur<AnnonceVisible[]>('/api/moi/annonces'),
      appelerServeur<RendezVousVisible[]>('/api/moi/prestataire/rendez-vous'),
    ])
    agenda.value = a
    profil.value = p
    annonces.value = liste
    rendezVous.value = rdv
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
onMounted(charger)
watch(compte, charger)
</script>

<template>
  <GardePrestataire titre="Mon agenda">
    <h1 class="text-[28px] font-bold">Mon agenda</h1>
    <AppOnglets v-model="ongletActif" :onglets="onglets" :compteurs="compteurs" />
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <template v-if="agenda && profil">
      <OngletCalendrier
        v-if="ongletActif === 'calendrier'"
        :agenda="agenda"
        :profil="profil"
        :rendez-vous="rendezVous"
        @maj="(a) => (agenda = a)"
      />
      <OngletRendezVous v-else-if="ongletActif === 'rendez-vous'" :rendez-vous="rendezVous" @maj="charger" />
      <OngletSemaine v-else-if="ongletActif === 'semaine'" :agenda="agenda" @maj="(a) => (agenda = a)" />
      <OngletReglages v-else-if="ongletActif === 'reglages'" :agenda="agenda" @maj="(a) => (agenda = a)" />
      <OngletHoraires v-else :annonces="annonces" />
    </template>
  </GardePrestataire>
</template>
