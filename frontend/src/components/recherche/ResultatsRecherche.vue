<script setup lang="ts">
// Résultats d'une recherche, affichés sur l'accueil (.doc/ihm/RM-TROUVER-IHM.md ; RM-RECHERCHE.md) : tri, filtres, pages.
// Toute la recherche est dans l'adresse (?metier=3&ville=12768&tri=distance&carte=1…) : un lien partagé montre
// les mêmes résultats, et le bouton « retour » revient à la recherche précédente.
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../../api'
import { type PageResultats, pluriel } from '../../outils/recherche'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppSection from '../ui/AppSection.vue'
import CarteResultat from './CarteResultat.vue'

// Lien ouvert directement : la page d'accueil remet le métier et la ville dans les choix du haut
const emit = defineEmits<{ charge: [page: PageResultats] }>()

const route = useRoute()
const routeur = useRouter()
const page = ref<PageResultats | null>(null)
const erreur = ref('')
const chargement = ref(false)

// Filtres et tri, lus dans l'adresse
const q = computed(() => route.query)
const tri = computed(() => (q.value.tri === 'distance' ? 'distance' : 'note'))
const filtres = ref({ chezMoi: false, carte: false, libre: false, prixMax: '' })

function lireAdresse() {
  filtres.value = {
    chezMoi: q.value.chez_moi === '1',
    carte: q.value.carte === '1',
    libre: q.value.libre === '1',
    prixMax: typeof q.value.prix_max === 'string' ? q.value.prix_max : '',
  }
}

function aller(changements: Record<string, string | undefined>, garderPage = false) {
  const suite: Record<string, string> = {}
  for (const [cle, valeur] of Object.entries({ ...q.value, ...changements })) {
    if (typeof valeur === 'string' && valeur) suite[cle] = valeur
  }
  if (!garderPage) delete suite.page
  routeur.push({ query: suite })
}

async function charger() {
  lireAdresse()
  if (!q.value.metier || !q.value.ville) {
    page.value = null
    return
  }
  chargement.value = true
  erreur.value = ''
  const parametres = new URLSearchParams({ metier_id: String(q.value.metier), commune_id: String(q.value.ville), tri: tri.value })
  if (q.value.page) parametres.set('page', String(q.value.page))
  if (filtres.value.chezMoi) parametres.set('vient_chez_moi', 'true')
  if (filtres.value.carte) parametres.set('carte_bancaire', 'true')
  if (filtres.value.libre) parametres.set('libre_7_jours', 'true')
  if (filtres.value.prixMax) parametres.set('prix_max', filtres.value.prixMax.replace(',', '.'))
  try {
    page.value = await appelerServeur<PageResultats>(`/api/recherche?${parametres}`)
    emit('charge', page.value)
  } catch (e) {
    erreur.value = messageErreur(e)
  } finally {
    chargement.value = false
  }
}
watch(() => route.fullPath, charger, { immediate: true })

// Filtres en pastilles : verte et pleine quand le filtre est actif
const PASTILLES = [
  { cle: 'chez_moi', champ: 'chezMoi', texte: 'Vient chez moi' },
  { cle: 'carte', champ: 'carte', texte: 'Paiement par carte' },
  { cle: 'libre', champ: 'libre', texte: 'Libre dans les 7 jours' },
] as const

// Un clic sur une pastille relance la recherche aussitôt ; le prix maximum, après une petite pause de frappe
function filtre(cle: 'chez_moi' | 'carte' | 'libre', coche: boolean) {
  aller({ [cle]: coche ? '1' : undefined })
}
let minuterie: ReturnType<typeof setTimeout> | undefined
watch(
  () => filtres.value.prixMax,
  (prix) => {
    clearTimeout(minuterie)
    if (prix === (q.value.prix_max ?? '')) return
    minuterie = setTimeout(() => aller({ prix_max: prix.trim() || undefined }), 600)
  },
)
const avecFiltres = computed(() => ['chez_moi', 'carte', 'libre', 'prix_max'].some((cle) => q.value[cle]))
function enleverFiltres() {
  aller({ chez_moi: undefined, carte: undefined, libre: undefined, prix_max: undefined })
}
</script>

<template>
  <section class="flex flex-col gap-5">
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <p v-if="chargement && !page" class="text-texte-doux">Recherche…</p>

    <template v-if="page">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <h2 class="text-[clamp(20px,3vw,26px)] font-bold">
          {{ pluriel(page.total, 'prestataire') }} « {{ page.metier.nom }} » pour {{ page.ville.nom }}
        </h2>
        <div class="inline-flex overflow-hidden rounded-rafals border border-bord" role="group" aria-label="Ordre des résultats">
          <button
            v-for="choix in [{ id: 'note', texte: 'Les mieux notés' }, { id: 'distance', texte: 'Les plus proches' }]"
            :key="choix.id"
            type="button"
            class="min-h-[42px] px-3 font-semibold"
            :class="tri === choix.id ? 'bg-primaire-doux text-primaire' : 'bg-surface text-texte-doux'"
            :aria-pressed="tri === choix.id"
            @click="aller({ tri: choix.id === 'distance' ? 'distance' : undefined })"
          >
            {{ choix.texte }}
          </button>
        </div>
      </div>

      <div class="flex flex-wrap items-center gap-2">
        <button
          v-for="pastille in PASTILLES"
          :key="pastille.cle"
          type="button"
          class="min-h-[42px] rounded-full border border-primaire px-4 font-semibold"
          :class="filtres[pastille.champ] ? 'bg-primaire text-primaire-texte' : 'bg-surface text-primaire hover:bg-primaire-doux'"
          :aria-pressed="filtres[pastille.champ]"
          @click="filtre(pastille.cle, !filtres[pastille.champ])"
        >
          {{ pastille.texte }}
        </button>
        <label class="flex min-h-[42px] items-center gap-2 rounded-full border border-bord bg-surface px-4 font-medium">
          Prix maximum
          <input
            v-model="filtres.prixMax"
            inputmode="decimal"
            placeholder="ex. 60"
            class="w-16 border-b border-bord bg-transparent py-0.5 text-texte focus:border-primaire"
          />
          €
        </label>
      </div>

      <p v-if="chargement" class="text-texte-doux">Recherche…</p>
      <div v-else-if="page.resultats.length" class="flex flex-col gap-3">
        <CarteResultat v-for="r in page.resultats" :key="r.prestataire_id" :resultat="r" :metier="page.metier.nom" />
      </div>
      <AppSection v-else-if="avecFiltres">
        <p class="font-semibold">Aucun résultat avec ces filtres.</p>
        <div><AppBouton variante="secondaire" @click="enleverFiltres">Enlever les filtres</AppBouton></div>
      </AppSection>
      <AppSection v-else>
        <h2 class="text-xl font-bold">
          Aucun prestataire « {{ page.metier.nom }} » ne vient à {{ page.ville.nom }} pour l'instant.
        </h2>
        <template v-if="page.metiers_voisins.length">
          <p class="text-[13.5px] text-texte-doux">Essayez un métier voisin :</p>
          <div class="flex flex-wrap gap-2">
            <AppBouton
              v-for="voisin in page.metiers_voisins"
              :key="voisin.id"
              variante="secondaire"
              @click="aller({ metier: String(voisin.id) })"
            >
              {{ voisin.nom }}
            </AppBouton>
          </div>
        </template>
      </AppSection>

      <nav v-if="page.pages > 1" class="flex flex-wrap justify-center gap-1.5" aria-label="Pages de résultats">
        <AppBouton v-if="page.page > 1" variante="secondaire" @click="aller({ page: String(page.page - 1) }, true)">‹ Précédente</AppBouton>
        <AppBouton
          v-for="n in page.pages"
          :key="n"
          :variante="n === page.page ? 'principal' : 'secondaire'"
          @click="aller({ page: String(n) }, true)"
        >
          {{ n }}
        </AppBouton>
        <AppBouton v-if="page.page < page.pages" variante="secondaire" @click="aller({ page: String(page.page + 1) }, true)">Suivante ›</AppBouton>
      </nav>
    </template>
  </section>
</template>
