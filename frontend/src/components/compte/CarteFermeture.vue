<script setup lang="ts">
// Mon compte › Fermer mon compte (.doc/ihm/RM-COMPTE-IHM.md ; RM-CLIENTS.md) : mot de passe retapé, puis effacement définitif.
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../../api'
import { useCompte } from '../../composables/useCompte'
import { useMessage } from '../../composables/useMessage'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppChamp from '../ui/AppChamp.vue'
import AppFenetre from '../ui/AppFenetre.vue'
import AppSection from '../ui/AppSection.vue'

const routeur = useRouter()
const { chargerCompte } = useCompte()
const { afficherMessage } = useMessage()
const ouverte = ref(false)
const motDePasse = ref('')
const erreur = ref('')
const envoiEnCours = ref(false)

function ouvrir() {
  motDePasse.value = ''
  erreur.value = ''
  ouverte.value = true
}

async function fermer() {
  erreur.value = ''
  envoiEnCours.value = true
  try {
    const reponse = await appelerServeur<{ message: string }>('/api/moi/fermer', { mot_de_passe: motDePasse.value })
    ouverte.value = false
    await chargerCompte() // plus personne n'est connecté
    await routeur.push('/')
    afficherMessage(reponse.message)
  } catch (e) {
    erreur.value = messageErreur(e)
  } finally {
    envoiEnCours.value = false
  }
}
</script>

<template>
  <AppSection titre="Fermer mon compte" danger>
    <p class="text-[13.5px] text-texte-doux">Vos informations personnelles seront effacées. C'est définitif.</p>
    <div><AppBouton variante="danger" @click="ouvrir">Fermer mon compte…</AppBouton></div>
  </AppSection>

  <AppFenetre :ouverte="ouverte" titre="Fermer votre compte ?" @fermer="ouverte = false">
    <form class="flex flex-col gap-3" @submit.prevent="fermer">
      <p>
        Votre nom, votre adresse mail, votre téléphone, votre date de naissance et votre adresse seront effacés, et vous
        serez déconnecté. C'est définitif.
      </p>
      <AppChamp v-model="motDePasse" etiquette="Votre mot de passe" obligatoire type="password" autocomplete="current-password" />
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    </form>
    <template #pied>
      <AppBouton variante="danger" :occupe="envoiEnCours" @click="fermer">Fermer définitivement</AppBouton>
      <AppBouton variante="secondaire" @click="ouverte = false">Annuler</AppBouton>
    </template>
  </AppFenetre>
</template>
