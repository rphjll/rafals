<script setup lang="ts">
// Carte d'une adresse unique, ajoutée, modifiée ou effacée : adresse du client (Mon compte, RM-CLIENTS.md)
// et adresse où le prestataire reçoit ses clients (RM-PRESTATAIRES.md). `chemin` : GET chemin, POST chemin, POST chemin/effacer.
// Les champs eux-mêmes (rue, ville, code postal) sont dans ChampsAdresse.
import { onMounted, ref } from 'vue'
import { appelerServeur, messageErreur } from '../api'
import { useMessage } from '../composables/useMessage'
import type { CommuneVisible } from '../outils/prestataires'
import ChampsAdresse from './ChampsAdresse.vue'
import AppAlerte from './ui/AppAlerte.vue'
import AppBouton from './ui/AppBouton.vue'
import AppChamp from './ui/AppChamp.vue'
import AppSection from './ui/AppSection.vue'

interface Adresse {
  ligne: string
  complement: string | null
  code_postal: string
  commune: CommuneVisible
}

const props = defineProps<{
  titre: string
  chemin: string
  texteVide: string
  texteAjouter: string
  texteEffacer: string
  /** Phrase montrée sous l'adresse enregistrée (facultative) */
  note?: string
}>()
// Prévient la page (ex. la fenêtre de réservation) quand l'adresse change : la nouvelle adresse, ou null si effacée
const emit = defineEmits<{ change: [adresse: Adresse | null] }>()
const { afficherMessage } = useMessage()
const adresse = ref<Adresse | null>(null)
const chargee = ref(false)
const enModification = ref(false)
const ligne = ref('')
const complement = ref('')
const commune = ref<CommuneVisible | null>(null)
const codePostal = ref('')
const erreur = ref('')
const envoiEnCours = ref(false)

onMounted(async () => {
  try {
    adresse.value = await appelerServeur<Adresse | null>(props.chemin)
    emit('change', adresse.value)
  } catch (e) {
    erreur.value = messageErreur(e)
  } finally {
    chargee.value = true
  }
})

function ouvrir() {
  ligne.value = adresse.value?.ligne ?? ''
  complement.value = adresse.value?.complement ?? ''
  commune.value = adresse.value?.commune ?? null
  codePostal.value = adresse.value?.code_postal ?? ''
  erreur.value = ''
  enModification.value = true
}

async function enregistrer() {
  erreur.value = ''
  if (!commune.value) {
    erreur.value = 'Choisissez la ville.'
    return
  }
  if (!codePostal.value) {
    erreur.value = 'Choisissez le code postal.'
    return
  }
  envoiEnCours.value = true
  try {
    adresse.value = await appelerServeur<Adresse>(props.chemin, {
      ligne: ligne.value,
      complement: complement.value.trim() || null,
      commune_id: commune.value.id,
      code_postal: codePostal.value,
    })
    enModification.value = false
    emit('change', adresse.value)
    afficherMessage('Adresse enregistrée.')
  } catch (e) {
    erreur.value = messageErreur(e)
  } finally {
    envoiEnCours.value = false
  }
}

async function effacer() {
  erreur.value = ''
  try {
    afficherMessage((await appelerServeur<{ message: string }>(`${props.chemin}/effacer`, {})).message)
    adresse.value = null
    emit('change', null)
  } catch (e) {
    erreur.value = messageErreur(e) // ex. « Vos clients viennent chez vous : changez d'abord le lieu de vos services… »
  }
}
</script>

<template>
  <AppSection v-if="chargee" :titre="titre">
    <form v-if="enModification" class="flex flex-col gap-3.5" @submit.prevent="enregistrer">
      <ChampsAdresse v-model:ligne="ligne" v-model:commune="commune" v-model:code-postal="codePostal">
        <AppChamp v-model="complement" etiquette="Complément" autocomplete="address-line2" placeholder="Bâtiment, étage, code…" />
      </ChampsAdresse>
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <div class="flex flex-wrap gap-2">
        <AppBouton type="submit" :occupe="envoiEnCours">Enregistrer</AppBouton>
        <AppBouton variante="secondaire" @click="enModification = false">Annuler</AppBouton>
      </div>
    </form>

    <template v-else-if="adresse">
      <p class="font-medium">
        {{ adresse.ligne }}<br />
        <template v-if="adresse.complement">{{ adresse.complement }}<br /></template>
        {{ adresse.code_postal }} {{ adresse.commune.nom }}
      </p>
      <p v-if="note" class="text-[13.5px] text-texte-doux">{{ note }}</p>
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <div class="flex flex-wrap gap-2">
        <AppBouton variante="secondaire" @click="ouvrir">Modifier</AppBouton>
        <AppBouton variante="danger" @click="effacer">{{ texteEffacer }}</AppBouton>
      </div>
    </template>

    <template v-else>
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <p class="text-[13.5px] text-texte-doux">{{ texteVide }}</p>
      <div><AppBouton variante="secondaire" @click="ouvrir">{{ texteAjouter }}</AppBouton></div>
    </template>
  </AppSection>
</template>
