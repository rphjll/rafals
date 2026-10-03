<script setup lang="ts">
// Créer mon auto-entreprise (.doc/ihm/RM-CREATION-AUTO-ENTREPRISE-IHM.md ; RM-CREATION-AUTO-ENTREPRISE.md, lot 6.2) :
// un guide en 5 étapes, ouvert à tous. rafals explique et donne les liens officiels ; il ne fait pas la démarche.
// L'avancement (cases « C'est fait ») est gardé sur l'appareil, pas sur rafals.
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppCase from '../components/ui/AppCase.vue'
import AppSection from '../components/ui/AppSection.vue'

const routeur = useRouter()
const CLE = 'rafals-guide-auto-entreprise'

interface Etape {
  titre: string
  texte: string
  /** Bouton facultatif : un site officiel (nouvel onglet) ou une page de rafals */
  bouton?: { texte: string; adresse?: string; page?: string }
}
const etapes: Etape[] = [
  {
    titre: 'Est-ce pour moi ?',
    texte:
      "Il faut avoir 18 ans (à 16 ou 17 ans : seulement avec l'accord des parents, sous conditions). Certains métiers demandent un diplôme ou 3 ans d'expérience (coiffeur, plombier, électricien, maçon…) et une assurance.",
  },
  {
    titre: 'Je prépare mes papiers',
    texte: "Une pièce d'identité, un justificatif de domicile, et selon le métier : votre diplôme ou la preuve de votre expérience.",
  },
  {
    titre: 'Je déclare mon activité',
    texte: "Sur le guichet unique de l'État : choisissez « micro-entrepreneur ». C'est gratuit, comptez 30 minutes.",
    bouton: { texte: 'Ouvrir le guichet unique', adresse: 'https://formalites.entreprises.gouv.fr' },
  },
  {
    titre: "J'attends mon SIRET",
    texte: "L'INSEE vous l'envoie en 1 à 4 semaines. En attendant, vous pouvez déjà proposer vos services sur rafals, payés en espèces.",
  },
  {
    titre: 'Je termine sur rafals',
    texte:
      "Ajoutez votre SIRET dans « Mon activité » (il est vérifié tout seul), créez votre espace sur le site de l'URSSAF, puis activez le paiement par carte.",
    bouton: { texte: 'Proposer mes services', page: '/proposer' },
  },
]

// L'avancement : gardé dans le navigateur ; si le navigateur le refuse (navigation privée), le guide marche quand même
function lire(): boolean[] {
  try {
    const garde = JSON.parse(localStorage.getItem(CLE) ?? '[]')
    return etapes.map((_, rang) => garde[rang] === true)
  } catch {
    return etapes.map(() => false)
  }
}
const faites = ref<boolean[]>(lire())
watch(
  faites,
  (valeur) => {
    try {
      localStorage.setItem(CLE, JSON.stringify(valeur))
    } catch {
      // rien : l'avancement ne sera simplement pas gardé
    }
  },
  { deep: true },
)
const nombre = computed(() => faites.value.filter(Boolean).length)

function suivre(bouton: NonNullable<Etape['bouton']>) {
  if (bouton.page) routeur.push(bouton.page)
  else window.open(bouton.adresse, '_blank', 'noopener')
}
</script>

<template>
  <div class="mx-auto flex w-full max-w-[720px] flex-col gap-4">
    <h1 class="text-[28px] font-bold">Créer mon auto-entreprise</h1>
    <p class="text-texte-doux">
      rafals vous guide en 5 étapes ; la déclaration se fait sur le site officiel de l'État, gratuitement.
    </p>
    <AppAlerte v-if="nombre" etat="ok">
      {{ nombre === etapes.length ? 'Les 5 étapes sont faites : bravo !' : `${nombre} étape${nombre > 1 ? 's' : ''} sur ${etapes.length} faite${nombre > 1 ? 's' : ''}.` }}
    </AppAlerte>
    <AppSection v-for="(etape, rang) in etapes" :key="rang" :titre="`${rang + 1}. ${etape.titre}`">
      <template #action><AppCase v-model="faites[rang]" texte="C'est fait" /></template>
      <p>{{ etape.texte }}</p>
      <div v-if="etape.bouton">
        <AppBouton variante="secondaire" @click="suivre(etape.bouton)">{{ etape.bouton.texte }}</AppBouton>
      </div>
    </AppSection>
    <p class="text-[13.5px] text-texte-doux">
      L'avancement est gardé sur cet appareil seulement. Besoin d'un conseil sur le statut ? Voyez la CCI ou la chambre des
      métiers (gratuit). Ces explications sont une aide, pas un conseil juridique.
    </p>
  </div>
</template>
