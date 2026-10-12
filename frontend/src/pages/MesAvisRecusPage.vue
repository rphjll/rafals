<script setup lang="ts">
// Mes avis reçus (.doc/ihm/RM-AVIS-CLIENTS-IHM.md ; RM-AVIS.md § « Notation dans les deux sens ») : les avis que des
// prestataires m'ont laissés comme client. Je peux répondre une fois à chacun et le signaler à l'administrateur.
// Ouvrir la page remet son compteur rouge à zéro.
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import FenetreTexte, { type DemandeTexte } from '../components/FenetreTexte.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBadge from '../components/ui/AppBadge.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import { useCompte } from '../composables/useCompte'
import { type AvisClientRecu, etoiles } from '../outils/avis'

const routeur = useRouter()
const { compte, chargementFait } = useCompte()
const avis = ref<AvisClientRecu[] | null>(null)
const erreur = ref('')
const fenetre = ref<DemandeTexte | null>(null)

async function charger() {
  if (!compte.value) return
  try {
    avis.value = await appelerServeur<AvisClientRecu[]>('/api/moi/avis-recus')
    erreur.value = ''
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
onMounted(charger)
watch(compte, charger)

function repondre(a: AvisClientRecu) {
  fenetre.value = {
    titre: `Répondre à ${a.auteur}`,
    explication: 'Votre réponse est affichée sous l’avis, sur votre page publique. Une seule réponse par avis.',
    etiquette: 'Votre réponse',
    aide: 'ex. « J’étais au téléphone, désolée pour l’attente. »',
    chemin: `/api/moi/avis-recus/${a.id}/repondre`,
    cle: 'texte',
    bouton: 'Publier ma réponse',
    reussite: 'Réponse publiée.',
  }
}
function signaler(a: AvisClientRecu) {
  fenetre.value = {
    titre: 'Signaler cet avis',
    explication: 'L’administrateur de rafals le regarde : il le laisse, ou il le cache. L’avis reste affiché en attendant.',
    etiquette: 'Pourquoi ?',
    aide: 'ex. « Fausse accusation », « Ce n’était pas moi ».',
    chemin: `/api/moi/avis-recus/${a.id}/signaler`,
    cle: 'texte',
    bouton: 'Signaler',
    danger: true,
    reussite: 'Avis signalé : l’administrateur va le regarder.',
  }
}
</script>

<template>
  <div class="mx-auto flex max-w-[760px] flex-col gap-5">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <h1 class="text-[clamp(28px,4.5vw,40px)] font-black">Mes avis reçus</h1>
      <AppBouton v-if="compte" variante="secondaire" @click="routeur.push(`/clients/${compte.id}/avis`)">Voir ma page publique</AppBouton>
    </div>
    <p class="text-texte-doux">
      Après un rendez-vous, le prestataire peut vous noter, comme vous le notez. Ces avis sont visibles de tous, avec votre prénom et l'initiale de votre nom.
    </p>
    <template v-if="chargementFait && !compte">
      <AppAlerte etat="neutre">Connectez-vous pour voir vos avis reçus.</AppAlerte>
      <div><AppBouton @click="routeur.push('/connexion')">Se connecter</AppBouton></div>
    </template>
    <AppAlerte v-else-if="erreur">{{ erreur }}</AppAlerte>
    <ul v-else-if="avis?.length" class="flex flex-col gap-4">
      <li v-for="a in avis" :key="a.id" class="carte flex flex-col gap-2 p-5">
        <div class="flex flex-wrap items-center gap-2">
          <b class="text-accent" :aria-label="`${a.note} sur 5`">{{ etoiles(a.note) }}</b>
          <span class="text-[14px] text-texte-doux">{{ a.auteur }} · {{ a.mois }} · « {{ a.titre }} »</span>
          <AppBadge v-if="a.cache_motif" etat="neutre">caché par l'administrateur</AppBadge>
          <AppBadge v-else-if="a.signale" etat="attente">signalé</AppBadge>
        </div>
        <p class="whitespace-pre-line">{{ a.texte }}</p>
        <p v-if="a.cache_motif" class="text-[14px] text-texte-doux">Cet avis n'est plus affiché ni compté. Motif : « {{ a.cache_motif }} ».</p>
        <p v-if="a.reponse" class="rounded-rafals bg-fond px-3 py-2 text-[14px]"><b>Votre réponse :</b> {{ a.reponse }}</p>
        <div v-if="!a.cache_motif" class="flex flex-wrap gap-2">
          <AppBouton v-if="!a.reponse" variante="secondaire" @click="repondre(a)">Répondre…</AppBouton>
          <AppBouton v-if="!a.signale" variante="danger" @click="signaler(a)">Signaler…</AppBouton>
        </div>
      </li>
    </ul>
    <p v-else-if="avis" class="rounded-carte border-2 border-dashed border-bord p-5 text-texte-doux">Aucun avis pour l'instant.</p>
    <FenetreTexte :demande="fenetre" @fermer="fenetre = null" @fait="(fenetre = null), charger()" />
  </div>
</template>
