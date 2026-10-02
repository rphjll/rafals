<script setup lang="ts">
// Administration › Mots interdits (.doc/ihm/RM-ADMINISTRATION-IHM.md ; RM-AVIS.md) : la liste de secours, en plus de
// l'IA qui lit chaque avis. Ajouter un mot ; × pour en retirer un.
import { onMounted, ref } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppChamp from '../ui/AppChamp.vue'
import AppSection from '../ui/AppSection.vue'

const { afficherMessage } = useMessage()
const mots = ref<{ id: number; mot: string }[]>([])
const nouveau = ref('')
const erreur = ref('')

async function charger() {
  mots.value = await appelerServeur('/api/admin/mots-interdits')
}
onMounted(charger)

async function ajouter() {
  erreur.value = ''
  try {
    const m = await appelerServeur<{ id: number; mot: string }>('/api/admin/mots-interdits', { mot: nouveau.value })
    afficherMessage(`« ${m.mot} » ajouté à la liste.`)
    nouveau.value = ''
    await charger()
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}

async function retirer(m: { id: number; mot: string }) {
  try {
    await appelerServeur(`/api/admin/mots-interdits/${m.id}/retirer`, {})
    afficherMessage(`« ${m.mot} » retiré de la liste.`)
    await charger()
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}
</script>

<template>
  <AppSection :titre="`Mots interdits (${mots.length})`">
    <p class="text-[13.5px] text-texte-doux">
      Une IA lit déjà chaque avis et chaque réponse. Cette liste est un filet de secours : un texte qui contient un de ces
      mots (mot entier, sans tenir compte des accents ni des majuscules) est refusé à l'envoi.
    </p>
    <form class="flex flex-wrap items-end gap-2" @submit.prevent="ajouter">
      <div class="w-[240px]"><AppChamp v-model="nouveau" etiquette="Ajouter un mot" placeholder="ex. abruti" /></div>
      <AppBouton type="submit">Ajouter</AppBouton>
    </form>
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <div class="flex flex-wrap gap-1.5">
      <span
        v-for="m in mots"
        :key="m.id"
        class="inline-flex items-center gap-1.5 rounded-full bg-neutre-doux py-0.5 pr-1 pl-2.5 text-sm"
      >
        {{ m.mot }}
        <button
          type="button"
          class="size-6 rounded-full bg-surface font-bold text-erreur"
          :aria-label="`Retirer « ${m.mot} »`"
          @click="retirer(m)"
        >
          ×
        </button>
      </span>
    </div>
  </AppSection>
</template>
