<script setup lang="ts">
// Administration › Tableau de bord (.doc/ihm/RM-ADMINISTRATION-IHM.md ; RM-ADMINISTRATION.md, lot 6.2) : ce qui attend
// une décision (un bouton par onglet concerné), puis l'activité du mois et ce qui est en ligne en ce moment.
import { computed, onMounted, ref } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { montant } from '../../outils/paiements'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppChiffre from '../ui/AppChiffre.vue'
import AppSection from '../ui/AppSection.vue'

interface TableauDeBord {
  a_traiter: Record<string, number>
  activite: {
    mois: string
    nouveaux_comptes: number
    prestataires_actifs: number
    annonces_en_ligne: number
    rendez_vous: number
    paiements: number
    paiements_centimes: number
    commission_centimes: number
    rembourses: number
  }
}

const emit = defineEmits<{ aller: [onglet: string] }>()
const tableau = ref<TableauDeBord | null>(null)
const erreur = ref('')
onMounted(async () => {
  try {
    tableau.value = await appelerServeur<TableauDeBord>('/api/admin/tableau-de-bord')
  } catch (e) {
    erreur.value = messageErreur(e)
  }
})

// Le texte du bouton pour chaque onglet où quelque chose attend
const TEXTES: Record<string, [string, string]> = {
  accords: ['accord à vérifier', 'accords à vérifier'],
  absences: ['absence contestée', 'absences contestées'],
  avis: ['avis signalé', 'avis signalés'],
  devis: ['problème de devis', 'problèmes de devis'],
  propositions: ['proposition de métier', 'propositions de métiers'],
  signalements: ['signalement', 'signalements'],
}
const aTraiter = computed(() =>
  Object.entries(tableau.value?.a_traiter ?? {})
    .filter(([onglet, nombre]) => nombre > 0 && TEXTES[onglet])
    .map(([onglet, nombre]) => ({ onglet, texte: `${nombre} ${TEXTES[onglet]?.[nombre > 1 ? 1 : 0]}` })),
)
const NOMS_MOIS = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
const titreDuMois = computed(() => {
  const [annee, mois] = (tableau.value?.activite.mois ?? '').split('-')
  return `${NOMS_MOIS[Number(mois) - 1] ?? ''} ${annee ?? ''}`
})
</script>

<template>
  <div class="flex flex-col gap-4">
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <template v-if="tableau">
      <AppSection titre="À traiter">
        <div v-if="aTraiter.length" class="flex flex-wrap gap-2">
          <AppBouton v-for="t in aTraiter" :key="t.onglet" variante="secondaire" @click="emit('aller', t.onglet)">{{ t.texte }}</AppBouton>
        </div>
        <p v-else class="text-texte-doux">Rien à traiter pour l'instant.</p>
      </AppSection>
      <AppSection :titre="titreDuMois">
        <div class="grid grid-cols-[repeat(auto-fit,minmax(150px,1fr))] gap-2.5">
          <AppChiffre titre="Nouveaux comptes" :valeur="String(tableau.activite.nouveaux_comptes)" />
          <AppChiffre titre="Rendez-vous pris" :valeur="String(tableau.activite.rendez_vous)" />
          <AppChiffre titre="Paiements par carte" :valeur="String(tableau.activite.paiements)" :detail="montant(tableau.activite.paiements_centimes)" />
          <AppChiffre titre="Commission de rafals" :valeur="montant(tableau.activite.commission_centimes)" detail="5 % des paiements" />
          <AppChiffre titre="Remboursements" :valeur="String(tableau.activite.rembourses)" />
        </div>
        <h3 class="text-[17px] font-bold">En ce moment</h3>
        <div class="grid grid-cols-[repeat(auto-fit,minmax(150px,1fr))] gap-2.5">
          <AppChiffre titre="Prestataires actifs" :valeur="String(tableau.activite.prestataires_actifs)" />
          <AppChiffre titre="Annonces en ligne" :valeur="String(tableau.activite.annonces_en_ligne)" />
        </div>
        <p class="text-[13.5px] text-texte-doux">
          Depuis le 1er du mois. Les paiements comptés sont ceux gardés (ni abandonnés, ni remboursés).
        </p>
      </AppSection>
    </template>
  </div>
</template>
