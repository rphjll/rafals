<script setup lang="ts">
// Mon agenda (.doc/ihm/RM-AGENDA-IHM.md), comme la grande maquette depuis le 10/11/2026 (lot 14.5) : 4 onglets
// (Calendrier, Rendez-vous, Semaine type, Paiements). Au premier passage (aucun horaire pour un métier), la semaine
// est demandée d'abord, déjà remplie avec des horaires courants. Un calendrier par métier : avec plusieurs métiers, on choisit lequel au-dessus du calendrier.
// Depuis le 07/10/2026 (demande de Raphael) : un client y voit le calendrier de ses rendez-vous (CalendrierClient) ;
// un prestataire a en plus le choix « Mes rendez-vous de client » à côté de ses métiers (?calendrier=client).
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import EditeurSemaine from '../components/agenda/EditeurSemaine.vue'
import OngletCalendrier from '../components/agenda/OngletCalendrier.vue'
import OngletPaiements from '../components/agenda/OngletPaiements.vue'
import OngletRendezVous from '../components/agenda/OngletRendezVous.vue'
import GardePrestataire from '../components/prestataire/GardePrestataire.vue'
import CalendrierClient from '../components/rendez-vous/CalendrierClient.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppCarte from '../components/ui/AppCarte.vue'
import AppIcone from '../components/ui/AppIcone.vue'
import AppOnglets from '../components/ui/AppOnglets.vue'
import AppSegment from '../components/ui/AppSegment.vue'
import { useCompte } from '../composables/useCompte'
import { type AgendaVisible, JOURS, heure } from '../outils/agenda'
import type { ProfilPrestataire } from '../outils/prestataires'
import type { RendezVousVisible } from '../outils/rendez_vous'

const onglets = [
  { id: 'calendrier', texte: 'Calendrier' },
  { id: 'rendez-vous', texte: 'Rendez-vous' },
  { id: 'semaine', texte: 'Semaine type' },
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

// Semaine type : « 9 h 00 – 12 h 00 · 14 h 00 – 18 h 00 » pour un jour (1 = lundi), vide s'il est fermé
const horairesDu = (jourSemaine: number) =>
  (agenda.value?.plages ?? []).filter((p) => p.jour_semaine === jourSemaine).sort((a, b) => a.debut.localeCompare(b.debut)).map((p) => `${heure(p.debut)} – ${heure(p.fin)}`).join(' · ')
const changerSemaine = ref(false)
const metierDeLaSemaine = computed({ get: () => metier.value?.id ?? 0, set: (id: number) => (metierId.value = id) })
watch(metierId, () => (changerSemaine.value = false))
// « d'Électricien », « de Plombier »
const deMetier = (nom: string) => (/^[aeiouyéèêàâîôûAEIOUYÉÈÊ]/.test(nom) ? `d’${nom}` : `de ${nom}`)

// Premier passage : les métiers qui n'ont encore aucun horaire. Le calendrier montré est celui du premier d'entre eux.
const avecHoraires = ref(new Set<number>())
const sansHoraires = computed(() => metiers.value.filter((m) => !avecHoraires.value.has(m.id)))
const premierPassage = computed(() => !!agenda.value && !agenda.value.plages.length && !vueClient.value)
// Déjà rempli : du lundi au vendredi 9 h – 12 h et 14 h – 18 h, le samedi matin, le dimanche fermé
const SEMAINE_COURANTE = [0, 1, 2, 3, 4, 5, 6].map((j) =>
  j < 5 ? [{ debut: '09:00', fin: '12:00' }, { debut: '14:00', fin: '18:00' }] : j === 5 ? [{ debut: '09:00', fin: '12:00' }] : [],
)
async function apresPremiereSemaine(a: AgendaVisible) {
  avecHoraires.value = new Set([...avecHoraires.value, a.metier_id])
  agenda.value = a
  const suivant = sansHoraires.value[0]
  if (suivant) {
    const autre = await lireAgenda(suivant.id)
    if (autre.plages.length) avecHoraires.value = new Set([...avecHoraires.value, suivant.id])
    else metierId.value = suivant.id
  }
  window.scrollTo({ top: 0 })
}

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
  <div v-else-if="compte && !compte.prestataire_id" class="page">
    <RouterLink class="retour" to="/mon-activite"><AppIcone nom="retour" />Mon activité</RouterLink>
    <div class="tete"><h1>Mon agenda</h1><p>Les rendez-vous que vous avez pris chez des prestataires.</p></div>
    <CalendrierClient />
  </div>

  <GardePrestataire v-else titre="Mon agenda" large>
    <div class="page">
      <RouterLink class="retour" to="/mon-activite"><AppIcone nom="retour" />Mon activité</RouterLink>
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>

      <!-- Premier passage (aucun horaire pour ce métier) : la semaine est demandée d'abord, déjà remplie (grande maquette) -->
      <template v-if="agenda && profil && metier && premierPassage">
        <section class="hero" style="padding: 26px">
          <span class="forme f1" /><span class="forme f2" />
          <p style="font-weight: 600; opacity: 0.9">Bienvenue dans votre agenda</p>
          <h1 style="font-size: clamp(26px, 4.5vw, 34px)">Quand travaillez-vous d’habitude ?</h1>
          <p>Choisissez les horaires d’une semaine normale. Les clients pourront réserver seulement pendant ces heures.</p>
        </section>
        <div class="carte form p-[18px]">
          <p v-if="sansHoraires.length > 1" class="doux petit" style="font-weight: 700">Étape {{ metiers.length - sansHoraires.length + 1 }} sur {{ metiers.length }}</p>
          <h2>Vos horaires {{ deMetier(metier.nom) }}</h2>
          <p class="doux">Déjà rempli avec des horaires courants : changez ce qui ne va pas. Un jour sans plage est fermé.</p>
          <EditeurSemaine
            :agenda="agenda"
            :depart="SEMAINE_COURANTE"
            :bouton="sansHoraires.length > 1 ? 'Enregistrer et continuer' : 'Enregistrer et voir mon calendrier'"
            @maj="apresPremiereSemaine"
          />
          <p class="doux petit">Vous pourrez les changer quand vous voulez dans l’onglet « Semaine type ».</p>
        </div>
      </template>

      <template v-else>
        <div class="tete"><h1>Mon agenda</h1><p>Vos horaires et vos rendez-vous.</p></div>
        <AppOnglets v-model="ongletActif" :onglets="onglets" :compteurs="compteurs" />
        <template v-if="agenda && profil && metier">
          <template v-if="ongletActif === 'calendrier'">
            <div class="cal-choix">
              <span class="doux petit" style="font-weight: 700">Calendrier :</span>
              <AppSegment v-model="metierChoisi" en-ligne etiquette="Calendrier" :options="casesCalendrier" />
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
              @apercu="(a) => (agenda = a)"
              @maj-profil="apresProfil"
              @semaine="routeur.replace({ query: { onglet: 'semaine' } })"
            />
          </template>
          <OngletRendezVous
            v-else-if="ongletActif === 'rendez-vous'"
            :rendez-vous="rendezVous"
            :siret-verifie="profil.siret_statut === 'verifie'"
            @maj="charger"
          />
          <!-- Semaine type : les horaires de chaque jour, puis [Changer les horaires] (grande maquette) -->
          <template v-else-if="ongletActif === 'semaine'">
            <div v-if="metiers.length > 1" class="cal-choix">
              <span class="doux petit" style="font-weight: 700">Semaine type :</span>
              <AppSegment v-model="metierDeLaSemaine" en-ligne etiquette="Semaine type" :options="metiers.map((m) => ({ valeur: m.id, texte: m.nom }))" />
            </div>
            <div v-if="changerSemaine" class="carte form p-[18px]">
              <h2>Changer les horaires {{ deMetier(metier.nom) }}</h2>
              <p class="doux">Vos horaires de chaque semaine. Un jour sans plage est fermé.</p>
              <EditeurSemaine :agenda="agenda" bouton="Enregistrer la semaine" annulable @maj="(a) => ((changerSemaine = false), apresChangement(a))" @annuler="changerSemaine = false" />
            </div>
            <template v-else>
              <div class="carte p-[18px]">
                <h2 style="margin-bottom: 6px">Mes horaires {{ deMetier(metier.nom) }}</h2>
                <div v-for="(nom, rang) in JOURS" :key="nom" class="reglage">
                  <div class="rl">
                    <b class="capitalize">{{ nom }}</b>
                    <span v-if="horairesDu(rang + 1)" style="text-align: right">{{ horairesDu(rang + 1) }}</span>
                    <span v-else class="puce p-neutre">Fermé</span>
                  </div>
                </div>
                <button type="button" class="btn btn-1" style="margin-top: 8px" @click="changerSemaine = true">Changer les horaires</button>
              </div>
              <p class="doux petit">Pour changer un seul jour (congés, rendez-vous perso…), cliquez sur ce jour dans l’onglet Calendrier.</p>
            </template>
          </template>
          <OngletPaiements v-else />
        </template>
      </template>
    </div>
  </GardePrestataire>
</template>
