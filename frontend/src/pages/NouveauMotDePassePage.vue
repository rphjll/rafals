<script setup lang="ts">
// Page ouverte par le lien du mail « mot de passe oublié » (.doc/ihm/RM-NOUVEAU-MOT-DE-PASSE-IHM.md).
import { ref } from 'vue'
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
const motDePasse = ref('')
const confirmation = ref('')
const erreur = ref('')
const envoiEnCours = ref(false)

async function enregistrer() {
  erreur.value = ''
  if (motDePasse.value !== confirmation.value) {
    erreur.value = 'Les deux mots de passe ne sont pas identiques.'
    return
  }
  envoiEnCours.value = true
  try {
    const reponse = await appelerServeur<{ message: string }>('/api/mot-de-passe/nouveau', {
      jeton: String(route.query.jeton ?? ''),
      mot_de_passe: motDePasse.value,
    })
    await chargerCompte() // tous les appareils ont été déconnectés, celui-ci aussi
    afficherMessage(reponse.message)
    routeur.push('/connexion')
  } catch (e) {
    erreur.value = messageErreur(e)
  } finally {
    envoiEnCours.value = false
  }
}
</script>

<template>
  <AppCarte titre="Nouveau mot de passe">
    <form class="flex flex-col gap-4" @submit.prevent="enregistrer">
      <AppChamp
        v-model="motDePasse"
        etiquette="Nouveau mot de passe"
        type="password"
        obligatoire
        autocomplete="new-password"
        aide="Au moins 10 caractères."
      />
      <AppChamp v-model="confirmation" etiquette="Le même, encore une fois" type="password" obligatoire autocomplete="new-password" />
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <AppBouton type="submit" pleine-largeur :occupe="envoiEnCours">Enregistrer le nouveau mot de passe</AppBouton>
    </form>
    <AppBouton variante="secondaire" pleine-largeur @click="routeur.push('/mot-de-passe-oublie')">
      Mon lien a expiré : en demander un autre
    </AppBouton>
  </AppCarte>
</template>
