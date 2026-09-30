<script setup lang="ts">
// Une annonce vue par un client (.doc/ihm/RM-ANNONCE-IHM.md) : photos, prix, durée, lieu (la ville, jamais la rue),
// paiement, description. Son auteur la voit aussi quand elle est cachée (aperçu).
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppSection from '../components/ui/AppSection.vue'
import { useCompte } from '../composables/useCompte'
import { type AnnoncePublique, duree, euros, lieuPourLeClient, paiement } from '../outils/annonces'

const route = useRoute()
const { compte } = useCompte()
const annonce = ref<AnnoncePublique | null>(null)
const erreur = ref('')
const photo = ref(1)

async function charger() {
  erreur.value = ''
  try {
    annonce.value = await appelerServeur<AnnoncePublique>(`/api/annonces/${route.params.id}`)
    photo.value = 1
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
watch(() => route.params.id, charger, { immediate: true })

const monAnnonce = computed(() => !!annonce.value && compte.value?.prestataire_id === annonce.value.prestataire.id)
const prix = computed(() => {
  const a = annonce.value
  if (!a || a.prix_centimes === null) return 'Sur devis'
  return a.forme_prix === 'heure' ? `${euros(a.prix_centimes)} de l'heure` : euros(a.prix_centimes)
})
</script>

<template>
  <div class="mx-auto flex w-full max-w-[720px] flex-col gap-4">
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>

    <template v-if="annonce">
      <AppAlerte v-if="monAnnonce" etat="attente">
        Aperçu de votre annonce, telle que les clients la voient.
        <RouterLink :to="`/mes-annonces/${annonce.id}`" class="font-semibold underline">Modifier</RouterLink>
      </AppAlerte>

      <div v-if="annonce.nombre_photos" class="flex flex-col gap-2">
        <img
          :src="`/api/annonces/${annonce.id}/photos/${photo}`"
          :alt="`Photo ${photo} de « ${annonce.titre} »`"
          class="max-h-[360px] w-full rounded-rafals object-cover"
        />
        <div v-if="annonce.nombre_photos > 1" class="flex flex-wrap gap-2">
          <button
            v-for="ordre in annonce.nombre_photos"
            :key="ordre"
            type="button"
            class="size-14 overflow-hidden rounded-lg border-2"
            :class="ordre === photo ? 'border-primaire' : 'border-transparent'"
            :aria-label="`Voir la photo ${ordre}`"
            @click="photo = ordre"
          >
            <img :src="`/api/annonces/${annonce.id}/photos/${ordre}`" alt="" class="size-full object-cover" />
          </button>
        </div>
      </div>

      <AppSection>
        <div class="flex flex-wrap items-baseline justify-between gap-3">
          <h1 class="text-2xl font-bold">{{ annonce.titre }}</h1>
          <span class="text-[22px] font-bold text-primaire">{{ prix }}</span>
        </div>
        <p class="text-[14.5px] text-texte-doux">
          par
          <RouterLink :to="`/prestataires/${annonce.prestataire.id}`" class="font-bold text-texte underline hover:text-primaire">
            {{ annonce.prestataire.nom_affiche }}
          </RouterLink>
          · {{ annonce.metier.nom }}
        </p>
        <dl class="grid grid-cols-[auto_1fr] gap-x-[18px] gap-y-2 text-[14.5px]">
          <template v-if="annonce.forme_prix === 'fixe' && annonce.duree_minutes">
            <dt class="text-texte-doux">Durée</dt>
            <dd class="font-medium">{{ duree(annonce.duree_minutes) }}</dd>
          </template>
          <template v-if="annonce.forme_prix === 'heure'">
            <dt class="text-texte-doux">Durée</dt>
            <dd class="font-medium">au choix, de {{ annonce.heures_min }} h à {{ annonce.heures_max }} h</dd>
          </template>
          <dt class="text-texte-doux">Où</dt>
          <dd class="font-medium">{{ lieuPourLeClient(annonce) }}</dd>
          <dt class="text-texte-doux">Paiement</dt>
          <dd class="font-medium">{{ paiement(annonce.modes_de_paiement) }}</dd>
        </dl>
        <p v-if="annonce.description" class="whitespace-pre-line">{{ annonce.description }}</p>
        <div class="pt-10 sm:pt-0">
          <AppBouton variante="verrouille" raison-verrou="La réservation arrive bientôt (niveau 4).">
            {{ annonce.forme_prix === 'devis' ? 'Demander un devis' : 'Réserver' }}
          </AppBouton>
        </div>
      </AppSection>
    </template>
  </div>
</template>
