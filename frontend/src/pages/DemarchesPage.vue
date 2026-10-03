<script setup lang="ts">
// Mes démarches (.doc/ihm/RM-DEMARCHES-IHM.md ; RM-DEMARCHES.md, lot 6.2) : le chiffre d'affaires à déclarer à
// l'URSSAF, par mois ou par trimestre, préparé d'après les factures. rafals prépare, il ne déclare pas.
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import GardePrestataire from '../components/prestataire/GardePrestataire.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBadge from '../components/ui/AppBadge.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppSection from '../components/ui/AppSection.vue'
import AppSegment from '../components/ui/AppSegment.vue'
import { useCompte } from '../composables/useCompte'
import { aParis, jourCourt } from '../outils/agenda'
import { montant } from '../outils/paiements'

interface Periode {
  rang: number
  debut: string
  fin: string
  encaisse_centimes: number
  nombre_factures: number
  a_declarer_avant: string
  terminee: boolean
}
interface Demarches {
  annee: number
  siret_verifie: boolean
  facture_tva: boolean
  mois: Periode[]
  trimestres: Periode[]
}

const SITE_URSSAF = 'https://www.autoentrepreneur.urssaf.fr'
const NOMS_MOIS = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
const routeur = useRouter()
const { compte } = useCompte()
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
const annees = computed(() =>
  Array.from({ length: anneeEnCours - 2026 + 1 }, (_, n) => ({ valeur: 2026 + n, texte: String(2026 + n) })),
)
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
      <div><AppBouton @click="routeur.push('/creer-mon-auto-entreprise')">Créer mon auto-entreprise</AppBouton></div>
    </AppSection>
    <AppSection v-else-if="demarches" titre="Déclaration à l'URSSAF">
      <p class="text-[14px] text-texte-doux">
        Un auto-entrepreneur déclare à l'URSSAF ce qu'il a encaissé, chaque mois ou chaque trimestre, même 0 €. rafals prépare
        le chiffre d'après vos factures ; la déclaration se fait sur le site de l'URSSAF.
      </p>
      <AppAlerte v-if="prochaine" etat="attente">
        À déclarer pour {{ nom(prochaine).toLowerCase() }} : <b>{{ montant(prochaine.encaisse_centimes) }}</b>, avant le
        {{ jourCourt(prochaine.a_declarer_avant) }}.
      </AppAlerte>
      <div><AppBouton @click="ouvrirUrssaf">Aller sur le site de l'URSSAF</AppBouton></div>
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
                <AppBadge v-if="!p.terminee" etat="neutre">en cours</AppBadge>
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
  </GardePrestataire>
</template>
