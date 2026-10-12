<script setup lang="ts">
// Mon activité (.doc/ihm/RM-MON-ACTIVITE-IHM.md) : toutes les fonctions de rafals au même endroit, en tuiles rangées
// par groupe. Un prestataire en voit plus qu'un client. Une fonction pas encore construite a une tuile « bientôt ».
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur } from '../api'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBadge from '../components/ui/AppBadge.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppPicto from '../components/ui/AppPicto.vue'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'
import { type ActiviteChiffree, type FonctionActivite, GROUPES_ACTIVITE, adresseDe, chiffresAffiches, fonctionsPour } from '../outils/activite'
import { montant } from '../outils/paiements'
import { teinte } from '../outils/pictos'

const routeur = useRouter()
const { compte, chargementFait } = useCompte()
const { afficherMessage } = useMessage()

const prestataireId = computed(() => compte.value?.prestataire_id ?? null)
// Les groupes qui ont au moins une tuile pour ce compte ; une couleur par tuile, dans l'ordre de la page
const groupes = computed(() => {
  let rang = 0
  return GROUPES_ACTIVITE.map((groupe) => ({
    cle: groupe.cle,
    titre: prestataireId.value === null ? (groupe.titreClient ?? groupe.titre) : groupe.titre,
    tuiles: fonctionsPour(prestataireId.value)
      .filter((f) => f.groupe === groupe.cle)
      .map((f) => ({ fonction: f, adresse: adresseDe(f, prestataireId.value), teinte: teinte(rang++) })),
  })).filter((groupe) => groupe.tuiles.length)
})

// Les chiffres du haut (RM-MON-ACTIVITE.md) : relus à chaque ouverture de la page ; sans eux, la page reste utilisable
const chiffres = ref<ActiviteChiffree | null>(null)
const pastilles = ref<Record<string, number>>({})
const affiches = computed(() =>
  chiffres.value ? chiffresAffiches(chiffres.value, montant, new Date().toLocaleDateString('fr-FR', { month: 'long', timeZone: 'Europe/Paris' })) : [],
)
// La barre de la TVA : seulement pour un prestataire qui ne la facture pas
const tva = computed(() => {
  const p = chiffres.value?.prestataire
  if (!p || p.seuil_tva_centimes === null || p.reste_avant_seuil_centimes === null) return null
  return {
    annee: p.annee,
    encaisse: montant(p.encaisse_annee_centimes),
    seuil: montant(p.seuil_tva_centimes),
    reste: montant(p.reste_avant_seuil_centimes),
    depasse: p.encaisse_annee_centimes > p.seuil_tva_centimes,
    pourcent: Math.min(100, Math.round((p.encaisse_annee_centimes / p.seuil_tva_centimes) * 100)),
  }
})
watch(
  compte,
  async (connecte) => {
    chiffres.value = null
    if (!connecte) return
    try {
      chiffres.value = await appelerServeur<ActiviteChiffree>('/api/moi/activite')
    } catch {
      // serveur injoignable : les tuiles suffisent
    }
    // Pastilles rouges (RM-ALERTES) : nouvelles demandes près de chez moi, nouveaux avis reçus
    const nombre = (chemin: string) => appelerServeur<{ nombre: number }>(chemin).then((r) => r.nombre).catch(() => 0)
    pastilles.value = {
      'demandes-pres': connecte.prestataire_id ? await nombre('/api/moi/prestataire/demandes/nouvelles') : 0,
      'mes-avis-recus': await nombre('/api/moi/avis-recus/non-vus'),
    }
  },
  { immediate: true },
)

function ouvrir(fonction: FonctionActivite, adresse: string | null) {
  if (adresse) routeur.push(adresse)
  else afficherMessage(`« ${fonction.texte} » n'est pas encore disponible : bientôt.`)
}
</script>

<template>
  <div class="flex flex-col gap-8">
    <div class="flex flex-col gap-2">
      <h1 class="text-[clamp(30px,5vw,48px)] leading-tight font-black">Mon activité</h1>
      <p class="text-[17px] text-texte-doux">Tout ce que vous faites sur rafals, au même endroit.</p>
    </div>

    <template v-if="chargementFait && !compte">
      <AppAlerte etat="neutre">Connectez-vous pour voir votre activité.</AppAlerte>
      <div><AppBouton @click="routeur.push({ path: '/connexion', query: { retour: '/mon-activite' } })">Se connecter</AppBouton></div>
    </template>

    <template v-else-if="compte">
      <!-- Les chiffres : un clic ouvre la page qui les détaille -->
      <div v-if="affiches.length" class="grid grid-cols-2 gap-3 md:grid-cols-[repeat(auto-fit,minmax(200px,1fr))] md:gap-4">
        <RouterLink
          v-for="chiffre in affiches"
          :key="chiffre.texte"
          :to="chiffre.vers"
          class="carte flex min-w-0 flex-col gap-0.5 p-4 hover:ring-2 hover:ring-primaire md:p-5"
        >
          <b class="text-[clamp(24px,4vw,32px)] leading-tight font-black tabular-nums">{{ chiffre.valeur }}</b>
          <span class="text-[14px] text-texte-doux">{{ chiffre.texte }}</span>
        </RouterLink>
      </div>

      <!-- Encaissé dans l'année et barre de la TVA -->
      <section v-if="chiffres?.prestataire" class="carte flex flex-col gap-3 p-5">
        <div class="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
          <h2 class="text-[19px] font-extrabold">Encaissé en {{ chiffres.prestataire.annee }}</h2>
          <b class="text-[26px] font-black tabular-nums">{{ montant(chiffres.prestataire.encaisse_annee_centimes) }}</b>
        </div>
        <template v-if="tva">
          <div
            class="h-3 overflow-hidden rounded-full bg-fond"
            role="progressbar"
            :aria-valuenow="tva.pourcent"
            aria-valuemin="0"
            aria-valuemax="100"
            :aria-label="`Part du seuil de TVA atteinte : ${tva.pourcent} %`"
          >
            <div class="h-full rounded-full" :class="tva.depasse ? 'bg-attente' : 'bg-primaire'" :style="{ width: `${tva.pourcent}%` }" />
          </div>
          <p v-if="tva.depasse" class="font-semibold text-attente">
            Vous avez dépassé le seuil de TVA ({{ tva.seuil }}) : parlez-en à votre comptable ou à votre service des impôts.
          </p>
          <p v-else class="text-texte-doux">Il vous reste <b class="text-texte">{{ tva.reste }}</b> avant le seuil de TVA ({{ tva.seuil }}).</p>
        </template>
        <p class="text-[13px] text-texte-doux">
          Seulement ce qui est passé par rafals : ajoutez vous-même ce que vous avez encaissé ailleurs.
        </p>
      </section>

      <section v-for="groupe in groupes" :key="groupe.cle" class="flex flex-col gap-4">
        <h2 class="text-[24px] font-extrabold">{{ groupe.titre }}</h2>
        <div class="grid grid-cols-[repeat(auto-fill,minmax(250px,1fr))] gap-4">
          <button
            v-for="tuile in groupe.tuiles"
            :key="tuile.fonction.cle"
            type="button"
            class="flex min-w-0 items-center gap-3.5 p-4 text-left"
            :class="tuile.adresse ? 'carte hover:ring-2 hover:ring-primaire' : 'rounded-carte border-2 border-dashed border-bord'"
            @click="ouvrir(tuile.fonction, tuile.adresse)"
          >
            <span class="grid size-[56px] shrink-0 place-items-center rounded-full" :class="tuile.teinte">
              <AppPicto :code="tuile.fonction.picto" :taille="26" />
            </span>
            <span class="flex min-w-0 flex-col">
              <span class="flex flex-wrap items-center gap-1.5">
                <b class="text-[17px] leading-tight">{{ tuile.fonction.texte }}</b>
                <AppBadge v-if="!tuile.adresse" etat="attente">bientôt</AppBadge>
                <span
                  v-if="pastilles[tuile.fonction.cle]"
                  class="rounded-full bg-erreur px-2 py-0.5 text-xs font-bold text-sur-etat"
                  :aria-label="`${pastilles[tuile.fonction.cle]} nouveau${pastilles[tuile.fonction.cle] > 1 ? 'x' : ''}`"
                >
                  {{ pastilles[tuile.fonction.cle] }}
                </span>
              </span>
              <small class="text-[13.5px] text-texte-doux">{{ tuile.fonction.detail }}</small>
            </span>
          </button>
        </div>
      </section>

      <AppAlerte v-if="prestataireId === null" etat="neutre">
        Vous proposez vos services ? Créez votre profil : les demandes des clients, l'agenda et les démarches s'ajoutent ici.
        <AppBouton variante="secondaire" @click="routeur.push('/proposer')">Proposer mes services</AppBouton>
      </AppAlerte>
    </template>
  </div>
</template>
