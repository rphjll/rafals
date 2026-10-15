<script setup lang="ts">
// Mes démarches (.doc/ihm/RM-DEMARCHES-IHM.md ; RM-DEMARCHES.md, lot 6.2) : le chiffre d'affaires à déclarer à
// l'URSSAF, par mois ou par trimestre, préparé d'après les factures. Depuis le lot 7.3, le prestataire qui a donné
// son accord peut déclarer d'un clic (components/demarches/DeclarerUrssaf.vue) ; sinon il déclare sur le site de l'URSSAF.
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import { useMessage } from '../composables/useMessage'
import DeclarerUrssaf, { type EtatUrssaf } from '../components/demarches/DeclarerUrssaf.vue'
import GardePrestataire from '../components/prestataire/GardePrestataire.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBadge from '../components/ui/AppBadge.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppSection from '../components/ui/AppSection.vue'
import AppSegment from '../components/ui/AppSegment.vue'
import { useCompte } from '../composables/useCompte'
import { aParis, jourCourt } from '../outils/agenda'
import { formaterDate } from '../outils/dates'
import { montant } from '../outils/paiements'
import { VERROU_SIRET } from '../outils/prestataires'

interface Periode {
  rang: number
  debut: string
  fin: string
  encaisse_centimes: number
  nombre_factures: number
  a_declarer_avant: string
  terminee: boolean
  /** Déclarée à l'URSSAF depuis rafals (lot 7.3) : total envoyé, cotisations, date ; vide sinon */
  declaree_centimes: number | null
  cotisations_centimes: number | null
  declaree_le: string | null
}
interface Demarches {
  annee: number
  siret_verifie: boolean
  facture_tva: boolean
  /** Déclare chaque mois, chaque trimestre, ou pas de rappel (lot 6.4) */
  periodicite: 'mois' | 'trimestre' | null
  mois: Periode[]
  trimestres: Periode[]
  urssaf: EtatUrssaf
}

const SITE_URSSAF = 'https://www.autoentrepreneur.urssaf.fr'
const NOMS_MOIS = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
const routeur = useRouter()
const { compte } = useCompte()
const { afficherMessage } = useMessage()
const aujourdhui = aParis(new Date().toISOString()).jour
const anneeEnCours = Number(aujourdhui.slice(0, 4))
const annee = ref(anneeEnCours)
const vue = ref<'mois' | 'trimestres'>('mois')
const demarches = ref<Demarches | null>(null)
const erreur = ref('')

async function charger() {
  if (!compte.value?.prestataire_id) return
  try {
    demarches.value = await appelerServeur<Demarches>(`/api/moi/prestataire/demarches?annee=${annee.value}`)
    rappels.value = demarches.value.periodicite ?? 'aucun'
    if (demarches.value.periodicite) vue.value = demarches.value.periodicite === 'mois' ? 'mois' : 'trimestres'
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
onMounted(charger)
watch([compte, annee], charger)

const nom = (p: Periode) =>
  vue.value === 'mois' ? `${NOMS_MOIS[p.rang - 1]} ${annee.value}` : `${p.rang}${p.rang === 1 ? 'er' : 'e'} trimestre ${annee.value}`
// Les périodes commencées, la plus récente d'abord
const periodes = computed(() => (demarches.value?.[vue.value] ?? []).filter((p) => p.debut <= aujourdhui).reverse())
// Période finie dont la date limite n'est pas passée : c'est celle qu'il faut déclarer maintenant
const aDeclarer = (p: Periode) => p.terminee && p.a_declarer_avant >= aujourdhui
const prochaine = computed(() => periodes.value.find(aDeclarer) ?? null)
// La même période, une fois déclarée depuis rafals : on montre ce qui a été envoyé
const declaree = computed(() => (prochaine.value?.declaree_le ? prochaine.value : null))
const annees = computed(() =>
  Array.from({ length: anneeEnCours - 2026 + 1 }, (_, n) => ({ valeur: 2026 + n, texte: String(2026 + n) })),
)
// ---------- Rappels par mail (lot 6.4) : le choix s'enregistre au clic ----------
const rappels = ref<'mois' | 'trimestre' | 'aucun'>('aucun')
async function choisirRappels(valeur: 'mois' | 'trimestre' | 'aucun') {
  if (!demarches.value || valeur === (demarches.value.periodicite ?? 'aucun')) return
  try {
    const periodicite = valeur === 'aucun' ? null : valeur
    await appelerServeur('/api/moi/prestataire/demarches/periodicite', { periodicite })
    demarches.value.periodicite = periodicite
    await charger() // la période à déclarer dépend de ce choix
    if (periodicite) vue.value = periodicite === 'mois' ? 'mois' : 'trimestres'
    afficherMessage(periodicite ? `Rappels activés : chaque ${periodicite}.` : 'Rappels arrêtés.')
  } catch (e) {
    rappels.value = demarches.value.periodicite ?? 'aucun'
    afficherMessage(messageErreur(e), 'erreur')
  }
}
watch(rappels, choisirRappels)

function ouvrirUrssaf() {
  window.open(SITE_URSSAF, '_blank', 'noopener')
}
</script>

<template>
  <GardePrestataire titre="Mes démarches">
    <h1 class="text-[28px] font-bold">Mes démarches</h1>
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <AppSection v-if="demarches && !demarches.siret_verifie" titre="Déclaration à l'URSSAF">
      <p class="text-texte-doux">Les démarches concernent les prestataires avec un SIRET vérifié : sans lui, rafals ne fait pas de facture.</p>
      <div class="flex flex-wrap gap-2">
        <AppBouton variante="verrouille" :raison-verrou="VERROU_SIRET.urssaf">Déclarer à l'URSSAF</AppBouton>
        <AppBouton variante="verrouille" :raison-verrou="VERROU_SIRET.urssaf">Rappels par mail</AppBouton>
      </div>
      <div><AppBouton @click="routeur.push('/creer-mon-auto-entreprise')">Créer mon auto-entreprise</AppBouton></div>
    </AppSection>
    <AppSection v-else-if="demarches" titre="Déclaration à l'URSSAF">
      <p class="text-[14px] text-texte-doux">
        Un auto-entrepreneur déclare à l'URSSAF ce qu'il a encaissé, chaque mois ou chaque trimestre, même 0 €. rafals prépare
        le chiffre d'après vos factures ; vous déclarez sur le site de l'URSSAF, ou d'un clic depuis rafals.
      </p>
      <template v-if="declaree">
        <AppAlerte etat="ok">
          {{ nom(declaree) }} déclaré le {{ formaterDate(declaree.declaree_le ?? '') }} : <b>{{ montant(declaree.declaree_centimes ?? 0) }}</b>.
          Cotisations à payer à l'URSSAF : <b>{{ montant(declaree.cotisations_centimes ?? 0) }}</b>.
        </AppAlerte>
        <p class="text-[13.5px] text-texte-doux">
          rafals a déclaré, il n'a pas payé : le paiement des cotisations se fait sur le site de l'URSSAF (ou par le
          prélèvement que vous y avez réglé). Pour corriger cette déclaration, passez aussi par le site de l'URSSAF.
        </p>
      </template>
      <AppAlerte v-else-if="prochaine" etat="attente">
        À déclarer pour {{ nom(prochaine).toLowerCase() }} : <b>{{ montant(prochaine.encaisse_centimes) }}</b>, avant le
        {{ jourCourt(prochaine.a_declarer_avant) }}.
      </AppAlerte>
      <DeclarerUrssaf :urssaf="demarches.urssaf" :periodicite="demarches.periodicite" @change="charger" @site="ouvrirUrssaf" />
      <div class="flex flex-wrap items-center gap-3">
        <AppSegment v-model="vue" etiquette="Voir" :options="[{ valeur: 'mois', texte: 'Par mois' }, { valeur: 'trimestres', texte: 'Par trimestre' }]" />
        <AppSegment v-if="annees.length > 1" v-model="annee" etiquette="Année" :options="annees" />
      </div>
      <div class="overflow-x-auto">
        <table class="w-full min-w-[520px] border-collapse text-[14px]">
          <thead>
            <tr class="border-b border-bord text-left text-[13px] text-texte-doux">
              <th class="px-1.5 py-2 font-semibold">Période</th>
              <th class="px-1.5 py-2 text-right font-semibold">Encaissé{{ demarches.facture_tva ? ' (HT)' : '' }}</th>
              <th class="px-1.5 py-2 text-right font-semibold">Factures</th>
              <th class="px-1.5 py-2 font-semibold">À déclarer avant le</th>
              <th class="px-1.5 py-2"><span class="sr-only">État</span></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in periodes" :key="p.rang" class="border-b border-bord">
              <td class="px-1.5 py-2">{{ nom(p) }}</td>
              <td class="px-1.5 py-2 text-right font-bold tabular-nums">{{ montant(p.encaisse_centimes) }}</td>
              <td class="px-1.5 py-2 text-right tabular-nums">{{ p.nombre_factures }}</td>
              <td class="px-1.5 py-2">{{ jourCourt(p.a_declarer_avant) }}</td>
              <td class="px-1.5 py-2">
                <AppBadge v-if="p.declaree_le" etat="ok">déclaré : {{ montant(p.declaree_centimes ?? 0) }}</AppBadge>
                <AppBadge v-else-if="!p.terminee" etat="neutre">en cours</AppBadge>
                <AppBadge v-else-if="aDeclarer(p)" etat="attente">à déclarer</AppBadge>
                <span v-else class="text-[13px] text-texte-doux">date passée</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p class="text-[13.5px] text-texte-doux">
        Seulement ce qui est passé par rafals : ajoutez ce que vous avez encaissé ailleurs. La commission de rafals et les
        frais de paiement ne se déduisent pas.<template v-if="demarches.facture_tva"> Vous facturez la TVA : les montants sont hors taxe.</template>
      </p>
    </AppSection>
    <AppSection v-if="demarches?.siret_verifie" titre="Rappels par mail">
      <p class="text-[14px] text-texte-doux">
        Dites à rafals comment vous déclarez à l'URSSAF : vous recevrez un mail 7 jours avant la date limite, puis la veille,
        avec le montant à déclarer.
      </p>
      <div>
        <AppSegment
          v-model="rappels"
          etiquette="Rappels par mail"
          :options="[{ valeur: 'mois', texte: 'Chaque mois' }, { valeur: 'trimestre', texte: 'Chaque trimestre' }, { valeur: 'aucun', texte: 'Pas de rappel' }]"
        />
      </div>
      <p v-if="demarches.periodicite && prochaine" class="text-[13.5px] text-texte-doux">
        Prochain rappel : 7 jours avant le {{ jourCourt(prochaine.a_declarer_avant) }}, puis la veille, pour {{ nom(prochaine).toLowerCase() }}.
      </p>
    </AppSection>
  </GardePrestataire>
</template>
