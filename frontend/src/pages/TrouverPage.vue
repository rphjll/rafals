<script setup lang="ts">
// Trouver un prestataire (.doc/ihm/RM-TROUVER-IHM.md ; RM-RECHERCHE.md) : la recherche en haut, puis
// - sans ville : on la demande d'abord ;
// - avec la ville seule (/trouver?ville=12768) : une rubrique par service, ses prestataires en rangée ;
// - avec un métier et la ville (/trouver?metier=3&ville=12768) : les prestataires de ce métier, tri et filtres.
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import dessinQuartier from '../assets/quartier.svg'
import AppChoixCommune from '../components/AppChoixCommune.vue'
import AppChoixMetier from '../components/AppChoixMetier.vue'
import ResultatsRecherche from '../components/recherche/ResultatsRecherche.vue'
import RubriquesPrestataires from '../components/recherche/RubriquesPrestataires.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppSection from '../components/ui/AppSection.vue'
import type { MetierVisible } from '../composables/useMetiers'
import type { CommuneVisible } from '../outils/prestataires'
import { type PageResultats, type PageRubriques, retenirVille, villeRetenue } from '../outils/recherche'

const route = useRoute()
const routeur = useRouter()

const metier = ref<MetierVisible | null>(null)
const commune = ref<CommuneVisible | null>(null)
const erreur = ref('')

// Tout est dans l'adresse : un lien partagé montre la même chose, et le bouton « retour » revient en arrière
const enRecherche = computed(() => !!route.query.metier && !!route.query.ville)
const parService = computed(() => !route.query.metier && !!route.query.ville)
const villeConnue = computed(() => enRecherche.value || parService.value)

// Ville déjà donnée lors d'une visite précédente : les rubriques s'affichent sans la redemander
onMounted(() => {
  const ville = villeRetenue()
  if (!ville) return
  commune.value = ville
  if (!route.query.ville) routeur.replace({ query: { ville: String(ville.id) } })
})

function chercher() {
  erreur.value = ''
  if (!commune.value) {
    erreur.value = 'Indiquez votre ville.'
    return
  }
  retenirVille(commune.value)
  if (!metier.value) return routeur.push({ query: { ville: String(commune.value.id) } })
  // Les filtres déjà choisis sont gardés ; on revient à la page 1
  const { page: _page, dossier: _dossier, ...reste } = route.query
  routeur.push({ query: { ...reste, metier: String(metier.value.id), ville: String(commune.value.id) } })
}

// Lien ouvert directement, ou métier voisin choisi : on remet le métier et la ville dans les choix du haut
function resultatsCharges(page: PageResultats) {
  if (metier.value?.id !== page.metier.id) metier.value = { ...page.metier, code: '', categorie: '' }
  if (commune.value?.id !== page.ville.id) commune.value = page.ville
}
function rubriquesChargees(page: PageRubriques) {
  metier.value = null
  if (commune.value?.id !== page.ville.id) commune.value = page.ville
}
</script>

<template>
  <div class="flex flex-col gap-10">
    <!-- Dès que la ville est connue, le haut se réduit à la carte de recherche pour laisser la place aux prestataires -->
    <section class="grid items-center gap-6" :class="villeConnue ? '' : 'md:grid-cols-[1.1fr_0.9fr]'">
      <div class="flex min-w-0 flex-col gap-5">
        <template v-if="!villeConnue">
          <h1 class="text-[clamp(32px,5.4vw,56px)] leading-[1.05] font-black">
            Le bon prestataire, <span class="text-primaire">près de chez vous.</span>
          </h1>
          <p class="max-w-[46ch] text-[18px] text-texte-doux">
            Ménage, jardinage, plomberie, coiffure à domicile : indiquez votre ville pour voir les prestataires proches et
            leurs avis.
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
      <img v-if="!villeConnue" :src="dessinQuartier" alt="" class="hidden w-full max-w-[440px] justify-self-center md:block" />
    </section>

    <template v-if="enRecherche">
      <div>
        <AppBouton variante="secondaire" @click="routeur.push({ query: { ville: String(route.query.ville) } })">← Tous les services</AppBouton>
      </div>
      <ResultatsRecherche @charge="resultatsCharges" />
    </template>
    <RubriquesPrestataires v-else-if="parService" @charge="rubriquesChargees" />
    <AppSection v-else>
      <h2 class="text-xl font-bold">Indiquez votre ville pour voir les prestataires près de chez vous.</h2>
      <p class="text-texte-doux">
        Tapez son nom ou son code postal dans « Où ? », puis [Rechercher]. Le service est facultatif : sans lui, vous voyez tous
        les services, rangés par rubrique.
      </p>
    </AppSection>
  </div>
</template>
