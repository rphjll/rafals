<script setup lang="ts">
// Page publique d'un prestataire (.doc/ihm/RM-PRESTATAIRE-PUBLIC-IHM.md ; RM-RECHERCHE.md) : profil, photos de son travail et avis.
// Jamais le téléphone, le mail ni la rue : ils sont donnés après une réservation.
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import AvisAffiche from '../components/avis/AvisAffiche.vue'
import FenetreDemandeDevis from '../components/devis/FenetreDemandeDevis.vue'
import BoutonAbonnement from '../components/prestataire/BoutonAbonnement.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppIcone from '../components/ui/AppIcone.vue'
import BoutonSignaler from '../components/BoutonSignaler.vue'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'
import { type AvisPublic, etoiles } from '../outils/avis'
import { couleurDe } from '../outils/noms'
import { euros } from '../outils/prix'
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
// Un clic sur la note (les 3 chiffres du haut) descend en douceur jusqu'aux avis
function versAvis() {
  document.getElementById('avis')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
function retour() {
  if (window.history.state?.back) routeur.back()
  else routeur.push('/trouver')
}
const prenom = computed(() => prestataire.value?.nom_affiche.replace(/^ZZTEST\s+/, '').split(/\s+/)[0] ?? '')
</script>

<template>
  <div class="page">
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>

    <template v-if="prestataire">
      <div v-if="monProfil" class="pp-auteur"><AppIcone nom="moi" /><span>Voici votre page, telle que les clients la voient.</span><RouterLink to="/profil">Modifier</RouterLink></div>
      <a v-else href="#" class="retour" @click.prevent="retour"><AppIcone nom="retour" />Retour</a>

      <!-- La carte de la grande maquette : bande de couleur, photo posée dessus, nom, métiers, lieu, 3 chiffres, boutons -->
      <section class="carte pp" style="--c: var(--primaire)">
        <div class="pp-couv" aria-hidden="true" />
        <div class="pp-corps">
          <img v-if="prestataire.a_une_photo" class="pp-photo" :src="`/api/prestataires/${prestataire.id}/photo`" :alt="`Photo de ${prestataire.nom_affiche}`" />
          <span v-else class="pp-photo" :style="{ background: couleurDe(prestataire.nom_affiche) }">{{ prenom[0]?.toUpperCase() }}</span>
          <div class="pp-nom">
            <h1>{{ prestataire.nom_affiche }}</h1>
            <span v-if="prestataire.siret_verifie" class="puce p-ok"><AppIcone nom="bouclier" class="size-4" />SIRET vérifié</span>
            <!-- Sans SIRET vérifié : l'étiquette que la règle impose (RM-PRESTATAIRES, limites sans SIRET) -->
            <span v-else class="puce p-accent">Particulier, non professionnel</span>
          </div>
          <p v-if="prestataire.metiers.length" class="pp-metier">
            <b>{{ prestataire.metiers[0]?.nom }}</b><template v-if="prestataire.metiers.length > 1"> · aussi {{ prestataire.metiers.slice(1).map((m) => (m.prix_centimes ? `${m.nom} (${euros(m.prix_centimes)}/h)` : m.nom)).join(', ') }}</template>
          </p>
          <p class="doux"><AppIcone nom="lieu" /> {{ lieuPourUnClient(prestataire) }}</p>
          <!-- 3 chiffres ; un clic sur la note descend jusqu'aux avis -->
          <div class="pp-chiffres">
            <button type="button" @click="versAvis">
              <b>{{ prestataire.nombre_avis ? `★ ${noteLisible(prestataire.note ?? 0)}` : 'Nouveau' }}</b><small>{{ prestataire.nombre_avis }} avis</small>
            </button>
            <span v-if="prestataire.metiers[0]?.prix_centimes"><b>{{ euros(prestataire.metiers[0].prix_centimes) }}</b><small>de l’heure</small></span>
            <span v-else><b>{{ prestataire.photos.length }}</b><small>photo{{ prestataire.photos.length > 1 ? 's' : '' }}</small></span>
            <span><b>{{ prestataire.abonnes }}</b><small>abonné{{ prestataire.abonnes > 1 ? 's' : '' }}</small></span>
          </div>
          <template v-if="!monProfil">
            <div class="pp-btns">
              <button type="button" class="btn btn-1" @click="ecrire"><AppIcone nom="messages" />Écrire à {{ prenom }}</button>
              <BoutonAbonnement :prestataire-id="prestataire.id" :nom="prestataire.nom_affiche" :abonne="prestataire.abonne" @change="Object.assign(prestataire, $event)" />
            </div>
            <div class="w-full max-w-[420px]">
              <AppBouton v-if="prestataire.siret_verifie" variante="secondaire" pleine-largeur @click="demanderDevis"><AppIcone nom="devis" />Demander un devis</AppBouton>
              <AppBouton v-else variante="verrouille" pleine-largeur :raison-verrou="VERROU_SIRET.devisClient">Demander un devis</AppBouton>
            </div>
            <AppAlerte v-if="erreurEcrire">{{ erreurEcrire }}</AppAlerte>
          </template>
        </div>
      </section>
      <AppAlerte v-if="prestataire.absences" etat="attente">
        {{ prestataire.absences }} absence{{ prestataire.absences > 1 ? 's' : '' }} sans prévenir ces 6 derniers mois
      </AppAlerte>

      <section v-if="prestataire.presentation" class="section">
        <h2>À propos</h2>
        <div class="carte p-[18px]"><p class="pp-bio whitespace-pre-line">{{ prestataire.presentation }}</p></div>
      </section>

      <section v-if="prestataire.photos.length" class="section">
        <h2>Son travail en photos</h2>
        <div class="photos pp-photos">
          <a v-for="rang in prestataire.photos" :key="rang" class="ph" style="--c: var(--surface2)" :href="adressePhotoTravail(prestataire.id, rang)" target="_blank" rel="noopener">
            <img :src="adressePhotoTravail(prestataire.id, rang)" :alt="`Photo n° ${rang} du travail de ${prenom}`" loading="lazy" />
          </a>
        </div>
      </section>

      <section id="avis" class="section">
        <h2>Avis</h2>
        <div class="carte pp-avis p-[18px]">
          <div class="pp-note">
            <b>{{ prestataire.nombre_avis ? noteLisible(prestataire.note ?? 0) : '—' }}</b>
            <span class="etoile">{{ etoiles(prestataire.note ?? 0) }}</span>
            <small class="doux">{{ prestataire.nombre_avis }} avis</small>
          </div>
          <div class="pp-liste">
            <div v-for="a in avis.slice(0, nombreAffiches)" :key="a.id" class="avis"><AvisAffiche :avis="a" :nom-prestataire="prenom" /></div>
            <p v-if="!avis.length" class="doux">Pas encore d'avis : seuls les clients qui ont eu un rendez-vous peuvent en laisser un.</p>
            <button v-if="avis.length > nombreAffiches" type="button" class="btn btn-2 btn-petit" @click="nombreAffiches += AVIS_PAR_PAGE">Voir plus d'avis</button>
          </div>
        </div>
      </section>
      <p class="pp-pied doux petit">
        <AppIcone nom="bouclier" />Le téléphone et l’adresse sont donnés après une réservation.
        <BoutonSignaler v-if="!monProfil" :prestataire-id="prestataire.id" :nom-prestataire="prestataire.nom_affiche" />
      </p>
      <FenetreDemandeDevis :prestataire="prestataire" :ouverte="devisOuvert" @fermer="devisOuvert = false" @envoyee="devisEnvoye" />
    </template>
  </div>
</template>
