<script setup lang="ts">
// « Mon profil » du prestataire, façon Instagram (.doc/ihm/RM-PROFIL-IHM.md, 21/10/2026) : photo et chiffres en haut,
// métiers en bulles, puis 3 onglets : Photos (grille), Mon activité (cartes en lignes qui se déplient), Mon compte
// (slot « compte », rempli par ProfilPage). Pause / reprise, arrêt. (L'adresse du local est dans « Mon adresse ».)
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { teinte } from '../../outils/pictos'
import { type ProfilPrestataire, badgeSiret, badgeStatut, siretLisible } from '../../outils/prestataires'
import { chiffre, chiffreNote, chiffreOuTiret, compterAbonnements } from '../../outils/profil'
import EnteteProfil from '../profil/EnteteProfil.vue'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBadge from '../ui/AppBadge.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppFenetre from '../ui/AppFenetre.vue'
import AppListeLignes from '../ui/AppListeLignes.vue'
import AppOnglets from '../ui/AppOnglets.vue'
import AppSection from '../ui/AppSection.vue'
import AvatarPrestataire from './AvatarPrestataire.vue'
import CarteMetiers from './CarteMetiers.vue'
import CarteParticulier from './CarteParticulier.vue'
import CartePaiementCarte from './CartePaiementCarte.vue'
import CartePhotosTravail from './CartePhotosTravail.vue'
import CarteTva from './CarteTva.vue'
import FenetreAjoutMetier from './FenetreAjoutMetier.vue'

const props = defineProps<{ profil: ProfilPrestataire }>()
const emit = defineEmits<{ maj: [profil: ProfilPrestataire]; modifier: [] }>()
const { afficherMessage } = useMessage()
const routeur = useRouter()

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

// ---------- Chiffres du haut : photos, note, abonnés, abonnements ----------
const publics = ref<{ note: number | null; nombre_avis: number; abonnes: number } | null>(null)
const abonnements = ref<number | null>(null)
onMounted(async () => {
  abonnements.value = await compterAbonnements()
  try {
    publics.value = await appelerServeur(`/api/prestataires/${props.profil.id}`)
  } catch {
    publics.value = null // profil en pause ou arrêté : sa page publique n'est pas lisible, les chiffres restent « — »
  }
})
const chiffres = computed(() => [
  chiffre(props.profil.photos.length, 'photo'),
  publics.value ? chiffreNote(publics.value.note, publics.value.nombre_avis) : { valeur: '—', texte: 'avis' },
  chiffreOuTiret(publics.value?.abonnes ?? null, 'abonné'),
  chiffreOuTiret(abonnements.value, 'abonnement'),
])

// ---------- Onglets et bulles des métiers ----------
const ICONES = {
  photos: 'M4 4h6.5v6.5H4zM13.5 4H20v6.5h-6.5zM4 13.5h6.5V20H4zM13.5 13.5H20V20h-6.5z',
  activite: 'M14.7 6.3a4 4 0 00-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 005.4-5.4l-2.5 2.5-2.4-.6-.6-2.4z',
  compte: 'M12 12a4 4 0 100-8 4 4 0 000 8zM4 21c1.5-4 4.5-6 8-6s6.5 2 8 6',
}
const onglets = computed(() =>
  props.profil.statut === 'arrete'
    ? [{ id: 'compte', texte: 'Mon compte', icone: ICONES.compte }]
    : [
        { id: 'photos', texte: 'Photos', icone: ICONES.photos },
        { id: 'activite', texte: 'Mon activité', icone: ICONES.activite },
        { id: 'compte', texte: 'Mon compte', icone: ICONES.compte },
      ],
)
const onglet = ref('photos')
const metiers = computed(() => [
  { ...props.profil.metier_principal, principal: true },
  ...props.profil.metiers_secondaires.map((m) => ({ ...m, principal: false })),
])
const lignesActivite = ref<InstanceType<typeof AppListeLignes> | null>(null)
const fenetreAjout = ref(false) // la bulle « + Ajouter » ouvre la fenêtre « Ajouter un métier »
/** Une bulle de métier ouvre la ligne « Mes métiers » de l'onglet « Mon activité » */
async function ouvrirMetiers() {
  await routeur.replace({ query: { onglet: 'activite' } })
  await nextTick()
  lignesActivite.value?.ouvrir('Mes métiers')
}
const resumes = computed(() => ({
  'Sans SIRET : vos limites': 'Petits services payés en espèces, 100 € au plus par proposition',
  'Mes métiers': [`${props.profil.metier_principal.nom} (principal)`, ...props.profil.metiers_secondaires.map((m) => m.nom)].join(' · '),
  Visibilité:
    props.profil.statut === 'en_pause'
      ? "En pause : vous n'apparaissez plus dans les recherches"
      : props.profil.statut === 'bloque'
        ? "Bloqué par l'administrateur"
        : 'Actif : vous apparaissez dans les recherches',
}))
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

    <section class="carte overflow-hidden">
      <EnteteProfil :nom="profil.nom_affiche" :chiffres="chiffres">
        <template #photo>
          <AvatarPrestataire
            :id="profil.id"
            :nom="profil.nom_affiche"
            :a-une-photo="profil.a_une_photo"
            taille="grande"
            :version="versionPhoto"
          />
        </template>
        <template #badges>
          <AppBadge :etat="badgeStatut(profil.statut).etat">{{ badgeStatut(profil.statut).texte }}</AppBadge>
          <AppBadge :etat="badgeSiret(profil.siret_statut).etat">{{ badgeSiret(profil.siret_statut).texte }}</AppBadge>
        </template>
        <p>
          <span class="font-extrabold text-primaire">{{ profil.metier_principal.nom }}</span>
          <span v-if="profil.metiers_secondaires.length" class="text-texte-doux">
            · aussi {{ profil.metiers_secondaires.map((m) => m.nom).join(', ') }}
          </span>
        </p>
        <p v-if="profil.presentation" class="whitespace-pre-line">{{ profil.presentation }}</p>
        <p class="text-[14px] text-texte-doux">
          📍 {{ profil.commune.nom }} ({{ profil.commune.codes_postaux[0] }}) · jusqu'à {{ profil.distance_km }} km
        </p>
        <p class="text-[13px] text-texte-doux">
          SIRET {{ siretLisible(profil.siret) }}
          <template v-if="profil.siret_statut !== 'verifie'">
            · espèces seulement<template v-if="profil.siret_statut === 'a_verifier'"> (nouvel essai automatique auprès de l'État)</template>
          </template>
        </p>
        <template v-if="profil.statut !== 'arrete'" #boutons>
          <AppBouton @click="emit('modifier')">Modifier mon profil</AppBouton>
          <AppBouton variante="secondaire" @click="champPhoto?.click()">Changer ma photo</AppBouton>
          <AppBouton variante="secondaire" @click="routeur.push('/mon-activite')">Mon activité</AppBouton>
        </template>
      </EnteteProfil>
      <input ref="champPhoto" type="file" accept="image/jpeg,image/png" class="sr-only" @change="envoyerPhoto" />

      <!-- Les métiers en bulles rondes, comme les « stories à la une » -->
      <div v-if="profil.statut !== 'arrete'" class="flex gap-4 overflow-x-auto px-5 pt-4 pb-5 max-sm:px-4">
        <button
          v-for="(m, rang) in metiers"
          :key="m.id"
          type="button"
          class="flex w-[76px] shrink-0 flex-col items-center gap-1.5"
          @click="ouvrirMetiers"
        >
          <span class="grid size-[66px] place-items-center rounded-full border-2 p-[3px]" :class="m.principal ? 'border-primaire' : 'border-bord'">
            <span class="grid size-full place-items-center rounded-full text-2xl font-black" :class="teinte(rang + 3)">{{ m.nom[0] }}</span>
          </span>
          <span class="text-center text-[12px] leading-tight font-bold">
            {{ m.nom }}
            <span v-if="m.principal" class="block text-[11px] font-semibold text-texte-doux">principal</span>
          </span>
        </button>
        <button type="button" class="flex w-[76px] shrink-0 flex-col items-center gap-1.5" @click="fenetreAjout = true">
          <span class="grid size-[66px] place-items-center rounded-full border-2 border-dashed border-bord text-[26px] text-texte-doux">+</span>
          <span class="text-[12px] font-bold">Ajouter</span>
        </button>
      </div>

      <AppOnglets v-model="onglet" :onglets="onglets" egaux />

      <div v-if="profil.statut !== 'arrete'" v-show="onglet === 'photos'">
        <CartePhotosTravail :profil="profil" @maj="(p) => emit('maj', p)" />
      </div>
      <AppListeLignes v-if="profil.statut !== 'arrete'" v-show="onglet === 'activite'" ref="lignesActivite" :resumes="resumes">
        <!-- Sans SIRET vérifié : ses limites et la case à cocher (la ligne se cache toute seule avec un SIRET) -->
        <CarteParticulier :key="profil.siret_statut" />
        <CartePaiementCarte />
        <CarteMetiers :profil="profil" @maj="(p) => emit('maj', p)" />
        <CarteTva :facture-tva="profil.facture_tva" @maj="(v) => emit('maj', { ...profil, facture_tva: v })" />
        <AppSection titre="Visibilité">
          <p class="text-[14.5px] text-texte-doux">
            Vous apparaissez dans les recherches tant que votre activité est active.
          </p>
          <div class="flex flex-wrap gap-2">
            <AppBouton v-if="bloque" variante="verrouille" :raison-verrou="raisonBlocage">Mettre en pause</AppBouton>
            <AppBouton v-else-if="profil.statut === 'en_pause'" @click="statut('reprendre')">Reprendre mon activité</AppBouton>
            <AppBouton v-else variante="secondaire" @click="statut('pause')">Mettre en pause</AppBouton>
            <AppBouton v-if="bloque" variante="verrouille" :raison-verrou="raisonBlocage">Arrêter mon activité…</AppBouton>
            <AppBouton v-else variante="danger" @click="fenetreArret = true">Arrêter mon activité…</AppBouton>
          </div>
        </AppSection>
      </AppListeLignes>
      <div v-show="onglet === 'compte'">
        <slot name="compte" />
      </div>
    </section>

    <FenetreAjoutMetier :ouverte="fenetreAjout" :profil="profil" @maj="(p) => emit('maj', p)" @fermer="fenetreAjout = false" />
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
