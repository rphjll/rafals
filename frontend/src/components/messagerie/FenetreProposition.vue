<script setup lang="ts">
// Fenêtre « Faire une proposition » du prestataire (.doc/ihm/RM-MESSAGES-IHM.md ; RM-DEMANDES.md) : pour quelle
// demande, prix, durée, jour, heure, paiement accepté. Sans demande (le client a écrit en premier) : métier et lieu.
import { computed, ref, watch } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { aujourdhuiIso } from '../../outils/dates'
import type { DemandeVisible } from '../../outils/demandes'
import { DUREES } from '../../outils/messagerie'
import type { ProfilPrestataire } from '../../outils/prestataires'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppCase from '../ui/AppCase.vue'
import AppChamp from '../ui/AppChamp.vue'
import AppFenetre from '../ui/AppFenetre.vue'
import AppSegment from '../ui/AppSegment.vue'
import AppSelection from '../ui/AppSelection.vue'

const props = defineProps<{ ouverte: boolean; conversationId: number; avec: string; demandes: DemandeVisible[] }>()
const emit = defineEmits<{ fermer: []; envoyee: [] }>()
const { afficherMessage } = useMessage()

const LIEUX = [
  { valeur: 'chez_client', texte: 'Chez le client' },
  { valeur: 'chez_moi', texte: 'Chez moi' },
]
const demandeId = ref<number | null>(null)
const metierId = ref<number | null>(null)
const lieu = ref('chez_client')
const prix = ref('')
const dureeMinutes = ref<number | null>(60)
const jour = ref('')
const heure = ref('')
const carte = ref(false)
const especes = ref(true)
const profil = ref<ProfilPrestataire | null>(null)
const erreur = ref('')
const occupe = ref(false)

const optionsDemandes = computed(() => props.demandes.map((d) => ({ valeur: d.id, texte: `${d.titre} · ${d.ville}` })))
const optionsMetiers = computed(() =>
  profil.value ? [profil.value.metier_principal, ...profil.value.metiers_secondaires].map((m) => ({ valeur: m.id, texte: m.nom })) : [],
)
const sansDemande = computed(() => props.demandes.length === 0)

watch(
  () => props.ouverte,
  async (ouverte) => {
    if (!ouverte) return
    erreur.value = ''
    demandeId.value = props.demandes[0]?.id ?? null
    if (sansDemande.value && !profil.value) {
      profil.value = await appelerServeur<ProfilPrestataire>('/api/moi/prestataire').catch(() => null)
      metierId.value = profil.value?.metier_principal.id ?? null
    }
  },
)

async function envoyer() {
  erreur.value = ''
  const euros = Number(prix.value.replace(',', '.'))
  if (!prix.value.trim() || !Number.isFinite(euros) || euros <= 0) erreur.value = 'Indiquez votre prix en euros (ex. 60).'
  else if (!jour.value || !heure.value) erreur.value = 'Indiquez le jour et l’heure de début.'
  else if (dureeMinutes.value === null) erreur.value = 'Indiquez la durée.'
  if (erreur.value) return
  occupe.value = true
  try {
    await appelerServeur(`/api/conversations/${props.conversationId}/propositions`, {
      prix_centimes: Math.round(euros * 100),
      debut: `${jour.value}T${heure.value}`, // heure de Paris
      duree_minutes: dureeMinutes.value,
      demande_id: sansDemande.value ? null : demandeId.value,
      metier_id: sansDemande.value ? metierId.value : null,
      lieu: sansDemande.value ? lieu.value : null,
      paiement_carte: carte.value,
      paiement_especes: especes.value,
    })
    afficherMessage(`Proposition envoyée à ${props.avec}.`)
    emit('envoyee')
  } catch (e) {
    erreur.value = messageErreur(e) // ex. « Vous avez déjà un rendez-vous à cette heure-là : proposez une autre heure. »
  } finally {
    occupe.value = false
  }
}
</script>

<template>
  <AppFenetre :ouverte="ouverte" titre="Faire une proposition" @fermer="emit('fermer')">
    <div class="flex flex-col gap-3 text-texte">
      <AppSelection v-if="!sansDemande" v-model="demandeId" etiquette="Pour quelle demande ?" :options="optionsDemandes" obligatoire />
      <template v-else>
        <AppSelection v-model="metierId" etiquette="Pour quel métier ?" :options="optionsMetiers" obligatoire />
        <AppSegment v-model="lieu" etiquette="Où a lieu le service ?" :options="LIEUX" />
      </template>
      <div class="grid gap-3 sm:grid-cols-2">
        <AppChamp v-model="prix" etiquette="Prix (€)" obligatoire inputmode="decimal" placeholder="ex. 60" />
        <AppSelection v-model="dureeMinutes" etiquette="Durée" :options="DUREES" obligatoire />
        <AppChamp v-model="jour" etiquette="Jour" type="date" obligatoire :min="aujourdhuiIso()" />
        <AppChamp v-model="heure" etiquette="Heure de début" type="time" obligatoire step="900" />
      </div>
      <div class="flex flex-col">
        <span class="text-[13px] font-semibold">Paiement accepté <span class="text-erreur" aria-hidden="true">*</span></span>
        <AppCase v-model="especes" texte="Espèces, le jour même" />
        <AppCase v-model="carte" texte="Carte sur rafals (SIRET vérifié et paiement par carte activé)" />
      </div>
      <p class="text-[13px] text-texte-doux">
        Si {{ avec }} accepte, un rendez-vous confirmé est créé dans votre agenda, même hors de votre semaine type. Par carte :
        5 % pour rafals, versement 48 h après.
      </p>
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    </div>
    <template #pied>
      <AppBouton variante="secondaire" @click="emit('fermer')">Fermer</AppBouton>
      <AppBouton :occupe="occupe" @click="envoyer">Envoyer la proposition</AppBouton>
    </template>
  </AppFenetre>
</template>
