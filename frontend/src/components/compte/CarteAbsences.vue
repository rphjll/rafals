<script setup lang="ts">
// Mon compte › Absences (.doc/ihm/RM-COMPTE-IHM.md ; RM-RENDEZ-VOUS.md) : « 2 absences sans prévenir en 6 mois »,
// et le mois sans réserver s'il y en a un. Sans absence : la carte ne s'affiche pas.
import { onMounted, ref } from 'vue'
import { appelerServeur } from '../../api'
import { formaterDate } from '../../outils/dates'
import AppAlerte from '../ui/AppAlerte.vue'
import AppSection from '../ui/AppSection.vue'

const compteur = ref<{ absences: number; reservation_suspendue_jusqu_au: string | null } | null>(null)
onMounted(async () => (compteur.value = await appelerServeur('/api/moi/absences')))
</script>

<template>
  <AppSection v-if="compteur && (compteur.absences || compteur.reservation_suspendue_jusqu_au)" titre="Absences">
    <AppAlerte v-if="compteur.reservation_suspendue_jusqu_au">
      {{ compteur.absences }} absences sans prévenir en 6 mois : vous ne pouvez plus réserver jusqu'au
      {{ formaterDate(compteur.reservation_suspendue_jusqu_au) }}.
    </AppAlerte>
    <p v-else class="font-semibold">
      {{ compteur.absences }} absence{{ compteur.absences > 1 ? 's' : '' }} sans prévenir en 6 mois
    </p>
    <p class="text-[13.5px] text-texte-doux">
      À 3 absences en 6 mois, vous ne pouvez plus réserver pendant 1 mois. Une absence compte 7 jours après avoir été
      signalée, sauf si vous la contestez (page « Mes rendez-vous »).
    </p>
  </AppSection>
</template>
