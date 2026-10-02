<script setup lang="ts">
// Page publique d'un prestataire (.doc/ihm/RM-PRESTATAIRE-PUBLIC-IHM.md ; RM-RECHERCHE.md) : profil et annonces en ligne.
// Jamais le téléphone, le mail ni la rue : ils sont donnés après une réservation.
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import AvisAffiche from '../components/avis/AvisAffiche.vue'
import AvatarPrestataire from '../components/prestataire/AvatarPrestataire.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBadge from '../components/ui/AppBadge.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppSection from '../components/ui/AppSection.vue'
import { useCompte } from '../composables/useCompte'
import { lieuPourLeClient, paiement, prixCourt } from '../outils/annonces'
import { type AvisPublic, etoiles } from '../outils/avis'
import { type PrestatairePublic, noteLisible } from '../outils/recherche'

const route = useRoute()
const routeur = useRouter()
const { compte } = useCompte()
const prestataire = ref<PrestatairePublic | null>(null)
const erreur = ref('')
// Avis : les 10 plus récents, puis [Voir plus d'avis]
const AVIS_PAR_PAGE = 10
const avis = ref<AvisPublic[]>([])
const nombreAffiches = ref(AVIS_PAR_PAGE)

watch(
  () => route.params.id,
  async (id) => {
    erreur.value = ''
    try {
      ;[prestataire.value, avis.value] = await Promise.all([
        appelerServeur<PrestatairePublic>(`/api/prestataires/${id}`),
        appelerServeur<AvisPublic[]>(`/api/prestataires/${id}/avis`),
      ])
      nombreAffiches.value = AVIS_PAR_PAGE
    } catch (e) {
      erreur.value = messageErreur(e)
    }
  },
  { immediate: true },
)
const monProfil = computed(() => !!prestataire.value && compte.value?.prestataire_id === prestataire.value.id)
// Retour à la page d'avant (ex. les résultats) ; ouverte directement par un lien : la recherche
function retour() {
  if (window.history.state?.back) routeur.back()
  else routeur.push('/trouver')
}
const prenom = computed(() => prestataire.value?.nom_affiche.replace(/^ZZTEST\s+/, '').split(/\s+/)[0] ?? '')
</script>

<template>
  <div class="mx-auto flex w-full max-w-[880px] flex-col gap-4">
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>

    <template v-if="prestataire">
      <p class="text-[13.5px] text-texte-doux">
        <a href="#" class="hover:text-primaire" @click.prevent="retour">‹ Retour</a>
      </p>
      <AppAlerte v-if="monProfil" etat="attente">
        Votre page, telle que les clients la voient.
        <RouterLink to="/proposer" class="font-semibold underline">Mon activité</RouterLink>
      </AppAlerte>

      <AppSection>
        <div class="grid items-start gap-4 sm:grid-cols-[96px_1fr]">
          <AvatarPrestataire :id="prestataire.id" :nom="prestataire.nom_affiche" :a-une-photo="prestataire.a_une_photo" taille="grande" />
          <div class="flex flex-col gap-2">
            <div class="flex flex-wrap items-center gap-2">
              <h1 class="text-[26px] font-bold">{{ prestataire.nom_affiche }}</h1>
              <AppBadge v-if="prestataire.siret_verifie" etat="ok">SIRET vérifié</AppBadge>
            </div>
            <p v-if="prestataire.nombre_avis" class="text-[14px]">
              <b class="text-accent">★ {{ noteLisible(prestataire.note ?? 0) }}</b>
              <span class="text-texte-doux"> ({{ prestataire.nombre_avis }} avis)</span>
            </p>
            <div v-else><AppBadge etat="attente">Nouveau sur rafals</AppBadge></div>
            <p class="text-[14px] text-texte-doux">
              <template v-if="prestataire.metiers.length">
                {{ prestataire.metiers[0]?.nom }}
                <template v-if="prestataire.metiers.length > 1">
                  · aussi {{ prestataire.metiers.slice(1).map((m) => m.nom).join(', ') }}
                </template>
              </template>
            </p>
            <p class="text-[14px] text-texte-doux">
              Part de {{ prestataire.ville }}, se déplace jusqu'à {{ prestataire.distance_km }} km
            </p>
            <AppAlerte v-if="prestataire.absences" etat="attente">
              {{ prestataire.absences }} absence{{ prestataire.absences > 1 ? 's' : '' }} sans prévenir ces 6 derniers mois
            </AppAlerte>
            <p v-if="prestataire.presentation" class="whitespace-pre-line">{{ prestataire.presentation }}</p>
          </div>
        </div>
      </AppSection>

      <AppSection titre="Ses annonces">
        <p v-if="!prestataire.annonces.length" class="text-texte-doux">
          {{ prenom }} n'a pas d'annonce en ligne pour l'instant.
        </p>
        <div class="flex flex-col divide-y divide-bord">
          <div
            v-for="annonce in prestataire.annonces"
            :key="annonce.id"
            class="flex flex-wrap items-center justify-between gap-3 py-3 first:pt-0"
          >
            <div class="flex flex-col gap-0.5">
              <b>{{ annonce.titre }}</b>
              <p class="text-[13.5px] text-texte-doux">
                <span class="font-bold text-primaire">{{ prixCourt(annonce) }}</span> · {{ lieuPourLeClient(annonce) }} ·
                {{ paiement(annonce.modes_de_paiement).toLowerCase() }}
              </p>
            </div>
            <AppBouton variante="secondaire" @click="routeur.push(`/annonces/${annonce.id}`)">Voir l'annonce</AppBouton>
          </div>
        </div>
      </AppSection>

      <AppSection titre="Avis">
        <template v-if="avis.length">
          <div class="flex flex-wrap items-center gap-3.5">
            <span class="text-[34px] font-bold">{{ noteLisible(prestataire.note ?? 0) }}</span>
            <div>
              <div class="text-lg tracking-wide text-accent">{{ etoiles(prestataire.note ?? 0) }}</div>
              <span class="text-[13.5px] text-texte-doux">{{ prestataire.nombre_avis }} avis de clients ayant eu un rendez-vous</span>
            </div>
          </div>
          <div class="flex flex-col divide-y divide-bord">
            <div v-for="a in avis.slice(0, nombreAffiches)" :key="a.id" class="py-3 first:pt-0">
              <AvisAffiche :avis="a" :nom-prestataire="prenom" />
            </div>
          </div>
          <div v-if="avis.length > nombreAffiches">
            <AppBouton variante="secondaire" @click="nombreAffiches += AVIS_PAR_PAGE">Voir plus d'avis</AppBouton>
          </div>
        </template>
        <p v-else class="text-[14px] text-texte-doux">Pas encore d'avis.</p>
      </AppSection>
      <p class="text-[13px] text-texte-doux">Le téléphone et l'adresse sont donnés après une réservation.</p>
    </template>
  </div>
</template>
