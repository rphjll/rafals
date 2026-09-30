<script setup lang="ts">
// Mon agenda › Horaires libres (.doc/ihm/RM-AGENDA-IHM.md) : ce que voit un client qui veut réserver une annonce un jour donné.
import { computed, ref, watch } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { aParis, heure, jourLisible } from '../../outils/agenda'
import { type AnnonceVisible, prixCourt } from '../../outils/annonces'
import { aujourdhuiIso } from '../../outils/dates'
import AppAlerte from '../ui/AppAlerte.vue'
import AppChamp from '../ui/AppChamp.vue'
import AppSection from '../ui/AppSection.vue'
import AppSelection from '../ui/AppSelection.vue'

const props = defineProps<{ annonces: AnnonceVisible[] }>()

// Seulement les annonces qui utilisent l'agenda (pas « sur devis ») et que les clients voient
const reservables = computed(() => props.annonces.filter((a) => a.forme_prix !== 'devis' && !a.raison_cachee))
const annonceId = ref<number | null>(reservables.value[0]?.id ?? null)
const annonce = computed(() => reservables.value.find((a) => a.id === annonceId.value))
const jour = ref(aujourdhuiIso())
const heures = ref<number | null>(null)
const debuts = ref<string[] | null>(null)
const erreur = ref('')

// À l'heure : le client choisit ses heures entre le minimum et le maximum de l'annonce
const choixHeures = computed(() => {
  const a = annonce.value
  if (a?.forme_prix !== 'heure' || !a.heures_min || !a.heures_max) return []
  return Array.from({ length: a.heures_max - a.heures_min + 1 }, (_, n) => (a.heures_min ?? 1) + n)
})

watch(annonce, (a) => (heures.value = a?.heures_min ?? null), { immediate: true })
watch(
  [annonceId, jour, heures],
  async () => {
    erreur.value = ''
    debuts.value = null
    if (!annonce.value || !jour.value) return
    const parametres = new URLSearchParams({ jour: jour.value })
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
  <AppSection titre="Horaires libres">
    <p class="text-[13.5px] text-texte-doux">Ce que voit un client qui veut réserver (la réservation arrive au niveau 4).</p>
    <p v-if="!reservables.length" class="text-[14.5px] text-texte-doux">
      Aucune annonce en ligne avec un prix fixe ou à l'heure : les annonces « sur devis » n'utilisent pas l'agenda.
    </p>
    <template v-else>
      <div class="grid gap-3 sm:grid-cols-2">
        <AppSelection
          v-model="annonceId"
          etiquette="Annonce"
          :options="reservables.map((a) => ({ valeur: a.id, texte: `${a.titre} — ${prixCourt(a)}` }))"
        />
        <AppChamp v-model="jour" etiquette="Jour" type="date" :min="aujourdhuiIso()" />
      </div>
      <AppSelection
        v-if="choixHeures.length"
        v-model="heures"
        etiquette="Nombre d'heures choisi par le client"
        :options="choixHeures.map((h) => ({ valeur: h, texte: `${h} h` }))"
      />
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <template v-if="debuts">
        <p class="font-semibold first-letter:uppercase">
          {{ jourLisible(jour) }} :
          {{ debuts.length ? `${debuts.length} horaire${debuts.length > 1 ? 's' : ''}` : 'aucun horaire' }}
        </p>
        <div v-if="debuts.length" class="flex flex-wrap gap-2">
          <span
            v-for="d in debuts"
            :key="d"
            class="rounded-full border border-primaire px-3 py-1.5 text-sm font-semibold text-primaire"
          >
            {{ d }}
          </span>
        </div>
        <p v-else class="text-[14.5px] text-texte-doux">
          Aucun horaire libre ce jour-là (fermé, bloqué, trop tôt ou trop loin, ou métier arrêté).
        </p>
      </template>
    </template>
  </AppSection>
</template>
