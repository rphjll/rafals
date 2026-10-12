<script setup lang="ts">
// Fiche « Mon activité » du prestataire (.doc/ihm/RM-PROPOSER-IHM.md) : profil, photo, métiers (dates de fin),
// pause / reprise, arrêt. (L'adresse du local est la carte « Mon adresse » de la page, depuis le 07/10/2026.)
import { computed, ref } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { type ProfilPrestataire, badgeSiret, badgeStatut, siretLisible } from '../../outils/prestataires'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBadge from '../ui/AppBadge.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppFenetre from '../ui/AppFenetre.vue'
import AppSection from '../ui/AppSection.vue'
import AvatarPrestataire from './AvatarPrestataire.vue'
import CarteMetiers from './CarteMetiers.vue'
import CartePaiementCarte from './CartePaiementCarte.vue'
import CartePhotosTravail from './CartePhotosTravail.vue'
import CarteTva from './CarteTva.vue'

const props = defineProps<{ profil: ProfilPrestataire }>()
const emit = defineEmits<{ maj: [profil: ProfilPrestataire]; modifier: [] }>()
const { afficherMessage } = useMessage()

const bloque = computed(() => props.profil.statut === 'bloque')
const raisonBlocage = "Votre profil est bloqué par l'administrateur de rafals : contactez-le."
const versionPhoto = ref(Date.now()) // change après un envoi, pour afficher la nouvelle photo

// ---------- Photo ----------
const champPhoto = ref<HTMLInputElement | null>(null)
async function envoyerPhoto(evenement: Event) {
  const fichier = (evenement.target as HTMLInputElement).files?.[0]
  if (!fichier) return
  const formulaire = new FormData()
  formulaire.append('fichier', fichier)
  try {
    emit('maj', await appelerServeur<ProfilPrestataire>('/api/moi/prestataire/photo', formulaire))
    versionPhoto.value = Date.now()
    afficherMessage('Photo enregistrée.')
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  } finally {
    if (champPhoto.value) champPhoto.value.value = ''
  }
}

// ---------- Pause, reprise, arrêt ----------
const messages = {
  pause: "Profil en pause : vous n'apparaissez plus dans les recherches.",
  reprendre: 'Profil de nouveau actif.',
  arreter: 'Votre activité est arrêtée.',
}
const fenetreArret = ref(false)
async function statut(action: 'pause' | 'reprendre' | 'arreter') {
  try {
    emit('maj', await appelerServeur<ProfilPrestataire>('/api/moi/prestataire/statut', { action }))
    fenetreArret.value = false
    afficherMessage(messages[action])
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}
</script>

<template>
  <div class="flex flex-col gap-4">
    <AppAlerte v-if="bloque">{{ raisonBlocage }}</AppAlerte>
    <AppAlerte v-else-if="profil.statut === 'en_pause'" etat="attente">
      Votre profil est en pause : vous n'apparaissez plus dans les recherches. Vos rendez-vous déjà pris restent.
    </AppAlerte>
    <AppAlerte v-else-if="profil.statut === 'arrete'" etat="attente">
      Votre activité est arrêtée : ce profil n'est plus visible ni modifiable.
    </AppAlerte>

    <section class="grid items-start gap-4 carte p-5 sm:grid-cols-[96px_1fr]">
      <AvatarPrestataire
        :id="profil.id"
        :nom="profil.nom_affiche"
        :a-une-photo="profil.a_une_photo"
        taille="grande"
        :version="versionPhoto"
      />

      <div class="flex flex-col gap-2.5">
        <div class="flex flex-wrap items-center gap-2">
          <h2 class="text-xl font-bold">{{ profil.nom_affiche }}</h2>
          <AppBadge :etat="badgeStatut(profil.statut).etat">{{ badgeStatut(profil.statut).texte }}</AppBadge>
        </div>
        <dl class="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1.5 text-[14.5px]">
          <dt class="text-texte-doux">Métier</dt>
          <dd class="font-medium">
            {{ profil.metier_principal.nom }}
            <template v-if="profil.metiers_secondaires.length">
              · aussi {{ profil.metiers_secondaires.map((m) => m.nom).join(', ') }}
            </template>
          </dd>
          <dt class="text-texte-doux">Zone</dt>
          <dd class="font-medium">
            {{ profil.commune.nom }} ({{ profil.commune.codes_postaux[0] }}), jusqu'à {{ profil.distance_km }} km
          </dd>
          <dt class="text-texte-doux">SIRET</dt>
          <dd class="flex flex-wrap items-center gap-2 font-medium">
            <AppBadge :etat="badgeSiret(profil.siret_statut).etat">{{ badgeSiret(profil.siret_statut).texte }}</AppBadge>
            {{ siretLisible(profil.siret) }}
            <span v-if="profil.siret_statut !== 'verifie'" class="text-[13px] font-normal text-texte-doux">
              espèces seulement<template v-if="profil.siret_statut === 'a_verifier'"> (nouvel essai automatique auprès de l'État)</template>
            </span>
          </dd>
          <template v-if="profil.presentation">
            <dt class="text-texte-doux">Présentation</dt>
            <dd class="font-medium whitespace-pre-line">{{ profil.presentation }}</dd>
          </template>
        </dl>
        <div v-if="profil.statut !== 'arrete'" class="flex flex-wrap gap-2">
          <AppBouton variante="secondaire" @click="emit('modifier')">Modifier mon profil</AppBouton>
          <AppBouton variante="secondaire" @click="champPhoto?.click()">Changer ma photo</AppBouton>
          <input ref="champPhoto" type="file" accept="image/jpeg,image/png" class="sr-only" @change="envoyerPhoto" />
        </div>
      </div>
    </section>

    <template v-if="profil.statut !== 'arrete'">
      <CartePhotosTravail :profil="profil" @maj="(p) => emit('maj', p)" />
      <CartePaiementCarte />
      <CarteTva :facture-tva="profil.facture_tva" @maj="(v) => emit('maj', { ...profil, facture_tva: v })" />
      <CarteMetiers :profil="profil" @maj="(p) => emit('maj', p)" />
    </template>

    <AppSection v-if="profil.statut !== 'arrete'" titre="Visibilité">
      <p class="text-[14.5px] text-texte-doux">
        Vous apparaissez dans les recherches tant que votre activité est active.
      </p>
      <div class="flex flex-wrap gap-2 pt-8 sm:pt-0">
        <AppBouton v-if="bloque" variante="verrouille" :raison-verrou="raisonBlocage">Mettre en pause</AppBouton>
        <AppBouton v-else-if="profil.statut === 'en_pause'" @click="statut('reprendre')">Reprendre mon activité</AppBouton>
        <AppBouton v-else variante="secondaire" @click="statut('pause')">Mettre en pause</AppBouton>
        <AppBouton v-if="bloque" variante="verrouille" :raison-verrou="raisonBlocage">Arrêter mon activité…</AppBouton>
        <AppBouton v-else variante="danger" @click="fenetreArret = true">Arrêter mon activité…</AppBouton>
      </div>
    </AppSection>

    <AppFenetre :ouverte="fenetreArret" titre="Arrêter votre activité ?" @fermer="fenetreArret = false">
      C'est définitif : votre profil ne sera plus visible ni modifiable. Vos factures restent consultables. Pour une
      absence, choisissez plutôt « Mettre en pause ».
      <template #pied>
        <AppBouton variante="danger" @click="statut('arreter')">Arrêter définitivement</AppBouton>
        <AppBouton variante="secondaire" @click="fenetreArret = false">Annuler</AppBouton>
      </template>
    </AppFenetre>
  </div>
</template>
