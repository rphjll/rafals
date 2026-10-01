<script setup lang="ts">
// Mon activité › Mes métiers (.doc/ihm/RM-PROPOSER-IHM.md ; RM-ANNONCES.md) : une date de fin au lieu d'un bouton
// « supprimer ». Métier principal : on choisit lequel le remplacera. Métier arrêté : [Reprendre ce métier].
import { computed, ref } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { aujourdhuiIso, formaterDate } from '../../outils/dates'
import type { MetierExerce, ProfilPrestataire } from '../../outils/prestataires'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBadge from '../ui/AppBadge.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppChamp from '../ui/AppChamp.vue'
import AppFenetre from '../ui/AppFenetre.vue'
import AppSection from '../ui/AppSection.vue'
import AppSelection from '../ui/AppSelection.vue'

const props = defineProps<{ profil: ProfilPrestataire }>()
const emit = defineEmits<{ maj: [profil: ProfilPrestataire] }>()
const { afficherMessage } = useMessage()

const cible = ref<MetierExerce | null>(null)
const date = ref('')
const suivantId = ref<number | null>(null)
const erreur = ref('')
const estPrincipal = computed(() => cible.value?.id === props.profil.metier_principal.id)

function ouvrir(metier: MetierExerce) {
  cible.value = metier
  date.value = metier.fin_le ?? ''
  suivantId.value = props.profil.metier_principal_suivant?.id ?? props.profil.metiers_secondaires[0]?.id ?? null
  erreur.value = ''
}

async function envoyer(metier: MetierExerce, finLe: string | null, message: string) {
  try {
    emit('maj', await appelerServeur<ProfilPrestataire>('/api/moi/prestataire/metiers/fin', {
      metier_id: metier.id,
      fin_le: finLe,
      suivant_id: finLe && metier.id === props.profil.metier_principal.id ? suivantId.value : null,
    }))
    cible.value = null
    afficherMessage(message)
  } catch (e) {
    if (cible.value) erreur.value = messageErreur(e)
    else afficherMessage(messageErreur(e), 'erreur')
  }
}

function enregistrer() {
  if (!cible.value) return
  if (!date.value) {
    erreur.value = 'Choisissez le dernier jour.'
    return
  }
  envoyer(cible.value, date.value, `Date de fin enregistrée : ${formaterDate(date.value)}.`)
}
</script>

<template>
  <AppSection titre="Mes métiers">
    <div class="flex flex-col divide-y divide-bord">
      <div class="flex flex-wrap items-center justify-between gap-2.5 py-3 first:pt-0">
        <div class="flex flex-col gap-1">
          <p class="flex flex-wrap items-center gap-2 font-semibold">
            {{ profil.metier_principal.nom }} <AppBadge etat="ok">principal</AppBadge>
          </p>
          <p v-if="profil.metier_principal.fin_le" class="text-[13.5px] text-texte-doux">
            Fin prévue le {{ formaterDate(profil.metier_principal.fin_le) }} :
            <template v-if="profil.metier_principal_suivant">
              ensuite, {{ profil.metier_principal_suivant.nom }} deviendra votre métier principal.
            </template>
            <template v-else>c'est votre seul métier ; votre profil restera affiché, sans annonce.</template>
          </p>
        </div>
        <AppBouton variante="secondaire" @click="ouvrir(profil.metier_principal)">
          {{ profil.metier_principal.fin_le ? 'Changer la date de fin…' : 'Mettre une date de fin…' }}
        </AppBouton>
      </div>

      <div
        v-for="metier in profil.metiers_secondaires"
        :key="metier.id"
        class="flex flex-wrap items-center justify-between gap-2.5 py-3"
      >
        <div class="flex flex-col gap-1">
          <p class="font-semibold">{{ metier.nom }}</p>
          <p v-if="metier.fin_le" class="text-[13.5px] text-texte-doux">Fin prévue le {{ formaterDate(metier.fin_le) }}.</p>
        </div>
        <AppBouton variante="secondaire" @click="ouvrir(metier)">
          {{ metier.fin_le ? 'Changer la date de fin…' : 'Mettre une date de fin…' }}
        </AppBouton>
      </div>

      <div
        v-for="metier in profil.metiers_arretes"
        :key="metier.id"
        class="flex flex-wrap items-center justify-between gap-2.5 py-3"
      >
        <div class="flex flex-col gap-1">
          <p class="flex flex-wrap items-center gap-2 font-semibold">
            {{ metier.nom }} <AppBadge>arrêté depuis le {{ formaterDate(metier.fin_le ?? '') }}</AppBadge>
          </p>
          <p class="text-[13.5px] text-texte-doux">Ses annonces sont en pause : reprenez le métier, puis republiez-les.</p>
        </div>
        <AppBouton @click="envoyer(metier, null, `${metier.nom} repris : republiez ses annonces dans « Mes annonces ».`)">
          Reprendre ce métier
        </AppBouton>
      </div>
    </div>
    <p class="text-[13px] text-texte-doux">
      Ajouter un métier : [Modifier mon profil]. Après la date de fin, les annonces du métier sont mises en pause (gardées),
      et les rendez-vous de ce métier pris après cette date sont annulés (clients prévenus).
    </p>
  </AppSection>

  <AppFenetre :ouverte="cible !== null" :titre="`Date de fin pour « ${cible?.nom} »`" @fermer="cible = null">
    <form class="flex flex-col gap-3" @submit.prevent="enregistrer">
      <AppChamp v-model="date" etiquette="Dernier jour" type="date" :min="aujourdhuiIso()" obligatoire />
      <AppSelection
        v-if="estPrincipal && profil.metiers_secondaires.length > 1"
        v-model="suivantId"
        etiquette="Ensuite, votre métier principal sera"
        obligatoire
        :options="profil.metiers_secondaires.map((m) => ({ valeur: m.id, texte: m.nom }))"
      />
      <p v-if="estPrincipal && profil.metiers_secondaires.length === 1">
        Ensuite, {{ profil.metiers_secondaires[0]?.nom }} deviendra votre métier principal.
      </p>
      <p v-if="estPrincipal && !profil.metiers_secondaires.length">
        C'est votre seul métier : après cette date, votre profil restera affiché, sans annonce.
      </p>
      <p v-else-if="!estPrincipal">Après cette date, ses annonces seront mises en pause. Vous pourrez le reprendre quand vous voudrez.</p>
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    </form>
    <template #pied>
      <AppBouton @click="enregistrer">Enregistrer</AppBouton>
      <AppBouton
        v-if="cible?.fin_le"
        variante="danger"
        @click="cible && envoyer(cible, null, `Plus de date de fin pour ${cible.nom}.`)"
      >
        Enlever la date
      </AppBouton>
      <AppBouton variante="secondaire" @click="cible = null">Annuler</AppBouton>
    </template>
  </AppFenetre>
</template>
