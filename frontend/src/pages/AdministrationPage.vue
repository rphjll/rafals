<script setup lang="ts">
// Administration (.doc/ihm/RM-ADMINISTRATION-IHM.md) : les onglets et le contrôle d'accès.
// Chaque onglet est un fichier de components/admin/.
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur } from '../api'
import OngletAbsences from '../components/admin/OngletAbsences.vue'
import OngletAccords from '../components/admin/OngletAccords.vue'
import OngletAvisSignales from '../components/admin/OngletAvisSignales.vue'
import OngletComptes from '../components/admin/OngletComptes.vue'
import OngletMetiers from '../components/admin/OngletMetiers.vue'
import OngletMotsInterdits from '../components/admin/OngletMotsInterdits.vue'
import OngletProblemesDevis from '../components/admin/OngletProblemesDevis.vue'
import OngletPrestataires from '../components/admin/OngletPrestataires.vue'
import OngletSignalements from '../components/admin/OngletSignalements.vue'
import OngletTableauDeBord from '../components/admin/OngletTableauDeBord.vue'
import OngletTousLesPaiements from '../components/admin/OngletTousLesPaiements.vue'
import OngletPropositions from '../components/admin/OngletPropositions.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppCarte from '../components/ui/AppCarte.vue'
import AppOnglets from '../components/ui/AppOnglets.vue'
import { useCompte } from '../composables/useCompte'

const routeur = useRouter()
const { compte, chargementFait } = useCompte()

const onglets = [
  { id: 'tableau', texte: 'Tableau de bord', composant: OngletTableauDeBord },
  { id: 'accords', texte: 'Accords à vérifier', composant: OngletAccords },
  { id: 'comptes', texte: 'Comptes', composant: OngletComptes },
  { id: 'prestataires', texte: 'Prestataires', composant: OngletPrestataires },
  { id: 'absences', texte: 'Absences contestées', composant: OngletAbsences },
  { id: 'avis', texte: 'Avis signalés', composant: OngletAvisSignales },
  { id: 'signalements', texte: 'Signalements', composant: OngletSignalements },
  { id: 'mots', texte: 'Mots interdits', composant: OngletMotsInterdits },
  { id: 'devis', texte: 'Problèmes de devis', composant: OngletProblemesDevis },
  { id: 'propositions', texte: 'Propositions de métiers', composant: OngletPropositions },
  { id: 'metiers', texte: 'Métiers', composant: OngletMetiers },
  { id: 'paiements', texte: 'Paiements', composant: OngletTousLesPaiements },
] as const
const ongletActif = ref('tableau')
const onglet = computed(() => onglets.find((o) => o.id === ongletActif.value) ?? onglets[0])

// Compteurs orange des choses qui attendent une décision
const enAttente = ref<Record<string, number>>({})
async function compter() {
  if (!compte.value?.est_administrateur) return
  const [accords, propositions, contestations, signales, problemes, signalements] = await Promise.all([
    appelerServeur<unknown[]>('/api/admin/accords'),
    appelerServeur<unknown[]>('/api/admin/propositions'),
    appelerServeur<unknown[]>('/api/admin/contestations'),
    appelerServeur<unknown[]>('/api/admin/avis-signales'),
    appelerServeur<unknown[]>('/api/admin/devis-problemes'),
    appelerServeur<unknown[]>('/api/admin/signalements'),
  ])
  enAttente.value = {
    accords: accords.length, propositions: propositions.length, absences: contestations.length, avis: signales.length,
    devis: problemes.length, signalements: signalements.length,
  }
}
onMounted(compter)
watch(compte, compter)
</script>

<template>
  <AppCarte
    v-if="chargementFait && !compte?.est_administrateur"
    titre="Réservé aux administrateurs"
    intro="Cette page n'est accessible qu'aux administrateurs de rafals."
  >
    <AppBouton pleine-largeur @click="routeur.push('/')">Retour à l'accueil</AppBouton>
  </AppCarte>

  <div v-else-if="compte" class="flex flex-col gap-5">
    <h1 class="text-[28px] font-bold">Administration</h1>

    <AppOnglets v-model="ongletActif" :onglets="onglets" :compteurs="enAttente" />

    <component :is="onglet.composant" :key="onglet.id" @maj="compter" @aller="(id: string) => (ongletActif = id)" />
  </div>
</template>
