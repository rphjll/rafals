<script setup lang="ts">
// Choisir un horaire libre d'une annonce (.doc/ihm/RM-ANNONCE-IHM.md) : les 14 prochains jours (grisés s'il n'y a
// aucun horaire), puis les heures de début du jour choisi. Sert à réserver et à déplacer un rendez-vous.
import { ref, watch } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { MOIS, aParis, ajouterJours, heure, jourLisible, jourSemaine, JOURS } from '../../outils/agenda'
import { aujourdhuiIso } from '../../outils/dates'
import AppAlerte from '../ui/AppAlerte.vue'

const props = defineProps<{ annonceId: number; heures?: number | null }>()
const emit = defineEmits<{ choisir: [debut: string] }>()

const NOMBRE_DE_JOURS = 14
const jours = Array.from({ length: NOMBRE_DE_JOURS }, (_, n) => ajouterJours(aujourdhuiIso(), n))
const parJour = ref<Record<string, string[]>>({})
const choisi = ref('')
const erreur = ref('')

async function charger() {
  erreur.value = ''
  try {
    const reponses = await Promise.all(
      jours.map((jour) => {
        const parametres = new URLSearchParams({ jour })
        if (props.heures) parametres.set('heures', String(props.heures))
        return appelerServeur<{ debuts: string[] }>(`/api/annonces/${props.annonceId}/horaires?${parametres}`)
      }),
    )
    parJour.value = Object.fromEntries(jours.map((jour, n) => [jour, reponses[n]?.debuts ?? []]))
    if (!parJour.value[choisi.value]?.length) choisi.value = jours.find((j) => parJour.value[j]?.length) ?? jours[0] ?? ''
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
watch(() => [props.annonceId, props.heures], charger, { immediate: true })

const etiquette = (jour: string) => ({
  nom: (JOURS[jourSemaine(jour) - 1] ?? '').slice(0, 3),
  numero: Number(jour.slice(8)),
  mois: (MOIS[Number(jour.slice(5, 7)) - 1] ?? '').slice(0, 4),
})
</script>

<template>
  <div class="flex flex-col gap-3">
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <div class="flex gap-1.5 overflow-x-auto pb-1" role="listbox" aria-label="Jour">
      <button
        v-for="jour in jours"
        :key="jour"
        type="button"
        role="option"
        :aria-selected="choisi === jour"
        class="min-w-16 flex-none rounded-rafals border px-2.5 py-2 text-center text-sm"
        :class="[
          choisi === jour ? 'border-primaire bg-primaire-doux font-bold text-primaire' : 'border-bord bg-surface',
          parJour[jour] && !parJour[jour]?.length ? 'opacity-50' : '',
        ]"
        @click="choisi = jour"
      >
        {{ etiquette(jour).nom }}<br />
        <b class="text-base">{{ etiquette(jour).numero }}</b>
        <small class="block text-xs text-texte-doux">{{ parJour[jour] && !parJour[jour]?.length ? 'complet' : etiquette(jour).mois }}</small>
      </button>
    </div>
    <p class="font-semibold first-letter:uppercase">{{ choisi ? jourLisible(choisi) : '' }}</p>
    <div v-if="parJour[choisi]?.length" class="flex flex-wrap gap-2">
      <button
        v-for="debut in parJour[choisi]"
        :key="debut"
        type="button"
        class="min-h-[38px] rounded-full border border-primaire bg-surface px-3.5 py-1.5 font-semibold text-primaire hover:bg-primaire-doux"
        @click="emit('choisir', debut)"
      >
        {{ heure(aParis(debut).heure) }}
      </button>
    </div>
    <p v-else-if="parJour[choisi]" class="text-[14px] text-texte-doux">Aucun horaire libre ce jour-là : essayez un autre jour.</p>
  </div>
</template>
