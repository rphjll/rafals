<script setup lang="ts">
// Une proposition dans le fil d'une conversation (.doc/ihm/RM-MESSAGES-IHM.md ; RM-DEMANDES.md) : prix, jour, heure,
// durée, lieu, paiement. Le client : [Accepter…] · [Négocier le prix] · [Refuser]. Le prestataire : [Retirer], et
// [Accepter 50,00 €] · [Refuser ce prix] quand le client a proposé un autre prix.
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { formaterDateHeure } from '../../outils/dates'
import { badgeProposition, prix, type PropositionVisible, quandEtOu, textePaiement } from '../../outils/messagerie'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBadge from '../ui/AppBadge.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppChamp from '../ui/AppChamp.vue'
import AppChoix from '../ui/AppChoix.vue'
import AppFenetre from '../ui/AppFenetre.vue'

const props = defineProps<{ proposition: PropositionVisible; cote: 'client' | 'prestataire'; avec: string }>()
const emit = defineEmits<{ change: [] }>()
const routeur = useRouter()
const { afficherMessage } = useMessage()

const erreur = ref('')
const occupe = ref(false)
const fenetre = ref<'accepter' | 'negocier' | null>(null)
const mode = ref<'carte' | 'especes'>('especes')
const nouveauPrix = ref('')

const badge = computed(() => badgeProposition(props.proposition))
const enAttente = computed(() => props.proposition.statut === 'en_attente')
const negociation = computed(() => props.proposition.negociation)
const texteAccepter = computed(() => `Accepter ${prix(props.proposition.prix_centimes)} · ${formaterDateHeure(props.proposition.debut)}`)
const modes = computed(() => [
  { valeur: 'especes' as const, texte: 'Espèces, le jour même',
    raisonVerrou: props.proposition.modes_de_paiement.includes('especes') ? undefined : `${props.avec} n'accepte que la carte pour ce rendez-vous.` },
  { valeur: 'carte' as const, texte: 'Carte, maintenant',
    raisonVerrou: props.proposition.modes_de_paiement.includes('carte') ? undefined : `${props.avec} ne peut pas être payé par carte : espèces seulement.` },
])

function ouvrir(quoi: 'accepter' | 'negocier') {
  erreur.value = ''
  mode.value = props.proposition.modes_de_paiement[0] ?? 'especes'
  nouveauPrix.value = ''
  fenetre.value = quoi
}

async function envoyer(chemin: string, donnees: unknown, reussite: string) {
  erreur.value = ''
  occupe.value = true
  try {
    const reponse = await appelerServeur<{ paiement_adresse?: string | null }>(chemin, donnees)
    fenetre.value = null
    if (reponse.paiement_adresse) {
      window.location.href = reponse.paiement_adresse // la page de paiement de Stripe (30 minutes pour payer)
      return
    }
    afficherMessage(reussite)
    emit('change')
  } catch (e) {
    erreur.value = messageErreur(e) // ex. « Vous avez déjà un rendez-vous à cette heure-là… »
  } finally {
    occupe.value = false
  }
}

const accepter = () =>
  envoyer(`/api/propositions/${props.proposition.id}/accepter`, { mode_paiement: mode.value }, `Rendez-vous confirmé · ${formaterDateHeure(props.proposition.debut)}`)
const refuser = () => envoyer(`/api/propositions/${props.proposition.id}/refuser`, {}, 'Proposition refusée.')
const retirer = () => envoyer(`/api/propositions/${props.proposition.id}/retirer`, {}, 'Proposition retirée.')
function negocier() {
  const euros = Number(nouveauPrix.value.replace(',', '.'))
  if (!nouveauPrix.value.trim() || !Number.isFinite(euros) || euros <= 0) {
    erreur.value = 'Indiquez votre prix en euros (ex. 50).'
    return
  }
  envoyer(`/api/propositions/${props.proposition.id}/negocier`, { prix_centimes: Math.round(euros * 100) }, `Prix proposé à ${props.avec}.`)
}
const repondreAuPrix = (oui: boolean) =>
  envoyer(`/api/negociations/${negociation.value?.id}/${oui ? 'accepter' : 'refuser'}`, {}, oui ? 'Prix accepté : le client n’a plus qu’à confirmer.' : 'Vous gardez votre prix.')
</script>

<template>
  <div
    class="flex flex-col gap-2 rounded-carte p-4"
    :class="enAttente ? 'bg-teinte-vert text-teinte-vert-texte' : 'bg-fond opacity-80'"
  >
    <div class="flex flex-wrap items-center justify-between gap-2">
      <span class="text-[13px] font-bold">
        {{ cote === 'client' ? `Proposition de ${avec}` : 'Votre proposition' }}<template v-if="proposition.demande_titre">
          · « {{ proposition.demande_titre }} »</template>
      </span>
      <AppBadge :etat="badge.etat">{{ badge.texte }}</AppBadge>
    </div>
    <div class="flex flex-wrap items-center justify-between gap-2">
      <b class="text-[17px]">{{ quandEtOu(proposition, cote) }}</b>
      <b class="rounded-full bg-primaire px-4 py-1 text-xl whitespace-nowrap text-primaire-texte tabular-nums">{{ prix(proposition.prix_centimes) }}</b>
    </div>
    <span class="text-[13px]">Paiement : {{ textePaiement(proposition) }}</span>

    <!-- Le client a proposé un autre prix : le prestataire accepte ou refuse ce prix -->
    <div v-if="enAttente && negociation" class="flex flex-col gap-2 rounded-rafals bg-attente-doux p-3 text-texte">
      <span>
        Prix proposé par {{ cote === 'client' ? 'vous' : avec }} : <b>{{ prix(negociation.prix_centimes) }}</b>
        au lieu de {{ prix(proposition.prix_centimes) }}. Le jour, l'heure et le reste ne changent pas.
      </span>
      <div v-if="cote === 'prestataire'" class="flex flex-wrap gap-2">
        <AppBouton :occupe="occupe" @click="repondreAuPrix(true)">Accepter {{ prix(negociation.prix_centimes) }}</AppBouton>
        <AppBouton variante="danger" :occupe="occupe" @click="repondreAuPrix(false)">Refuser ce prix</AppBouton>
      </div>
      <span v-else class="text-[13px] text-texte-doux">En attente de la réponse de {{ avec }}.</span>
    </div>

    <div v-if="enAttente && cote === 'client'" class="flex flex-wrap gap-2">
      <AppBouton @click="ouvrir('accepter')">{{ texteAccepter }}</AppBouton>
      <AppBouton v-if="!negociation" variante="secondaire" @click="ouvrir('negocier')">Négocier le prix</AppBouton>
      <AppBouton
        v-else
        variante="verrouille"
        :raison-verrou="`Vous avez déjà proposé ${prix(negociation.prix_centimes)} : attendez la réponse de ${avec}.`"
      >
        Négocier le prix
      </AppBouton>
      <AppBouton variante="danger" :occupe="occupe" @click="refuser">Refuser</AppBouton>
    </div>
    <div v-if="enAttente && cote === 'prestataire'">
      <AppBouton variante="danger" :occupe="occupe" @click="retirer">Retirer ma proposition</AppBouton>
    </div>
    <div v-if="proposition.statut === 'acceptee' && proposition.rendez_vous_id">
      <AppBouton variante="secondaire" @click="routeur.push(cote === 'client' ? '/rendez-vous' : '/mon-agenda')">Voir le rendez-vous</AppBouton>
    </div>
    <AppAlerte v-if="erreur && !fenetre">{{ erreur }}</AppAlerte>

    <AppFenetre :ouverte="fenetre === 'accepter'" titre="Confirmer le rendez-vous" @fermer="fenetre = null">
      <div class="flex flex-col gap-3 text-texte">
        <p>
          <b>{{ prix(proposition.prix_centimes) }}</b> · {{ quandEtOu(proposition, 'client') }}, avec {{ avec }}.
        </p>
        <AppChoix v-model="mode" etiquette="Comment payez-vous ?" :options="modes" obligatoire />
        <AppAlerte v-if="mode === 'carte'" etat="neutre">
          Vous payez maintenant sur la page sécurisée de Stripe. Vous êtes remboursé en entier si {{ avec }} annule.
        </AppAlerte>
        <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      </div>
      <template #pied>
        <AppBouton variante="secondaire" @click="fenetre = null">Fermer</AppBouton>
        <AppBouton :occupe="occupe" @click="accepter">{{ texteAccepter }}</AppBouton>
      </template>
    </AppFenetre>

    <AppFenetre :ouverte="fenetre === 'negocier'" titre="Négocier le prix" @fermer="fenetre = null">
      <div class="flex flex-col gap-3 text-texte">
        <p>{{ avec }} propose {{ prix(proposition.prix_centimes) }}. Le jour, l'heure, la durée et le lieu ne changent pas.</p>
        <AppChamp v-model="nouveauPrix" etiquette="Votre prix (€)" obligatoire inputmode="decimal" placeholder="ex. 50" />
        <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      </div>
      <template #pied>
        <AppBouton variante="secondaire" @click="fenetre = null">Fermer</AppBouton>
        <AppBouton :occupe="occupe" @click="negocier">Proposer ce prix</AppBouton>
      </template>
    </AppFenetre>
  </div>
</template>
