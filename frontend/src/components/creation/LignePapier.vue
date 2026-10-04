<script setup lang="ts">
// Un papier du dossier de création : son nom, son explication, son état, et le bouton pour le déposer ou le remplacer.
// Utilisé à l'étape 4 et dans le suivi (un papier à refaire).
import { computed, ref } from 'vue'
import { messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { CHEMIN, envoyerEtape, type PieceVisible, type Situation } from '../../outils/creation'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBadge from '../ui/AppBadge.vue'
import AppBouton from '../ui/AppBouton.vue'

const props = defineProps<{ piece: PieceVisible; modifiable: boolean }>()
const emit = defineEmits<{ enregistre: [situation: Situation] }>()
const { afficherMessage } = useMessage()
const champ = ref<HTMLInputElement | null>(null)
const erreur = ref('')
const envoiEnCours = ref(false)

const EXPLICATIONS: Record<string, string> = {
  identite:
    "Carte d'identité (recto et verso) ou passeport. Écrivez à la main sur la copie : « J'atteste sur l'honneur que cette copie est conforme à l'original », la date et votre signature.",
  titre_sejour: 'Votre titre de séjour ou carte de résident, en cours de validité.',
  diplome: "Demandé parce que votre métier est réglementé. ex. CAP, BEP, ou bulletins de salaire prouvant 3 ans d'expérience.",
  autorisation_parents: 'Vous avez moins de 18 ans : une lettre de vos parents qui vous autorisent à créer votre entreprise, datée et signée.',
  bail: 'Le bail ou le contrat de votre local.',
  attestation: "« Je n'ai jamais été condamné à une interdiction de gérer une entreprise. » rafals l'écrit avec votre nom et celui de vos parents ; vous la signez en envoyant le dossier.",
  pouvoir: 'Vous autorisez rafals à déposer ce dossier en votre nom.',
}
const titre = computed(() => props.piece.nom.replace(/^(la |le |l')/, '').replace(/^./, (c) => c.toUpperCase()))
const deposee = computed(() => props.piece.depose_le !== null)
const badge = computed(() => {
  if (props.piece.efface) return { etat: 'neutre' as const, texte: 'effacé' }
  if (props.piece.a_refaire) return { etat: 'erreur' as const, texte: 'à refaire' }
  if (deposee.value) return { etat: 'ok' as const, texte: props.piece.deposee_par_rafals ? 'écrit par rafals' : 'déposé' }
  return props.piece.deposee_par_rafals
    ? { etat: 'neutre' as const, texte: 'préparé par rafals' }
    : { etat: 'attente' as const, texte: 'à déposer' }
})

async function choisi(evenement: Event) {
  const fichier = (evenement.target as HTMLInputElement).files?.[0]
  if (!fichier) return
  erreur.value = ''
  envoiEnCours.value = true
  try {
    const formulaire = new FormData()
    formulaire.append('fichier', fichier)
    emit('enregistre', await envoyerEtape(`/pieces/${props.piece.sorte}`, formulaire))
    afficherMessage('Papier déposé.')
  } catch (e) {
    erreur.value = messageErreur(e)
  } finally {
    envoiEnCours.value = false
    if (champ.value) champ.value.value = ''
  }
}
</script>

<template>
  <div class="flex flex-col gap-2 rounded-rafals border border-bord p-3">
    <div class="flex flex-wrap items-center justify-between gap-2">
      <b>{{ titre }}</b>
      <AppBadge :etat="badge.etat">{{ badge.texte }}</AppBadge>
    </div>
    <p class="text-[13.5px] text-texte-doux">{{ EXPLICATIONS[piece.sorte] }}</p>
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <div v-if="!piece.efface && (deposee || (modifiable && !piece.deposee_par_rafals))" class="flex flex-wrap gap-2">
      <AppBouton v-if="modifiable && !piece.deposee_par_rafals" variante="secondaire" :occupe="envoiEnCours" @click="champ?.click()">
        {{ deposee ? 'Remplacer…' : 'Choisir un fichier…' }}
      </AppBouton>
      <a
        v-if="deposee"
        :href="`${CHEMIN}/pieces/${piece.sorte}`"
        target="_blank"
        rel="noopener"
        class="inline-flex min-h-[42px] items-center px-2 font-semibold text-primaire underline"
      >
        Voir
      </a>
    </div>
    <input ref="champ" type="file" accept="application/pdf,image/jpeg" class="sr-only" :aria-label="`Fichier : ${titre}`" @change="choisi" />
  </div>
</template>
