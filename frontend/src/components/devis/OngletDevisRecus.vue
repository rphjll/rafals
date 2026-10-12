<script setup lang="ts">
// Mes devis › Devis reçus, côté prestataire (.doc/ihm/RM-DEVIS-IHM.md ; RM-DEVIS.md) : les demandes (texte, photos,
// lieu, téléphone du client), écrire ou décliner, proposer d'autres dates, travail terminé, payé en direct, annuler.
import { ref } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { aParis } from '../../outils/agenda'
import { formaterDate } from '../../outils/dates'
import { type DemandeVisible, MOYENS_DIRECTS, arrhesPayees, badgeDemande, jourDevis } from '../../outils/devis'
import { montant } from '../../outils/paiements'
import type { MoyenDirect } from '../../outils/factures'
import FenetrePayeDirect from '../FenetrePayeDirect.vue'
import FenetreTexte, { type DemandeTexte } from '../FenetreTexte.vue'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBadge from '../ui/AppBadge.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppChamp from '../ui/AppChamp.vue'
import AppFenetre from '../ui/AppFenetre.vue'
import AppSection from '../ui/AppSection.vue'
import FenetreEcrireDevis from './FenetreEcrireDevis.vue'
import TableauDevis from './TableauDevis.vue'

defineProps<{ demandes: DemandeVisible[]; factureTva: boolean; nomPrestataire: string }>()
const emit = defineEmits<{ maj: [] }>()
const { afficherMessage } = useMessage()
const aujourdhui = aParis(new Date().toISOString()).jour

const aRepondre = ref<DemandeVisible | null>(null)
const aEcrire = ref<DemandeTexte | null>(null)

const decliner = (d: DemandeVisible): DemandeTexte => ({
  titre: 'Décliner la demande ?', explication: `${d.autre.nom} est prévenu.`, etiquette: 'Pourquoi ?',
  aide: 'ex. « Je ne fais pas ce genre de travaux »', chemin: `/api/moi/prestataire/demandes-devis/${d.id}/decliner`,
  cle: 'motif', bouton: 'Décliner', danger: true, facultatif: true, reussite: 'Demande déclinée : le client est prévenu.',
})
const annuler = (d: DemandeVisible): DemandeTexte => ({
  titre: `Annuler le devis ${d.devis?.numero} ?`,
  explication: `Les jours des travaux redeviennent libres.${d.devis && arrhesPayees(d.devis) ? ' Les arrhes payées par carte sont rendues en entier au client (reprises sur vos prochains paiements).' : ''}`,
  etiquette: 'Motif', aide: 'ex. « Chantier impossible »', chemin: `/api/moi/prestataire/devis/${d.devis?.id}/annuler`,
  cle: 'motif', bouton: 'Annuler le devis', danger: true, reussite: 'Devis annulé : le client est prévenu.',
})

async function terminer(d: DemandeVisible) {
  try {
    await appelerServeur(`/api/moi/prestataire/devis/${d.devis?.id}/termine`, {})
    afficherMessage('Travail déclaré terminé : le client est prévenu.')
    emit('maj')
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}

// ---------- Proposer d'autres dates ----------
const aDater = ref<DemandeVisible | null>(null)
const debut = ref('')
const fin = ref('')
const erreurDates = ref('')
function ouvrirDates(d: DemandeVisible) {
  aDater.value = d
  debut.value = d.devis?.travaux_debut ?? ''
  fin.value = d.devis?.travaux_fin ?? ''
  erreurDates.value = ''
}
async function envoyerDates() {
  erreurDates.value = ''
  try {
    await appelerServeur(`/api/moi/prestataire/devis/${aDater.value?.devis?.id}/dates`, { travaux_debut: debut.value, travaux_fin: fin.value })
    aDater.value = null
    afficherMessage('Nouvelles dates envoyées au client.')
    emit('maj')
  } catch (e) {
    erreurDates.value = messageErreur(e)
  }
}

// ---------- Payé en direct ----------
const aEncaisser = ref<DemandeVisible | null>(null)
async function confirmerPaye(moyen: MoyenDirect) {
  const d = aEncaisser.value
  aEncaisser.value = null
  try {
    await appelerServeur(`/api/moi/prestataire/devis/${d?.devis?.id}/paye`, { moyen })
    afficherMessage('Devis payé : la facture est créée.')
    emit('maj')
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}
</script>

<template>
  <AppSection v-if="!demandes.length">
    <p class="text-texte-doux">Aucune demande de devis pour l'instant : vos clients vous en demandent depuis votre page, avec [Demander un devis].</p>
  </AppSection>

  <AppSection v-for="d in demandes" :key="d.id" :titre="`${d.titre} · ${d.autre.nom}`">
    <template #action><AppBadge :etat="badgeDemande(d, 'prestataire').etat">{{ badgeDemande(d, 'prestataire').texte }}</AppBadge></template>
    <p class="whitespace-pre-line">« {{ d.texte }} »</p>
    <div v-if="d.nombre_photos" class="flex flex-wrap gap-2">
      <a v-for="n in d.nombre_photos" :key="n" :href="`/api/demandes-devis/${d.id}/photos/${n}`" target="_blank" rel="noopener">
        <img :src="`/api/demandes-devis/${d.id}/photos/${n}`" :alt="`Photo ${n} de la demande`" class="size-24 rounded-rafals border border-bord object-cover" />
      </a>
    </div>
    <p class="text-[14px] text-texte-doux">
      <template v-if="d.lieu">{{ d.lieu }} · </template><template v-if="d.autre.telephone">{{ d.autre.telephone }} · </template>reçue le {{ formaterDate(d.cree_le) }}
    </p>

    <div v-if="d.statut === 'envoyee'" class="flex flex-wrap gap-2">
      <AppBouton @click="aRepondre = d">Écrire le devis…</AppBouton>
      <AppBouton variante="danger" @click="aEcrire = decliner(d)">Décliner…</AppBouton>
    </div>
    <p v-else-if="d.statut === 'declinee'" class="text-[14px] text-texte-doux">Vous avez décliné.<template v-if="d.motif"> Motif : « {{ d.motif }} ».</template></p>
    <p v-else-if="d.statut === 'annulee'" class="text-[14px] text-texte-doux">Le client a annulé sa demande.</p>

    <template v-if="d.devis">
      <TableauDevis :devis="d.devis" :nom-prestataire="nomPrestataire" />
      <p v-if="d.devis.statut === 'envoye'" class="text-[14px] text-texte-doux">En attente de la réponse du client.</p>
      <template v-else-if="d.devis.statut === 'autre_date'">
        <AppAlerte etat="attente">Le client demande : « {{ d.devis.message }} »</AppAlerte>
        <div><AppBouton @click="ouvrirDates(d)">Proposer d'autres dates…</AppBouton></div>
      </template>
      <template v-else-if="d.devis.statut === 'accepte'">
        <AppAlerte etat="ok">
          Accepté, {{ d.devis.mode_paiement === 'carte' ? (arrhesPayees(d.devis) ? 'arrhes payées par carte' : 'payé par carte') : 'payé en direct' }} ·
          jours bloqués dans votre agenda.
        </AppAlerte>
        <div class="flex flex-wrap gap-2">
          <AppBouton
            v-if="aujourdhui < d.devis.travaux_debut"
            variante="verrouille"
            :raison-verrou="`Vous pourrez déclarer le travail terminé à partir du ${jourDevis(d.devis.travaux_debut)}.`"
          >
            Travail terminé
          </AppBouton>
          <AppBouton v-else @click="terminer(d)">Travail terminé</AppBouton>
          <AppBouton v-if="d.devis.mode_paiement === 'direct'" variante="secondaire" @click="aEncaisser = d">Payé…</AppBouton>
          <AppBouton variante="danger" @click="aEcrire = annuler(d)">Annuler le devis…</AppBouton>
        </div>
      </template>
      <template v-else-if="d.devis.statut === 'termine'">
        <p v-if="d.devis.mode_paiement === 'carte'" class="text-[14px] text-texte-doux">
          En attente du solde ({{ montant(d.devis.solde_centimes) }}) : le client le paie après avoir vérifié le travail.
        </p>
        <div v-else><AppBouton @click="aEncaisser = d">Payé…</AppBouton></div>
      </template>
      <AppAlerte v-else-if="d.devis.statut === 'paye'" etat="ok">
        Payé le {{ formaterDate(d.devis.paye_le ?? d.devis.envoye_le) }}<template v-if="d.devis.moyen_direct"> ({{ MOYENS_DIRECTS[d.devis.moyen_direct] }})</template>.
      </AppAlerte>
      <p v-else-if="d.devis.statut === 'refuse'" class="text-[14px] text-texte-doux">
        Refusé par le client<template v-if="d.devis.message"> : « {{ d.devis.message }} »</template>.
      </p>
      <p v-else-if="d.devis.statut === 'annule_client'" class="text-[14px] text-texte-doux">
        Le client a annulé.<template v-if="arrhesPayees(d.devis)"> Vous gardez les arrhes ({{ montant(d.devis.arrhes_centimes) }}).</template>
      </p>
      <AppAlerte v-if="d.devis.probleme" etat="attente">
        Problème signalé par le client : « {{ d.devis.probleme }} ». L'administrateur de rafals regarde.
      </AppAlerte>
    </template>
  </AppSection>

  <FenetreEcrireDevis :demande="aRepondre" :facture-tva="factureTva" @fermer="aRepondre = null" @envoye="(aRepondre = null), emit('maj')" />
  <FenetreTexte :demande="aEcrire" @fermer="aEcrire = null" @fait="(aEcrire = null), emit('maj')" />

  <AppFenetre :ouverte="aDater !== null" titre="Proposer d'autres dates" @fermer="aDater = null">
    <div class="flex flex-col gap-3 text-texte">
      <div class="grid gap-2 sm:grid-cols-2">
        <AppChamp v-model="debut" etiquette="Travaux du" obligatoire type="date" />
        <AppChamp v-model="fin" etiquette="au" obligatoire type="date" />
      </div>
      <p class="text-[13.5px] text-texte-doux">Le reste du devis ne change pas ; il revient au client.</p>
      <AppAlerte v-if="erreurDates">{{ erreurDates }}</AppAlerte>
    </div>
    <template #pied>
      <AppBouton @click="envoyerDates">Envoyer</AppBouton>
      <AppBouton variante="secondaire" @click="aDater = null">Annuler</AppBouton>
    </template>
  </AppFenetre>

  <FenetrePayeDirect
    :demande="aEncaisser?.devis ? { nom: aEncaisser.autre.nom, centimes: aEncaisser.devis.ttc_centimes } : null"
    @fermer="aEncaisser = null"
    @confirmer="confirmerPaye"
  />
</template>
