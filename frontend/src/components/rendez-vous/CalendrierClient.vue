<script setup lang="ts">
// Calendrier du client, dans « Mon agenda » (.doc/ihm/RM-RENDEZ-VOUS-IHM.md ; RM-RENDEZ-VOUS.md) : ses rendez-vous dans
// le mois, puis ceux du jour choisi (ou du mois) avec leurs boutons : annuler dans le délai du prestataire,
// donner un avis, signaler une absence. Remplace la page « Mes rendez-vous » (demande de Raphael du 07/10/2026).
// Retour de la page de paiement de Stripe (?paiement=fait|annule, lot 5.2).
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../../api'
import AvisAffiche from '../avis/AvisAffiche.vue'
import FenetreAvis from '../avis/FenetreAvis.vue'
import FenetreTexte, { type DemandeTexte } from '../FenetreTexte.vue'
import LigneRendezVous from './LigneRendezVous.vue'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppFenetre from '../ui/AppFenetre.vue'
import AppSection from '../ui/AppSection.vue'
import { useCompte } from '../../composables/useCompte'
import { useMessage } from '../../composables/useMessage'
import { JOURS, MOIS, aParis, jourLisible, jourSemaine } from '../../outils/agenda'
import { montant } from '../../outils/paiements'
import { type RendezVousVisible, absenceSignalable, aVenir, contestable, momentCourt, plage } from '../../outils/rendez_vous'

const route = useRoute()
const routeur = useRouter()
const { compte } = useCompte()
const { afficherMessage } = useMessage()
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
  // On enlève seulement ce qui concerne le paiement : le calendrier choisi (?calendrier=client) reste dans l'adresse
  const { rdv: _rdv, paiement: _paiement, ...reste } = route.query
  routeur.replace({ query: reste })
})
onUnmounted(() => clearTimeout(relecture))

// ---------- Le calendrier ----------
const aujourdhui = aParis(new Date().toISOString()).jour // « 2026-10-07 »
const mois = ref({ annee: Number(aujourdhui.slice(0, 4)), mois: Number(aujourdhui.slice(5, 7)) })
const jourChoisi = ref<string | null>(null)
const cleDuMois = computed(() => `${mois.value.annee}-${String(mois.value.mois).padStart(2, '0')}`)
function changerDeMois(sens: 1 | -1) {
  const suivant = mois.value.mois + sens
  mois.value = suivant < 1 ? { annee: mois.value.annee - 1, mois: 12 } : suivant > 12 ? { annee: mois.value.annee + 1, mois: 1 } : { annee: mois.value.annee, mois: suivant }
  jourChoisi.value = null
}
// Les rendez-vous rangés par jour (heure de Paris), le plus tôt d'abord
const parJour = computed(() => {
  const jours = new Map<string, RendezVousVisible[]>()
  for (const r of [...(tous.value ?? [])].sort((a, b) => a.debut.localeCompare(b.debut))) {
    const jour = aParis(r.debut).jour
    jours.set(jour, [...(jours.get(jour) ?? []), r])
  }
  return jours
})
// Les cases du mois : des vides avant le 1er (la semaine commence le lundi), puis une case par jour
const cases = computed(() => {
  const nombre = new Date(Date.UTC(mois.value.annee, mois.value.mois, 0)).getUTCDate()
  const jours = Array.from({ length: nombre }, (_, n) => {
    const jour = `${cleDuMois.value}-${String(n + 1).padStart(2, '0')}`
    const duJour = parJour.value.get(jour) ?? []
    return { jour, numero: n + 1, nombre: duJour.length, aVenir: duJour.some((r) => aVenir(r)) }
  })
  return { avant: jourSemaine(`${cleDuMois.value}-01`) - 1, jours }
})
// Sous le calendrier : les rendez-vous du jour choisi, sinon tous ceux du mois affiché
const montres = computed(() =>
  jourChoisi.value
    ? (parJour.value.get(jourChoisi.value) ?? [])
    : [...parJour.value].filter(([jour]) => jour.startsWith(cleDuMois.value)).flatMap(([, liste]) => liste),
)
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

</script>

<template>
  <div class="mx-auto flex w-full max-w-[720px] flex-col gap-4">
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <AppAlerte v-if="retourPaiement" :etat="retourPaiement.etat">{{ retourPaiement.texte }}</AppAlerte>

    <template v-if="tous">
      <!-- Le calendrier du mois : un clic sur un jour ne montre que ses rendez-vous ; un 2e clic les remontre tous -->
      <section class="carte flex flex-col gap-3 p-4 sm:p-5">
        <div class="flex items-center justify-between gap-2">
          <AppBouton variante="secondaire" @click="changerDeMois(-1)">‹<span class="sr-only"> Mois précédent</span></AppBouton>
          <h2 class="text-[19px] font-bold capitalize">{{ MOIS[mois.mois - 1] }} {{ mois.annee }}</h2>
          <AppBouton variante="secondaire" @click="changerDeMois(1)"><span class="sr-only">Mois suivant </span>›</AppBouton>
        </div>
        <div class="grid grid-cols-7 gap-1 text-center">
          <span v-for="nom in JOURS" :key="nom" class="pb-1 text-[12.5px] font-semibold text-texte-doux capitalize">{{ nom.slice(0, 3) }}</span>
          <span v-for="vide in cases.avant" :key="`v${vide}`" />
          <button
            v-for="c in cases.jours"
            :key="c.jour"
            type="button"
            class="flex min-h-[54px] flex-col items-center justify-start gap-0.5 rounded-rafals border px-0.5 py-1.5 tabular-nums"
            :class="[
              c.jour === jourChoisi ? 'border-primaire bg-primaire text-primaire-texte' : c.aVenir ? 'border-transparent bg-ouvert text-ouvert-texte' : c.nombre ? 'border-transparent bg-neutre-doux' : 'border-transparent hover:bg-fond',
              c.jour === aujourdhui && c.jour !== jourChoisi ? 'ring-2 ring-accent' : '',
            ]"
            :aria-pressed="c.jour === jourChoisi"
            :aria-label="`${jourLisible(c.jour)} : ${c.nombre ? `${c.nombre} rendez-vous` : 'aucun rendez-vous'}`"
            @click="jourChoisi = jourChoisi === c.jour ? null : c.jour"
          >
            <span class="font-semibold">{{ c.numero }}</span>
            <span v-if="c.nombre" class="text-[11.5px] leading-none font-bold">{{ c.nombre }} rdv</span>
          </button>
        </div>
        <p class="flex flex-wrap gap-x-4 gap-y-1 text-[13px] text-texte-doux">
          <span><span class="mr-1 inline-block size-3 rounded-sm bg-ouvert align-middle" />rendez-vous à venir</span>
          <span><span class="mr-1 inline-block size-3 rounded-sm bg-neutre-doux align-middle" />passé ou annulé</span>
          <span><span class="mr-1 inline-block size-3 rounded-sm ring-2 ring-accent align-middle" />aujourd'hui</span>
        </p>
      </section>

      <AppSection>
        <div class="flex flex-wrap items-center justify-between gap-2">
          <h2 class="text-xl font-bold first-letter:uppercase">{{ jourChoisi ? jourLisible(jourChoisi) : `${MOIS[mois.mois - 1]} ${mois.annee}` }}</h2>
          <AppBouton v-if="jourChoisi" variante="secondaire" @click="jourChoisi = null">Voir tout le mois</AppBouton>
        </div>
        <template v-if="!montres.length">
          <p class="text-texte-doux">{{ jourChoisi ? 'Aucun rendez-vous ce jour-là.' : 'Aucun rendez-vous ce mois-ci.' }}</p>
          <div v-if="!tous.length"><AppBouton @click="routeur.push('/')">Publier une demande</AppBouton></div>
        </template>
        <div class="flex flex-col divide-y divide-bord">
          <LigneRendezVous v-for="r in montres" :key="r.id" :rdv="r" libelle-autre="Avec">
            <template #actions>
              <!-- Rendez-vous à venir : annuler (pour changer d'heure, on écrit au prestataire) -->
              <template v-if="aVenir(r)">
                <template v-if="r.statut === 'en_attente'">
                  <span class="text-[13.5px] text-texte-doux">
                    {{ r.autre.nom }} doit accepter avant le {{ momentCourt(r.reponse_avant ?? r.debut) }}.
                  </span>
                  <AppBouton variante="danger" @click="aAnnuler = r">Annuler la demande</AppBouton>
                </template>
                <template v-else-if="dansLeDelai(r)">
                  <AppBouton variante="danger" @click="aAnnuler = r">Annuler…</AppBouton>
                  <span v-if="r.annulable_jusqu_au" class="text-[13.5px] text-texte-doux">
                    Annulation gratuite jusqu'au {{ momentCourt(r.annulable_jusqu_au) }}.
                  </span>
                </template>
                <template v-else>
                  <AppBouton variante="verrouille" :raison-verrou="raisonHorsDelai(r)">Annuler</AppBouton>
                </template>
              </template>
              <!-- Rendez-vous passé ou annulé : avis, absence -->
              <template v-else>
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

  </div>
</template>
