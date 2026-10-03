<script setup lang="ts">
// Fenêtre « Accepter le devis D-2026-0002 ? » (.doc/ihm/RM-DEVIS-IHM.md ; RM-DEVIS.md) : par carte sur rafals (arrhes
// payées maintenant sur la page de Stripe) ou en direct avec le prestataire (rafals ne prend rien).
import { computed, ref, watch } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { type AvecPaiement, type DemandeVisible, jourMois } from '../../outils/devis'
import { montant } from '../../outils/paiements'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppChoix from '../ui/AppChoix.vue'
import AppFenetre from '../ui/AppFenetre.vue'

const props = defineProps<{ demande: DemandeVisible | null }>()
const emit = defineEmits<{ fermer: []; fait: [] }>()
const { afficherMessage } = useMessage()
const mode = ref<'carte' | 'direct'>('carte')
const erreur = ref('')
const envoiEnCours = ref(false)
const devis = computed(() => props.demande?.devis ?? null)
watch(devis, (d) => ((mode.value = d?.modes_possibles[0] ?? 'carte'), (erreur.value = '')))

const nom = computed(() => props.demande?.autre.nom ?? '')
const bouton = computed(() => {
  const d = devis.value
  if (!d) return ''
  return mode.value === 'carte' && d.arrhes_centimes ? `Accepter et payer ${montant(d.arrhes_centimes)} d'arrhes` : 'Accepter le devis'
})

async function accepter() {
  const d = devis.value
  if (!d) return
  erreur.value = ''
  envoiEnCours.value = true
  try {
    const reponse = await appelerServeur<AvecPaiement>(`/api/moi/devis/${d.id}/accepter`, { mode_paiement: mode.value })
    if (reponse.paiement_adresse) {
      window.location.href = reponse.paiement_adresse // la page de paiement de Stripe ; retour sur « Mes devis »
      return
    }
    afficherMessage(`Devis accepté : ${nom.value} est prévenu.`)
    emit('fait')
  } catch (e) {
    erreur.value = messageErreur(e)
  } finally {
    envoiEnCours.value = false
  }
}
</script>

<template>
  <AppFenetre :ouverte="devis !== null" :titre="`Accepter le devis ${devis?.numero ?? ''} ?`" @fermer="emit('fermer')">
    <div v-if="demande && devis" class="flex flex-col gap-3 text-texte">
      <p class="text-[14px] text-texte-doux">
        {{ demande.titre }} avec {{ nom }} · {{ montant(devis.ttc_centimes) }} · travaux du {{ jourMois(devis.travaux_debut) }}
        au {{ jourMois(devis.travaux_fin) }}.
      </p>
      <AppChoix
        v-model="mode"
        etiquette="Paiement"
        obligatoire
        :options="[
          { valeur: 'carte', texte: 'Par carte sur rafals', raisonVerrou: devis.modes_possibles.includes('carte') ? undefined : `${nom} ne prend pas la carte sur rafals.` },
          { valeur: 'direct', texte: `En direct avec ${nom}`, raisonVerrou: devis.modes_possibles.includes('direct') ? undefined : `${nom} se fait payer par carte sur rafals.` },
        ]"
      />
      <AppAlerte etat="neutre">
        <template v-if="mode === 'carte' && devis.arrhes_centimes">
          Arrhes : {{ montant(devis.arrhes_centimes) }} — payées maintenant sur la page sécurisée de Stripe, gardées par {{ nom }}
          si vous annulez. Le solde ({{ montant(devis.solde_centimes) }}) se paie après les travaux.
        </template>
        <template v-else-if="mode === 'carte'">Rien à payer maintenant : le total se paie par carte après les travaux.</template>
        <template v-else>Vous réglez {{ nom }} directement (espèces, chèque, virement). rafals ne prend rien.</template>
      </AppAlerte>
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    </div>
    <template #pied>
      <AppBouton :occupe="envoiEnCours" @click="accepter">{{ bouton }}</AppBouton>
      <AppBouton variante="secondaire" @click="emit('fermer')">Annuler</AppBouton>
    </template>
  </AppFenetre>
</template>
