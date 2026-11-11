<script setup lang="ts">
// « Paramètres » (.doc/ihm/RM-PARAMETRES-IHM.md), ouverte depuis la liste sous le prénom (demande de Raphael du 17/10/2026).
// « Apparence » : thème Automatique, Clair ou Sombre, gardé dans l'appareil. « Notifications » (prestataire seulement) :
// les alertes de nouvelles demandes, venues de « Mon activité » le 21/10/2026 (demande de Raphael).
// « Mes abonnements » (tout compte connecté) : les 3 notifications des prestataires suivis, pour tous à la fois.
import ReglagesAbonnements from '../components/abonnements/ReglagesAbonnements.vue'
import ReglagesAlertes from '../components/alertes/ReglagesAlertes.vue'
import AppSegment from '../components/ui/AppSegment.vue'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'
import { useTheme, type ChoixTheme } from '../composables/useTheme'

const { choix, choisirTheme } = useTheme()
const { afficherMessage } = useMessage()
const { compte } = useCompte()

// Comme la grande maquette : 3 cases collées, et l'explication du choix dessous
const options: { valeur: ChoixTheme; texte: string; exemple: string }[] = [
  { valeur: 'auto', texte: 'Automatique', exemple: 'Comme votre téléphone ou votre ordinateur : clair le jour, sombre s’il est réglé en sombre. Gardé sur cet appareil.' },
  { valeur: 'clair', texte: 'Clair', exemple: 'Fond clair, toujours, sur toutes les pages. Gardé sur cet appareil.' },
  { valeur: 'sombre', texte: 'Sombre', exemple: 'Fond sombre, plus doux le soir, sur toutes les pages. Gardé sur cet appareil.' },
]
const messages: Record<ChoixTheme, string> = {
  auto: 'Thème automatique : comme votre appareil.',
  clair: 'Thème clair activé.',
  sombre: 'Thème sombre activé.',
}

// Effet immédiat, sans bouton « Enregistrer »
function changer(nouveau: ChoixTheme) {
  choisirTheme(nouveau)
  afficherMessage(messages[nouveau])
}
</script>

<template>
  <div class="page">
    <div class="tete"><h1>Paramètres</h1><p>Réglez rafals comme vous le préférez.</p></div>
    <section class="section">
      <h2>Apparence</h2>
      <div class="carte p-[18px]">
        <div class="reglage">
          <b>Thème</b>
          <AppSegment :model-value="choix" etiquette="Thème" :options="options" @update:model-value="changer" />
          <p class="exemple">{{ options.find((o) => o.valeur === choix)?.exemple }}</p>
        </div>
      </div>
    </section>
    <ReglagesAbonnements v-if="compte" />
    <ReglagesAlertes v-if="compte?.prestataire_id" />
  </div>
</template>
