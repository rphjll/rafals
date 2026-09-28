<script setup lang="ts">
// Mot de passe oublié (.doc/ihm/RM-MOT-DE-PASSE-OUBLIE-IHM.md). Règles : RM-COMPTES.md.
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppCarte from '../components/ui/AppCarte.vue'
import AppChamp from '../components/ui/AppChamp.vue'

const routeur = useRouter()
const email = ref('')
const erreur = ref('')
const confirmation = ref('')
const envoiEnCours = ref(false)

async function demanderLien() {
  erreur.value = ''
  envoiEnCours.value = true
  try {
    confirmation.value = (await appelerServeur<{ message: string }>('/api/mot-de-passe/oubli', { email: email.value })).message
  } catch (e) {
    erreur.value = messageErreur(e)
  } finally {
    envoiEnCours.value = false
  }
}
</script>

<template>
  <AppCarte titre="Mot de passe oublié" intro="Indiquez votre adresse : nous vous envoyons un lien pour en choisir un nouveau.">
    <form class="flex flex-col gap-4" @submit.prevent="demanderLien">
      <AppChamp v-model="email" etiquette="Adresse mail" type="email" obligatoire autocomplete="email" />
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <AppAlerte v-if="confirmation" etat="ok">{{ confirmation }}</AppAlerte>
      <AppBouton type="submit" pleine-largeur :occupe="envoiEnCours">Recevoir un lien</AppBouton>
    </form>
    <AppBouton variante="secondaire" pleine-largeur @click="routeur.push('/connexion')">Retour à la connexion</AppBouton>
  </AppCarte>
</template>
