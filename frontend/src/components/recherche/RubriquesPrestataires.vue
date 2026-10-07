<script setup lang="ts">
// « Trouver un prestataire » pour une ville, sans métier choisi (.doc/ihm/RM-TROUVER-IHM.md ; RM-RECHERCHE.md) :
// une rubrique par dossier de métiers, ses prestataires en rangée qui défile, et [Voir tout].
// Tout est dans l'adresse : /trouver?ville=12768 (les rubriques), /trouver?ville=12768&dossier=3&page=2 (un dossier entier).
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../../api'
import { type PageRubriques, pluriel } from '../../outils/recherche'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppPages from '../ui/AppPages.vue'
import AppSection from '../ui/AppSection.vue'
import CarteResultat from './CarteResultat.vue'

// Lien ouvert directement : la page remet la ville dans le champ « Où ? »
const emit = defineEmits<{ charge: [page: PageRubriques] }>()

const route = useRoute()
const routeur = useRouter()
const page = ref<PageRubriques | null>(null)
const erreur = ref('')
const chargement = ref(false)

const ville = computed(() => String(route.query.ville ?? ''))
const dossier = computed(() => (typeof route.query.dossier === 'string' ? route.query.dossier : ''))

async function charger() {
  if (!ville.value) return
  chargement.value = true
  erreur.value = ''
  const parametres = new URLSearchParams({ commune_id: ville.value })
  if (dossier.value && route.query.page) parametres.set('page', String(route.query.page))
  try {
    page.value = await appelerServeur<PageRubriques>(`/api/recherche/rubriques${dossier.value ? `/${dossier.value}` : ''}?${parametres}`)
    emit('charge', page.value)
  } catch (e) {
    page.value = null
    erreur.value = messageErreur(e)
  } finally {
    chargement.value = false
  }
}
watch(() => route.fullPath, charger, { immediate: true })

function voir(dossierId?: number, numero?: number) {
  const suite: Record<string, string> = { ville: ville.value }
  if (dossierId) suite.dossier = String(dossierId)
  if (numero && numero > 1) suite.page = String(numero)
  routeur.push({ query: suite })
  if (dossierId) window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<template>
  <section class="flex flex-col gap-8">
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <p v-if="chargement && !page" class="text-texte-doux">Recherche…</p>

    <template v-if="page">
      <div v-if="dossier"><AppBouton variante="secondaire" @click="voir()">← Tous les services</AppBouton></div>

      <AppSection v-if="!page.rubriques.length">
        <h2 class="text-xl font-bold">Aucun prestataire ne vient à {{ page.ville.nom }} pour l'instant.</h2>
        <p class="text-texte-doux">
          Essayez une ville voisine, ou publiez votre demande : les prestataires qui s'inscriront près de chez vous pourront y répondre.
        </p>
        <div><AppBouton variante="accent" @click="routeur.push('/')">Publier une demande</AppBouton></div>
      </AppSection>

      <section v-for="rubrique in page.rubriques" :key="rubrique.dossier_id" class="flex flex-col gap-3">
        <div>
          <h2 class="text-[24px] font-black">{{ rubrique.nom }}</h2>
          <p class="text-[14.5px] text-texte-doux">{{ pluriel(rubrique.total, 'prestataire') }} près de {{ page.ville.nom }}</p>
        </div>

        <template v-if="dossier">
          <div class="grid grid-cols-[repeat(auto-fill,minmax(270px,1fr))] gap-4">
            <CarteResultat v-for="r in rubrique.resultats" :key="r.prestataire_id" :resultat="r" />
          </div>
          <AppPages :page="rubrique.page" :pages="rubrique.pages" etiquette="Pages de prestataires" @aller="(n) => voir(rubrique.dossier_id, n)" />
        </template>

        <template v-else>
          <!-- La rangée défile de côté ; la marge négative laisse la place à l'ombre et à l'anneau de survol -->
          <div class="-mx-1 flex snap-x gap-4 overflow-x-auto px-1 pt-1.5 pb-4" tabindex="0" :aria-label="`Prestataires : ${rubrique.nom}`">
            <div v-for="r in rubrique.resultats" :key="r.prestataire_id" class="w-[min(318px,82vw)] shrink-0 snap-start">
              <CarteResultat :resultat="r" />
            </div>
          </div>
          <div class="flex justify-center">
            <AppBouton variante="secondaire" @click="voir(rubrique.dossier_id)">Voir tout</AppBouton>
          </div>
        </template>
      </section>
    </template>
  </section>
</template>
