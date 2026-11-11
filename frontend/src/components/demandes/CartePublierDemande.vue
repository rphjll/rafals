<script setup lang="ts">
// Le formulaire « Publier une demande » (page /demandes/nouvelle ; .doc/ihm/RM-DEMANDES-IHM.md ; RM-DEMANDES.md), comme la
// grande maquette depuis le 10/11/2026 : le client écrit son besoin avec ses mots et rafals trouve le métier tout seul
// (« Métier trouvé : Plombier · [Changer] »), grâce aux mots-clés des métiers ; puis les détails, pour quand, l'adresse
// avec son plan, où a lieu le service, le budget et jusqu'à 5 photos. Envoyé au serveur par /api/demandes.
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { type MetierVisible as Metier, useMetiers } from '../../composables/useMetiers'
import { devinerMetier } from '../../outils/devineMetier'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../../api'
import { useCompte } from '../../composables/useCompte'
import { useMessage } from '../../composables/useMessage'
import { QUAND, type DemandeVisible } from '../../outils/demandes'
import AppChoixMetier from '../AppChoixMetier.vue'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppIcone from '../ui/AppIcone.vue'
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

const metier = ref<Metier | null>(null)
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

// Métier trouvé tout seul à partir du titre et des détails (outils/devineMetier.ts : les mots de chaque métier, comme
// la grande maquette). Ex. « Fuite sous l'évier » → Plombier. [Changer] ouvre le choix à la main ; ensuite le métier
// choisi n'est plus remplacé.
const { dossiers, chargerDossiers } = useMetiers()
chargerDossiers().catch(() => {})
const choixALaMain = ref(false)
const changerMetier = ref(false)
const recherchePasFaite = ref(true)
watch([titre, texte, dossiers], () => {
  if (choixALaMain.value) return
  const ecrit = `${titre.value} ${texte.value}`.trim()
  recherchePasFaite.value = ecrit.length < 4
  const code = devinerMetier(ecrit)
  metier.value = (code && dossiers.value.flatMap((d) => d.metiers).find((m) => m.code === code)) || null
})
watch(changerMetier, (ouvert) => {
  if (ouvert) choixALaMain.value = true
})
watch(metier, (m) => {
  if (m && changerMetier.value) changerMetier.value = false
})

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
  if (!metier.value) {
    erreur.value = 'Choisissez le métier : nous ne l’avons pas reconnu.'
    changerMetier.value = true
  }
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
  <form class="carte form p-[18px]" @submit.prevent="publier">
    <div class="champ">
      <label for="d-titre">De quoi avez-vous besoin ? <span class="text-erreur" aria-hidden="true">*</span></label>
      <input id="d-titre" v-model="titre" required autocomplete="off" maxlength="80" placeholder="Ex. Fuite sous l’évier de la cuisine" />
      <!-- Le métier trouvé tout seul -->
      <div class="zone-metier" aria-live="polite">
        <AppChoixMetier v-if="changerMetier" v-model="metier" :avec-dossiers="false" etiquette="Choisissez le métier" class="flex-1" />
        <template v-else-if="metier">
          <span class="trouve"><AppIcone nom="ok" />Métier trouvé : <b>{{ metier.nom }}</b></span>
          <button type="button" class="lien" @click="changerMetier = true">Changer</button>
        </template>
        <span v-else-if="recherchePasFaite" class="doux petit">Écrivez votre besoin avec vos mots : rafals trouve tout seul le bon métier.</span>
        <template v-else>
          <span class="pas-trouve">Nous n’avons pas reconnu le métier.</span>
          <button type="button" class="lien" @click="changerMetier = true">Choisir le métier</button>
        </template>
      </div>
    </div>
    <AppZoneTexte
      v-model="texte"
      etiquette="Détails"
      obligatoire
      :maximum="1000"
      aide="Ex. L’eau coule dans le meuble depuis hier. Au moins 20 caractères, sans téléphone ni mail."
    />
    <AppSelection v-model="quand" etiquette="Pour quand ?" :options="OPTIONS_QUAND" obligatoire />
    <AppChamp v-if="jourPrecis" v-model="jour" etiquette="Quel jour ?" type="date" obligatoire />

    <div v-if="adresse" class="champ">
      <label>Où ?</label>
      <AppElementChoisi :texte="adresse.libelle" @changer="adresse = null" />
      <iframe :src="adressePlan" :title="`Plan : ${adresse.libelle}`" class="h-56 w-full rounded-[12px] border border-bord" loading="lazy" referrerpolicy="no-referrer" />
      <small>Votre adresse exacte n’est jamais montrée : les prestataires voient la ville.</small>
    </div>
    <AppRecherche
      v-else
      etiquette="Où ?"
      obligatoire
      :chercher="chercherAdresse"
      :libelle="(a: Adresse) => a.libelle"
      :cle="(a: Adresse) => a.id"
      placeholder="Ex. 12 rue des Lilas, Mérignac"
      aide="Votre adresse exacte n’est jamais montrée : les prestataires voient la ville."
      @choisir="(a: Adresse) => (adresse = a)"
    />
    <div class="champ">
      <label>Le service a lieu</label>
      <AppSegment v-model="lieu" etiquette="Où a lieu le service ?" :options="LIEUX" />
    </div>
    <AppChamp v-model="budget" etiquette="Budget en euros (facultatif)" inputmode="decimal" placeholder="Ex. 40" />

    <AppChampFichier
      v-if="photos.length < PHOTOS_MAX"
      v-model="choisie"
      :etiquette="`Photos, facultatif (${photos.length} / ${PHOTOS_MAX})`"
      aide="JPG ou PNG, 5 Mo au plus"
      accepte="image/jpeg,image/png"
    />
    <AppAlerte v-if="erreurPhoto">{{ erreurPhoto }}</AppAlerte>
    <div v-if="photos.length" class="photos">
      <div v-for="(photo, rang) in photos" :key="photo.apercu" class="ph" style="--c: var(--surface2)">
        <img :src="photo.apercu" :alt="`Photo ${rang + 1} : ${photo.fichier.name}`" />
        <button type="button" class="sur" style="border: 0; color: #fff; cursor: pointer" @click="enleverPhoto(rang)">Enlever</button>
      </div>
    </div>

    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <AppBouton v-if="compte" type="submit" :occupe="envoiEnCours" style="align-self: flex-start">Publier ma demande</AppBouton>
    <template v-else>
      <p class="doux petit">Il faut un compte pour publier une demande. C’est gratuit.</p>
      <AppBouton style="align-self: flex-start" @click="routeur.push('/connexion')">Se connecter pour publier</AppBouton>
    </template>
  </form>
</template>
