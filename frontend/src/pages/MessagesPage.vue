<script setup lang="ts">
// Messages (.doc/ihm/RM-MESSAGES-IHM.md ; RM-MESSAGERIE.md) : /messages = la liste de mes conversations ;
// /messages/12 = le fil avec Karim (ou Marie D.), ses propositions, et la zone pour écrire.
// Ordinateur : la liste reste à gauche, le fil est à droite. Téléphone : l'un ou l'autre.
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
import AppPicto from '../components/ui/AppPicto.vue'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'
import { useNonLus } from '../composables/useNonLus'
import { formaterDateHeure } from '../outils/dates'
import { type DemandeVisible, texteBudget, texteQuand } from '../outils/demandes'
import { initialesDe } from '../outils/noms'
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
// [Plus…] montre « Signaler… » et « Bloquer… », rangés pour ne pas encombrer le haut du fil
const plusOuvert = ref(false)
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
  <div class="flex flex-col gap-5">
    <h1 class="text-[clamp(28px,4.5vw,40px)] font-black">Messages</h1>
    <template v-if="chargementFait && !compte">
      <AppAlerte etat="neutre">Connectez-vous pour lire vos messages.</AppAlerte>
      <div><AppBouton @click="routeur.push('/connexion')">Se connecter</AppBouton></div>
    </template>

    <template v-else>
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <div class="carte grid overflow-hidden md:grid-cols-[300px_1fr]">
        <!-- ---------- La liste (téléphone : cachée quand un fil est ouvert) ---------- -->
        <div class="min-w-0 flex-col gap-1 p-2.5 md:flex md:border-r-2 md:border-fond" :class="conversationId === null ? 'flex' : 'hidden'">
          <RouterLink
            v-for="c in liste ?? []"
            :key="c.id"
            :to="`/messages/${c.id}`"
            class="flex min-h-[64px] items-center gap-3 rounded-rafals px-3 py-2.5 hover:bg-fond"
            :class="c.id === conversationId ? 'bg-fond' : ''"
            :aria-current="c.id === conversationId ? 'page' : undefined"
          >
            <span class="grid size-11 shrink-0 place-items-center rounded-full bg-primaire-doux font-bold text-primaire" aria-hidden="true">
              {{ initialesDe(c.avec) }}
            </span>
            <span class="flex min-w-0 flex-1 flex-col">
              <span class="flex items-center gap-2">
                <b class="truncate">{{ c.avec }}</b>
                <AppBadge v-if="c.bloquee" etat="neutre">bloquée</AppBadge>
              </span>
              <span class="truncate text-[14px] text-texte-doux">{{ c.apercu || 'Aucun message pour l’instant.' }}</span>
              <span class="text-[12px] text-texte-doux">{{ formaterDateHeure(c.dernier_message_le) }}</span>
            </span>
            <span v-if="c.non_lus" class="shrink-0 rounded-full bg-erreur px-2 py-0.5 text-xs font-bold text-sur-etat">{{ c.non_lus }}</span>
          </RouterLink>
          <p v-if="liste && !liste.length" class="p-3 text-texte-doux">
            Aucune conversation. Publiez une demande sur l'accueil, ou répondez à une demande si vous proposez vos services.
          </p>
        </div>

        <!-- ---------- Le fil (téléphone : caché tant qu'aucun n'est ouvert) ---------- -->
        <section class="min-w-0 flex-col md:flex md:min-h-[520px]" :class="conversationId === null ? 'hidden' : 'flex'">
          <p v-if="conversationId === null" class="m-auto p-6 text-center text-texte-doux">
            Choisissez une conversation dans la liste. Une seule conversation par personne : tous vos échanges au même endroit.
          </p>
          <template v-else-if="conversation">
            <div class="flex flex-wrap items-center gap-2.5 border-b-2 border-fond px-4 py-3">
              <RouterLink
                to="/messages"
                class="grid size-[42px] shrink-0 place-items-center rounded-full bg-secondaire-fond text-xl font-bold text-primaire md:hidden"
                aria-label="Retour à la liste des messages"
              >
                ‹
              </RouterLink>
              <span class="grid size-11 shrink-0 place-items-center rounded-full bg-primaire-doux font-bold text-primaire" aria-hidden="true">
                {{ initialesDe(conversation.avec) }}
              </span>
              <h2 class="mr-auto min-w-0 text-xl font-extrabold">{{ conversation.avec }}</h2>
              <AppBouton variante="secondaire" @click="plusOuvert = !plusOuvert">Plus…</AppBouton>
              <div v-if="plusOuvert" class="flex w-full flex-wrap justify-end gap-2">
                <AppBouton variante="secondaire" @click="signaler">Signaler…</AppBouton>
                <AppBouton v-if="!conversation.bloquee" variante="danger" @click="aBloquer = true">Bloquer…</AppBouton>
                <AppBouton v-else-if="conversation.bloquee_par_moi" variante="secondaire" @click="bloquer(false)">Débloquer</AppBouton>
              </div>
            </div>

            <!-- Les demandes dont on parle, rappelées en haut -->
            <div v-if="demandes.length" class="flex flex-col gap-2 px-4 pt-3">
              <p v-for="d in demandes" :key="d.id" class="rounded-rafals bg-fond px-3 py-2 text-[14px] text-texte-doux">
                Demande : <b class="text-texte">{{ d.titre }}</b> · {{ d.ville }} · {{ texteQuand(d) }}<template v-if="d.budget_centimes">
                  · budget {{ texteBudget(d.budget_centimes) }}</template>
              </p>
            </div>

            <div class="flex flex-1 flex-col gap-3 p-4" aria-live="polite">
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
                  class="flex max-w-[85%] flex-col gap-1.5 px-4 py-2.5"
                  :class="element.message.de_moi ? 'self-end rounded-[20px_20px_6px_20px] bg-primaire text-primaire-texte' : 'self-start rounded-[20px_20px_20px_6px] bg-fond'"
                >
                  <span v-if="element.message.texte" class="break-words whitespace-pre-line">{{ element.message.texte }}</span>
                  <div v-if="element.message.nombre_photos" class="flex flex-wrap gap-2">
                    <a v-for="n in element.message.nombre_photos" :key="n" :href="`/api/messages/${element.message.id}/photos/${n}`" target="_blank" rel="noopener">
                      <img :src="`/api/messages/${element.message.id}/photos/${n}`" :alt="`Photo ${n} du message`" class="size-24 rounded-rafals object-cover" />
                    </a>
                  </div>
                  <small class="text-[12px] opacity-80">
                    {{ formaterDateHeure(element.message.cree_le) }}<template v-if="element.message.de_moi"> · {{ element.message.lu ? 'lu' : 'envoyé' }}</template>
                  </small>
                </div>
              </template>
              <p v-if="!fil.length" class="text-texte-doux">Aucun message pour l'instant : écrivez le premier.</p>
              <span ref="basDuFil" />
            </div>

            <div v-if="conversation.bloquee" class="p-4">
              <AppAlerte etat="neutre">Conversation bloquée : plus aucun message ne passe.</AppAlerte>
            </div>
            <form v-else class="flex flex-col gap-2 border-t-2 border-fond p-3" @submit.prevent="envoyer">
              <ul v-if="photos.length" class="flex flex-wrap gap-1.5">
                <li v-for="(photo, rang) in photos" :key="rang" class="inline-flex items-center gap-1.5 rounded-full bg-neutre-doux py-0.5 pr-1 pl-2.5 text-sm">
                  {{ photo.name }}
                  <button type="button" class="size-7 rounded-full font-bold hover:bg-erreur-doux" :aria-label="`Enlever ${photo.name}`" @click="photos.splice(rang, 1)">×</button>
                </li>
              </ul>
              <AppAlerte v-if="erreurEnvoi">{{ erreurEnvoi }}</AppAlerte>
              <!-- Une seule ligne : photo, texte, envoyer (deux boutons ronds à pictogramme, propres à cette ligne) -->
              <div class="flex items-end gap-2">
                <button
                  v-if="photos.length < PHOTOS_MAX"
                  type="button"
                  class="grid size-[46px] shrink-0 place-items-center rounded-full bg-secondaire-fond text-primaire hover:brightness-95"
                  :aria-label="`Joindre une photo (${photos.length} / ${PHOTOS_MAX})`"
                  @click="champPhotos?.click()"
                >
                  <AppPicto code="appareil" :taille="22" />
                </button>
                <label for="message" class="sr-only">Votre message</label>
                <textarea
                  id="message"
                  v-model="texte"
                  rows="1"
                  maxlength="2000"
                  placeholder="Écrire un message…"
                  class="min-h-[46px] min-w-0 flex-1 resize-y rounded-rafals border border-bord bg-fond px-3.5 py-2.5 text-texte outline-none focus:border-primaire focus:ring-2 focus:ring-primaire"
                />
                <button
                  type="submit"
                  class="grid size-[46px] shrink-0 place-items-center rounded-full bg-primaire text-primaire-texte hover:brightness-110"
                  :class="envoiEnCours ? 'cursor-wait opacity-70' : ''"
                  :aria-busy="envoiEnCours || undefined"
                  aria-label="Envoyer"
                >
                  <AppPicto code="envoyer" :taille="22" />
                </button>
              </div>
              <div v-if="conversation.cote === 'prestataire'">
                <AppBouton variante="accent" @click="fenetreProposition = true">Faire une proposition…</AppBouton>
              </div>
              <input ref="champPhotos" type="file" accept="image/jpeg,image/png" multiple class="sr-only" aria-label="Photos à joindre" @change="choisirPhotos" />
            </form>
            <p v-if="conversation.coordonnees_masquees" class="px-4 pb-3 text-[13px] text-texte-doux">
              Téléphone et mail sont masqués dans les messages tant qu'il n'y a pas de rendez-vous entre vous.
            </p>
          </template>
        </section>
      </div>
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
