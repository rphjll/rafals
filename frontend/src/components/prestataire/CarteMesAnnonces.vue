<script setup lang="ts">
// Mon activité › Mes annonces (.doc/ihm/RM-PROPOSER-IHM.md) : combien sont en ligne, et les boutons pour y aller.
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur } from '../../api'
import type { AnnonceVisible } from '../../outils/annonces'
import AppBouton from '../ui/AppBouton.vue'
import AppSection from '../ui/AppSection.vue'

const ANNONCES_EN_LIGNE_MAX = 20

const routeur = useRouter()
const annonces = ref<AnnonceVisible[] | null>(null)
onMounted(async () => (annonces.value = await appelerServeur<AnnonceVisible[]>('/api/moi/annonces')))
const visibles = computed(() => annonces.value?.filter((a) => a.raison_cachee === null).length ?? 0)
</script>

<template>
  <AppSection v-if="annonces" titre="Mes annonces">
    <template #action>
      <span class="text-[13.5px] text-texte-doux">{{ visibles }} en ligne sur {{ ANNONCES_EN_LIGNE_MAX }}</span>
    </template>
    <p class="text-[14.5px] text-texte-doux">
      <template v-if="visibles">Vous apparaissez dans les recherches grâce à vos annonces en ligne.</template>
      <template v-else>Aucune annonce en ligne : écrivez-en une pour que les clients vous trouvent.</template>
    </p>
    <div class="flex flex-wrap gap-2">
      <AppBouton v-if="annonces.length" @click="routeur.push('/mes-annonces')">Voir mes annonces</AppBouton>
      <AppBouton :variante="annonces.length ? 'secondaire' : 'principal'" @click="routeur.push('/mes-annonces/nouvelle')">
        Écrire une annonce
      </AppBouton>
    </div>
  </AppSection>
</template>
