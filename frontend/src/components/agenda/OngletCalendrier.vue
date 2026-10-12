<script setup lang="ts">
// Mon agenda › Calendrier (.doc/ihm/RM-AGENDA-IHM.md) : le calendrier d'UN métier. Le mois (ou 2 mois) en couleurs,
// le détail du ou des jours choisis à droite, les boutons « Fermeture exceptionnelle », « Ouverture exceptionnelle »
// et « Date d'arrêt » (on clique ou on glisse sur les jours), les ouvertures à gauche et les fermetures à droite en bas.
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { ErreurServeur, appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import {
  type AgendaVisible,
  type Blocage,
  JOURS,
  MOIS,
  type Minutes,
  aParis,
  ajouterJours,
  enMinutes,
  heureCourte,
  heuresOuvertes,
  jourCourt,
  jourLisible,
  jourSemaine,
  minutesEnHeure,
  minutesLisibles,
  morceauDuJour,
  periodeLisible,
} from '../../outils/agenda'
import { aujourdhuiIso } from '../../outils/dates'
import type { MetierExerce, ProfilPrestataire } from '../../outils/prestataires'
import { type RendezVousVisible, aVenir, plage } from '../../outils/rendez_vous'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBadge from '../ui/AppBadge.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppFenetre from '../ui/AppFenetre.vue'
import AppSection from '../ui/AppSection.vue'
import AppSegment from '../ui/AppSegment.vue'
import FenetreArret from './FenetreArret.vue'
import FenetrePeriode from './FenetrePeriode.vue'
import FenetreReglages from './FenetreReglages.vue'
import FenetreSemaine from './FenetreSemaine.vue'

const props = defineProps<{
  agenda: AgendaVisible
  profil: ProfilPrestataire
  /** Le métier de ce calendrier */
  metier: MetierExerce
  /** Rendez-vous montrés dans ce calendrier ; « autre » = pris dans un autre métier (il occupe quand même l'heure) */
  rendezVous: (RendezVousVisible & { autreMetier?: string })[]
  plusieursMetiers: boolean
}>()
const emit = defineEmits<{ maj: [agenda: AgendaVisible]; majProfil: [profil: ProfilPrestataire] }>()
const { afficherMessage } = useMessage()

const aujourdhui = aujourdhuiIso()
const mois = ref(aujourdhui.slice(0, 7)) // « 2026-10 »
const nombreMois = ref<1 | 2>(1) // toujours 1 mois à l'arrivée sur la page
// Jours choisis (un seul : les deux sont égaux)
const choisiDu = ref(aujourdhui)
const choisiAu = ref(aujourdhui)
const unSeulJour = computed(() => choisiDu.value === choisiAu.value)

function decaler(moisDepart: string, ecart: number): string {
  const [a, m] = moisDepart.split('-').map(Number)
  return new Date(Date.UTC(a ?? 0, (m ?? 1) - 1 + ecart, 1)).toISOString().slice(0, 7)
}
const nomMois = (unMois: string) => MOIS[Number(unMois.slice(5)) - 1] ?? ''
const moisAffiches = computed(() => (nombreMois.value === 2 ? [mois.value, decaler(mois.value, 1)] : [mois.value]))
const titreMois = computed(() => {
  const [premier, second] = moisAffiches.value
  if (!premier) return ''
  if (!second) return `${nomMois(premier)} ${premier.slice(0, 4)}`
  const memeAnnee = premier.slice(0, 4) === second.slice(0, 4)
  return `${nomMois(premier)}${memeAnnee ? '' : ` ${premier.slice(0, 4)}`} – ${nomMois(second)} ${second.slice(0, 4)}`
})

// ---------- Ce qu'on sait d'un jour ----------

interface Morceau {
  periode: Blocage
  minutes: Minutes
}
interface Jour {
  jour: string
  numero: number
  /** Semaine type, en minutes */
  plages: Minutes[]
  fermetures: Morceau[]
  ouvertures: Morceau[]
  /** La fermeture qui couvre tout le jour, s'il y en a une */
  entier: Blocage | undefined
  /** Ce qui reste réservable */
  ouvertes: Minutes[]
  /** Après la date d'arrêt du métier : fermé */
  arrete: boolean
  /** Le dernier jour du métier */
  dernier: boolean
  rendezVous: (RendezVousVisible & { autreMetier?: string })[]
}
function decrire(jour: string): Jour {
  const arrete = !!props.metier.fin_le && jour > props.metier.fin_le
  const morceaux = (periodes: Blocage[]): Morceau[] =>
    arrete ? [] : periodes.flatMap((periode) => {
      const minutes = morceauDuJour(periode, jour)
      return minutes ? [{ periode, minutes }] : []
    })
  const plages: Minutes[] = arrete ? [] : props.agenda.plages
    .filter((p) => p.jour_semaine === jourSemaine(jour))
    .map((p) => [enMinutes(p.debut), enMinutes(p.fin)])
  const fermetures = morceaux(props.agenda.blocages)
  const ouvertures = morceaux(props.agenda.ouvertures)
  return {
    jour,
    numero: Number(jour.slice(8)),
    plages,
    fermetures,
    ouvertures,
    entier: fermetures.find((f) => f.minutes[0] === 0 && f.minutes[1] === 1440)?.periode,
    ouvertes: heuresOuvertes(plages, ouvertures.map((o) => o.minutes), fermetures.map((f) => f.minutes)),
    arrete,
    dernier: props.metier.fin_le === jour,
    // Rendez-vous confirmés et demandes en attente de ce jour
    rendezVous: props.rendezVous.filter((r) => aVenir(r, new Date(0)) && aParis(r.debut).jour === jour),
  }
}
function grille(unMois: string) {
  const premier = `${unMois}-01`
  const jours: Jour[] = []
  for (let jour = premier; jour.startsWith(unMois); jour = ajouterJours(jour, 1)) jours.push(decrire(jour))
  return { mois: unMois, vides: jourSemaine(premier) - 1, jours }
}
const grilles = computed(() => moisAffiches.value.map(grille))

const etat = (j: Jour): { etat: 'ok' | 'attente' | 'neutre'; texte: string } => {
  if (j.arrete) return { etat: 'neutre', texte: 'arrêté' }
  if (j.entier) return { etat: 'attente', texte: 'fermeture exceptionnelle' }
  if (j.fermetures.length) return { etat: 'attente', texte: 'partiellement fermé' }
  if (j.ouvertures.length) return { etat: 'ok', texte: 'ouverture exceptionnelle' }
  return j.ouvertes.length ? { etat: 'ok', texte: 'ouvert' } : { etat: 'neutre', texte: 'fermé' }
}
const heuresDe = (liste: Minutes[]) => liste.map(([d, f]) => `${minutesLisibles(d)} – ${minutesLisibles(f)}`).join(' · ')
const heuresCourtes = (liste: Minutes[]) =>
  liste.map(([d, f]) => `${heureCourte(minutesEnHeure(d))}-${f === 1440 ? '24' : heureCourte(minutesEnHeure(f))}`).join(' · ')

// Partie hachurée d'une fermeture de quelques heures : la journée se lit de gauche (7 h) à droite (21 h) ;
// les heures hors de cette fenêtre sont collées aux bords.
const DEBUT_BANDE = 7 * 60
const FIN_BANDE = 21 * 60
function hachure([debut, fin]: Minutes): { left: string; width: string } | null {
  const position = (m: number) => Math.max(0, Math.min(1, (m - DEBUT_BANDE) / (FIN_BANDE - DEBUT_BANDE)))
  const gauche = position(debut)
  const droite = position(fin)
  return droite > gauche ? { left: `${(gauche * 100).toFixed(1)}%`, width: `${((droite - gauche) * 100).toFixed(1)}%` } : null
}

// ---------- Choisir des jours : clic, ou glisser d'un jour à l'autre ----------

type Mode = 'fermeture' | 'ouverture' | 'arret'
const mode = ref<Mode | null>(null)
const selection = ref<{ a: string; b: string } | null>(null) // pendant qu'on glisse
const bornes = computed(() => (selection.value ? [selection.value.a, selection.value.b].sort() : null))
let vientDeGlisser = false

function basculer(nouveau: Mode) {
  mode.value = mode.value === nouveau ? null : nouveau
}
// Changer de calendrier (de métier) : on quitte le mode en cours
watch(() => props.agenda.metier_id, () => (mode.value = null))

const jourSous = (e: PointerEvent) =>
  (document.elementFromPoint(e.clientX, e.clientY)?.closest('[data-jour]') as HTMLElement | null)?.dataset.jour
// Avec un bouton activé, on ne touche pas au passé ; pour lire, tous les jours se choisissent
const permis = (jour: string | undefined): jour is string => !!jour && (!mode.value || jour >= aujourdhui)

function appui(e: PointerEvent) {
  // Sans bouton activé, glisser au doigt sert à faire défiler la page : la sélection de plusieurs jours est à la souris
  if (!mode.value && e.pointerType !== 'mouse') return
  const jour = jourSous(e)
  if (!permis(jour)) return
  e.preventDefault()
  selection.value = { a: jour, b: jour }
}
function glissement(e: PointerEvent) {
  if (!selection.value) return
  const jour = jourSous(e)
  if (!permis(jour) || jour === selection.value.b) return
  // Date d'arrêt : un seul jour, celui sous le curseur
  selection.value = mode.value === 'arret' ? { a: jour, b: jour } : { a: selection.value.a, b: jour }
}
function relache() {
  if (!bornes.value) return
  const [du, au] = bornes.value as [string, string]
  selection.value = null
  vientDeGlisser = true
  setTimeout(() => (vientDeGlisser = false), 50)
  if (mode.value === 'arret') ouvrirArret(du)
  else if (mode.value) ouvrirPeriode(mode.value, du, au)
  else [choisiDu.value, choisiAu.value] = [du, au]
}
// Doigt ou clavier (pas de glissement) : un seul jour
function clic(jour: string) {
  if (vientDeGlisser) return
  if (!mode.value) choisiDu.value = choisiAu.value = jour
  else if (jour >= aujourdhui) mode.value === 'arret' ? ouvrirArret(jour) : ouvrirPeriode(mode.value, jour, jour)
}
onMounted(() => window.addEventListener('pointerup', relache))
onBeforeUnmount(() => window.removeEventListener('pointerup', relache))

const CONTOURS: Record<Mode, string> = {
  fermeture: 'outline-3 outline-attente', ouverture: 'outline-3 outline-ok', arret: 'outline-3 outline-erreur',
}
function classes(j: Jour) {
  const liste: string[] = []
  if (j.entier) liste.push('border-attente bg-[repeating-linear-gradient(135deg,var(--color-attente-doux)_0_6px,var(--color-surface)_6px_12px)] text-texte')
  // Ouverture exceptionnelle : même vert, bord en pointillés foncés
  else if (j.ouvertures.length) liste.push('border-2 border-dashed border-ouvert-texte bg-ouvert text-ouvert-texte')
  else if (j.plages.length) liste.push('border-ouvert bg-ouvert text-ouvert-texte')
  else liste.push('border-bord bg-neutre-doux text-texte-doux')
  if (j.jour < aujourdhui) liste.push('opacity-55')
  const dansSelection = bornes.value && j.jour >= (bornes.value[0] ?? '') && j.jour <= (bornes.value[1] ?? '')
  if (dansSelection) {
    liste.push(mode.value ? CONTOURS[mode.value] : 'outline-3 outline-primaire')
  } else if (!mode.value && !selection.value && j.jour >= choisiDu.value && j.jour <= choisiAu.value) {
    liste.push('outline-3 outline-primaire')
  }
  return liste
}

// ---------- Détail à droite ----------

const detail = computed(() => decrire(choisiDu.value))
const joursChoisis = computed(() => {
  const jours: Jour[] = []
  for (let jour = choisiDu.value; jour <= choisiAu.value; jour = ajouterJours(jour, 1)) jours.push(decrire(jour))
  return jours
})
const nombreRendezVous = computed(() => joursChoisis.value.reduce((n, j) => n + j.rendezVous.length, 0))
/** Fermetures et ouvertures qui touchent les jours choisis (pour les retirer d'ici) */
const touchees = computed(() => {
  const dans = (periodes: Blocage[]) => periodes.filter((p) => joursChoisis.value.some((j) => morceauDuJour(p, j.jour)))
  return { fermetures: dans(props.agenda.blocages), ouvertures: dans(props.agenda.ouvertures) }
})
const sansLe = (texte: string) => texte.replace(/^Le /, '')
const peutModifier = computed(() => choisiAu.value >= aujourdhui)
const premierJourModifiable = computed(() => (choisiDu.value < aujourdhui ? aujourdhui : choisiDu.value))

// ---------- Fenêtres ----------

const periode = ref<{ type: 'fermeture' | 'ouverture'; du: string; au: string } | null>(null)
function ouvrirPeriode(type: 'fermeture' | 'ouverture', du: string, au: string) {
  periode.value = { type, du, au }
}
function apresPeriode(agenda: AgendaVisible) {
  emit('maj', agenda)
  if (periode.value) choisiDu.value = choisiAu.value = periode.value.du
  mode.value = null
}
const jourArret = ref('')
function ouvrirArret(jour: string) {
  jourArret.value = jour
}
function apresArret(profil: ProfilPrestataire) {
  emit('majProfil', profil)
  choisiDu.value = choisiAu.value = jourArret.value
  mode.value = null
}
const semaineOuverte = ref(false)
const reglagesOuverts = ref(false)

async function retirerFermeture(blocage: Blocage) {
  try {
    emit('maj', await appelerServeur<AgendaVisible>(`/api/moi/agenda/blocages/${blocage.id}/retirer`, {}))
    afficherMessage('Fermeture retirée : ces horaires sont de nouveau réservables.')
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}
// Retirer une ouverture où des rendez-vous ont été pris : le serveur refuse (409) et liste ; le prestataire choisit
const retrait = ref<{ ouverture: Blocage; conflit: string } | null>(null)
async function retirerOuverture(ouverture: Blocage, rendezVous: 'annuler' | 'garder' | null = null) {
  try {
    emit('maj', await appelerServeur<AgendaVisible>(`/api/moi/agenda/ouvertures/${ouverture.id}/retirer`, { rendez_vous: rendezVous }))
    retrait.value = null
    afficherMessage('Ouverture retirée : ces horaires ne sont plus réservables.')
  } catch (e) {
    if (e instanceof ErreurServeur && e.statut === 409) retrait.value = { ouverture, conflit: e.message }
    else afficherMessage(messageErreur(e), 'erreur')
  }
}
async function retirerArret() {
  try {
    emit('majProfil', await appelerServeur<ProfilPrestataire>('/api/moi/prestataire/metiers/fin', {
      metier_id: props.metier.id, fin_le: null, suivant_id: null,
    }))
    afficherMessage(`Date d'arrêt retirée : ${props.metier.nom} continue.`)
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}

const AIDES: Record<Mode, string> = {
  fermeture: 'Fermeture exceptionnelle : appuyez sur le premier jour et glissez jusqu\'au dernier (ou cliquez un seul jour). Vous réglerez les heures ensuite.',
  ouverture: 'Ouverture exceptionnelle : appuyez sur le premier jour et glissez jusqu\'au dernier (ou cliquez un seul jour). Vous réglerez les heures ensuite.',
  arret: 'Date d\'arrêt : cliquez sur votre dernier jour de travail (un seul jour). Tous les jours d\'après seront fermés.',
}
const BOUTONS: { mode: Mode; texte: string; actif: string }[] = [
  { mode: 'fermeture', texte: 'Fermeture exceptionnelle', actif: 'border-attente bg-attente text-sur-etat' },
  { mode: 'ouverture', texte: 'Ouverture exceptionnelle', actif: 'border-ok bg-ok text-sur-etat' },
  { mode: 'arret', texte: 'Date d\'arrêt', actif: 'border-erreur bg-erreur text-sur-etat' },
]
</script>

<template>
  <AppSection class="py-3.5!">
    <div class="flex flex-wrap items-center justify-between gap-2.5">
      <AppSegment
        v-model="nombreMois"
        etiquette="Nombre de mois affichés"
        :options="[{ valeur: 1, texte: '1 mois' }, { valeur: 2, texte: '2 mois' }]"
      />
      <div class="flex flex-wrap gap-2">
        <AppBouton variante="secondaire" @click="semaineOuverte = true">Semaine type</AppBouton>
        <AppBouton variante="secondaire" @click="reglagesOuverts = true">Réglages</AppBouton>
      </div>
    </div>
  </AppSection>

  <div class="grid items-stretch gap-4 lg:grid-cols-[minmax(0,1fr)_330px]">
    <AppSection>
      <div class="flex flex-wrap items-center justify-between gap-2.5">
        <AppBouton variante="secondaire" @click="mois = decaler(mois, -1)">‹ {{ nomMois(decaler(mois, -1)) }}</AppBouton>
        <h2 class="text-xl font-bold first-letter:uppercase">{{ titreMois }}</h2>
        <AppBouton variante="secondaire" @click="mois = decaler(mois, 1)">{{ nomMois(decaler(mois, 1)) }} ›</AppBouton>
      </div>

      <div
        class="grid items-start gap-4 select-none"
        :class="[nombreMois === 2 ? 'md:grid-cols-2' : '', mode ? 'cursor-crosshair touch-none' : '']"
        @pointerdown="appui"
        @pointermove="glissement"
      >
        <div v-for="g in grilles" :key="g.mois" class="flex min-w-0 flex-col gap-1.5">
          <h3 v-if="nombreMois === 2" class="text-center text-[17px] font-bold first-letter:uppercase">{{ nomMois(g.mois) }}</h3>
          <div class="grid grid-cols-7 gap-1">
            <div v-for="nom in JOURS" :key="nom" class="pb-0.5 text-center text-xs font-semibold text-texte-doux">
              {{ nom.slice(0, 3) }}
            </div>
            <div v-for="n in g.vides" :key="`vide-${n}`" />
            <button
              v-for="j in g.jours"
              :key="j.jour"
              type="button"
              :data-jour="j.jour"
              class="relative flex flex-col gap-px overflow-hidden rounded-lg border p-1 text-left -outline-offset-1"
              :class="[classes(j), nombreMois === 2 ? 'min-h-[58px] text-[11px]' : 'min-h-[62px] text-xs sm:min-h-[74px]']"
              :aria-label="`${jourLisible(j.jour)}, ${etat(j).texte}`"
              @click="clic(j.jour)"
            >
              <template v-if="!j.entier">
                <span
                  v-for="(f, n) in j.fermetures.map((x) => hachure(x.minutes)).filter((x) => x !== null)"
                  :key="n"
                  class="absolute inset-y-0 border-x-2 border-attente bg-[repeating-linear-gradient(135deg,var(--color-attente-doux)_0_6px,transparent_6px_12px)]"
                  :style="f"
                />
              </template>
              <b class="relative text-sm">{{ j.numero }}</b>
              <!-- Textes longs sur ordinateur avec 1 mois ; courts sur téléphone et avec 2 mois -->
              <span v-if="j.entier" class="relative font-bold text-attente">
                fermé<span v-if="nombreMois === 1" class="hidden sm:inline"> (exceptionnel)</span>
              </span>
              <template v-else>
                <span v-if="nombreMois === 1" class="relative hidden sm:block">
                  {{ j.arrete ? 'arrêté' : j.plages.length ? heuresCourtes(j.plages) : j.ouvertures.length ? '' : 'fermé' }}
                </span>
                <span v-if="j.fermetures.length" class="relative self-start rounded bg-surface px-1 font-bold text-attente">
                  <span :class="nombreMois === 1 ? 'hidden sm:inline' : 'hidden'">partiellement fermé</span>
                  <span :class="nombreMois === 1 ? 'sm:hidden' : ''">partiel</span>
                </span>
                <span v-if="j.ouvertures.length" class="relative self-start rounded bg-surface px-1 font-bold text-ok">
                  <span :class="nombreMois === 1 ? 'hidden sm:inline' : 'hidden'">+ {{ heuresCourtes(j.ouvertures.map((o) => o.minutes)) }}</span>
                  <span :class="nombreMois === 1 ? 'sm:hidden' : ''">+ ouvert</span>
                </span>
              </template>
              <span v-if="j.rendezVous.length" class="relative self-start rounded bg-surface px-1 font-bold text-primaire">
                {{ j.rendezVous.length }} rdv
              </span>
              <span v-if="j.dernier" class="relative self-start rounded bg-surface px-1 font-bold text-erreur">
                fin<span v-if="nombreMois === 1" class="hidden sm:inline"> {{ metier.nom }}</span>
              </span>
            </button>
          </div>
        </div>
      </div>

      <div class="flex flex-wrap gap-2">
        <button
          v-for="b in BOUTONS"
          :key="b.mode"
          type="button"
          :aria-pressed="mode === b.mode"
          class="min-h-[42px] rounded-rafals border px-[18px] py-2.5 font-semibold transition"
          :class="mode === b.mode ? b.actif : 'border-bord bg-surface text-texte hover:bg-neutre-doux'"
          @click="basculer(b.mode)"
        >
          {{ b.texte }}
        </button>
      </div>
      <AppAlerte v-if="mode" :etat="mode === 'fermeture' ? 'attente' : mode === 'ouverture' ? 'ok' : 'erreur'">
        <div class="flex flex-wrap items-center justify-between gap-2.5">
          <span class="min-w-0 flex-1 basis-[240px]">{{ AIDES[mode] }}</span>
          <AppBouton variante="secondaire" @click="mode = null">Terminer</AppBouton>
        </div>
      </AppAlerte>

      <div class="flex flex-wrap gap-3 text-[13px] text-texte-doux">
        <span class="inline-flex items-center gap-1.5"><i class="size-3.5 rounded bg-ouvert" />ouvert</span>
        <span class="inline-flex items-center gap-1.5"><i class="size-3.5 rounded bg-neutre-doux" />fermé</span>
        <span class="inline-flex items-center gap-1.5">
          <i class="size-3.5 rounded border border-attente bg-[repeating-linear-gradient(135deg,var(--color-attente-doux)_0_3px,var(--color-surface)_3px_6px)]" />
          fermeture (hachurée sur les heures concernées)
        </span>
        <span class="inline-flex items-center gap-1.5">
          <i class="size-3.5 rounded border-2 border-dashed border-ouvert-texte bg-ouvert" />ouverture exceptionnelle
        </span>
        <span><b class="text-primaire">2 rdv</b> rendez-vous</span>
        <span><b class="text-erreur">fin …</b> dernier jour avant l'arrêt</span>
      </div>
    </AppSection>

    <!-- Détail du ou des jours choisis : même hauteur que le calendrier, défile à l'intérieur s'il dépasse -->
    <AppSection class="overflow-y-auto overscroll-contain max-lg:max-h-[70vh] lg:h-0 lg:min-h-full [&>*]:shrink-0">
      <template v-if="unSeulJour">
        <div class="flex flex-wrap items-center justify-between gap-2.5">
          <h2 class="text-xl font-bold first-letter:uppercase">{{ jourLisible(choisiDu) }}</h2>
          <AppBadge :etat="etat(detail).etat">{{ etat(detail).texte }}</AppBadge>
        </div>
        <p v-if="detail.arrete">
          <b>Fermé</b> : {{ metier.nom }} est arrêté depuis le {{ jourCourt(ajouterJours(metier.fin_le ?? '', 1)) }}.
        </p>
        <template v-else>
          <p v-if="detail.dernier" class="font-semibold text-erreur">
            Dernier jour du métier {{ metier.nom }}. Tous les jours d'après sont fermés.
          </p>
          <p v-if="detail.entier">
            <b>Fermé</b> : {{ periodeLisible(detail.entier) }}<template v-if="detail.entier.motif"> · {{ detail.entier.motif }}</template>
          </p>
          <template v-else>
            <p class="text-[14.5px] text-texte-doux">
              {{ detail.plages.length ? `${heuresDe(detail.plages)} (semaine type)` : 'Fermé ce jour-là (semaine type).' }}
            </p>
            <p v-for="f in detail.fermetures" :key="`f${f.periode.id}`" class="font-semibold text-attente">
              Fermé de {{ minutesLisibles(f.minutes[0]) }} à {{ minutesLisibles(f.minutes[1]) }}<template v-if="f.periode.motif"> · {{ f.periode.motif }}</template>
            </p>
            <p v-for="o in detail.ouvertures" :key="`o${o.periode.id}`" class="font-semibold text-ok">
              Ouvert en plus de {{ minutesLisibles(o.minutes[0]) }} à {{ minutesLisibles(o.minutes[1]) }}<template v-if="o.periode.motif"> · {{ o.periode.motif }}</template>
            </p>
            <p v-if="detail.fermetures.length || detail.ouvertures.length">
              <b>Réservable :</b> {{ detail.ouvertes.length ? heuresDe(detail.ouvertes) : 'rien ce jour-là' }}
            </p>
          </template>
        </template>
        <div v-if="detail.rendezVous.length" class="flex flex-col gap-1">
          <h3 class="text-[17px] font-bold">Rendez-vous</h3>
          <ul class="flex flex-col divide-y divide-bord text-[14px]">
            <li v-for="r in detail.rendezVous" :key="r.id" class="py-2">
              <b>{{ plage(r).split(', ')[1] }}</b> · {{ r.titre }} · {{ r.autre.nom }}
              <span v-if="r.statut === 'en_attente'" class="font-semibold text-attente">(demande en attente)</span>
              <span v-if="r.autreMetier" class="text-texte-doux">({{ r.autreMetier }})</span>
            </li>
          </ul>
        </div>
      </template>

      <template v-else>
        <div class="flex flex-wrap items-center justify-between gap-2.5">
          <h2 class="text-xl font-bold">Du {{ jourLisible(choisiDu) }} au {{ jourLisible(choisiAu) }}</h2>
          <AppBadge>{{ joursChoisis.length }} jours · {{ nombreRendezVous }} rdv</AppBadge>
        </div>
        <ul class="flex flex-col divide-y divide-bord text-[14px]">
          <li v-for="j in joursChoisis" :key="j.jour" class="flex flex-col gap-0.5 py-2.5">
            <span class="flex flex-wrap items-center gap-2">
              <b class="first-letter:uppercase">{{ jourLisible(j.jour) }}</b>
              <AppBadge :etat="etat(j).etat">{{ etat(j).texte }}</AppBadge>
            </span>
            <span class="text-texte-doux">
              <template v-if="j.arrete">Métier arrêté</template>
              <template v-else-if="j.entier">Fermé<template v-if="j.entier.motif"> · {{ j.entier.motif }}</template></template>
              <template v-else>{{ j.ouvertes.length ? heuresDe(j.ouvertes) : 'Fermé' }}</template>
            </span>
            <template v-if="!j.entier">
              <span v-for="f in j.fermetures" :key="`f${f.periode.id}`" class="font-semibold text-attente">
                Fermé de {{ minutesLisibles(f.minutes[0]) }} à {{ minutesLisibles(f.minutes[1]) }}<template v-if="f.periode.motif"> · {{ f.periode.motif }}</template>
              </span>
            </template>
            <span v-for="o in j.ouvertures" :key="`o${o.periode.id}`" class="font-semibold text-ok">
              Ouvert en plus de {{ minutesLisibles(o.minutes[0]) }} à {{ minutesLisibles(o.minutes[1]) }}<template v-if="o.periode.motif"> · {{ o.periode.motif }}</template>
            </span>
            <span v-if="j.dernier" class="font-semibold text-erreur">Dernier jour du métier {{ metier.nom }}.</span>
            <span v-for="r in j.rendezVous" :key="r.id">
              <b>{{ plage(r).split(', ')[1] }}</b> · {{ r.titre }} · {{ r.autre.nom }}
              <span v-if="r.statut === 'en_attente'" class="font-semibold text-attente">(demande en attente)</span>
              <span v-if="r.autreMetier" class="text-texte-doux">({{ r.autreMetier }})</span>
            </span>
          </li>
        </ul>
      </template>

      <div v-if="peutModifier" class="flex flex-wrap gap-2">
        <AppBouton
          v-if="!unSeulJour || (!detail.entier && !detail.arrete)"
          variante="secondaire"
          @click="ouvrirPeriode('fermeture', premierJourModifiable, choisiAu)"
        >
          {{ unSeulJour ? 'Fermer ce jour…' : 'Fermer ces jours…' }}
        </AppBouton>
        <AppBouton
          v-if="!unSeulJour || !detail.arrete"
          variante="secondaire"
          @click="ouvrirPeriode('ouverture', premierJourModifiable, choisiAu)"
        >
          Ouvrir en plus…
        </AppBouton>
        <AppBouton v-for="b in touchees.fermetures" :key="`f${b.id}`" variante="danger" @click="retirerFermeture(b)">
          Retirer la fermeture ({{ sansLe(periodeLisible(b)) }})
        </AppBouton>
        <AppBouton v-for="o in touchees.ouvertures" :key="`o${o.id}`" variante="danger" @click="retirerOuverture(o)">
          Retirer l'ouverture ({{ sansLe(periodeLisible(o)) }})
        </AppBouton>
      </div>
      <div v-if="!unSeulJour">
        <AppBouton variante="secondaire" @click="choisiAu = choisiDu">Revenir à un seul jour</AppBouton>
      </div>
    </AppSection>
  </div>

  <!-- Ouvertures à gauche, fermetures à droite -->
  <div class="grid items-start gap-4 md:grid-cols-2">
    <AppSection titre="Ouvertures exceptionnelles">
      <template #action><AppBadge etat="ok">{{ agenda.ouvertures.length }}</AppBadge></template>
      <p v-if="!agenda.ouvertures.length" class="text-[14.5px] text-texte-doux">Aucune ouverture à venir.</p>
      <div class="flex flex-col divide-y divide-bord">
        <div v-for="o in agenda.ouvertures" :key="o.id" class="flex flex-wrap items-center justify-between gap-2.5 py-2.5">
          <div>
            <b>{{ periodeLisible(o) }}</b>
            <p v-if="o.motif" class="text-[13.5px] text-texte-doux">{{ o.motif }}</p>
          </div>
          <AppBouton variante="danger" @click="retirerOuverture(o)">Retirer</AppBouton>
        </div>
      </div>
    </AppSection>
    <AppSection titre="Fermetures exceptionnelles">
      <template #action><AppBadge etat="attente">{{ agenda.blocages.length }}</AppBadge></template>
      <p v-if="!agenda.blocages.length" class="text-[14.5px] text-texte-doux">Aucune fermeture à venir.</p>
      <div class="flex flex-col divide-y divide-bord">
        <div v-for="b in agenda.blocages" :key="b.id" class="flex flex-wrap items-center justify-between gap-2.5 py-2.5">
          <div>
            <b>{{ periodeLisible(b) }}</b>
            <p v-if="b.motif" class="text-[13.5px] text-texte-doux">{{ b.motif }}</p>
          </div>
          <AppBouton variante="danger" @click="retirerFermeture(b)">Retirer</AppBouton>
        </div>
      </div>
    </AppSection>
  </div>
  <p class="text-[13px] text-texte-doux">Le motif n'est jamais montré aux clients : ils voient seulement plus ou moins d'horaires.</p>

  <AppSection v-if="metier.fin_le" titre="Date d'arrêt">
    <template #action><AppBouton variante="danger" @click="retirerArret">Retirer la date d'arrêt</AppBouton></template>
    <p>
      <b>{{ metier.nom }}</b> : dernier jour le {{ jourCourt(metier.fin_le) }}, fermé à partir du
      {{ jourCourt(ajouterJours(metier.fin_le, 1)) }}.
    </p>
  </AppSection>

  <FenetrePeriode
    :ouverte="periode !== null"
    :type="periode?.type ?? 'fermeture'"
    :du="periode?.du ?? ''"
    :au="periode?.au ?? ''"
    :agenda="agenda"
    @maj="apresPeriode"
    @fermer="periode = null"
  />
  <FenetreArret :ouverte="jourArret !== ''" :jour="jourArret" :metier="metier" :profil="profil" @maj-profil="apresArret" @fermer="jourArret = ''" />
  <FenetreSemaine :ouverte="semaineOuverte" :agenda="agenda" :metier="metier.nom" @maj="(a) => emit('maj', a)" @fermer="semaineOuverte = false" />
  <FenetreReglages
    :ouverte="reglagesOuverts"
    :agenda="agenda"
    :plusieurs-metiers="plusieursMetiers"
    @maj="(a) => emit('maj', a)"
    @fermer="reglagesOuverts = false"
  />
  <AppFenetre :ouverte="retrait !== null" titre="Retirer l'ouverture" @fermer="retrait = null">
    <AppAlerte etat="attente">
      {{ retrait?.conflit }} Annuler : chaque client est prévenu par mail. Garder : les rendez-vous restent, plus aucun
      autre horaire n'est proposé.
    </AppAlerte>
    <template #pied>
      <AppBouton variante="danger" @click="retrait && retirerOuverture(retrait.ouverture, 'annuler')">Annuler ces rendez-vous et retirer</AppBouton>
      <AppBouton variante="secondaire" @click="retrait && retirerOuverture(retrait.ouverture, 'garder')">Les garder et retirer</AppBouton>
      <AppBouton variante="secondaire" @click="retrait = null">Annuler</AppBouton>
    </template>
  </AppFenetre>
</template>
