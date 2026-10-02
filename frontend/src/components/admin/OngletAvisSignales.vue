<script setup lang="ts">
// Administration › Avis signalés (.doc/ihm/RM-ADMINISTRATION-IHM.md ; RM-AVIS.md) : l'avis et la raison du signalement,
// puis [Le laisser] ou [Le cacher…] avec un motif envoyé au client. Rien n'est effacé.
import { onMounted, ref } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import type { AvisPublic } from '../../outils/avis'
import { formaterDateHeure } from '../../outils/dates'
import AvisAffiche from '../avis/AvisAffiche.vue'
import FenetreTexte, { type DemandeTexte } from '../FenetreTexte.vue'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBadge from '../ui/AppBadge.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppSection from '../ui/AppSection.vue'

interface AvisSignale {
  avis: AvisPublic
  prestataire: string
  signalement: string
  signale_le: string
}

const emit = defineEmits<{ maj: [] }>()
const { afficherMessage } = useMessage()
const liste = ref<AvisSignale[]>([])
const erreur = ref('')
const aCacher = ref<DemandeTexte | null>(null)

async function charger() {
  try {
    liste.value = await appelerServeur<AvisSignale[]>('/api/admin/avis-signales')
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
onMounted(charger)

async function laisser(s: AvisSignale) {
  try {
    await appelerServeur(`/api/admin/avis/${s.avis.id}/decision`, { cacher: false })
    afficherMessage('Avis laissé : le signalement est traité.')
    await charger()
    emit('maj')
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}
const cacher = (s: AvisSignale): DemandeTexte => ({
  titre: 'Cacher cet avis ?',
  explication: "Il ne sera plus affiché et sa note ne comptera plus. Le motif est envoyé au client. Rien n'est effacé.",
  etiquette: 'Motif', aide: 'ex. « Accusation grave sans élément »',
  chemin: `/api/admin/avis/${s.avis.id}/decision`, cle: 'motif', fixes: { cacher: true },
  bouton: 'Cacher', danger: true, reussite: 'Avis caché : le client est prévenu.',
})
</script>

<template>
  <div class="flex flex-col gap-4">
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <AppSection v-if="!liste.length"><p class="text-texte-doux">Aucun avis signalé.</p></AppSection>
    <AppSection v-for="s in liste" :key="s.avis.id" :titre="`Avis sur ${s.prestataire}`">
      <template #action><AppBadge etat="attente">signalé</AppBadge></template>
      <AvisAffiche :avis="s.avis" />
      <AppAlerte etat="attente">
        Signalé par {{ s.prestataire }} le {{ formaterDateHeure(s.signale_le) }} : « {{ s.signalement }} »
      </AppAlerte>
      <div class="flex flex-wrap gap-2">
        <AppBouton variante="secondaire" @click="laisser(s)">Le laisser</AppBouton>
        <AppBouton variante="danger" @click="aCacher = cacher(s)">Le cacher…</AppBouton>
      </div>
    </AppSection>
    <FenetreTexte :demande="aCacher" @fermer="aCacher = null" @fait="(aCacher = null), charger(), emit('maj')" />
  </div>
</template>
