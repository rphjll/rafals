<script setup lang="ts">
// Étape 4 « Vos papiers » du dossier de création d'auto-entreprise (.doc/ihm/RM-CREATION-AUTO-ENTREPRISE-IHM.md).
import { computed, ref } from 'vue'
import { messageErreur } from '../../api'
import { type DossierCreation, envoyerEtape, type PieceVisible, type Situation } from '../../outils/creation'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppChamp from '../ui/AppChamp.vue'
import AppSection from '../ui/AppSection.vue'
import LignePapier from './LignePapier.vue'

const props = defineProps<{ dossier: DossierCreation }>()
const emit = defineEmits<{ enregistre: [situation: Situation]; suite: [situation: Situation]; retour: [] }>()

const pere = ref(props.dossier.pere_nom ?? '')
const mere = ref(props.dossier.mere_nom ?? '')
const erreur = ref('')
const envoiEnCours = ref(false)

// L'attestation est écrite par rafals au moment de l'envoi : on la montre ici « préparée »
const attestation: PieceVisible = { sorte: 'attestation', nom: "l'attestation sur l'honneur", deposee_par_rafals: true, depose_le: null, a_refaire: false, efface: false }
const papiers = computed(() => [
  ...props.dossier.pieces.filter((p) => !p.deposee_par_rafals),
  props.dossier.pieces.find((p) => p.sorte === 'attestation') ?? attestation,
])
// Ce qui manque parmi les papiers à déposer (les noms des parents sont envoyés par le bouton)
const manquants = computed(() => (props.dossier.manque.papiers ?? []).filter((m) => m !== 'les noms de vos parents'))

async function enregistrer() {
  erreur.value = ''
  envoiEnCours.value = true
  try {
    emit('suite', await envoyerEtape('/parents', { pere_nom: pere.value, mere_nom: mere.value }))
  } catch (e) {
    erreur.value = messageErreur(e)
  } finally {
    envoiEnCours.value = false
  }
}
</script>

<template>
  <AppSection titre="Vos papiers">
    <p class="text-[13.5px] text-texte-doux">En PDF ou en photo JPG (rafals range la photo dans un PDF). 10 Mo au plus par papier.</p>
    <LignePapier v-for="piece in papiers" :key="piece.sorte" :piece="piece" modifiable @enregistre="(s) => emit('enregistre', s)" />
    <form class="flex flex-col gap-3.5" @submit.prevent="enregistrer">
      <div class="grid gap-3.5 sm:grid-cols-2">
        <AppChamp v-model="pere" etiquette="Nom et prénom de votre père" obligatoire aide="Demandé par l'administration pour l'attestation. Sinon : « inconnu »." />
        <AppChamp v-model="mere" etiquette="Nom de naissance et prénom de votre mère" obligatoire />
      </div>
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <div class="flex flex-wrap justify-between gap-2">
        <AppBouton variante="secondaire" @click="emit('retour')">Retour</AppBouton>
        <AppBouton v-if="manquants.length" variante="verrouille" :raison-verrou="`Il manque : ${manquants.join(', ')}.`">
          Enregistrer et continuer
        </AppBouton>
        <AppBouton v-else type="submit" :occupe="envoiEnCours">Enregistrer et continuer</AppBouton>
      </div>
    </form>
  </AppSection>
</template>
