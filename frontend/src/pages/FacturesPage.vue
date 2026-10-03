<script setup lang="ts">
// Mes factures (.doc/ihm/RM-FACTURES-IHM.md ; RM-FACTURES.md) : pour un client, ses factures reçues ; pour un
// prestataire, 3 onglets : « Reçues », « Émises » (faites par rafals à son nom) et « Commission de rafals ».
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import TableauFactures from '../components/factures/TableauFactures.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppCarte from '../components/ui/AppCarte.vue'
import AppOnglets from '../components/ui/AppOnglets.vue'
import AppSection from '../components/ui/AppSection.vue'
import { useCompte } from '../composables/useCompte'
import type { FactureVisible } from '../outils/factures'

const routeur = useRouter()
const { compte, chargementFait } = useCompte()
const onglet = ref('recues')
const recues = ref<FactureVisible[] | null>(null)
const duPrestataire = ref<FactureVisible[]>([])
const erreur = ref('')

async function charger() {
  if (!compte.value) return
  try {
    recues.value = await appelerServeur<FactureVisible[]>('/api/moi/factures')
    if (compte.value.prestataire_id) duPrestataire.value = await appelerServeur<FactureVisible[]>('/api/moi/prestataire/factures')
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
onMounted(charger)
watch(compte, charger)

const onglets = [
  { id: 'recues', texte: 'Reçues' },
  { id: 'emises', texte: 'Émises' },
  { id: 'commission', texte: 'Commission de rafals' },
]
const emises = computed(() => duPrestataire.value.filter((f) => f.sorte !== 'commission'))
const commissions = computed(() => duPrestataire.value.filter((f) => f.sorte === 'commission'))
</script>

<template>
  <AppCarte v-if="chargementFait && !compte" titre="Mes factures" intro="Connectez-vous pour voir vos factures.">
    <AppBouton pleine-largeur @click="routeur.push({ path: '/connexion', query: { retour: '/factures' } })">Se connecter</AppBouton>
  </AppCarte>

  <div v-else-if="compte" class="mx-auto flex w-full max-w-[760px] flex-col gap-4">
    <h1 class="text-[28px] font-bold">Mes factures</h1>
    <AppOnglets v-if="compte.prestataire_id" v-model="onglet" :onglets="onglets" />
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>

    <AppSection v-if="recues && onglet === 'emises' && compte.prestataire_id">
      <TableauFactures v-if="emises.length" :factures="emises" autre="acheteur" />
      <p v-else class="text-texte-doux">Aucune facture pour l'instant : elles se créent toutes seules à chaque paiement.</p>
      <p class="text-[13.5px] text-texte-doux">
        rafals fait ces factures à votre place, à votre nom (mandat de facturation). Un avoir est une facture « en moins »,
        après un remboursement.
      </p>
    </AppSection>
    <AppSection v-else-if="recues && onglet === 'commission' && compte.prestataire_id">
      <TableauFactures v-if="commissions.length" :factures="commissions" autre="vendeur" />
      <p v-else class="text-texte-doux">
        Pas encore de facture de commission : rafals vous en envoie une le 1er de chaque mois si vous avez été payé par carte.
      </p>
    </AppSection>
    <AppSection v-else-if="recues">
      <TableauFactures v-if="recues.length" :factures="recues" autre="vendeur" />
      <p v-else class="text-texte-doux">Aucune facture pour l'instant.</p>
      <p class="text-[13.5px] text-texte-doux">
        Les numéros sont ceux de chaque prestataire. Un avoir est une facture « en moins », après un remboursement.
      </p>
    </AppSection>
  </div>
</template>
