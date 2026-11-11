<script setup lang="ts">
// Mes clients (.doc/ihm/RM-MON-ACTIVITE-IHM.md ; RM-MON-ACTIVITE.md § « Mes clients ») : pour un prestataire, les
// personnes qui ont eu un rendez-vous confirmé ou un devis avec lui sur rafals. Un clic sur un client ouvre son
// détail dessous. Le nom complet, le téléphone et l'adresse viennent du serveur seulement tant que la règle des
// coordonnées le permet (3 mois après le dernier rendez-vous).
import EnteteActivite from '../components/EnteteActivite.vue'
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
import AppIcone from '../components/ui/AppIcone.vue'
import AppInitiales from '../components/ui/AppInitiales.vue'
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
    <EnteteActivite titre="Mes clients" :texte="clients ? `${clients.length} personne${clients.length > 1 ? 's' : ''} pour qui vous avez déjà travaillé.` : 'Les personnes pour qui vous avez déjà travaillé.'" />
    <p class="doux petit">Cliquez sur un client pour voir son détail. Le nom complet, le téléphone et l'adresse restent visibles 3 mois après le dernier rendez-vous.</p>
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>

    <template v-else-if="clients?.length">
      <AppChamp v-if="clients.length > 10" v-model="recherche" etiquette="Chercher un client" type="search" placeholder="ex. Julie" />
      <div v-if="trouves.length" class="liste">
        <div v-for="client in trouves.slice(0, nombreAffiches)" :key="client.client_id" class="dep" :class="{ ouvert: ouvert === client.client_id }">
          <!-- La ligne du client : un clic ouvre ou referme son détail -->
          <button type="button" class="dep-tete" :aria-expanded="ouvert === client.client_id" :aria-controls="`detail-client-${client.client_id}`" @click="basculer(client)">
            <AppInitiales :nom="client.nom" />
            <span class="txt"><b>{{ client.nom }}</b><span>{{ resumeClient(client, montant) }} · {{ quand(client) }}</span></span>
            <span class="chev" aria-hidden="true">›</span>
          </button>
          <div v-if="ouvert === client.client_id" :id="`detail-client-${client.client_id}`" class="dep-corps">
            <AppAlerte v-if="erreurFiche">{{ erreurFiche }}</AppAlerte>
            <p v-else-if="!fiches[client.client_id]" class="doux">Lecture…</p>
            <DetailClient v-else :fiche="fiches[client.client_id]!" />
            <div class="btns">
              <AppBouton v-if="client.peut_ecrire" petit :occupe="enCours === client.client_id" @click="ecrire(client.client_id)"><AppIcone nom="messages" />Écrire</AppBouton>
              <AppBouton variante="secondaire" petit @click="routeur.push(`/clients/${client.client_id}`)">Voir le profil</AppBouton>
            </div>
            <AppAlerte v-if="erreurEcrire?.clientId === client.client_id">{{ erreurEcrire.texte }}</AppAlerte>
          </div>
        </div>
      </div>
      <p v-else class="carte vide">Aucun client ne s'appelle « {{ recherche.trim() }} ».</p>
      <div v-if="trouves.length > nombreAffiches">
        <AppBouton variante="secondaire" @click="nombreAffiches += PAR_PAGE">Voir les {{ Math.min(PAR_PAGE, trouves.length - nombreAffiches) }} suivants</AppBouton>
      </div>
    </template>

    <p v-else-if="clients" class="carte vide">
      Pas encore de client. Dès qu'un client confirme un rendez-vous ou reçoit un devis de votre part, il apparaît ici.
    </p>
  </GardePrestataire>
</template>
