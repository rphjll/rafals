<script setup lang="ts">
// Profil d'un client, vu par un de ses prestataires (.doc/ihm/RM-MON-ACTIVITE-IHM.md ; RM-MON-ACTIVITE.md § « Mes
// clients ») : la même mise en page que la page publique d'un prestataire, avec ce que le client a renseigné.
// Ce n'est pas une page publique : le serveur ne répond qu'à un prestataire qui a ce client.
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import DetailClient from '../components/clients/DetailClient.vue'
import GardePrestataire from '../components/prestataire/GardePrestataire.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppSection from '../components/ui/AppSection.vue'
import { useEcrireAuClient } from '../composables/useEcrireAuClient'
import { MOIS } from '../outils/agenda'
import type { FicheClient } from '../outils/activite'
import { initialesDe } from '../outils/noms'

const route = useRoute()
const routeur = useRouter()
const { enCours, erreurEcrire, ecrire } = useEcrireAuClient()
const fiche = ref<FicheClient | null>(null)
const erreur = ref('')

watch(
  () => route.params.id,
  async (id) => {
    erreur.value = ''
    fiche.value = null
    try {
      fiche.value = await appelerServeur<FicheClient>(`/api/moi/prestataire/clients/${id}`)
    } catch (e) {
      erreur.value = messageErreur(e) // ex. « Cette personne ne fait pas partie de vos clients. »
    }
  },
  { immediate: true },
)

const prenom = computed(() => fiche.value?.nom.split(' ')[0] ?? '')
// « octobre 2026 », à l'heure de Paris
const depuis = computed(() => {
  if (!fiche.value) return ''
  const [annee, mois] = new Date(fiche.value.inscrit_le).toLocaleDateString('sv-SE', { timeZone: 'Europe/Paris' }).split('-')
  return `${MOIS[Number(mois) - 1]} ${annee}`
})
</script>

<template>
  <GardePrestataire titre="Profil d'un client" large>
    <p class="text-[13.5px] text-texte-doux">
      <RouterLink to="/mes-clients" class="hover:text-primaire">‹ Mes clients</RouterLink>
    </p>
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>

    <template v-if="fiche">
      <!-- Ordinateur : le profil à gauche, la carte « Joindre Julie » à droite, qui reste visible -->
      <div class="grid items-start gap-8" :class="fiche.peut_ecrire ? 'md:grid-cols-[1fr_340px]' : ''">
        <div class="flex min-w-0 flex-col gap-6">
          <div class="grid items-center gap-5 sm:grid-cols-[auto_1fr]">
            <span class="grid size-24 shrink-0 place-items-center rounded-full bg-primaire-doux text-3xl font-bold text-primaire" aria-hidden="true">
              {{ initialesDe(fiche.nom) }}
            </span>
            <div class="flex min-w-0 flex-col gap-1.5">
              <h1 class="text-[clamp(28px,4.5vw,40px)] leading-tight font-black">{{ fiche.nom }}</h1>
              <p class="text-texte-doux">Client · sur rafals depuis {{ depuis }}</p>
            </div>
          </div>
          <AppSection titre="Avec vous">
            <DetailClient :fiche="fiche" />
          </AppSection>
        </div>

        <aside v-if="fiche.peut_ecrire" class="flex flex-col gap-3 rounded-carte bg-fonce p-6 text-sur-fonce md:sticky md:top-24">
          <h2 class="text-[22px] font-extrabold">Joindre {{ prenom }}</h2>
          <AppBouton variante="accent" pleine-largeur :occupe="enCours === fiche.client_id" @click="ecrire(fiche.client_id)">
            Écrire à {{ prenom }}
          </AppBouton>
          <AppAlerte v-if="erreurEcrire">{{ erreurEcrire.texte }}</AppAlerte>
          <p v-if="fiche.telephone" class="text-[17px] font-bold tabular-nums">Tél. {{ fiche.telephone }}</p>
          <p class="text-[13.5px] text-sur-fonce-doux">
            Son nom complet, son téléphone et son adresse restent visibles 3 mois après votre dernier rendez-vous.
          </p>
        </aside>
      </div>

      <AppSection titre="Ses demandes en ligne">
        <p v-if="!fiche.demandes.length" class="text-texte-doux">{{ prenom }} n'a pas de demande en ligne en ce moment.</p>
        <ul v-else class="flex flex-col divide-y divide-bord">
          <li v-for="d in fiche.demandes" :key="d.id" class="flex flex-wrap items-center justify-between gap-3 py-2.5 first:pt-0">
            <span><b>{{ d.titre }}</b> <span class="text-texte-doux">· {{ d.ville }}</span></span>
            <AppBouton variante="secondaire" @click="routeur.push('/')">Voir sur l'accueil</AppBouton>
          </li>
        </ul>
      </AppSection>
    </template>
  </GardePrestataire>
</template>
