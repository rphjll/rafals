<script setup lang="ts">
// Une annonce dans « Mes annonces » (.doc/ihm/RM-MES-ANNONCES-IHM.md) : photo, titre, état, prix, raison si cachée, actions.
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { type AnnonceVisible, LIEUX, badgeAnnonce, paiement, prixCourt } from '../../outils/annonces'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBadge from '../ui/AppBadge.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppFenetre from '../ui/AppFenetre.vue'

const props = defineProps<{ annonce: AnnonceVisible }>()
const emit = defineEmits<{ maj: [annonce: AnnonceVisible] }>()
const routeur = useRouter()
const { afficherMessage } = useMessage()
const fenetreRetrait = ref(false)
const erreur = ref('')

const messages = { pause: 'Annonce mise en pause.', retirer: 'Annonce retirée.', republier: 'Annonce republiée.' }
async function statut(action: 'pause' | 'retirer' | 'republier') {
  erreur.value = ''
  try {
    emit('maj', await appelerServeur<AnnonceVisible>(`/api/moi/annonces/${props.annonce.id}/statut`, { action }))
    fenetreRetrait.value = false
    afficherMessage(messages[action])
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
</script>

<template>
  <div class="grid grid-cols-[72px_1fr] items-start gap-3.5 py-3.5">
    <img
      v-if="annonce.nombre_photos"
      :src="`/api/annonces/${annonce.id}/photos/1`"
      :alt="`Photo de « ${annonce.titre} »`"
      class="size-[72px] rounded-rafals object-cover"
    />
    <div v-else class="grid size-[72px] place-items-center rounded-rafals bg-primaire-doux text-center text-xs font-semibold text-primaire">
      sans<br />photo
    </div>
    <div class="flex flex-col gap-1.5">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <h3 class="text-[17px] font-bold">{{ annonce.titre }}</h3>
        <AppBadge :etat="badgeAnnonce(annonce.statut).etat">{{ badgeAnnonce(annonce.statut).texte }}</AppBadge>
      </div>
      <p class="text-[13.5px] text-texte-doux">
        <span class="font-bold text-primaire">{{ prixCourt(annonce) }}</span> · {{ annonce.metier.nom }} ·
        {{ LIEUX[annonce.lieu].toLowerCase() }} · {{ paiement(annonce.modes_de_paiement).toLowerCase() }}
      </p>
      <p v-if="annonce.raison_cachee && annonce.statut === 'en_ligne'" class="text-[13.5px] text-attente">
        Cachée aux clients : {{ annonce.raison_cachee }}
      </p>
      <p v-else-if="annonce.metier_arrete" class="text-[13.5px] text-texte-doux">
        Cachée : vous avez arrêté le métier {{ annonce.metier.nom }}.
      </p>
      <AppAlerte v-if="annonce.retiree_par_administrateur">Retirée par l'administrateur de rafals : elle ne peut pas être remise en ligne.</AppAlerte>
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <div class="flex flex-wrap items-center gap-2 pt-1">
        <AppBouton variante="secondaire" @click="routeur.push(`/mes-annonces/${annonce.id}`)">Modifier</AppBouton>
        <template v-if="annonce.statut === 'en_ligne'">
          <AppBouton variante="secondaire" @click="routeur.push(`/annonces/${annonce.id}`)">Voir comme un client</AppBouton>
          <AppBouton variante="secondaire" @click="statut('pause')">Mettre en pause</AppBouton>
        </template>
        <!-- Retirée par l'administrateur : jamais republiable par le prestataire (bouton visible, verrouillé) -->
        <AppBouton
          v-else-if="annonce.retiree_par_administrateur"
          variante="verrouille"
          raison-verrou="Cette annonce a été retirée par l'administrateur de rafals : vous ne pouvez pas la remettre en ligne."
        >
          Republier
        </AppBouton>
        <!-- Métier arrêté : republier est refusé tant qu'il n'est pas repris (bouton visible, verrouillé) -->
        <AppBouton
          v-else-if="annonce.metier_arrete"
          variante="verrouille"
          :raison-verrou="`Reprenez d'abord le métier ${annonce.metier.nom} (page « Mon profil »), puis republiez.`"
        >
          Republier
        </AppBouton>
        <AppBouton v-else variante="secondaire" @click="statut('republier')">Republier</AppBouton>
        <AppBouton v-if="annonce.statut !== 'retiree'" variante="danger" class="ml-auto" @click="fenetreRetrait = true">
          Retirer…
        </AppBouton>
      </div>
    </div>
  </div>

  <AppFenetre :ouverte="fenetreRetrait" :titre="`Retirer « ${annonce.titre} » ?`" @fermer="fenetreRetrait = false">
    Elle ne sera plus proposée aux clients et passera dans « Annonces retirées ». Vous pourrez la republier plus tard.
    Les rendez-vous déjà pris restent.
    <template #pied>
      <AppBouton variante="danger" @click="statut('retirer')">Retirer</AppBouton>
      <AppBouton variante="secondaire" @click="fenetreRetrait = false">Annuler</AppBouton>
    </template>
  </AppFenetre>
</template>
