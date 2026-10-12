<script setup lang="ts">
// Carte d'une demande (.doc/ihm/RM-ACCUEIL-IHM.md, RM-DEMANDES-IHM.md) : la même sur l'accueil, dans « Demandes près
// de chez moi » et dans « Mes demandes ». Un prestataire qui peut répondre voit [Répondre] ; les boutons propres à
// une page (fermer, prolonger…) arrivent par l'emplacement du bas.
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../../api'
import { useCompte } from '../../composables/useCompte'
import { texteNote } from '../../outils/avis'
import { formaterDate } from '../../outils/dates'
import { initialesDe } from '../../outils/noms'
import { type DemandeVisible, REPONSES_MAX, texteBudget, texteQuand } from '../../outils/demandes'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBadge from '../ui/AppBadge.vue'
import AppBouton from '../ui/AppBouton.vue'

const props = defineProps<{ demande: DemandeVisible }>()
const routeur = useRouter()
const { compte } = useCompte()
const erreur = ref('')
const occupe = ref(false)
const initiales = computed(() => initialesDe(props.demande.client))

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
  <article class="carte flex flex-col gap-3.5 p-5">
    <!-- Qui demande, où, quand ; le budget à droite -->
    <div class="flex items-center gap-3">
      <span class="grid size-11 shrink-0 place-items-center rounded-full bg-primaire-doux font-bold text-primaire" aria-hidden="true">
        {{ initiales }}
      </span>
      <div class="mr-auto flex min-w-0 flex-col leading-tight">
        <b>{{ demande.client }}</b>
        <span v-if="demande.client_avis" class="text-[13.5px]">
          <b class="text-accent">{{ texteNote(demande.client_note, demande.client_avis) }}</b>
          <RouterLink :to="`/clients/${demande.client_id}/avis`" class="ml-1 font-semibold text-primaire underline">Voir les avis</RouterLink>
        </span>
        <span class="text-[13.5px] text-texte-doux">{{ demande.ville }} · {{ formaterDate(demande.cree_le) }}</span>
      </div>
      <b v-if="demande.budget_centimes" class="rounded-full bg-primaire px-3.5 py-1 text-[17px] whitespace-nowrap text-primaire-texte tabular-nums">
        {{ texteBudget(demande.budget_centimes) }}
      </b>
      <span v-else class="rounded-full bg-fond px-3 py-1 text-[13.5px] font-bold whitespace-nowrap text-primaire">Prix à proposer</span>
    </div>
    <div class="flex flex-col gap-1">
      <h3 class="text-[19px] leading-snug font-bold">{{ demande.titre }}</h3>
      <p class="whitespace-pre-line text-texte-doux">{{ demande.description }}</p>
    </div>
    <!-- Les photos demandent d'être connecté : elles montrent souvent l'intérieur d'un logement -->
    <div v-if="demande.nombre_photos && compte" class="flex flex-wrap gap-2">
      <a v-for="n in demande.nombre_photos" :key="n" :href="`/api/demandes/${demande.id}/photos/${n}`" target="_blank" rel="noopener">
        <img :src="`/api/demandes/${demande.id}/photos/${n}`" :alt="`Photo ${n} de la demande « ${demande.titre} »`" class="size-24 rounded-rafals object-cover" />
      </a>
    </div>
    <div class="flex flex-wrap gap-1.5">
      <AppBadge etat="neutre">{{ demande.metier }}</AppBadge>
      <AppBadge etat="neutre">{{ texteQuand(demande) }}</AppBadge>
      <AppBadge etat="neutre">{{ demande.lieu === 'chez_moi' ? 'Chez le client' : 'Chez le prestataire' }}</AppBadge>
      <AppBadge etat="neutre">{{ demande.nombre_reponses }} réponse{{ demande.nombre_reponses > 1 ? 's' : '' }} sur {{ REPONSES_MAX }}</AppBadge>
      <AppBadge v-if="demande.a_moi" etat="ok">Ma demande</AppBadge>
      <AppBadge v-if="demande.nombre_photos && !compte" etat="neutre">
        {{ demande.nombre_photos }} photo{{ demande.nombre_photos > 1 ? 's' : '' }} (connectez-vous pour les voir)
      </AppBadge>
    </div>
    <div v-if="demande.conversation_id || demande.peut_repondre || demande.raison_verrou || (compte?.prestataire_id && demande.complete && !demande.a_moi) || $slots.default" class="flex flex-wrap gap-2">
      <AppBouton v-if="demande.conversation_id" variante="secondaire" @click="routeur.push(`/messages/${demande.conversation_id}`)">
        Voir la conversation
      </AppBouton>
      <AppBouton v-else-if="demande.peut_repondre" :occupe="occupe" @click="repondre">Répondre</AppBouton>
      <!-- Prestataire sans SIRET : métier qui en demande un, adresse ou case manquante, plafond de l'année atteint -->
      <AppBouton v-else-if="demande.raison_verrou" variante="verrouille" :raison-verrou="demande.raison_verrou">Répondre</AppBouton>
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
