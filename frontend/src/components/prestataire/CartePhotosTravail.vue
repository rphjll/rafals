<script setup lang="ts">
// Carte « Photos de mon travail » de « Mon profil » (.doc/ihm/RM-PROPOSER-IHM.md ; RM-PRESTATAIRES § « Sans annonces ») :
// 10 photos au plus ; les 2 premières sont montrées sur la carte du prestataire dans « Trouver un prestataire ».
import { ref } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import type { ProfilPrestataire } from '../../outils/prestataires'
import { adressePhotoTravail } from '../../outils/recherche'
import AppBouton from '../ui/AppBouton.vue'
import AppSection from '../ui/AppSection.vue'

const PHOTOS_MAX = 10

const props = defineProps<{ profil: ProfilPrestataire }>()
const emit = defineEmits<{ maj: [profil: ProfilPrestataire] }>()
const { afficherMessage } = useMessage()

const champ = ref<HTMLInputElement | null>(null)
const envoi = ref(false)
const version = ref(Date.now()) // change après chaque envoi ou retrait : les rangs sont réutilisés par d'autres photos

async function ajouter(evenement: Event) {
  const fichier = (evenement.target as HTMLInputElement).files?.[0]
  if (!fichier) return
  const formulaire = new FormData()
  formulaire.append('fichier', fichier)
  envoi.value = true
  try {
    emit('maj', await appelerServeur<ProfilPrestataire>('/api/moi/prestataire/photos', formulaire))
    version.value = Date.now()
    afficherMessage('Photo ajoutée.')
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  } finally {
    envoi.value = false
    if (champ.value) champ.value.value = ''
  }
}

async function retirer(rang: number) {
  try {
    emit('maj', await appelerServeur<ProfilPrestataire>(`/api/moi/prestataire/photos/${rang}/retirer`, {}))
    version.value = Date.now()
    afficherMessage('Photo retirée.')
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}
</script>

<template>
  <AppSection titre="Photos de mon travail">
    <p class="text-[14.5px] text-texte-doux">
      Montrez ce que vous savez faire : une cuisine posée, une haie taillée… {{ PHOTOS_MAX }} photos au plus (JPG ou PNG, 5 Mo
      chacune). Les 2 premières sont sur votre carte dans « Trouver un prestataire ».
    </p>
    <ul v-if="props.profil.photos.length" class="grid grid-cols-[repeat(auto-fill,minmax(130px,1fr))] gap-3">
      <li v-for="rang in props.profil.photos" :key="rang" class="flex flex-col gap-1.5">
        <img
          :src="adressePhotoTravail(props.profil.id, rang, version)"
          :alt="`Photo n° ${rang} de mon travail`"
          class="aspect-[4/3] w-full rounded-rafals object-cover"
        />
        <AppBouton variante="danger" @click="retirer(rang)">Retirer</AppBouton>
      </li>
    </ul>
    <p v-else class="font-semibold">Aucune photo pour l'instant.</p>
    <div>
      <AppBouton v-if="props.profil.photos.length < PHOTOS_MAX" variante="secondaire" :occupe="envoi" @click="champ?.click()">
        {{ envoi ? 'Envoi…' : 'Ajouter une photo' }}
      </AppBouton>
      <p v-else class="text-[13.5px] text-texte-doux">{{ PHOTOS_MAX }} photos : retirez-en une pour en ajouter une autre.</p>
      <input ref="champ" type="file" accept="image/jpeg,image/png" class="sr-only" @change="ajouter" />
    </div>
  </AppSection>
</template>
