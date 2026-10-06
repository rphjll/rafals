<script setup lang="ts">
// Accueil (.doc/ihm/RM-ACCUEIL-IHM.md) : « Bonjour Julie », la barre « De quoi avez-vous besoin ? » qui filtre les
// demandes des clients listées dessous, et à droite, sur toute la hauteur, la carte où l'on écrit sa propre demande.
// La recherche d'un prestataire est sur « Trouver un prestataire ».
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import CartePublierDemande from '../components/demandes/CartePublierDemande.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBadge from '../components/ui/AppBadge.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppChamp from '../components/ui/AppChamp.vue'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'
import { type DemandeVisible, texteBudget, texteQuand } from '../outils/demandes'

const routeur = useRouter()
const { compte, renvoyerLienVerification } = useCompte()
const { afficherMessage } = useMessage()
const etatServeur = ref('Vérification du serveur…')
const serveurOk = ref<boolean | null>(null)

const demandes = ref<DemandeVisible[]>([])
const chargementDemandes = ref(true)
const erreurDemandes = ref('')
const besoin = ref('')
// La barre ne garde que les demandes qui contiennent le texte tapé (titre, description, métier ou ville)
const demandesFiltrees = computed(() => {
  const mot = besoin.value.trim().toLowerCase()
  if (!mot) return demandes.value
  return demandes.value.filter((d) => `${d.titre} ${d.description} ${d.metier} ${d.ville}`.toLowerCase().includes(mot))
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
  { titre: 'Publiez votre demande', texte: 'Décrivez votre besoin et indiquez votre ville. C’est gratuit.' },
  { titre: 'Recevez des propositions', texte: 'Les prestataires proches vous proposent un prix, un jour et une heure. Vous acceptez, refusez ou négociez.' },
  { titre: 'Payez et donnez votre avis', texte: 'Par carte ou en espèces. La facture arrive dans votre compte.' },
]
const ATOUTS = [
  'Les demandes des clients près de chez vous arrivent toutes seules',
  'Devis et factures prêts en un clic',
  'Un rappel avant chaque déclaration à l’URSSAF',
]

onMounted(async () => {
  chargerDemandes()
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

    <!-- Ordinateur : à gauche le bonjour, la barre et la liste ; à droite la carte « Publier », de haut en bas.
         Téléphone : le bonjour et la barre, la carte, puis la liste. -->
    <div class="grid gap-6 md:grid-cols-[1fr_380px] md:grid-rows-[auto_1fr]">
      <section class="flex flex-col gap-5">
        <h1 class="text-[clamp(30px,5vw,44px)] leading-tight font-bold">
          Bonjour<template v-if="compte"> {{ compte.prenom }}</template> !
        </h1>
        <AppChamp v-model="besoin" etiquette="Chercher dans les demandes" type="search" placeholder="De quoi avez-vous besoin ?" maxlength="80" />
        <div v-if="!compte"><AppBouton variante="secondaire" @click="routeur.push('/inscription')">Créer mon compte</AppBouton></div>
      </section>

      <!-- La carte occupe les deux lignes de la colonne de droite, et au moins la hauteur de l'écran sous l'en-tête -->
      <CartePublierDemande class="md:col-start-2 md:row-span-2 md:row-start-1 md:min-h-[calc(100vh-150px)]" @publiee="chargerDemandes" />

      <section class="flex flex-col gap-4">
        <h2 class="text-[26px] font-bold">Les demandes des clients</h2>
        <AppAlerte v-if="erreurDemandes">{{ erreurDemandes }}</AppAlerte>
        <ul v-else-if="demandesFiltrees.length" class="flex flex-col gap-3">
          <li v-for="demande in demandesFiltrees" :key="demande.id" class="flex flex-col gap-2 rounded-rafals border border-bord bg-surface p-5">
            <div class="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1">
              <b class="text-[17px]">{{ demande.titre }}</b>
              <b v-if="demande.budget_centimes" class="font-titre text-lg text-primaire">{{ texteBudget(demande.budget_centimes) }}</b>
            </div>
            <div class="flex flex-wrap gap-1.5">
              <AppBadge etat="neutre">{{ demande.metier }}</AppBadge>
              <AppBadge etat="neutre">{{ demande.ville }}</AppBadge>
              <AppBadge etat="neutre">{{ texteQuand(demande) }}</AppBadge>
              <AppBadge etat="neutre">{{ demande.lieu === 'chez_moi' ? 'Chez le client' : 'Chez le prestataire' }}</AppBadge>
              <AppBadge v-if="demande.a_moi" etat="ok">Ma demande</AppBadge>
            </div>
            <p class="whitespace-pre-line text-texte-doux">{{ demande.description }}</p>
            <!-- Les photos demandent d'être connecté : elles montrent souvent l'intérieur d'un logement -->
            <div v-if="demande.nombre_photos && compte" class="flex flex-wrap gap-2">
              <a v-for="n in demande.nombre_photos" :key="n" :href="`/api/demandes/${demande.id}/photos/${n}`" target="_blank" rel="noopener">
                <img :src="`/api/demandes/${demande.id}/photos/${n}`" :alt="`Photo ${n} de la demande « ${demande.titre} »`" class="size-24 rounded-rafals border border-bord object-cover" />
              </a>
            </div>
            <span class="text-[13px] text-texte-doux">
              {{ demande.client }}<template v-if="demande.nombre_photos && !compte">
                · {{ demande.nombre_photos }} photo{{ demande.nombre_photos > 1 ? 's' : '' }} (connectez-vous pour les voir)</template>
            </span>
          </li>
        </ul>
        <p v-else-if="!chargementDemandes" class="rounded-rafals border border-bord bg-surface p-5 text-texte-doux">
          {{ besoin.trim() ? `Aucune demande ne contient « ${besoin.trim()} ».` : 'Aucune demande pour l’instant.' }}
        </p>
      </section>
    </div>

    <section class="flex flex-col gap-4">
      <h2 class="text-[26px] font-bold">Comment ça marche</h2>
      <ol class="grid gap-3 md:grid-cols-3">
        <li v-for="(etape, rang) in ETAPES" :key="etape.titre" class="flex flex-col gap-2 rounded-rafals border border-bord bg-surface p-5">
          <span
            class="flex h-10 w-10 items-center justify-center rounded-full bg-primaire font-titre text-lg font-bold text-primaire-texte"
            aria-hidden="true"
          >
            {{ rang + 1 }}
          </span>
          <b class="text-[17px]">{{ etape.titre }}</b>
          <span class="text-texte-doux">{{ etape.texte }}</span>
        </li>
      </ol>
    </section>

    <section
      v-if="!compte?.prestataire_id"
      class="flex flex-wrap items-center gap-6 rounded-rafals bg-accent-vif p-6 text-accent-vif-texte md:p-10"
    >
      <div class="flex min-w-0 flex-[999_1_380px] flex-col gap-4">
        <h2 class="text-[clamp(24px,4vw,32px)] leading-tight font-bold">Vous proposez vos services ?</h2>
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
