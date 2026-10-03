<script setup lang="ts">
// Administration › Problèmes de devis (.doc/ihm/RM-ADMINISTRATION-IHM.md ; RM-DEVIS.md, lot 5.4) : ce que les clients
// signalent après des travaux ; l'administrateur contacte les deux, puis marque le problème traité.
import { onMounted, ref } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { formaterDateHeure } from '../../outils/dates'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBadge from '../ui/AppBadge.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppSection from '../ui/AppSection.vue'

interface ProblemeAdministre {
  devis_id: number
  numero: string
  titre: string
  client: string
  prestataire: string
  probleme: string
  probleme_le: string
}

const emit = defineEmits<{ maj: [] }>()
const { afficherMessage } = useMessage()
const liste = ref<ProblemeAdministre[]>([])
const erreur = ref('')

async function charger() {
  try {
    liste.value = await appelerServeur<ProblemeAdministre[]>('/api/admin/devis-problemes')
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
onMounted(charger)

async function traite(p: ProblemeAdministre) {
  try {
    await appelerServeur(`/api/admin/devis/${p.devis_id}/probleme-traite`, {})
    afficherMessage('Problème traité.')
    await charger()
    emit('maj')
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}
</script>

<template>
  <div class="flex flex-col gap-4">
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <AppSection v-if="!liste.length"><p class="text-texte-doux">Aucun problème signalé.</p></AppSection>
    <AppSection v-for="p in liste" :key="p.devis_id" :titre="`${p.numero} · ${p.titre}`">
      <template #action><AppBadge etat="attente">problème</AppBadge></template>
      <dl class="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 text-[14px]">
        <dt class="text-texte-doux">Client</dt>
        <dd>{{ p.client }}</dd>
        <dt class="text-texte-doux">Prestataire</dt>
        <dd>{{ p.prestataire }}</dd>
        <dt class="text-texte-doux">Signalé le</dt>
        <dd>{{ formaterDateHeure(p.probleme_le) }}</dd>
      </dl>
      <AppAlerte etat="attente">« {{ p.probleme }} »</AppAlerte>
      <p class="text-[13.5px] text-texte-doux">Contactez le client et le prestataire (téléphones dans « Comptes »), puis :</p>
      <div><AppBouton variante="secondaire" @click="traite(p)">Marquer comme traité</AppBouton></div>
    </AppSection>
  </div>
</template>
