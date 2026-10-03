<script setup lang="ts">
// Mes devis (.doc/ihm/RM-DEVIS-IHM.md ; RM-DEVIS.md) : « Mes demandes » (client), et « Devis reçus » pour un
// prestataire. Retour de la page de paiement de Stripe (?devis=…&paiement=fait|annule) : arrhes ou solde.
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import OngletDevisRecus from '../components/devis/OngletDevisRecus.vue'
import OngletMesDemandes from '../components/devis/OngletMesDemandes.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppCarte from '../components/ui/AppCarte.vue'
import AppOnglets from '../components/ui/AppOnglets.vue'
import { useCompte } from '../composables/useCompte'
import { type DemandeVisible, aFaire } from '../outils/devis'
import type { ProfilPrestataire } from '../outils/prestataires'

const route = useRoute()
const routeur = useRouter()
const { compte, chargementFait } = useCompte()
const onglet = ref('demandes')
const mesDemandes = ref<DemandeVisible[] | null>(null)
const recues = ref<DemandeVisible[]>([])
const profil = ref<ProfilPrestataire | null>(null)
const erreur = ref('')

async function charger() {
  if (!compte.value) return
  try {
    mesDemandes.value = await appelerServeur<DemandeVisible[]>('/api/moi/devis')
    if (compte.value.prestataire_id) {
      ;[recues.value, profil.value] = await Promise.all([
        appelerServeur<DemandeVisible[]>('/api/moi/prestataire/devis'),
        appelerServeur<ProfilPrestataire>('/api/moi/prestataire'),
      ])
    }
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
onMounted(charger)
watch(compte, charger)

const onglets = computed(() =>
  compte.value?.prestataire_id
    ? [{ id: 'demandes', texte: 'Mes demandes' }, { id: 'recus', texte: 'Devis reçus' }]
    : [{ id: 'demandes', texte: 'Mes demandes' }],
)
// Compteurs orange : ce qui attend une action
const compteurs = computed(() => ({
  demandes: (mesDemandes.value ?? []).filter((d) => aFaire(d, 'client')).length,
  recus: recues.value.filter((d) => aFaire(d, 'prestataire')).length,
}))

// ---------- Retour de la page de paiement de Stripe ----------
const retourPaiement = ref<{ etat: 'ok' | 'attente'; texte: string } | null>(null)
let relecture: ReturnType<typeof setTimeout> | undefined
async function suivrePaiement(devisId: number, essais = 0) {
  await charger()
  const devis = mesDemandes.value?.find((d) => d.devis?.id === devisId)?.devis
  const enCours = devis && (devis.arrhes_paiement === 'a_payer' || devis.solde_paiement === 'a_payer')
  if (enCours && essais < 15) {
    retourPaiement.value = { etat: 'attente', texte: 'Paiement en cours de confirmation…' }
    relecture = setTimeout(() => suivrePaiement(devisId, essais + 1), 2000)
    return
  }
  if (devis?.statut === 'paye') retourPaiement.value = { etat: 'ok', texte: 'Solde payé : merci !' }
  else if (devis?.statut === 'accepte') retourPaiement.value = { etat: 'ok', texte: 'Arrhes payées : devis accepté.' }
  else retourPaiement.value = { etat: 'attente', texte: "Le paiement n'est pas encore confirmé : actualisez la page dans quelques minutes." }
}
onMounted(() => {
  const devisId = Number(route.query.devis)
  if (!devisId || !route.query.paiement) return
  if (route.query.paiement === 'fait') suivrePaiement(devisId)
  else retourPaiement.value = { etat: 'attente', texte: "Paiement non terminé : rien n'a été pris. Vous pouvez recommencer dans 30 minutes au plus tard." }
  routeur.replace({ query: {} })
})
onUnmounted(() => clearTimeout(relecture))
</script>

<template>
  <AppCarte v-if="chargementFait && !compte" titre="Mes devis" intro="Connectez-vous pour voir vos devis.">
    <AppBouton pleine-largeur @click="routeur.push({ path: '/connexion', query: { retour: '/devis' } })">Se connecter</AppBouton>
  </AppCarte>

  <div v-else-if="compte" class="mx-auto flex w-full max-w-[760px] flex-col gap-4">
    <h1 class="text-[28px] font-bold">Mes devis</h1>
    <AppOnglets v-if="onglets.length > 1" v-model="onglet" :onglets="onglets" :compteurs="compteurs" />
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <AppAlerte v-if="retourPaiement" :etat="retourPaiement.etat">{{ retourPaiement.texte }}</AppAlerte>
    <template v-if="mesDemandes">
      <OngletDevisRecus
        v-if="onglet === 'recus'"
        :demandes="recues"
        :facture-tva="profil?.facture_tva ?? false"
        :nom-prestataire="profil?.nom_affiche ?? ''"
        @maj="charger"
      />
      <OngletMesDemandes v-else :demandes="mesDemandes" @maj="charger" />
    </template>
  </div>
</template>
