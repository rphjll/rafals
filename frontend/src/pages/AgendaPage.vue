<script setup lang="ts">
// Mon agenda (.doc/ihm/RM-AGENDA-IHM.md) : 3 onglets (Calendrier, Rendez-vous, Paiements), un fichier chacun dans
// components/agenda/. Un calendrier par métier : avec plusieurs métiers, on choisit lequel au-dessus du calendrier.
import { computed, onMounted, ref, watch } from 'vue'
import { appelerServeur, messageErreur } from '../api'
import OngletCalendrier from '../components/agenda/OngletCalendrier.vue'
import OngletPaiements from '../components/agenda/OngletPaiements.vue'
import OngletRendezVous from '../components/agenda/OngletRendezVous.vue'
import GardePrestataire from '../components/prestataire/GardePrestataire.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppOnglets from '../components/ui/AppOnglets.vue'
import AppSegment from '../components/ui/AppSegment.vue'
import { useCompte } from '../composables/useCompte'
import type { AgendaVisible } from '../outils/agenda'
import type { AnnonceVisible } from '../outils/annonces'
import type { ProfilPrestataire } from '../outils/prestataires'
import type { RendezVousVisible } from '../outils/rendez_vous'

const onglets = [
  { id: 'calendrier', texte: 'Calendrier' },
  { id: 'rendez-vous', texte: 'Rendez-vous' },
  { id: 'paiements', texte: 'Paiements' },
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

// Un calendrier par métier exercé (principal d'abord) ; rien de choisi = le métier principal
const metiers = computed(() => (profil.value ? [profil.value.metier_principal, ...profil.value.metiers_secondaires] : []))
const metierId = ref<number | null>(null)
const metier = computed(() => metiers.value.find((m) => m.id === metierId.value) ?? metiers.value[0])
// Pour les cases « Coiffeuse | Maquilleuse » : toujours un métier choisi
const metierChoisi = computed({ get: () => metier.value?.id ?? 0, set: (id) => (metierId.value = id) })

// Dans le calendrier d'un métier : ses rendez-vous, et ceux des autres métiers s'ils bloquent aussi ce calendrier
const metierDeLAnnonce = computed(() => new Map(annonces.value.map((a) => [a.id, a.metier])))
const rendezVousDuCalendrier = computed(() =>
  rendezVous.value.flatMap((r) => {
    const sien = metierDeLAnnonce.value.get(r.annonce_id)
    if (!sien || sien.id === metier.value?.id) return [r]
    return agenda.value?.reglages.rendez_vous_bloque_autres_metiers ? [{ ...r, autreMetier: sien.nom }] : []
  }),
)

const lireAgenda = (id: number | undefined) => appelerServeur<AgendaVisible>(`/api/moi/agenda${id ? `?metier_id=${id}` : ''}`)

async function charger() {
  if (!compte.value?.prestataire_id) return
  try {
    const [p, liste, rdv] = await Promise.all([
      appelerServeur<ProfilPrestataire>('/api/moi/prestataire'),
      appelerServeur<AnnonceVisible[]>('/api/moi/annonces'),
      appelerServeur<RendezVousVisible[]>('/api/moi/prestataire/rendez-vous'),
    ])
    profil.value = p
    annonces.value = liste
    rendezVous.value = rdv
    agenda.value = await lireAgenda(metier.value?.id)
    metierId.value = agenda.value.metier_id
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
// Changer de calendrier
watch(metierId, async (id) => {
  if (!id || id === agenda.value?.metier_id) return
  try {
    agenda.value = await lireAgenda(id)
  } catch (e) {
    erreur.value = messageErreur(e)
  }
})
async function apresChangement(a: AgendaVisible) {
  agenda.value = a
  rendezVous.value = await appelerServeur<RendezVousVisible[]>('/api/moi/prestataire/rendez-vous')
}
// Date d'arrêt posée ou retirée : des rendez-vous ont pu être annulés, des annonces mises en pause
async function apresProfil(p: ProfilPrestataire) {
  profil.value = p
  await charger()
}
onMounted(charger)
watch(compte, charger)
</script>

<template>
  <GardePrestataire titre="Mon agenda" large>
    <h1 class="text-[28px] font-bold">Mon agenda</h1>
    <AppOnglets v-model="ongletActif" :onglets="onglets" :compteurs="compteurs" />
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <template v-if="agenda && profil && metier">
      <template v-if="ongletActif === 'calendrier'">
        <div v-if="metiers.length > 1" class="flex flex-wrap items-center gap-2.5">
          <b>Calendrier du métier :</b>
          <AppSegment v-model="metierChoisi" etiquette="Métier" :options="metiers.map((m) => ({ valeur: m.id, texte: m.nom }))" />
        </div>
        <OngletCalendrier
          :agenda="agenda"
          :profil="profil"
          :metier="metier"
          :rendez-vous="rendezVousDuCalendrier"
          :annonces="annonces.filter((a) => a.metier.id === metier?.id)"
          :plusieurs-metiers="metiers.length > 1"
          @maj="apresChangement"
          @maj-profil="apresProfil"
        />
      </template>
      <div v-else class="mx-auto flex w-full max-w-[720px] flex-col gap-4">
        <OngletRendezVous
          v-if="ongletActif === 'rendez-vous'"
          :rendez-vous="rendezVous"
          :siret-verifie="profil.siret_statut === 'verifie'"
          @maj="charger"
        />
        <OngletPaiements v-else />
      </div>
    </template>
  </GardePrestataire>
</template>
