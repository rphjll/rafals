<script setup lang="ts">
// Inscription (.doc/ihm/RM-INSCRIPTION-IHM.md). Règles : RM-COMPTES.md.
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppCarte from '../components/ui/AppCarte.vue'
import AppChamp from '../components/ui/AppChamp.vue'
import AppSeparateur from '../components/ui/AppSeparateur.vue'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'

const routeur = useRouter()
const { afficherMessage } = useMessage()
const { renvoyerLienVerification } = useCompte()
const formulaire = reactive({ prenom: '', nom: '', email: '', telephone: '', date_naissance: '', mot_de_passe: '' })
const erreur = ref('')
const envoiEnCours = ref(false)
const adresseInscrite = ref('')

async function creerCompte() {
  erreur.value = ''
  envoiEnCours.value = true
  try {
    const compte = await appelerServeur<{ email: string }>('/api/comptes', formulaire)
    adresseInscrite.value = compte.email
  } catch (e) {
    erreur.value = messageErreur(e)
  } finally {
    envoiEnCours.value = false
  }
}

async function renvoyerLien() {
  try {
    afficherMessage(await renvoyerLienVerification(adresseInscrite.value))
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}
</script>

<template>
  <AppCarte v-if="adresseInscrite" titre="Vérifiez votre boîte mail">
    <p>
      Un lien vient d'être envoyé à <b>{{ adresseInscrite }}</b>. Cliquez dessus pour finir votre inscription (il est
      valable 7 jours).
    </p>
    <AppAlerte etat="attente">
      Tant que votre adresse n'est pas vérifiée, vous pouvez vous connecter, mais pas réserver ni publier.
    </AppAlerte>
    <AppBouton pleine-largeur @click="routeur.push('/connexion')">Se connecter</AppBouton>
    <AppBouton variante="secondaire" pleine-largeur @click="renvoyerLien">Je n'ai rien reçu : renvoyer le lien</AppBouton>
  </AppCarte>

  <AppCarte v-else titre="Créer mon compte" intro="Pour réserver un prestataire, ou proposer vos services.">
    <form class="flex flex-col gap-4" @submit.prevent="creerCompte">
      <div class="grid gap-3 sm:grid-cols-2">
        <AppChamp v-model="formulaire.prenom" etiquette="Prénom" obligatoire autocomplete="given-name" />
        <AppChamp v-model="formulaire.nom" etiquette="Nom" obligatoire autocomplete="family-name" />
      </div>
      <AppChamp v-model="formulaire.email" etiquette="Adresse mail" type="email" obligatoire autocomplete="email" />
      <AppChamp
        v-model="formulaire.telephone"
        etiquette="Téléphone"
        type="tel"
        obligatoire
        autocomplete="tel"
        aide="Visible seulement des prestataires chez qui vous réservez."
      />
      <AppChamp
        v-model="formulaire.date_naissance"
        etiquette="Date de naissance"
        type="date"
        obligatoire
        autocomplete="bday"
        aide="Il faut avoir au moins 16 ans."
      />
      <AppChamp
        v-model="formulaire.mot_de_passe"
        etiquette="Mot de passe"
        type="password"
        obligatoire
        autocomplete="new-password"
        aide="Au moins 10 caractères (ex. MaisonBleue44)."
      />
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <AppBouton type="submit" pleine-largeur :occupe="envoiEnCours">Créer mon compte</AppBouton>
    </form>
    <AppSeparateur>déjà inscrit ?</AppSeparateur>
    <AppBouton variante="secondaire" pleine-largeur @click="routeur.push('/connexion')">Se connecter</AppBouton>
  </AppCarte>
</template>
