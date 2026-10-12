<script setup lang="ts">
// Fenêtre « Demander un devis à Paul Petit », ouverte depuis sa page (.doc/ihm/RM-DEVIS-IHM.md ; RM-DEVIS.md) :
// le métier s'il en a plusieurs, le besoin (10 à 2000
// caractères), jusqu'à 5 photos, le lieu des travaux (l'adresse du client quand le prestataire vient chez lui).
import { ref, watch } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import type { PrestatairePublic } from '../../outils/recherche'
import type { DemandeVisible } from '../../outils/devis'
import CarteAdresse from '../CarteAdresse.vue'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppChampFichier from '../ui/AppChampFichier.vue'
import AppFenetre from '../ui/AppFenetre.vue'
import AppSelection from '../ui/AppSelection.vue'
import AppZoneTexte from '../ui/AppZoneTexte.vue'

const PHOTOS_MAX = 5
const props = defineProps<{ prestataire: PrestatairePublic; ouverte: boolean }>()
const emit = defineEmits<{ fermer: []; envoyee: [demande: DemandeVisible] }>()

const texte = ref('')
// Le métier concerné : un seul métier → déjà choisi
const metierId = ref<number | null>(props.prestataire.metiers[0]?.id ?? null)
const photos = ref<File[]>([])
const choisie = ref<File | null>(null)
const aUneAdresse = ref(false)
const erreur = ref('')
const envoiEnCours = ref(false)
watch(() => props.ouverte, () => ((texte.value = ''), (photos.value = []), (erreur.value = '')))
// Chaque photo choisie rejoint la liste ; le champ redevient libre pour la suivante
watch(choisie, (f) => {
  if (f && photos.value.length < PHOTOS_MAX) photos.value.push(f)
  if (f) choisie.value = null
})

const chezLeClient = () => props.prestataire.lieu !== 'chez_moi'

async function envoyer() {
  erreur.value = ''
  envoiEnCours.value = true
  try {
    let demande = await appelerServeur<DemandeVisible>('/api/devis/demandes', {
      prestataire_id: props.prestataire.id,
      metier_id: metierId.value,
      texte: texte.value,
    })
    for (const photo of photos.value) {
      const formulaire = new FormData()
      formulaire.append('fichier', photo)
      demande = await appelerServeur<DemandeVisible>(`/api/moi/demandes-devis/${demande.id}/photos`, formulaire)
    }
    emit('envoyee', demande)
  } catch (e) {
    erreur.value = messageErreur(e) // ex. « Décrivez votre besoin en 10 à 2000 caractères… »
  } finally {
    envoiEnCours.value = false
  }
}
</script>

<template>
  <AppFenetre :ouverte="ouverte" :titre="`Demander un devis à ${prestataire.nom_affiche}`" @fermer="emit('fermer')">
    <div class="flex flex-col gap-3 text-texte">
      <p class="text-[14px] text-texte-doux">
        Décrivez votre besoin : {{ prestataire.nom_affiche }} vous répond par un devis.
      </p>
      <AppSelection
        v-if="prestataire.metiers.length > 1"
        v-model="metierId"
        etiquette="Pour quel métier ?"
        obligatoire
        :options="prestataire.metiers.map((m) => ({ valeur: m.id, texte: m.nom }))"
      />
      <AppZoneTexte
        v-model="texte"
        etiquette="Votre besoin"
        obligatoire
        :maximum="2000"
        aide="ex. « Muret de 5 mètres au fond du jardin, hauteur 1 m ». De 10 à 2000 caractères."
      />
      <AppChampFichier
        v-if="photos.length < PHOTOS_MAX"
        v-model="choisie"
        :etiquette="`Photos (${photos.length} / ${PHOTOS_MAX})`"
        aide="JPG ou PNG, 5 Mo au plus"
        accepte="image/jpeg,image/png"
      />
      <ul v-if="photos.length" class="flex flex-wrap gap-1.5">
        <li v-for="(photo, rang) in photos" :key="rang" class="inline-flex items-center gap-1.5 rounded-full bg-neutre-doux py-0.5 pr-1 pl-2.5 text-sm">
          {{ photo.name }}
          <button type="button" class="size-6 rounded-full bg-surface font-bold text-erreur" :aria-label="`Retirer ${photo.name}`" @click="photos.splice(rang, 1)">
            ×
          </button>
        </li>
      </ul>
      <CarteAdresse
        v-if="chezLeClient()"
        titre="Lieu des travaux : votre adresse"
        chemin="/api/moi/adresse"
        texte-vide="Le prestataire vient chez vous : indiquez votre adresse (elle sera gardée pour les prochaines fois)."
        texte-ajouter="Ajouter mon adresse"
        texte-effacer="Effacer"
        @change="(a) => (aUneAdresse = a !== null)"
      />
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    </div>
    <template #pied>
      <AppBouton
        v-if="prestataire.lieu === 'chez_client' && !aUneAdresse"
        variante="verrouille"
        raison-verrou="Ajoutez d'abord votre adresse, juste au-dessus."
      >
        Envoyer ma demande
      </AppBouton>
      <AppBouton v-else :occupe="envoiEnCours" @click="envoyer">Envoyer ma demande</AppBouton>
      <AppBouton variante="secondaire" @click="emit('fermer')">Annuler</AppBouton>
    </template>
  </AppFenetre>
</template>
