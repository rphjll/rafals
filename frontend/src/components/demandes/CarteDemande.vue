<script setup lang="ts">
// Carte d'une demande publique (.doc/ihm/RM-DEMANDES-IHM.md), « Demandes › Près de chez moi », comme la grande maquette.
// Un prestataire qui peut répondre voit [Faire une proposition] (s'appelait [Répondre] avant le 25/11/2026 : la demande
// est publique, il fait une offre) et, avec un SIRET vérifié, le petit lien « ou un devis » ; sinon le bouton verrouillé
// et sa raison au clic.
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../../api'
import { useCompte } from '../../composables/useCompte'
import { texteNote } from '../../outils/avis'
import { formaterDate } from '../../outils/dates'
import { type DemandeVisible, REPONSES_MAX, texteBudget, texteQuand } from '../../outils/demandes'
import type { ProfilPrestataire } from '../../outils/prestataires'
import FenetreTexte, { type DemandeTexte } from '../FenetreTexte.vue'
import FenetreEcrireDevis from '../devis/FenetreEcrireDevis.vue'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppIcone from '../ui/AppIcone.vue'
import AppInitiales from '../ui/AppInitiales.vue'

const props = defineProps<{ demande: DemandeVisible }>()
const emit = defineEmits<{ maj: [] }>()
const routeur = useRouter()
const { compte } = useCompte()
const erreur = ref('')
const occupe = ref(false)

// « ou un devis » (25/11/2026) : la fenêtre de devis habituelle, envoyée sur la demande publiée
const aDeviser = ref<DemandeVisible | null>(null)
const factureTva = ref(false)
async function ouvrirDevis() {
  erreur.value = ''
  try {
    factureTva.value = (await appelerServeur<ProfilPrestataire>('/api/moi/prestataire')).facture_tva
    aDeviser.value = props.demande
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
function devisEnvoye() {
  aDeviser.value = null
  emit('maj')
}

// [Signaler…] : réservé aux prestataires ; l'administrateur laisse la demande ou la cache
const aSignaler = ref<DemandeTexte | null>(null)
function signaler() {
  aSignaler.value = {
    titre: `Signaler « ${props.demande.titre} »`,
    explication: 'Demande fausse, hors sujet ou contraire à la loi : l’administrateur de rafals la regarde. Votre nom n’est pas donné au client.',
    etiquette: 'Que se passe-t-il ?',
    aide: 'ex. « Ce n’est pas une vraie demande ». De 10 à 1000 caractères.',
    chemin: `/api/demandes/${props.demande.id}/signaler`,
    cle: 'motif',
    bouton: 'Signaler',
    danger: true,
    reussite: 'Demande signalée : l’administrateur va regarder.',
  }
}

async function repondre() {
  erreur.value = ''
  occupe.value = true
  try {
    const { conversation_id } = await appelerServeur<{ conversation_id: number }>(`/api/demandes/${props.demande.id}/repondre`, {})
    // La fenêtre « Faire une proposition » s'ouvre tout de suite dans la conversation (25/11/2026)
    routeur.push({ path: `/messages/${conversation_id}`, query: { proposition: '1' } })
  } catch (e) {
    erreur.value = messageErreur(e) // ex. « Cette demande est complète : 10 prestataires ont déjà répondu. »
  } finally {
    occupe.value = false
  }
}
</script>

<template>
  <!-- La demande publique de la grande maquette : le métier et la date, le titre, où et quand, le texte, puis qui demande et le bouton -->
  <article class="carte dmd p-[18px]">
    <div class="dmd-haut">
      <span class="puce p-accent">{{ demande.metier }}</span>
      <span class="doux petit">{{ formaterDate(demande.cree_le) }}</span>
    </div>
    <div>
      <h3>{{ demande.titre }}</h3>
      <p class="doux petit" style="margin-top: 2px">
        <AppIcone nom="lieu" class="size-[15px]" style="vertical-align: -3px" /> {{ demande.ville }} · {{ texteQuand(demande) }}
        · {{ demande.lieu === 'chez_moi' ? 'chez le client' : 'chez le prestataire' }}
        · {{ demande.budget_centimes ? `budget ${texteBudget(demande.budget_centimes)}` : 'prix à proposer' }}
      </p>
    </div>
    <p class="whitespace-pre-line">{{ demande.description }}</p>
    <!-- Les photos demandent d'être connecté : elles montrent souvent l'intérieur d'un logement -->
    <div v-if="demande.nombre_photos && compte" class="flex flex-wrap gap-2">
      <a v-for="n in demande.nombre_photos" :key="n" :href="`/api/demandes/${demande.id}/photos/${n}`" target="_blank" rel="noopener">
        <img :src="`/api/demandes/${demande.id}/photos/${n}`" :alt="`Photo ${n} de la demande « ${demande.titre} »`" class="size-24 rounded-[12px] object-cover" />
      </a>
    </div>
    <p v-else-if="demande.nombre_photos" class="doux petit">{{ demande.nombre_photos }} photo{{ demande.nombre_photos > 1 ? 's' : '' }} (connectez-vous pour les voir)</p>
    <div class="dmd-pied">
      <span class="qui">
        <AppInitiales :nom="demande.client" />
        <span>
          <b>{{ demande.client }}</b>
          <small class="doux">
            {{ demande.a_moi ? 'vous' : 'particulier' }} · {{ demande.nombre_reponses }} réponse{{ demande.nombre_reponses > 1 ? 's' : '' }} sur {{ REPONSES_MAX }}
            <template v-if="demande.client_avis">
              · <b class="etoile">{{ texteNote(demande.client_note, demande.client_avis) }}</b>
              <RouterLink :to="`/clients/${demande.client_id}/avis`" class="lien">Voir les avis</RouterLink>
            </template>
          </small>
        </span>
      </span>
      <span class="btns">
        <span v-if="demande.a_moi" class="puce p-neutre">C’est votre demande</span>
        <RouterLink v-else-if="demande.conversation_id" class="btn btn-2 btn-petit" :to="`/messages/${demande.conversation_id}`">
          <AppIcone nom="messages" />Voir la conversation
        </RouterLink>
        <button v-else-if="demande.peut_repondre" type="button" class="btn btn-1 btn-petit" :aria-busy="occupe || undefined" @click="repondre">
          Faire une proposition
        </button>
        <!-- Verrouillé, avec la raison au clic : autre métier, trop loin, activité en pause, pas d'adresse ; sans SIRET : métier
             qui en demande un, case manquante, plafond de l'année atteint -->
        <AppBouton v-else-if="demande.raison_verrou" variante="verrouille" petit :raison-verrou="demande.raison_verrou">Faire une proposition</AppBouton>
        <AppBouton
          v-else-if="compte?.prestataire_id && demande.complete"
          variante="verrouille"
          petit
          :raison-verrou="`Cette demande est complète : ${REPONSES_MAX} prestataires ont déjà répondu.`"
        >
          Faire une proposition
        </AppBouton>
        <!-- Pour les gros travaux (25/11/2026) : un devis à la place, en petit ; le bouton principal reste la proposition -->
        <button v-if="demande.peut_devis" type="button" class="lien-devis" @click="ouvrirDevis">ou un devis</button>
        <button v-if="compte?.prestataire_id && !demande.a_moi" type="button" class="lien-discret" @click="signaler">Signaler…</button>
      </span>
    </div>
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <FenetreTexte :demande="aSignaler" @fermer="aSignaler = null" @fait="aSignaler = null" />
    <FenetreEcrireDevis :demande="null" :publiee="aDeviser" :facture-tva="factureTva" @fermer="aDeviser = null" @envoye="devisEnvoye" />
  </article>
</template>

<style scoped>
.lien-devis{background:none;border:0;padding:0 4px;font-weight:600;font-size:14px;color:var(--primaire);text-decoration:underline;cursor:pointer}
</style>
