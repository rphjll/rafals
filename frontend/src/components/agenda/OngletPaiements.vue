<script setup lang="ts">
// Mon agenda › Paiements (.doc/ihm/RM-AGENDA-IHM.md ; RM-PAIEMENTS.md, lot 5.2) : ce qui est bloqué chez Stripe en
// attendant les rendez-vous, ce qui est versé ce mois-ci, puis chaque paiement par carte (5 % de rafals, frais de Stripe,
// ce qui revient au prestataire).
import { computed, onMounted, ref } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { jourCourt, aParis } from '../../outils/agenda'
import { type PaiementVisible, badgePaiement, montant, pourLePrestataire } from '../../outils/paiements'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBadge from '../ui/AppBadge.vue'
import AppSection from '../ui/AppSection.vue'

const paiements = ref<PaiementVisible[] | null>(null)
const erreur = ref('')
onMounted(async () => {
  try {
    paiements.value = await appelerServeur<PaiementVisible[]>('/api/moi/prestataire/paiements')
  } catch (e) {
    erreur.value = messageErreur(e)
  }
})

const NOMS_MOIS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
const moisCourant = aParis(new Date().toISOString()).jour.slice(0, 7) // « 2026-10 »
const bloques = computed(() => (paiements.value ?? []).filter((p) => p.statut === 'paye'))
const versesCeMois = computed(() =>
  (paiements.value ?? []).filter((p) => p.statut === 'verse' && p.verse_le && aParis(p.verse_le).jour.startsWith(moisCourant)),
)
const somme = (liste: PaiementVisible[]) => liste.reduce((total, p) => total + (p.net_centimes ?? 0), 0)
const rendezVous = (n: number) => `${n} rendez-vous`
/** « mar. 13/10 » */
function jourDuRendezVous(iso: string): string {
  const jour = aParis(iso).jour
  const nom = ['dim.', 'lun.', 'mar.', 'mer.', 'jeu.', 'ven.', 'sam.'][new Date(`${jour}T12:00:00`).getDay()]
  return `${nom} ${jourCourt(jour).slice(0, 5)}`
}
</script>

<template>
  <AppSection>
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <template v-if="paiements">
      <p v-if="!paiements.length" class="text-texte-doux">Aucun paiement par carte pour l'instant.</p>
      <template v-else>
        <div class="grid grid-cols-[repeat(auto-fit,minmax(150px,1fr))] gap-2.5">
          <div class="rounded-rafals bg-fond px-3 py-2.5">
            <span class="text-[13.5px] text-texte-doux">À venir (bloqué chez Stripe)</span>
            <b class="block text-[22px] tabular-nums">{{ montant(somme(bloques)) }}</b>
            <span class="text-[13.5px] text-texte-doux">{{ rendezVous(bloques.length) }}</span>
          </div>
          <div class="rounded-rafals bg-fond px-3 py-2.5">
            <span class="text-[13.5px] text-texte-doux">Versé en {{ NOMS_MOIS[Number(moisCourant.slice(5)) - 1] }}</span>
            <b class="block text-[22px] tabular-nums">{{ montant(somme(versesCeMois)) }}</b>
            <span class="text-[13.5px] text-texte-doux">{{ rendezVous(versesCeMois.length) }}</span>
          </div>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full min-w-[560px] border-collapse text-[14px]">
            <thead>
              <tr class="border-b border-bord text-left text-[13px] text-texte-doux">
                <th class="px-1.5 py-2 font-semibold">Rendez-vous</th>
                <th class="px-1.5 py-2 font-semibold">État</th>
                <th class="px-1.5 py-2 text-right font-semibold">Payé</th>
                <th class="px-1.5 py-2 text-right font-semibold">rafals 5 %</th>
                <th class="px-1.5 py-2 text-right font-semibold">Frais Stripe</th>
                <th class="px-1.5 py-2 text-right font-semibold">Pour vous</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in paiements" :key="p.id" class="border-b border-bord">
                <td class="px-1.5 py-2">
                  {{ p.titre }}<br />
                  <span class="text-[13px] text-texte-doux">{{ jourDuRendezVous(p.debut) }} · {{ p.avec }}</span>
                </td>
                <td class="px-1.5 py-2"><AppBadge :etat="badgePaiement(p).etat">{{ badgePaiement(p).texte }}</AppBadge></td>
                <td class="px-1.5 py-2 text-right tabular-nums">{{ montant(p.montant_centimes) }}</td>
                <td class="px-1.5 py-2 text-right tabular-nums">{{ p.statut === 'rembourse' ? '—' : montant(p.commission_centimes ?? 0) }}</td>
                <td class="px-1.5 py-2 text-right tabular-nums">{{ p.frais_stripe_centimes === null ? '—' : montant(p.frais_stripe_centimes) }}</td>
                <td class="px-1.5 py-2 text-right font-bold tabular-nums">{{ montant(pourLePrestataire(p)) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p class="text-[13.5px] text-texte-doux">
          « versé le 15/10 » en orange : date prévue, 48 h après la fin du rendez-vous ; l'argent arrive sur votre compte en
          banque quelques jours après. Les frais d'un remboursement sont retirés de votre versement suivant.
        </p>
      </template>
    </template>
  </AppSection>
</template>
