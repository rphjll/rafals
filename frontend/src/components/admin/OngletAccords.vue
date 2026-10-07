<script setup lang="ts">
// Administration › Accords à vérifier (.doc/ihm/RM-ADMINISTRATION-IHM.md).
import { onMounted, ref } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { age, formaterDateHeure } from '../../outils/dates'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppChamp from '../ui/AppChamp.vue'
import AppFenetre from '../ui/AppFenetre.vue'

interface AccordAVerifier {
  id: number
  depose_le: string
  prenom: string
  nom: string
  date_naissance: string
  nom_fichier: string
}

const emit = defineEmits<{ maj: [] }>()
const { afficherMessage } = useMessage()
const accords = ref<AccordAVerifier[]>([])
const erreur = ref('')

async function charger() {
  try {
    accords.value = await appelerServeur<AccordAVerifier[]>('/api/admin/accords')
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
onMounted(charger)

async function apresDecision(message: string) {
  afficherMessage(message)
  await charger()
  emit('maj')
}

function voirFichier(accord: AccordAVerifier) {
  window.open(`/api/admin/accords/${accord.id}/fichier`, '_blank')
}

async function accepter(accord: AccordAVerifier) {
  try {
    await appelerServeur(`/api/admin/accords/${accord.id}/decision`, { accepte: true })
    await apresDecision(`Accord de ${accord.prenom} ${accord.nom} accepté.`)
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}

const aRefuser = ref<AccordAVerifier | null>(null)
const motif = ref('')
const erreurFenetre = ref('')

function ouvrirRefus(accord: AccordAVerifier) {
  aRefuser.value = accord
  motif.value = ''
  erreurFenetre.value = ''
}

async function refuser() {
  const accord = aRefuser.value
  if (!accord) return
  try {
    await appelerServeur(`/api/admin/accords/${accord.id}/decision`, { accepte: false, motif_refus: motif.value })
    aRefuser.value = null
    await apresDecision(`Accord refusé : ${accord.prenom} ${accord.nom} verra le motif.`)
  } catch (e) {
    erreurFenetre.value = messageErreur(e)
  }
}
</script>

<template>
  <div class="flex flex-col gap-3">
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <p v-if="!accords.length" class="text-texte-doux">Aucun accord à vérifier pour l'instant.</p>
    <div
      v-for="accord in accords"
      :key="accord.id"
      class="grid items-center gap-3 carte p-3.5 sm:grid-cols-[1fr_auto]"
    >
      <div>
        <b>{{ accord.prenom }} {{ accord.nom }}</b> · {{ age(accord.date_naissance) }} ans · envoyé le
        {{ formaterDateHeure(accord.depose_le) }}
        <div class="text-[13px] text-texte-doux">{{ accord.nom_fichier }}</div>
      </div>
      <div class="flex flex-wrap gap-2">
        <AppBouton variante="secondaire" @click="voirFichier(accord)">Voir le fichier</AppBouton>
        <AppBouton @click="accepter(accord)">Accepter</AppBouton>
        <AppBouton variante="danger" @click="ouvrirRefus(accord)">Refuser…</AppBouton>
      </div>
    </div>

    <AppFenetre
      :ouverte="aRefuser !== null"
      :titre="`Refuser l'accord de ${aRefuser?.prenom} ${aRefuser?.nom} ?`"
      @fermer="aRefuser = null"
    >
      <div class="flex flex-col gap-3">
        <p>Le motif sera montré à {{ aRefuser?.prenom }}, qui pourra en renvoyer un.</p>
        <AppChamp v-model="motif" etiquette="Motif du refus" obligatoire aide="Ex. « Signature illisible »" />
        <AppAlerte v-if="erreurFenetre">{{ erreurFenetre }}</AppAlerte>
      </div>
      <template #pied>
        <AppBouton variante="danger" @click="refuser">Refuser</AppBouton>
        <AppBouton variante="secondaire" @click="aRefuser = null">Annuler</AppBouton>
      </template>
    </AppFenetre>
  </div>
</template>
