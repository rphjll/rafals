<script setup lang="ts">
// « Sur ce téléphone » (.doc/ihm/RM-ALERTES-IHM.md ; RM-ALERTES.md, RM-APPLICATION.md, lot 8.7) : dans « Alertes »
// pour un prestataire, dans « Mon profil » pour tout le monde. Chaque appareil s'active à part.
import { onMounted, ref } from 'vue'
import { messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { useNotifications } from '../../composables/useNotifications'
import AppBadge from '../ui/AppBadge.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppSection from '../ui/AppSection.vue'

defineProps<{ titre: string; exemple: string }>()
const { afficherMessage } = useMessage()
const { etat, charger, activer, couper } = useNotifications()
const occupe = ref(false)

onMounted(() => charger().catch(() => (etat.value = 'impossible')))

async function agir(action: () => Promise<string>) {
  occupe.value = true
  try {
    afficherMessage(await action())
  } catch (e) {
    // Nos phrases (refus du navigateur, pas branché) et celles du serveur s'affichent telles quelles
    afficherMessage(e instanceof Error && e.name === 'Error' ? e.message : messageErreur(e), 'erreur')
  } finally {
    occupe.value = false
  }
}
</script>

<template>
  <AppSection :titre="titre">
    <div class="flex flex-col gap-3">
      <p class="text-[14px] text-texte-doux">{{ exemple }} Le téléphone sonne même quand rafals est fermé. Jamais de nom complet, d'adresse ni le texte d'un message.</p>
      <div v-if="etat === 'actif'" class="flex flex-wrap items-center gap-3">
        <AppBadge etat="ok">activées sur cet appareil</AppBadge>
        <AppBouton variante="secondaire" :occupe="occupe" @click="agir(couper)">Couper les notifications</AppBouton>
      </div>
      <div v-else-if="etat === 'inactif'">
        <AppBouton :occupe="occupe" @click="agir(activer)">Activer les notifications sur cet appareil</AppBouton>
      </div>
      <div v-else-if="etat === 'pas-branche'">
        <AppBouton variante="verrouille" raison-verrou="Les notifications ne sont pas encore branchées sur rafals : vous recevez les mails en attendant.">
          Activer les notifications sur cet appareil
        </AppBouton>
      </div>
      <p v-else-if="etat === 'refuse'" class="text-[14px] text-texte-doux">
        Ce navigateur a bloqué les notifications de rafals. Pour les autoriser : cliquez sur le cadenas à gauche de l'adresse du site, puis « Notifications » → « Autoriser ».
      </p>
      <p v-else-if="etat === 'impossible'" class="text-[14px] text-texte-doux">
        Ce navigateur ne sait pas recevoir de notifications. Sur iPhone : installez d'abord rafals (menu du compte → [Installer rafals]), puis ouvrez-le depuis son icône.
      </p>
    </div>
  </AppSection>
</template>
