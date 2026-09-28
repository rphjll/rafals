<script setup lang="ts">
// Administration (.doc/ihm/RM-ADMINISTRATION-IHM.md) : accords des parents à vérifier, comptes et administrateurs.
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBadge from '../components/ui/AppBadge.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppCarte from '../components/ui/AppCarte.vue'
import AppChamp from '../components/ui/AppChamp.vue'
import AppFenetre from '../components/ui/AppFenetre.vue'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'
import { age, formaterDateHeure } from '../outils/dates'

interface AccordAVerifier {
  id: number
  depose_le: string
  prenom: string
  nom: string
  date_naissance: string
  nom_fichier: string
}
interface CompteAdministre {
  id: number
  email: string
  prenom: string
  nom: string
  email_verifie: boolean
  est_administrateur: boolean
}

const route = useRoute()
const routeur = useRouter()
const { compte, chargementFait, chargerCompte } = useCompte()
const { afficherMessage } = useMessage()

const onglet = computed(() => (route.query.onglet === 'comptes' ? 'comptes' : 'accords'))
const accords = ref<AccordAVerifier[]>([])
const comptes = ref<CompteAdministre[]>([])
const erreurChargement = ref('')

async function charger() {
  if (!compte.value?.est_administrateur) return
  erreurChargement.value = ''
  try {
    accords.value = await appelerServeur<AccordAVerifier[]>('/api/admin/accords')
    comptes.value = await appelerServeur<CompteAdministre[]>('/api/admin/comptes')
  } catch (e) {
    erreurChargement.value = messageErreur(e)
  }
}
onMounted(charger)
watch(compte, charger)

// ---------- Accords ----------
function voirFichier(accord: AccordAVerifier) {
  window.open(`/api/admin/accords/${accord.id}/fichier`, '_blank')
}

async function accepter(accord: AccordAVerifier) {
  try {
    await appelerServeur(`/api/admin/accords/${accord.id}/decision`, { accepte: true })
    afficherMessage(`Accord de ${accord.prenom} ${accord.nom} accepté.`)
    await charger()
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}

const accordARefuser = ref<AccordAVerifier | null>(null)
const motif = ref('')
const erreurFenetre = ref('')

function ouvrirRefus(accord: AccordAVerifier) {
  accordARefuser.value = accord
  motif.value = ''
  erreurFenetre.value = ''
}

async function refuser() {
  const accord = accordARefuser.value
  if (!accord) return
  try {
    await appelerServeur(`/api/admin/accords/${accord.id}/decision`, { accepte: false, motif_refus: motif.value })
    accordARefuser.value = null
    afficherMessage(`Accord refusé : ${accord.prenom} ${accord.nom} verra le motif.`)
    await charger()
  } catch (e) {
    erreurFenetre.value = messageErreur(e)
  }
}

// ---------- Rôle administrateur ----------
const compteARoler = ref<CompteAdministre | null>(null)
const erreurRole = ref('')

function ouvrirRole(cible: CompteAdministre) {
  compteARoler.value = cible
  erreurRole.value = ''
}

async function changerRole() {
  const cible = compteARoler.value
  if (!cible) return
  const nommer = !cible.est_administrateur
  try {
    await appelerServeur(`/api/admin/comptes/${cible.id}/administrateur`, { est_administrateur: nommer })
    compteARoler.value = null
    afficherMessage(`${cible.prenom} ${cible.nom} ${nommer ? 'est administrateur' : "n'est plus administrateur"}.`)
    await chargerCompte() // si l'on s'est retiré son propre rôle, le menu change
    await charger()
  } catch (e) {
    erreurRole.value = messageErreur(e)
  }
}
</script>

<template>
  <AppCarte
    v-if="chargementFait && !compte?.est_administrateur"
    titre="Réservé aux administrateurs"
    intro="Cette page n'est accessible qu'aux administrateurs de rafals."
  >
    <AppBouton pleine-largeur @click="routeur.push('/')">Retour à l'accueil</AppBouton>
  </AppCarte>

  <div v-else-if="compte" class="flex flex-col gap-5">
    <h1 class="text-[28px] font-bold">Administration</h1>

    <div class="flex flex-wrap gap-1.5 border-b border-bord" role="tablist">
      <button
        v-for="o in [
          { id: 'accords', texte: 'Accords à vérifier', nombre: accords.length },
          { id: 'comptes', texte: 'Comptes', nombre: 0 },
        ]"
        :key="o.id"
        type="button"
        role="tab"
        :aria-selected="onglet === o.id"
        class="-mb-px border-b-[3px] px-3 py-2.5 font-semibold"
        :class="onglet === o.id ? 'border-primaire text-primaire' : 'border-transparent text-texte-doux'"
        @click="routeur.replace({ query: o.id === 'comptes' ? { onglet: 'comptes' } : {} })"
      >
        {{ o.texte }}
        <span v-if="o.nombre" class="ml-1 rounded-full bg-accent px-[7px] py-px text-xs text-sur-etat">{{ o.nombre }}</span>
      </button>
    </div>

    <AppAlerte v-if="erreurChargement">{{ erreurChargement }}</AppAlerte>

    <!-- Onglet « Accords à vérifier » -->
    <template v-if="onglet === 'accords'">
      <p v-if="!accords.length" class="text-texte-doux">Aucun accord à vérifier pour l'instant.</p>
      <div
        v-for="accord in accords"
        :key="accord.id"
        class="grid items-center gap-3 rounded-rafals border border-bord bg-surface p-3.5 sm:grid-cols-[1fr_auto]"
      >
        <div>
          <b>{{ accord.prenom }} {{ accord.nom }}</b> · {{ age(accord.date_naissance) }} ans · envoyé le
          {{ formaterDateHeure(accord.depose_le) }}
          <div class="text-[13px] text-texte-doux">{{ accord.nom_fichier }}</div>
        </div>
        <div class="flex flex-wrap gap-2">
          <AppBouton variante="secondaire" @click="voirFichier(accord)">Voir le fichier</AppBouton>
          <AppBouton @click="accepter(accord)">Accepter</AppBouton>
          <AppBouton variante="danger" @click="ouvrirRefus(accord)">Refuser…</AppBouton>
        </div>
      </div>
    </template>

    <!-- Onglet « Comptes » -->
    <div v-else class="overflow-x-auto rounded-rafals border border-bord bg-surface">
      <table class="w-full min-w-[640px] border-collapse text-sm">
        <thead>
          <tr class="text-left text-xs tracking-wide text-texte-doux uppercase">
            <th class="border-b border-bord px-3 py-2.5">Nom</th>
            <th class="border-b border-bord px-3 py-2.5">Adresse mail</th>
            <th class="border-b border-bord px-3 py-2.5">Adresse</th>
            <th class="border-b border-bord px-3 py-2.5">Rôle</th>
            <th class="border-b border-bord px-3 py-2.5"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="ligne in comptes" :key="ligne.id" class="border-b border-bord last:border-0">
            <td class="px-3 py-2.5">{{ ligne.nom }} {{ ligne.prenom }}</td>
            <td class="px-3 py-2.5">{{ ligne.email }}</td>
            <td class="px-3 py-2.5">
              <AppBadge :etat="ligne.email_verifie ? 'ok' : 'attente'">{{ ligne.email_verifie ? 'vérifiée' : 'non vérifiée' }}</AppBadge>
            </td>
            <td class="px-3 py-2.5"><AppBadge v-if="ligne.est_administrateur" etat="ok">administrateur</AppBadge></td>
            <td class="px-3 py-2.5 text-right">
              <AppBouton :variante="ligne.est_administrateur ? 'danger' : 'secondaire'" @click="ouvrirRole(ligne)">
                {{ ligne.est_administrateur ? 'Retirer le rôle' : 'Nommer administrateur' }}
              </AppBouton>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <AppFenetre
      :ouverte="accordARefuser !== null"
      :titre="`Refuser l'accord de ${accordARefuser?.prenom} ${accordARefuser?.nom} ?`"
      @fermer="accordARefuser = null"
    >
      <div class="flex flex-col gap-3">
        <p>Le motif sera montré à {{ accordARefuser?.prenom }}, qui pourra en renvoyer un.</p>
        <AppChamp v-model="motif" etiquette="Motif du refus" obligatoire aide="Ex. « Signature illisible »" />
        <AppAlerte v-if="erreurFenetre">{{ erreurFenetre }}</AppAlerte>
      </div>
      <template #pied>
        <AppBouton variante="danger" @click="refuser">Refuser</AppBouton>
        <AppBouton variante="secondaire" @click="accordARefuser = null">Annuler</AppBouton>
      </template>
    </AppFenetre>

    <AppFenetre
      :ouverte="compteARoler !== null"
      :titre="
        compteARoler?.est_administrateur
          ? `Retirer le rôle d'administrateur à ${compteARoler?.prenom} ${compteARoler?.nom} ?`
          : `Nommer ${compteARoler?.prenom} ${compteARoler?.nom} administrateur ?`
      "
      @fermer="compteARoler = null"
    >
      <div class="flex flex-col gap-3">
        <p v-if="compteARoler?.est_administrateur">Il ou elle garde son compte, sans l'écran Administration.</p>
        <p v-else>Tous les droits : voir tous les comptes, vérifier les accords, nommer d'autres administrateurs.</p>
        <AppAlerte v-if="erreurRole">{{ erreurRole }}</AppAlerte>
      </div>
      <template #pied>
        <AppBouton :variante="compteARoler?.est_administrateur ? 'danger' : 'principal'" @click="changerRole">
          {{ compteARoler?.est_administrateur ? 'Retirer' : 'Nommer' }}
        </AppBouton>
        <AppBouton variante="secondaire" @click="compteARoler = null">Annuler</AppBouton>
      </template>
    </AppFenetre>
  </div>
</template>
