<script setup lang="ts">
// Administration › Propositions de métiers (.doc/ihm/RM-ADMINISTRATION-IHM.md). Règles : RM-METIERS.md.
import { computed, onMounted, ref } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { type MetierVisible, useMetiers } from '../../composables/useMetiers'
import { formaterDateHeure } from '../../outils/dates'
import AppChoixMetier from '../AppChoixMetier.vue'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppFenetre from '../ui/AppFenetre.vue'
import AppSelection from '../ui/AppSelection.vue'

interface Proposition {
  id: number
  nom_propose: string
  propose_le: string
  propose_par: string
}

const emit = defineEmits<{ maj: [] }>()
const { afficherMessage } = useMessage()
const { dossiers, chargerDossiers } = useMetiers()
const propositions = ref<Proposition[]>([])
const erreur = ref('')

async function charger() {
  try {
    propositions.value = await appelerServeur<Proposition[]>('/api/admin/propositions')
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
onMounted(() => {
  charger()
  chargerDossiers()
})

const optionsDossiers = computed(() => dossiers.value.map((d) => ({ valeur: d.id, texte: d.nom })))

// Une seule fenêtre, deux usages : accepter (choisir le dossier) ou remplacer (choisir un métier existant)
const enCours = ref<{ proposition: Proposition; mode: 'acceptee' | 'remplacee' } | null>(null)
const dossierChoisi = ref<number | null>(null)
const metierChoisi = ref<MetierVisible | null>(null)
const erreurFenetre = ref('')

function ouvrir(proposition: Proposition, mode: 'acceptee' | 'remplacee') {
  enCours.value = { proposition, mode }
  dossierChoisi.value = null
  metierChoisi.value = null
  erreurFenetre.value = ''
}

async function decider(proposition: Proposition, decision: 'acceptee' | 'remplacee' | 'refusee') {
  const reponse = await appelerServeur(`/api/admin/propositions/${proposition.id}/decision`, {
    decision,
    categorie_id: dossierChoisi.value,
    metier_id: metierChoisi.value?.id ?? null,
  })
  await charger()
  await chargerDossiers(true) // un métier a pu être créé
  emit('maj')
  return reponse
}

async function valider() {
  const courant = enCours.value
  if (!courant) return
  try {
    await decider(courant.proposition, courant.mode)
    enCours.value = null
    afficherMessage(
      courant.mode === 'acceptee'
        ? `« ${courant.proposition.nom_propose} » ajouté à la liste des métiers.`
        : `Remplacé par « ${metierChoisi.value?.nom} ».`,
    )
  } catch (e) {
    erreurFenetre.value = messageErreur(e)
  }
}

async function refuser(proposition: Proposition) {
  try {
    await decider(proposition, 'refusee')
    afficherMessage(`Proposition « ${proposition.nom_propose} » refusée.`)
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}
</script>

<template>
  <div class="flex flex-col gap-3">
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <p v-if="!propositions.length" class="text-texte-doux">Aucune proposition de métier pour l'instant.</p>
    <div
      v-for="proposition in propositions"
      :key="proposition.id"
      class="grid items-center gap-3 rounded-rafals border border-bord bg-surface p-3.5 sm:grid-cols-[1fr_auto]"
    >
      <div>
        <b>« {{ proposition.nom_propose }} »</b> · proposé par {{ proposition.propose_par }} · le
        {{ formaterDateHeure(proposition.propose_le) }}
      </div>
      <div class="flex flex-wrap gap-2">
        <AppBouton @click="ouvrir(proposition, 'acceptee')">Accepter…</AppBouton>
        <AppBouton variante="secondaire" @click="ouvrir(proposition, 'remplacee')">Remplacer…</AppBouton>
        <AppBouton variante="danger" @click="refuser(proposition)">Refuser</AppBouton>
      </div>
    </div>

    <AppFenetre
      :ouverte="enCours !== null"
      :titre="
        enCours?.mode === 'acceptee'
          ? `Accepter « ${enCours?.proposition.nom_propose} » ?`
          : `Remplacer « ${enCours?.proposition.nom_propose} »`
      "
      @fermer="enCours = null"
    >
      <div class="flex flex-col gap-3">
        <template v-if="enCours?.mode === 'acceptee'">
          <p>Le métier sera créé et proposé à tous.</p>
          <AppSelection v-model="dossierChoisi" etiquette="Dossier où le ranger" :options="optionsDossiers" obligatoire />
        </template>
        <template v-else>
          <p>par un métier qui existe déjà. Le nom proposé deviendra un de ses mots-clés.</p>
          <AppChoixMetier v-model="metierChoisi" :avec-dossiers="false" etiquette="Métier existant *" />
        </template>
        <AppAlerte v-if="erreurFenetre">{{ erreurFenetre }}</AppAlerte>
      </div>
      <template #pied>
        <AppBouton @click="valider">{{ enCours?.mode === 'acceptee' ? 'Accepter' : 'Remplacer' }}</AppBouton>
        <AppBouton variante="secondaire" @click="enCours = null">Annuler</AppBouton>
      </template>
    </AppFenetre>
  </div>
</template>
