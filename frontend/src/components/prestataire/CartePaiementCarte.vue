<script setup lang="ts">
// Mon activité › Paiement par carte (.doc/ihm/RM-PROPOSER-IHM.md ; RM-PAIEMENTS.md, lot 5.2) : sans SIRET vérifié,
// à activer (case du mandat de facturation, puis la page de Stripe), en vérification par Stripe, activé.
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { formaterDate } from '../../outils/dates'
import type { EtatCarte } from '../../outils/paiements'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBadge from '../ui/AppBadge.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppCase from '../ui/AppCase.vue'
import AppSection from '../ui/AppSection.vue'

const route = useRoute()
const routeur = useRouter()
const { afficherMessage } = useMessage()
const etat = ref<EtatCarte | null>(null)
const mandat = ref(false)
const erreur = ref('')
const envoiEnCours = ref(false)

async function charger(apresStripe = false) {
  try {
    etat.value = await appelerServeur<EtatCarte>('/api/moi/prestataire/paiement-carte')
    if (apresStripe) afficherMessage(etat.value.pret ? 'Paiement par carte activé.' : 'Toujours en cours de vérification par Stripe.')
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
onMounted(async () => {
  await charger()
  // Retour de la page de Stripe (?stripe=retour) : message, puis l'adresse redevient propre
  if (route.query.stripe) {
    if (route.query.stripe === 'retour' && etat.value && !etat.value.pret) afficherMessage('Merci : Stripe vérifie vos informations.')
    routeur.replace({ query: {} })
  }
})

const badge = computed(() => {
  const e = etat.value
  if (!e || !e.siret_verifie) return { etat: 'neutre' as const, texte: 'espèces seulement' }
  if (e.pret) return { etat: 'ok' as const, texte: 'activé' }
  if (e.compte_cree) return { etat: 'attente' as const, texte: 'vérification par Stripe' }
  return { etat: 'neutre' as const, texte: 'pas activé' }
})

/** Vers la page de Stripe (identité et RIB) : la première fois avec l'accord du mandat de facturation */
async function allerChezStripe() {
  erreur.value = ''
  envoiEnCours.value = true
  try {
    const { adresse } = await appelerServeur<{ adresse: string }>('/api/moi/prestataire/paiement-carte', { mandat: mandat.value })
    window.location.href = adresse
  } catch (e) {
    erreur.value = messageErreur(e) // ex. « Cochez la case : vous acceptez que rafals fasse vos factures à votre place. »
    envoiEnCours.value = false
  }
}
</script>

<template>
  <AppSection v-if="etat" titre="Paiement par carte">
    <template v-if="etat.ouvert" #action><AppBadge :etat="badge.etat">{{ badge.texte }}</AppBadge></template>

    <p v-if="!etat.ouvert" class="text-[14px] text-texte-doux">Le paiement par carte arrivera bientôt sur rafals.</p>

    <template v-else-if="!etat.siret_verifie">
      <p class="text-[14px] text-texte-doux">Payé par carte, l'argent arrive sur votre compte en banque 48 h après chaque rendez-vous.</p>
      <div>
        <AppBouton variante="verrouille" raison-verrou="Il faut d'abord un SIRET vérifié par l'État : ajoutez-le avec [Modifier mon profil].">
          Activer le paiement par carte
        </AppBouton>
      </div>
    </template>

    <template v-else-if="etat.pret">
      <p>Vos annonces qui acceptent la carte la proposent aux clients.</p>
      <p class="text-[13.5px] text-texte-doux">
        <template v-if="etat.mandat_facturation_le">Mandat de facturation accepté le {{ formaterDate(etat.mandat_facturation_le) }}. </template>
        Vos paiements : « Mon agenda › Paiements ».
      </p>
    </template>

    <template v-else-if="etat.compte_cree">
      <AppAlerte etat="attente">
        Stripe vérifie vos informations : cela prend de quelques minutes à 2 jours. Vos annonces proposent les espèces en attendant.
      </AppAlerte>
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <div class="flex flex-wrap gap-2">
        <AppBouton variante="secondaire" :occupe="envoiEnCours" @click="allerChezStripe">Continuer chez Stripe</AppBouton>
        <AppBouton variante="secondaire" @click="charger(true)">Actualiser</AppBouton>
      </div>
    </template>

    <template v-else>
      <p class="text-[14px] text-texte-doux">
        Vos clients paient en réservant, sur la page sécurisée de Stripe. L'argent reste bloqué jusqu'au rendez-vous, puis
        arrive sur votre compte en banque 48 h après.
      </p>
      <dl class="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 text-[14px]">
        <dt class="text-texte-doux">Exemple</dt>
        <dd>Coupe à 50 € : rafals garde 2,50 € (5 %), Stripe 1,00 € de frais, vous recevez <b>46,50 €</b>.</dd>
        <dt class="text-texte-doux">Remboursements</dt>
        <dd>Si vous refusez, annulez ou êtes absent, le client est remboursé et les frais de Stripe restent à votre charge.</dd>
      </dl>
      <AppCase v-if="!etat.mandat_facturation_le" v-model="mandat" texte="J'accepte que rafals fasse mes factures à ma place, à mon nom (mandat de facturation). *" />
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <div><AppBouton :occupe="envoiEnCours" @click="allerChezStripe">Activer le paiement par carte</AppBouton></div>
      <p class="text-[13.5px] text-texte-doux">Vous allez sur la page de Stripe pour donner votre identité et votre RIB, puis vous revenez ici.</p>
    </template>
  </AppSection>
</template>
