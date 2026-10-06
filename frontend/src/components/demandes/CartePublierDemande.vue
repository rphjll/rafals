<script setup lang="ts">
// Accueil › carte « Publier une demande » (.doc/ihm/RM-ACCUEIL-IHM.md ; RM-DEMANDES.md) : le métier, le titre, le besoin,
// l'adresse avec son plan, pour quand, le budget, jusqu'à 5 photos. Envoyée au serveur par /api/demandes.
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../../api'
import { useCompte } from '../../composables/useCompte'
import type { MetierVisible } from '../../composables/useMetiers'
import { useMessage } from '../../composables/useMessage'
import { QUAND, type DemandeVisible } from '../../outils/demandes'
import AppChoixMetier from '../AppChoixMetier.vue'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppChamp from '../ui/AppChamp.vue'
import AppChampFichier from '../ui/AppChampFichier.vue'
import AppElementChoisi from '../ui/AppElementChoisi.vue'
import AppRecherche from '../ui/AppRecherche.vue'
import AppSegment from '../ui/AppSegment.vue'
import AppSelection from '../ui/AppSelection.vue'
import AppZoneTexte from '../ui/AppZoneTexte.vue'

const PHOTOS_MAX = 5
const PHOTO_OCTETS_MAX = 5 * 1024 * 1024
// Service d'adresses de l'État (Géoplateforme de l'IGN) : gratuit, sans clé (.doc/technique/API-EXTERNES.md)
const SERVICE_ADRESSES = 'https://data.geopf.fr/geocodage/search'
const LIEUX = [
  { valeur: 'chez_moi', texte: 'Chez moi' },
  { valeur: 'chez_prestataire', texte: 'Chez le prestataire' },
]
const OPTIONS_QUAND = QUAND.map((q, rang) => ({ valeur: rang, texte: q.texte }))

interface Adresse {
  id: number
  libelle: string
  rue: string | null // vide quand le client n'a choisi qu'une ville
  codePostal: string
  codeInsee: string
  latitude: number
  longitude: number
}
interface ReponseAdresses {
  features: {
    geometry: { coordinates: [number, number] }
    properties: { label: string; name: string; postcode: string; citycode: string; type: string }
  }[]
}

const emit = defineEmits<{ publiee: [demande: DemandeVisible] }>()
const routeur = useRouter()
const { compte } = useCompte()
const { afficherMessage } = useMessage()

const metier = ref<MetierVisible | null>(null)
const titre = ref('')
const texte = ref('')
const adresse = ref<Adresse | null>(null)
const lieu = ref('chez_moi')
const quand = ref<number | null>(0)
const jour = ref('')
const budget = ref('')
const photos = ref<{ fichier: File; apercu: string }[]>([])
const choisie = ref<File | null>(null)
const erreurPhoto = ref('')
const erreur = ref('')
const envoiEnCours = ref(false)

const jourPrecis = computed(() => quand.value !== null && QUAND[quand.value].valeur === 'jour_precis')

async function chercherAdresse(saisie: string): Promise<Adresse[]> {
  if (saisie.trim().length < 3) return []
  try {
    const reponse = await fetch(`${SERVICE_ADRESSES}?q=${encodeURIComponent(saisie)}&limit=5`)
    if (!reponse.ok) return []
    const { features } = (await reponse.json()) as ReponseAdresses
    return features.map((f, rang) => ({
      id: rang,
      libelle: f.properties.label,
      rue: f.properties.type === 'municipality' ? null : f.properties.name,
      codePostal: f.properties.postcode,
      codeInsee: f.properties.citycode,
      longitude: f.geometry.coordinates[0],
      latitude: f.geometry.coordinates[1],
    }))
  } catch {
    return [] // service injoignable : pas de proposition
  }
}

// Plan OpenStreetMap centré sur l'adresse, avec un repère (environ 400 m de chaque côté)
const adressePlan = computed(() => {
  if (!adresse.value) return ''
  const { latitude, longitude } = adresse.value
  const cadre = [longitude - 0.005, latitude - 0.003, longitude + 0.005, latitude + 0.003].join(',')
  return `https://www.openstreetmap.org/export/embed.html?bbox=${cadre}&layer=mapnik&marker=${latitude},${longitude}`
})

// Chaque photo choisie rejoint la liste ; le champ redevient libre pour la suivante
watch(choisie, (fichier) => {
  if (!fichier) return
  choisie.value = null
  erreurPhoto.value = ''
  if (!['image/jpeg', 'image/png'].includes(fichier.type)) erreurPhoto.value = 'Choisissez une photo JPG ou PNG.'
  else if (fichier.size > PHOTO_OCTETS_MAX) erreurPhoto.value = 'Cette photo dépasse 5 Mo.'
  else photos.value.push({ fichier, apercu: URL.createObjectURL(fichier) })
})

function enleverPhoto(rang: number) {
  URL.revokeObjectURL(photos.value[rang].apercu)
  photos.value.splice(rang, 1)
}
function oublierPhotos() {
  photos.value.forEach((photo) => URL.revokeObjectURL(photo.apercu))
  photos.value = []
}
onBeforeUnmount(oublierPhotos)

async function publier() {
  erreur.value = ''
  if (!metier.value) erreur.value = 'Choisissez un métier : il dit quels prestataires prévenir.'
  else if (!adresse.value) erreur.value = 'Choisissez votre adresse dans la liste proposée.'
  else if (quand.value === null) erreur.value = 'Indiquez pour quand.'
  if (erreur.value || !metier.value || !adresse.value || quand.value === null) return

  const formulaire = new FormData()
  formulaire.append('metier_id', String(metier.value.id))
  formulaire.append('titre', titre.value)
  formulaire.append('description', texte.value)
  formulaire.append('quand', QUAND[quand.value].valeur)
  if (jourPrecis.value && jour.value) formulaire.append('jour', jour.value)
  formulaire.append('lieu', lieu.value)
  const euros = Number(budget.value.replace(',', '.'))
  if (budget.value.trim() && Number.isFinite(euros)) formulaire.append('budget_centimes', String(Math.round(euros * 100)))
  if (adresse.value.rue) formulaire.append('adresse_ligne', adresse.value.rue)
  formulaire.append('code_postal', adresse.value.codePostal)
  formulaire.append('code_insee', adresse.value.codeInsee)
  formulaire.append('latitude', String(adresse.value.latitude))
  formulaire.append('longitude', String(adresse.value.longitude))
  photos.value.forEach((photo) => formulaire.append('photos', photo.fichier))

  envoiEnCours.value = true
  try {
    const demande = await appelerServeur<DemandeVisible>('/api/demandes', formulaire)
    emit('publiee', demande)
    afficherMessage(`Votre demande « ${demande.titre} » est publiée.`)
    titre.value = texte.value = budget.value = jour.value = ''
    quand.value = 0
    oublierPhotos()
  } catch (e) {
    erreur.value = messageErreur(e) // ex. « Le titre doit faire entre 5 et 80 caractères. »
  } finally {
    envoiEnCours.value = false
  }
}
</script>

<template>
  <form class="flex flex-col gap-4 rounded-rafals border border-bord bg-surface p-5" @submit.prevent="publier">
    <h2 class="text-xl font-bold">Publier une demande</h2>

    <AppChoixMetier v-model="metier" :avec-dossiers="false" etiquette="Quel métier ?" obligatoire />
    <AppChamp v-model="titre" etiquette="Titre" obligatoire placeholder="ex. Tondre ma pelouse" maxlength="80" />
    <AppZoneTexte
      v-model="texte"
      etiquette="Décrivez votre besoin"
      obligatoire
      :maximum="1000"
      aide="ex. 200 m², terrain plat, j'ai une prise dehors. Au moins 20 caractères, sans téléphone ni mail."
    />

    <div class="flex flex-col gap-2">
      <template v-if="adresse">
        <AppElementChoisi :texte="adresse.libelle" @changer="adresse = null" />
        <iframe
          :src="adressePlan"
          :title="`Plan : ${adresse.libelle}`"
          class="h-56 w-full rounded-rafals border border-bord"
          loading="lazy"
          referrerpolicy="no-referrer"
        />
      </template>
      <AppRecherche
        v-else
        etiquette="Adresse"
        obligatoire
        :chercher="chercherAdresse"
        :libelle="(a: Adresse) => a.libelle"
        :cle="(a: Adresse) => a.id"
        placeholder="ex. 12 rue des Lilas, Mérignac"
        aide="Seul le prestataire que vous choisirez verra la rue ; les autres voient la ville."
        @choisir="(a: Adresse) => (adresse = a)"
      />
      <AppSegment v-model="lieu" etiquette="Où a lieu le service ?" :options="LIEUX" />
    </div>

    <AppSelection v-model="quand" etiquette="Pour quand ?" :options="OPTIONS_QUAND" obligatoire />
    <AppChamp v-if="jourPrecis" v-model="jour" etiquette="Quel jour ?" type="date" obligatoire />
    <AppChamp v-model="budget" etiquette="Budget en euros (facultatif)" inputmode="decimal" placeholder="ex. 40" />

    <div class="flex flex-col gap-2">
      <AppChampFichier
        v-if="photos.length < PHOTOS_MAX"
        v-model="choisie"
        :etiquette="`Photos (${photos.length} / ${PHOTOS_MAX})`"
        aide="JPG ou PNG, 5 Mo au plus"
        accepte="image/jpeg,image/png"
      />
      <p v-else class="text-[13px] font-semibold">Photos ({{ PHOTOS_MAX }} / {{ PHOTOS_MAX }})</p>
      <AppAlerte v-if="erreurPhoto">{{ erreurPhoto }}</AppAlerte>
      <ul v-if="photos.length" class="grid grid-cols-3 gap-2">
        <li v-for="(photo, rang) in photos" :key="photo.apercu" class="flex flex-col gap-1">
          <img :src="photo.apercu" :alt="`Photo ${rang + 1} : ${photo.fichier.name}`" class="aspect-square w-full rounded-rafals border border-bord object-cover" />
          <button type="button" class="text-[13px] font-semibold text-erreur underline" @click="enleverPhoto(rang)">Enlever</button>
        </li>
      </ul>
    </div>

    <div class="mt-auto flex flex-col gap-3">
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <AppBouton v-if="compte" type="submit" variante="accent" pleine-largeur :occupe="envoiEnCours">Publier ma demande</AppBouton>
      <template v-else>
        <p class="text-[13px] text-texte-doux">Il faut un compte pour publier une demande. C'est gratuit.</p>
        <AppBouton variante="accent" pleine-largeur @click="routeur.push('/connexion')">Se connecter pour publier</AppBouton>
      </template>
    </div>
  </form>
</template>
