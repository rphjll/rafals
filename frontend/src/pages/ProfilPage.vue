<script setup lang="ts">
// « Mon profil » (.doc/ihm/RM-PROFIL-IHM.md) : depuis le 07/10/2026, une seule page réunit l'ancien « Mon profil »
// (la fiche du prestataire, RM-PROPOSER-IHM.md) et l'ancien « Mon compte » (RM-COMPTE-IHM.md), l'un sous l'autre.
// Prestataire : sa fiche d'abord, puis son compte. Client : son compte, avec une carte « Proposer mes services ».
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { appelerServeur } from '../api'
import CarteAdresse from '../components/CarteAdresse.vue'
import CarteAbsences from '../components/compte/CarteAbsences.vue'
import CarteAccordParental from '../components/compte/CarteAccordParental.vue'
import CarteDonnees from '../components/compte/CarteDonnees.vue'
import CarteFermeture from '../components/compte/CarteFermeture.vue'
import CarteInformations from '../components/compte/CarteInformations.vue'
import CartePaiements from '../components/compte/CartePaiements.vue'
import FicheActivite from '../components/prestataire/FicheActivite.vue'
import FormulaireProfil from '../components/prestataire/FormulaireProfil.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppCarte from '../components/ui/AppCarte.vue'
import AppSection from '../components/ui/AppSection.vue'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'
import type { ProfilPrestataire } from '../outils/prestataires'

const route = useRoute()
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

// Client : le formulaire « Proposer mes services » s'ouvre tout seul quand on arrive par ce bouton
// (/profil?proposer=1) ou de « Créer mon auto-entreprise » (/profil?siret=91234567800017)
const veutProposer = computed(() => 'proposer' in route.query || 'siret' in route.query)
const formulaireOuvert = ref(veutProposer.value)
watch(veutProposer, (oui) => oui && (formulaireOuvert.value = true))

async function enregistre(nouveau: ProfilPrestataire) {
  const creation = profil.value === null
  profil.value = nouveau
  enModification.value = false
  afficherMessage(creation ? 'Votre profil de prestataire est créé.' : 'Profil enregistré.')
  if (creation) await chargerCompte() // le menu n'affiche plus « Proposer mes services »
}
</script>

<template>
  <AppCarte v-if="chargementFait && !compte" titre="Mon profil" intro="Connectez-vous pour voir votre profil ou proposer vos services.">
    <AppBouton pleine-largeur @click="routeur.push('/connexion')">Se connecter</AppBouton>
    <AppBouton variante="secondaire" pleine-largeur @click="routeur.push('/inscription')">Créer mon compte</AppBouton>
  </AppCarte>

  <div v-else-if="compte && profilCharge" class="mx-auto flex w-full max-w-[720px] flex-col gap-[18px]">
    <h1 class="text-[28px] font-bold">Mon profil</h1>

    <!-- Prestataire : sa fiche (ou le formulaire pour la modifier) en premier -->
    <template v-if="profil">
      <FormulaireProfil v-if="enModification" :existant="profil" @enregistre="enregistre" @annuler="enModification = false" />
      <FicheActivite v-else :profil="profil" @maj="(p) => (profil = p)" @modifier="enModification = true" />
    </template>

    <!-- Client : de quoi devenir prestataire, replié tant qu'il ne le demande pas -->
    <template v-else>
      <AppSection titre="Proposer mes services">
        <AppAlerte v-if="!compte.email_verifie" etat="attente">
          Vérifiez d'abord votre adresse mail (lien reçu par mail), puis revenez proposer vos services.
        </AppAlerte>
        <AppAlerte v-else-if="!compte.peut_reserver_ou_publier" etat="attente">
          Il faut d'abord que l'accord de tes parents soit accepté (carte « Accord de tes parents », plus bas).
        </AppAlerte>
        <template v-else-if="formulaireOuvert">
          <p class="text-texte-doux">Créez votre profil de prestataire : les clients vous trouveront dès qu'il sera rempli.</p>
          <FormulaireProfil @enregistre="enregistre" />
          <p class="text-[14px] text-texte-doux">
            Pas encore d'entreprise ?
            <AppBouton variante="secondaire" @click="routeur.push('/creer-mon-auto-entreprise')">Créer mon auto-entreprise</AppBouton>
          </p>
        </template>
        <template v-else>
          <p class="text-texte-doux">Vous faites du ménage, du jardinage, de la plomberie… ? Créez votre profil de prestataire.</p>
          <div><AppBouton @click="formulaireOuvert = true">Proposer mes services</AppBouton></div>
        </template>
      </AppSection>
    </template>

    <CarteInformations :compte="compte" />
    <CarteAccordParental v-if="compte.accord_parental_necessaire" :compte="compte" />
    <CarteAdresse
      titre="Mon adresse"
      chemin="/api/moi/adresse"
      :texte-vide="
        profil
          ? 'Aucune adresse enregistrée : ajoutez-la si des clients viennent chez vous (salon, atelier…) ou pour réserver un service à domicile.'
          : 'Aucune adresse enregistrée : elle vous sera demandée quand vous réserverez un service à domicile.'
      "
      :note="profil ? 'C’est aussi l’adresse de votre local. Les clients voient seulement la ville ; la rue, après avoir réservé.' : undefined"
      texte-ajouter="Ajouter mon adresse"
      texte-effacer="Effacer mon adresse"
    />
    <CarteAbsences />
    <CartePaiements />
    <CarteDonnees />
    <CarteFermeture />
  </div>
</template>
