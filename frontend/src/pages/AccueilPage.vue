<script setup lang="ts">
// Accueil (.doc/ihm/RM-ACCUEIL-IHM.md), identique à la grande maquette depuis le 10/11/2026 :
// - le bandeau vert foncé : « Bonjour Karim », « De quoi avez-vous besoin aujourd'hui ? », la recherche et les services ;
// - « Votre journée » : les chiffres de « Mon activité » ;
// - « Prochain rendez-vous » ;
// - « Près de chez vous » : les 3 prestataires les plus proches.
// Les demandes des clients sont dans l'onglet « Demandes » ; on publie la sienne par [Publier une demande].
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import ChiffresActivite from '../components/prestataire/ChiffresActivite.vue'
import CarteResultat from '../components/recherche/CarteResultat.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBadge from '../components/ui/AppBadge.vue'
import AppIcone from '../components/ui/AppIcone.vue'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'
import { useMetiers } from '../composables/useMetiers'
import type { ActiviteChiffree } from '../outils/activite'
import type { ProfilPrestataire } from '../outils/prestataires'
import { type CarteResultat as Carte, type PageRubriques, villeRetenue } from '../outils/recherche'
import { type RendezVousVisible, aVenir, badgeRendezVous } from '../outils/rendez_vous'

const routeur = useRouter()
const { compte, renvoyerLienVerification } = useCompte()
const { afficherMessage } = useMessage()
const { dossiers, chargerDossiers } = useMetiers()
onMounted(() => chargerDossiers().catch(() => {}))

// La recherche du bandeau ouvre « Trouver » avec le texte tapé ; un service ouvre « Trouver » sur ce service
const texte = ref('')
function chercher() {
  routeur.push({ path: '/trouver', query: texte.value.trim() ? { q: texte.value.trim() } : {} })
}
const services = computed(() => dossiers.value.slice(0, 6))

const chiffres = ref<ActiviteChiffree | null>(null)
const prochain = ref<RendezVousVisible | null>(null)
const ville = ref<{ id: number; nom: string } | null>(villeRetenue())
const proches = ref<Carte[]>([])
const erreur = ref('')

watch(
  compte,
  async (c) => {
    chiffres.value = null
    prochain.value = null
    if (c) {
      appelerServeur<ActiviteChiffree>('/api/moi/activite').then((r) => (chiffres.value = r)).catch(() => {})
      const chemin = c.prestataire_id ? '/api/moi/prestataire/rendez-vous' : '/api/moi/rendez-vous'
      appelerServeur<RendezVousVisible[]>(chemin)
        .then((liste) => (prochain.value = liste.filter((r) => aVenir(r)).sort((a, b) => a.debut.localeCompare(b.debut))[0] ?? null))
        .catch(() => {})
      // Un prestataire : les prestataires autour de sa ville, s'il n'en a pas donné d'autre dans « Trouver »
      if (c.prestataire_id && !ville.value) {
        const p = await appelerServeur<ProfilPrestataire>('/api/moi/prestataire').catch(() => null)
        if (p) ville.value = p.commune
      }
    }
    chargerProches()
  },
  { immediate: true },
)
async function chargerProches() {
  if (!ville.value) return
  try {
    const page = await appelerServeur<PageRubriques>(`/api/recherche/rubriques?commune_id=${ville.value.id}`)
    const vus = new Map<number, Carte>()
    for (const r of page.rubriques) for (const carte of r.resultats) if (carte.prestataire_id !== compte.value?.prestataire_id && !vus.has(carte.prestataire_id)) vus.set(carte.prestataire_id, carte)
    proches.value = [...vus.values()].sort((a, b) => a.distance_km - b.distance_km).slice(0, 3)
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}

// « 14 h », « Jeudi 12 novembre · Pessac »
const PARIS = { timeZone: 'Europe/Paris' } as const
const heureCourte = (iso: string) => {
  const [h, m] = new Date(iso).toLocaleTimeString('fr-FR', { ...PARIS, hour: '2-digit', minute: '2-digit' }).split(':')
  return `${Number(h)} h${m === '00' ? '' : ` ${m}`}`
}
const jourLong = (iso: string) => {
  const t = new Date(iso).toLocaleDateString('fr-FR', { ...PARIS, weekday: 'long', day: 'numeric', month: 'long' })
  return t.charAt(0).toUpperCase() + t.slice(1)
}
// La ville d'une adresse « 12 rue des Lilas, 33600 Pessac » → « Pessac »
const villeDe = (adresse: string | null) => (adresse?.split(',').pop() ?? '').replace(/\d{5}/, '').trim()

async function renvoyerLien() {
  try {
    afficherMessage(await renvoyerLienVerification(compte.value?.email ?? ''))
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}
</script>

<template>
  <div class="page">
    <AppAlerte v-if="compte && !compte.email_verifie" etat="attente">
      Vérifiez votre adresse mail pour pouvoir réserver.
      <button type="button" class="btn btn-2 btn-petit" @click="renvoyerLien">Renvoyer le lien</button>
    </AppAlerte>

    <section class="hero">
      <span class="forme f1" /><span class="forme f2" /><span class="forme f3" />
      <p v-if="compte" style="font-weight: 600; opacity: 0.9">Bonjour {{ compte.prenom }}</p>
      <h1>De quoi avez-vous besoin aujourd’hui ?</h1>
      <p>Des prestataires de confiance {{ ville ? `autour de ${ville.nom}` : 'près de chez vous' }}, avec leurs vrais avis.</p>
      <form class="recherche" @submit.prevent="chercher">
        <input v-model="texte" placeholder="Ex. plombier, ménage, cours de maths…" aria-label="Que cherchez-vous ?" />
        <button class="btn" type="submit"><AppIcone nom="trouver" />Chercher</button>
      </form>
      <div v-if="services.length" class="chips" style="margin-top: 14px">
        <button v-for="d in services" :key="d.id" type="button" class="chip" @click="routeur.push({ path: '/trouver', query: { dossier: String(d.id) } })">
          {{ d.nom }}
        </button>
      </div>
    </section>

    <section v-if="chiffres" class="section">
      <h2>Votre journée</h2>
      <ChiffresActivite :chiffres="chiffres" />
    </section>

    <section v-if="compte" class="section">
      <div class="section-titre">
        <h2>Prochain rendez-vous</h2>
        <RouterLink to="/mon-agenda" class="doux petit">Tout voir</RouterLink>
      </div>
      <RouterLink v-if="prochain" class="ligne" to="/mon-agenda">
        <span class="heure">{{ heureCourte(prochain.debut) }}</span>
        <div class="txt">
          <b>{{ prochain.titre }} {{ compte.prestataire_id ? 'chez' : 'avec' }} {{ prochain.autre.nom }}</b>
          <span>{{ jourLong(prochain.debut) }}<template v-if="villeDe(prochain.adresse)"> · {{ villeDe(prochain.adresse) }}</template></span>
        </div>
        <span class="fin"><AppBadge :etat="badgeRendezVous(prochain).etat">{{ badgeRendezVous(prochain).texte }}</AppBadge></span>
      </RouterLink>
      <div v-else class="carte vide">Aucun rendez-vous à venir.</div>
    </section>

    <section class="section">
      <div class="section-titre">
        <h2>Près de chez vous</h2>
        <RouterLink to="/trouver" class="doux petit">Tout voir</RouterLink>
      </div>
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <div v-else-if="proches.length" class="grille">
        <CarteResultat v-for="c in proches" :key="c.prestataire_id" :resultat="c" />
      </div>
      <div v-else class="carte vide">
        <template v-if="ville">Pas encore de prestataire autour de {{ ville.nom }}.</template>
        <template v-else>Indiquez votre ville dans <RouterLink to="/trouver">Trouver</RouterLink> pour voir les prestataires près de chez vous.</template>
      </div>
    </section>
  </div>
</template>
