<script setup lang="ts">
// Photos d'une annonce (.doc/ihm/RM-MES-ANNONCES-IHM.md) : 5 au plus, JPG ou PNG ; la n° 1 est montrée en premier.
// Retirer une photo fait remonter les suivantes d'un rang.
import { ref } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import type { AnnonceVisible } from '../../outils/annonces'
import AppAlerte from '../ui/AppAlerte.vue'
import AppSection from '../ui/AppSection.vue'

const PHOTOS_MAX = 5

const props = defineProps<{ annonce: AnnonceVisible }>()
const emit = defineEmits<{ maj: [annonce: AnnonceVisible] }>()
const { afficherMessage } = useMessage()
const champ = ref<HTMLInputElement | null>(null)
const erreur = ref('')
const version = ref(Date.now()) // change après chaque envoi, pour recharger les images

async function changer(chemin: string, donnees: FormData | object, message: string) {
  erreur.value = ''
  try {
    emit('maj', await appelerServeur<AnnonceVisible>(chemin, donnees))
    version.value = Date.now()
    afficherMessage(message)
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}

async function envoyer(evenement: Event) {
  const fichier = (evenement.target as HTMLInputElement).files?.[0]
  if (!fichier) return
  const formulaire = new FormData()
  formulaire.append('fichier', fichier)
  await changer(`/api/moi/annonces/${props.annonce.id}/photos`, formulaire, 'Photo ajoutée.')
  if (champ.value) champ.value.value = ''
}
</script>

<template>
  <AppSection titre="Photos">
    <template #action>
      <span class="text-[13.5px] text-texte-doux">{{ annonce.nombre_photos }} / {{ PHOTOS_MAX }}</span>
    </template>
    <div class="flex flex-wrap gap-2.5">
      <div v-for="ordre in annonce.nombre_photos" :key="`${ordre}-${version}`" class="relative size-24">
        <img
          :src="`/api/annonces/${annonce.id}/photos/${ordre}?v=${version}`"
          :alt="`Photo n° ${ordre}`"
          class="size-24 rounded-rafals object-cover"
        />
        <span class="absolute bottom-1 left-1 rounded-full bg-surface px-1.5 text-xs font-bold">{{ ordre }}</span>
        <button
          type="button"
          class="absolute top-1 right-1 size-7 rounded-full bg-surface font-bold text-erreur"
          :aria-label="`Retirer la photo n° ${ordre}`"
          @click="changer(`/api/moi/annonces/${annonce.id}/photos/${ordre}/retirer`, {}, 'Photo retirée.')"
        >
          ×
        </button>
      </div>
      <button
        v-if="annonce.nombre_photos < PHOTOS_MAX"
        type="button"
        class="grid size-24 place-items-center rounded-rafals border-[1.5px] border-dashed border-primaire text-center text-[13px] font-semibold text-primaire"
        @click="champ?.click()"
      >
        + Ajouter<br />une photo
      </button>
      <input ref="champ" type="file" accept="image/jpeg,image/png" class="sr-only" @change="envoyer" />
    </div>
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <p class="text-[13px] text-texte-doux">JPG ou PNG, 5 Mo au plus. La n° 1 est montrée en premier.</p>
  </AppSection>
</template>
