<script setup lang="ts">
// « Ma carte de visite » (lot 10.4, .doc/ihm/RM-CARTE-VISITE-IHM.md ; règles : RM-CARTE-VISITE.md). Ouverte par la tuile
// de « Mon activité ». L'aperçu montre la vraie carte (le carré à scanner vient du serveur) ; deux PDF à télécharger.
// Depuis le 22/10/2026 : 6 couleurs toutes prêtes et une petite phrase, gardées par [Enregistrer ma carte] (schema_v33),
// et 2 onglets : « Chez un imprimeur » (une carte) et « Chez moi » (la planche A4 de 10 cartes), chacun avec son bouton.
// Verrouillé sans SIRET vérifié ou si le profil n'est pas actif (raison donnée par le serveur).
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import ApercuCarteVisite from '../components/prestataire/ApercuCarteVisite.vue'
import GardePrestataire from '../components/prestataire/GardePrestataire.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppCase from '../components/ui/AppCase.vue'
import AppChamp from '../components/ui/AppChamp.vue'
import AppOnglets from '../components/ui/AppOnglets.vue'
import AppSection from '../components/ui/AppSection.vue'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'

interface Couleur {
  code: string
  nom: string
  /** Ex. « #1D3A5F » (bleu nuit) : la teinte vient du serveur, la même que sur le PDF */
  teinte: string
}
interface Apercu {
  nom: string
  metier: string
  ville: string
  note: string
  /** Le numéro du compte, ex. « 06 12 34 56 78 » ; vide : la case du téléphone est verrouillée */
  telephone: string | null
  adresse: string
  /** Couleur et phrase enregistrées (« vert » et vide au départ) */
  couleur: string
  phrase: string | null
  couleurs: Couleur[]
  /** Pourquoi les boutons sont verrouillés (sans SIRET vérifié, profil en pause…), sinon vide */
  raison: string | null
}

const PHRASE_MAX = 40
const CHEMIN = '/api/moi/prestataire/carte-de-visite'
const SANS_TELEPHONE = "Ajoutez d'abord votre téléphone dans Mon profil › Mon compte › Mes informations."

const routeur = useRouter()
const { compte } = useCompte()
const { afficherMessage } = useMessage()
const apercu = ref<Apercu | null>(null)
const erreur = ref('')
const avecTelephone = ref(false)
// Ce qui est affiché (l'aperçu change tout de suite) ; [Enregistrer ma carte] le garde
const couleur = ref('vert')
const phrase = ref('')
const envoi = ref(false)
// « Chez un imprimeur » d'abord (Raphael, 22/10/2026 : « un apparcu de la carte a imprimer chez le pro et un a imprimer chez soi »)
const ONGLETS = [{ id: 'imprimeur', texte: 'Chez un imprimeur' }, { id: 'chez-moi', texte: 'Chez moi' }] as const
const onglet = ref('imprimeur')

function prendre(a: Apercu) {
  apercu.value = a
  couleur.value = a.couleur
  phrase.value = a.phrase ?? ''
}
onMounted(async () => {
  if (!compte.value?.prestataire_id) return
  try {
    prendre(await appelerServeur<Apercu>(CHEMIN))
  } catch (e) {
    erreur.value = messageErreur(e)
  }
})

const teinte = computed(() => apercu.value?.couleurs.find((c) => c.code === couleur.value)?.teinte ?? '')
const telephoneMontre = computed(() => (avecTelephone.value ? (apercu.value?.telephone ?? null) : null))
const carre = computed(() => `${CHEMIN}/carre.svg?couleur=${couleur.value}`) // le même carré que sur le PDF
const modifie = computed(() => !!apercu.value && (couleur.value !== apercu.value.couleur || phrase.value.trim() !== (apercu.value.phrase ?? '')))

async function enregistrer() {
  envoi.value = true
  try {
    prendre(await appelerServeur<Apercu>(CHEMIN, { couleur: couleur.value, phrase: phrase.value }))
    afficherMessage('Carte enregistrée : vous la retrouverez à votre prochaine visite.')
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  } finally {
    envoi.value = false
  }
}

/** Le PDF s'ouvre dans un nouvel onglet (enregistrer ou imprimer), comme une facture, avec ce qui est affiché */
function telecharger(forme: 'planche' | 'carte') {
  const reglages = new URLSearchParams({ forme, telephone: String(avecTelephone.value), couleur: couleur.value, phrase: phrase.value })
  window.open(`${CHEMIN}/pdf?${reglages}`, '_blank', 'noopener')
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
        <AppOnglets v-model="onglet" :onglets="ONGLETS" />

        <!-- Chez un imprimeur : une carte au format exact -->
        <template v-if="onglet === 'imprimeur'">
          <div class="mx-auto w-full max-w-[425px]">
            <ApercuCarteVisite :nom="apercu.nom" :metier="apercu.metier" :ville="apercu.ville" :note="apercu.note" :phrase="phrase" :telephone="telephoneMontre" :teinte="teinte" :carre="carre" />
          </div>
          <p class="text-[14.5px] text-texte-doux">
            Une seule carte au format exact (8,5 × 5,5 cm). Envoyez ce PDF à un imprimeur, en ligne ou en boutique : il en imprime
            autant que vous voulez.
          </p>
          <div>
            <AppBouton v-if="apercu.raison" variante="verrouille" :raison-verrou="apercu.raison">Télécharger pour un imprimeur</AppBouton>
            <AppBouton v-else @click="telecharger('carte')">Télécharger pour un imprimeur</AppBouton>
          </div>
        </template>

        <!-- Chez moi : la page A4 avec 10 cartes (marges de 20 mm à gauche et à droite, 11 mm en haut et en bas) -->
        <template v-else>
          <div class="mx-auto grid aspect-[210/297] w-full max-w-[340px] grid-cols-2 content-center bg-papier px-[9.5%] shadow-[0_2px_14px_rgb(0_0_0/0.18)]">
            <ApercuCarteVisite
              v-for="n in 10"
              :key="n"
              :nom="apercu.nom" :metier="apercu.metier" :ville="apercu.ville" :note="apercu.note"
              :phrase="phrase"
              :telephone="telephoneMontre"
              :teinte="teinte"
              :carre="carre"
              petite
            />
          </div>
          <p class="text-[14.5px] text-texte-doux">
            Une page A4 avec 10 cartes. Imprimez-la sur du papier épais (250 g), puis coupez le long des petits traits gris dans
            les marges.
          </p>
          <div>
            <AppBouton v-if="apercu.raison" variante="verrouille" :raison-verrou="apercu.raison">Télécharger la planche à découper</AppBouton>
            <AppBouton v-else @click="telecharger('planche')">Télécharger la planche à découper</AppBouton>
          </div>
        </template>

        <div v-if="apercu.raison?.includes('SIRET')">
          <AppBouton variante="secondaire" @click="routeur.push('/creer-mon-auto-entreprise')">Créer mon auto-entreprise</AppBouton>
        </div>
      </AppSection>

      <!-- Ce qui est choisi ici vaut pour les deux onglets -->
      <AppSection v-if="!apercu.raison" titre="Personnaliser ma carte">
        <div class="flex flex-col gap-1.5">
          <span class="text-[13px] font-semibold">Couleur de la carte</span>
          <div class="flex flex-wrap gap-2.5" role="group" aria-label="Couleur de la carte">
            <button
              v-for="c in apercu.couleurs"
              :key="c.code"
              type="button"
              class="flex min-w-16 flex-col items-center gap-1 text-[12px] font-bold"
              :aria-pressed="couleur === c.code"
              @click="couleur = c.code"
            >
              <i
                class="block size-[38px] rounded-full outline-3 outline-offset-3"
                :class="couleur === c.code ? 'outline-primaire' : 'outline-transparent'"
                :style="{ background: c.teinte }"
              />
              {{ c.nom }}
            </button>
          </div>
        </div>
        <AppChamp
          v-model="phrase"
          etiquette="Petite phrase (facultative)"
          :maxlength="PHRASE_MAX"
          placeholder="Ex. Devis gratuit, intervention sous 48 h"
          :aide="`Elle s'imprime sous la ville. ${phrase.length}/${PHRASE_MAX}`"
        />
        <AppCase
          v-model="avecTelephone"
          texte="Mettre mon téléphone sur la carte"
          :raison-verrou="apercu.telephone ? undefined : SANS_TELEPHONE"
        />
        <p v-if="apercu.telephone" class="-mt-2 text-[13px] text-texte-doux">Le numéro de votre compte : {{ apercu.telephone }}.</p>
        <div>
          <AppBouton variante="secondaire" :occupe="envoi" @click="enregistrer">
            {{ modifie ? 'Enregistrer ma carte' : 'Carte enregistrée ✓' }}
          </AppBouton>
        </div>
      </AppSection>
    </template>
  </GardePrestataire>
</template>
