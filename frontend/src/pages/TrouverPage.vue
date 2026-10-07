<script setup lang="ts">
// Trouver un prestataire (.doc/ihm/RM-TROUVER-IHM.md ; RM-RECHERCHE.md) : recherche métier + ville, dossiers de
// métiers en tuiles (bulle de couleur + pictogramme), puis les prestataires trouvés à la place des tuiles.
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import dessinQuartier from '../assets/quartier.svg'
import AppChoixCommune from '../components/AppChoixCommune.vue'
import AppChoixMetier from '../components/AppChoixMetier.vue'
import ResultatsRecherche from '../components/recherche/ResultatsRecherche.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppPicto from '../components/ui/AppPicto.vue'
import { useMessage } from '../composables/useMessage'
import { type Dossier, type MetierVisible, useMetiers } from '../composables/useMetiers'
import { teinte } from '../outils/pictos'
import type { CommuneVisible } from '../outils/prestataires'
import type { PageResultats } from '../outils/recherche'

const route = useRoute()
const routeur = useRouter()
const { afficherMessage } = useMessage()
const { dossiers, chargerDossiers } = useMetiers()

const metier = ref<MetierVisible | null>(null)
const commune = ref<CommuneVisible | null>(null)
const erreur = ref('')
const dossierOuvert = ref<Dossier | null>(null)

onMounted(() => {
  chargerDossiers().catch(() => {}) // sans les dossiers, la recherche du haut suffit
})

// La recherche reste sur cette page : le métier et la ville vont dans l'adresse (/trouver?metier=3&ville=12768),
// et les prestataires trouvés remplacent les tuiles.
const enRecherche = computed(() => !!route.query.metier && !!route.query.ville)

function chercher() {
  erreur.value = ''
  if (!metier.value || !commune.value) {
    erreur.value = !metier.value ? 'Choisissez un métier.' : 'Choisissez votre ville.'
    return
  }
  // Les filtres déjà choisis sont gardés ; on revient à la page 1
  const { page: _page, ...reste } = route.query
  routeur.push({ query: { ...reste, metier: String(metier.value.id), ville: String(commune.value.id) } })
}

// Lien ouvert directement, ou métier voisin choisi : on remet le métier et la ville dans les choix du haut
function resultatsCharges(page: PageResultats) {
  if (metier.value?.id !== page.metier.id) metier.value = { ...page.metier, code: '', categorie: '' }
  if (commune.value?.id !== page.ville.id) commune.value = page.ville
}

// Métier choisi dans une tuile : la recherche part si la ville est connue, sinon on remonte la demander
function choisirMetier(choix: MetierVisible) {
  metier.value = choix
  dossierOuvert.value = null
  if (commune.value) return chercher()
  erreur.value = ''
  window.scrollTo({ top: 0, behavior: 'smooth' })
  afficherMessage(`« ${choix.nom} » choisi : indiquez votre ville.`)
}
</script>

<template>
  <div class="flex flex-col gap-10">
    <!-- Pendant une recherche, le haut se réduit à la carte de recherche pour laisser la place aux résultats -->
    <section class="grid items-center gap-6" :class="enRecherche ? '' : 'md:grid-cols-[1.1fr_0.9fr]'">
      <div class="flex min-w-0 flex-col gap-5">
        <template v-if="!enRecherche">
          <h1 class="text-[clamp(32px,5.4vw,56px)] leading-[1.05] font-black">
            Le bon prestataire, <span class="text-primaire">près de chez vous.</span>
          </h1>
          <p class="max-w-[46ch] text-[18px] text-texte-doux">
            Ménage, jardinage, plomberie, coiffure à domicile : indiquez un service et votre ville pour voir les prestataires
            proches et leurs avis.
          </p>
        </template>
        <!-- Les deux champs s'alignent par le haut ; le bouton descend de la hauteur d'une étiquette -->
        <form class="carte grid items-start gap-3 p-4 md:grid-cols-[1fr_1fr_auto]" @submit.prevent="chercher">
          <AppChoixMetier v-model="metier" :avec-dossiers="false" etiquette="Quel service ?" />
          <AppChoixCommune v-model="commune" etiquette="Où ?" />
          <div class="md:pt-6"><AppBouton type="submit" variante="accent" pleine-largeur>Rechercher</AppBouton></div>
          <AppAlerte v-if="erreur" class="md:col-span-3">{{ erreur }}</AppAlerte>
        </form>
      </div>
      <img v-if="!enRecherche" :src="dessinQuartier" alt="" class="hidden w-full max-w-[440px] justify-self-center md:block" />
    </section>

    <template v-if="enRecherche">
      <div><AppBouton variante="secondaire" @click="routeur.push('/trouver')">← Tous les métiers</AppBouton></div>
      <ResultatsRecherche @charge="resultatsCharges" />
    </template>

    <section v-else-if="dossiers.length" class="flex flex-col gap-4">
      <h2 class="text-[26px] font-extrabold">De quoi avez-vous besoin ?</h2>
      <template v-if="dossierOuvert">
        <div class="flex flex-wrap items-center gap-2.5">
          <AppBouton variante="secondaire" @click="dossierOuvert = null">← Tous les dossiers</AppBouton>
          <h3 class="text-lg font-bold">{{ dossierOuvert.nom }}</h3>
        </div>
        <div class="flex flex-wrap gap-2">
          <AppBouton v-for="choix in dossierOuvert.metiers" :key="choix.id" variante="secondaire" @click="choisirMetier(choix)">
            {{ choix.nom }}
          </AppBouton>
        </div>
      </template>
      <div v-else class="grid grid-cols-[repeat(auto-fill,minmax(230px,1fr))] gap-4">
        <button
          v-for="(dossier, rang) in dossiers"
          :key="dossier.id"
          type="button"
          class="carte flex items-center gap-3.5 p-4 text-left hover:ring-2 hover:ring-primaire"
          @click="dossierOuvert = dossier"
        >
          <span class="grid size-[58px] shrink-0 place-items-center rounded-full" :class="teinte(rang)"><AppPicto :code="dossier.code" :taille="26" /></span>
          <span class="flex min-w-0 flex-col">
            <b class="text-[17px] leading-tight">{{ dossier.nom }}</b>
            <small class="text-[13px] text-texte-doux">{{ dossier.metiers.slice(0, 3).map((m) => m.nom).join(', ') }}…</small>
          </span>
        </button>
      </div>
    </section>
  </div>
</template>
