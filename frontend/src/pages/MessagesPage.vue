<script setup lang="ts">
// Messages (.doc/ihm/RM-MESSAGES-IHM.md ; RM-MESSAGERIE.md) : /messages = la liste de mes conversations ;
// /messages/12 = le fil avec Karim (ou Marie D.), ses propositions, et la zone pour écrire.
// Comme la grande maquette (10/11/2026) : la liste sur une page, chaque conversation sur la sienne (« ‹ Messages »),
// les bulles, puis la barre d'écriture collée en bas.
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { appelerServeur, ErreurServeur, messageErreur } from '../api'
import FenetreTexte, { type DemandeTexte } from '../components/FenetreTexte.vue'
import FenetreAvis from '../components/avis/FenetreAvis.vue'
import CarteProposition from '../components/messagerie/CarteProposition.vue'
import FenetreProposition from '../components/messagerie/FenetreProposition.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBadge from '../components/ui/AppBadge.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppFenetre from '../components/ui/AppFenetre.vue'
import AppIcone from '../components/ui/AppIcone.vue'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'
import { useNonLus } from '../composables/useNonLus'
import { texteNote } from '../outils/avis'
import { formaterDate, formaterDateHeure } from '../outils/dates'
import { type DemandeVisible, texteBudget, texteQuand } from '../outils/demandes'
import AppInitiales from '../components/ui/AppInitiales.vue'
import {
  type ANoter, type ConversationResumee, type ConversationVisible, type MessageVisible, type PropositionVisible, repeteUneCarte,
} from '../outils/messagerie'

const PHOTOS_MAX = 5
const RAFRAICHIR_MS = 15000 // le fil se relit tout seul : les nouveaux messages arrivent sans recharger la page

const route = useRoute()
const routeur = useRouter()
const { compte, chargementFait } = useCompte()
const { afficherMessage } = useMessage()
const { actualiserNonLus } = useNonLus()

const conversationId = computed(() => (route.params.id ? Number(route.params.id) : null))
const liste = ref<ConversationResumee[] | null>(null)
const conversation = ref<ConversationVisible | null>(null)
const propositions = ref<PropositionVisible[]>([])
const demandes = ref<DemandeVisible[]>([])
// Rendez-vous passés entre nous deux, encore notables : une carte « Comment ça s'est passé ? » dans le fil
const aNoter = ref<ANoter[]>([])
const cibleAvis = ref<{ rendezVousId: number; avis: null; prestataire: string; quoi: string; versClient: boolean } | null>(null)
const joursRestants = (jusquAu: string) => Math.max(0, Math.ceil((new Date(jusquAu).getTime() - Date.now()) / 86400000))
const erreur = ref('')
// « 2 conversations non lues. » ; à côté de chaque ligne, le jour du dernier message (« 12/11 »)
const nonLues = computed(() => (liste.value ?? []).filter((c) => c.non_lus).length)
watch([chargementFait, compte], () => {
  if (chargementFait.value && !compte.value) routeur.replace('/connexion')
})
const jourCourtDe = (iso: string | null) => (iso ? new Date(iso).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', timeZone: 'Europe/Paris' }) : '')

const texte = ref('')
const photos = ref<File[]>([])
const champPhotos = ref<HTMLInputElement | null>(null)
const erreurEnvoi = ref('')
const envoiEnCours = ref(false)
const basDuFil = ref<HTMLElement | null>(null)

const fenetreProposition = ref(false)
const aBloquer = ref(false)
// [Plus…] montre « Signaler… » et « Bloquer… », rangés pour ne pas encombrer le haut du fil
const plusOuvert = ref(false)
const aSignaler = ref<DemandeTexte | null>(null)

// Messages et propositions mêlés, du plus ancien au plus récent
type Element = { cle: string; quand: string; message?: MessageVisible; proposition?: PropositionVisible; noter?: ANoter }
const fil = computed<Element[]>(() => {
  const messages = (conversation.value?.messages ?? [])
    .filter((m) => !(m.genre === 'information' && repeteUneCarte(m.texte)))
    .map((m) => ({ cle: `m${m.id}`, quand: m.cree_le, message: m }))
  const cartes = propositions.value.map((p) => ({ cle: `p${p.id}`, quand: p.cree_le, proposition: p }))
  const notes = aNoter.value.map((n) => ({ cle: `n${n.rendez_vous_id}`, quand: n.quand, noter: n }))
  return [...messages, ...cartes, ...notes].sort((a, b) => a.quand.localeCompare(b.quand))
})
// Le prestataire propose pour une demande encore ouverte à laquelle il a répondu
const demandesOuvertes = computed(() => demandes.value.filter((d) => d.peut_repondre))

async function charger(defiler = false) {
  if (!compte.value) return
  try {
    if (conversationId.value === null) {
      liste.value = await appelerServeur<ConversationResumee[]>('/api/moi/conversations')
      conversation.value = null
    } else {
      const id = conversationId.value
      const avant = conversation.value?.messages.length ?? 0
      const [lue, sesPropositions, sesDemandes, sesNotes] = await Promise.all([
        appelerServeur<ConversationVisible>(`/api/conversations/${id}`),
        appelerServeur<PropositionVisible[]>(`/api/conversations/${id}/propositions`),
        appelerServeur<DemandeVisible[]>(`/api/conversations/${id}/demandes`),
        appelerServeur<ANoter[]>(`/api/conversations/${id}/a-noter`),
      ])
      if (id !== conversationId.value) return // on a changé de page pendant la lecture
      conversation.value = lue
      propositions.value = sesPropositions
      demandes.value = sesDemandes
      aNoter.value = sesNotes
      if (defiler || lue.messages.length > avant) nextTick(() => basDuFil.value?.scrollIntoView({ block: 'end' }))
      // La liste de gauche, relue après le fil : la conversation ouverte n'y compte plus comme « non lue »
      liste.value = await appelerServeur<ConversationResumee[]>('/api/moi/conversations')
    }
    erreur.value = ''
    actualiserNonLus()
  } catch (e) {
    erreur.value = messageErreur(e)
    if (e instanceof ErreurServeur && e.statut === 404) conversation.value = null
  }
}

let minuteur: ReturnType<typeof setInterval> | undefined
onMounted(() => {
  charger(true)
  minuteur = setInterval(() => document.visibilityState === 'visible' && charger(), RAFRAICHIR_MS)
})
onBeforeUnmount(() => clearInterval(minuteur))
watch([conversationId, compte], () => {
  conversation.value = null
  propositions.value = []
  texte.value = erreurEnvoi.value = ''
  photos.value = []
  plusOuvert.value = false
  charger(true)
})

function choisirPhotos(evenement: Event) {
  const champ = evenement.target as HTMLInputElement
  erreurEnvoi.value = ''
  photos.value = [...photos.value, ...Array.from(champ.files ?? [])].slice(0, PHOTOS_MAX)
  champ.value = ''
}

async function envoyer() {
  if (envoiEnCours.value || !conversation.value || (!texte.value.trim() && !photos.value.length)) return
  erreurEnvoi.value = ''
  envoiEnCours.value = true
  const formulaire = new FormData()
  formulaire.append('texte', texte.value)
  photos.value.forEach((photo) => formulaire.append('photos', photo))
  try {
    conversation.value = await appelerServeur<ConversationVisible>(`/api/conversations/${conversation.value.id}/messages`, formulaire)
    texte.value = ''
    photos.value = []
    nextTick(() => basDuFil.value?.scrollIntoView({ block: 'end' }))
  } catch (e) {
    erreurEnvoi.value = messageErreur(e) // ex. « Votre message semble injurieux : reformulez-le calmement… »
  } finally {
    envoiEnCours.value = false
  }
}

async function bloquer(oui: boolean) {
  if (!conversation.value) return
  try {
    conversation.value = await appelerServeur<ConversationVisible>(`/api/conversations/${conversation.value.id}/${oui ? 'bloquer' : 'debloquer'}`, {})
    afficherMessage(oui ? 'Personne bloquée : plus aucun message ne passe.' : 'Conversation débloquée.')
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
  aBloquer.value = false
}

function signaler() {
  if (!conversation.value) return
  aSignaler.value = {
    titre: `Signaler ${conversation.value.avec}`,
    explication: 'L’administrateur de rafals lira cette conversation pour juger. Votre nom n’est pas donné à l’autre personne.',
    etiquette: 'Que se passe-t-il ?',
    aide: 'ex. « Il insiste pour être payé avant de venir ». De 10 à 1000 caractères.',
    chemin: `/api/conversations/${conversation.value.id}/signaler`,
    cle: 'motif',
    bouton: 'Signaler',
    danger: true,
    reussite: 'Conversation signalée : l’administrateur va regarder.',
  }
}
</script>

<template>
  <div class="page">
    <!-- ---------- La liste des conversations (grande maquette : une ligne par personne) ---------- -->
    <template v-if="conversationId === null">
      <div class="tete">
        <h1>Messages</h1>
        <p v-if="liste">{{ nonLues ? `${nonLues} conversation${nonLues > 1 ? 's' : ''} non lue${nonLues > 1 ? 's' : ''}.` : 'Tout est lu.' }}</p>
      </div>
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <div v-if="liste?.length" class="liste">
        <RouterLink v-for="c in liste" :key="c.id" class="ligne" :to="`/messages/${c.id}`">
          <AppInitiales :nom="c.avec" />
          <div class="txt">
            <b>{{ c.avec }}<AppBadge v-if="c.bloquee" etat="neutre" class="ml-2">bloquée</AppBadge></b>
            <span>{{ c.apercu || 'Aucun message pour l’instant.' }}</span>
          </div>
          <span class="fin petit">
            <span v-if="c.non_lus" class="point" aria-label="Non lu" />{{ jourCourtDe(c.dernier_message_le) }}
          </span>
        </RouterLink>
      </div>
      <div v-else-if="liste" class="carte vide">
        <h3>Aucune conversation</h3>
        <p style="margin-top: 6px">Publiez une demande, ou répondez à une demande si vous proposez vos services.</p>
      </div>
    </template>

    <!-- ---------- Une conversation ---------- -->
    <template v-else>
      <RouterLink class="retour" to="/messages"><AppIcone nom="retour" />Messages</RouterLink>
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <template v-if="conversation">
        <div class="flex flex-wrap items-center gap-3">
          <AppInitiales :nom="conversation.avec" />
          <div class="mr-auto flex min-w-0 flex-col">
            <h2>{{ conversation.avec }}</h2>
            <span v-if="conversation.avec_avis" class="doux petit">
              {{ texteNote(conversation.avec_note, conversation.avec_avis) }}
              <RouterLink
                :to="conversation.cote === 'prestataire' ? `/clients/${conversation.client_id}/avis` : `/prestataires/${conversation.prestataire_id}`"
                class="lien"
              >
                Voir les avis
              </RouterLink>
            </span>
          </div>
          <AppBouton variante="secondaire" petit @click="plusOuvert = !plusOuvert">Plus…</AppBouton>
          <div v-if="plusOuvert" class="btns w-full justify-end">
            <AppBouton variante="secondaire" petit @click="signaler">Signaler…</AppBouton>
            <AppBouton v-if="!conversation.bloquee" variante="danger" petit @click="aBloquer = true">Bloquer…</AppBouton>
            <AppBouton v-else-if="conversation.bloquee_par_moi" variante="secondaire" petit @click="bloquer(false)">Débloquer</AppBouton>
          </div>
        </div>

        <!-- Les demandes dont on parle, rappelées en haut -->
        <p v-for="d in demandes" :key="d.id" class="dmd-vide petit">
          Demande : <b style="color: var(--texte)">{{ d.titre }}</b> · {{ d.ville }} · {{ texteQuand(d) }}<template v-if="d.budget_centimes">
            · budget {{ texteBudget(d.budget_centimes) }}</template>
        </p>

        <div class="conv" aria-live="polite">
          <template v-for="element in fil" :key="element.cle">
            <CarteProposition
              v-if="element.proposition"
              :proposition="element.proposition"
              :cote="conversation.cote"
              :avec="conversation.avec"
              @change="charger(true)"
            />
            <div v-else-if="element.noter" class="carte flex flex-col gap-2 p-[18px]" :class="element.noter.deja_note ? 'opacity-80' : ''">
              <span class="doux petit">Rendez-vous passé · {{ element.noter.titre }} · {{ formaterDate(element.noter.debut) }}</span>
              <b>Comment ça s'est passé avec {{ conversation.avec }} ?</b>
              <div v-if="element.noter.deja_note"><AppBadge etat="ok">avis laissé</AppBadge></div>
              <div v-else class="btns" style="align-items: center">
                <AppBouton
                  petit
                  @click="cibleAvis = {
                    rendezVousId: element.noter.rendez_vous_id, avis: null, prestataire: conversation.avec,
                    quoi: `${element.noter.titre} · ${formaterDate(element.noter.debut)}`, versClient: conversation.cote === 'prestataire',
                  }"
                >
                  Noter {{ conversation.avec }}
                </AppBouton>
                <span class="doux petit">encore {{ joursRestants(element.noter.jusqu_au) }} jours</span>
              </div>
            </div>
            <p v-else-if="element.message?.genre === 'information'" class="puce p-neutre self-center" style="white-space: normal; text-align: center">
              {{ element.message.texte }}
            </p>
            <div v-else-if="element.message" class="bulle" :class="{ moi: element.message.de_moi }">
              <span v-if="element.message.texte" class="break-words whitespace-pre-line">{{ element.message.texte }}</span>
              <div v-if="element.message.nombre_photos" class="mt-1.5 flex flex-wrap gap-2">
                <a v-for="n in element.message.nombre_photos" :key="n" :href="`/api/messages/${element.message.id}/photos/${n}`" target="_blank" rel="noopener">
                  <img :src="`/api/messages/${element.message.id}/photos/${n}`" :alt="`Photo ${n} du message`" class="size-24 rounded-[12px] object-cover" />
                </a>
              </div>
              <small>
                {{ formaterDateHeure(element.message.cree_le) }}<template v-if="element.message.de_moi"> · {{ element.message.lu ? 'lu' : 'envoyé' }}</template>
              </small>
            </div>
          </template>
          <p v-if="!fil.length" class="doux">Aucun message pour l'instant : écrivez le premier.</p>
          <span ref="basDuFil" />
        </div>

        <AppAlerte v-if="conversation.bloquee" etat="neutre">Conversation bloquée : plus aucun message ne passe.</AppAlerte>
        <template v-else>
          <div v-if="photos.length" class="btns">
            <span v-for="(photo, rang) in photos" :key="rang" class="puce p-neutre">
              {{ photo.name }}
              <button type="button" class="font-bold" :aria-label="`Enlever ${photo.name}`" @click="photos.splice(rang, 1)">×</button>
            </span>
          </div>
          <AppAlerte v-if="erreurEnvoi">{{ erreurEnvoi }}</AppAlerte>
          <!-- La barre d'écriture de la maquette, collée en bas : photo, texte, envoyer -->
          <form class="ecrire" @submit.prevent="envoyer">
            <button
              v-if="photos.length < PHOTOS_MAX"
              type="button"
              class="btn btn-2"
              style="padding: 0 14px"
              :aria-label="`Joindre une photo (${photos.length} / ${PHOTOS_MAX})`"
              @click="champPhotos?.click()"
            >
              <AppIcone nom="photo" />
            </button>
            <input id="message" v-model="texte" maxlength="2000" autocomplete="off" :placeholder="`Écrire à ${conversation.avec.split(' ')[0]}…`" aria-label="Votre message" />
            <button type="submit" class="btn btn-1" :class="envoiEnCours ? 'cursor-wait opacity-70' : ''" :aria-busy="envoiEnCours || undefined" aria-label="Envoyer">
              <AppIcone nom="envoyer" />
            </button>
            <input ref="champPhotos" type="file" accept="image/jpeg,image/png" multiple class="sr-only" aria-label="Photos à joindre" @change="choisirPhotos" />
          </form>
          <div v-if="conversation.cote === 'prestataire'">
            <AppBouton variante="accent" @click="fenetreProposition = true">Faire une proposition…</AppBouton>
          </div>
        </template>
        <p v-if="conversation.coordonnees_masquees" class="doux petit">
          Téléphone et mail sont masqués dans les messages tant qu'il n'y a pas de rendez-vous entre vous.
        </p>
      </template>
    </template>

    <FenetreProposition
      v-if="conversation?.cote === 'prestataire'"
      :ouverte="fenetreProposition"
      :conversation-id="conversation.id"
      :avec="conversation.avec"
      :demandes="demandesOuvertes"
      @fermer="fenetreProposition = false"
      @envoyee="(fenetreProposition = false), charger(true)"
    />
    <AppFenetre :ouverte="aBloquer" titre="Bloquer cette personne ?" @fermer="aBloquer = false">
      Plus aucun message ne passera, dans les deux sens. Les rendez-vous déjà pris restent.
      <template #pied>
        <button type="button" class="btn btn-danger" @click="bloquer(true)">Bloquer</button>
        <AppBouton variante="secondaire" @click="aBloquer = false">Annuler</AppBouton>
      </template>
    </AppFenetre>
    <FenetreTexte :demande="aSignaler" @fermer="aSignaler = null" @fait="aSignaler = null" />
    <FenetreAvis :cible="cibleAvis" @fermer="cibleAvis = null" @enregistre="(cibleAvis = null), charger()" />
  </div>
</template>
