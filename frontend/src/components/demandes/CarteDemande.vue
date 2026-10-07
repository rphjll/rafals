<script setup lang="ts">
// Carte d'une demande (.doc/ihm/RM-ACCUEIL-IHM.md, RM-DEMANDES-IHM.md) : la même sur l'accueil, dans « Demandes près
// de chez moi » et dans « Mes demandes ». Un prestataire qui peut répondre voit [Répondre] ; les boutons propres à
// une page (fermer, prolonger…) arrivent par l'emplacement du bas.
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../../api'
import { useCompte } from '../../composables/useCompte'
import { type DemandeVisible, REPONSES_MAX, texteBudget, texteQuand } from '../../outils/demandes'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBadge from '../ui/AppBadge.vue'
import AppBouton from '../ui/AppBouton.vue'

const props = defineProps<{ demande: DemandeVisible }>()
const routeur = useRouter()
const { compte } = useCompte()
const erreur = ref('')
const occupe = ref(false)

async function repondre() {
  erreur.value = ''
  occupe.value = true
  try {
    const { conversation_id } = await appelerServeur<{ conversation_id: number }>(`/api/demandes/${props.demande.id}/repondre`, {})
    routeur.push(`/messages/${conversation_id}`)
  } catch (e) {
    erreur.value = messageErreur(e) // ex. « Cette demande est complète : 10 prestataires ont déjà répondu. »
  } finally {
    occupe.value = false
  }
}
</script>

<template>
  <article class="flex flex-col gap-2 rounded-rafals border border-bord bg-surface p-5">
    <div class="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1">
      <b class="text-[17px]">{{ demande.titre }}</b>
      <b v-if="demande.budget_centimes" class="font-titre text-lg text-primaire">{{ texteBudget(demande.budget_centimes) }}</b>
    </div>
    <div class="flex flex-wrap gap-1.5">
      <AppBadge etat="neutre">{{ demande.metier }}</AppBadge>
      <AppBadge etat="neutre">{{ demande.ville }}</AppBadge>
      <AppBadge etat="neutre">{{ texteQuand(demande) }}</AppBadge>
      <AppBadge etat="neutre">{{ demande.lieu === 'chez_moi' ? 'Chez le client' : 'Chez le prestataire' }}</AppBadge>
      <AppBadge etat="neutre">{{ demande.nombre_reponses }} réponse{{ demande.nombre_reponses > 1 ? 's' : '' }} sur {{ REPONSES_MAX }}</AppBadge>
      <AppBadge v-if="demande.a_moi" etat="ok">Ma demande</AppBadge>
    </div>
    <p class="whitespace-pre-line text-texte-doux">{{ demande.description }}</p>
    <!-- Les photos demandent d'être connecté : elles montrent souvent l'intérieur d'un logement -->
    <div v-if="demande.nombre_photos && compte" class="flex flex-wrap gap-2">
      <a v-for="n in demande.nombre_photos" :key="n" :href="`/api/demandes/${demande.id}/photos/${n}`" target="_blank" rel="noopener">
        <img :src="`/api/demandes/${demande.id}/photos/${n}`" :alt="`Photo ${n} de la demande « ${demande.titre} »`" class="size-24 rounded-rafals border border-bord object-cover" />
      </a>
    </div>
    <span class="text-[13px] text-texte-doux">
      {{ demande.client }}<template v-if="demande.nombre_photos && !compte">
        · {{ demande.nombre_photos }} photo{{ demande.nombre_photos > 1 ? 's' : '' }} (connectez-vous pour les voir)</template>
    </span>
    <div v-if="demande.conversation_id || demande.peut_repondre || (compte?.prestataire_id && demande.complete && !demande.a_moi) || $slots.default" class="flex flex-wrap gap-2">
      <AppBouton v-if="demande.conversation_id" variante="secondaire" @click="routeur.push(`/messages/${demande.conversation_id}`)">
        Voir la conversation
      </AppBouton>
      <AppBouton v-else-if="demande.peut_repondre" :occupe="occupe" @click="repondre">Répondre</AppBouton>
      <AppBouton
        v-else-if="compte?.prestataire_id && demande.complete && !demande.a_moi"
        variante="verrouille"
        :raison-verrou="`Cette demande est complète : ${REPONSES_MAX} prestataires ont déjà répondu.`"
      >
        Répondre
      </AppBouton>
      <slot />
    </div>
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
  </article>
</template>
