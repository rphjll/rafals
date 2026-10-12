<script setup lang="ts">
// Suivi du dossier de création d'auto-entreprise une fois envoyé (.doc/ihm/RM-CREATION-AUTO-ENTREPRISE-IHM.md) :
// où il en est, la correction demandée par l'administration, le SIRET reçu.
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { jourCourt } from '../../outils/agenda'
import { badgeDossier, type DossierCreation, envoyerEtape, type Situation } from '../../outils/creation'
import { formaterDateHeure } from '../../outils/dates'
import { siretLisible } from '../../outils/prestataires'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBadge from '../ui/AppBadge.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppSection from '../ui/AppSection.vue'
import LignePapier from './LignePapier.vue'

const props = defineProps<{ dossier: DossierCreation; aUnProfil: boolean }>()
const emit = defineEmits<{ enregistre: [situation: Situation]; corrigerReponses: []; recommencer: [] }>()
const routeur = useRouter()
const { afficherMessage } = useMessage()
const erreur = ref('')
const envoiEnCours = ref(false)

const d = computed(() => props.dossier)
const badge = computed(() => badgeDossier(d.value.statut))
const titre = computed(() => d.value.nom_commercial ?? `${d.value.prenoms?.split(',')[0] ?? ''} ${d.value.nom_naissance ?? ''}`.trim())
const enCours = computed(() => ['envoye', 'en_examen', 'a_corriger'].includes(d.value.statut))
const manquants = computed(() => Object.values(d.value.manque).flat())
const papiers = computed(() => d.value.pieces.filter((p) => !p.deposee_par_rafals))
const etapes = computed(() => [
  {
    etat: 'faite',
    titre: 'Dossier envoyé',
    texte: `le ${d.value.envoye_le ? formaterDateHeure(d.value.envoye_le) : '…'} · numéro de dossier ${d.value.guichet_numero ?? '…'}`,
  },
  {
    etat: d.value.statut === 'accepte' ? 'faite' : 'ici',
    titre: "L'administration examine votre dossier",
    texte: 'En général 1 à 4 semaines. rafals regarde tout seul chaque heure et vous écrit dès qu\'il y a du nouveau.',
  },
  {
    etat: d.value.statut === 'accepte' ? 'faite' : '',
    titre: 'Dossier accepté : vous recevez votre SIRET',
    texte: 'rafals l\'ajoute tout seul à votre profil : le paiement par carte et les devis deviennent possibles.',
  },
])

async function faire(chemin: string, reussite: string) {
  erreur.value = ''
  envoiEnCours.value = true
  try {
    const situation = await envoyerEtape(chemin)
    if (reussite) afficherMessage(reussite)
    emit('enregistre', situation)
  } catch (e) {
    erreur.value = messageErreur(e)
  } finally {
    envoiEnCours.value = false
  }
}
</script>

<template>
  <AppSection>
    <div class="flex flex-wrap items-center justify-between gap-2">
      <h2 class="text-xl font-bold">{{ titre }}</h2>
      <AppBadge :etat="badge.etat">{{ badge.texte }}</AppBadge>
    </div>
    <AppAlerte v-if="dossier.demonstration" etat="attente">
      Mode démonstration : rien n'a été envoyé à l'État, aucune entreprise n'est créée.
    </AppAlerte>

    <!-- Une correction est demandée -->
    <template v-if="dossier.statut === 'a_corriger'">
      <AppAlerte>
        L'administration demande une correction{{ dossier.corriger_avant_le ? ` avant le ${jourCourt(dossier.corriger_avant_le)}` : '' }} :
        « {{ dossier.motif }} »
      </AppAlerte>
      <LignePapier v-for="piece in papiers" :key="piece.sorte" :piece="piece" modifiable @enregistre="(s) => emit('enregistre', s)" />
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <div class="flex flex-wrap justify-between gap-2">
        <AppBouton variante="secondaire" @click="emit('corrigerReponses')">Corriger mes réponses</AppBouton>
        <AppBouton v-if="manquants.length" variante="verrouille" :raison-verrou="`Il manque : ${manquants.join(', ')}.`">Envoyer la correction</AppBouton>
        <AppBouton v-else :occupe="envoiEnCours" @click="faire('/correction', 'Correction envoyée.')">Envoyer la correction</AppBouton>
      </div>
      <p class="text-[13px] text-texte-doux">Sans correction avant la date limite, l'administration ferme le dossier.</p>
    </template>

    <!-- Envoyé, en cours d'examen, accepté -->
    <template v-else-if="enCours || dossier.statut === 'accepte'">
      <ol class="flex flex-col gap-3.5">
        <li v-for="etape in etapes" :key="etape.titre" class="flex items-start gap-3">
          <b
            class="grid h-7 w-7 flex-none place-items-center rounded-full"
            :class="etape.etat === 'faite' ? 'bg-ok-doux text-ok' : etape.etat === 'ici' ? 'bg-attente-doux text-attente' : 'bg-neutre-doux text-neutre'"
          >
            {{ etape.etat === 'faite' ? '✓' : etape.etat === 'ici' ? '…' : '' }}
          </b>
          <div>
            <strong>{{ etape.titre }}</strong>
            <p class="text-[13.5px] text-texte-doux">{{ etape.texte }}</p>
          </div>
        </li>
      </ol>
      <template v-if="dossier.statut === 'accepte'">
        <AppAlerte etat="ok">
          Votre auto-entreprise est créée. SIRET : <b>{{ siretLisible(dossier.siret_recu) }}</b>.
          {{ dossier.demonstration ? '(faux numéro de démonstration, non ajouté au profil)' : aUnProfil ? 'Il est ajouté à votre profil.' : 'Gardez-le pour créer votre profil.' }}
        </AppAlerte>
        <div class="flex flex-wrap gap-2">
          <AppBouton v-if="aUnProfil" @click="routeur.push('/profil')">Activer le paiement par carte</AppBouton>
          <AppBouton v-else @click="routeur.push({ path: '/proposer', query: dossier.demonstration ? {} : { siret: dossier.siret_recu ?? '' } })">
            Proposer mes services
          </AppBouton>
          <AppBouton v-if="aUnProfil" variante="secondaire" @click="routeur.push('/demarches')">Voir mes démarches</AppBouton>
        </div>
      </template>
      <template v-else>
        <AppAlerte etat="neutre">En attendant, vous pouvez déjà faire des propositions payées en espèces.</AppAlerte>
        <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
        <div><AppBouton variante="secondaire" :occupe="envoiEnCours" @click="faire('/actualiser', '')">Actualiser</AppBouton></div>
      </template>
    </template>

    <!-- Refusé ou fermé -->
    <template v-else>
      <AppAlerte>{{ dossier.motif }}</AppAlerte>
      <p class="text-[13.5px] text-texte-doux">Votre numéro de sécurité sociale et vos papiers ont été effacés de rafals.</p>
      <div><AppBouton @click="emit('recommencer')">Recommencer un dossier</AppBouton></div>
    </template>
  </AppSection>
</template>
