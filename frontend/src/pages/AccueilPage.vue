<script setup lang="ts">
// Accueil provisoire (.doc/ihm/RM-ACCUEIL-IHM.md) : la recherche arrivera au niveau 4.
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import AppBadge from '../components/ui/AppBadge.vue'
import AppBouton from '../components/ui/AppBouton.vue'

const routeur = useRouter()
const etatServeur = ref('Vérification du serveur…')
const serveurOk = ref<boolean | null>(null)

onMounted(async () => {
  try {
    const reponse = await fetch('/api/etat')
    if (!reponse.ok) throw new Error(String(reponse.status))
    etatServeur.value = (await reponse.json()).message
    serveurOk.value = true
  } catch {
    etatServeur.value = 'Le serveur ne répond pas. Relance demarrer.bat.'
    serveurOk.value = false
  }
})
</script>

<template>
  <section class="flex flex-col gap-4 py-6">
    <h1 class="max-w-[18ch] text-[clamp(28px,5vw,42px)] leading-tight font-bold">Le bon prestataire, près de chez vous.</h1>
    <p class="max-w-[52ch] text-[17px] text-texte-doux">
      Plombiers, femmes de ménage, coiffeuses à domicile… rafals est en construction : la recherche arrive bientôt.
    </p>
    <div>
      <AppBadge :etat="serveurOk === null ? 'neutre' : serveurOk ? 'ok' : 'erreur'">{{ etatServeur }}</AppBadge>
    </div>
    <div>
      <AppBouton variante="secondaire" @click="routeur.push('/catalogue')">Voir le catalogue des composants</AppBouton>
    </div>
  </section>
</template>
