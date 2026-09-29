<script setup lang="ts">
// Administration (.doc/ihm/RM-ADMINISTRATION-IHM.md) : les onglets et le contrôle d'accès.
// Chaque onglet est un fichier de components/admin/.
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { appelerServeur } from '../api'
import OngletAccords from '../components/admin/OngletAccords.vue'
import OngletComptes from '../components/admin/OngletComptes.vue'
import OngletMetiers from '../components/admin/OngletMetiers.vue'
import OngletPrestataires from '../components/admin/OngletPrestataires.vue'
import OngletPropositions from '../components/admin/OngletPropositions.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppCarte from '../components/ui/AppCarte.vue'
import { useCompte } from '../composables/useCompte'

const route = useRoute()
const routeur = useRouter()
const { compte, chargementFait } = useCompte()

const onglets = [
  { id: 'accords', texte: 'Accords à vérifier', composant: OngletAccords },
  { id: 'comptes', texte: 'Comptes', composant: OngletComptes },
  { id: 'prestataires', texte: 'Prestataires', composant: OngletPrestataires },
  { id: 'propositions', texte: 'Propositions de métiers', composant: OngletPropositions },
  { id: 'metiers', texte: 'Métiers', composant: OngletMetiers },
] as const
const onglet = computed(() => onglets.find((o) => o.id === route.query.onglet) ?? onglets[0])

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

    <div class="flex flex-wrap gap-1.5 border-b border-bord" role="tablist">
      <button
        v-for="o in onglets"
        :key="o.id"
        type="button"
        role="tab"
        :aria-selected="onglet.id === o.id"
        class="-mb-px border-b-[3px] px-3 py-2.5 font-semibold"
        :class="onglet.id === o.id ? 'border-primaire text-primaire' : 'border-transparent text-texte-doux'"
        @click="routeur.replace({ query: o.id === 'accords' ? {} : { onglet: o.id } })"
      >
        {{ o.texte }}
        <span v-if="enAttente[o.id]" class="ml-1 rounded-full bg-accent px-[7px] py-px text-xs text-sur-etat">
          {{ enAttente[o.id] }}
        </span>
      </button>
    </div>

    <component :is="onglet.composant" :key="onglet.id" @maj="compter" />
  </div>
</template>
