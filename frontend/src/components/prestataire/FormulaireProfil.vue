<script setup lang="ts">
// Formulaire du profil prestataire, pour le créer ou le modifier (.doc/ihm/RM-PROPOSER-IHM.md).
// Règles : RM-PRESTATAIRES.md (100 km, 5 métiers secondaires, 80 / 1 000 caractères, SIRET).
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { appelerServeur, messageErreur } from '../../api'
import type { MetierVisible } from '../../composables/useMetiers'
import { useMetiers } from '../../composables/useMetiers'
import { type CommuneVisible, LIEUX_SERVICE, type LieuService, type ProfilPrestataire, siretLisible } from '../../outils/prestataires'
import AppChoixCommune from '../AppChoixCommune.vue'
import AppChoixMetier from '../AppChoixMetier.vue'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppChamp from '../ui/AppChamp.vue'
import AppChoix from '../ui/AppChoix.vue'
import AppRecherche from '../ui/AppRecherche.vue'
import AppZoneTexte from '../ui/AppZoneTexte.vue'
import AppSection from '../ui/AppSection.vue'

const SECONDAIRES_MAX = 5
const PRESENTATION_MAX = 1000

const props = defineProps<{ existant?: ProfilPrestataire | null }>()
const emit = defineEmits<{ enregistre: [profil: ProfilPrestataire]; annuler: [] }>()
const { rechercher } = useMetiers()
const route = useRoute()

// Préremplissage à partir du profil existant (modification)
const e = props.existant
const nomAffiche = ref(e?.nom_affiche ?? '')
const principal = ref<MetierVisible | null>(e ? { ...e.metier_principal, code: '', categorie: '' } : null)
const secondaires = ref<{ id: number; nom: string }[]>(e ? [...e.metiers_secondaires] : [])
const commune = ref<CommuneVisible | null>(e?.commune ?? null)
const distance = ref(String(e?.distance_km ?? 15))
const lieu = ref<LieuService>(e?.lieu ?? 'chez_client')
const presentation = ref(e?.presentation ?? '')
// Création : le SIRET peut arriver de « Créer mon auto-entreprise » (/profil?siret=91234567800017)
const siretAnnonce = typeof route.query.siret === 'string' ? route.query.siret : null
const siret = ref(siretLisible(e ? e.siret : siretAnnonce))
const erreur = ref('')
const envoiEnCours = ref(false)

// Les métiers déjà choisis ne sont plus proposés
const chercherSecondaire = async (texte: string) => {
  const exclus = new Set([principal.value?.id, ...secondaires.value.map((m) => m.id)])
  return (await rechercher(texte)).filter((m) => !exclus.has(m.id))
}
const plein = computed(() => secondaires.value.length >= SECONDAIRES_MAX)

async function enregistrer() {
  erreur.value = ''
  if (!principal.value || !commune.value) {
    erreur.value = !principal.value ? 'Choisissez votre métier principal.' : 'Choisissez votre ville de départ.'
    return
  }
  envoiEnCours.value = true
  try {
    const profil = await appelerServeur<ProfilPrestataire>(e ? '/api/moi/prestataire/modifier' : '/api/moi/prestataire', {
      nom_affiche: nomAffiche.value,
      metier_principal_id: principal.value.id,
      metiers_secondaires: secondaires.value.map((m) => m.id),
      commune_id: commune.value.id,
      distance_km: Number(distance.value),
      lieu: lieu.value,
      presentation: presentation.value,
      siret: siret.value,
    })
    emit('enregistre', profil)
  } catch (err) {
    erreur.value = messageErreur(err)
  } finally {
    envoiEnCours.value = false
  }
}
</script>

<template>
  <form class="flex flex-col gap-4" @submit.prevent="enregistrer">
    <AppSection titre="Votre activité">
      <AppChamp
        v-model="nomAffiche"
        etiquette="Nom affiché"
        obligatoire
        aide="Ce que les clients verront, ex. « Julie Martin — Ménage » ou « Net & Clair »."
      />
      <AppChoixMetier v-model="principal" :avec-dossiers="false" etiquette="Métier principal" obligatoire />
      <div class="flex flex-col gap-2">
        <div v-if="secondaires.length" class="flex flex-wrap gap-2">
          <span
            v-for="metier in secondaires"
            :key="metier.id"
            class="inline-flex items-center gap-2 rounded-full bg-primaire-doux py-1 pr-1.5 pl-3 text-sm font-semibold text-primaire"
          >
            {{ metier.nom }}
            <button
              type="button"
              class="size-6 rounded-full bg-surface font-bold"
              :aria-label="`Retirer ${metier.nom}`"
              @click="secondaires = secondaires.filter((m) => m.id !== metier.id)"
            >
              ×
            </button>
          </span>
        </div>
        <AppRecherche
          v-if="!plein"
          :etiquette="`Métiers secondaires (${SECONDAIRES_MAX} au plus)`"
          :chercher="chercherSecondaire"
          :libelle="(m: MetierVisible) => m.nom"
          :detail="(m: MetierVisible) => m.categorie"
          :cle="(m: MetierVisible) => m.id"
          placeholder="Ajouter un métier : tapez les premières lettres…"
          aide="Vous apparaîtrez aussi dans ces recherches, après les spécialistes."
          @choisir="(m: MetierVisible) => secondaires.push({ id: m.id, nom: m.nom })"
        />
        <p v-else class="text-[13px] text-texte-doux">{{ SECONDAIRES_MAX }} métiers secondaires : c'est le maximum.</p>
      </div>
    </AppSection>

    <AppSection titre="Où intervenez-vous ?">
      <div class="grid gap-3 sm:grid-cols-[2fr_1fr]">
        <AppChoixCommune v-model="commune" etiquette="Ville de départ" obligatoire />
        <AppChamp
          v-model="distance"
          etiquette="Jusqu'à (km)"
          type="number"
          min="1"
          max="100"
          obligatoire
          aide="De 1 à 100 km, à vol d'oiseau."
        />
      </div>
      <AppChoix v-model="lieu" etiquette="Où ont lieu vos services ?" :options="LIEUX_SERVICE" obligatoire />
      <p v-if="lieu !== 'chez_client'" class="text-[13px] text-texte-doux">
        Il faut que « Mon adresse » soit remplie. Votre rue n'est montrée à un client qu'après un rendez-vous.
      </p>
    </AppSection>

    <AppSection titre="Présentation et SIRET">
      <AppZoneTexte v-model="presentation" etiquette="Présentation" :maximum="PRESENTATION_MAX" aide="Facultatif." />
      <AppChamp
        v-model="siret"
        etiquette="SIRET (facultatif)"
        inputmode="numeric"
        placeholder="14 chiffres, ex. 443 061 841 00047"
        aide="Sans SIRET, vos clients ne pourront vous payer qu'en espèces. Avec un SIRET vérifié par l'État, la carte bancaire devient possible."
      />
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <div class="flex flex-wrap gap-2.5">
        <AppBouton type="submit" :occupe="envoiEnCours">{{ e ? 'Enregistrer' : 'Proposer mes services' }}</AppBouton>
        <AppBouton v-if="e" variante="secondaire" @click="emit('annuler')">Annuler</AppBouton>
      </div>
    </AppSection>
  </form>
</template>
