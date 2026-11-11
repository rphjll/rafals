<script setup lang="ts">
// Mes demandes (.doc/ihm/RM-DEMANDES-IHM.md ; RM-DEMANDES.md) : la page. La liste elle-même est dans
// ListeMesDemandes (aussi montrée dans l'onglet « Mes demandes » de l'accueil). On publie depuis l'accueil.
import { useRouter } from 'vue-router'
import ListeMesDemandes from '../components/demandes/ListeMesDemandes.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import { useCompte } from '../composables/useCompte'

const routeur = useRouter()
const { compte, chargementFait } = useCompte()
</script>

<template>
  <div class="mx-auto flex max-w-[760px] flex-col gap-5">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <h1 class="text-[clamp(28px,4.5vw,40px)] font-black">Mes demandes</h1>
      <AppBouton variante="accent" @click="routeur.push('/')">Publier une demande</AppBouton>
    </div>
    <template v-if="chargementFait && !compte">
      <AppAlerte etat="neutre">Connectez-vous pour voir vos demandes.</AppAlerte>
      <div><AppBouton @click="routeur.push('/connexion')">Se connecter</AppBouton></div>
    </template>
    <ListeMesDemandes v-else />
  </div>
</template>
