<script setup lang="ts">
// Mes devis › Mes demandes, côté client (.doc/ihm/RM-DEVIS-IHM.md ; RM-DEVIS.md) : chaque demande et son devis, avec
// les actions permises à ce moment-là (accepter, autre date, refuser, payer le solde, signaler un problème, annuler).
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { formaterDate } from '../../outils/dates'
import { type AvecPaiement, type DemandeVisible, MOYENS_DIRECTS, arrhesPayees, badgeDemande } from '../../outils/devis'
import { montant } from '../../outils/paiements'
import FenetreTexte, { type DemandeTexte } from '../FenetreTexte.vue'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBadge from '../ui/AppBadge.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppFenetre from '../ui/AppFenetre.vue'
import AppSection from '../ui/AppSection.vue'
import FenetreAccepterDevis from './FenetreAccepterDevis.vue'
import TableauDevis from './TableauDevis.vue'

defineProps<{ demandes: DemandeVisible[] }>()
const emit = defineEmits<{ maj: [] }>()
const routeur = useRouter()
const { afficherMessage } = useMessage()

const aAccepter = ref<DemandeVisible | null>(null)
const aEcrire = ref<DemandeTexte | null>(null)
const aAnnuler = ref<DemandeVisible | null>(null)

const autreDate = (d: DemandeVisible): DemandeTexte => ({
  titre: 'Demander une autre date',
  explication: `${d.autre.nom} pourra changer les dates ; le reste du devis ne change pas.`,
  etiquette: 'Les dates qui vous iraient', aide: 'ex. « Je suis absente cette semaine-là, plutôt fin octobre »',
  chemin: `/api/moi/devis/${d.devis?.id}/autre-date`, cle: 'texte', bouton: 'Envoyer',
  reussite: `Demande envoyée : ${d.autre.nom} va proposer d'autres dates.`,
})
const refuser = (d: DemandeVisible): DemandeTexte => ({
  titre: 'Refuser ce devis ?', explication: `${d.autre.nom} est prévenu.`, etiquette: 'Pourquoi ?', aide: 'ex. « Trop cher »',
  chemin: `/api/moi/devis/${d.devis?.id}/refuser`, cle: 'motif', bouton: 'Refuser', danger: true, facultatif: true,
  reussite: `Devis refusé : ${d.autre.nom} est prévenu.`,
})
const probleme = (d: DemandeVisible): DemandeTexte => ({
  titre: 'Signaler un problème', explication: `L'administrateur de rafals regarde ; ${d.autre.nom} est prévenu.`,
  etiquette: 'Le problème', aide: 'ex. « Le muret penche de 5 cm »', chemin: `/api/moi/devis/${d.devis?.id}/probleme`,
  cle: 'texte', bouton: 'Signaler', danger: true, reussite: "Problème signalé : l'administrateur va regarder.",
})

async function action(chemin: string, reussite: string) {
  try {
    await appelerServeur(chemin, {})
    afficherMessage(reussite)
    emit('maj')
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}
async function payerSolde(d: DemandeVisible) {
  try {
    const reponse = await appelerServeur<AvecPaiement>(`/api/moi/devis/${d.devis?.id}/payer-solde`, {})
    if (reponse.paiement_adresse) window.location.href = reponse.paiement_adresse
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}
async function annulerDevis() {
  const d = aAnnuler.value
  aAnnuler.value = null
  if (d?.devis) await action(`/api/moi/devis/${d.devis.id}/annuler`, `Devis annulé : ${d.autre.nom} est prévenu.`)
}
</script>

<template>
  <AppSection v-if="!demandes.length">
    <p class="text-texte-doux">Aucune demande de devis.</p>
    <div><AppBouton @click="routeur.push('/trouver')">Trouver un prestataire</AppBouton></div>
  </AppSection>

  <AppSection v-for="d in demandes" :key="d.id" :titre="`${d.titre} · ${d.autre.nom}`">
    <template #action><AppBadge :etat="badgeDemande(d, 'client').etat">{{ badgeDemande(d, 'client').texte }}</AppBadge></template>
    <p class="text-[14px] text-texte-doux">
      Votre demande du {{ formaterDate(d.cree_le) }} : « {{ d.texte }} »<template v-if="d.nombre_photos"> · {{ d.nombre_photos }} photo{{ d.nombre_photos > 1 ? 's' : '' }}</template><template v-if="d.lieu"> · {{ d.lieu }}</template>
    </p>

    <template v-if="d.statut === 'envoyee'">
      <p class="text-[14px]">{{ d.autre.nom }} n'a pas encore répondu.</p>
      <div><AppBouton variante="danger" @click="action(`/api/moi/demandes-devis/${d.id}/annuler`, 'Demande annulée.')">Annuler la demande</AppBouton></div>
    </template>
    <AppAlerte v-else-if="d.statut === 'declinee'">
      {{ d.autre.nom }} ne peut pas faire ce devis.<template v-if="d.motif"> Motif : « {{ d.motif }} ».</template>
    </AppAlerte>

    <template v-if="d.devis">
      <TableauDevis :devis="d.devis" :nom-prestataire="d.autre.nom" />
      <p v-if="d.autre.telephone" class="text-[14px]"><span class="text-texte-doux">Téléphone de {{ d.autre.nom }} :</span> {{ d.autre.telephone }}</p>

      <div v-if="d.devis.statut === 'envoye'" class="flex flex-wrap gap-2">
        <AppBouton @click="aAccepter = d">Accepter…</AppBouton>
        <AppBouton variante="secondaire" @click="aEcrire = autreDate(d)">Demander une autre date…</AppBouton>
        <AppBouton variante="danger" @click="aEcrire = refuser(d)">Refuser…</AppBouton>
      </div>
      <AppAlerte v-else-if="d.devis.statut === 'autre_date'" etat="attente">
        Vous avez demandé : « {{ d.devis.message }} ». {{ d.autre.nom }} va proposer d'autres dates.
      </AppAlerte>

      <template v-else-if="d.devis.statut === 'accepte'">
        <AppAlerte etat="ok">
          Accepté le {{ formaterDate(d.devis.accepte_le ?? d.devis.envoye_le) }}<template v-if="d.devis.mode_paiement === 'direct'">, payé en direct à {{ d.autre.nom }}</template><template v-else-if="arrhesPayees(d.devis)">, arrhes payées par carte</template>.
        </AppAlerte>
        <div class="flex flex-wrap gap-2">
          <AppBouton v-if="!d.devis.probleme" variante="secondaire" @click="aEcrire = probleme(d)">Signaler un problème…</AppBouton>
          <AppBouton variante="danger" @click="aAnnuler = d">Annuler le devis…</AppBouton>
        </div>
      </template>

      <template v-else-if="d.devis.statut === 'termine'">
        <AppAlerte etat="attente">
          {{ d.autre.nom }} a terminé le {{ formaterDate(d.devis.termine_le ?? d.devis.envoye_le) }}.
          {{ d.devis.mode_paiement === 'carte' ? 'Vérifiez le travail, puis payez le solde.' : `Réglez le montant restant directement à ${d.autre.nom}.` }}
        </AppAlerte>
        <div class="flex flex-wrap gap-2">
          <AppBouton v-if="d.devis.mode_paiement === 'carte'" @click="payerSolde(d)">Payer le solde : {{ montant(d.devis.solde_centimes) }}</AppBouton>
          <AppBouton v-if="!d.devis.probleme" variante="danger" @click="aEcrire = probleme(d)">Signaler un problème…</AppBouton>
        </div>
      </template>

      <AppAlerte v-else-if="d.devis.statut === 'paye'" etat="ok">
        Payé le {{ formaterDate(d.devis.paye_le ?? d.devis.envoye_le) }}<template v-if="d.devis.moyen_direct"> ({{ MOYENS_DIRECTS[d.devis.moyen_direct] }}, en direct)</template>. Merci !
      </AppAlerte>
      <AppAlerte v-else-if="d.devis.statut === 'annule_prestataire'">
        {{ d.autre.nom }} a annulé le devis. Motif : « {{ d.devis.message }} ».
        <template v-if="arrhesPayees(d.devis)">Vos arrhes vous sont rendues en entier.</template>
      </AppAlerte>
      <p v-else-if="d.devis.statut === 'expire'" class="text-[14px] text-texte-doux">
        Ce devis a expiré : demandez-en un nouveau depuis l'annonce si vous êtes toujours intéressé.
      </p>

      <AppAlerte v-if="d.devis.probleme" etat="attente">
        Problème signalé le {{ formaterDate(d.devis.probleme_le ?? d.devis.envoye_le) }} : « {{ d.devis.probleme }} ». L'administrateur de rafals regarde.
      </AppAlerte>
    </template>
  </AppSection>

  <FenetreAccepterDevis :demande="aAccepter" @fermer="aAccepter = null" @fait="(aAccepter = null), emit('maj')" />
  <FenetreTexte :demande="aEcrire" @fermer="aEcrire = null" @fait="(aEcrire = null), emit('maj')" />
  <AppFenetre :ouverte="aAnnuler !== null" :titre="`Annuler le devis ${aAnnuler?.devis?.numero ?? ''} ?`" @fermer="aAnnuler = null">
    <template v-if="aAnnuler">
      {{ aAnnuler.autre.nom }} est prévenu et les jours des travaux se libèrent.
      <template v-if="aAnnuler.devis && arrhesPayees(aAnnuler.devis)">Il garde les arrhes ({{ montant(aAnnuler.devis?.arrhes_centimes ?? 0) }}).</template>
    </template>
    <template #pied>
      <AppBouton variante="danger" @click="annulerDevis">Annuler le devis</AppBouton>
      <AppBouton variante="secondaire" @click="aAnnuler = null">Garder</AppBouton>
    </template>
  </AppFenetre>
</template>
