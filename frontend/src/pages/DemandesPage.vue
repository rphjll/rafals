<script setup lang="ts">
// Onglet « Demandes » (lot 14.2 ; .doc/ihm/RM-DEMANDES-IHM.md), identique à la grande maquette depuis le 10/11/2026 :
// le titre et [+ Publier une demande], puis 2 sous-onglets.
// « Près de chez moi » : les demandes des autres, lues par tous, avec [Répondre] ou 🔒 et sa raison.
// « Mes demandes » : les miennes, « En cours » puis « Terminées », repliées en une ligne ; un clic ouvre le détail.
import { computed, onMounted, ref } from 'vue'
import { appelerServeur, messageErreur } from '../api'
import CarteDemande from '../components/demandes/CarteDemande.vue'
import ListeMesDemandes from '../components/demandes/ListeMesDemandes.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppIcone from '../components/ui/AppIcone.vue'
import AppOnglets from '../components/ui/AppOnglets.vue'
import { useCompte } from '../composables/useCompte'
import type { DemandeVisible } from '../outils/demandes'

const { compte, chargementFait } = useCompte()
const onglet = ref('pres')
const nombreMiennes = ref<number | null>(null)
const onglets = computed(() => [
  { id: 'pres', texte: 'Près de chez moi' },
  { id: 'miennes', texte: nombreMiennes.value === null ? 'Mes demandes' : `Mes demandes (${nombreMiennes.value})` },
])

const toutes = ref<DemandeVisible[] | null>(null)
const erreur = ref('')
// Ma propre demande n'est que dans « Mes demandes » (demande de Raphael du 09/11/2026, sur la maquette)
const autres = computed(() => (toutes.value ?? []).filter((d) => !d.a_moi))
onMounted(async () => {
  try {
    toutes.value = await appelerServeur<DemandeVisible[]>('/api/demandes')
  } catch (e) {
    erreur.value = messageErreur(e)
  }
})
</script>

<template>
  <div class="page">
    <div class="section-titre" style="align-items: center; flex-wrap: wrap">
      <div class="tete">
        <h1>Demandes</h1>
        <p>Les besoins publiés près de chez vous. Tout le monde peut les voir.</p>
      </div>
      <RouterLink class="btn btn-1" :to="compte ? '/demandes/nouvelle' : '/connexion'"><AppIcone nom="plus" />Publier une demande</RouterLink>
    </div>
    <AppOnglets v-model="onglet" :onglets="onglets" />

    <template v-if="onglet === 'pres'">
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <template v-else-if="toutes">
        <p class="doux petit">
          {{ autres.length }} demande{{ autres.length > 1 ? 's' : '' }} en ligne, de la plus récente à la plus ancienne.
          <template v-if="compte?.prestataire_id"> Vous pouvez répondre à celles de vos métiers, dans votre zone.</template>
        </p>
        <CarteDemande v-for="demande in autres" :key="demande.id" :demande="demande" />
        <div v-if="!autres.length" class="carte vide">Aucune demande en ligne pour l’instant. Revenez bientôt, ou publiez la vôtre.</div>
      </template>
    </template>

    <template v-else>
      <template v-if="chargementFait && !compte">
        <div class="carte vide">
          <h3>Connectez-vous pour voir vos demandes</h3>
          <RouterLink class="btn btn-1" to="/connexion" style="margin-top: 14px">Se connecter</RouterLink>
        </div>
      </template>
      <p v-else class="doux petit">Ce que vous avez publié, et les réponses des prestataires.</p>
    </template>
    <!-- Toujours chargée (même cachée) pour que le nombre de l'onglet soit juste -->
    <div v-if="compte" v-show="onglet === 'miennes'" class="contents">
      <ListeMesDemandes @nombre="(n) => (nombreMiennes = n)" />
    </div>
  </div>
</template>
