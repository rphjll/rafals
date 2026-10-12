<script setup lang="ts">
// Fenêtre « Votre avis sur Léa Martin » (.doc/ihm/RM-AVIS-IHM.md) : la note en étoiles cliquables, puis le texte.
// Sert à donner un avis (sur un rendez-vous) et à le modifier (pendant les 30 jours).
import { ref, watch } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { AVIS_CLIENT_TEXTE_MAX, AVIS_TEXTE_MAX, type AvisDetaille } from '../../outils/avis'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppFenetre from '../ui/AppFenetre.vue'
import AppZoneTexte from '../ui/AppZoneTexte.vue'

/** cible : le rendez-vous à noter (nouvel avis) ou l'avis à modifier ; null = fenêtre fermée */
const props = defineProps<{
  // versClient : c'est le prestataire qui note son client (lot 8.6) ; « prestataire » est alors le nom du client
  cible: { rendezVousId: number; avis: Pick<AvisDetaille, 'id' | 'note' | 'texte'> | null; prestataire: string; quoi: string; versClient?: boolean } | null
}>()
const emit = defineEmits<{ fermer: []; enregistre: [] }>()
const { afficherMessage } = useMessage()

const note = ref(0)
const texte = ref('')
const erreur = ref('')
const envoiEnCours = ref(false)
watch(
  () => props.cible,
  (c) => {
    note.value = c?.avis?.note ?? 0
    texte.value = c?.avis?.texte ?? ''
    erreur.value = ''
  },
)

async function publier() {
  const c = props.cible
  if (!c) return
  erreur.value = ''
  if (!note.value) {
    erreur.value = 'Choisissez une note de 1 à 5 étoiles.'
    return
  }
  envoiEnCours.value = true
  try {
    const chemin = c.versClient
      ? c.avis ? `/api/moi/prestataire/avis-clients/${c.avis.id}/modifier` : `/api/moi/prestataire/rendez-vous/${c.rendezVousId}/avis-client`
      : c.avis ? `/api/moi/avis/${c.avis.id}/modifier` : `/api/moi/rendez-vous/${c.rendezVousId}/avis`
    await appelerServeur(chemin, { note: note.value, texte: texte.value })
    afficherMessage(c.avis ? 'Votre avis est modifié.' : 'Merci : votre avis est publié.')
    emit('enregistre')
  } catch (e) {
    erreur.value = messageErreur(e) // ex. « Votre avis semble injurieux : reformulez-le calmement… »
  } finally {
    envoiEnCours.value = false
  }
}
</script>

<template>
  <AppFenetre :ouverte="cible !== null" :titre="`Votre avis sur ${cible?.prestataire}`" @fermer="emit('fermer')">
    <div v-if="cible" class="flex flex-col gap-3 text-texte">
      <p class="text-[14px] text-texte-doux">{{ cible.quoi }}</p>
      <div class="flex flex-col gap-1">
        <span class="text-[13px] font-semibold">Note <span class="text-erreur" aria-hidden="true">*</span></span>
        <div class="flex gap-1" role="radiogroup" aria-label="Note de 1 à 5 étoiles">
          <button
            v-for="n in 5"
            :key="n"
            type="button"
            role="radio"
            :aria-checked="note === n"
            :aria-label="`${n} étoile${n > 1 ? 's' : ''}`"
            class="min-h-[42px] px-0.5 text-[30px] leading-none"
            :class="n <= note ? 'text-accent' : 'text-bord'"
            @click="note = n"
          >
            ★
          </button>
        </div>
      </div>
      <AppZoneTexte
        v-model="texte"
        etiquette="Votre avis"
        obligatoire
        :maximum="cible.versClient ? AVIS_CLIENT_TEXTE_MAX : AVIS_TEXTE_MAX"
        :aide="cible.versClient ? 'De 10 à 500 caractères. Signé de votre nom affiché, visible sur la page publique de ce client.' : 'De 10 à 1000 caractères. Signé de votre prénom et de l’initiale de votre nom.'"
      />
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    </div>
    <template #pied>
      <AppBouton :occupe="envoiEnCours" @click="publier">{{ cible?.avis ? 'Enregistrer' : 'Publier mon avis' }}</AppBouton>
      <AppBouton variante="secondaire" @click="emit('fermer')">Annuler</AppBouton>
    </template>
  </AppFenetre>
</template>
