<script setup lang="ts">
// Alertes : être prévenu des nouvelles demandes (.doc/ihm/RM-ALERTES-IHM.md ; RM-ALERTES.md). Écrit en questions
// complètes, avec la conséquence de chaque réponse : pour quels métiers, et comment (un mail à chaque demande, un seul
// mail le soir, aucun mail). Chaque clic est enregistré tout de suite.
import { onMounted, ref } from 'vue'
import { appelerServeur, messageErreur } from '../api'
import CarteNotifications from '../components/alertes/CarteNotifications.vue'
import GardePrestataire from '../components/prestataire/GardePrestataire.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppChoix from '../components/ui/AppChoix.vue'
import AppSection from '../components/ui/AppSection.vue'
import AppSegment from '../components/ui/AppSegment.vue'
import { useMessage } from '../composables/useMessage'

interface Alertes {
  alerte_mail: 'chaque_demande' | 'resume' | 'aucun'
  metiers: { id: number; nom: string; prevenu: boolean }[]
  distance_km: number
  ville: string
}

const OUI_NON = [
  { valeur: 'oui', texte: 'Me prévenir' },
  { valeur: 'non', texte: 'Ne pas me prévenir' },
]
const MAILS = [
  { valeur: 'chaque_demande' as const, texte: 'Un mail à chaque demande' },
  { valeur: 'resume' as const, texte: 'Un seul mail le soir à 18 h', detail: 'avec toutes les demandes du jour' },
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
  <GardePrestataire titre="Alertes">
    <h1 class="text-[clamp(28px,4.5vw,40px)] font-black">Alertes : être prévenu des nouvelles demandes</h1>
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <template v-if="alertes">
      <AppSection titre="Pour quels métiers voulez-vous être prévenu ?">
        <div class="flex flex-col gap-5">
          <div v-for="metier in alertes.metiers" :key="metier.id" class="flex flex-col gap-2">
            <span class="font-bold">Un client cherche « {{ metier.nom }} » près de chez vous :</span>
            <div>
              <AppSegment
                :model-value="metier.prevenu ? 'oui' : 'non'"
                :etiquette="`Être prévenu des demandes « ${metier.nom} »`"
                :options="OUI_NON"
                @update:model-value="(reponse) => choisirMetier(metier.id, reponse)"
              />
            </div>
            <span class="text-[14px] text-texte-doux">
              <template v-if="metier.prevenu">
                Vous êtes prévenu de chaque demande « {{ metier.nom }} » dans votre rayon de {{ alertes.distance_km }} km autour de {{ alertes.ville }}.
              </template>
              <template v-else>
                Vous ne recevez rien pour « {{ metier.nom }} ». Les demandes restent visibles dans « Demandes près de chez moi ».
              </template>
            </span>
          </div>
        </div>
      </AppSection>

      <CarteNotifications
        titre="Sur ce téléphone"
        exemple="Une notification à chaque nouvelle demande de vos métiers près de chez vous, ex. « Nouvelle demande : Fuite sous l'évier, Talence (5 km) »."
      />
      <AppSection titre="Comment voulez-vous être prévenu par mail ?">
        <div class="flex flex-col gap-3">
          <AppChoix :model-value="alertes.alerte_mail" etiquette="Par mail" :options="MAILS" @update:model-value="choisirMail" />
          <p class="text-[14px] text-texte-doux">
            <template v-if="alertes.alerte_mail === 'chaque_demande'">
              Vous recevez un mail dès qu'une demande est publiée. Au-delà de 20 dans la journée, les suivantes arrivent dans un seul mail à 18 h.
            </template>
            <template v-else-if="alertes.alerte_mail === 'resume'">
              Vous recevez un seul mail à 18 h, avec toutes les demandes du jour. Ex. 15 demandes dans la journée : 1 mail au lieu de 15.
            </template>
            <template v-else>Vous ne recevez aucun mail de demande. Le compteur rouge de « Demandes près de chez moi » reste.</template>
          </p>
          <p class="text-[14px] text-texte-doux">
            Les mails qui concernent vos conversations, vos propositions et vos rendez-vous ne se coupent pas.
          </p>
        </div>
      </AppSection>
    </template>
  </GardePrestataire>
</template>
