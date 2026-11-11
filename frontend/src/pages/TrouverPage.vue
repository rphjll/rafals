<script setup lang="ts">
// Trouver un prestataire (.doc/ihm/RM-TROUVER-IHM.md ; RM-RECHERCHE.md), identique à la grande maquette depuis le
// 10/11/2026 : le titre, un champ « Nom, métier ou ville… », les pastilles des services, puis les cartes, de la plus
// proche à la plus loin.
// - Sans ville connue : on la demande d'abord (rafals cherche toujours autour d'une ville).
// - /trouver?ville=12768 : tous les services ; &dossier=3 : un seul service (pastille) ; &q=fuite : le texte tapé.
// - /trouver?metier=3&ville=12768 (anciens liens) : les résultats d'un métier, avec tri et filtres.
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import AppChoixCommune from '../components/AppChoixCommune.vue'
import CarteResultat from '../components/recherche/CarteResultat.vue'
import ResultatsRecherche from '../components/recherche/ResultatsRecherche.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import type { CommuneVisible } from '../outils/prestataires'
import { type CarteResultat as Carte, type PageRubriques, retenirVille, villeRetenue } from '../outils/recherche'

const route = useRoute()
const routeur = useRouter()

const commune = ref<CommuneVisible | null>(null)
const changerVille = ref(false)
const ville = computed(() => (typeof route.query.ville === 'string' ? route.query.ville : ''))
const dossier = computed(() => (typeof route.query.dossier === 'string' ? Number(route.query.dossier) : null))
const parMetier = computed(() => !!route.query.metier && !!ville.value)

// Ville déjà donnée lors d'une visite précédente : pas besoin de la redemander
watch(
  ville,
  (v) => {
    const retenue = villeRetenue()
    if (!v && retenue) routeur.replace({ query: { ...route.query, ville: String(retenue.id) } })
  },
  { immediate: true },
)
watch(commune, (c) => {
  if (!c) return
  retenirVille(c)
  changerVille.value = false
  routeur.push({ query: { ville: String(c.id), ...(route.query.q ? { q: route.query.q } : {}) } })
})

// Tous les services d'une ville : les cartes de chaque rubrique, sans doublon (un prestataire a plusieurs métiers)
const page = ref<PageRubriques | null>(null)
const cartesDossier = ref<Carte[]>([])
const pageDossier = ref({ page: 1, pages: 1 })
const erreur = ref('')
const chargement = ref(false)
async function charger() {
  if (!ville.value || parMetier.value) return
  chargement.value = true
  erreur.value = ''
  try {
    page.value = await appelerServeur<PageRubriques>(`/api/recherche/rubriques?commune_id=${ville.value}`)
    retenirVille(page.value.ville)
    if (dossier.value) await chargerDossier(1)
  } catch (e) {
    page.value = null
    erreur.value = messageErreur(e)
  } finally {
    chargement.value = false
  }
}
// Une pastille : toutes les cartes de ce service, page après page ([Voir plus])
async function chargerDossier(numero: number) {
  const r = await appelerServeur<PageRubriques>(`/api/recherche/rubriques/${dossier.value}?commune_id=${ville.value}&page=${numero}`)
  const rubrique = r.rubriques[0]
  cartesDossier.value = numero === 1 ? (rubrique?.resultats ?? []) : [...cartesDossier.value, ...(rubrique?.resultats ?? [])]
  pageDossier.value = { page: rubrique?.page ?? 1, pages: rubrique?.pages ?? 1 }
}
watch(() => [ville.value, dossier.value, parMetier.value], charger, { immediate: true })

const cartes = computed<Carte[]>(() => {
  if (dossier.value) return cartesDossier.value
  const vues = new Map<number, Carte>()
  for (const r of page.value?.rubriques ?? []) for (const c of r.resultats) if (!vues.has(c.prestataire_id) || c.principal) vues.set(c.prestataire_id, c)
  return [...vues.values()].sort((a, b) => a.distance_km - b.distance_km)
})
// Le champ filtre les cartes sur le nom, le métier et la ville (« fuite » ne trouve que ce qui est écrit)
const texte = ref(typeof route.query.q === 'string' ? route.query.q : '')
const visibles = computed(() => {
  const mot = texte.value.trim().toLowerCase()
  return mot ? cartes.value.filter((c) => `${c.nom_affiche} ${c.metier} ${c.ville}`.toLowerCase().includes(mot)) : cartes.value
})
function choisirDossier(id: number | null) {
  const { dossier: _d, page: _p, ...reste } = route.query
  routeur.replace({ query: id ? { ...reste, dossier: String(id) } : reste })
}
</script>

<template>
  <div class="page">
    <div class="tete">
      <h1>Trouver un prestataire</h1>
      <p v-if="page && !changerVille">
        Autour de {{ page.ville.nom }}, triés du plus proche au plus loin.
        <button type="button" class="lien" @click="changerVille = true">Changer de ville</button>
      </p>
      <p v-else-if="!parMetier">Indiquez votre ville : rafals vous montre les prestataires autour, du plus proche au plus loin.</p>
    </div>

    <!-- Pas encore de ville, ou [Changer de ville] -->
    <div v-if="(!ville || changerVille) && !parMetier" class="carte form p-[18px]">
      <AppChoixCommune v-model="commune" etiquette="Votre ville" />
      <button v-if="changerVille" type="button" class="btn btn-2 btn-petit" style="align-self: flex-start" @click="changerVille = false">Annuler</button>
    </div>

    <ResultatsRecherche v-if="parMetier" />
    <template v-else-if="ville">
      <div class="champ"><input v-model="texte" placeholder="Nom, métier ou ville…" aria-label="Rechercher" /></div>
      <div v-if="page?.rubriques.length" class="chips">
        <button type="button" class="chip" :class="{ on: !dossier }" @click="choisirDossier(null)">Tous</button>
        <button v-for="r in page.rubriques" :key="r.dossier_id" type="button" class="chip" :class="{ on: dossier === r.dossier_id }" @click="choisirDossier(r.dossier_id)">
          {{ r.nom }}
        </button>
      </div>
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <div v-else-if="!chargement || cartes.length" class="section">
        <template v-if="visibles.length">
          <p class="doux petit">{{ visibles.length }} prestataire{{ visibles.length > 1 ? 's' : '' }}</p>
          <div class="grille">
            <CarteResultat v-for="c in visibles" :key="c.prestataire_id" :resultat="c" />
          </div>
          <button v-if="dossier && pageDossier.page < pageDossier.pages" type="button" class="btn btn-2" style="align-self: center" @click="chargerDossier(pageDossier.page + 1)">
            Voir plus
          </button>
        </template>
        <div v-else-if="page" class="carte vide">
          <h3>Personne pour l’instant</h3>
          <p style="margin-top: 6px">Essayez un autre métier, ou <RouterLink to="/demandes/nouvelle">publiez une demande</RouterLink> : les prestataires viendront à vous.</p>
        </div>
      </div>
    </template>
  </div>
</template>
