<script setup lang="ts">
// Administration › Avis signalés (.doc/ihm/RM-ADMINISTRATION-IHM.md ; RM-AVIS.md) : l'avis et la raison du signalement,
// puis [Le laisser] ou [Le cacher…] avec un motif envoyé à celui qui l'a écrit. Rien n'est effacé.
// Deux sortes d'avis : sur un prestataire (signalé par lui) et, depuis le lot 8.6, sur un client (signalé par lui).
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
  /** La personne notée, qui a signalé l'avis : « Karim Benali » ou « Marie D. » */
  sur: string
  signalement: string
  signale_le: string
  /** L'adresse du serveur pour décider : avis sur un prestataire, ou avis sur un client */
  chemin: string
  /** Qui reçoit le motif si l'avis est caché */
  auteur: 'client' | 'prestataire'
}

const emit = defineEmits<{ maj: [] }>()
const { afficherMessage } = useMessage()
const liste = ref<AvisSignale[]>([])
const erreur = ref('')
const aCacher = ref<DemandeTexte | null>(null)

async function charger() {
  try {
    const [surPrestataires, surClients] = await Promise.all([
      appelerServeur<{ avis: AvisPublic; prestataire: string; signalement: string; signale_le: string }[]>('/api/admin/avis-signales'),
      appelerServeur<{ avis: AvisPublic; client: string; signalement: string; signale_le: string }[]>('/api/admin/avis-clients-signales'),
    ])
    liste.value = [
      ...surPrestataires.map((s) => ({
        avis: s.avis, sur: s.prestataire, signalement: s.signalement, signale_le: s.signale_le,
        chemin: `/api/admin/avis/${s.avis.id}/decision`, auteur: 'client' as const,
      })),
      ...surClients.map((s) => ({
        avis: s.avis, sur: s.client, signalement: s.signalement, signale_le: s.signale_le,
        chemin: `/api/admin/avis-clients/${s.avis.id}/decision`, auteur: 'prestataire' as const,
      })),
    ].sort((a, b) => a.signale_le.localeCompare(b.signale_le))
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
onMounted(charger)

async function laisser(s: AvisSignale) {
  try {
    await appelerServeur(s.chemin, { cacher: false })
    afficherMessage('Avis laissé : le signalement est traité.')
    await charger()
    emit('maj')
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}
const cacher = (s: AvisSignale): DemandeTexte => ({
  titre: 'Cacher cet avis ?',
  explication: `Il ne sera plus affiché et sa note ne comptera plus. Le motif est envoyé au ${s.auteur} qui l'a écrit. Rien n'est effacé.`,
  etiquette: 'Motif', aide: 'ex. « Accusation grave sans élément »',
  chemin: s.chemin, cle: 'motif', fixes: { cacher: true },
  bouton: 'Cacher', danger: true, reussite: `Avis caché : le ${s.auteur} est prévenu.`,
})
</script>

<template>
  <div class="flex flex-col gap-4">
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <AppSection v-if="!liste.length"><p class="text-texte-doux">Aucun avis signalé.</p></AppSection>
    <AppSection v-for="s in liste" :key="s.chemin" :titre="`Avis sur ${s.sur}`">
      <template #action>
        <AppBadge etat="attente">{{ s.auteur === 'prestataire' ? 'avis sur un client, signalé' : 'signalé' }}</AppBadge>
      </template>
      <AvisAffiche :avis="s.avis" />
      <AppAlerte etat="attente">
        Signalé par {{ s.sur }} le {{ formaterDateHeure(s.signale_le) }} : « {{ s.signalement }} »
      </AppAlerte>
      <div class="flex flex-wrap gap-2">
        <AppBouton variante="secondaire" @click="laisser(s)">Le laisser</AppBouton>
        <AppBouton variante="danger" @click="aCacher = cacher(s)">Le cacher…</AppBouton>
      </div>
    </AppSection>
    <FenetreTexte :demande="aCacher" @fermer="aCacher = null" @fait="(aCacher = null), charger(), emit('maj')" />
  </div>
</template>
