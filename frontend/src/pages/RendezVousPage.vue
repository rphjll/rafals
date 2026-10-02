<script setup lang="ts">
// Mes rendez-vous, côté client (.doc/ihm/RM-RENDEZ-VOUS-IHM.md ; RM-RENDEZ-VOUS.md) : à venir (annuler, déplacer dans
// le délai du prestataire), puis passés et annulés. Retour de la page de paiement de Stripe (?paiement=fait|annule, lot 5.2).
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import AvisAffiche from '../components/avis/AvisAffiche.vue'
import FenetreAvis from '../components/avis/FenetreAvis.vue'
import ChoixHoraire from '../components/rendez-vous/ChoixHoraire.vue'
import FenetreTexte, { type DemandeTexte } from '../components/FenetreTexte.vue'
import LigneRendezVous from '../components/rendez-vous/LigneRendezVous.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppCarte from '../components/ui/AppCarte.vue'
import AppFenetre from '../components/ui/AppFenetre.vue'
import AppOnglets from '../components/ui/AppOnglets.vue'
import AppSection from '../components/ui/AppSection.vue'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'
import { aParis, heure, jourCourt } from '../outils/agenda'
import { montant } from '../outils/paiements'
import { type RendezVousVisible, absenceSignalable, aVenir, contestable, momentCourt, plage } from '../outils/rendez_vous'

const route = useRoute()
const routeur = useRouter()
const { compte, chargementFait } = useCompte()
const { afficherMessage } = useMessage()
const onglet = ref('a-venir')
const tous = ref<RendezVousVisible[] | null>(null)
const erreur = ref('')

async function charger() {
  if (!compte.value) return
  try {
    tous.value = await appelerServeur<RendezVousVisible[]>('/api/moi/rendez-vous')
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
onMounted(charger)
watch(compte, charger)

// ---------- Retour de la page de paiement de Stripe (lot 5.2) ----------
// « fait » : Stripe prévient rafals de son côté, parfois quelques secondes après ; on relit jusqu'à ce que ce soit arrivé.
// « annule » (le client est revenu sans payer) : la réservation est annulée aussitôt, l'horaire se libère.
const retourPaiement = ref<{ etat: 'ok' | 'attente'; texte: string } | null>(null)
let relecture: ReturnType<typeof setTimeout> | undefined
async function suivrePaiement(rdvId: number, essais = 0) {
  await charger()
  const r = tous.value?.find((x) => x.id === rdvId)
  if (r?.paiement?.statut === 'a_payer' && essais < 15) {
    retourPaiement.value = { etat: 'attente', texte: 'Paiement en cours de confirmation…' }
    relecture = setTimeout(() => suivrePaiement(rdvId, essais + 1), 2000)
    return
  }
  retourPaiement.value =
    r?.paiement?.statut === 'paye'
      ? { etat: 'ok', texte: r.statut === 'en_attente' ? `Paiement reçu : ${r.autre.nom} a 24 h pour accepter.` : 'Paiement reçu : votre rendez-vous est confirmé.' }
      : { etat: 'attente', texte: "Le paiement n'est pas encore confirmé : actualisez la page dans quelques minutes." }
}
async function abandonPaiement(rdvId: number) {
  try {
    await appelerServeur(`/api/moi/rendez-vous/${rdvId}/annuler`, {})
  } catch {
    // déjà annulée (par exemple au bout de 30 minutes) : rien à faire
  }
  retourPaiement.value = { etat: 'attente', texte: "Paiement non terminé : rien n'a été pris, la réservation est annulée." }
  await charger()
}
onMounted(() => {
  const rdvId = Number(route.query.rdv)
  if (!rdvId || !route.query.paiement) return
  if (route.query.paiement === 'fait') suivrePaiement(rdvId)
  else abandonPaiement(rdvId)
  routeur.replace({ query: {} })
})
onUnmounted(() => clearTimeout(relecture))

// À venir : le plus proche d'abord ; passés et annulés : le plus récent d'abord
const avenir = computed(() => (tous.value ?? []).filter((r) => aVenir(r)).sort((a, b) => a.debut.localeCompare(b.debut)))
const passes = computed(() => (tous.value ?? []).filter((r) => !aVenir(r)))
const dansLeDelai = (r: RendezVousVisible) => !r.annulable_jusqu_au || new Date() < new Date(r.annulable_jusqu_au)
const raisonHorsDelai = (r: RendezVousVisible) =>
  `Le délai d'annulation gratuite est passé : appelez ${r.autre.nom}${r.autre.telephone ? ` au ${r.autre.telephone}` : ''}.`

// ---------- Annuler ----------
const aAnnuler = ref<RendezVousVisible | null>(null)
async function annuler() {
  const r = aAnnuler.value
  if (!r) return
  try {
    await appelerServeur(`/api/moi/rendez-vous/${r.id}/annuler`, {})
    aAnnuler.value = null
    afficherMessage(
      r.paiement?.statut === 'paye' ? 'Rendez-vous annulé : remboursement en cours.' : r.statut === 'en_attente' ? 'Demande annulée.' : 'Rendez-vous annulé.',
    )
    await charger()
  } catch (e) {
    aAnnuler.value = null
    afficherMessage(messageErreur(e), 'erreur')
  }
}

// ---------- Absences (lot 4.6) ----------
const pasVenu = ref<RendezVousVisible | null>(null)
const aContester = ref<DemandeTexte | null>(null)
// [Je suis venu…] : la fenêtre commune à un seul texte
const contester = (chemin: string): DemandeTexte => ({
  titre: "Contester l'absence",
  explication: "Expliquez ce qui s'est passé : l'administrateur de rafals lira les deux versions et tranchera. En attendant, rien n'est compté ni affiché.",
  etiquette: "Ce qui s'est passé", aide: "ex. « Je suis venu à 10 h, personne n'a ouvert, j'ai appelé 2 fois. »",
  chemin, cle: 'explication', bouton: 'Envoyer', reussite: 'Contestation envoyée : rafals va trancher.',
})
async function signalerPasVenu() {
  const r = pasVenu.value
  if (!r) return
  try {
    await appelerServeur(`/api/moi/rendez-vous/${r.id}/absent`, {})
    afficherMessage(`Absence signalée : ${r.autre.nom} a 7 jours pour contester.`)
    await charger()
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  } finally {
    pasVenu.value = null
  }
}

// ---------- Avis (lot 4.8) ----------
const aNoter = ref<{ rendezVousId: number; avis: RendezVousVisible['avis']; prestataire: string; quoi: string } | null>(null)
async function retirerAvis(r: RendezVousVisible) {
  if (!r.avis) return
  try {
    await appelerServeur(`/api/moi/avis/${r.avis.id}/retirer`, {})
    afficherMessage("Avis retiré : il n'est plus affiché.")
    await charger()
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}

// ---------- Déplacer ----------
const aDeplacer = ref<RendezVousVisible | null>(null)
const erreurDeplacement = ref('')
async function deplacer(debut: string) {
  const r = aDeplacer.value
  if (!r) return
  erreurDeplacement.value = ''
  try {
    const nouveau = await appelerServeur<RendezVousVisible>(`/api/moi/rendez-vous/${r.id}/deplacer`, { debut })
    aDeplacer.value = null
    const m = aParis(nouveau.debut)
    afficherMessage(
      nouveau.statut === 'confirme'
        ? `Rendez-vous déplacé au ${jourCourt(m.jour).slice(0, 5)} à ${heure(m.heure)}.`
        : `Demande envoyée : votre rendez-vous actuel reste valable tant que ${r.autre.nom} n'a pas accepté.`,
    )
    await charger()
  } catch (e) {
    erreurDeplacement.value = messageErreur(e)
  }
}
</script>

<template>
  <AppCarte v-if="chargementFait && !compte" titre="Mes rendez-vous" intro="Connectez-vous pour voir vos rendez-vous.">
    <AppBouton pleine-largeur @click="routeur.push({ path: '/connexion', query: { retour: '/rendez-vous' } })">Se connecter</AppBouton>
  </AppCarte>

  <div v-else-if="compte" class="mx-auto flex w-full max-w-[720px] flex-col gap-4">
    <h1 class="text-[28px] font-bold">Mes rendez-vous</h1>
    <AppOnglets
      v-model="onglet"
      :onglets="[{ id: 'a-venir', texte: 'À venir' }, { id: 'passes', texte: 'Passés et annulés' }]"
    />
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <AppAlerte v-if="retourPaiement" :etat="retourPaiement.etat">{{ retourPaiement.texte }}</AppAlerte>

    <template v-if="tous">
      <AppSection v-if="onglet === 'a-venir'">
        <template v-if="!avenir.length">
          <p class="text-texte-doux">Aucun rendez-vous pour l'instant.</p>
          <div><AppBouton @click="routeur.push('/trouver')">Trouver un prestataire</AppBouton></div>
        </template>
        <div class="flex flex-col divide-y divide-bord">
          <LigneRendezVous v-for="r in avenir" :key="r.id" :rdv="r" libelle-autre="Avec">
            <template #actions>
              <template v-if="r.statut === 'en_attente'">
                <span class="text-[13.5px] text-texte-doux">
                  {{ r.autre.nom }} doit accepter avant le {{ momentCourt(r.reponse_avant ?? r.debut) }}.
                </span>
                <AppBouton variante="danger" @click="aAnnuler = r">Annuler la demande</AppBouton>
              </template>
              <template v-else-if="dansLeDelai(r)">
                <AppBouton variante="secondaire" @click="(aDeplacer = r), (erreurDeplacement = '')">Déplacer</AppBouton>
                <AppBouton variante="danger" @click="aAnnuler = r">Annuler…</AppBouton>
                <span v-if="r.annulable_jusqu_au" class="text-[13.5px] text-texte-doux">
                  Annulation gratuite jusqu'au {{ momentCourt(r.annulable_jusqu_au) }}.
                </span>
              </template>
              <template v-else>
                <AppBouton variante="verrouille" :raison-verrou="raisonHorsDelai(r)">Déplacer</AppBouton>
                <AppBouton variante="verrouille" :raison-verrou="raisonHorsDelai(r)">Annuler</AppBouton>
              </template>
            </template>
          </LigneRendezVous>
        </div>
      </AppSection>

      <AppSection v-else>
        <p v-if="!passes.length" class="text-texte-doux">Aucun rendez-vous passé ou annulé.</p>
        <div class="flex flex-col divide-y divide-bord">
          <LigneRendezVous v-for="r in passes" :key="r.id" :rdv="r" libelle-autre="Avec">
            <template #actions>
              <div v-if="r.avis" class="w-full rounded-rafals bg-fond p-3">
                <AvisAffiche :avis="r.avis" titre="Votre avis" :nom-prestataire="r.autre.nom">
                  <template #actions>
                    <template v-if="!r.avis.retire && !r.avis.cache_motif">
                      <AppBouton
                        v-if="new Date() < new Date(r.avis.modifiable_jusqu_au)"
                        variante="secondaire"
                        @click="aNoter = { rendezVousId: r.id, avis: r.avis, prestataire: r.autre.nom, quoi: plage(r) }"
                      >
                        Modifier
                      </AppBouton>
                      <AppBouton variante="danger" @click="retirerAvis(r)">Retirer</AppBouton>
                      <span v-if="new Date() < new Date(r.avis.modifiable_jusqu_au)" class="text-[13.5px] text-texte-doux">
                        Modifiable jusqu'au {{ momentCourt(r.avis.modifiable_jusqu_au) }}.
                      </span>
                    </template>
                  </template>
                </AvisAffiche>
              </div>
              <template v-else-if="r.peut_noter">
                <AppBouton @click="aNoter = { rendezVousId: r.id, avis: null, prestataire: r.autre.nom, quoi: `${r.titre}, ${plage(r).toLowerCase()}.` }">
                  Donner mon avis
                </AppBouton>
              </template>
              <AppBouton v-if="absenceSignalable(r, 'client')" variante="danger" @click="pasVenu = r">{{ r.autre.nom }} n'est pas venu…</AppBouton>
              <AppBouton v-if="contestable(r.absence, 'client')" variante="secondaire" @click="aContester = contester(`/api/moi/rendez-vous/${r.id}/contester`)">
                Je suis venu…
              </AppBouton>
            </template>
          </LigneRendezVous>
        </div>
      </AppSection>
    </template>

    <AppFenetre :ouverte="aAnnuler !== null" :titre="aAnnuler?.statut === 'en_attente' ? 'Annuler la demande ?' : 'Annuler ce rendez-vous ?'" @fermer="aAnnuler = null">
      <template v-if="aAnnuler">
        {{ aAnnuler.titre }} avec {{ aAnnuler.autre.nom }}, {{ plage(aAnnuler).toLowerCase() }}.
        {{ aAnnuler.autre.nom }} est prévenu par mail et l'horaire redevient libre.
        <AppAlerte v-if="aAnnuler.paiement?.rembourse_si_annule_centimes" etat="neutre" class="mt-3">
          Payé par carte : vous serez remboursé de {{ montant(aAnnuler.paiement.rembourse_si_annule_centimes) }}
          ({{ montant(aAnnuler.paiement.montant_centimes) }} moins
          {{ montant(aAnnuler.paiement.montant_centimes - aAnnuler.paiement.rembourse_si_annule_centimes) }} de frais de paiement),
          sous 5 à 10 jours.
        </AppAlerte>
      </template>
      <template #pied>
        <AppBouton variante="danger" @click="annuler">{{ aAnnuler?.statut === 'en_attente' ? 'Annuler la demande' : 'Annuler le rendez-vous' }}</AppBouton>
        <AppBouton variante="secondaire" @click="aAnnuler = null">Garder</AppBouton>
      </template>
    </AppFenetre>

    <AppFenetre :ouverte="pasVenu !== null" :titre="`${pasVenu?.autre.nom} n'est pas venu ?`" @fermer="pasVenu = null">
      <template v-if="pasVenu">
        {{ pasVenu.titre }}, {{ plage(pasVenu).toLowerCase() }}. {{ pasVenu.autre.nom }} est prévenu et a 7 jours pour
        contester ; sinon, l'absence apparaîtra sur sa page.
      </template>
      <template #pied>
        <AppBouton variante="danger" @click="signalerPasVenu">Signaler l'absence</AppBouton>
        <AppBouton variante="secondaire" @click="pasVenu = null">Annuler</AppBouton>
      </template>
    </AppFenetre>
    <FenetreTexte :demande="aContester" @fermer="aContester = null" @fait="(aContester = null), charger()" />

    <FenetreAvis :cible="aNoter" @fermer="aNoter = null" @enregistre="(aNoter = null), charger()" />

    <AppFenetre :ouverte="aDeplacer !== null" :titre="`Déplacer « ${aDeplacer?.titre} »`" @fermer="aDeplacer = null">
      <div v-if="aDeplacer" class="flex flex-col gap-3 text-texte">
        <p class="text-[14px] text-texte-doux">Actuellement : {{ plage(aDeplacer).toLowerCase() }}. Choisissez un nouvel horaire (même prix).</p>
        <ChoixHoraire :annonce-id="aDeplacer.annonce_id" :heures="aDeplacer.heures" @choisir="deplacer" />
        <AppAlerte v-if="erreurDeplacement">{{ erreurDeplacement }}</AppAlerte>
      </div>
      <template #pied>
        <span />
        <AppBouton variante="secondaire" @click="aDeplacer = null">Fermer</AppBouton>
      </template>
    </AppFenetre>
  </div>
</template>
