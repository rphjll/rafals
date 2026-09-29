<script setup lang="ts">
// Accueil provisoire (.doc/ihm/RM-ACCUEIL-IHM.md) : la recherche arrivera au niveau 4.
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBadge from '../components/ui/AppBadge.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'

const routeur = useRouter()
const { compte, renvoyerLienVerification } = useCompte()
const { afficherMessage } = useMessage()
const etatServeur = ref('Vérification du serveur…')
const serveurOk = ref<boolean | null>(null)

onMounted(async () => {
  try {
    etatServeur.value = (await appelerServeur<{ message: string }>('/api/etat')).message
    serveurOk.value = true
  } catch {
    etatServeur.value = 'Le serveur ne répond pas. Relance demarrer.bat.'
    serveurOk.value = false
  }
})

async function renvoyerLien() {
  try {
    afficherMessage(await renvoyerLienVerification(compte.value?.email ?? ''))
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}
</script>

<template>
  <section class="flex flex-col gap-4 py-6">
    <AppAlerte v-if="compte && !compte.email_verifie" etat="attente">
      Vérifiez votre adresse mail pour pouvoir réserver.
      <AppBouton variante="secondaire" @click="renvoyerLien">Renvoyer le lien</AppBouton>
    </AppAlerte>
    <h1 class="max-w-[18ch] text-[clamp(28px,5vw,42px)] leading-tight font-bold">Le bon prestataire, près de chez vous.</h1>
    <p class="max-w-[52ch] text-[17px] text-texte-doux">
      Plombiers, femmes de ménage, coiffeuses à domicile… rafals est en construction : la recherche arrive bientôt.
    </p>
    <div>
      <AppBadge :etat="serveurOk === null ? 'neutre' : serveurOk ? 'ok' : 'erreur'">{{ etatServeur }}</AppBadge>
    </div>
    <div class="flex flex-wrap gap-3">
      <AppBouton v-if="!compte" @click="routeur.push('/inscription')">Créer mon compte</AppBouton>
      <AppBouton variante="secondaire" @click="routeur.push('/catalogue')">Voir le catalogue des composants</AppBouton>
    </div>
  </section>
</template>
