<script setup lang="ts">
// Mon compte (.doc/ihm/RM-COMPTE-IHM.md) : une carte par sujet, chacune dans components/compte/.
import { useRouter } from 'vue-router'
import CarteAdresse from '../components/CarteAdresse.vue'
import CarteAbsences from '../components/compte/CarteAbsences.vue'
import CarteAccordParental from '../components/compte/CarteAccordParental.vue'
import CarteDonnees from '../components/compte/CarteDonnees.vue'
import CarteFermeture from '../components/compte/CarteFermeture.vue'
import CarteInformations from '../components/compte/CarteInformations.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppCarte from '../components/ui/AppCarte.vue'
import { useCompte } from '../composables/useCompte'

const routeur = useRouter()
const { compte, chargementFait } = useCompte()
</script>

<template>
  <AppCarte v-if="chargementFait && !compte" titre="Mon compte" intro="Connectez-vous pour voir votre compte.">
    <AppBouton pleine-largeur @click="routeur.push('/connexion')">Se connecter</AppBouton>
  </AppCarte>

  <div v-else-if="compte" class="flex flex-col gap-[18px]">
    <h1 class="text-[28px] font-bold">Mon compte</h1>
    <CarteInformations :compte="compte" />
    <CarteAccordParental v-if="compte.accord_parental_necessaire" :compte="compte" />
    <CarteAdresse
      titre="Mon adresse"
      chemin="/api/moi/adresse"
      texte-vide="Aucune adresse enregistrée : elle vous sera demandée quand vous réserverez un service à domicile."
      texte-ajouter="Ajouter mon adresse"
      texte-effacer="Effacer mon adresse"
    />
    <CarteAbsences />
    <CarteDonnees />
    <CarteFermeture />
  </div>
</template>
