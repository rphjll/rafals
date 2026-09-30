<script setup lang="ts">
// Administration (.doc/ihm/RM-ADMINISTRATION-IHM.md) : les onglets et le contrôle d'accès.
// Chaque onglet est un fichier de components/admin/.
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur } from '../api'
import OngletAccords from '../components/admin/OngletAccords.vue'
import OngletComptes from '../components/admin/OngletComptes.vue'
import OngletMetiers from '../components/admin/OngletMetiers.vue'
import OngletPrestataires from '../components/admin/OngletPrestataires.vue'
import OngletPropositions from '../components/admin/OngletPropositions.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppCarte from '../components/ui/AppCarte.vue'
import AppOnglets from '../components/ui/AppOnglets.vue'
import { useCompte } from '../composables/useCompte'

const routeur = useRouter()
const { compte, chargementFait } = useCompte()

const onglets = [
  { id: 'accords', texte: 'Accords à vérifier', composant: OngletAccords },
  { id: 'comptes', texte: 'Comptes', composant: OngletComptes },
  { id: 'prestataires', texte: 'Prestataires', composant: OngletPrestataires },
  { id: 'propositions', texte: 'Propositions de métiers', composant: OngletPropositions },
  { id: 'metiers', texte: 'Métiers', composant: OngletMetiers },
] as const
const ongletActif = ref('accords')
const onglet = computed(() => onglets.find((o) => o.id === ongletActif.value) ?? onglets[0])

// Compteurs orange des choses qui attendent une décision
const enAttente = ref<Record<string, number>>({})
async function compter() {
  if (!compte.value?.est_administrateur) return
  const [accords, propositions] = await Promise.all([
    appelerServeur<unknown[]>('/api/admin/accords'),
    appelerServeur<unknown[]>('/api/admin/propositions'),
  ])
  enAttente.value = { accords: accords.length, propositions: propositions.length }
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

    <component :is="onglet.composant" :key="onglet.id" @maj="compter" />
  </div>
</template>
