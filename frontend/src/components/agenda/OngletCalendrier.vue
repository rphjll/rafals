<script setup lang="ts">
// Mon agenda › Calendrier (.doc/ihm/RM-AGENDA-IHM.md ; maquette validée par Raphael le 17/10/2026 :
// .doc/ihm/maquette-agenda-simple/agenda-simple-f.html) : le calendrier d'UN métier.
// - un clic sur un jour (un toucher sur téléphone) : la fenêtre « Horaires du … » ; ce qui n'est pas ouvert est fermé ;
import { computed, ref } from 'vue'
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
} from '../../outils/agenda'
import { aujourdhuiIso } from '../../outils/dates'
import type { MetierExerce, ProfilPrestataire } from '../../outils/prestataires'
import { type RendezVousVisible, aVenir } from '../../outils/rendez_vous'
import AppBouton from '../ui/AppBouton.vue'
import AppFenetre from '../ui/AppFenetre.vue'
import AppIcone from '../ui/AppIcone.vue'
import AppSegment from '../ui/AppSegment.vue'
import FenetreJour from './FenetreJour.vue'
import FenetreReglages from './FenetreReglages.vue'

const props = defineProps<{
  agenda: AgendaVisible
  profil: ProfilPrestataire
  /** Le métier de ce calendrier */
  metier: MetierExerce
  /** Rendez-vous montrés dans ce calendrier ; « autre » = pris dans un autre métier (il occupe quand même l'heure) */
  rendezVous: (RendezVousVisible & { autreMetier?: string })[]
  plusieursMetiers: boolean
}>()
// apercu : le changement montré tout de suite, avant la réponse du serveur ; maj : ce que le serveur a enregistré
const emit = defineEmits<{ maj: [agenda: AgendaVisible]; apercu: [agenda: AgendaVisible]; majProfil: [profil: ProfilPrestataire]; semaine: [] }>()
const { afficherMessage } = useMessage()

/** Motif posé par le serveur sur les morceaux d'« horaires d'un jour » (services/agenda.py, MOTIF_HORAIRES_DU_JOUR) */
const MARQUE = 'Horaires du jour'
const aujourdhui = aujourdhuiIso()
const mois = ref(aujourdhui.slice(0, 7)) // « 2026-10 »

function decaler(moisDepart: string, ecart: number): string {
  const [a, m] = moisDepart.split('-').map(Number)
  return new Date(Date.UTC(a ?? 0, (m ?? 1) - 1 + ecart, 1)).toISOString().slice(0, 7)
}
const nomMois = (unMois: string) => MOIS[Number(unMois.slice(5)) - 1] ?? ''
// « 2 mois » : le mois et le suivant côte à côte, seulement sur ordinateur (Raphael, 22/10/2026 : « je veux une option
// pour pouvoir voir 2 mois en meme temps dans la meme page cette option que sur pc »). Toujours 1 mois à l'arrivée.
const nbMois = ref<1 | 2>(1)
const OPTIONS_MOIS = [{ valeur: 1 as const, texte: '1 mois' }, { valeur: 2 as const, texte: '2 mois' }]
/** « octobre – novembre 2026 », « décembre 2026 – janvier 2027 » */
const titreDeuxMois = computed(() => {
  const suivant = decaler(mois.value, 1)
  const annee = mois.value.slice(0, 4)
  return annee === suivant.slice(0, 4)
    ? `${nomMois(mois.value)} – ${nomMois(suivant)} ${annee}`
    : `${nomMois(mois.value)} ${annee} – ${nomMois(suivant)} ${suivant.slice(0, 4)}`
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
  /** Ce jour a des horaires différents de sa semaine type (fenêtre « Horaires du … », ou une ancienne exception) */
  modifie: boolean
  /** Ce qui reste ouvert */
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
    entier: fermetures.find((f) => f.minutes[0] === 0 && f.minutes[1] === 1440 && f.periode.motif !== MARQUE)?.periode,
    modifie: fermetures.length > 0 || ouvertures.length > 0,
    ouvertes: heuresOuvertes(plages, ouvertures.map((o) => o.minutes), fermetures.map((f) => f.minutes)),
    arrete,
    dernier: props.metier.fin_le === jour,
    rendezVous: props.rendezVous.filter((r) => aVenir(r, new Date(0)) && aParis(r.debut).jour === jour),
  }
}
function grilleDe(unMois: string) {
  const premier = `${unMois}-01`
  const jours: Jour[] = []
  for (let jour = premier; jour.startsWith(unMois); jour = ajouterJours(jour, 1)) jours.push(decrire(jour))
  return { mois: unMois, vides: jourSemaine(premier) - 1, jours }
}
/** Le mois montré, puis le suivant (affiché seulement avec « 2 mois », sur ordinateur) */
const grilles = computed(() => [grilleDe(mois.value), grilleDe(decaler(mois.value, 1))])
const heuresDe = (liste: Minutes[]) => liste.map(([d, f]) => `${minutesLisibles(d)} – ${minutesLisibles(f)}`).join(' · ')
/** « 9-12 · 14-19 » */
const heuresCourtes = (liste: Minutes[]) =>
  liste.map(([d, f]) => `${heureCourte(minutesEnHeure(d))}-${f === 1440 ? '24' : heureCourte(minutesEnHeure(f))}`).join(' · ')

// Heures fermées hachurées en rouge : la case se lit de gauche (0 h) à droite (24 h). Tout ce qui n'est pas ouvert est
// fermé (Raphael, 21/10/2026 : semaine type de 8 h à 20 h → hachuré de 0 h à 8 h et de 20 h à 24 h).
function hachure([debut, fin]: Minutes): { left: string; width: string } | null {
  return fin > debut ? { left: `${((debut / 1440) * 100).toFixed(2)}%`, width: `${(((fin - debut) / 1440) * 100).toFixed(2)}%` } : null
}
/** Une bande verte par plage ouverte, posée sur le fond hachuré : de 0 h (à gauche) à 24 h (à droite) */
const bande = (o: Minutes) => hachure(o) ?? {}
const etat = (j: Jour) =>
  j.arrete ? 'arrêté' : j.ouvertes.length ? `ouvert ${heuresDe(j.ouvertes)}` : 'fermé'

// Un clic (ou un toucher) sur un jour : la fenêtre « Horaires du … » (Raphael, 21/10/2026 : « enleve le sistème de
// fermeture exeptionel et ouverture exeptionel et juste quand il clic sur le jours il dis quand il est ouvert »)
function clic(jour: string) {
  ouvrirJour(jour)
}

// ---------- Comme la maquette : l'écran change à l'instant ; le serveur enregistre derrière ----------
// Chaque geste change d'abord l'écran (« aperçu »), puis part au serveur dans une file : un geste après l'autre, jamais
// deux en même temps. L'écran ne relit ce que le serveur a enregistré qu'une fois la file vide : il ne clignote plus.
let provisoire = -1
/** Un moment de ce jour, heure de l'ordinateur (Paris) : « 2026-10-20 » + 540 → 9 h 00 ; 1440 → minuit le lendemain */
function moment(jour: string, minutes: number): string {
  if (minutes >= 1440) return new Date(`${ajouterJours(jour, 1)}T00:00:00`).toISOString()
  return new Date(`${jour}T${minutesEnHeure(minutes)}:00`).toISOString()
}
const temps = (iso: string) => new Date(iso).getTime()
function nouvelle(debut: string, fin: string, motif: string | null = null): Blocage {
  return { id: provisoire--, debut, fin, motif }
}
/** Ce qui reste d'une période une fois ce jour retiré (avant et après) */
function sansCeJour(p: Blocage, jour: string): Blocage[] {
  const a = temps(moment(jour, 0))
  const b = temps(moment(jour, 1440))
  if (temps(p.debut) >= b || temps(p.fin) <= a) return [p]
  return [
    ...(temps(p.debut) < a ? [{ ...p, id: provisoire--, fin: moment(jour, 0) }] : []),
    ...(temps(p.fin) > b ? [{ ...p, id: provisoire--, debut: moment(jour, 1440) }] : []),
  ]
}
function apercu(blocages: Blocage[], ouvertures: Blocage[]) {
  emit('apercu', { ...props.agenda, blocages, ouvertures })
}

/** Gestes en route vers le serveur ; la file les envoie un par un, dans l'ordre */
let enCours = 0
let file: Promise<void> = Promise.resolve()
function envoyer(tache: () => Promise<void>) {
  enCours++
  file = file.then(async () => {
    try {
      await tache()
    } catch (e) {
      afficherMessage(messageErreur(e), 'erreur')
    } finally {
      enCours--
      if (enCours === 0) await relire()
    }
  })
}
/** L'écran reprend ce que le serveur a vraiment enregistré (file vide, ou après un refus) */
async function relire() {
  try {
    emit('maj', await appelerServeur<AgendaVisible>(`/api/moi/agenda?metier_id=${props.agenda.metier_id}`))
  } catch {
    // l'erreur d'origine est déjà affichée
  }
}

// Des rendez-vous gênent : le serveur refuse (409) et les liste ; le prestataire choisit, puis on renvoie le même geste
type Choix = 'annuler' | 'garder'
const conflit = ref<{ titre: string; texte: string; annuler: string; garder: string; refaire: (choix: Choix) => void } | null>(null)
async function avecChoix(appel: (choix: Choix | null) => Promise<unknown>, titre: string, verbe: string, choix: Choix | null) {
  try {
    await appel(choix)
  } catch (e) {
    if (!(e instanceof ErreurServeur && e.statut === 409)) throw e
    conflit.value = {
      titre, texte: e.message, annuler: `Annuler ces rendez-vous et ${verbe}`, garder: `Les garder et ${verbe}`,
      refaire: (c) => {
        conflit.value = null
        envoyer(() => avecChoix(appel, titre, verbe, c))
      },
    }
  }
}

// ---------- Clic sur un jour : la fenêtre « Horaires du … » ----------

const fenetreJour = ref<Jour | null>(null)
function ouvrirJour(jour: string) {
  if (jour < aujourdhui) return afficherMessage('Ce jour est passé : ses horaires ne se changent plus.', 'erreur')
  const j = decrire(jour)
  if (j.arrete) return afficherMessage(`${props.metier.nom} est arrêté à cette date : ce jour reste fermé.`, 'erreur')
  fenetreJour.value = j
}
/** « Ouvert seulement à ces heures » ce jour-là (comme le serveur : services/agenda.py, fixer_jour) */
function enregistrerJour(jour: string, ouvert: Minutes[]) {
  const j = decrire(jour)
  const fermees = ouvert.reduce<Minutes[]>((reste, [d, f]) => reste.flatMap(([x, y]): Minutes[] =>
    f <= x || d >= y ? [[x, y]] : [...(x < d ? [[x, d] as Minutes] : []), ...(f < y ? [[f, y] as Minutes] : [])]), [[0, 1440]])
  const enPlus = j.plages.reduce<Minutes[]>((reste, [d, f]) => reste.flatMap(([x, y]): Minutes[] =>
    f <= x || d >= y ? [[x, y]] : [...(x < d ? [[x, d] as Minutes] : []), ...(f < y ? [[f, y] as Minutes] : [])]), ouvert)
  apercu(
    [...props.agenda.blocages.flatMap((p) => sansCeJour(p, jour)), ...fermees.map(([d, f]) => nouvelle(moment(jour, d), moment(jour, f), MARQUE))],
    [...props.agenda.ouvertures.flatMap((p) => sansCeJour(p, jour)), ...enPlus.map(([d, f]) => nouvelle(moment(jour, d), moment(jour, f), MARQUE))],
  )
  fenetreJour.value = null
  afficherMessage(`Horaires enregistrés : ${jourCourt(jour)}, ouvert ${heuresDe(ouvert)}.`)
  envoyer(() => avecChoix(
    (choix) => appelerServeur(`/api/moi/agenda/jours/${jour}`, { metier_id: props.agenda.metier_id, ouvert, rendez_vous: choix }),
    'Des rendez-vous tombent en dehors de ces heures', 'enregistrer', null,
  ))
}
/** [Remettre les horaires habituels] : seuls les morceaux « Horaires du jour » de ce jour-là partent */
function remettreJour(jour: string) {
  apercu(props.agenda.blocages.flatMap((p) => sansCeJour(p, jour)), props.agenda.ouvertures.flatMap((p) => sansCeJour(p, jour)))
  fenetreJour.value = null
  afficherMessage(`${jourCourt(jour)} : de nouveau vos horaires habituels.`)
  envoyer(() => appelerServeur(`/api/moi/agenda/jours/${jour}`, { metier_id: props.agenda.metier_id }).then(() => undefined))
}

const reglagesOuverts = ref(false)
</script>

<template>
  <!-- Le calendrier de la grande maquette : 1 ou 2 mois, une case par jour ; heures ouvertes en vert sur fond hachuré rouge -->
  <div class="carte cal p-[18px]">
    <div class="cal-barre">
      <AppSegment v-model="nbMois" en-ligne etiquette="Nombre de mois montrés" :options="OPTIONS_MOIS" class="max-lg:hidden!" />
      <div class="btns" style="margin-left: auto">
        <button type="button" class="btn btn-2 btn-petit" @click="emit('semaine')"><AppIcone nom="agenda" />Semaine type</button>
        <button type="button" class="btn btn-2 btn-petit" @click="reglagesOuverts = true"><AppIcone nom="reglages" />Réglages</button>
      </div>
    </div>
    <div class="mois-nav">
      <button type="button" class="btn btn-2 btn-petit" aria-label="Mois précédent" @click="mois = decaler(mois, -1)">‹ {{ nomMois(decaler(mois, -1)) }}</button>
      <h2 class="first-letter:uppercase">
        <span :class="nbMois === 2 ? 'lg:hidden' : ''">{{ nomMois(mois) }} {{ mois.slice(0, 4) }}</span>
        <span v-if="nbMois === 2" class="max-lg:hidden">{{ titreDeuxMois }}</span>
      </h2>
      <button type="button" class="btn btn-2 btn-petit" aria-label="Mois suivant" @click="mois = decaler(mois, 1)">{{ nomMois(decaler(mois, 1)) }} ›</button>
    </div>
    <p class="doux petit">Cliquez sur un jour pour dire quand vous êtes ouvert ce jour-là. Le reste du temps, vous êtes fermé (hachuré en rouge).</p>

    <div class="mois-liste" :class="{ 'lg:grid-cols-2': nbMois === 2, deuxMois: nbMois === 2 }">
      <div v-for="(grille, rang) in grilles.slice(0, nbMois)" :key="grille.mois" class="mois" :class="rang === 1 ? 'max-lg:hidden!' : ''">
        <p v-if="nbMois === 2" class="mois-nom first-letter:uppercase max-lg:hidden">{{ nomMois(grille.mois) }} {{ grille.mois.slice(0, 4) }}</p>
        <div class="sem-tete"><span v-for="nom in JOURS" :key="nom">{{ nom.slice(0, 3) }}</span></div>
        <div class="grille-j select-none">
          <span v-for="n in grille.vides" :key="`vide-${n}`" />
          <button
            v-for="j in grille.jours"
            :key="j.jour"
            type="button"
            class="jcase"
            :class="{ passe: j.jour < aujourdhui, auj: j.jour === aujourdhui }"
            :disabled="j.jour < aujourdhui"
            :data-jour="j.jour"
            :aria-label="`${jourLisible(j.jour)} : ${etat(j)}${j.rendezVous.length ? `, ${j.rendezVous.length} rendez-vous` : ''}`"
            @click="clic(j.jour)"
          >
            <span class="bandes"><i v-for="(o, n) in j.ouvertes" :key="n" :style="bande(o)" /></span>
            <b>{{ j.numero }}</b>
            <small v-if="j.ouvertes.length && nbMois === 1" class="h">{{ heuresCourtes(j.ouvertes) }}</small>
            <span v-if="j.rendezVous.length" class="nrdv">{{ j.rendezVous.length }} rdv</span>
            <span v-if="j.dernier" class="nrdv" style="background: var(--erreur); color: #fff">fin {{ metier.nom }}</span>
          </button>
        </div>
      </div>
    </div>

    <div class="legende">
      <span><i class="lg lg-ouvert" />ouvert</span>
      <span><i class="lg lg-ferme" />fermé (hachuré sur les heures fermées, de 0 h à gauche à 24 h à droite)</span>
      <span><span class="nrdv">2 rdv</span>rendez-vous</span>
      <span><i class="lg lg-auj" />aujourd’hui</span>
      <span v-if="metier.fin_le"><span class="nrdv" style="background: var(--erreur); color: #fff">fin</span>dernier jour avant l'arrêt</span>
    </div>
  </div>

  <FenetreJour
    :ouverte="fenetreJour !== null"
    :jour="fenetreJour?.jour ?? ''"
    :depart="fenetreJour?.ouvertes ?? []"
    :modifie="!!fenetreJour?.modifie"
    :habituelles="fenetreJour?.plages.length ? heuresDe(fenetreJour.plages) : 'fermé'"
    :metier="metier.nom"
    @enregistrer="(plages) => fenetreJour && enregistrerJour(fenetreJour.jour, plages)"
    @remettre="fenetreJour && remettreJour(fenetreJour.jour)"
    @fermer="fenetreJour = null"
  />
  <FenetreReglages
    :ouverte="reglagesOuverts"
    :agenda="agenda"
    :plusieurs-metiers="plusieursMetiers"
    @maj="(a) => emit('maj', a)"
    @fermer="reglagesOuverts = false"
  />
  <AppFenetre :ouverte="conflit !== null" :titre="conflit?.titre ?? ''" @fermer="conflit = null">
    <div class="bandeau b-att">{{ conflit?.texte }} Annuler : chaque client est prévenu par mail. Garder : les rendez-vous restent.</div>
    <template #pied>
      <button type="button" class="btn btn-danger" @click="conflit?.refaire('annuler')">{{ conflit?.annuler }}</button>
      <AppBouton variante="secondaire" @click="conflit?.refaire('garder')">{{ conflit?.garder }}</AppBouton>
      <AppBouton variante="secondaire" @click="(conflit = null), relire()">Ne rien changer</AppBouton>
    </template>
  </AppFenetre>
</template>
