<script setup lang="ts">
// Choix d'un métier (.doc/ihm/RM-CHOIX-METIER-IHM.md) : par les premières lettres, ou par dossier.
// Servira aussi à « Proposer mes services » (lot 2.5) et à la recherche (niveau 4).
import { onMounted, ref, useId, watch } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'
import { type Dossier, type MetierVisible, useMetiers } from '../composables/useMetiers'
import AppAlerte from './ui/AppAlerte.vue'
import AppBouton from './ui/AppBouton.vue'
import AppChamp from './ui/AppChamp.vue'
import AppFenetre from './ui/AppFenetre.vue'

const props = withDefaults(defineProps<{ avecDossiers?: boolean; etiquette?: string }>(), {
  avecDossiers: true,
  etiquette: 'Tapez les premières lettres',
})
const choisi = defineModel<MetierVisible | null>({ default: null })

const routeur = useRouter()
const { compte } = useCompte()
const { afficherMessage } = useMessage()
const { dossiers, chargerDossiers, rechercher } = useMetiers()
const id = useId()

const texte = ref('')
const resultats = ref<MetierVisible[]>([])
const actif = ref(0)
const dossierOuvert = ref<Dossier | null>(null)
let minuteur: ReturnType<typeof setTimeout> | undefined

onMounted(() => {
  if (props.avecDossiers) chargerDossiers()
})

// On attend une courte pause dans la frappe avant d'interroger le serveur
watch(texte, (valeur) => {
  clearTimeout(minuteur)
  minuteur = setTimeout(async () => {
    resultats.value = valeur.trim() ? await rechercher(valeur) : []
    actif.value = 0
  }, 150)
})

function choisir(metier: MetierVisible) {
  choisi.value = metier
  texte.value = ''
  resultats.value = []
  dossierOuvert.value = null
}

function clavier(evenement: KeyboardEvent) {
  if (!resultats.value.length) return
  if (evenement.key === 'ArrowDown') actif.value = Math.min(resultats.value.length - 1, actif.value + 1)
  else if (evenement.key === 'ArrowUp') actif.value = Math.max(0, actif.value - 1)
  else if (evenement.key === 'Enter') choisir(resultats.value[actif.value])
  else return
  evenement.preventDefault()
}

// ---------- Proposer un métier ----------
const fenetreOuverte = ref(false)
const nomPropose = ref('')
const erreurProposition = ref('')

function ouvrirProposition() {
  nomPropose.value = texte.value.trim()
  erreurProposition.value = ''
  fenetreOuverte.value = true
}

async function envoyerProposition() {
  erreurProposition.value = ''
  try {
    const reponse = await appelerServeur<{ message: string }>('/api/metiers/propositions', { nom: nomPropose.value })
    fenetreOuverte.value = false
    afficherMessage(reponse.message)
  } catch (e) {
    erreurProposition.value = messageErreur(e)
  }
}
</script>

<template>
  <div class="flex flex-col gap-3">
    <div v-if="choisi" class="flex flex-wrap items-center gap-2.5 rounded-rafals bg-ok-doux px-3 py-2.5 font-semibold text-ok">
      ✓ {{ choisi.nom }} <span class="text-[13px] font-medium">({{ choisi.categorie }})</span>
      <span class="ml-auto"><AppBouton variante="secondaire" @click="choisi = null">Changer</AppBouton></span>
    </div>

    <template v-else>
      <div class="flex flex-col gap-1.5">
        <label :for="id" class="text-[13px] font-semibold">{{ etiquette }}</label>
        <input
          :id="id"
          v-model="texte"
          autocomplete="off"
          placeholder="ex. plom, fuite, coiffeuse, piano…"
          role="combobox"
          :aria-expanded="resultats.length > 0"
          class="min-h-[42px] rounded-rafals border border-bord bg-fond px-3 py-2.5 text-texte outline-none focus:border-primaire focus:ring-2 focus:ring-primaire"
          @keydown="clavier"
        />
        <div v-if="resultats.length" class="overflow-hidden rounded-rafals border border-bord bg-surface" role="listbox">
          <button
            v-for="(metier, i) in resultats"
            :key="metier.id"
            type="button"
            role="option"
            :aria-selected="i === actif"
            class="flex w-full justify-between gap-2.5 border-t border-bord px-3 py-2.5 text-left first:border-t-0 hover:bg-primaire-doux"
            :class="i === actif ? 'bg-primaire-doux' : ''"
            @click="choisir(metier)"
          >
            {{ metier.nom }} <small class="text-texte-doux">{{ metier.categorie }}</small>
          </button>
        </div>
        <p v-else-if="texte.trim()" class="flex flex-wrap items-center gap-2 text-[13px] text-texte-doux">
          Aucun métier ne correspond.
          <AppBouton variante="secondaire" @click="ouvrirProposition">Proposer un métier</AppBouton>
        </p>
        <p class="text-[13px] text-texte-doux">Flèches ↑ ↓ puis Entrée au clavier, ou un clic. Les accents ne comptent pas.</p>
      </div>

      <div v-if="avecDossiers" class="flex flex-col gap-3">
        <template v-if="dossierOuvert">
          <div class="flex flex-wrap items-center gap-2.5">
            <AppBouton variante="secondaire" @click="dossierOuvert = null">← Tous les dossiers</AppBouton>
            <h3 class="text-lg font-bold">{{ dossierOuvert.nom }}</h3>
          </div>
          <div class="overflow-hidden rounded-rafals border border-bord bg-surface">
            <button
              v-for="metier in dossierOuvert.metiers"
              :key="metier.id"
              type="button"
              class="block w-full border-t border-bord px-3 py-2.5 text-left first:border-t-0 hover:bg-primaire-doux"
              @click="choisir(metier)"
            >
              {{ metier.nom }}
            </button>
          </div>
        </template>
        <template v-else>
          <h3 class="text-lg font-bold">Ou parcourir par dossier</h3>
          <div class="grid grid-cols-[repeat(auto-fill,minmax(190px,1fr))] gap-2.5">
            <button
              v-for="dossier in dossiers"
              :key="dossier.id"
              type="button"
              class="flex flex-col gap-1 rounded-rafals border border-bord bg-surface p-3.5 text-left hover:border-primaire"
              @click="dossierOuvert = dossier"
            >
              <b>{{ dossier.nom }}</b>
              <small class="text-texte-doux">{{ dossier.metiers.slice(0, 3).map((m) => m.nom).join(', ') }}…</small>
            </button>
          </div>
        </template>
        <p class="flex flex-wrap items-center gap-2 text-[13px] text-texte-doux">
          Votre métier n'est pas dans la liste ?
          <AppBouton variante="secondaire" @click="ouvrirProposition">Proposer un métier</AppBouton>
        </p>
      </div>
    </template>

    <AppFenetre :ouverte="fenetreOuverte" titre="Proposer un métier" @fermer="fenetreOuverte = false">
      <div v-if="compte" class="flex flex-col gap-3">
        <p>L'administrateur le vérifiera. En attendant, choisissez « Autre ».</p>
        <AppChamp v-model="nomPropose" etiquette="Nom du métier" obligatoire aide="Ex. « Cerf-voliste »" />
        <AppAlerte v-if="erreurProposition">{{ erreurProposition }}</AppAlerte>
      </div>
      <p v-else>Connectez-vous pour proposer un métier.</p>
      <template #pied>
        <AppBouton v-if="compte" @click="envoyerProposition">Envoyer</AppBouton>
        <AppBouton v-else @click="routeur.push('/connexion')">Se connecter</AppBouton>
        <AppBouton variante="secondaire" @click="fenetreOuverte = false">Annuler</AppBouton>
      </template>
    </AppFenetre>
  </div>
</template>
