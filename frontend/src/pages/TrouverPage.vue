<script setup lang="ts">
// Trouver un prestataire (.doc/ihm/RM-TROUVER-IHM.md ; RM-RECHERCHE.md) : recherche métier + ville, dossiers de
// métiers en tuiles de couleur, puis les prestataires trouvés à la place des tuiles.
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppChoixCommune from '../components/AppChoixCommune.vue'
import AppChoixMetier from '../components/AppChoixMetier.vue'
import ResultatsRecherche from '../components/recherche/ResultatsRecherche.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import { useMessage } from '../composables/useMessage'
import { type Dossier, type MetierVisible, useMetiers } from '../composables/useMetiers'
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

// Une couleur par tuile, dans l'ordre, puis on recommence (noms écrits en entier pour Tailwind)
const TEINTES = [
  'bg-teinte-orange text-teinte-orange-texte',
  'bg-teinte-vert text-teinte-vert-texte',
  'bg-teinte-jaune text-teinte-jaune-texte',
  'bg-teinte-bleu text-teinte-bleu-texte',
  'bg-teinte-rose text-teinte-rose-texte',
  'bg-teinte-violet text-teinte-violet-texte',
]

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
    <!-- Pendant une recherche, le bandeau se réduit à la carte de recherche pour laisser la place aux résultats -->
    <section
      class="flex flex-col gap-6 rounded-rafals bg-fonce px-4 text-sur-fonce"
      :class="enRecherche ? 'py-4' : 'py-8 md:px-12 md:py-14'"
    >
      <template v-if="!enRecherche">
        <h1 class="max-w-[16ch] text-[clamp(32px,6vw,54px)] leading-[1.05] font-bold">
          Le bon prestataire, <span class="text-fonce-vif">près de chez vous.</span>
        </h1>
        <p class="max-w-[50ch] text-[17px] text-sur-fonce-doux">
          Ménage, jardinage, plomberie, coiffure à domicile : indiquez un service et votre ville pour voir les prestataires
          proches et leurs avis.
        </p>
      </template>
      <!-- Les deux champs s'alignent par le haut ; le bouton descend de la hauteur d'une étiquette -->
      <form
        class="grid items-start gap-3 rounded-rafals bg-surface p-4 text-texte md:grid-cols-[1fr_1fr_auto]"
        @submit.prevent="chercher"
      >
        <AppChoixMetier v-model="metier" :avec-dossiers="false" etiquette="Quel service ?" />
        <AppChoixCommune v-model="commune" etiquette="Où ?" />
        <div class="md:pt-6"><AppBouton type="submit" variante="accent" pleine-largeur>Rechercher</AppBouton></div>
        <AppAlerte v-if="erreur" class="md:col-span-3">{{ erreur }}</AppAlerte>
      </form>
    </section>

    <template v-if="enRecherche">
      <div><AppBouton variante="secondaire" @click="routeur.push('/trouver')">← Tous les métiers</AppBouton></div>
      <ResultatsRecherche @charge="resultatsCharges" />
    </template>

    <section v-else-if="dossiers.length" class="flex flex-col gap-4">
      <h2 class="text-[26px] font-bold">De quoi avez-vous besoin ?</h2>
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
      <div v-else class="grid grid-cols-[repeat(auto-fill,minmax(210px,1fr))] gap-3">
        <button
          v-for="(dossier, rang) in dossiers"
          :key="dossier.id"
          type="button"
          class="flex min-h-[104px] flex-col justify-between gap-2 rounded-rafals p-4 text-left hover:brightness-95"
          :class="TEINTES[rang % TEINTES.length]"
          @click="dossierOuvert = dossier"
        >
          <b class="font-titre text-lg leading-tight">{{ dossier.nom }}</b>
          <small class="text-[13px]">{{ dossier.metiers.slice(0, 3).map((m) => m.nom).join(', ') }}…</small>
        </button>
      </div>
    </section>
  </div>
</template>
