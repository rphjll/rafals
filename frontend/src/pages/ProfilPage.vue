<script setup lang="ts">
// « Mon profil » (.doc/ihm/RM-PROFIL-IHM.md) : depuis le 07/10/2026, une seule page réunit l'ancien « Mon profil »
// (la fiche du prestataire, RM-PROPOSER-IHM.md) et l'ancien « Mon compte » (RM-COMPTE-IHM.md).
// Façon Instagram depuis le 21/10/2026 : photo et chiffres en haut. Prestataire : onglets Photos · Mon activité ·
// Mon compte (FicheActivite). Client : ses chiffres, la carte « Proposer mes services », puis son compte.
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { appelerServeur } from '../api'
import AvatarPrestataire from '../components/prestataire/AvatarPrestataire.vue'
import FicheActivite from '../components/prestataire/FicheActivite.vue'
import FormulaireProfil from '../components/prestataire/FormulaireProfil.vue'
import EnteteProfil from '../components/profil/EnteteProfil.vue'
import LignesCompte from '../components/profil/LignesCompte.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppCarte from '../components/ui/AppCarte.vue'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'
import type { ProfilPrestataire } from '../outils/prestataires'
import { chiffreOuTiret, compterAbonnements } from '../outils/profil'
import type { RendezVousVisible } from '../outils/rendez_vous'

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
  else chargerChiffresClient()
  profilCharge.value = true
}
onMounted(chargerProfil)
watch(compte, chargerProfil)

// ---------- Client : ses chiffres (rendez-vous, avis donnés, abonnements) ----------
const rendezVous = ref<RendezVousVisible[] | null>(null)
const abonnements = ref<number | null>(null)
async function chargerChiffresClient() {
  abonnements.value = await compterAbonnements()
  try {
    rendezVous.value = await appelerServeur<RendezVousVisible[]>('/api/moi/rendez-vous')
  } catch {
    rendezVous.value = null
  }
}
const chiffresClient = computed(() => [
  chiffreOuTiret(rendezVous.value?.filter((r) => r.statut === 'confirme').length ?? null, 'rendez-vous'),
  chiffreOuTiret(rendezVous.value?.filter((r) => r.avis && !r.avis.retire).length ?? null, 'avis donné'),
  chiffreOuTiret(abonnements.value, 'abonnement'),
])
const lignesClient = ref<InstanceType<typeof LignesCompte> | null>(null)

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

  <div v-else-if="compte && profilCharge" class="mx-auto flex w-full max-w-[640px] flex-col gap-[18px]">
    <!-- Prestataire : son profil façon Instagram (ou le formulaire pour le modifier) -->
    <template v-if="profil">
      <FormulaireProfil v-if="enModification" :existant="profil" @enregistre="enregistre" @annuler="enModification = false" />
      <FicheActivite v-else :profil="profil" @maj="(p) => (profil = p)" @modifier="enModification = true">
        <template #compte><LignesCompte :compte="compte" prestataire /></template>
      </FicheActivite>
    </template>

    <!-- Client : ses chiffres, de quoi devenir prestataire, puis son compte -->
    <section v-else class="carte overflow-hidden">
      <EnteteProfil :nom="`${compte.prenom} ${compte.nom}`" :chiffres="chiffresClient">
        <template #photo>
          <AvatarPrestataire :id="0" :nom="`${compte.prenom} ${compte.nom}`" :a-une-photo="false" taille="grande" />
        </template>
        <p class="text-[14px] text-texte-doux">{{ compte.email }}</p>
        <template #boutons>
          <AppBouton @click="lignesClient?.ouvrir('Mes informations')">Modifier mes informations</AppBouton>
        </template>
      </EnteteProfil>

      <div class="mx-5 mt-5 mb-4 flex flex-col gap-2.5 rounded-carte bg-linear-135 from-teinte-orange to-teinte-vert p-5 max-sm:mx-4">
        <h2 class="text-[17px] font-black">Proposer mes services</h2>
        <AppAlerte v-if="!compte.email_verifie" etat="attente">
          Vérifiez d'abord votre adresse mail (lien reçu par mail), puis revenez proposer vos services.
        </AppAlerte>
        <AppAlerte v-else-if="!compte.peut_reserver_ou_publier" etat="attente">
          Il faut d'abord que l'accord de tes parents soit accepté (ligne « Accord de tes parents », plus bas).
        </AppAlerte>
        <template v-else-if="formulaireOuvert">
          <p>Créez votre profil de prestataire : les clients vous trouveront dès qu'il sera rempli.</p>
          <FormulaireProfil @enregistre="enregistre" />
          <p class="text-[14px]">
            Pas encore d'entreprise ?
            <AppBouton variante="secondaire" @click="routeur.push('/creer-mon-auto-entreprise')">Créer mon auto-entreprise</AppBouton>
          </p>
        </template>
        <template v-else>
          <p>Vous faites du ménage, du jardinage, de la plomberie… ? Créez votre profil de prestataire.</p>
          <div><AppBouton @click="formulaireOuvert = true">Proposer mes services</AppBouton></div>
        </template>
      </div>

      <h2 class="px-5 pt-2 text-[12px] font-extrabold tracking-[.06em] text-texte-doux uppercase max-sm:px-4">Mon compte</h2>
      <LignesCompte ref="lignesClient" :compte="compte" :prestataire="false" />
    </section>
  </div>
</template>
