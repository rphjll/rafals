<script setup lang="ts">
// Mes clients (.doc/ihm/RM-MON-ACTIVITE-IHM.md ; RM-MON-ACTIVITE.md § « Mes clients ») : pour un prestataire, les
// personnes qui ont eu un rendez-vous confirmé ou un devis avec lui sur rafals. Un clic sur un client ouvre son
// détail dessous. Le nom complet, le téléphone et l'adresse viennent du serveur seulement tant que la règle des
// coordonnées le permet (3 mois après le dernier rendez-vous).
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import DetailClient from '../components/clients/DetailClient.vue'
import GardePrestataire from '../components/prestataire/GardePrestataire.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppChamp from '../components/ui/AppChamp.vue'
import { useEcrireAuClient } from '../composables/useEcrireAuClient'
import { type ClientDuPrestataire, type FicheClient, resumeClient } from '../outils/activite'
import { formaterDate } from '../outils/dates'
import { initialesDe } from '../outils/noms'
import { montant } from '../outils/paiements'

const PAR_PAGE = 30

const routeur = useRouter()
const { enCours, erreurEcrire, ecrire } = useEcrireAuClient()
const clients = ref<ClientDuPrestataire[] | null>(null)
const erreur = ref('')
const recherche = ref('')
const nombreAffiches = ref(PAR_PAGE)

// Le client ouvert (un seul à la fois) ; son détail est lu au 1er clic, puis gardé
const ouvert = ref<number | null>(null)
const fiches = ref<Record<number, FicheClient>>({})
const erreurFiche = ref('')

const trouves = computed(() => {
  const mot = recherche.value.trim().toLowerCase()
  return (clients.value ?? []).filter((c) => !mot || c.nom.toLowerCase().includes(mot))
})

onMounted(async () => {
  try {
    clients.value = await appelerServeur<ClientDuPrestataire[]>('/api/moi/prestataire/clients')
  } catch (e) {
    erreur.value = messageErreur(e)
  }
})

function quand(client: ClientDuPrestataire): string {
  if (client.prochain_rendez_vous) return `Prochain rendez-vous : ${formaterDate(client.prochain_rendez_vous)}`
  if (client.dernier_rendez_vous) return `Dernier rendez-vous : ${formaterDate(client.dernier_rendez_vous)}`
  return 'Pas encore de rendez-vous'
}

async function basculer(client: ClientDuPrestataire) {
  erreurFiche.value = ''
  if (ouvert.value === client.client_id) {
    ouvert.value = null
    return
  }
  ouvert.value = client.client_id
  if (fiches.value[client.client_id]) return
  try {
    fiches.value[client.client_id] = await appelerServeur<FicheClient>(`/api/moi/prestataire/clients/${client.client_id}`)
  } catch (e) {
    erreurFiche.value = messageErreur(e)
  }
}
</script>

<template>
  <GardePrestataire titre="Mes clients">
    <div class="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
      <h1 class="text-[clamp(28px,4.5vw,40px)] font-black">Mes clients</h1>
      <span v-if="clients" class="text-texte-doux">{{ clients.length }} client{{ clients.length > 1 ? 's' : '' }}</span>
    </div>
    <p class="text-texte-doux">
      Les personnes qui ont eu un rendez-vous ou un devis avec vous sur rafals. Cliquez sur un client pour voir son détail.
      Le nom complet, le téléphone et l'adresse restent visibles 3 mois après le dernier rendez-vous.
    </p>
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>

    <template v-else-if="clients?.length">
      <AppChamp v-if="clients.length > 10" v-model="recherche" etiquette="Chercher un client" type="search" placeholder="ex. Julie" />
      <ul v-if="trouves.length" class="flex flex-col gap-3">
        <li v-for="client in trouves.slice(0, nombreAffiches)" :key="client.client_id" class="carte flex flex-col">
          <!-- La ligne du client : un clic ouvre ou referme son détail -->
          <button
            type="button"
            class="flex w-full flex-wrap items-center gap-x-4 gap-y-2 rounded-carte p-4 text-left hover:bg-fond sm:p-5"
            :aria-expanded="ouvert === client.client_id"
            :aria-controls="`detail-client-${client.client_id}`"
            @click="basculer(client)"
          >
            <span class="grid size-12 shrink-0 place-items-center rounded-full bg-primaire-doux font-bold text-primaire" aria-hidden="true">
              {{ initialesDe(client.nom) }}
            </span>
            <span class="flex min-w-0 flex-[1_1_220px] flex-col gap-0.5">
              <b class="text-[17px]">{{ client.nom }}</b>
              <span>{{ resumeClient(client, montant) }}</span>
              <span class="text-[13.5px] text-texte-doux">{{ quand(client) }}</span>
            </span>
            <span class="text-xl text-texte-doux" aria-hidden="true">{{ ouvert === client.client_id ? '▴' : '▾' }}</span>
          </button>

          <div v-if="ouvert === client.client_id" :id="`detail-client-${client.client_id}`" class="flex flex-col gap-4 border-t-2 border-fond p-4 sm:p-5">
            <AppAlerte v-if="erreurFiche">{{ erreurFiche }}</AppAlerte>
            <p v-else-if="!fiches[client.client_id]" class="text-texte-doux">Lecture…</p>
            <DetailClient v-else :fiche="fiches[client.client_id]!" />
            <div class="flex flex-wrap gap-2">
              <AppBouton v-if="client.peut_ecrire" :occupe="enCours === client.client_id" @click="ecrire(client.client_id)">
                Écrire à {{ client.nom.split(' ')[0] }}
              </AppBouton>
              <AppBouton variante="secondaire" @click="routeur.push(`/clients/${client.client_id}`)">Voir le profil</AppBouton>
            </div>
            <AppAlerte v-if="erreurEcrire?.clientId === client.client_id">{{ erreurEcrire.texte }}</AppAlerte>
          </div>
        </li>
      </ul>
      <p v-else class="rounded-carte border-2 border-dashed border-bord p-5 text-texte-doux">Aucun client ne s'appelle « {{ recherche.trim() }} ».</p>
      <div v-if="trouves.length > nombreAffiches">
        <AppBouton variante="secondaire" @click="nombreAffiches += PAR_PAGE">Voir les {{ Math.min(PAR_PAGE, trouves.length - nombreAffiches) }} suivants</AppBouton>
      </div>
    </template>

    <p v-else-if="clients" class="rounded-carte border-2 border-dashed border-bord p-5 text-texte-doux">
      Pas encore de client. Dès qu'un client confirme un rendez-vous ou reçoit un devis de votre part, il apparaît ici.
    </p>
  </GardePrestataire>
</template>
