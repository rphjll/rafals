<script setup lang="ts">
// « Proposer mes services » / « Mon activité » (.doc/ihm/RM-PROPOSER-IHM.md).
// Sans profil : le formulaire de création. Avec un profil : la fiche, et le formulaire pour la modifier.
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur } from '../api'
import FicheActivite from '../components/prestataire/FicheActivite.vue'
import FormulaireProfil from '../components/prestataire/FormulaireProfil.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppCarte from '../components/ui/AppCarte.vue'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'
import type { ProfilPrestataire } from '../outils/prestataires'

const routeur = useRouter()
const { compte, chargementFait, chargerCompte } = useCompte()
const { afficherMessage } = useMessage()
const profil = ref<ProfilPrestataire | null>(null)
const profilCharge = ref(false)
const enModification = ref(false)

async function chargerProfil() {
  if (!compte.value) return // pas (encore) connecté : la page attend
  if (compte.value.prestataire_id) profil.value = await appelerServeur<ProfilPrestataire>('/api/moi/prestataire')
  profilCharge.value = true
}
onMounted(chargerProfil)
watch(compte, chargerProfil)

async function enregistre(nouveau: ProfilPrestataire) {
  const creation = profil.value === null
  profil.value = nouveau
  enModification.value = false
  afficherMessage(creation ? 'Votre profil de prestataire est créé.' : 'Profil enregistré.')
  if (creation) await chargerCompte() // le menu affiche maintenant « Mon activité »
}
</script>

<template>
  <AppCarte v-if="chargementFait && !compte" titre="Proposer mes services" intro="Connectez-vous pour proposer vos services.">
    <AppBouton pleine-largeur @click="routeur.push('/connexion')">Se connecter</AppBouton>
    <AppBouton variante="secondaire" pleine-largeur @click="routeur.push('/inscription')">Créer mon compte</AppBouton>
  </AppCarte>

  <div v-else-if="compte && profilCharge" class="mx-auto flex w-full max-w-[720px] flex-col gap-4">
    <template v-if="profil">
      <h1 class="text-[28px] font-bold">Mon activité</h1>
      <FormulaireProfil v-if="enModification" :existant="profil" @enregistre="enregistre" @annuler="enModification = false" />
      <FicheActivite v-else :profil="profil" @maj="(p) => (profil = p)" @modifier="enModification = true" />
    </template>

    <template v-else>
      <h1 class="text-[28px] font-bold">Proposer mes services</h1>
      <AppAlerte v-if="!compte.email_verifie" etat="attente">
        Vérifiez d'abord votre adresse mail (lien reçu par mail), puis revenez proposer vos services.
      </AppAlerte>
      <AppAlerte v-else-if="!compte.peut_reserver_ou_publier" etat="attente">
        Il faut d'abord que l'accord de tes parents soit accepté.
        <AppBouton variante="secondaire" @click="routeur.push('/compte')">Mon compte</AppBouton>
      </AppAlerte>
      <template v-else>
        <p class="text-texte-doux">
          Créez votre profil de prestataire : les clients vous trouveront dès que vous publierez votre première annonce.
        </p>
        <FormulaireProfil @enregistre="enregistre" />
        <p class="text-[14px] text-texte-doux">
          Pas encore d'entreprise ?
          <AppBouton variante="secondaire" @click="routeur.push('/creer-mon-auto-entreprise')">Créer mon auto-entreprise : le guide</AppBouton>
        </p>
      </template>
    </template>
  </div>
</template>
