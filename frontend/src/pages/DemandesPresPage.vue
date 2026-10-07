<script setup lang="ts">
// Demandes près de chez moi (.doc/ihm/RM-DEMANDES-IHM.md ; RM-DEMANDES.md) : pour un prestataire, les demandes
// ouvertes de ses métiers, dans son rayon.
import { onMounted, ref } from 'vue'
import { appelerServeur, messageErreur } from '../api'
import CarteDemande from '../components/demandes/CarteDemande.vue'
import GardePrestataire from '../components/prestataire/GardePrestataire.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import type { DemandeVisible } from '../outils/demandes'

const demandes = ref<DemandeVisible[] | null>(null)
const erreur = ref('')

onMounted(async () => {
  try {
    demandes.value = await appelerServeur<DemandeVisible[]>('/api/moi/prestataire/demandes')
  } catch (e) {
    erreur.value = messageErreur(e)
  }
})
</script>

<template>
  <GardePrestataire titre="Demandes près de chez moi">
    <h1 class="text-[28px] font-bold">Demandes près de chez moi</h1>
    <p class="text-texte-doux">
      Les demandes de vos métiers, dans votre rayon. Répondre est gratuit ; rafals garde 5 % seulement si le client paie par carte.
    </p>
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <div v-else-if="demandes?.length" class="flex flex-col gap-3">
      <CarteDemande v-for="demande in demandes" :key="demande.id" :demande="demande" />
    </div>
    <p v-else-if="demandes" class="rounded-rafals border border-bord bg-surface p-5 text-texte-doux">
      Aucune demande ouverte pour vos métiers près de chez vous en ce moment.
    </p>
  </GardePrestataire>
</template>
