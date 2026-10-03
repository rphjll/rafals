<script setup lang="ts">
// Mon agenda › Calendrier › détail d'un jour › « Ce que voit un client » (.doc/ihm/RM-AGENDA-IHM.md) :
// les heures de début qu'un client peut réserver ce jour-là, pour une annonce du métier de ce calendrier.
import { computed, ref, watch } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { type AgendaVisible, aParis, heure } from '../../outils/agenda'
import { type AnnonceVisible, prixCourt } from '../../outils/annonces'
import AppAlerte from '../ui/AppAlerte.vue'
import AppSelection from '../ui/AppSelection.vue'

// « agenda » : seulement pour recalculer quand le calendrier change (fermeture, ouverture, semaine type, réglages)
const props = defineProps<{ annonces: AnnonceVisible[]; jour: string; agenda: AgendaVisible }>()

// Seulement les annonces qui utilisent l'agenda (pas « sur devis ») et que les clients voient
const reservables = computed(() => props.annonces.filter((a) => a.forme_prix !== 'devis' && !a.raison_cachee))
const annonceId = ref<number | null>(null)
const annonce = computed(() => reservables.value.find((a) => a.id === annonceId.value))
const heures = ref<number | null>(null)
const debuts = ref<string[] | null>(null)
const erreur = ref('')

// À l'heure : le client choisit ses heures entre le minimum et le maximum de l'annonce
const choixHeures = computed(() => {
  const a = annonce.value
  if (a?.forme_prix !== 'heure' || !a.heures_min || !a.heures_max) return []
  return Array.from({ length: a.heures_max - a.heures_min + 1 }, (_, n) => (a.heures_min ?? 1) + n)
})

// En changeant de calendrier (de métier), on repart de sa première annonce
watch(
  reservables,
  (liste) => {
    if (!liste.some((a) => a.id === annonceId.value)) annonceId.value = liste[0]?.id ?? null
  },
  { immediate: true },
)
watch(annonce, (a) => (heures.value = a?.heures_min ?? null), { immediate: true })
watch(
  [annonceId, () => props.jour, heures, () => props.agenda],
  async () => {
    erreur.value = ''
    debuts.value = null
    if (!annonce.value || !props.jour) return
    const parametres = new URLSearchParams({ jour: props.jour })
    if (annonce.value.forme_prix === 'heure' && heures.value) parametres.set('heures', String(heures.value))
    try {
      const reponse = await appelerServeur<{ debuts: string[] }>(`/api/annonces/${annonce.value.id}/horaires?${parametres}`)
      debuts.value = reponse.debuts.map((d) => heure(aParis(d).heure))
    } catch (e) {
      erreur.value = messageErreur(e)
    }
  },
  { immediate: true },
)
</script>

<template>
  <div class="flex flex-col gap-2 border-t border-bord pt-3">
    <h3 class="text-[17px] font-bold">Ce que voit un client</h3>
    <p v-if="!reservables.length" class="text-[13.5px] text-texte-doux">
      Aucune annonce en ligne de ce métier avec un prix fixe ou à l'heure : les annonces « sur devis » n'utilisent pas
      l'agenda.
    </p>
    <template v-else>
      <AppSelection
        v-model="annonceId"
        etiquette="Annonce"
        :options="reservables.map((a) => ({ valeur: a.id, texte: `${a.titre} — ${prixCourt(a)}` }))"
      />
      <AppSelection
        v-if="choixHeures.length"
        v-model="heures"
        etiquette="Nombre d'heures choisi par le client"
        :options="choixHeures.map((h) => ({ valeur: h, texte: `${h} h` }))"
      />
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <template v-if="debuts">
        <p class="text-[13.5px] text-texte-doux">
          {{ debuts.length ? `${debuts.length} horaire${debuts.length > 1 ? 's' : ''} proposé${debuts.length > 1 ? 's' : ''} :` : '' }}
        </p>
        <div v-if="debuts.length" class="flex flex-wrap gap-1.5">
          <span
            v-for="d in debuts"
            :key="d"
            class="rounded-full bg-primaire-doux px-2.5 py-1 text-[13px] font-semibold text-primaire tabular-nums"
          >
            {{ d }}
          </span>
        </div>
        <p v-else class="text-[13.5px] text-texte-doux">
          Aucun horaire libre ce jour-là (fermé, trop tôt ou trop loin, déjà pris, ou métier arrêté).
        </p>
      </template>
    </template>
  </div>
</template>
