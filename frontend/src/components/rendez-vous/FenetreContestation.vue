<script setup lang="ts">
// Fenêtre « Contester l'absence » (.doc/ihm/RM-RENDEZ-VOUS-IHM.md) : la personne marquée absente explique ce qui
// s'est passé ; l'administrateur lira les deux versions. Sert au client et au prestataire.
import { ref, watch } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppFenetre from '../ui/AppFenetre.vue'
import AppZoneTexte from '../ui/AppZoneTexte.vue'

/** chemin : « /api/moi/rendez-vous/12/contester » (client) ou « /api/moi/prestataire/rendez-vous/12/contester » */
const props = defineProps<{ chemin: string | null }>()
const emit = defineEmits<{ fermer: []; conteste: [] }>()
const { afficherMessage } = useMessage()
const explication = ref('')
const erreur = ref('')
watch(() => props.chemin, () => ((explication.value = ''), (erreur.value = '')))

async function envoyer() {
  if (!props.chemin) return
  erreur.value = ''
  try {
    await appelerServeur(props.chemin, { explication: explication.value })
    afficherMessage('Contestation envoyée : rafals va trancher.')
    emit('conteste')
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
</script>

<template>
  <AppFenetre :ouverte="chemin !== null" titre="Contester l'absence" @fermer="emit('fermer')">
    <div class="flex flex-col gap-3 text-texte">
      <p class="text-[14px] text-texte-doux">
        Expliquez ce qui s'est passé : l'administrateur de rafals lira les deux versions et tranchera. En attendant, rien
        n'est compté ni affiché.
      </p>
      <AppZoneTexte
        v-model="explication"
        etiquette="Ce qui s'est passé"
        obligatoire
        :maximum="1000"
        aide="ex. « Je suis venu à 10 h, personne n'a ouvert, j'ai appelé 2 fois. »"
      />
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    </div>
    <template #pied>
      <AppBouton @click="envoyer">Envoyer</AppBouton>
      <AppBouton variante="secondaire" @click="emit('fermer')">Annuler</AppBouton>
    </template>
  </AppFenetre>
</template>
