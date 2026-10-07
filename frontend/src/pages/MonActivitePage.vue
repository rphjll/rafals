<script setup lang="ts">
// Mon activité (.doc/ihm/RM-MON-ACTIVITE-IHM.md) : toutes les fonctions de rafals au même endroit, en tuiles rangées
// par groupe. Un prestataire en voit plus qu'un client. Une fonction pas encore construite a une tuile « bientôt ».
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBadge from '../components/ui/AppBadge.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppPicto from '../components/ui/AppPicto.vue'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'
import { type FonctionActivite, GROUPES_ACTIVITE, adresseDe, fonctionsPour } from '../outils/activite'
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
