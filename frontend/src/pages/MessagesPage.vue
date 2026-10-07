<script setup lang="ts">
// Messages (.doc/ihm/RM-MESSAGES-IHM.md ; RM-MESSAGERIE.md) : /messages = la liste de mes conversations ;
// /messages/12 = le fil avec Karim (ou Marie D.), ses propositions, et la zone pour écrire.
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { appelerServeur, ErreurServeur, messageErreur } from '../api'
import FenetreTexte, { type DemandeTexte } from '../components/FenetreTexte.vue'
import CarteProposition from '../components/messagerie/CarteProposition.vue'
import FenetreProposition from '../components/messagerie/FenetreProposition.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBadge from '../components/ui/AppBadge.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppFenetre from '../components/ui/AppFenetre.vue'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'
import { useNonLus } from '../composables/useNonLus'
import { formaterDateHeure } from '../outils/dates'
import { type DemandeVisible, texteBudget, texteQuand } from '../outils/demandes'
import {
  type ConversationResumee, type ConversationVisible, type MessageVisible, type PropositionVisible, repeteUneCarte,
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
const erreur = ref('')

const texte = ref('')
const photos = ref<File[]>([])
const champPhotos = ref<HTMLInputElement | null>(null)
const erreurEnvoi = ref('')
const envoiEnCours = ref(false)
const basDuFil = ref<HTMLElement | null>(null)

const fenetreProposition = ref(false)
const aBloquer = ref(false)
const aSignaler = ref<DemandeTexte | null>(null)

// Messages et propositions mêlés, du plus ancien au plus récent
type Element = { cle: string; quand: string; message?: MessageVisible; proposition?: PropositionVisible }
const fil = computed<Element[]>(() => {
  const messages = (conversation.value?.messages ?? [])
    .filter((m) => !(m.genre === 'information' && repeteUneCarte(m.texte)))
    .map((m) => ({ cle: `m${m.id}`, quand: m.cree_le, message: m }))
  const cartes = propositions.value.map((p) => ({ cle: `p${p.id}`, quand: p.cree_le, proposition: p }))
  return [...messages, ...cartes].sort((a, b) => a.quand.localeCompare(b.quand))
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
      const [lue, sesPropositions, sesDemandes] = await Promise.all([
        appelerServeur<ConversationVisible>(`/api/conversations/${id}`),
        appelerServeur<PropositionVisible[]>(`/api/conversations/${id}/propositions`),
        appelerServeur<DemandeVisible[]>(`/api/conversations/${id}/demandes`),
      ])
      if (id !== conversationId.value) return // on a changé de page pendant la lecture
      conversation.value = lue
      propositions.value = sesPropositions
      demandes.value = sesDemandes
      if (defiler || lue.messages.length > avant) nextTick(() => basDuFil.value?.scrollIntoView({ block: 'end' }))
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
  charger(true)
})

function choisirPhotos(evenement: Event) {
  const champ = evenement.target as HTMLInputElement
  erreurEnvoi.value = ''
  photos.value = [...photos.value, ...Array.from(champ.files ?? [])].slice(0, PHOTOS_MAX)
  champ.value = ''
}

async function envoyer() {
  if (!conversation.value || (!texte.value.trim() && !photos.value.length)) return
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
  <div class="mx-auto flex max-w-[760px] flex-col gap-5">
    <template v-if="chargementFait && !compte">
      <h1 class="text-[28px] font-bold">Messages</h1>
      <AppAlerte etat="neutre">Connectez-vous pour lire vos messages.</AppAlerte>
      <div><AppBouton @click="routeur.push('/connexion')">Se connecter</AppBouton></div>
    </template>

    <!-- ---------- La liste ---------- -->
    <template v-else-if="conversationId === null">
      <h1 class="text-[28px] font-bold">Messages</h1>
      <p class="text-texte-doux">Une seule conversation par personne : tous vos échanges au même endroit.</p>
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <ul v-if="liste?.length" class="flex flex-col overflow-hidden rounded-rafals border border-bord bg-surface">
        <li v-for="c in liste" :key="c.id" class="border-t border-bord first:border-t-0">
          <RouterLink :to="`/messages/${c.id}`" class="flex min-h-[64px] items-center gap-3 px-4 py-3 hover:bg-primaire-doux">
            <div class="flex min-w-0 flex-1 flex-col">
              <span class="flex flex-wrap items-center gap-2">
                <b>{{ c.avec }}</b>
                <span v-if="c.non_lus" class="rounded-full bg-erreur px-2 py-0.5 text-xs font-bold text-sur-etat">{{ c.non_lus }}</span>
                <AppBadge v-if="c.bloquee" etat="neutre">bloquée</AppBadge>
              </span>
              <span class="truncate text-[14px] text-texte-doux">{{ c.apercu || 'Aucun message pour l’instant.' }}</span>
            </div>
            <span class="shrink-0 text-[13px] text-texte-doux">{{ formaterDateHeure(c.dernier_message_le) }} ›</span>
          </RouterLink>
        </li>
      </ul>
      <p v-else-if="liste" class="rounded-rafals border border-bord bg-surface p-5 text-texte-doux">
        Aucune conversation. Publiez une demande sur l'accueil, ou répondez à une demande si vous proposez vos services.
      </p>
    </template>

    <!-- ---------- Une conversation ---------- -->
    <template v-else>
      <div class="flex flex-wrap items-center justify-between gap-2">
        <AppBouton variante="secondaire" @click="routeur.push('/messages')">‹ Messages</AppBouton>
        <div v-if="conversation" class="flex flex-wrap gap-2">
          <AppBouton variante="secondaire" @click="signaler">Signaler…</AppBouton>
          <AppBouton v-if="!conversation.bloquee" variante="danger" @click="aBloquer = true">Bloquer…</AppBouton>
          <AppBouton v-else-if="conversation.bloquee_par_moi" variante="secondaire" @click="bloquer(false)">Débloquer</AppBouton>
        </div>
      </div>
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>

      <section v-if="conversation" class="flex flex-col gap-4 rounded-rafals border border-bord bg-surface p-4">
        <h1 class="text-xl font-bold">{{ conversation.avec }}</h1>

        <!-- Les demandes dont on parle, rappelées en haut -->
        <p v-for="d in demandes" :key="d.id" class="rounded-rafals border border-dashed border-bord px-3 py-2 text-[14px] text-texte-doux">
          Demande : <b class="text-texte">{{ d.titre }}</b> · {{ d.ville }} · {{ texteQuand(d) }}<template v-if="d.budget_centimes">
            · budget {{ texteBudget(d.budget_centimes) }}</template>
        </p>

        <div class="flex flex-col gap-3" aria-live="polite">
          <template v-for="element in fil" :key="element.cle">
            <CarteProposition
              v-if="element.proposition"
              :proposition="element.proposition"
              :cote="conversation.cote"
              :avec="conversation.avec"
              @change="charger(true)"
            />
            <p v-else-if="element.message?.genre === 'information'" class="self-center rounded-full bg-neutre-doux px-3 py-1 text-center text-[13px] text-texte-doux">
              {{ element.message.texte }}
            </p>
            <div
              v-else-if="element.message"
              class="flex max-w-[85%] flex-col gap-1.5 rounded-rafals px-3.5 py-2.5"
              :class="element.message.de_moi ? 'self-end bg-primaire-doux' : 'self-start bg-neutre-doux'"
            >
              <span v-if="element.message.texte" class="whitespace-pre-line break-words">{{ element.message.texte }}</span>
              <div v-if="element.message.nombre_photos" class="flex flex-wrap gap-2">
                <a v-for="n in element.message.nombre_photos" :key="n" :href="`/api/messages/${element.message.id}/photos/${n}`" target="_blank" rel="noopener">
                  <img :src="`/api/messages/${element.message.id}/photos/${n}`" :alt="`Photo ${n} du message`" class="size-24 rounded-rafals border border-bord object-cover" />
                </a>
              </div>
              <small class="text-[12px] text-texte-doux">
                {{ formaterDateHeure(element.message.cree_le) }}<template v-if="element.message.de_moi"> · {{ element.message.lu ? 'lu' : 'envoyé' }}</template>
              </small>
            </div>
          </template>
          <p v-if="!fil.length" class="text-texte-doux">Aucun message pour l'instant : écrivez le premier.</p>
          <span ref="basDuFil" />
        </div>

        <AppAlerte v-if="conversation.bloquee" etat="neutre">Conversation bloquée : plus aucun message ne passe.</AppAlerte>
        <form v-else class="flex flex-col gap-2" @submit.prevent="envoyer">
          <label for="message" class="text-[13px] font-semibold">Votre message</label>
          <textarea
            id="message"
            v-model="texte"
            rows="3"
            maxlength="2000"
            placeholder="Écrire un message…"
            class="min-h-[84px] resize-y rounded-rafals border border-bord bg-fond px-3 py-2.5 text-texte outline-none focus:border-primaire focus:ring-2 focus:ring-primaire"
          />
          <ul v-if="photos.length" class="flex flex-wrap gap-1.5">
            <li v-for="(photo, rang) in photos" :key="rang" class="inline-flex items-center gap-1.5 rounded-full bg-neutre-doux py-0.5 pr-1 pl-2.5 text-sm">
              {{ photo.name }}
              <button type="button" class="size-7 rounded-full font-bold hover:bg-erreur-doux" :aria-label="`Enlever ${photo.name}`" @click="photos.splice(rang, 1)">×</button>
            </li>
          </ul>
          <AppAlerte v-if="erreurEnvoi">{{ erreurEnvoi }}</AppAlerte>
          <div class="flex flex-wrap gap-2">
            <AppBouton type="submit" :occupe="envoiEnCours">Envoyer</AppBouton>
            <AppBouton v-if="photos.length < PHOTOS_MAX" variante="secondaire" @click="champPhotos?.click()">
              Joindre une photo ({{ photos.length }} / {{ PHOTOS_MAX }})
            </AppBouton>
            <AppBouton v-if="conversation.cote === 'prestataire'" variante="secondaire" @click="fenetreProposition = true">
              Faire une proposition…
            </AppBouton>
          </div>
          <input ref="champPhotos" type="file" accept="image/jpeg,image/png" multiple class="sr-only" aria-label="Photos à joindre" @change="choisirPhotos" />
        </form>
        <p v-if="conversation.coordonnees_masquees" class="text-[13px] text-texte-doux">
          Téléphone et mail sont masqués dans les messages tant qu'il n'y a pas de rendez-vous entre vous.
        </p>
      </section>
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
        <AppBouton variante="danger" @click="bloquer(true)">Bloquer</AppBouton>
        <AppBouton variante="secondaire" @click="aBloquer = false">Annuler</AppBouton>
      </template>
    </AppFenetre>
    <FenetreTexte :demande="aSignaler" @fermer="aSignaler = null" @fait="aSignaler = null" />
  </div>
</template>
