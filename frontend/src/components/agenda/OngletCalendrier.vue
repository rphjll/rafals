<script setup lang="ts">
// Mon agenda › Calendrier (.doc/ihm/RM-AGENDA-IHM.md) : le mois en couleurs (ouvert, fermé, bloqué, fin d'un métier),
// le détail d'un jour, les périodes bloquées à venir, et la fenêtre « Bloquer une période ».
import { computed, ref } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import {
  type AgendaVisible,
  type Blocage,
  JOURS,
  MOIS,
  ajouterJours,
  bloqueCeJour,
  heure,
  heureCourte,
  jourCourt,
  jourLisible,
  jourSemaine,
  periodeLisible,
} from '../../outils/agenda'
import { aujourdhuiIso } from '../../outils/dates'
import type { ProfilPrestataire } from '../../outils/prestataires'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBadge from '../ui/AppBadge.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppCase from '../ui/AppCase.vue'
import AppChamp from '../ui/AppChamp.vue'
import AppFenetre from '../ui/AppFenetre.vue'
import AppSection from '../ui/AppSection.vue'

const props = defineProps<{ agenda: AgendaVisible; profil: ProfilPrestataire }>()
const emit = defineEmits<{ maj: [agenda: AgendaVisible] }>()
const { afficherMessage } = useMessage()

const aujourdhui = aujourdhuiIso()
const mois = ref(aujourdhui.slice(0, 7)) // « 2026-10 »
const choisi = ref(aujourdhui)

function changerMois(ecart: number) {
  const [a, m] = mois.value.split('-').map(Number)
  const date = new Date(Date.UTC(a ?? 0, (m ?? 1) - 1 + ecart, 1))
  mois.value = date.toISOString().slice(0, 7)
}
const titreMois = computed(() => {
  const [a, m] = mois.value.split('-').map(Number)
  return `${MOIS[(m ?? 1) - 1]} ${a}`
})
const nomMois = (ecart: number) => {
  const [a, m] = mois.value.split('-').map(Number)
  return MOIS[(((m ?? 1) - 1 + ecart) % 12 + 12) % 12] ?? `${a}`
}

// Dates de fin des métiers (ex. « fin Plombier » le 15/10)
const fins = computed(() =>
  [props.profil.metier_principal, ...props.profil.metiers_secondaires]
    .filter((m) => m.fin_le)
    .map((m) => ({ jour: m.fin_le ?? '', nom: m.nom })),
)

interface Jour {
  jour: string
  numero: number
  plages: string
  bloque: Blocage | undefined
  fins: string[]
}
function decrire(jour: string): Jour {
  const plages = props.agenda.plages.filter((p) => p.jour_semaine === jourSemaine(jour))
  return {
    jour,
    numero: Number(jour.slice(8)),
    plages: plages.map((p) => `${heureCourte(p.debut)}-${heureCourte(p.fin)}`).join(' · '),
    bloque: props.agenda.blocages.find((b) => bloqueCeJour(b, jour)),
    fins: fins.value.filter((f) => f.jour === jour).map((f) => f.nom),
  }
}
const cases = computed(() => {
  const premier = `${mois.value}-01`
  const vides = jourSemaine(premier) - 1
  const jours: Jour[] = []
  for (let jour = premier; jour.startsWith(mois.value); jour = ajouterJours(jour, 1)) jours.push(decrire(jour))
  return { vides, jours }
})
const detail = computed(() => decrire(choisi.value))
const plagesDuJour = computed(() =>
  props.agenda.plages
    .filter((p) => p.jour_semaine === jourSemaine(choisi.value))
    .map((p) => `${heure(p.debut)} – ${heure(p.fin)}`)
    .join(' · '),
)

function classes(j: Jour) {
  if (j.bloque) return 'border-attente bg-[repeating-linear-gradient(135deg,var(--color-attente-doux)_0_6px,var(--color-surface)_6px_12px)]'
  return j.plages ? 'border-bord bg-ok-doux' : 'border-bord bg-neutre-doux text-texte-doux'
}

// ---------- Bloquer / débloquer ----------
const fenetre = ref(false)
const quelquesHeures = ref(false)
const du = ref('')
const au = ref('')
const le = ref('')
const de = ref('14:00')
const a = ref('16:00')
const motif = ref('')
const erreur = ref('')

function ouvrir(jour: string, heures: boolean) {
  du.value = au.value = le.value = jour
  quelquesHeures.value = heures
  motif.value = ''
  erreur.value = ''
  fenetre.value = true
}

async function bloquer() {
  erreur.value = ''
  // Des jours entiers « du 20/10 au 24/10 inclus » : du 20/10 0 h au 25/10 0 h (heure de Paris)
  const [debut, fin] = quelquesHeures.value
    ? [`${le.value}T${de.value}`, `${le.value}T${a.value}`]
    : [`${du.value}T00:00`, `${ajouterJours(au.value, 1)}T00:00`]
  if (!le.value || !du.value || !au.value) {
    erreur.value = 'Choisissez les dates.'
    return
  }
  try {
    const agenda = await appelerServeur<AgendaVisible>('/api/moi/agenda/blocages', { debut, fin, motif: motif.value })
    emit('maj', agenda)
    fenetre.value = false
    const nouveau = agenda.blocages.find((b) => !props.agenda.blocages.some((ancien) => ancien.id === b.id))
    afficherMessage(`Période bloquée : ${nouveau ? periodeLisible(nouveau).toLowerCase() : ''}.`)
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}

async function debloquer(blocage: Blocage) {
  try {
    emit('maj', await appelerServeur<AgendaVisible>(`/api/moi/agenda/blocages/${blocage.id}/retirer`, {}))
    afficherMessage('Période débloquée : ces horaires sont de nouveau réservables.')
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}
</script>

<template>
  <AppSection>
    <div class="flex flex-wrap items-center justify-between gap-2.5">
      <AppBouton variante="secondaire" @click="changerMois(-1)">‹ {{ nomMois(-1) }}</AppBouton>
      <h2 class="text-xl font-bold first-letter:uppercase">{{ titreMois }}</h2>
      <AppBouton variante="secondaire" @click="changerMois(1)">{{ nomMois(1) }} ›</AppBouton>
    </div>
    <div class="grid grid-cols-7 gap-1">
      <div v-for="nom in JOURS" :key="nom" class="pb-1 text-center text-xs font-semibold text-texte-doux">
        {{ nom.slice(0, 3) }}
      </div>
      <div v-for="n in cases.vides" :key="`vide-${n}`" />
      <button
        v-for="j in cases.jours"
        :key="j.jour"
        type="button"
        class="flex min-h-[58px] flex-col gap-0.5 overflow-hidden rounded-lg border p-1 text-left text-xs"
        :class="[classes(j), j.jour === choisi ? 'outline-3 outline-primaire' : '', j.jour < aujourdhui ? 'opacity-60' : '']"
        :aria-label="jourLisible(j.jour)"
        @click="choisi = j.jour"
      >
        <b class="text-sm">{{ j.numero }}</b>
        <span v-if="j.bloque" class="font-bold text-attente">bloqué</span>
        <span v-else-if="j.plages" class="hidden sm:block">{{ j.plages }}</span>
        <span v-else class="hidden sm:block">fermé</span>
        <span v-for="nom in j.fins" :key="nom" class="font-bold text-erreur">fin {{ nom }}</span>
      </button>
    </div>
    <div class="flex flex-wrap gap-3 text-[13px] text-texte-doux">
      <span class="inline-flex items-center gap-1.5"><i class="size-3.5 rounded bg-ok-doux" />ouvert</span>
      <span class="inline-flex items-center gap-1.5"><i class="size-3.5 rounded bg-neutre-doux" />fermé</span>
      <span class="inline-flex items-center gap-1.5"><i class="size-3.5 rounded bg-attente-doux" />bloqué</span>
      <span><b class="text-erreur">fin …</b> date de fin d'un métier</span>
    </div>
  </AppSection>

  <AppSection :titre="jourLisible(choisi)">
    <template #action>
      <AppBadge :etat="detail.bloque ? 'attente' : detail.plages ? 'ok' : 'neutre'">
        {{ detail.bloque ? 'bloqué' : detail.plages ? 'ouvert' : 'fermé' }}
      </AppBadge>
    </template>
    <p class="text-[14.5px] text-texte-doux">
      <template v-if="detail.bloque">
        {{ periodeLisible(detail.bloque) }}<template v-if="detail.bloque.motif"> · {{ detail.bloque.motif }}</template>
      </template>
      <template v-else-if="plagesDuJour">{{ plagesDuJour }} (semaine type)</template>
      <template v-else>Fermé ce jour-là (semaine type).</template>
    </p>
    <p v-for="nom in detail.fins" :key="nom" class="text-[14.5px] font-semibold text-erreur">
      Dernier jour du métier {{ nom }}.
    </p>
    <div v-if="choisi >= aujourdhui" class="flex flex-wrap gap-2">
      <AppBouton v-if="detail.bloque" variante="danger" @click="detail.bloque && debloquer(detail.bloque)">
        Débloquer cette période
      </AppBouton>
      <template v-else>
        <AppBouton variante="secondaire" @click="ouvrir(choisi, false)">Bloquer ce jour</AppBouton>
        <AppBouton variante="secondaire" @click="ouvrir(choisi, true)">Bloquer quelques heures…</AppBouton>
      </template>
    </div>
  </AppSection>

  <AppSection titre="Périodes bloquées à venir">
    <template #action>
      <AppBouton @click="ouvrir(choisi >= aujourdhui ? choisi : aujourdhui, false)">Bloquer une période…</AppBouton>
    </template>
    <p v-if="!agenda.blocages.length" class="text-[14.5px] text-texte-doux">Aucune période bloquée.</p>
    <div class="flex flex-col divide-y divide-bord">
      <div v-for="b in agenda.blocages" :key="b.id" class="flex flex-wrap items-center justify-between gap-2.5 py-2.5">
        <div>
          <b>{{ periodeLisible(b) }}</b>
          <span v-if="b.motif" class="text-[13.5px] text-texte-doux"> · {{ b.motif }}</span>
        </div>
        <AppBouton variante="danger" @click="debloquer(b)">Débloquer</AppBouton>
      </div>
    </div>
    <p class="text-[13px] text-texte-doux">Le motif n'est jamais montré aux clients : ils voient seulement moins d'horaires.</p>
  </AppSection>

  <AppSection v-if="fins.length" titre="Dates de fin de métier">
    <p v-for="f in fins" :key="f.nom" class="text-[14.5px]">
      <b>{{ f.nom }}</b> : dernier jour le {{ jourCourt(f.jour) }}.
    </p>
    <p class="text-[13px] text-texte-doux">
      Réglées dans <RouterLink to="/proposer" class="font-semibold text-primaire">Mon activité › Mes métiers</RouterLink>.
    </p>
  </AppSection>

  <AppFenetre :ouverte="fenetre" titre="Bloquer une période" @fermer="fenetre = false">
    <form class="flex flex-col gap-3" @submit.prevent="bloquer">
      <AppCase v-model="quelquesHeures" texte="Seulement quelques heures" />
      <div v-if="quelquesHeures" class="flex flex-col gap-3">
        <AppChamp v-model="le" etiquette="Le" type="date" :min="aujourdhui" obligatoire />
        <div class="grid grid-cols-2 gap-3">
          <AppChamp v-model="de" etiquette="De" type="time" obligatoire />
          <AppChamp v-model="a" etiquette="À" type="time" obligatoire />
        </div>
      </div>
      <div v-else class="grid gap-3 sm:grid-cols-2">
        <AppChamp v-model="du" etiquette="Du" type="date" :min="aujourdhui" obligatoire />
        <AppChamp v-model="au" etiquette="Au (inclus)" type="date" :min="du" obligatoire />
      </div>
      <AppChamp v-model="motif" etiquette="Motif (pour vous seul)" maxlength="120" placeholder="ex. Congés, dentiste…" />
      <p class="text-[13.5px]">
        Les clients ne verront plus d'horaires pendant cette période. (Rendez-vous déjà pris : vous choisirez de les annuler
        ou de les garder, quand les rendez-vous existeront.)
      </p>
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    </form>
    <template #pied>
      <AppBouton @click="bloquer">Bloquer</AppBouton>
      <AppBouton variante="secondaire" @click="fenetre = false">Annuler</AppBouton>
    </template>
  </AppFenetre>
</template>
