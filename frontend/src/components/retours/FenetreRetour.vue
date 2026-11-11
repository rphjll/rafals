<script setup lang="ts">
// « Un problème ? Une idée ? » (lot 13.1, .doc/ihm/RM-RETOURS-IHM.md ; règle RM-RETOURS.md) : ouverte depuis le menu
// du compte. Problème ou idée, le texte, une capture d'écran facultative ; la page où l'on est part avec le message,
// l'appareil et le navigateur sont lus par le serveur. Les refus du serveur (texte trop court, 5 par jour, image)
// s'affichent juste au-dessus des boutons.
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppChampFichier from '../ui/AppChampFichier.vue'
import AppChoix from '../ui/AppChoix.vue'
import AppFenetre from '../ui/AppFenetre.vue'
import AppZoneTexte from '../ui/AppZoneTexte.vue'

type Sorte = 'probleme' | 'idee'

const props = defineProps<{ ouverte: boolean }>()
const emit = defineEmits<{ fermer: [] }>()
const route = useRoute()
const { afficherMessage } = useMessage()

const sorte = ref<Sorte>('probleme')
const texte = ref('')
const capture = ref<File | null>(null)
const erreur = ref('')
const envoi = ref(false)
// À chaque ouverture, une fenêtre vide
watch(
  () => props.ouverte,
  (ouverte) => {
    if (ouverte) [sorte.value, texte.value, capture.value, erreur.value] = ['probleme', '', null, '']
  },
)

const options: { valeur: Sorte; texte: string; detail: string }[] = [
  { valeur: 'probleme', texte: 'Un problème', detail: 'quelque chose ne marche pas' },
  { valeur: 'idee', texte: 'Une idée', detail: 'quelque chose à ajouter' },
]
const etiquette = computed(() => (sorte.value === 'probleme' ? "Que s'est-il passé ?" : 'Quelle est votre idée ?'))
const exemple = computed(() =>
  sorte.value === 'probleme'
    ? 'Ex. Le bouton Publier ne répond pas sur mon téléphone.'
    : 'Ex. Pouvoir mettre une vidéo de mon travail sur mon profil.',
)

async function envoyer() {
  erreur.value = ''
  envoi.value = true
  const formulaire = new FormData()
  formulaire.append('sorte', sorte.value)
  formulaire.append('texte', texte.value)
  formulaire.append('page', route.fullPath)
  if (capture.value) formulaire.append('capture', capture.value)
  try {
    const reponse = await appelerServeur<{ message: string }>('/api/retours', formulaire)
    afficherMessage(reponse.message)
    emit('fermer')
  } catch (e) {
    erreur.value = messageErreur(e)
  } finally {
    envoi.value = false
  }
}
</script>

<template>
  <AppFenetre :ouverte="ouverte" titre="Un problème ? Une idée ?" @fermer="emit('fermer')">
    <div class="flex flex-col gap-4 text-texte">
      <AppChoix v-model="sorte" etiquette="Vous nous écrivez pour" :options="options" />
      <AppZoneTexte v-model="texte" :etiquette="etiquette" obligatoire :maximum="2000" :aide="exemple" />
      <div class="flex flex-col gap-2">
        <AppChampFichier v-model="capture" etiquette="Capture d'écran (facultatif)" aide="JPG ou PNG, 5 Mo au plus" accepte="image/png,image/jpeg" />
        <AppBouton v-if="capture" variante="secondaire" class="self-start" @click="capture = null">Retirer la capture</AppBouton>
      </div>
      <p class="text-[13px] text-texte-doux">
        La page où vous êtes, votre appareil et votre navigateur sont joints tout seuls pour nous aider. Rien d'autre.
      </p>
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    </div>
    <template #pied>
      <AppBouton :occupe="envoi" @click="envoyer">{{ sorte === 'probleme' ? 'Envoyer le problème' : "Envoyer l'idée" }}</AppBouton>
      <AppBouton variante="secondaire" @click="emit('fermer')">Annuler</AppBouton>
    </template>
  </AppFenetre>
</template>
