<script setup lang="ts">
// Accueil (.doc/ihm/RM-ACCUEIL-IHM.md) : recherche métier + ville, dossiers de métiers en tuiles de couleur.
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import AppChoixCommune from '../components/AppChoixCommune.vue'
import AppChoixMetier from '../components/AppChoixMetier.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBadge from '../components/ui/AppBadge.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'
import { type Dossier, type MetierVisible, useMetiers } from '../composables/useMetiers'
import type { CommuneVisible } from '../outils/prestataires'

const routeur = useRouter()
const { compte, renvoyerLienVerification } = useCompte()
const { afficherMessage } = useMessage()
const { dossiers, chargerDossiers } = useMetiers()
const etatServeur = ref('Vérification du serveur…')
const serveurOk = ref<boolean | null>(null)

const metier = ref<MetierVisible | null>(null)
const commune = ref<CommuneVisible | null>(null)
const erreur = ref('')
const dossierOuvert = ref<Dossier | null>(null)

// Une couleur par tuile, dans l'ordre, puis on recommence (noms écrits en entier pour Tailwind)
const TEINTES = [
  'bg-teinte-orange text-teinte-orange-texte',
  'bg-teinte-vert text-teinte-vert-texte',
  'bg-teinte-jaune text-teinte-jaune-texte',
  'bg-teinte-bleu text-teinte-bleu-texte',
  'bg-teinte-rose text-teinte-rose-texte',
  'bg-teinte-violet text-teinte-violet-texte',
]
const ETAPES = [
  { titre: 'Cherchez', texte: 'Indiquez un service et votre ville. Vous voyez les prestataires proches, leurs prix et leurs avis.' },
  { titre: 'Réservez', texte: 'Choisissez un créneau libre dans son agenda, ou demandez un devis si le travail est à chiffrer.' },
  { titre: 'Payez et donnez votre avis', texte: 'Par carte ou en espèces. La facture arrive dans votre compte.' },
]
const ATOUTS = [
  'Vos clients réservent directement dans votre agenda',
  'Devis et factures prêts en un clic',
  'Un rappel avant chaque déclaration à l’URSSAF',
]

onMounted(async () => {
  chargerDossiers().catch(() => {}) // sans les dossiers, la recherche du haut suffit
  try {
    etatServeur.value = (await appelerServeur<{ message: string }>('/api/etat')).message
    serveurOk.value = true
  } catch {
    etatServeur.value = 'Le serveur ne répond pas. Relance demarrer.bat.'
    serveurOk.value = false
  }
})

function chercher() {
  erreur.value = ''
  if (!metier.value || !commune.value) {
    erreur.value = !metier.value ? 'Choisissez un métier.' : 'Choisissez votre ville.'
    return
  }
  routeur.push({ path: '/trouver', query: { metier: String(metier.value.id), ville: String(commune.value.id) } })
}

// Métier choisi dans une tuile : la recherche part si la ville est connue, sinon on remonte la demander
function choisirMetier(choix: MetierVisible) {
  metier.value = choix
  dossierOuvert.value = null
  if (commune.value) return chercher()
  erreur.value = ''
  window.scrollTo({ top: 0, behavior: 'smooth' })
  afficherMessage(`« ${choix.nom} » choisi : indiquez votre ville.`)
}

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

    <section class="flex flex-col gap-6 rounded-rafals bg-fonce px-5 py-8 text-sur-fonce md:px-12 md:py-14">
      <h1 class="max-w-[16ch] text-[clamp(32px,6vw,54px)] leading-[1.05] font-bold">
        Le bon prestataire, <span class="text-fonce-vif">près de chez vous.</span>
      </h1>
      <p class="max-w-[50ch] text-[17px] text-sur-fonce-doux">
        Ménage, jardinage, plomberie, coiffure à domicile : réservez un créneau en quelques clics, ou demandez un devis.
      </p>
      <form
        class="grid items-end gap-3 rounded-rafals bg-surface p-4 text-texte md:grid-cols-[1fr_1fr_auto]"
        @submit.prevent="chercher"
      >
        <AppChoixMetier v-model="metier" :avec-dossiers="false" etiquette="Quel service ?" />
        <AppChoixCommune v-model="commune" etiquette="Où ?" />
        <AppBouton type="submit" variante="accent">Rechercher</AppBouton>
        <AppAlerte v-if="erreur" class="md:col-span-3">{{ erreur }}</AppAlerte>
      </form>
      <div v-if="!compte">
        <AppBouton variante="secondaire" @click="routeur.push('/inscription')">Créer mon compte</AppBouton>
      </div>
    </section>

    <section v-if="dossiers.length" class="flex flex-col gap-4">
      <h2 class="text-[26px] font-bold">De quoi avez-vous besoin ?</h2>
      <template v-if="dossierOuvert">
        <div class="flex flex-wrap items-center gap-2.5">
          <AppBouton variante="secondaire" @click="dossierOuvert = null">← Tous les dossiers</AppBouton>
          <h3 class="text-lg font-bold">{{ dossierOuvert.nom }}</h3>
        </div>
        <div class="flex flex-wrap gap-2">
          <AppBouton v-for="choix in dossierOuvert.metiers" :key="choix.id" variante="secondaire" @click="choisirMetier(choix)">
            {{ choix.nom }}
          </AppBouton>
        </div>
      </template>
      <div v-else class="grid grid-cols-[repeat(auto-fill,minmax(210px,1fr))] gap-3">
        <button
          v-for="(dossier, rang) in dossiers"
          :key="dossier.id"
          type="button"
          class="flex min-h-[104px] flex-col justify-between gap-2 rounded-rafals p-4 text-left hover:brightness-95"
          :class="TEINTES[rang % TEINTES.length]"
          @click="dossierOuvert = dossier"
        >
          <b class="font-titre text-lg leading-tight">{{ dossier.nom }}</b>
          <small class="text-[13px]">{{ dossier.metiers.slice(0, 3).map((m) => m.nom).join(', ') }}…</small>
        </button>
      </div>
    </section>

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
