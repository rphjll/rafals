<script setup lang="ts">
// Mes annonces (.doc/ihm/RM-MES-ANNONCES-IHM.md) : les annonces en ligne ou en pause, puis les retirées à part.
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import LigneAnnonce from '../components/annonces/LigneAnnonce.vue'
import GardePrestataire from '../components/prestataire/GardePrestataire.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppSection from '../components/ui/AppSection.vue'
import { useCompte } from '../composables/useCompte'
import type { AnnonceVisible } from '../outils/annonces'

const ANNONCES_EN_LIGNE_MAX = 20

const routeur = useRouter()
const { compte } = useCompte()
const annonces = ref<AnnonceVisible[] | null>(null)
const erreur = ref('')

async function charger() {
  if (!compte.value?.prestataire_id) return
  try {
    annonces.value = await appelerServeur<AnnonceVisible[]>('/api/moi/annonces')
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
onMounted(charger)
watch(compte, charger)

const actives = computed(() => annonces.value?.filter((a) => a.statut !== 'retiree') ?? [])
const retirees = computed(() => annonces.value?.filter((a) => a.statut === 'retiree') ?? [])
const enLigne = computed(() => actives.value.filter((a) => a.statut === 'en_ligne').length)

function remplacer(nouvelle: AnnonceVisible) {
  annonces.value = (annonces.value ?? []).map((a) => (a.id === nouvelle.id ? nouvelle : a))
}
</script>

<template>
  <GardePrestataire titre="Mes annonces">
    <p class="text-[13.5px] text-texte-doux">
      <RouterLink to="/proposer" class="hover:text-primaire">Mon activité</RouterLink> › Mes annonces
    </p>
    <div class="flex flex-wrap items-center justify-between gap-3">
      <h1 class="text-[28px] font-bold">Mes annonces</h1>
      <AppBouton @click="routeur.push('/mes-annonces/nouvelle')">Écrire une annonce</AppBouton>
    </div>
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>

    <template v-if="annonces">
      <p class="text-[13.5px] text-texte-doux">{{ enLigne }} annonces en ligne sur {{ ANNONCES_EN_LIGNE_MAX }} au plus.</p>
      <AppSection v-if="actives.length">
        <div class="flex flex-col divide-y divide-bord">
          <LigneAnnonce v-for="annonce in actives" :key="annonce.id" :annonce="annonce" @maj="remplacer" />
        </div>
      </AppSection>
      <AppSection v-else>
        <p class="text-texte-doux">Aucune annonce pour l'instant : écrivez la première pour que les clients vous trouvent.</p>
      </AppSection>

      <details v-if="retirees.length" class="rounded-rafals border border-bord bg-surface p-5">
        <summary class="min-h-[28px] cursor-pointer font-bold">Annonces retirées ({{ retirees.length }})</summary>
        <div class="flex flex-col divide-y divide-bord">
          <LigneAnnonce v-for="annonce in retirees" :key="annonce.id" :annonce="annonce" @maj="remplacer" />
        </div>
      </details>
    </template>
  </GardePrestataire>
</template>
