<script setup lang="ts">
// Étape 2 « Votre activité » du dossier de création d'auto-entreprise (.doc/ihm/RM-CREATION-AUTO-ENTREPRISE-IHM.md).
import { computed, ref } from 'vue'
import { messageErreur } from '../../api'
import type { MetierVisible } from '../../composables/useMetiers'
import { type DossierCreation, envoyerEtape, type ReglesMetiers, type Situation, SITE_DE_L_ETAT } from '../../outils/creation'
import { jourCourt } from '../../outils/agenda'
import type { CommuneVisible } from '../../outils/prestataires'
import AppChoixMetier from '../AppChoixMetier.vue'
import ChampsAdresse from '../ChampsAdresse.vue'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppChamp from '../ui/AppChamp.vue'
import AppChoix from '../ui/AppChoix.vue'
import AppSection from '../ui/AppSection.vue'
import AppZoneTexte from '../ui/AppZoneTexte.vue'

const props = defineProps<{ dossier: DossierCreation; regles: ReglesMetiers }>()
const emit = defineEmits<{ enregistre: [situation: Situation]; retour: [] }>()

const d = props.dossier
const aujourdhui = new Date().toLocaleDateString('sv-SE', { timeZone: 'Europe/Paris' })
const metier = ref<MetierVisible | null>(d.metier_id ? { id: d.metier_id, code: '', nom: d.metier ?? '', categorie: '' } : null)
const description = ref(d.description ?? '')
const debut = ref(d.debut_le ?? '')
const lieu = ref<'chez_clients' | 'chez_moi' | 'local'>(d.lieu_travail ?? 'chez_clients')
const localRue = ref(d.local_adresse ?? '')
const localCommune = ref<CommuneVisible | null>(d.local_commune)
const localCodePostal = ref(d.local_code_postal ?? '')
const nomCommercial = ref(d.nom_commercial ?? '')
const enMemeTemps = ref<'aucune' | 'salarie' | 'retraite'>(d.activite_en_meme_temps ?? 'aucune')
const dejaASonCompte = ref<'non' | 'oui'>(d.ancien_siren ? 'oui' : 'non')
const ancienSiren = ref(d.ancien_siren ?? '')
const erreur = ref('')
const envoiEnCours = ref(false)

const reglemente = computed(() => metier.value !== null && props.regles.reglementes.includes(metier.value.id))
const renvoye = computed(() => metier.value !== null && props.regles.renvoyes.includes(metier.value.id))
const domicile = computed(() => (d.adresse_rue ? `${d.adresse_rue}, ${d.code_postal} ${d.commune?.nom ?? ''}` : 'votre adresse (étape 1)'))

async function enregistrer() {
  erreur.value = ''
  if (!metier.value || !debut.value) {
    erreur.value = 'Choisissez votre métier et la date de début.'
    return
  }
  envoiEnCours.value = true
  try {
    const local = lieu.value === 'local'
    emit(
      'enregistre',
      await envoyerEtape('/activite', {
        metier_id: metier.value.id,
        description: description.value,
        debut_le: debut.value,
        lieu_travail: lieu.value,
        local_adresse: local ? localRue.value : null,
        local_commune_id: local ? (localCommune.value?.id ?? null) : null,
        local_code_postal: local ? localCodePostal.value : null,
        nom_commercial: nomCommercial.value.trim() || null,
        activite_en_meme_temps: enMemeTemps.value,
        ancien_siren: dejaASonCompte.value === 'oui' ? ancienSiren.value : null,
      }),
    )
  } catch (e) {
    erreur.value = messageErreur(e)
  } finally {
    envoiEnCours.value = false
  }
}
</script>

<template>
  <AppSection titre="Votre activité">
    <form class="flex flex-col gap-3.5" @submit.prevent="enregistrer">
      <AppChoixMetier v-model="metier" :avec-dossiers="false" etiquette="Votre métier" obligatoire />
      <AppAlerte v-if="renvoye" etat="attente">
        Pour le métier « {{ metier?.nom }} », la démarche se fait sur le site de l'État,
        <a :href="SITE_DE_L_ETAT" target="_blank" rel="noopener" class="underline">formalites.entreprises.gouv.fr</a>.
      </AppAlerte>
      <AppAlerte v-else-if="reglemente" etat="attente">
        {{ metier?.nom }} est un métier réglementé : il faut un diplôme (CAP, BEP…) ou 3 ans d'expérience. rafals vous demandera
        le papier à l'étape 4.
      </AppAlerte>
      <AppZoneTexte
        v-model="description"
        etiquette="Décrivez ce que vous faites"
        obligatoire
        :maximum="250"
        aide="Une phrase simple. ex. « Dépannage et installation de plomberie chez les particuliers ». De 10 à 250 caractères."
      />
      <AppChamp
        v-model="debut"
        etiquette="Date de début"
        type="date"
        obligatoire
        :min="aujourdhui"
        :max="regles.debut_max"
        :aide="`Au plus tôt aujourd'hui, au plus tard le ${jourCourt(regles.debut_max)}.`"
      />
      <AppChoix
        v-model="lieu"
        etiquette="Où travaillez-vous ?"
        obligatoire
        :options="[
          { valeur: 'chez_clients', texte: 'Chez mes clients' },
          { valeur: 'chez_moi', texte: 'Chez moi' },
          { valeur: 'local', texte: 'Dans un local', detail: 'bail demandé' },
        ]"
      />
      <template v-if="lieu === 'local'">
        <h3 class="text-[17px] font-bold">L'adresse de votre local</h3>
        <ChampsAdresse v-model:ligne="localRue" v-model:commune="localCommune" v-model:code-postal="localCodePostal" />
      </template>
      <p v-else class="text-[13.5px] text-texte-doux">Votre entreprise est déclarée à votre adresse : {{ domicile }}.</p>
      <AppChamp v-model="nomCommercial" etiquette="Nom commercial" aide="Facultatif. Sinon, votre entreprise porte votre nom." />
      <AppChoix
        v-model="enMemeTemps"
        etiquette="En même temps, vous êtes…"
        obligatoire
        :options="[
          { valeur: 'aucune', texte: 'Rien d\'autre', detail: 'ou étudiant, sans emploi' },
          { valeur: 'salarie', texte: 'Salarié' },
          { valeur: 'retraite', texte: 'Retraité' },
        ]"
      />
      <AppChoix
        v-model="dejaASonCompte"
        etiquette="Avez-vous déjà été à votre compte ?"
        obligatoire
        :options="[{ valeur: 'non', texte: 'Non, jamais' }, { valeur: 'oui', texte: 'Oui' }]"
      />
      <AppChamp
        v-if="dejaASonCompte === 'oui'"
        v-model="ancienSiren"
        etiquette="Ancien numéro SIREN"
        obligatoire
        inputmode="numeric"
        aide="9 chiffres. Si cette entreprise existe encore, ne la recréez pas : ajoutez son SIRET à votre profil."
      />
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <div class="flex flex-wrap justify-between gap-2">
        <AppBouton variante="secondaire" @click="emit('retour')">Retour</AppBouton>
        <AppBouton
          v-if="renvoye"
          variante="verrouille"
          raison-verrou="Pour ce métier, la démarche se fait sur le site de l'État."
        >
          Enregistrer et continuer
        </AppBouton>
        <AppBouton v-else type="submit" :occupe="envoiEnCours">Enregistrer et continuer</AppBouton>
      </div>
    </form>
  </AppSection>
</template>
