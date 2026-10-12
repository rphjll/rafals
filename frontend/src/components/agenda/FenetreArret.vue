<script setup lang="ts">
// Mon agenda › Calendrier › [Date d'arrêt] (.doc/ihm/RM-AGENDA-IHM.md ; RM-PRESTATAIRES.md) : le dernier jour de travail
// du métier de ce calendrier. Tous les jours d'après sont fermés. Métier principal : on choisit lequel le remplacera.
import { computed, ref, watch } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { ajouterJours, jourCourt, jourLisible } from '../../outils/agenda'
import type { MetierExerce, ProfilPrestataire } from '../../outils/prestataires'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppFenetre from '../ui/AppFenetre.vue'
import AppSelection from '../ui/AppSelection.vue'

const props = defineProps<{ ouverte: boolean; jour: string; metier: MetierExerce; profil: ProfilPrestataire }>()
const emit = defineEmits<{ majProfil: [profil: ProfilPrestataire]; fermer: [] }>()
const { afficherMessage } = useMessage()

const estPrincipal = computed(() => props.metier.id === props.profil.metier_principal.id)
const suivantId = ref<number | null>(null)
const erreur = ref('')
const envoiEnCours = ref(false)

watch(
  () => props.ouverte,
  (ouverte) => {
    if (!ouverte) return
    erreur.value = ''
    suivantId.value = props.profil.metier_principal_suivant?.id ?? props.profil.metiers_secondaires[0]?.id ?? null
  },
  { immediate: true },
)

async function arreter() {
  erreur.value = ''
  envoiEnCours.value = true
  try {
    emit('majProfil', await appelerServeur<ProfilPrestataire>('/api/moi/prestataire/metiers/fin', {
      metier_id: props.metier.id,
      fin_le: props.jour,
      suivant_id: estPrincipal.value ? suivantId.value : null,
    }))
    emit('fermer')
    afficherMessage(`${props.metier.nom} : dernier jour le ${jourCourt(props.jour)}.`)
  } catch (e) {
    erreur.value = messageErreur(e)
  } finally {
    envoiEnCours.value = false
  }
}
</script>

<template>
  <AppFenetre :ouverte="ouverte" :titre="`Date d'arrêt — ${metier.nom}`" @fermer="emit('fermer')">
    <div v-if="jour" class="flex flex-col gap-3 text-texte">
      <p>Dernier jour de travail : <b>{{ jourLisible(jour) }}</b>.</p>
      <p class="text-[13.5px] text-texte-doux">
        À partir du {{ jourCourt(ajouterJours(jour, 1)) }}, tous les jours du calendrier « {{ metier.nom }} » sont fermés
        . Les rendez-vous de ce métier pris après cette date sont annulés : chaque
        client est prévenu par mail.
      </p>
      <AppSelection
        v-if="estPrincipal && profil.metiers_secondaires.length > 1"
        v-model="suivantId"
        etiquette="Ensuite, votre métier principal sera"
        obligatoire
        :options="profil.metiers_secondaires.map((m) => ({ valeur: m.id, texte: m.nom }))"
      />
      <p v-else-if="estPrincipal && profil.metiers_secondaires.length === 1" class="text-[13.5px]">
        Ensuite, {{ profil.metiers_secondaires[0]?.nom }} deviendra votre métier principal.
      </p>
      <p v-else-if="estPrincipal" class="text-[13.5px]">
        C'est votre seul métier : après cette date, votre profil restera affiché.
      </p>
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    </div>
    <template #pied>
      <AppBouton variante="danger" :occupe="envoiEnCours" @click="arreter">
        Arrêter {{ metier.nom }} après le {{ jour ? jourCourt(jour) : '' }}
      </AppBouton>
      <AppBouton variante="secondaire" @click="emit('fermer')">Annuler</AppBouton>
    </template>
  </AppFenetre>
</template>
