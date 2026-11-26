<script setup lang="ts">
// Sans SIRET vérifié, un métier qui en demande un : on le dit tout de suite, et on propose le métier à prendre à la
// place s'il existe (RM-METIERS-SANS-SIRET.md, demande de Raphael du 25/11/2026 : « pour plombier ca serai bricoleur »).
// Ex. « Plombier » → [Prendre « Homme toutes mains / Multiservices »] ; « Infirmier » → pas d'équivalent.
// Servi dans « Ajouter un métier » et dans le formulaire du profil.
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur } from '../../api'
import type { MetierVisible } from '../../composables/useMetiers'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'

const props = defineProps<{ metier: { id: number; nom: string } | null }>()
const emit = defineEmits<{ choisir: [metier: MetierVisible] }>()
const routeur = useRouter()

interface SansSiret {
  siret_obligatoire: boolean
  equivalent: MetierVisible | null
}
const info = ref<SansSiret | null>(null)

watch(
  () => props.metier?.id,
  async (id) => {
    info.value = null
    if (id) info.value = await appelerServeur<SansSiret>(`/api/metiers/${id}/sans-siret`).catch(() => null)
  },
  { immediate: true },
)
</script>

<template>
  <AppAlerte v-if="metier && info?.siret_obligatoire" etat="attente">
    <p class="m-0 basis-full">
      « {{ metier.nom }} » demande un SIRET : sans SIRET, vous ne pourrez pas répondre à ses demandes.
      <template v-if="info.equivalent">Choisissez plutôt « {{ info.equivalent.nom }} » (petits services, sans SIRET).</template>
      <template v-else>Ce métier n'a pas d'équivalent sans SIRET : créez votre auto-entreprise pour l'exercer.</template>
    </p>
    <AppBouton v-if="info.equivalent" @click="emit('choisir', info.equivalent)">Prendre « {{ info.equivalent.nom }} »</AppBouton>
    <AppBouton variante="secondaire" @click="routeur.push('/creer-mon-auto-entreprise')">Créer mon auto-entreprise</AppBouton>
  </AppAlerte>
</template>
