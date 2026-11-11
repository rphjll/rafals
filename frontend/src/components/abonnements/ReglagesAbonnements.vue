<script setup lang="ts">
// « Paramètres › Mes abonnements » (.doc/ihm/RM-PARAMETRES-IHM.md ; RM-ABONNEMENTS.md) : les 3 notifications envoyées
// par les prestataires suivis, cochées une fois pour tous (demande de Raphael du 21/10/2026). Un prestataire précis se
// coupe avec [Rendre muet] dans « Mes abonnements ». Chaque clic est enregistré tout de suite.
import { onMounted, ref } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { CASES_NOTIFICATIONS, type NotificationsAbonnement } from '../../outils/abonnements'
import AppAlerte from '../ui/AppAlerte.vue'
import AppInterrupteur from '../ui/AppInterrupteur.vue'

const ADRESSE = '/api/moi/abonnements/notifications'
const { afficherMessage } = useMessage()
const cases = ref<NotificationsAbonnement | null>(null)
const erreur = ref('')

onMounted(async () => {
  try {
    cases.value = await appelerServeur<NotificationsAbonnement>(ADRESSE)
  } catch (e) {
    erreur.value = messageErreur(e)
  }
})

// Effet immédiat ; en cas d'échec, la case revient comme avant
async function changer(cle: keyof NotificationsAbonnement, valeur: boolean) {
  if (!cases.value) return
  const avant = { ...cases.value }
  cases.value[cle] = valeur
  try {
    cases.value = await appelerServeur<NotificationsAbonnement>(ADRESSE, cases.value)
    afficherMessage('Enregistré')
  } catch (e) {
    cases.value = avant
    afficherMessage(messageErreur(e), 'erreur')
  }
}
</script>

<template>
  <section id="abonnements" class="section">
    <h2>Mes abonnements : ce qui vous est envoyé</h2>
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <div v-if="cases" class="carte p-[18px]">
      <div v-for="c in CASES_NOTIFICATIONS" :key="c.cle" class="reglage">
        <div class="rl">
          <div><b>{{ c.titre }}</b><p class="doux petit">Ex. {{ c.exemple.replace('{nom}', 'Karim') }}</p></div>
          <AppInterrupteur :model-value="cases[c.cle]" :etiquette="c.titre" @update:model-value="changer(c.cle, $event)" />
        </div>
      </div>
      <p class="doux petit" style="padding-top: 8px">
        Pour ne plus rien recevoir d'un prestataire en particulier : [Rendre muet] dans <RouterLink to="/mes-abonnements" class="lien">Mes abonnements</RouterLink>.
      </p>
    </div>
  </section>
</template>
