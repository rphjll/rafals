<script setup lang="ts">
// « Ma carte de visite » (lot 10.4, .doc/ihm/RM-CARTE-VISITE-IHM.md ; règles : RM-CARTE-VISITE.md). Ouverte par la tuile
// de « Mon activité ». L'aperçu montre la vraie carte (le carré à scanner vient du serveur) ; deux PDF à télécharger.
// Verrouillé sans SIRET vérifié ou si le profil n'est pas actif (raison donnée par le serveur).
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import GardePrestataire from '../components/prestataire/GardePrestataire.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppCase from '../components/ui/AppCase.vue'
import AppSection from '../components/ui/AppSection.vue'
import { useCompte } from '../composables/useCompte'

interface Apercu {
  nom: string
  metier: string
  ville: string
  note: string
  /** Le numéro du compte, ex. « 06 12 34 56 78 » ; vide : la case du téléphone est verrouillée */
  telephone: string | null
  adresse: string
  /** Pourquoi les boutons sont verrouillés (sans SIRET vérifié, profil en pause…), sinon vide */
  raison: string | null
}

const routeur = useRouter()
const { compte } = useCompte()
const apercu = ref<Apercu | null>(null)
const erreur = ref('')
const avecTelephone = ref(false)
const CARRE = '/api/moi/prestataire/carte-de-visite/carre.svg' // le même carré que sur le PDF
const SANS_TELEPHONE = "Ajoutez d'abord votre téléphone dans Mon profil › Mon compte › Mes informations."

onMounted(async () => {
  if (!compte.value?.prestataire_id) return
  try {
    apercu.value = await appelerServeur<Apercu>('/api/moi/prestataire/carte-de-visite')
  } catch (e) {
    erreur.value = messageErreur(e)
  }
})

/** Le PDF s'ouvre dans un nouvel onglet (enregistrer ou imprimer), comme une facture */
function telecharger(forme: 'planche' | 'carte') {
  window.open(`/api/moi/prestataire/carte-de-visite/pdf?forme=${forme}&telephone=${avecTelephone.value}`, '_blank', 'noopener')
}
</script>

<template>
  <GardePrestataire titre="Ma carte de visite">
    <h1 class="text-[clamp(28px,4.5vw,40px)] font-black">Ma carte de visite</h1>
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>

    <template v-if="apercu">
      <AppSection>
        <p class="text-texte-doux">
          Donnez-la à vos clients : en scannant le carré, ils arrivent sur votre page rafals, avec vos avis et vos photos.
        </p>
        <AppAlerte v-if="apercu.raison" etat="attente">{{ apercu.raison }}</AppAlerte>

        <!-- L'aperçu : 8,5 × 5,5 cm, papier blanc même en mode sombre -->
        <div
          class="mx-auto grid aspect-[85/55] w-full max-w-[425px] grid-cols-[1fr_31%] gap-[5%] rounded-lg bg-papier px-[6%] py-[6.5%] font-[Helvetica,Arial,sans-serif] text-encre shadow-[0_2px_14px_rgb(0_0_0/0.18)]"
          aria-label="Aperçu de la carte de visite"
        >
          <div class="flex min-w-0 flex-col">
            <b class="text-[clamp(15px,4.4vw,21px)] leading-tight">{{ apercu.nom }}</b>
            <span class="mt-[3%] text-[clamp(11px,3vw,14px)]">{{ apercu.metier }}</span>
            <span class="text-[clamp(10px,2.7vw,12.5px)] text-encre-douce">{{ apercu.ville }}</span>
            <span class="mt-auto text-[clamp(10px,2.7vw,12.5px)]">{{ apercu.note }}</span>
            <b v-if="avecTelephone && apercu.telephone" class="text-[clamp(11px,3vw,14px)]">{{ apercu.telephone }}</b>
            <span class="mt-[3%] text-[clamp(8px,2vw,10px)] text-encre-douce">rafals.</span>
          </div>
          <div class="flex flex-col items-center justify-center gap-1">
            <img :src="CARRE" alt="Carré à scanner vers votre page publique" class="w-full" />
            <span class="text-center text-[clamp(7px,1.9vw,9.5px)] leading-tight text-encre-douce">Mes avis et mes photos</span>
          </div>
        </div>

        <template v-if="!apercu.raison">
          <AppCase
            v-model="avecTelephone"
            texte="Mettre mon téléphone sur la carte"
            :raison-verrou="apercu.telephone ? undefined : SANS_TELEPHONE"
          />
          <p v-if="apercu.telephone" class="-mt-2 text-[13px] text-texte-doux">Le numéro de votre compte : {{ apercu.telephone }}.</p>
        </template>

        <div class="flex flex-wrap gap-2">
          <template v-if="apercu.raison">
            <AppBouton variante="verrouille" :raison-verrou="apercu.raison">Télécharger la planche à découper</AppBouton>
            <AppBouton variante="verrouille" :raison-verrou="apercu.raison">Télécharger pour un imprimeur</AppBouton>
          </template>
          <template v-else>
            <AppBouton @click="telecharger('planche')">Télécharger la planche à découper</AppBouton>
            <AppBouton variante="secondaire" @click="telecharger('carte')">Télécharger pour un imprimeur</AppBouton>
          </template>
        </div>
        <div v-if="apercu.raison?.includes('SIRET')">
          <AppBouton variante="secondaire" @click="routeur.push('/creer-mon-auto-entreprise')">Créer mon auto-entreprise</AppBouton>
        </div>
      </AppSection>

      <AppSection v-if="!apercu.raison" titre="Comment l'imprimer">
        <p class="text-[14.5px] text-texte-doux">
          <b class="text-texte">La planche à découper</b> : une page A4 avec 10 cartes. Imprimez-la sur du papier épais (250 g),
          puis coupez le long des petits traits gris dans les marges.
        </p>
        <p class="text-[14.5px] text-texte-doux">
          <b class="text-texte">Pour un imprimeur</b> : une seule carte au format exact (8,5 × 5,5 cm), à envoyer à un imprimeur
          en ligne ou en boutique, qui en imprime autant que vous voulez.
        </p>
      </AppSection>
    </template>
  </GardePrestataire>
</template>
