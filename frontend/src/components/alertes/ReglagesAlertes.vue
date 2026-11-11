<script setup lang="ts">
// Notifications d'un prestataire, dans « Paramètres » (.doc/ihm/RM-ALERTES-IHM.md ; RM-ALERTES.md) : être prévenu des
// nouvelles demandes. Ancienne page « Alertes » de « Mon activité », déplacée le 21/10/2026 (demande de Raphael). Écrit en questions
// complètes, avec la conséquence de chaque réponse : pour quels métiers, et comment (un mail à chaque demande, un seul
// mail le soir, aucun mail). Chaque clic est enregistré tout de suite.
import { onMounted, ref } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import AppAlerte from '../ui/AppAlerte.vue'
import AppInterrupteur from '../ui/AppInterrupteur.vue'
import AppSegment from '../ui/AppSegment.vue'
import CarteNotifications from './CarteNotifications.vue'

interface Alertes {
  alerte_mail: 'chaque_demande' | 'resume' | 'aucun'
  metiers: { id: number; nom: string; prevenu: boolean }[]
  distance_km: number
  ville: string
}

const MAILS = [
  { valeur: 'chaque_demande' as const, texte: 'À chaque demande' },
  { valeur: 'resume' as const, texte: 'Un mail le soir à 18 h' },
  { valeur: 'aucun' as const, texte: 'Aucun mail' },
]

const { afficherMessage } = useMessage()
const alertes = ref<Alertes | null>(null)
const erreur = ref('')

onMounted(async () => {
  try {
    alertes.value = await appelerServeur<Alertes>('/api/moi/prestataire/alertes')
  } catch (e) {
    erreur.value = messageErreur(e)
  }
})

async function enregistrer(suivant: Alertes) {
  try {
    alertes.value = await appelerServeur<Alertes>('/api/moi/prestataire/alertes', {
      alerte_mail: suivant.alerte_mail,
      metiers_coupes: suivant.metiers.filter((m) => !m.prevenu).map((m) => m.id),
    })
    afficherMessage('Alertes enregistrées.')
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}

function choisirMetier(id: number, reponse: string) {
  if (!alertes.value) return
  enregistrer({ ...alertes.value, metiers: alertes.value.metiers.map((m) => (m.id === id ? { ...m, prevenu: reponse === 'oui' } : m)) })
}
function choisirMail(mail: Alertes['alerte_mail']) {
  if (alertes.value && mail !== alertes.value.alerte_mail) enregistrer({ ...alertes.value, alerte_mail: mail })
}
</script>

<template>
  <section id="notifications" class="section">
    <h2>Nouvelles demandes</h2>
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <div v-if="alertes" class="carte p-[18px]">
      <div v-for="metier in alertes.metiers" :key="metier.id" class="reglage">
        <div class="rl">
          <div>
            <b>Un client cherche « {{ metier.nom }} »</b>
            <p class="doux petit">
              <template v-if="metier.prevenu">Vous êtes prévenu dans votre rayon de {{ alertes.distance_km }} km autour de {{ alertes.ville }}.</template>
              <template v-else>Vous ne recevez rien. Les demandes restent dans « Demandes ».</template>
            </p>
          </div>
          <AppInterrupteur :model-value="metier.prevenu" :etiquette="`Être prévenu des demandes « ${metier.nom} »`" @update:model-value="(oui) => choisirMetier(metier.id, oui ? 'oui' : 'non')" />
        </div>
      </div>
      <div class="reglage">
        <b>Par mail</b>
        <AppSegment :model-value="alertes.alerte_mail" etiquette="Par mail" :options="MAILS" @update:model-value="choisirMail" />
        <p class="exemple">
          <template v-if="alertes.alerte_mail === 'chaque_demande'">Un mail pour chaque nouvelle demande. Au-delà de 20 dans la journée, les suivantes arrivent dans un seul mail à 18 h.</template>
          <template v-else-if="alertes.alerte_mail === 'resume'">15 demandes dans la journée : 1 mail au lieu de 15, à 18 h.</template>
          <template v-else>Aucun mail. Les mails de vos conversations, propositions et rendez-vous, eux, continuent.</template>
        </p>
      </div>
    </div>
    <CarteNotifications
      titre="Sur ce téléphone"
      exemple="Ex. « Nouvelle demande : Fuite sous l'évier, Talence (5 km) »."
    />
  </section>
</template>
