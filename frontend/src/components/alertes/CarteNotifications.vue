<script setup lang="ts">
// « Sur ce téléphone » (.doc/ihm/RM-ALERTES-IHM.md ; RM-ALERTES.md, RM-APPLICATION.md, lot 8.7) : dans « Alertes »
// pour un prestataire, dans « Mon profil » pour tout le monde. Chaque appareil s'active à part.
import { inject, onMounted, ref } from 'vue'
import { messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { useNotifications } from '../../composables/useNotifications'
import AppBouton from '../ui/AppBouton.vue'
import AppInterrupteur from '../ui/AppInterrupteur.vue'
import AppSection from '../ui/AppSection.vue'
import { CLE_LISTE_LIGNES } from '../../outils/profil'

defineProps<{ titre: string; exemple: string }>()
const { afficherMessage } = useMessage()
const { etat, charger, activer, couper } = useNotifications()
const occupe = ref(false)
// Dans « Mon profil › Mon compte » : une ligne qui se déplie ; dans « Paramètres » : une carte
const dansListe = !!inject(CLE_LISTE_LIGNES, null)

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
  <component :is="dansListe ? AppSection : 'div'" :titre="dansListe ? titre : undefined" :class="dansListe ? '' : 'carte p-[18px]'">
    <div class="reglage">
      <div class="rl">
        <div>
          <b>{{ titre }}</b>
          <p class="doux petit">{{ exemple }} Le téléphone sonne même quand rafals est fermé. Jamais de nom complet, d'adresse ni le texte d'un message.</p>
        </div>
        <AppInterrupteur
          v-if="etat === 'actif' || etat === 'inactif'"
          :model-value="etat === 'actif'"
          :etiquette="titre"
          :desactive="occupe"
          @update:model-value="(oui) => agir(oui ? activer : couper)"
        />
        <AppBouton v-else-if="etat === 'pas-branche'" variante="verrouille" petit raison-verrou="Les notifications ne sont pas encore branchées sur rafals : vous recevez les mails en attendant.">
          Activer
        </AppBouton>
      </div>
      <p v-if="etat === 'refuse'" class="exemple">
        Ce navigateur a bloqué les notifications de rafals. Pour les autoriser : cliquez sur le cadenas à gauche de l'adresse du site, puis « Notifications » → « Autoriser ».
      </p>
      <p v-else-if="etat === 'impossible'" class="exemple">
        Ce navigateur ne sait pas recevoir de notifications. Sur iPhone : installez d'abord rafals (menu du compte → [Installer rafals]), puis ouvrez-le depuis son icône.
      </p>
    </div>
  </component>
</template>
