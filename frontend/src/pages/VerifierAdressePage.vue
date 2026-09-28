<script setup lang="ts">
// Page ouverte par le lien du mail de vérification (.doc/ihm/RM-VERIFIER-ADRESSE-IHM.md).
// Elle vérifie toute seule à l'ouverture, sans rien demander.
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppCarte from '../components/ui/AppCarte.vue'
import AppChamp from '../components/ui/AppChamp.vue'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'

const route = useRoute()
const routeur = useRouter()
const { chargerCompte } = useCompte()
const { afficherMessage } = useMessage()
const etat = ref<'en-cours' | 'ok' | 'erreur'>('en-cours')
const erreur = ref('')
const email = ref('')

onMounted(async () => {
  try {
    await appelerServeur('/api/comptes/verification', { jeton: String(route.query.jeton ?? '') })
    etat.value = 'ok'
    await chargerCompte() // si la personne est connectée, le bandeau « vérifiez votre adresse » disparaît
  } catch (e) {
    erreur.value = messageErreur(e)
    etat.value = 'erreur'
  }
})

async function nouveauLien() {
  try {
    afficherMessage((await appelerServeur<{ message: string }>('/api/comptes/verification/renvoi', { email: email.value })).message)
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}
</script>

<template>
  <AppCarte v-if="etat === 'en-cours'" titre="Vérification de votre adresse…" />
  <AppCarte v-else-if="etat === 'ok'" titre="Adresse vérifiée">
    <AppAlerte etat="ok">Votre adresse mail est vérifiée.</AppAlerte>
    <AppBouton pleine-largeur @click="routeur.push('/connexion')">Se connecter</AppBouton>
  </AppCarte>
  <AppCarte v-else titre="Ce lien ne marche pas">
    <AppAlerte>{{ erreur }}</AppAlerte>
    <form class="flex flex-col gap-4" @submit.prevent="nouveauLien">
      <AppChamp v-model="email" etiquette="Adresse mail" type="email" obligatoire autocomplete="email" />
      <AppBouton type="submit" pleine-largeur>Recevoir un nouveau lien</AppBouton>
    </form>
  </AppCarte>
</template>
