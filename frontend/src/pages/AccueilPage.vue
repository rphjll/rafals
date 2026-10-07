<script setup lang="ts">
// Accueil (.doc/ihm/RM-ACCUEIL-IHM.md) : « Bonjour Julie », la barre et les bulles de services qui filtrent les
// demandes des clients listées dessous, et à droite la carte où l'on écrit sa propre demande.
// La recherche d'un prestataire est sur « Trouver un prestataire ».
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import dessinQuartier from '../assets/quartier.svg'
import CarteDemande from '../components/demandes/CarteDemande.vue'
import CartePublierDemande from '../components/demandes/CartePublierDemande.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBadge from '../components/ui/AppBadge.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppPicto from '../components/ui/AppPicto.vue'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'
import { useMetiers } from '../composables/useMetiers'
import type { DemandeVisible } from '../outils/demandes'
import { teinte } from '../outils/pictos'

const routeur = useRouter()
const { compte, renvoyerLienVerification } = useCompte()
const { afficherMessage } = useMessage()
const { dossiers, chargerDossiers } = useMetiers()
const etatServeur = ref('Vérification du serveur…')
const serveurOk = ref<boolean | null>(null)

const demandes = ref<DemandeVisible[]>([])
const chargementDemandes = ref(true)
const erreurDemandes = ref('')
const besoin = ref('')
// Bulle choisie : un dossier de métiers (« Jardin & extérieur »), ou null pour « Tout »
const dossierChoisi = ref<number | null>(null)
// Seuls les dossiers qui ont au moins une demande ont une bulle : aucune bulle ne mène à une liste vide
const bulles = computed(() =>
  dossiers.value
    .map((dossier, rang) => ({ id: dossier.id, code: dossier.code, nom: dossier.nom, teinte: teinte(rang), ids: new Set(dossier.metiers.map((m) => m.id)) }))
    .filter((dossier) => demandes.value.some((d) => dossier.ids.has(d.metier_id))),
)
const bullesAvecTout = computed(() => [{ id: null as number | null, code: 'tout', nom: 'Tout', teinte: teinte(2) }, ...bulles.value])
// La liste ne garde que les demandes du dossier choisi qui contiennent le texte tapé (titre, description, métier ou ville)
const demandesFiltrees = computed(() => {
  const mot = besoin.value.trim().toLowerCase()
  const ids = bulles.value.find((b) => b.id === dossierChoisi.value)?.ids
  return demandes.value.filter(
    (d) => (!ids || ids.has(d.metier_id)) && (!mot || `${d.titre} ${d.description} ${d.metier} ${d.ville}`.toLowerCase().includes(mot)),
  )
})
const texteListeVide = computed(() => {
  if (besoin.value.trim()) return `Aucune demande ne contient « ${besoin.value.trim()} ».`
  return dossierChoisi.value ? 'Aucune demande dans ce type de service.' : 'Aucune demande pour l’instant.'
})

async function chargerDemandes() {
  try {
    demandes.value = await appelerServeur<DemandeVisible[]>('/api/demandes')
    erreurDemandes.value = ''
  } catch (e) {
    erreurDemandes.value = messageErreur(e)
  } finally {
    chargementDemandes.value = false
  }
}

const ETAPES = [
  { titre: 'Publiez votre demande', texte: 'Décrivez votre besoin et indiquez votre ville. C’est gratuit.', teinte: teinte(1) },
  { titre: 'Recevez des propositions', texte: 'Les prestataires proches vous proposent un prix, un jour et une heure. Vous acceptez, refusez ou négociez.', teinte: teinte(2) },
  { titre: 'Payez et donnez votre avis', texte: 'Par carte ou en espèces. La facture arrive dans votre compte.', teinte: teinte(0) },
]
const ATOUTS = [
  'Les demandes des clients près de chez vous arrivent toutes seules',
  'Devis et factures prêts en un clic',
  'Un rappel avant chaque déclaration à l’URSSAF',
]

onMounted(async () => {
  chargerDemandes()
  chargerDossiers().catch(() => {}) // sans les dossiers, pas de bulles : la barre suffit
  try {
    etatServeur.value = (await appelerServeur<{ message: string }>('/api/etat')).message
    serveurOk.value = true
  } catch {
    etatServeur.value = 'Le serveur ne répond pas. Relance demarrer.bat.'
    serveurOk.value = false
  }
})

async function renvoyerLien() {
  try {
    afficherMessage(await renvoyerLienVerification(compte.value?.email ?? ''))
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}
</script>

<template>
  <div class="flex flex-col gap-10">
    <AppAlerte v-if="compte && !compte.email_verifie" etat="attente">
      Vérifiez votre adresse mail pour pouvoir réserver.
      <AppBouton variante="secondaire" @click="renvoyerLien">Renvoyer le lien</AppBouton>
    </AppAlerte>

    <!-- Le bonjour et la barre à gauche, le dessin de la rue à droite (caché sur téléphone), puis les bulles -->
    <div class="flex flex-col gap-4">
      <section class="grid items-center gap-6 md:grid-cols-[1.1fr_0.9fr]">
        <div class="flex min-w-0 flex-col gap-4">
          <h1 class="text-[clamp(32px,5.4vw,56px)] leading-[1.05] font-black">
            Bonjour<template v-if="compte"> {{ compte.prenom }}</template> !
            <span class="text-primaire">{{ compte?.prestataire_id ? 'Qui pouvez-vous aider ?' : 'De quoi avez-vous besoin ?' }}</span>
          </h1>
          <p class="max-w-[42ch] text-[18px] text-texte-doux">
            Un voisin ou un professionnel du quartier s'en occupe, souvent dès cette semaine.
          </p>
          <label class="flex max-w-[520px] items-center gap-3 rounded-bouton border border-bord-carte bg-surface py-1.5 shadow-carte pr-1.5 pl-5 focus-within:ring-2 focus-within:ring-primaire">
            <span class="sr-only">Chercher dans les demandes</span>
            <input
              v-model="besoin"
              type="search"
              maxlength="80"
              placeholder="ex. pelouse, ménage, robinet, Pessac…"
              class="min-h-[46px] min-w-0 flex-1 bg-transparent text-texte outline-none"
            />
            <span class="grid size-[46px] shrink-0 place-items-center rounded-full bg-accent-vif text-accent-vif-texte" aria-hidden="true">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">
                <circle cx="11" cy="11" r="7" />
                <path d="M20 20l-3.5-3.5" />
              </svg>
            </span>
          </label>
          <div v-if="!compte"><AppBouton variante="secondaire" @click="routeur.push('/inscription')">Créer mon compte</AppBouton></div>
        </div>
        <img :src="dessinQuartier" alt="" class="hidden w-full max-w-[440px] justify-self-center md:block" />
      </section>

      <div v-if="bulles.length" class="flex gap-5 overflow-x-auto px-1 pt-2 pb-3" role="group" aria-label="Types de service">
        <button
          v-for="bulle in bullesAvecTout"
          :key="bulle.id ?? 0"
          type="button"
          class="flex w-[84px] shrink-0 flex-col items-center gap-2 text-center text-[13.5px] leading-tight font-bold"
          :aria-pressed="dossierChoisi === bulle.id"
          @click="dossierChoisi = bulle.id"
        >
          <span
            class="grid size-[72px] place-items-center rounded-full ring-offset-4 ring-offset-fond"
            :class="[bulle.teinte, dossierChoisi === bulle.id ? 'ring-[3px] ring-primaire' : '']"
          >
            <AppPicto :code="bulle.code" />
          </span>
          {{ bulle.nom }}
        </button>
      </div>
    </div>

    <!-- Ordinateur : la liste à gauche, la carte « Publier » à droite. Téléphone : la carte, puis la liste. -->
    <div class="grid items-start gap-8 md:grid-cols-[1fr_380px]">
      <section class="order-2 flex min-w-0 flex-col gap-4 md:order-1">
        <div class="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1">
          <h2 class="text-[26px] font-extrabold">Les demandes des clients</h2>
          <span v-if="!chargementDemandes && !erreurDemandes" class="text-[13.5px] text-texte-doux">
            {{ demandesFiltrees.length }} demande{{ demandesFiltrees.length > 1 ? 's' : '' }}
          </span>
        </div>
        <AppAlerte v-if="erreurDemandes">{{ erreurDemandes }}</AppAlerte>
        <ul v-else-if="demandesFiltrees.length" class="flex flex-col gap-4">
          <li v-for="demande in demandesFiltrees" :key="demande.id"><CarteDemande :demande="demande" /></li>
        </ul>
        <p v-else-if="!chargementDemandes" class="rounded-carte border-2 border-dashed border-bord p-5 text-texte-doux">{{ texteListeVide }}</p>
      </section>

      <CartePublierDemande class="order-1 md:order-2" @publiee="chargerDemandes" />
    </div>

    <section class="flex flex-col gap-4">
      <h2 class="text-[26px] font-extrabold">Comment ça marche</h2>
      <ol class="grid gap-4 md:grid-cols-3">
        <li v-for="(etape, rang) in ETAPES" :key="etape.titre" class="carte flex flex-col gap-2 p-5">
          <span class="flex size-11 items-center justify-center rounded-full text-lg font-black" :class="etape.teinte" aria-hidden="true">
            {{ rang + 1 }}
          </span>
          <b class="text-[17px]">{{ etape.titre }}</b>
          <span class="text-texte-doux">{{ etape.texte }}</span>
        </li>
      </ol>
    </section>

    <section
      v-if="!compte?.prestataire_id"
      class="flex flex-wrap items-center gap-6 rounded-carte bg-accent-vif p-6 text-accent-vif-texte md:p-10"
    >
      <div class="flex min-w-0 flex-[999_1_380px] flex-col gap-4">
        <h2 class="text-[clamp(24px,4vw,32px)] leading-tight font-extrabold">Vous proposez vos services ?</h2>
        <p class="max-w-[48ch] text-[17px]">
          rafals vous aide à créer votre auto-entreprise, puis s'occupe de l'agenda, des devis et des factures.
        </p>
        <div class="flex flex-wrap gap-3">
          <AppBouton @click="routeur.push('/proposer')">Proposer mes services</AppBouton>
          <AppBouton variante="secondaire" @click="routeur.push('/creer-mon-auto-entreprise')">Créer mon auto-entreprise</AppBouton>
        </div>
      </div>
      <ul class="flex flex-[1_1_260px] flex-col gap-2.5 font-semibold">
        <li v-for="atout in ATOUTS" :key="atout" class="flex gap-2.5"><span aria-hidden="true">✓</span>{{ atout }}</li>
      </ul>
    </section>

    <!-- Pour le développement : état du serveur et catalogue des composants -->
    <div class="flex flex-wrap items-center gap-3 border-t border-bord pt-4">
      <AppBadge :etat="serveurOk === null ? 'neutre' : serveurOk ? 'ok' : 'erreur'">{{ etatServeur }}</AppBadge>
      <AppBouton variante="secondaire" @click="routeur.push('/catalogue')">Voir le catalogue des composants</AppBouton>
    </div>
  </div>
</template>
