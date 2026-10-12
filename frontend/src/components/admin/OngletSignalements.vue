<script setup lang="ts">
// Administration › Signalements (.doc/ihm/RM-SIGNALEMENTS-IHM.md ; RM-ADMINISTRATION.md, lot 6.4) : chaque signalement
// de prestataire, puis [Rien à faire] ou [Bloquer le prestataire…] avec un motif
// envoyé au prestataire (jamais le nom de celui qui a signalé).
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { formaterDateHeure } from '../../outils/dates'
import FenetreTexte, { type DemandeTexte } from '../FenetreTexte.vue'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBadge from '../ui/AppBadge.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppSection from '../ui/AppSection.vue'

interface SignalementAdministre {
  id: number
  cree_le: string
  auteur: string
  prestataire_id: number | null // vide : c'est un client qui est visé (demande ou conversation signalée)
  demande_id?: number | null
  demande_titre?: string | null
  demande_texte?: string | null
  prestataire: string
  prestataire_statut: string
  motif: string
  deja_signale: number
}

const emit = defineEmits<{ maj: [] }>()
const routeur = useRouter()
const { afficherMessage } = useMessage()
const liste = ref<SignalementAdministre[]>([])
const erreur = ref('')
const aDecider = ref<DemandeTexte | null>(null)

async function charger() {
  try {
    liste.value = await appelerServeur<SignalementAdministre[]>('/api/admin/signalements')
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
onMounted(charger)

async function classer(s: SignalementAdministre) {
  try {
    await appelerServeur(`/api/admin/signalements/${s.id}`, { action: 'classer' })
    afficherMessage('Signalement classé.')
    await charger()
    emit('maj')
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}
const bloquer = (s: SignalementAdministre): DemandeTexte => ({
  titre: `Bloquer ${s.prestataire} ?`,
  explication: 'Son profil disparaît des recherches, ses rendez-vous à venir sont annulés et ses clients prévenus. Le motif lui est envoyé.',
  etiquette: 'Motif', aide: 'ex. « Faux profil »', chemin: `/api/admin/signalements/${s.id}`, cle: 'decision',
  fixes: { action: 'bloquer_prestataire' }, bouton: 'Bloquer', danger: true, reussite: 'Prestataire bloqué.',
})
const cacherDemande = (s: SignalementAdministre): DemandeTexte => ({
  titre: `Cacher « ${s.demande_titre} » ?`,
  explication: 'La demande disparaît de l’accueil et plus personne ne peut y répondre. Le motif est envoyé au client, jamais le nom de celui qui a signalé.',
  etiquette: 'Motif', aide: 'ex. « Demande contraire à la loi »', chemin: `/api/admin/signalements/${s.id}`, cle: 'decision',
  fixes: { action: 'cacher_demande' }, bouton: 'Cacher la demande', danger: true, reussite: 'Demande cachée.',
})
const ETATS: Record<string, string> = { actif: 'actif', en_pause: 'en pause', bloque: 'bloqué', arrete: 'arrêté' }
</script>

<template>
  <div class="flex flex-col gap-4">
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <AppSection v-if="!liste.length"><p class="text-texte-doux">Aucun signalement à traiter.</p></AppSection>
    <AppSection v-for="s in liste" :key="s.id" :titre="s.prestataire">
      <template #action>
        <AppBadge etat="attente">{{ s.demande_id ? 'demande signalée' : s.prestataire_id ? 'prestataire signalé' : 'client signalé' }}</AppBadge>
      </template>
      <dl class="grid grid-cols-[auto_1fr] items-center gap-x-4 gap-y-1 text-[14px]">
        <dt class="text-texte-doux">Signalé par</dt>
        <dd>{{ s.auteur }}, le {{ formaterDateHeure(s.cree_le) }}</dd>
        <dt class="text-texte-doux">Prestataire</dt>
        <dd class="flex flex-wrap items-center gap-2">
          {{ ETATS[s.prestataire_statut] ?? s.prestataire_statut }}<template v-if="s.deja_signale"> · déjà signalé {{ s.deja_signale }} fois</template>
          <AppBouton v-if="s.prestataire_id" variante="secondaire" @click="routeur.push(`/prestataires/${s.prestataire_id}`)">Voir sa page</AppBouton>
        </dd>
      </dl>
      <p v-if="s.demande_id" class="rounded-rafals bg-fond px-3 py-2 text-[14px]">
        <b>Demande : {{ s.demande_titre }}</b><br />{{ s.demande_texte }}
      </p>
      <AppAlerte etat="attente">« {{ s.motif }} »</AppAlerte>
      <div class="flex flex-wrap gap-2">
        <AppBouton variante="secondaire" @click="classer(s)">Rien à faire</AppBouton>
        <AppBouton v-if="s.demande_id" variante="danger" @click="aDecider = cacherDemande(s)">Cacher la demande…</AppBouton>
        <AppBouton v-else-if="s.prestataire_id && s.prestataire_statut !== 'bloque' && s.prestataire_statut !== 'arrete'" variante="danger" @click="aDecider = bloquer(s)">
          Bloquer le prestataire…
        </AppBouton>
      </div>
    </AppSection>
    <FenetreTexte :demande="aDecider" @fermer="aDecider = null" @fait="(aDecider = null), charger(), emit('maj')" />
  </div>
</template>
