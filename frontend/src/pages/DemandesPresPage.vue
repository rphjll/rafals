<script setup lang="ts">
// Demandes près de chez moi (.doc/ihm/RM-DEMANDES-IHM.md ; RM-DEMANDES.md) : pour un prestataire, les demandes
// ouvertes de ses métiers, dans son rayon autour de l'adresse de son compte. Sans adresse : un bouton pour l'ajouter.
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import CarteDemande from '../components/demandes/CarteDemande.vue'
import GardePrestataire from '../components/prestataire/GardePrestataire.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import type { DemandeVisible } from '../outils/demandes'

const routeur = useRouter()
const demandes = ref<DemandeVisible[] | null>(null)
const sansAdresse = ref(false)
const erreur = ref('')

onMounted(async () => {
  try {
    const [liste, adresse] = await Promise.all([
      appelerServeur<DemandeVisible[]>('/api/moi/prestataire/demandes'),
      appelerServeur<unknown | null>('/api/moi/adresse'),
    ])
    demandes.value = liste
    sansAdresse.value = adresse === null
  } catch (e) {
    erreur.value = messageErreur(e)
  }
})
</script>

<template>
  <GardePrestataire titre="Demandes près de chez moi">
    <h1 class="text-[28px] font-bold">Demandes près de chez moi</h1>
    <p class="text-texte-doux">
      Les demandes de vos métiers, dans votre rayon autour de votre adresse. Répondre est gratuit ; rafals garde 5 % seulement si
      le client paie par carte.
    </p>
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <div v-else-if="sansAdresse" class="flex flex-col items-start gap-3 rounded-carte border-2 border-dashed border-bord p-5">
      <p class="text-texte-doux">
        Vous n'avez pas encore d'adresse : rafals ne sait pas où vous êtes, donc ne peut pas vous montrer les demandes près de chez vous.
      </p>
      <AppBouton @click="routeur.push('/profil')">Ajouter votre adresse</AppBouton>
    </div>
    <div v-else-if="demandes?.length" class="flex flex-col gap-3">
      <CarteDemande v-for="demande in demandes" :key="demande.id" :demande="demande" />
    </div>
    <p v-else-if="demandes" class="rounded-carte border-2 border-dashed border-bord p-5 text-texte-doux">
      Aucune demande ouverte pour vos métiers près de chez vous en ce moment.
    </p>
  </GardePrestataire>
</template>
