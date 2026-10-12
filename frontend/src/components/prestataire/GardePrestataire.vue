<script setup lang="ts">
// Pages réservées aux prestataires (Mon agenda…) : pas connecté → se connecter ; pas prestataire → proposer ses
// services ; sinon le contenu de la page.
import { useRouter } from 'vue-router'
import { useCompte } from '../../composables/useCompte'
import AppBouton from '../ui/AppBouton.vue'
import AppCarte from '../ui/AppCarte.vue'

// « large » : toute la largeur de la page (1080 px), ex. le calendrier avec le détail du jour à côté
defineProps<{ titre: string; large?: boolean }>()
const routeur = useRouter()
const { compte, chargementFait } = useCompte()
</script>

<template>
  <AppCarte v-if="chargementFait && !compte" :titre="titre" intro="Connectez-vous pour gérer votre activité.">
    <AppBouton pleine-largeur @click="routeur.push('/connexion')">Se connecter</AppBouton>
  </AppCarte>
  <AppCarte v-else-if="compte && !compte.prestataire_id" :titre="titre" intro="Créez d'abord votre profil de prestataire.">
    <AppBouton pleine-largeur @click="routeur.push('/proposer')">Proposer mes services</AppBouton>
  </AppCarte>
  <div v-else-if="compte" class="mx-auto flex w-full flex-col gap-4" :class="large ? 'max-w-[1080px]' : 'max-w-[720px]'">
    <slot />
  </div>
</template>
