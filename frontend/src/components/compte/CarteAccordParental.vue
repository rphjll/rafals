<script setup lang="ts">
// Mon compte › Accord de tes parents, pour les 16-17 ans (.doc/ihm/RM-COMPTE-IHM.md ; RM-COMPTES.md).
import { onMounted, ref } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useCompte, type CompteVisible } from '../../composables/useCompte'
import { useMessage } from '../../composables/useMessage'
import { age, formaterDateHeure } from '../../outils/dates'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBadge from '../ui/AppBadge.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppChampFichier from '../ui/AppChampFichier.vue'
import AppSection from '../ui/AppSection.vue'

interface EtatAccord {
  necessaire: boolean
  statut: 'en_attente' | 'accepte' | 'refuse' | null
  motif_refus: string | null
  depose_le: string | null
}

defineProps<{ compte: CompteVisible }>()
const { chargerCompte } = useCompte()
const { afficherMessage } = useMessage()
const accord = ref<EtatAccord | null>(null)
const fichier = ref<File | null>(null)
const erreur = ref('')
const envoiEnCours = ref(false)

async function chargerAccord() {
  accord.value = await appelerServeur<EtatAccord>('/api/moi/accord-parental')
}
onMounted(chargerAccord)

async function envoyerAccord() {
  erreur.value = ''
  if (!fichier.value) {
    erreur.value = 'Choisis d\'abord le fichier de l\'accord signé.'
    return
  }
  envoiEnCours.value = true
  try {
    const formulaire = new FormData()
    formulaire.append('fichier', fichier.value)
    accord.value = await appelerServeur<EtatAccord>('/api/moi/accord-parental', formulaire)
    fichier.value = null
    afficherMessage("Accord envoyé : il attend la vérification de l'administrateur.")
  } catch (e) {
    erreur.value = messageErreur(e)
  } finally {
    envoiEnCours.value = false
  }
}

async function actualiser() {
  await chargerCompte()
  await chargerAccord()
}
</script>

<template>
  <AppSection v-if="accord" titre="Accord de tes parents">
    <template v-if="accord.statut === 'accepte'">
      <div><AppBadge etat="ok">Accepté</AppBadge></div>
      <p class="text-texte-doux">Tu peux prendre des rendez-vous et proposer tes services.</p>
    </template>

    <template v-else-if="accord.statut === 'en_attente'">
      <div><AppBadge etat="attente">En attente de vérification</AppBadge></div>
      <p class="text-texte-doux">Envoyé le {{ formaterDateHeure(accord.depose_le ?? '') }}. Tu verras la réponse ici.</p>
      <div><AppBouton variante="secondaire" @click="actualiser">Actualiser</AppBouton></div>
    </template>

    <template v-else>
      <AppAlerte etat="attente">
        Tu as {{ age(compte.date_naissance ?? '') }} ans : pour prendre un rendez-vous ou proposer tes services, il faut l'accord signé de
        tes parents, vérifié par rafals.
      </AppAlerte>
      <AppAlerte v-if="accord.statut === 'refuse'">
        Ton accord a été refusé : « {{ accord.motif_refus }} ». Tu peux en envoyer un nouveau.
      </AppAlerte>
      <form class="flex flex-col gap-3.5" @submit.prevent="envoyerAccord">
        <AppChampFichier
          v-model="fichier"
          etiquette="Accord signé de tes parents"
          aide="PDF, JPG ou PNG, 5 Mo au maximum (ex. une photo de la lettre signée)"
          accepte="application/pdf,image/jpeg,image/png"
        />
        <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
        <div><AppBouton type="submit" :occupe="envoiEnCours">Envoyer l'accord</AppBouton></div>
      </form>
    </template>
  </AppSection>
</template>
