<script setup lang="ts">
// Choix d'un métier (.doc/ihm/RM-CHOIX-METIER-IHM.md) : par les premières lettres, ou par dossier.
// Utilisé par « Trouver un prestataire », « Proposer mes services » et la fenêtre « Remplacer » de l'Administration.
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'
import { type Dossier, type MetierVisible, useMetiers } from '../composables/useMetiers'
import AppAlerte from './ui/AppAlerte.vue'
import AppBouton from './ui/AppBouton.vue'
import AppChamp from './ui/AppChamp.vue'
import AppElementChoisi from './ui/AppElementChoisi.vue'
import AppFenetre from './ui/AppFenetre.vue'
import AppRecherche from './ui/AppRecherche.vue'

const props = withDefaults(defineProps<{ avecDossiers?: boolean; etiquette?: string; obligatoire?: boolean }>(), {
  avecDossiers: true,
  etiquette: 'Tapez les premières lettres',
  obligatoire: false,
})
const choisi = defineModel<MetierVisible | null>({ default: null })

const routeur = useRouter()
const { compte } = useCompte()
const { afficherMessage } = useMessage()
const { dossiers, chargerDossiers, rechercher } = useMetiers()
const texte = ref('')
const dossierOuvert = ref<Dossier | null>(null)

onMounted(() => {
  if (props.avecDossiers) chargerDossiers()
})

function choisir(metier: MetierVisible) {
  choisi.value = metier
  dossierOuvert.value = null
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
    <AppElementChoisi v-if="choisi" :texte="choisi.nom" :detail="choisi.categorie" @changer="choisi = null" />

    <template v-else>
      <AppRecherche
        v-model:texte="texte"
        :etiquette="etiquette"
        :obligatoire="obligatoire"
        :chercher="rechercher"
        :libelle="(m: MetierVisible) => m.nom"
        :detail="(m: MetierVisible) => m.categorie"
        :cle="(m: MetierVisible) => m.id"
        placeholder="ex. plom, fuite, coiffeuse, piano…"
        aide="Flèches ↑ ↓ puis Entrée au clavier, ou un clic. Les accents ne comptent pas."
        @choisir="choisir"
      >
        <template #aucun-resultat>
          <p class="flex flex-wrap items-center gap-2 text-[13px] text-texte-doux">
            Aucun métier ne correspond.
            <AppBouton variante="secondaire" @click="ouvrirProposition">Proposer un métier</AppBouton>
          </p>
        </template>
      </AppRecherche>

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
              class="flex flex-col gap-1 carte p-3.5 text-left hover:border-primaire"
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
