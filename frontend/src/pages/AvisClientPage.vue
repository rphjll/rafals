<script setup lang="ts">
// Page publique d'un client (.doc/ihm/RM-AVIS-CLIENTS-IHM.md ; RM-AVIS.md § « Notation dans les deux sens ») :
// « Marie D. », membre depuis, sa moyenne, et les avis que des prestataires lui ont laissés. Jamais le nom complet, la
// ville, l'adresse, le téléphone ni le mail. La page demande aux moteurs de recherche de ne pas l'enregistrer.
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppSection from '../components/ui/AppSection.vue'
import { type ClientPublic, etoiles, texteNote } from '../outils/avis'
import { initialesDe } from '../outils/noms'

const route = useRoute()
const routeur = useRouter()
const client = ref<ClientPublic | null>(null)
const erreur = ref('')

// « noindex » : on ne doit pas tomber sur cette page en tapant un prénom dans un moteur de recherche
const balise = document.createElement('meta')
balise.name = 'robots'
balise.content = 'noindex'

onMounted(async () => {
  document.head.appendChild(balise)
  try {
    client.value = await appelerServeur<ClientPublic>(`/api/clients/${route.params.id}/avis`)
  } catch (e) {
    erreur.value = messageErreur(e) // ex. « Cette personne n'est pas (ou plus) sur rafals. »
  }
})
onBeforeUnmount(() => balise.remove())
</script>

<template>
  <div class="mx-auto flex w-full max-w-[760px] flex-col gap-4">
    <div><AppBouton variante="secondaire" @click="routeur.back()">‹ Retour</AppBouton></div>
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <template v-if="client">
      <AppSection>
        <div class="flex items-center gap-4">
          <span class="grid size-16 shrink-0 place-items-center rounded-full bg-primaire-doux text-xl font-bold text-primaire" aria-hidden="true">
            {{ initialesDe(client.nom) }}
          </span>
          <div class="flex flex-col">
            <h1 class="text-[26px] font-bold">{{ client.nom }}</h1>
            <span class="text-texte-doux">Membre depuis {{ client.membre_depuis }}</span>
            <b>{{ texteNote(client.note, client.nombre_avis) }}</b>
          </div>
        </div>
      </AppSection>
      <AppSection titre="Les avis des prestataires">
        <ul v-if="client.avis.length" class="flex flex-col gap-4">
          <li v-for="avis in client.avis" :key="avis.id" class="flex flex-col gap-1">
            <span>
              <b class="text-accent" :aria-label="`${avis.note} sur 5`">{{ etoiles(avis.note) }}</b>
              <span class="text-[14px] text-texte-doux"> · {{ avis.auteur }} · {{ avis.mois }}</span>
            </span>
            <p class="whitespace-pre-line">{{ avis.texte }}</p>
            <p v-if="avis.reponse" class="rounded-rafals bg-fond px-3 py-2 text-[14px]">
              <b>Réponse de {{ client.nom }} :</b> {{ avis.reponse }}
            </p>
          </li>
        </ul>
        <p v-else class="text-texte-doux">Aucun avis pour l'instant.</p>
      </AppSection>
    </template>
  </div>
</template>
