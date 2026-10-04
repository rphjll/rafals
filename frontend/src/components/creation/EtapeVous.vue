<script setup lang="ts">
// Étape 1 « Vous » du dossier de création d'auto-entreprise (.doc/ihm/RM-CREATION-AUTO-ENTREPRISE-IHM.md).
import { computed, ref } from 'vue'
import { messageErreur } from '../../api'
import { type DossierCreation, envoyerEtape, numeroSecuLisible, type Situation, SITUATIONS, SITE_DE_L_ETAT } from '../../outils/creation'
import type { CommuneVisible } from '../../outils/prestataires'
import AppChoixCommune from '../AppChoixCommune.vue'
import ChampsAdresse from '../ChampsAdresse.vue'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppCase from '../ui/AppCase.vue'
import AppChamp from '../ui/AppChamp.vue'
import AppChoix from '../ui/AppChoix.vue'
import AppSection from '../ui/AppSection.vue'
import AppSelection from '../ui/AppSelection.vue'

const props = defineProps<{ dossier: DossierCreation }>()
const emit = defineEmits<{ enregistre: [situation: Situation]; retour: [] }>()

const d = props.dossier
const civilite = ref<'monsieur' | 'madame'>(d.civilite ?? 'monsieur')
const nom = ref(d.nom_naissance ?? '')
const nomUsage = ref(d.nom_usage ?? '')
const prenoms = ref(d.prenoms ?? '')
const naissance = ref(d.naissance_le ?? '')
const neALEtranger = ref(Boolean(d.naissance_pays))
const villeNaissance = ref<CommuneVisible | null>(d.naissance_commune)
const paysNaissance = ref(d.naissance_pays ?? '')
const nationalite = ref<'francaise' | 'union_europeenne' | 'autre'>(d.nationalite ?? 'francaise')
const situation = ref<number | null>(SITUATIONS.find((s) => s.cle === d.situation_famille)?.valeur ?? null)
const conjointTravaille = ref<'non' | 'oui'>('non')
const numeroSecu = ref(d.numero_secu ? numeroSecuLisible(d.numero_secu) : '')
const rue = ref(d.adresse_rue ?? '')
const commune = ref<CommuneVisible | null>(d.commune)
const codePostal = ref(d.code_postal ?? '')
const mail = ref(d.mail ?? '')
const telephone = ref(d.telephone ?? '')
const erreur = ref('')
const envoiEnCours = ref(false)

const cleSituation = computed(() => SITUATIONS.find((s) => s.valeur === situation.value)?.cle ?? '')
const enCouple = computed(() => ['marie', 'pacse'].includes(cleSituation.value))

async function enregistrer() {
  erreur.value = ''
  if (!naissance.value || !situation.value || !commune.value || !codePostal.value) {
    erreur.value = 'Remplissez tous les champs marqués d\'une étoile (date de naissance, situation de famille, ville, code postal).'
    return
  }
  envoiEnCours.value = true
  try {
    emit(
      'enregistre',
      await envoyerEtape('/vous', {
        civilite: civilite.value,
        nom_naissance: nom.value,
        nom_usage: nomUsage.value.trim() || null,
        prenoms: prenoms.value,
        naissance_le: naissance.value,
        naissance_commune_id: neALEtranger.value ? null : (villeNaissance.value?.id ?? null),
        naissance_pays: neALEtranger.value ? paysNaissance.value : null,
        nationalite: nationalite.value,
        situation_famille: cleSituation.value,
        conjoint_travaille: enCouple.value && conjointTravaille.value === 'oui',
        numero_secu: numeroSecu.value,
        adresse_rue: rue.value,
        commune_id: commune.value.id,
        code_postal: codePostal.value,
        mail: mail.value,
        telephone: telephone.value,
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
  <AppSection titre="Vous">
    <form class="flex flex-col gap-3.5" @submit.prevent="enregistrer">
      <p class="text-[13.5px] text-texte-doux">Écrivez exactement comme sur votre pièce d'identité.</p>
      <AppChoix
        v-model="civilite"
        etiquette="Civilité"
        obligatoire
        :options="[{ valeur: 'monsieur', texte: 'Monsieur' }, { valeur: 'madame', texte: 'Madame' }]"
      />
      <div class="grid gap-3.5 sm:grid-cols-2">
        <AppChamp v-model="nom" etiquette="Nom de naissance" obligatoire autocomplete="family-name" />
        <AppChamp v-model="nomUsage" etiquette="Nom d'usage" aide="Facultatif. ex. nom d'époux ou d'épouse" />
      </div>
      <AppChamp v-model="prenoms" etiquette="Prénoms" obligatoire aide="Tous vos prénoms, séparés par une virgule. ex. Karim, Youssef" />
      <AppChamp v-model="naissance" etiquette="Date de naissance" type="date" obligatoire autocomplete="bday" />
      <AppChamp v-if="neALEtranger" v-model="paysNaissance" etiquette="Pays de naissance" obligatoire placeholder="ex. Maroc" />
      <AppChoixCommune v-else v-model="villeNaissance" etiquette="Ville de naissance" obligatoire />
      <AppCase v-model="neALEtranger" texte="Je suis né(e) à l'étranger" />
      <AppChoix
        v-model="nationalite"
        etiquette="Nationalité"
        obligatoire
        :options="[
          { valeur: 'francaise', texte: 'Française' },
          { valeur: 'union_europeenne', texte: 'Union européenne' },
          { valeur: 'autre', texte: 'Autre pays', detail: 'titre de séjour demandé' },
        ]"
      />
      <AppSelection v-model="situation" etiquette="Situation de famille" obligatoire :options="SITUATIONS" />
      <template v-if="enCouple">
        <AppChoix
          v-model="conjointTravaille"
          etiquette="Votre conjoint travaille-t-il avec vous dans l'entreprise ?"
          obligatoire
          :options="[{ valeur: 'non', texte: 'Non' }, { valeur: 'oui', texte: 'Oui' }]"
        />
        <AppAlerte v-if="conjointTravaille === 'oui'" etat="attente">
          Ce cas est particulier : la démarche se fait sur le site de l'État,
          <a :href="SITE_DE_L_ETAT" target="_blank" rel="noopener" class="underline">formalites.entreprises.gouv.fr</a>.
        </AppAlerte>
      </template>
      <AppChamp
        v-model="numeroSecu"
        etiquette="Numéro de sécurité sociale"
        obligatoire
        inputmode="numeric"
        placeholder="ex. 1 98 03 33 063 123 52"
        aide="Les 15 chiffres de votre carte Vitale. Il sert à vous rattacher à l'URSSAF ; rafals l'efface dès que votre dossier est fini."
      />
      <h3 class="text-[17px] font-bold">Votre adresse</h3>
      <ChampsAdresse v-model:ligne="rue" v-model:commune="commune" v-model:code-postal="codePostal" />
      <div class="grid gap-3.5 sm:grid-cols-2">
        <AppChamp v-model="mail" etiquette="Mail" type="email" obligatoire autocomplete="email" />
        <AppChamp v-model="telephone" etiquette="Téléphone" type="tel" obligatoire autocomplete="tel" />
      </div>
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <div class="flex flex-wrap justify-between gap-2">
        <AppBouton variante="secondaire" @click="emit('retour')">Retour</AppBouton>
        <AppBouton type="submit" :occupe="envoiEnCours">Enregistrer et continuer</AppBouton>
      </div>
    </form>
  </AppSection>
</template>
