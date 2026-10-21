<script setup lang="ts">
// Page publique d'un prestataire (.doc/ihm/RM-PRESTATAIRE-PUBLIC-IHM.md ; RM-RECHERCHE.md) : profil, photos de son travail et avis.
// Jamais le téléphone, le mail ni la rue : ils sont donnés après une réservation.
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import AvisAffiche from '../components/avis/AvisAffiche.vue'
import FenetreDemandeDevis from '../components/devis/FenetreDemandeDevis.vue'
import AvatarPrestataire from '../components/prestataire/AvatarPrestataire.vue'
import BoutonAbonnement from '../components/prestataire/BoutonAbonnement.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBadge from '../components/ui/AppBadge.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppSection from '../components/ui/AppSection.vue'
import BoutonSignaler from '../components/BoutonSignaler.vue'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'
import { texteAbonnes } from '../outils/abonnements'
import { type AvisPublic, etoiles } from '../outils/avis'
import { VERROU_SIRET, lieuPourUnClient } from '../outils/prestataires'
import { type PrestatairePublic, adressePhotoTravail, noteLisible } from '../outils/recherche'

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
// [Écrire à Karim] (RM-MESSAGERIE) : ouvre la conversation, ou la retrouve si elle existe déjà
const erreurEcrire = ref('')
async function ecrire() {
  if (!prestataire.value) return
  if (!compte.value) return routeur.push('/connexion')
  erreurEcrire.value = ''
  try {
    const conversation = await appelerServeur<{ id: number }>('/api/conversations', { prestataire_id: prestataire.value.id })
    routeur.push(`/messages/${conversation.id}`)
  } catch (e) {
    erreurEcrire.value = messageErreur(e) // ex. « Ce prestataire n'est pas joignable en ce moment. »
  }
}

// [Demander un devis] : seulement à un prestataire au SIRET vérifié (RM-DEVIS § « Sans annonces »)
const devisOuvert = ref(false)
const { afficherMessage } = useMessage()
function demanderDevis() {
  if (!compte.value) return routeur.push({ path: '/connexion', query: { retour: route.fullPath } })
  devisOuvert.value = true
}
function devisEnvoye() {
  devisOuvert.value = false
  afficherMessage(`Demande envoyée : ${prenom.value} vous répond par un devis.`)
  routeur.push('/devis')
}

const monProfil = computed(() => !!prestataire.value && compte.value?.prestataire_id === prestataire.value.id)
// Retour à la page d'avant (ex. les résultats) ; ouverte directement par un lien : la recherche
function retour() {
  if (window.history.state?.back) routeur.back()
  else routeur.push('/trouver')
}
const prenom = computed(() => prestataire.value?.nom_affiche.replace(/^ZZTEST\s+/, '').split(/\s+/)[0] ?? '')
</script>

<template>
  <div class="flex w-full flex-col gap-4">
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>

    <template v-if="prestataire">
      <p class="text-[13.5px] text-texte-doux">
        <a href="#" class="hover:text-primaire" @click.prevent="retour">‹ Retour</a>
      </p>
      <AppAlerte v-if="monProfil" etat="attente">
        Votre page, telle que les clients la voient.
        <RouterLink to="/profil" class="font-semibold underline">Mon profil</RouterLink>
      </AppAlerte>

      <!-- Ordinateur : la fiche à gauche, la carte « Besoin de Karim ? » à droite, qui reste visible.
           Téléphone : la présentation, la carte, puis les photos et les avis. -->
      <div class="grid items-start gap-8" :class="monProfil ? '' : 'md:grid-cols-[1fr_340px]'">
        <div class="flex min-w-0 flex-col gap-6">
          <div class="grid items-center gap-5 sm:grid-cols-[auto_1fr]">
            <AvatarPrestataire :id="prestataire.id" :nom="prestataire.nom_affiche" :a-une-photo="prestataire.a_une_photo" taille="grande" />
            <div class="flex min-w-0 flex-col gap-2">
              <h1 class="text-[clamp(28px,4.5vw,40px)] leading-tight font-black">{{ prestataire.nom_affiche }}</h1>
              <p v-if="prestataire.nombre_avis">
                <b class="text-accent">★ {{ noteLisible(prestataire.note ?? 0) }}</b>
                <span class="text-texte-doux"> · {{ prestataire.nombre_avis }} avis</span>
              </p>
              <div class="flex flex-wrap gap-1.5">
                <AppBadge v-if="!prestataire.nombre_avis" etat="attente">Nouveau sur rafals</AppBadge>
                <AppBadge v-if="prestataire.siret_verifie" etat="ok">SIRET vérifié</AppBadge>
              <!-- Sans SIRET vérifié : l'étiquette que la règle impose (RM-PRESTATAIRES, limites sans SIRET) -->
              <AppBadge v-else etat="attente">Particulier, non professionnel</AppBadge>
              </div>
              <!-- [S'abonner] et « 12 abonnés » (21/10/2026) ; sur sa propre page, seulement le nombre -->
              <div class="flex flex-wrap items-center gap-x-3.5 gap-y-2">
                <BoutonAbonnement
                  v-if="!monProfil"
                  :prestataire-id="prestataire.id"
                  :nom="prestataire.nom_affiche"
                  :abonne="prestataire.abonne"
                  @change="Object.assign(prestataire, $event)"
                />
                <span class="text-[13.5px] font-bold text-texte-doux tabular-nums">
                  {{ texteAbonnes(prestataire.abonnes) || "Aucun abonné pour l'instant" }}
                </span>
              </div>
            </div>
          </div>
          <div class="flex flex-col gap-1 text-texte-doux">
            <p v-if="prestataire.metiers.length">
              <b class="text-texte">{{ prestataire.metiers[0]?.nom }}</b>
              <template v-if="prestataire.metiers.length > 1">
                · aussi {{ prestataire.metiers.slice(1).map((m) => m.nom).join(', ') }}
              </template>
            </p>
            <p>{{ lieuPourUnClient(prestataire) }}</p>
          </div>
          <AppAlerte v-if="prestataire.absences" etat="attente">
            {{ prestataire.absences }} absence{{ prestataire.absences > 1 ? 's' : '' }} sans prévenir ces 6 derniers mois
          </AppAlerte>
          <p v-if="prestataire.presentation" class="max-w-[65ch] text-[16.5px] whitespace-pre-line">{{ prestataire.presentation }}</p>
        </div>

        <aside v-if="!monProfil" class="flex flex-col gap-3 rounded-carte bg-fonce p-6 text-sur-fonce md:sticky md:top-24">
          <h2 class="text-[22px] font-extrabold">Besoin de {{ prenom }} ?</h2>
          <AppBouton variante="accent" pleine-largeur @click="ecrire">Écrire à {{ prenom }}</AppBouton>
          <AppAlerte v-if="erreurEcrire">{{ erreurEcrire }}</AppAlerte>
          <AppBouton v-if="prestataire.siret_verifie" variante="secondaire" pleine-largeur @click="demanderDevis">Demander un devis</AppBouton>
          <AppBouton v-else variante="verrouille" pleine-largeur :raison-verrou="VERROU_SIRET.devisClient">Demander un devis</AppBouton>
          <p class="text-[13.5px] text-sur-fonce-doux">Son téléphone et son adresse vous sont donnés après un rendez-vous.</p>
        </aside>
      </div>

      <AppSection v-if="prestataire.photos.length" titre="Son travail en photos">
        <div class="grid grid-cols-[repeat(auto-fill,minmax(160px,1fr))] gap-3">
          <a v-for="rang in prestataire.photos" :key="rang" :href="adressePhotoTravail(prestataire.id, rang)" target="_blank" rel="noopener">
            <img
              :src="adressePhotoTravail(prestataire.id, rang)"
              :alt="`Photo n° ${rang} du travail de ${prenom}`"
              loading="lazy"
              class="aspect-[4/3] w-full rounded-rafals object-cover hover:ring-2 hover:ring-primaire"
            />
          </a>
        </div>
      </AppSection>

      <AppSection titre="Avis">
        <template v-if="avis.length">
          <div class="flex flex-wrap items-center gap-3.5">
            <span class="text-[40px] leading-none font-black">{{ noteLisible(prestataire.note ?? 0) }}</span>
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
      <BoutonSignaler v-if="!monProfil" :prestataire-id="prestataire.id" :nom-prestataire="prestataire.nom_affiche" />
      <FenetreDemandeDevis :prestataire="prestataire" :ouverte="devisOuvert" @fermer="devisOuvert = false" @envoyee="devisEnvoye" />
    </template>
  </div>
</template>
