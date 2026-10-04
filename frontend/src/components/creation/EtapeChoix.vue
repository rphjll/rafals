<script setup lang="ts">
// Étape 3 « Vos choix » du dossier de création d'auto-entreprise (.doc/ihm/RM-CREATION-AUTO-ENTREPRISE-IHM.md).
import { ref } from 'vue'
import { messageErreur } from '../../api'
import { type DossierCreation, envoyerEtape, type Situation } from '../../outils/creation'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppCase from '../ui/AppCase.vue'
import AppChoix from '../ui/AppChoix.vue'
import AppSection from '../ui/AppSection.vue'

const props = defineProps<{ dossier: DossierCreation }>()
const emit = defineEmits<{ enregistre: [situation: Situation]; retour: [] }>()

const d = props.dossier
const periodicite = ref<'trimestre' | 'mois'>(d.periodicite ?? 'trimestre')
const impot = ref<'non' | 'oui'>(d.impot_avec_cotisations ? 'oui' : 'non')
const acre = ref(d.acre_demandee ?? true)
const adresseNonPublique = ref(d.adresse_non_publique ?? true)
const erreur = ref('')
const envoiEnCours = ref(false)

async function enregistrer() {
  erreur.value = ''
  envoiEnCours.value = true
  try {
    emit(
      'enregistre',
      await envoyerEtape('/choix', {
        periodicite: periodicite.value,
        impot_avec_cotisations: impot.value === 'oui',
        acre_demandee: acre.value,
        adresse_non_publique: adresseNonPublique.value,
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
  <AppSection titre="Vos choix">
    <form class="flex flex-col gap-3.5" @submit.prevent="enregistrer">
      <p class="text-[13.5px] text-texte-doux">Si vous ne savez pas, gardez le choix conseillé : il se change plus tard.</p>
      <AppChoix
        v-model="periodicite"
        etiquette="Vous déclarerez à l'URSSAF l'argent encaissé…"
        obligatoire
        :options="[
          { valeur: 'trimestre', texte: 'Chaque trimestre', detail: 'conseillé : 4 déclarations par an' },
          { valeur: 'mois', texte: 'Chaque mois', detail: '12 déclarations par an' },
        ]"
      />
      <AppChoix
        v-model="impot"
        etiquette="Payer l'impôt en même temps que les cotisations ?"
        obligatoire
        :options="[
          { valeur: 'non', texte: 'Non', detail: 'conseillé' },
          { valeur: 'oui', texte: 'Oui', detail: 'possible seulement sous un certain revenu' },
        ]"
      />
      <div>
        <AppCase v-model="acre" texte="Demander la réduction de début d'activité (ACRE)" />
        <p class="text-[13px] text-texte-doux">Des cotisations moins chères la première année, si vous y avez droit. C'est l'URSSAF qui décide.</p>
      </div>
      <div>
        <AppCase v-model="adresseNonPublique" texte="Ne pas rendre mon adresse publique" />
        <p class="text-[13px] text-texte-doux">Votre adresse personnelle n'apparaîtra pas dans les annuaires d'entreprises.</p>
      </div>
      <AppAlerte etat="neutre">Déjà choisi pour vous, car c'est la règle des auto-entreprises : pas de TVA à facturer, et le régime « micro ».</AppAlerte>
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <div class="flex flex-wrap justify-between gap-2">
        <AppBouton variante="secondaire" @click="emit('retour')">Retour</AppBouton>
        <AppBouton type="submit" :occupe="envoiEnCours">Enregistrer et continuer</AppBouton>
      </div>
    </form>
  </AppSection>
</template>
