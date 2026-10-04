<script setup lang="ts">
// « Vous avez déjà une entreprise ? » (demande de Raphael du 04/10/2026) : on n'en recrée pas, le SIRET est ajouté au
// profil (même vérification que dans « Mon activité »). Sans profil : on part créer le profil, le SIRET déjà rempli.
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../../api'
import { useCompte } from '../../composables/useCompte'
import { useMessage } from '../../composables/useMessage'
import type { Situation } from '../../outils/creation'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppChamp from '../ui/AppChamp.vue'
import AppSection from '../ui/AppSection.vue'

const props = defineProps<{ aUnProfil: boolean }>()
const emit = defineEmits<{ enregistre: [situation: Situation] }>()
const routeur = useRouter()
const { compte } = useCompte()
const { afficherMessage } = useMessage()
const siret = ref('')
const erreur = ref('')
const envoiEnCours = ref(false)

async function ajouter() {
  erreur.value = ''
  const chiffres = siret.value.replace(/\s/g, '')
  if (!/^\d{14}$/.test(chiffres)) {
    erreur.value = 'Le SIRET fait 14 chiffres (ex. 912 345 678 00012).'
    return
  }
  if (!compte.value) {
    routeur.push({ path: '/connexion', query: { retour: '/creer-mon-auto-entreprise' } })
    return
  }
  if (!props.aUnProfil) {
    routeur.push({ path: '/proposer', query: { siret: chiffres } })
    return
  }
  envoiEnCours.value = true
  try {
    const situation = await appelerServeur<Situation>('/api/moi/prestataire/siret', { siret: chiffres })
    afficherMessage('SIRET ajouté à votre profil.')
    emit('enregistre', situation)
  } catch (e) {
    erreur.value = messageErreur(e)
  } finally {
    envoiEnCours.value = false
  }
}
</script>

<template>
  <AppSection titre="Vous avez déjà une entreprise ?">
    <p>
      Auto-entreprise, entreprise individuelle ou société : ne créez rien. Écrivez son numéro SIRET, rafals le vérifie tout
      seul et l'ajoute à votre profil.
    </p>
    <form class="flex flex-col gap-3.5" @submit.prevent="ajouter">
      <AppChamp
        v-model="siret"
        etiquette="Numéro SIRET"
        obligatoire
        inputmode="numeric"
        placeholder="ex. 912 345 678 00012"
        aide="14 chiffres, sur vos papiers de l'INSEE ou de l'URSSAF."
      />
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <div><AppBouton type="submit" variante="secondaire" :occupe="envoiEnCours">Ajouter mon entreprise</AppBouton></div>
    </form>
  </AppSection>
</template>
