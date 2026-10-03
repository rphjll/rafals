<script setup lang="ts">
// Fenêtre « Payé en direct ? » (RM-DEVIS-IHM, RM-RENDEZ-VOUS-IHM) : le prestataire a reçu l'argent hors de rafals et
// dit comment (espèces, chèque, virement) ; rafals crée la facture. Commune aux devis et aux rendez-vous en espèces.
import { ref, watch } from 'vue'
import type { MoyenDirect } from '../outils/factures'
import { montant } from '../outils/paiements'
import AppBouton from './ui/AppBouton.vue'
import AppChoix from './ui/AppChoix.vue'
import AppFenetre from './ui/AppFenetre.vue'

/** `nom` : le client ; `centimes` : la somme reçue */
const props = defineProps<{ demande: { nom: string; centimes: number } | null }>()
const emit = defineEmits<{ fermer: []; confirmer: [moyen: MoyenDirect] }>()
const moyen = ref<MoyenDirect>('especes')
watch(() => props.demande, () => (moyen.value = 'especes'))
</script>

<template>
  <AppFenetre :ouverte="demande !== null" titre="Payé en direct ?" @fermer="emit('fermer')">
    <div v-if="demande" class="flex flex-col gap-3 text-texte">
      <p class="text-[14px] text-texte-doux">
        {{ demande.nom }} vous a payé {{ montant(demande.centimes) }} hors de rafals. rafals crée la facture à votre nom.
      </p>
      <AppChoix
        v-model="moyen"
        etiquette="Comment ?"
        obligatoire
        :options="[{ valeur: 'especes', texte: 'Espèces' }, { valeur: 'cheque', texte: 'Chèque' }, { valeur: 'virement', texte: 'Virement' }]"
      />
    </div>
    <template #pied>
      <AppBouton @click="emit('confirmer', moyen)">Confirmer</AppBouton>
      <AppBouton variante="secondaire" @click="emit('fermer')">Annuler</AppBouton>
    </template>
  </AppFenetre>
</template>
