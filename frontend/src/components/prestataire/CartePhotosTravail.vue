<script setup lang="ts">
// Onglet « Photos » de « Mon profil » (.doc/ihm/RM-PROFIL-IHM.md ; RM-PRESTATAIRES § « Sans annonces ») : grille carrée
// de 3 colonnes, façon Instagram (21/10/2026). 10 photos au plus ; les 2 premières sont sur la carte du prestataire
// dans « Trouver un prestataire ». Un clic sur une photo l'ouvre en grand, avec [Retirer cette photo].
import { ref } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import type { ProfilPrestataire } from '../../outils/prestataires'
import { adressePhotoTravail } from '../../outils/recherche'
import AppBouton from '../ui/AppBouton.vue'
import AppFenetre from '../ui/AppFenetre.vue'
import AppIcone from '../ui/AppIcone.vue'

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

const enGrand = ref<number | null>(null) // rang de la photo ouverte en grand

async function retirer(rang: number) {
  enGrand.value = null
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
  <!-- La grille de la grande maquette : 3 colonnes, « Sur ma carte » sur les 2 premières, la case « + Ajouter une photo » -->
  <div class="flex flex-col gap-3">
    <div class="photos">
      <button v-for="(rang, i) in props.profil.photos" :key="rang" type="button" class="ph" style="--c: var(--surface2)" :aria-label="`Ouvrir la photo ${i + 1}`" @click="enGrand = rang">
        <img :src="adressePhotoTravail(props.profil.id, rang, version)" :alt="`Photo n° ${rang} de mon travail`" />
        <span v-if="i < 2" class="sur">Sur ma carte</span>
      </button>
      <button v-if="props.profil.photos.length < PHOTOS_MAX" type="button" class="ph ajout" :disabled="envoi" @click="champ?.click()">
        <AppIcone nom="plus" />{{ envoi ? 'Envoi…' : 'Ajouter une photo' }}
      </button>
    </div>
    <p class="doux petit">
      <template v-if="!props.profil.photos.length">Aucune photo pour l'instant. Montrez ce que vous savez faire : une cuisine posée, une haie taillée… </template>
      {{ props.profil.photos.length }} photo{{ props.profil.photos.length > 1 ? 's' : '' }} sur {{ PHOTOS_MAX }} (JPG ou PNG, 5 Mo
      chacune). Les 2 premières sont sur votre carte dans « Trouver un prestataire ».
      <template v-if="props.profil.photos.length >= PHOTOS_MAX">Retirez-en une pour en ajouter une autre.</template>
    </p>
    <input ref="champ" type="file" accept="image/jpeg,image/png" class="sr-only" @change="ajouter" />

    <AppFenetre :ouverte="enGrand !== null" :titre="`Photo n° ${enGrand}`" @fermer="enGrand = null">
      <img v-if="enGrand !== null" :src="adressePhotoTravail(props.profil.id, enGrand, version)" alt="" class="w-full rounded-rafals" />
      <template #pied>
        <AppBouton variante="danger" @click="retirer(enGrand!)">Retirer cette photo</AppBouton>
        <AppBouton variante="secondaire" @click="enGrand = null">Fermer</AppBouton>
      </template>
    </AppFenetre>
  </div>
</template>
