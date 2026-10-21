<script setup lang="ts">
// Mon activité › Mes métiers (.doc/ihm/RM-PROPOSER-IHM.md ; RM-PRESTATAIRES.md) : la liste des métiers et leur date
// d'arrêt. La date d'arrêt se règle dans « Mon agenda › Calendrier » (bouton [Date d'arrêt], refonte du 03/10/2026).
// Métier arrêté : [Reprendre ce métier].
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { formaterDate } from '../../outils/dates'
import type { MetierExerce, ProfilPrestataire } from '../../outils/prestataires'
import AppBadge from '../ui/AppBadge.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppSection from '../ui/AppSection.vue'

defineProps<{ profil: ProfilPrestataire }>()
const emit = defineEmits<{ maj: [profil: ProfilPrestataire] }>()
const { afficherMessage } = useMessage()

async function reprendre(metier: MetierExerce) {
  try {
    emit('maj', await appelerServeur<ProfilPrestataire>('/api/moi/prestataire/metiers/fin', {
      metier_id: metier.id, fin_le: null, suivant_id: null,
    }))
    afficherMessage(`${metier.nom} repris : vous apparaissez de nouveau dans ses recherches.`)
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}
</script>

<template>
  <AppSection titre="Mes métiers">
    <div class="flex flex-col divide-y divide-bord">
      <div class="flex flex-wrap items-center justify-between gap-2.5 py-3 first:pt-0">
        <div class="flex flex-col gap-1">
          <p class="flex flex-wrap items-center gap-2 font-semibold">
            {{ profil.metier_principal.nom }} <AppBadge etat="ok">principal</AppBadge>
          </p>
          <p v-if="profil.metier_principal.fin_le" class="text-[13.5px] text-texte-doux">
            Arrêt prévu après le {{ formaterDate(profil.metier_principal.fin_le) }} :
            <template v-if="profil.metier_principal_suivant">
              ensuite, {{ profil.metier_principal_suivant.nom }} deviendra votre métier principal.
            </template>
            <template v-else>c'est votre seul métier ; votre profil restera affiché.</template>
          </p>
        </div>
      </div>

      <div
        v-for="metier in profil.metiers_secondaires"
        :key="metier.id"
        class="flex flex-wrap items-center justify-between gap-2.5 py-3"
      >
        <div class="flex flex-col gap-1">
          <p class="font-semibold">{{ metier.nom }}</p>
          <p v-if="metier.fin_le" class="text-[13.5px] text-texte-doux">Arrêt prévu après le {{ formaterDate(metier.fin_le) }}.</p>
        </div>
      </div>

      <div
        v-for="metier in profil.metiers_arretes"
        :key="metier.id"
        class="flex flex-wrap items-center justify-between gap-2.5 py-3"
      >
        <div class="flex flex-col gap-1">
          <p class="flex flex-wrap items-center gap-2 font-semibold">
            {{ metier.nom }} <AppBadge>arrêté depuis le {{ formaterDate(metier.fin_le ?? '') }}</AppBadge>
          </p>
          <p class="text-[13.5px] text-texte-doux">Vous n'apparaissez plus dans les recherches de ce métier.</p>
        </div>
        <AppBouton @click="reprendre(metier)">Reprendre ce métier</AppBouton>
      </div>
    </div>
    <p class="text-[13px] text-texte-doux">
      Ajouter un métier : la bulle « + Ajouter » en haut du profil. Arrêter un métier : dans
      <RouterLink to="/mon-agenda" class="font-semibold text-primaire">Mon agenda › Calendrier</RouterLink>, bouton
      « Date d'arrêt ». Après cette date, vous n'apparaissez plus dans les recherches de ce métier, et les rendez-vous de ce
      métier pris après cette date sont annulés (clients prévenus).
    </p>
  </AppSection>
</template>
