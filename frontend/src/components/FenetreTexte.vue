<script setup lang="ts">
// Fenêtre à un seul texte : contester une absence (RM-RENDEZ-VOUS-IHM), répondre à un avis, le signaler, le cacher
// (RM-AVIS-IHM). La page donne le titre, l'explication, le chemin du serveur et le message de réussite.
import { ref, watch } from 'vue'
import { appelerServeur, messageErreur } from '../api'
import { useMessage } from '../composables/useMessage'
import AppAlerte from './ui/AppAlerte.vue'
import AppBouton from './ui/AppBouton.vue'
import AppFenetre from './ui/AppFenetre.vue'
import AppZoneTexte from './ui/AppZoneTexte.vue'

export interface DemandeTexte {
  titre: string
  explication: string
  etiquette: string
  aide: string
  chemin: string
  /** Données envoyées : le texte est mis sous cette clé (ex. « texte », « motif ») ; autres valeurs fixes en plus */
  cle: string
  fixes?: Record<string, unknown>
  bouton: string
  danger?: boolean
  reussite: string
}

const props = defineProps<{ demande: DemandeTexte | null }>()
const emit = defineEmits<{ fermer: []; fait: [] }>()
const { afficherMessage } = useMessage()
const texte = ref('')
const erreur = ref('')
watch(() => props.demande, () => ((texte.value = ''), (erreur.value = '')))

async function envoyer() {
  const d = props.demande
  if (!d) return
  erreur.value = ''
  try {
    await appelerServeur(d.chemin, { ...d.fixes, [d.cle]: texte.value })
    afficherMessage(d.reussite)
    emit('fait')
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
</script>

<template>
  <AppFenetre :ouverte="demande !== null" :titre="demande?.titre ?? ''" @fermer="emit('fermer')">
    <div v-if="demande" class="flex flex-col gap-3 text-texte">
      <p class="text-[14px] text-texte-doux">{{ demande.explication }}</p>
      <AppZoneTexte v-model="texte" :etiquette="demande.etiquette" obligatoire :maximum="1000" :aide="demande.aide" />
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    </div>
    <template #pied>
      <AppBouton :variante="demande?.danger ? 'danger' : 'principal'" @click="envoyer">{{ demande?.bouton }}</AppBouton>
      <AppBouton variante="secondaire" @click="emit('fermer')">Annuler</AppBouton>
    </template>
  </AppFenetre>
</template>
