<script setup lang="ts">
// Déclarer à l'URSSAF d'un clic depuis « Mes démarches » (.doc/ihm/RM-DEMARCHES-IHM.md ; RM-DEMARCHES.md, lot 7.3) :
// donner son accord une fois, puis [Déclarer à l'URSSAF…] pour la période finie. rafals déclare, il ne paie pas.
import { computed, ref, watch } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { jourCourt } from '../../outils/agenda'
import { formaterDate } from '../../outils/dates'
import { montant } from '../../outils/paiements'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBadge from '../ui/AppBadge.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppCase from '../ui/AppCase.vue'
import AppChamp from '../ui/AppChamp.vue'
import AppFenetre from '../ui/AppFenetre.vue'

export interface EtatUrssaf {
  /** L'accord en cours (date), ou vide */
  mandat_le: string | null
  texte_mandat: string
  /** rafals n'est pas branché à l'URSSAF : rien n'est envoyé */
  demonstration: boolean
  a_declarer: {
    periodicite: 'mois' | 'trimestre'
    debut: string
    nom: string
    limite: string
    montant_rafals_centimes: number
    nombre_factures: number
  } | null
}

const props = defineProps<{ urssaf: EtatUrssaf; periodicite: 'mois' | 'trimestre' | null }>()
// La page reçoit les démarches à jour (accord donné ou retiré, période déclarée)
const emit = defineEmits<{ change: [demarches: unknown]; site: [] }>()
const { afficherMessage } = useMessage()
const CHEMIN = '/api/moi/prestataire/urssaf'

const fenetre = ref<'accord' | 'declarer' | 'retirer' | null>(null)
const erreur = ref('')
const envoiEnCours = ref(false)
// Le dernier refus de l'URSSAF reste affiché dans la carte, fenêtre fermée
const refus = ref('')

// ---------- L'accord ----------
const numeroSecu = ref('')
const accepte = ref(false)

// ---------- La déclaration ----------
const ailleurs = ref('0')
const certifie = ref(false)
const estimation = ref<{ total_centimes: number; cotisations_centimes: number } | null>(null)
const ailleursCentimes = computed(() => {
  const nombre = Number(ailleurs.value.replace(/\s/g, '').replace(',', '.') || '0')
  return Number.isFinite(nombre) && nombre >= 0 ? Math.round(nombre * 100) : null
})

function ouvrir(nom: 'accord' | 'declarer' | 'retirer') {
  erreur.value = ''
  numeroSecu.value = ''
  accepte.value = false
  ailleurs.value = '0'
  certifie.value = false
  estimation.value = null
  fenetre.value = nom
  if (nom === 'declarer') estimer()
}

async function estimer() {
  estimation.value = null
  if (ailleursCentimes.value === null) return
  try {
    estimation.value = await appelerServeur('/api/moi/prestataire/urssaf/estimation', { ailleurs_centimes: ailleursCentimes.value })
    erreur.value = ''
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
// L'estimation suit le montant saisi, après une courte pause de frappe
let minuteur: ReturnType<typeof setTimeout> | undefined
watch(ailleurs, () => {
  clearTimeout(minuteur)
  if (fenetre.value === 'declarer') minuteur = setTimeout(estimer, 400)
})

async function envoyer(chemin: string, donnees: unknown, reussite: string) {
  erreur.value = ''
  envoiEnCours.value = true
  try {
    emit('change', await appelerServeur(`${CHEMIN}${chemin}`, donnees))
    fenetre.value = null
    refus.value = ''
    afficherMessage(reussite)
  } catch (e) {
    erreur.value = messageErreur(e)
    if (chemin === '/declaration') refus.value = erreur.value
  } finally {
    envoiEnCours.value = false
  }
}
</script>

<template>
  <AppAlerte v-if="urssaf.demonstration && urssaf.mandat_le" etat="attente">
    Mode démonstration : rafals n'est pas encore branché à l'URSSAF. Rien n'est envoyé ; déclarez aussi sur le site de l'URSSAF.
  </AppAlerte>
  <AppAlerte v-if="refus">{{ refus }}</AppAlerte>

  <!-- Pas encore d'accord -->
  <div v-if="!urssaf.mandat_le" class="flex flex-col gap-3 rounded-rafals bg-fond p-4">
    <h3 class="text-[17px] font-bold">Déclarer d'un clic depuis rafals</h3>
    <p>
      Donnez votre accord une fois : rafals enverra ensuite vos déclarations à l'URSSAF quand vous cliquerez sur [Déclarer].
      Rien ne part sans votre clic.
    </p>
    <p class="text-[13.5px] text-texte-doux">
      Vous gardez votre espace sur le site de l'URSSAF : vous pouvez y corriger une déclaration, et retirer votre accord quand
      vous voulez.
    </p>
    <div class="flex flex-wrap gap-2">
      <AppBouton @click="ouvrir('accord')">Donner mon accord…</AppBouton>
      <AppBouton variante="secondaire" @click="emit('site')">Aller sur le site de l'URSSAF</AppBouton>
    </div>
  </div>

  <!-- Accord donné -->
  <template v-else>
    <div class="flex flex-wrap items-center gap-2">
      <AppBadge etat="ok">accord donné le {{ formaterDate(urssaf.mandat_le) }}</AppBadge>
      <button type="button" class="min-h-[36px] text-[13.5px] font-semibold text-erreur underline" @click="ouvrir('retirer')">
        Retirer mon accord…
      </button>
    </div>
    <div class="flex flex-wrap gap-2">
      <AppBouton v-if="urssaf.a_declarer" @click="ouvrir('declarer')">Déclarer à l'URSSAF…</AppBouton>
      <AppBouton
        v-else-if="!periodicite"
        variante="verrouille"
        raison-verrou="Dites d'abord si vous déclarez chaque mois ou chaque trimestre, dans « Rappels par mail » plus bas."
      >
        Déclarer à l'URSSAF…
      </AppBouton>
      <AppBouton variante="secondaire" @click="emit('site')">Aller sur le site de l'URSSAF</AppBouton>
    </div>
    <p v-if="!urssaf.a_declarer && periodicite" class="text-[13.5px] text-texte-doux">
      Rien à déclarer depuis rafals pour le moment : la dernière période est déjà déclarée, ou sa date limite est passée.
    </p>
  </template>

  <AppFenetre :ouverte="fenetre === 'accord'" titre="Donner mon accord à rafals ?" @fermer="fenetre = null">
    <p>J'autorise rafals à envoyer à l'URSSAF, en mon nom, mes déclarations de chiffre d'affaires, chaque fois que je clique sur [Déclarer].</p>
    <AppChamp
      v-model="numeroSecu"
      etiquette="Numéro de sécurité sociale"
      obligatoire
      inputmode="numeric"
      placeholder="ex. 2 95 07 33 063 045 97"
      aide="L'URSSAF le demande pour vous reconnaître. 15 chiffres, sur votre carte Vitale. rafals l'efface si vous retirez votre accord."
    />
    <AppCase v-model="accepte" :texte="urssaf.texte_mandat" />
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <template #pied>
      <AppBouton v-if="!accepte" variante="verrouille" raison-verrou="Cochez la case pour donner votre accord.">Donner mon accord</AppBouton>
      <AppBouton v-else :occupe="envoiEnCours" @click="envoyer('/mandat', { numero_secu: numeroSecu, accepte }, 'Accord enregistré.')">
        Donner mon accord
      </AppBouton>
      <AppBouton variante="secondaire" @click="fenetre = null">Annuler</AppBouton>
    </template>
  </AppFenetre>

  <AppFenetre
    v-if="urssaf.a_declarer"
    :ouverte="fenetre === 'declarer'"
    :titre="`Déclarer ${urssaf.a_declarer.periodicite === 'trimestre' ? 'le ' : ''}${urssaf.a_declarer.nom} ?`"
    @fermer="fenetre = null"
  >
    <p>
      Encaissé sur rafals : <b>{{ montant(urssaf.a_declarer.montant_rafals_centimes) }}</b>
      ({{ urssaf.a_declarer.nombre_factures }} facture{{ urssaf.a_declarer.nombre_factures > 1 ? 's' : '' }})
    </p>
    <AppChamp
      v-model="ailleurs"
      etiquette="Encaissé ailleurs que sur rafals (en euros)"
      inputmode="decimal"
      aide="Ce que vos clients vous ont payé sans passer par rafals pendant cette période. Laissez 0 s'il n'y a rien."
      :erreur="ailleursCentimes === null ? 'Écrivez un montant positif, ex. 200 ou 200,50.' : ''"
    />
    <AppAlerte v-if="estimation" etat="neutre">
      Total déclaré : <b>{{ montant(estimation.total_centimes) }}</b><br />
      Cotisations estimées{{ urssaf.demonstration ? ' par rafals' : " par l'URSSAF" }} : <b>{{ montant(estimation.cotisations_centimes) }}</b>
    </AppAlerte>
    <AppCase v-model="certifie" texte="Je certifie que ce montant est exact." />
    <p class="text-[13px] text-texte-doux">À déclarer avant le {{ jourCourt(urssaf.a_declarer.limite) }}. Une période déclarée ne se corrige plus depuis rafals.</p>
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <template #pied>
      <AppBouton v-if="!certifie || ailleursCentimes === null" variante="verrouille" raison-verrou="Cochez « Je certifie que ce montant est exact. »">
        Envoyer à l'URSSAF
      </AppBouton>
      <AppBouton
        v-else
        :occupe="envoiEnCours"
        @click="envoyer('/declaration', { ailleurs_centimes: ailleursCentimes, certifie }, urssaf.demonstration ? 'Déclaration enregistrée (démonstration).' : `Déclaration envoyée à l'URSSAF.`)"
      >
        Envoyer à l'URSSAF
      </AppBouton>
      <AppBouton variante="secondaire" @click="fenetre = null">Annuler</AppBouton>
    </template>
  </AppFenetre>

  <AppFenetre :ouverte="fenetre === 'retirer'" titre="Retirer mon accord ?" @fermer="fenetre = null">
    <p>
      rafals ne pourra plus envoyer vos déclarations : vous déclarerez vous-même sur le site de l'URSSAF. Les déclarations
      déjà envoyées restent valables.
    </p>
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <template #pied>
      <AppBouton variante="danger" :occupe="envoiEnCours" @click="envoyer('/mandat/retirer', {}, 'Accord retiré.')">Retirer mon accord</AppBouton>
      <AppBouton variante="secondaire" @click="fenetre = null">Annuler</AppBouton>
    </template>
  </AppFenetre>
</template>
