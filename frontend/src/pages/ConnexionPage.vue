<script setup lang="ts">
// Connexion (.doc/ihm/RM-CONNEXION-IHM.md). Règles : RM-COMPTES.md.
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { messageErreur } from '../api'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppCarte from '../components/ui/AppCarte.vue'
import AppChamp from '../components/ui/AppChamp.vue'
import AppSeparateur from '../components/ui/AppSeparateur.vue'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'

const route = useRoute()
const routeur = useRouter()
// Retour à la page d'avant (ex. une annonce : /connexion?retour=/annonces/12) ; seulement une page de rafals
const retour = typeof route.query.retour === 'string' && /^\/(?!\/)/.test(route.query.retour) ? route.query.retour : '/'
const { seConnecter, compte } = useCompte()
const { afficherMessage } = useMessage()
const email = ref('')
const motDePasse = ref('')
const erreur = ref('')
const envoiEnCours = ref(false)

async function connexion() {
  erreur.value = ''
  envoiEnCours.value = true
  try {
    await seConnecter(email.value, motDePasse.value)
    afficherMessage(`Bonjour ${compte.value?.prenom} !`)
    routeur.push(retour)
  } catch (e) {
    erreur.value = messageErreur(e)
  } finally {
    envoiEnCours.value = false
  }
}
</script>

<template>
  <AppCarte titre="Se connecter">
    <form class="flex flex-col gap-4" @submit.prevent="connexion">
      <AppChamp v-model="email" etiquette="Adresse mail" type="email" obligatoire autocomplete="email" />
      <AppChamp v-model="motDePasse" etiquette="Mot de passe" type="password" obligatoire autocomplete="current-password" />
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <AppBouton type="submit" pleine-largeur :occupe="envoiEnCours">Se connecter</AppBouton>
    </form>
    <AppBouton variante="secondaire" pleine-largeur @click="routeur.push('/mot-de-passe-oublie')">Mot de passe oublié ?</AppBouton>
    <AppSeparateur>pas encore de compte ?</AppSeparateur>
    <AppBouton variante="secondaire" pleine-largeur @click="routeur.push('/inscription')">Créer mon compte</AppBouton>
  </AppCarte>
</template>
