<script setup lang="ts">
// Mon agenda (.doc/ihm/RM-AGENDA-IHM.md) : 3 onglets (Calendrier, Rendez-vous, Paiements), un fichier chacun dans
// components/agenda/. Un calendrier par métier : avec plusieurs métiers, on choisit lequel au-dessus du calendrier.
// Depuis le 07/10/2026 (demande de Raphael) : un client y voit le calendrier de ses rendez-vous (CalendrierClient) ;
// un prestataire a en plus le choix « Mes rendez-vous de client » à côté de ses métiers (?calendrier=client).
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import OngletCalendrier from '../components/agenda/OngletCalendrier.vue'
import OngletPaiements from '../components/agenda/OngletPaiements.vue'
import OngletRendezVous from '../components/agenda/OngletRendezVous.vue'
import GardePrestataire from '../components/prestataire/GardePrestataire.vue'
import CalendrierClient from '../components/rendez-vous/CalendrierClient.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppCarte from '../components/ui/AppCarte.vue'
import AppOnglets from '../components/ui/AppOnglets.vue'
import AppSegment from '../components/ui/AppSegment.vue'
import { useCompte } from '../composables/useCompte'
import type { AgendaVisible } from '../outils/agenda'
import type { ProfilPrestataire } from '../outils/prestataires'
import type { RendezVousVisible } from '../outils/rendez_vous'

const onglets = [
  { id: 'calendrier', texte: 'Calendrier' },
  { id: 'rendez-vous', texte: 'Rendez-vous' },
  { id: 'paiements', texte: 'Paiements' },
] as const

const { compte, chargementFait } = useCompte()
const route = useRoute()
const routeur = useRouter()
const ongletActif = ref('calendrier')
const agenda = ref<AgendaVisible | null>(null)
const profil = ref<ProfilPrestataire | null>(null)
const rendezVous = ref<RendezVousVisible[]>([])
// Compteur orange : d'anciennes demandes de rendez-vous encore en attente (il n'y en a plus de nouvelles)
const compteurs = computed(() => ({
  'rendez-vous': rendezVous.value.filter((r) => r.statut === 'en_attente' && new Date(r.fin) > new Date()).length,
}))
const erreur = ref('')

// Un calendrier par métier exercé (principal d'abord) ; rien de choisi = le métier principal
const metiers = computed(() => (profil.value ? [profil.value.metier_principal, ...profil.value.metiers_secondaires] : []))
const metierId = ref<number | null>(null)
const metier = computed(() => metiers.value.find((m) => m.id === metierId.value) ?? metiers.value[0])
// Le calendrier « client » d'un prestataire : ses propres rendez-vous pris chez d'autres ; le choix est dans l'adresse
const CLIENT = -1
const vueClient = computed(() => route.query.calendrier === 'client')
// Pour les cases « Coiffeuse | Maquilleuse | Mes rendez-vous de client » : toujours une case choisie
const metierChoisi = computed({
  get: () => (vueClient.value ? CLIENT : (metier.value?.id ?? 0)),
  set: (id) => {
    routeur.replace({ query: id === CLIENT ? { calendrier: 'client' } : {} })
    if (id !== CLIENT) metierId.value = id
  },
})
const casesCalendrier = computed(() => [
  ...metiers.value.map((m) => ({ valeur: m.id, texte: m.nom })),
  { valeur: CLIENT, texte: 'Mes rendez-vous de client' },
])

// Dans le calendrier d'un métier : ses rendez-vous, et ceux des autres métiers s'ils bloquent aussi ce calendrier
const rendezVousDuCalendrier = computed(() =>
  rendezVous.value.flatMap((r) => {
    const sien = r.metier // porté par le rendez-vous lui-même 
    if (sien.id === metier.value?.id) return [r]
    return agenda.value?.reglages.rendez_vous_bloque_autres_metiers ? [{ ...r, autreMetier: sien.nom }] : []
  }),
)

const lireAgenda = (id: number | undefined) => appelerServeur<AgendaVisible>(`/api/moi/agenda${id ? `?metier_id=${id}` : ''}`)

async function charger() {
  if (!compte.value?.prestataire_id) return
  try {
    const [p, rdv] = await Promise.all([
      appelerServeur<ProfilPrestataire>('/api/moi/prestataire'),
      appelerServeur<RendezVousVisible[]>('/api/moi/prestataire/rendez-vous'),
    ])
    profil.value = p
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
// Date d'arrêt posée ou retirée : des rendez-vous ont pu être annulés
async function apresProfil(p: ProfilPrestataire) {
  profil.value = p
  await charger()
}
onMounted(charger)
watch(compte, charger)
</script>

<template>
  <AppCarte v-if="chargementFait && !compte" titre="Mon agenda" intro="Connectez-vous pour voir vos rendez-vous.">
    <AppBouton pleine-largeur @click="routeur.push({ path: '/connexion', query: { retour: '/mon-agenda' } })">Se connecter</AppBouton>
  </AppCarte>

  <!-- Un client (sans profil de prestataire) : le calendrier de ses rendez-vous -->
  <div v-else-if="compte && !compte.prestataire_id" class="mx-auto flex w-full max-w-[720px] flex-col gap-4">
    <h1 class="text-[clamp(28px,4.5vw,40px)] font-black">Mon agenda</h1>
    <CalendrierClient />
  </div>

  <GardePrestataire v-else titre="Mon agenda" large>
    <h1 class="text-[28px] font-bold">Mon agenda</h1>
    <AppOnglets v-model="ongletActif" :onglets="onglets" :compteurs="compteurs" />
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <template v-if="agenda && profil && metier">
      <template v-if="ongletActif === 'calendrier'">
        <div class="flex flex-wrap items-center gap-2.5">
          <b>Calendrier :</b>
          <AppSegment v-model="metierChoisi" etiquette="Calendrier" :options="casesCalendrier" />
        </div>
        <CalendrierClient v-if="vueClient" />
        <OngletCalendrier
          v-else
          :agenda="agenda"
          :profil="profil"
          :metier="metier"
          :rendez-vous="rendezVousDuCalendrier"
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
